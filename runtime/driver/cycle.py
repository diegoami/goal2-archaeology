#!/usr/bin/env python3
"""G-M1 cycle (E002): restore a start state -> key -> screen read -> reset, one run/1 record per cycle.

    python3 runtime/driver/cycle.py --runs 10 --start-state title [--key n] [--out runs/E002] [--dry]

Each cycle is one DOSBox-X process (driver.Driver): launch to the title screen, displace it with
the key, restore the start state with Host+L (polled until the stored screen digest is back: the
`before` read), press the key and poll until the screen settles (the `after` read), restore again
(the `reset` read), terminate. Every read records the host UTC and local time, the screen digest
and text, and the BIOS video mode byte (0040:0049) and timer tick count (0040:006C) as I1 memory
reads from the same savestate. Records are raw; the host clock is recorded, not controlled.
A record is written only when runtime/driver/ has no uncommitted change, so `code_commit` names the
code that ran, and an existing record is never overwritten (L207)."""
import argparse
import json
import platform
import re
import subprocess
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import driver  # noqa: E402

ROOT = driver.ROOT
EXPERIMENT = "E002"


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def machine_id():
    d = {}
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            k, _, v = line.partition("=")
            d[k] = v.strip('"')
    except OSError:
        pass
    mid = f"{d.get('ID', 'linux')}-{d.get('VERSION_ID', 'x')}".replace(".", "-")
    if "microsoft" in platform.release().lower():
        mid += "-wsl2"
    return re.sub(r"[^a-z0-9-]", "-", mid.lower())


