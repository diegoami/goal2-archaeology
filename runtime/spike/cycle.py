#!/usr/bin/env python3
"""T02 spike: one launch -> one keystroke -> before/after screen read -> terminate cycle of GOAL2
under DOSBox-X in Xvfb, writing one run/1 record to runs/E001/.

    python3 runtime/spike/cycle.py [--out runs/E001] [--key n] [--dry]

Route (F001): Xvfb + DOSBox-X (surface output) + xdotool (XTEST) for input; the text screen is read
from a DOSBox-X savestate (Host+S, component Vga) and cross-checked against DOSBox-X's own PNG
capture (Host+P) on every read. Standard library only.

The run record is raw: no interpretation. Every wait is a poll for a screen (bounded) or a delay
recorded in the `log` observation. The record is written only if the working tree holds no
uncommitted change under runtime/spike/, so `code_commit` names the code that ran."""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dbx  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = "E001"
TITLE_TEXT = "Do you want to load a saved game"


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def known_set():
    return json.loads((ROOT / "artifacts/known.json").read_text())["sets"][0]["manifest"]


def verify_release(cache):
    """The release copy in .cache must match the registered set byte for byte."""
    bad = []
    for f in known_set()["files"]:
        p = Path(cache) / f["path"]
        if not p.is_file() or sha256_file(p) != f["sha256"]:
            bad.append(f["path"])
    if bad:
        raise SystemExit(f"{cache} does not match artifacts/known.json for: {', '.join(bad)} (run setup/goal2-runtime.sh)")


