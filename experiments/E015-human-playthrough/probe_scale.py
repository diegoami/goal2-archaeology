#!/usr/bin/env python3
"""#148's live check: play.sh --scale N on a private Xvfb (2600x1500, never :99 or :0), the game
window's size on the nested display read with xwininfo every few seconds, then the sitting ends.
Prints one line per read; the PR's evidence is this output (probe-scale-<date>.log beside it)."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "human"))
import recorder  # noqa: E402


def geometry(env, wid):
    out = subprocess.run(["xwininfo", "-id", str(wid)], env=env, capture_output=True, text=True).stdout
    get = lambda k: next((l.split(":")[1].strip() for l in out.splitlines() if l.strip().startswith(k)), "?")
    return f"{get('Width')}x{get('Height')}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=int, required=True)
    a = ap.parse_args()
    before = set(recorder.SESSIONS.glob("*"))
    outer = sitting = None
    try:
        for number in range(800, 820):
            outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "2600x1500x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(2)
            if outer.poll() is None:
                break
        env = dict(os.environ, DISPLAY=f":{number}")
        sitting = subprocess.Popen(["bash", "runtime/human/play.sh", "--scale", str(a.scale), "--fresh",
                                    "--quit-after", "30"], cwd=ROOT, env=env, start_new_session=True,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline, meta = time.monotonic() + 60, None
        while time.monotonic() < deadline:
            fresh = set(recorder.SESSIONS.glob("*")) - before
            if fresh:
                session = fresh.pop()
                try:
                    meta = json.loads((session / "meta.json").read_text())
                    if meta.get("window_id"):
                        break
                except (OSError, json.JSONDecodeError):
                    pass
            time.sleep(0.2)
        else:
            raise RuntimeError("no game window in 60 s")
        child = dict(env, DISPLAY=meta["display"])
        print(f"scale {a.scale}: session {session.name}, meta scale {meta.get('scale')}, nested display "
              f"{meta['display']}, config has scaler: {'scaler=normal' in meta['config']}", flush=True)
        start = time.monotonic()
        for t in (3, 8, 15, 22):
            time.sleep(max(0, start + t - time.monotonic()))
            print(f"  +{t:2d}s game window {geometry(child, meta['window_id'])}", flush=True)
        sitting.wait(timeout=60)
        return 0
    finally:
        for p in (sitting, outer):
            if p is not None and p.poll() is None:
                p.terminate()


if __name__ == "__main__":
    sys.exit(main())
