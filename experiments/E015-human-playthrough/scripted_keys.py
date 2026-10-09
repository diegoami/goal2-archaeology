#!/usr/bin/env python3
"""T34 acceptance sitting on private displays; never uses the owner's display.

The privacy proof has both halves of T34 review R3:
- XSendEvent keys to the other application's window (`xdotool key --window`) — no raw XI2
  events exist for a logger to see, so this alone proves little;
- focused real XTEST keys: `xdotool windowfocus --sync <xev>` then plain `xdotool key x y z`
  on the outer display, which DOES generate raw events there (an outer raw reader runs as the
  positive control and must see them). A logger attached to the outer display would leak them
  into keys.jsonl; the assertion is that it does not, while the xev window's own log shows
  every key was really delivered.

Game keys are sent with gaps drawn from [0.5, 1.5] s (T34 rework: the earlier 2 s gap hid the
burst/request-window behaviour the map rules handle).
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder


def group_presses(events, quiet):
    """The key groups: consecutive press times no two > quiet apart form one group. Returns a
    list of groups, each a list of press monotonic times in order (releases are not listed)."""
    groups, current = [], []
    for e in events:
        if e["event"] != "press":
            continue
        if current and e["monotonic_s"] > current[-1] + quiet:
            groups.append(current)
            current = []
        current.append(e["monotonic_s"])
    if current:
        groups.append(current)
    return groups


def check_bursts(groups, bursts, t0):
    """The acceptance guard, count half (R3): each key group has its own burst snapshot, staged
    after the group's last key. Distinct, not just any later snapshot — the old `any(...)` let
    one final snapshot satisfy every group, so a recorder that merged groups (4 snapshots for
    10 groups) still passed. Returns (ok, message)."""
    if len(bursts) != len(groups):
        return False, (f"{len(bursts)} burst snapshots for {len(groups)} key group(s); each "
                       f"group needs its own snapshot staged after its last key")
    by_stage = sorted(bursts, key=lambda b: b["elapsed_s"] + t0)
    for group, b in zip(groups, by_stage):
        if b["elapsed_s"] + t0 < group[-1]:
            return False, f"a burst snapshot staged before key group ending {group[-1]}"
    return True, f"{len(bursts)} burst snapshots for {len(groups)} key group(s)"


def check_request_windows(groups, bursts, t0, margin):
    """The acceptance guard, timing half (Sol r2 R2a): each key group's save request must open
    inside its own bracket — at or after the group's last key, and before the next group's keys
    are all in. The blocking scheduler sent the ten-key reproduction's requests at 8.5 s, after
    the last key at 5.6 s: equal counts staged after each group still certified that, and the
    late windows could not recover the screen boundaries between groups. Returns (ok, message)."""
    if len(bursts) != len(groups):
        return False, f"{len(bursts)} burst snapshots for {len(groups)} key group(s)"
    by_request = sorted(bursts, key=lambda b: b["request_s"])
    for i, (group, b) in enumerate(zip(groups, by_request)):
        request = t0 + b["request_s"]
        if request < group[-1]:
            return False, (f"group {i}'s save request opened at {b['request_s']:.3f}s, before "
                           f"the group's last key")
        if i + 1 < len(groups) and request > groups[i + 1][-1] + margin:
            return False, (f"group {i}'s save request opened at {b['request_s']:.3f}s, after "
                           f"group {i + 1} had ended; requests must interleave with the keys, "
                           f"not follow them")
    return True, f"{len(bursts)} request windows interleaved with their key groups"


def check_mapped(result):
    """The acceptance guard, coverage half (Sol r2 R2b): every press must be mapped. Equal
    snapshot counts are not enough — the pre-fix clean sitting exited 0 with '10 for 10 key
    group(s)' while 6 of 10 presses were unmapped. Returns (ok, message)."""
    if result["unmapped_keys"]:
        return False, (f"{result['unmapped_keys']} unmapped presses ({result['summary']}); "
                       "every group must map from the screen before it to the screen after it")
    return True, f"{result['summary']}; every press mapped"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--keys", default="a;b;c", help="game keys as a ';'-separated list")
    ap.add_argument("--gap-min", type=float, default=0.5, help="minimum gap between game keys (s)")
    ap.add_argument("--gap-max", type=float, default=1.5, help="maximum gap between game keys (s)")
    ap.add_argument("--seed", type=int, default=None, help="seed the gap draw (reproducible gaps)")
    a = ap.parse_args()
    keys = [k for k in a.keys.split(";") if k]
    rng = random.Random(a.seed)
    outer = app = sitting = raw_outer = None
    before = set(recorder.SESSIONS.glob("*"))
    scratch = ROOT / "scratch" / "t34-tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        for number in range(740, 760):
            outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(1)
            if outer.poll() is None:
                break
        if outer.poll() is not None:
            raise RuntimeError("no private outer display")
        env = dict(os.environ, DISPLAY=f":{number}")
        xev_log = scratch / f"xev-{os.getpid()}.log"
        app = subprocess.Popen(["xev", "-name", "T34-other-app"], env=env, stdout=open(xev_log, "w"),
                               stderr=subprocess.DEVNULL, start_new_session=True)
        # the positive control: a raw reader on the OUTER display (stand-in for a wrong logger)
        raw_log = scratch / f"raw-outer-{os.getpid()}.log"
        raw_outer = subprocess.Popen(["stdbuf", "-oL", "xinput", "test-xi2", "--root"], env=env,
                                     stdout=open(raw_log, "w"), stderr=subprocess.DEVNULL,
                                     start_new_session=True)
        quit_after = 12 + 2 * len(keys)
        sitting = subprocess.Popen(["bash", "runtime/human/play.sh", "--quit-after", str(quit_after)], env=env, start_new_session=True)
        deadline = time.monotonic() + 15
        session = None
        while time.monotonic() < deadline:
            fresh = set(recorder.SESSIONS.glob("*")) - before
            if fresh:
                session = fresh.pop()
                try:
                    meta = json.loads((session / "meta.json").read_text())
                    if meta.get("window_id") and (session / "index.jsonl").exists():
                        break
                except (OSError, json.JSONDecodeError):
                    pass
            time.sleep(0.1)
        else:
            raise RuntimeError("opening snapshot never appeared")
        child = dict(env, DISPLAY=meta["display"])
        subprocess.run(["xdotool", "windowfocus", meta["window_id"]], env=child, check=True)
        gaps = []
        for i, key in enumerate(keys):
            if i:
                gap = rng.uniform(a.gap_min, a.gap_max)
                gaps.append(round(gap, 3))
                time.sleep(gap)
            subprocess.run(["xdotool", "key", key], env=child, check=True)
        # R3's real-key half: xev holds the outer focus and receives real XTEST keys
        other = subprocess.check_output(["xdotool", "search", "--name", "T34-other-app"], env=env, text=True).split()[0]
        subprocess.run(["xdotool", "key", "--window", other, "x"], env=env, check=True)
        subprocess.run(["xdotool", "windowfocus", "--sync", other], env=env, check=True)
        subprocess.run(["xdotool", "key", "y", "z"], env=env, check=True)
        assert sitting.wait(timeout=quit_after + 40) == 0
        events = [json.loads(line) for line in (session / "keys.jsonl").read_text().splitlines()]
        presses = [e["keysym"] for e in events if e["event"] == "press"]
        assert presses == list(keys), presses
        assert not {"x", "y", "z"} & set(presses), presses
        # the keys really were typed on the outer display: the control reader saw them raw...
        raw = raw_log.read_text()
        raw_presses = raw.count("RawKeyPress")
        assert raw_presses >= 2, raw_presses   # y and z were really typed on the outer display
        # ...and xev (the other application) received every one of them: its own KeyPress log is
        # the positive control, written as one JSON line per press alongside the session (R1)
        foreign = recorder.xev_presses(xev_log)
        (session / "foreign-keys.jsonl").write_text(
            "".join(json.dumps(p) + "\n" for p in foreign))
        assert [p["keysym"] for p in foreign] == ["x", "y", "z"], foreign
        # DW1: a burst snapshot after each key burst (keys grouped by the recorder's quiet gap)
        index = [json.loads(line) for line in (session / "index.jsonl").read_text().splitlines()]
        bursts = [entry for entry in index if entry["origin"] == "burst"]
        t0 = meta["monotonic_start_s"]
        quiet = meta.get("burst_quiet_s", recorder.BURST_QUIET_S)
        margin = meta.get("capture_margin_s", recorder.CAPTURE_MARGIN_S)
        groups = group_presses(events, quiet)
        ok, why = check_bursts(groups, bursts, t0)
        assert ok, why
        # Sol r2 R2a: request-window timing per group (not clustered after every group) ...
        ok, why = check_request_windows(groups, bursts, t0, margin)
        if not ok:
            print(f"acceptance guard FAILED: {why}", file=sys.stderr)
            return 1
        # ... and R2b/R2c: mapped coverage — reject a sitting whose presses do not all map
        sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))
        import keymap
        result = keymap.read_session(session)
        ok, why = check_mapped(result)
        if not ok:
            print(f"acceptance guard FAILED: {why}", file=sys.stderr)
            return 1
        print(f"map coverage OK: {why}", flush=True)
        print(f"privacy OK: {'/'.join(keys)} game keys only; outer-app x/y/z excluded "
              f"(xev log holds them; outer raw reader saw {raw_presses} RawKeyPress); "
              f"burst snapshots: {len(bursts)} for {len(groups)} key group(s)", flush=True)
        print(f"gaps (s): {gaps}", flush=True)
        print(f"session: {session.relative_to(ROOT)}", flush=True)
        subprocess.run(["python3", "experiments/E015-human-playthrough/keymap.py", str(session)], check=True)
        return 0
    finally:
        for proc in (sitting, app, raw_outer, outer):
            recorder.terminate(proc)


if __name__ == "__main__":
    sys.exit(main())