def tool_version(cmd, pattern=None):
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        text = (out.stdout + out.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return f"unavailable ({type(e).__name__})"
    if pattern:
        m = re.search(pattern, text)
        return m.group(1) if m else text.splitlines()[0] if text else "unknown"
    return text.splitlines()[0] if text else "unknown"


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


def log_find(session, pattern):
    """A value DOSBox-X printed to its own stdout at start (captured in dosbox.out)."""
    try:
        m = re.search(pattern, (Path(session.workdir) / "dosbox.out").read_text(errors="replace"))
        return m.group(1) if m else "not printed"
    except OSError:
        return "no log"


def fingerprint(session):
    v = subprocess.run(["dosbox-x", "-version"], capture_output=True, text=True)
    first = (v.stdout + v.stderr).strip().splitlines()[0]
    return {
        "dosbox-x": re.sub(r"[/\\]", "-", first.replace("DOSBox-X version ", "").split(",")[0]),
        "dosbox-x-build": log_find(session, r"DOSBox-X version \S+ (Commit \w+ \([^)]*\))"),
        "sdl": log_find(session, r"SDL: (version [\d.]+, Video \w+)"),
        "xvfb": tool_version(["dpkg-query", "-W", "-f=${Version}", "xvfb"]),
        "xdotool": tool_version(["xdotool", "--version"]),
        "python": platform.python_version(),
        "kernel": platform.release(),
        "machine": session.machine,
        "memsize": str(session.memsize),
        "cycles": str(session.cycles),
        "core": session.core,
        "cputype": session.cputype,
    }


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout.strip()


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def observe(session, step, obs, label):
    """Savestate read + PNG cross-check. Returns the Screen; appends raw observations."""
    sc, _ = session.screen()
    png = session.capture_png()
    size, lit = dbx.lit_cells(png)
    text_cells = {(i // dbx.COLS, i % dbx.COLS) for i, c in enumerate(sc.chars) if c not in (0, 0x20)}
    diff = len(lit ^ text_cells)
    mode, cols, rows = sc.mode
    obs += [
        {"step": step, "source": "screen", "field": f"{label}: text screen {dbx.COLS}x{dbx.ROWS}, chars+attributes (4000 bytes), sha256",
         "value": sc.digest()},
        {"step": step, "source": "ui-text", "field": f"{label}: text screen rows 0-24, CP437 decoded, trailing blanks trimmed",
         "value": sc.text()},
        {"step": step, "source": "memory", "addr": "0x449", "field": f"{label}: BIOS data area video mode, columns, rows (guest memory from savestate)",
         "value": f"mode={mode:02x} cols={cols} rows={rows}"},
        {"step": step, "source": "screen", "field": f"{label}: cells differing between DOSBox-X PNG capture ({size[0]}x{size[1]}, 9x16 cells) and non-blank text cells",
         "value": str(diff)},
    ]
    return sc


def settled_after(session, before, key_name, timeout=10):
    """After a key: poll until the screen differs from `before` and two consecutive reads agree."""
    end = time.monotonic() + timeout
    prev, polls = None, 0
    while time.monotonic() < end:
        polls += 1
        sc, _ = session.screen()
        if sc.digest() != before.digest() and prev is not None and sc.digest() == prev:
            session.log(f"after key {key_name}: screen changed and stable after {polls} polls")
            return
        prev = sc.digest() if sc.digest() != before.digest() else None
    raise RuntimeError(f"screen did not change and settle within {timeout}s after {key_name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/E001")
    ap.add_argument("--key", default="n")
    ap.add_argument("--cache", default=".cache/goal2")
    ap.add_argument("--dry", action="store_true", help="do not write a record")
    a = ap.parse_args()

    cache = ROOT / a.cache
    verify_release(cache)
    dirty = git("status", "--porcelain", "--", "runtime/spike")
    if dirty and not a.dry:
        raise SystemExit("uncommitted changes under runtime/spike/: commit them first so code_commit names the code that ran\n" + dirty)
    out_dir = ROOT / a.out
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(out_dir.glob(f"{EXPERIMENT}-r*.json"))) + 1
    run_id = f"{EXPERIMENT}-r{n:04d}"
    work = ROOT / "scratch" / "cycle" / run_id
    shutil.rmtree(work, ignore_errors=True)
    game = work / "game"
    shutil.copytree(cache, game)  # a private copy: the game may write beside itself

    started = now()
    s = dbx.Session(work / "dbx", game)
    obs = []
    status = "completed"
    try:
        s.start()
        s.wait_screen(lambda sc: TITLE_TEXT in sc.text(), timeout=30, what="title screen")
        b = observe(s, 0, obs, "before")
        s.key(a.key)
        settled_after(s, b, a.key)
        observe(s, 1, obs, "after")
    except Exception as e:  # noqa: BLE001
        status = f"aborted: {type(e).__name__}: {e}".splitlines()[0][:300]
        print(status, file=sys.stderr)
    finally:
        pids = [p.pid for p in (s.dbx, s.xvfb) if p]
        s.stop()
    gone = all(not Path(f"/proc/{pid}").exists() for pid in pids)
    ended = now()
    obs.append({"step": 2, "source": "process", "field": "dosbox-x and Xvfb after SIGTERM to their process groups, waited",
                "value": "both exited" if gone else "a process remained"})
    obs.append({"step": 2, "source": "log", "field": "waits and polls, seconds since launch (recorded delays and bounded polls)",
                "value": json.dumps(s.events, separators=(",", ":"))})
    commit = git("rev-parse", "--short", "HEAD")
    me = Path(__file__).resolve()
    record = {
        "schema": "run/1",
        "run_id": run_id,
        "experiment": EXPERIMENT,
        "arm": "fresh-launch",
        "rep": n,
        "code_commit": commit,
        "machine": machine_id(),
        "artifact": {"set": known_set()["id"], "variant": None},
        "runtime": {
            "driver": f"runtime/spike/cycle.py@{commit}",
            "platform": f"python-{platform.python_version()}/{machine_id()}",
            "fingerprint": fingerprint(s),
        },
        "interventions": [
            {"level": "I1", "what": "text screen and BIOS data area read from DOSBox-X savestates (Host+S, components Vga and Memory); screenshot (Host+P) taken once per screen"},
            {"level": "I2", "what": "a savestate is written at each read (listed I2 in vocabulary/interventions.md, claimed neutral: not tested here, see F001)"},
        ],
        "start_state": {
            "id": "fresh-launch",
            "sha256": hashlib.sha256(s.conf_text().replace(str(s.workdir), "<work>").replace(str(s.game_dir), "<game>").encode()).hexdigest(),
            "restore": "fresh DOSBox-X process from the configuration whose sha256 is given (paths replaced by <work> and <game>), mounting a copy of the release files; nothing restored; seed not controlled",
        },
        "seed": None,
        "actions": {"script": "runtime/spike/cycle.py", "sha256": sha256_file(me),
                    "args": ["--key", a.key]},
        "observations": obs,
        "outputs": [],
        "started": started,
        "ended": ended,
        "status": status,
    }
    text = json.dumps(record, indent=2, ensure_ascii=False) + "\n"
    if a.dry:
        print(text)
        return 0 if status == "completed" else 1
    (out_dir / f"{run_id}.json").write_text(text, encoding="utf-8")
    print(f"{run_id}: {status}; wrote {out_dir / (run_id + '.json')}")
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
