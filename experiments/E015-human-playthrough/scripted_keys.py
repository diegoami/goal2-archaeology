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
burst/request-window behaviour the map rules handle); `--sleep N` replaces the draw with a fixed
N-second gap, the r3-era 2 s pacing (T35 Done-when 4).
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


def check_attribution(requests, session=None, index=(), write_events_total=None):
    """The acceptance guard, attribution half (Sol delta r3 R2, r4 R2; T35 issue #111): no save
    request may be superseded — a request whose capture found a later request's write already on
    the live savestate staged nothing and the screen boundary it was sent to catch is lost. The old
    guard certified that sitting ("every press mapped", "10 for 10") because it trusted the
    recorder's request windows; with a superseded request those windows are exactly what is
    wrong.

    r4 R2: absence of `superseded` is NOT ownership evidence — the r4 bypasses staged a later
    request's bytes with ordinary successful lines. Every STAGED request must carry the
    recorder's write accounting: `pre_events`/`accept_events` with at most one save's worth of
    write events in between (ONE_SAVE_MAX_EVENTS; one real save is ~53-54 events on this host,
    evidence/E015/T34-probe-closes-20261009-01.log), staged requests owning strictly increasing
    write counts (the single serialized writer answers requests in order), and — when the
    session folder is given — a per-request savestate whose bytes hash to the recorded
    request_sha256 and to the staged snapshot's own sha256. The check is on this accounting,
    never on hash uniqueness: legitimately identical screens (a 20 s cadence snapshot between
    key groups) still pass.

    T35 (issue #111 R2): the accounting is not enough on its own either — it is written by the
    same capture that staged the bytes, so a capture that staged a LATER request's bytes wrote
    plausible accounting beside them and the r4 review's bracketing snapshot + key event sailed
    through all four checks. The line must therefore also carry the recorder's signature PAIR:
    `pre_sig` (the live savestate's signature hash taken before the save key was sent, via
    note_request) and `accept_sig` (its hash at the accepted capture). Either missing is an
    evidence-free line — the recorder writes both on every staged line, so absence is a line no
    capture of this tree produced — and when both are there they must DIFFER: a fresh write
    inside this request's own window. A request that staged nothing fails (Scope:
    missing-staged requests fail — its screen is not in the chain), superseded requests fail
    above, and with an index the sequence the line names must be in it (the staged snapshot
    itself) and that snapshot's request window must be THIS request's: a snapshot whose
    `request_s` is a later request's window is later-request bytes under this line, which no
    amount of green elsewhere can make this request's.

    T35 round 3 (Sol's R1 on PR 112; the owner's option A, 2026-10-11): the signature pair is
    metadata, and the per-request hash is the recorder's own record of whatever it staged, so
    neither binds the bytes to THIS request's save. The kernel's write count does: the single
    serialized writer answers requests in order, one save each (ONE_SAVE_MIN_EVENTS to
    ONE_SAVE_MAX_EVENTS write events), so every save in the sitting must be owned by exactly one
    staged line, in order: no save before the first line, each line's accept count exactly one
    save past the previous staged line's (past its own pre-send count for the first), and — with
    the session — the recorder's `write_events_total` leaving no save after the last line.
    Bytes of a later save under an earlier line leave a save owned twice or by no line, and fail
    here. Returns (ok, message)."""
    lost = [i for i, r in enumerate(requests) if r.get("superseded")]
    if lost:
        return False, (f"request attribution lost: lost boundary at request line(s) {lost} "
                       f"(request_s {[requests[i]['request_s'] for i in lost]}): another "
                       "request's savestate write completed first")
    by_seq = {e.get("seq"): e for e in index if isinstance(e, dict)}
    seen = None
    for i, r in enumerate(requests):
        if r.get("seq") is None:
            # T35 (issue #111 R2, Scope: missing-staged requests fail): a request line with
            # no staged entry is a screen the recorder could not see — the boundary it was
            # sent to catch is not in the chain. Certifying it would certify a boundary this
            # request never owned; superseded lines are caught above with their own reason.
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) staged nothing: no snapshot carries this "
                           "request's window (evidence-free)")
        pre, acc = r.get("pre_events"), r.get("accept_events")
        if pre is None or acc is None:
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) staged without ownership evidence: no write "
                           "accounting ties the staged bytes to this request's own save")
        pre_sig, accept_sig = r.get("pre_sig"), r.get("accept_sig")
        if pre_sig is None:
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) staged without the request's pre-send state "
                           "hash (no pre_sig): an evidence-free line — nothing ties the "
                           "staged bytes to the live savestate this request was sent against")
        if accept_sig is None:
            # T35 sweep, the same class as the missing pre_sig: the recorder writes the
            # signature PAIR on every staged line (capture always returns an accept-time
            # signature), so a line with only half of it is evidence-free the same way —
            # the absence of one side of the evidence is never evidence.
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) staged without the accept-time state hash "
                           "(no accept_sig): an evidence-free line — nothing ties the "
                           "staged bytes to a fresh write inside this request's window")
        if pre_sig == accept_sig:
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) records the accept-time state equal to its "
                           "pre-send state: no write happened inside this request's window "
                           "(evidence-free)")
        if acc <= pre:
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) records no write between its send and its "
                           "staging")
        if acc - pre > recorder.ONE_SAVE_MAX_EVENTS:
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) spans {acc - pre} write events — more than "
                           f"one save's bound of {recorder.ONE_SAVE_MAX_EVENTS}: a later "
                           "request's savestate was staged under this window")
        if seen is not None and acc <= seen:
            return False, (f"request attribution lost: request lines do not own distinct "
                           f"writes (accept_events not increasing at line {i})")
        if seen is None and pre >= recorder.ONE_SAVE_MIN_EVENTS:
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) was sent {pre} write events into the sitting: "
                           "a save before the first request is owned by no request line")
        step = acc - (pre if seen is None else seen)
        if not (recorder.ONE_SAVE_MIN_EVENTS <= step <= recorder.ONE_SAVE_MAX_EVENTS):
            return False, (f"request attribution lost: request line {i} (request_s "
                           f"{r['request_s']}) accepted {step} write events past the previous "
                           f"staged request, not exactly one save ({recorder.ONE_SAVE_MIN_EVENTS}"
                           f"-{recorder.ONE_SAVE_MAX_EVENTS}): its bytes are another save's")
        seen = acc
        if session is not None:
            name = r.get("request_file")
            if not name:
                return False, (f"request attribution lost: request line {i} (request_s "
                               f"{r['request_s']}) names no per-request savestate")
            path = Path(session) / name
            if not path.is_file() or recorder.sha256(path.read_bytes()) != r.get("request_sha256"):
                return False, (f"request attribution lost: request line {i} (request_s "
                               f"{r['request_s']}): the per-request savestate is missing or "
                               "not the recorded bytes")
        if index:
            entry = by_seq.get(r.get("seq"))
            if entry is None:
                return False, (f"request attribution lost: request line {i} (request_s "
                               f"{r['request_s']}) names sequence {r.get('seq')}, which the "
                               "index does not hold: the staged snapshot is missing")
            if entry.get("sha256") != r.get("request_sha256"):
                return False, (f"request attribution lost: request line {i} (request_s "
                               f"{r['request_s']}): the staged snapshot's bytes differ from "
                               "the per-request savestate")
            if entry.get("request_s") != r.get("request_s"):
                return False, (f"request attribution lost: request line {i} (request_s "
                               f"{r['request_s']}) staged the snapshot of a LATER request's "
                               f"window (snapshot request_s {entry.get('request_s')}): the "
                               "staged bytes are evidence-free for this request")
    if session is not None and write_events_total is None:
        return False, ("request attribution lost: the sitting records no write_events_total: "
                       "nothing proves every save is owned by a request line (evidence-free)")
    if write_events_total is not None:
        rest = write_events_total - (seen if seen is not None else 0)
        if rest >= recorder.ONE_SAVE_MIN_EVENTS:
            return False, (f"request attribution lost: {rest} write events after the last staged "
                           "request: a save no request line owns, so a staged line holds "
                           "another save's bytes")
    return True, f"{len(requests)} save requests, every staged request owns its savestate bytes"


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
    ap.add_argument("--sleep", type=float, default=None,
                    help="a fixed gap between game keys (s), instead of the draw: the r3-era "
                         "2 s-paced reproduction runs as --sleep 2 (T35 Done-when 4)")
    a = ap.parse_args()
    # the calibrated emulator or nothing (#117): another version's savestates cannot be read, and
    # the sitting would fail only at extraction, after every key was typed
    try:
        recorder.driver.require_dosbox()
    except RuntimeError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
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
                gap = a.sleep if a.sleep is not None else rng.uniform(a.gap_min, a.gap_max)
                gaps.append(round(gap, 3))
                time.sleep(gap)
            subprocess.run(["xdotool", "key", key], env=child, check=True)
        # R3's real-key half: xev holds the outer focus and receives real XTEST keys
        other = subprocess.check_output(["xdotool", "search", "--name", "T34-other-app"], env=env, text=True).split()[0]
        subprocess.run(["xdotool", "key", "--window", other, "x"], env=env, check=True)
        subprocess.run(["xdotool", "windowfocus", "--sync", other], env=env, check=True)
        subprocess.run(["xdotool", "key", "y", "z"], env=env, check=True)
        assert sitting.wait(timeout=quit_after + 40) == 0
        # the sitting's final meta.json: the copy read while the sitting started holds no
        # write_events_total, which the recorder writes only once the emulator is gone (T35 r3)
        meta = json.loads((session / "meta.json").read_text())
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
        # Sol delta r3 R2: per-request attribution FIRST — a superseded request (its bytes
        # taken by a later request's write) rejects the sitting before any coverage is
        # claimed; the count checks below would only crash on the missing snapshots
        request_lines = []
        if (session / "requests.jsonl").is_file():
            request_lines = [json.loads(line) for line in
                             (session / "requests.jsonl").read_text().splitlines() if line.strip()]
        ok, why = check_attribution(request_lines, session=session, index=index,
                                    write_events_total=meta.get("write_events_total"))
        if not ok:
            print(f"acceptance guard FAILED: {why}", file=sys.stderr)
            return 1
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