def tool_first_line(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return ((p.stdout + p.stderr).strip().splitlines() or ["unknown"])[0]
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"unavailable ({type(e).__name__})"


def fingerprint(d, conf_sha):
    dbx = tool_first_line([driver.dosbox_x(), "-version"]).replace("DOSBox-X version ", "").split(",")[0]
    fp = {"dosbox-x": re.sub(r"[/\\]", "-", dbx),
          "xvfb": tool_first_line(["dpkg-query", "-W", "-f=${Version}", "xvfb"]),
          "xdotool": tool_first_line(["xdotool", "--version"]),
          "python": platform.python_version(), "kernel": platform.release(),
          "config_sha256": conf_sha}
    fp.update({k: str(v) for k, v in d.config.items()})
    return {k: re.sub(r"[/\\]", "-", v) for k, v in fp.items()}


def read_observations(step, label, times, state):
    """The raw observations of one read: host clock, screen, BIOS mode byte and tick count."""
    sc = state.screen()
    ticks, raw = state.ticks()
    return [
        {"step": step, "source": "log", "field": f"{label}: host UTC time just before the savestate was requested", "value": times["utc"]},
        {"step": step, "source": "log", "field": f"{label}: host local time with UTC offset, and zone name, at the same instant",
         "value": f"{times['local']} {times['tz']}"},
        {"step": step, "source": "screen", "field": f"{label}: text screen 80x25, chars+attributes (4000 bytes), sha256", "value": sc.digest()},
        {"step": step, "source": "ui-text", "field": f"{label}: text screen rows 0-24, CP437 decoded, trailing blanks trimmed", "value": sc.text()},
        {"step": step, "source": "memory", "addr": "0x449", "field": f"{label}: 1 byte at 0040:0049 (BIOS video mode), guest memory from the savestate, hex",
         "value": f"{state.video_mode():02x}"},
        {"step": step, "source": "memory", "addr": "0x46c", "field": f"{label}: 4 bytes at 0040:006C (BIOS timer tick count), guest memory from the savestate, as a little-endian dword (bytes in memory order)",
         "value": f"0x{ticks:08x} ({raw.hex(' ')})"},
    ]


def dosbox_out(d):
    try:
        text = (d.workdir / "dosbox.out").read_text(errors="replace")
        return text.replace(str(d.workdir), "<work>").replace(str(d.game_dir), "<game>").replace(str(ROOT), "<repo>")
    except OSError:
        return ""


def one_cycle(n, st, key, out_dir, commit, dry):
    run_id = f"{EXPERIMENT}-r{n:04d}"
    d = driver.Driver(st.config, workdir=driver.SCRATCH / "cycle" / run_id)  # per run: its dosbox.out is kept in scratch/
    obs, status = [], "completed"
    recorded = set()  # ids of the reads already in obs

    def add(step, label, read):
        recorded.add(id(read))
        obs.extend(read_observations(step, label, *read))

    try:
        d.launch(st, displace_key=key)
        add(0, "before restore (title screen displaced by the key)", d.pre_restore)
        obs.append({"step": 0, "source": "save", "field": "screen sha256 stored with the start state", "value": st.screen_digest})
        add(0, "before", d.last)  # the read whose digest matched after Host+L
        before = d.last[1].screen()
        d.keys(key)
        d.settle(before.digest(), what=f"after key {key}")
        add(1, "after", d.last)
        d.restore(st)
        add(2, "reset (Host+L again)", d.last)
    except Exception as e:  # noqa: BLE001
        status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
        traceback.print_exc()
        # an aborted record keeps the reads it made: the one before the restore and the last complete one
        if d.pre_restore is not None and id(d.pre_restore) not in recorded:
            add(0, "before restore (title screen displaced by the key)", d.pre_restore)
        if d.last is not None and id(d.last) not in recorded:
            add(3, "last complete read before the abort", d.last)
    finally:
        if d.launched:
            obs[:0] = [{"step": 0, "source": "log", "field": "host UTC time at launch", "value": d.launched["utc"]},
                       {"step": 0, "source": "log", "field": "host local time at launch, with UTC offset, and zone name",
                        "value": f"{d.launched['local']} {d.launched['tz']}"}]
        gone = d.terminate()
    conf_text, conf_sha = d.conf_public() if getattr(d, "conf", None) else ("not written", "0" * 64)
    obs += [
        {"step": 0, "source": "file", "field": "DOSBox-X config of the session, host paths replaced by <work> and <game>", "value": conf_text},
        {"step": 0, "source": "file", "field": "sha256 of that config text (UTF-8)", "value": conf_sha},
        {"step": 3, "source": "log", "field": "lines of DOSBox-X's own output (dosbox.out) that mention save, load or corrupt (Save_Remark lines left out), in order",
         "value": "\n".join(l for l in dosbox_out(d).splitlines() if any(w in l.lower() for w in ("save", "load", "corrupt")) and "Save_Remark" not in l)},
        {"step": 3, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups (SIGKILL to the group after 0.5 s when SIGTERM is ignored, see log)",
         "value": "both exited" if gone else "a process remained"},
        {"step": 3, "source": "log", "field": "waits, polls and key holds, seconds since launch", "value": json.dumps(d.events, separators=(",", ":"))},
    ]
    obs.sort(key=lambda o: o["step"])
    record = {
        "schema": "run/1", "run_id": run_id, "experiment": EXPERIMENT, "arm": f"restore-{st.name}-key-{key}", "rep": n,
        "code_commit": commit, "machine": machine_id(),
        "artifact": {"set": driver.verify_release(driver.CACHE), "variant": None},
        "runtime": {"driver": f"runtime/driver/driver.py@{commit}", "platform": f"python-{platform.python_version()}/{machine_id()}",
                    "fingerprint": fingerprint(d, conf_sha)},
        "interventions": [
            {"level": "I1", "what": "text screen and BIOS data area (0040:0049, 0040:006C) read from DOSBox-X savestates (Host+S; components Vga and Memory)"},
            {"level": "I2", "what": "a savestate is written at each read, and one is loaded (Host+L) at the start and at the reset (vocabulary/interventions.md lists save and load of state as I2; neutrality not tested)"},
        ],
        "start_state": {
            "id": st.name, "sha256": st.sha256,
            "restore": (f"fresh DOSBox-X process (config sha256 {conf_sha}) with C: mounted from the folder the savestate was made with, "
                        f"recreated from the verified release copy; GOAL run to its title screen; key {key} to change the screen; "
                        f"then Host+L (host key F12+L) loads the savestate whose sha256 is given; polled until the screen digest equals the one stored "
                        f"with it ({st.screen_digest}); host clock and seed not controlled"),
        },
        "seed": None,
        "actions": {"script": "runtime/driver/cycle.py", "sha256": driver.sha256(Path(__file__).read_bytes()),
                    "args": ["--start-state", st.name, "--key", key]},
        "observations": obs, "outputs": [],
        "started": d.launched["utc"] if d.launched else driver.host_times()["utc"],
        "ended": driver.host_times()["utc"], "status": status,
    }
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if str(ROOT) in text:
        raise SystemExit(f"{run_id}: a host path leaked into the record")
    if dry:
        print(text)
    else:
        with open(out_dir / f"{run_id}.json", "x", encoding="utf-8") as f:  # never overwrite (L207)
            f.write(text)
        print(f"{run_id}: {status}")
    return status == "completed"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--start-state", default="title")
    ap.add_argument("--key", default="n")
    ap.add_argument("--out", default=f"runs/{EXPERIMENT}")
    ap.add_argument("--dry", action="store_true", help="print the record, write nothing")
    a = ap.parse_args(argv)
    dirty = git("status", "--porcelain", "--", "runtime/driver")
    if dirty and not a.dry:
        raise SystemExit("uncommitted changes under runtime/driver/: commit them first so code_commit names the code that ran\n" + dirty)
    commit = git("rev-parse", "--short", "HEAD")
    try:
        st = driver.StartState(a.start_state)
    except FileNotFoundError:
        print(f"start state {a.start_state} not stored yet: making it", file=sys.stderr)
        st = driver.make_state(a.start_state)
    try:
        driver.Driver(st.config).check_start_state(st)  # refuse an incompatible state before any record
    except driver.StateLayoutMismatch as e:
        raise SystemExit(f"refused: {e}") from None
    out_dir = ROOT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    first = 1 + max((int(p.stem.split("-r")[1]) for p in out_dir.glob(f"{EXPERIMENT}-r*.json")), default=0)
    ok = sum(one_cycle(first + i, st, a.key, out_dir, commit, a.dry) for i in range(a.runs))
    print(f"{ok} of {a.runs} cycles completed")
    return 0 if ok == a.runs else 1


if __name__ == "__main__":
    sys.exit(main())
