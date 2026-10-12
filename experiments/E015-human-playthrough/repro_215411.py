#!/usr/bin/env python3
"""T39b (Scope 6, 7): replay the shape of the owner's test sitting 20261011-215411's third pause
and its end on private displays (never :99, never the owner's), to find why pauses.jsonl holds no
third resume and meta.json no `ended`/`stop_reason`.

    python3 experiments/E015-human-playthrough/repro_215411.py [--end close|none]

The keys follow that sitting's keys.jsonl (+211.9 s to +237.9 s): F12 held with the host's
autorepeat (press/release pairs every 25 ms), P, keys typed while paused (Up, Down, Shift,
Control, Num_Lock), F12 held again with P four times; then, ~30 s later, an XTEST Pause key down
and up with the game window focused (the main session's resume at about 19:58:40Z); then the
Xephyr window is closed on the outer display (the owner's end). Prints pauses.jsonl, the tail of
keys.jsonl, meta.json's end fields and the recorder's own output."""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--end", choices=("close", "none"), default="close")
    ap.add_argument("--play-args", default="", help="extra play.sh arguments (e.g. --fresh)")
    a = ap.parse_args()
    recorder.driver.require_dosbox()
    before = set(recorder.SESSIONS.glob("*"))
    outer = sitting = None
    out_path = ROOT / "scratch" / f"repro-215411-{os.getpid()}.out"
    try:
        for number in range(800, 820):
            outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     start_new_session=True)
            time.sleep(2)
            if outer.poll() is None:
                break
        env = dict(os.environ, DISPLAY=f":{number}")
        sitting = subprocess.Popen(["bash", "runtime/human/play.sh", *a.play_args.split(),
                                    "--quit-after", "150"], cwd=ROOT, env=env,
                                   stdout=open(out_path, "w"), stderr=subprocess.STDOUT,
                                   start_new_session=True)
        deadline = time.monotonic() + 60
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
            time.sleep(0.2)
        else:
            raise RuntimeError("no opening snapshot")
        child = dict(env, DISPLAY=meta["display"])
        wid = meta["window_id"]

        def x(*args):
            subprocess.run(["xdotool", *args], env=child, check=True)

        def tap(k, hold=0.08):
            x("keydown", k)
            time.sleep(hold)
            x("keyup", k)

        def f12_autorepeat(n_p):
            x("keydown", "F12")
            time.sleep(0.4)
            for _ in range(15):          # the host's autorepeat: release/press every 25 ms
                x("keyup", "F12")
                x("keydown", "F12")
                time.sleep(0.02)
            for _ in range(n_p):
                tap("p")
                time.sleep(0.08)
            time.sleep(0.3)
            x("keyup", "F12")

        x("windowfocus", wid)
        time.sleep(8)
        tap("a")
        time.sleep(2)
        f12_autorepeat(1)                # the owner's pause 3 (+211.9 s)
        time.sleep(1)
        for k in ("Up", "Down", "Up", "Shift_L", "Up", "Num_Lock", "Control_L", "Down"):
            tap(k)
            time.sleep(0.3)
        time.sleep(10)
        f12_autorepeat(4)                # the owner's F12+P x4 while paused (+236 s)
        time.sleep(30)
        title = subprocess.run(["xdotool", "getwindowname", wid], env=child, capture_output=True,
                               text=True).stdout.strip()
        print("title before the XTEST Pause:", title, flush=True)
        x("windowfocus", wid)
        x("keydown", "Pause")
        time.sleep(0.05)
        x("keyup", "Pause")              # the main session's resume (~19:58:40Z)
        time.sleep(3)
        title = subprocess.run(["xdotool", "getwindowname", wid], env=child, capture_output=True,
                               text=True).stdout.strip()
        print("title after the XTEST Pause:", title, flush=True)
        time.sleep(5)
        if a.end == "close":
            xw = meta["xephyr_window_id"]
            subprocess.run(["xdotool", "windowkill", xw], env=env)   # the owner closes the window
            print("closed the Xephyr window", flush=True)
        try:
            print("play.sh exit:", sitting.wait(timeout=200), flush=True)
        except subprocess.TimeoutExpired:
            print("play.sh still running after 200 s", flush=True)
        print("session:", session.relative_to(ROOT), flush=True)
        print("pauses.jsonl:", (session / "pauses.jsonl").read_text() if
              (session / "pauses.jsonl").exists() else None, flush=True)
        keys = [json.loads(line) for line in (session / "keys.jsonl").read_text().splitlines()]
        print("last keys:", [(round(e["monotonic_s"] - meta["monotonic_start_s"], 2), e["event"],
                              e["keysym"], e.get("by")) for e in keys[-6:]], flush=True)
        meta = json.loads((session / "meta.json").read_text())
        print("meta end:", {k: meta.get(k) for k in ("ended", "stop_reason", "problems")},
              flush=True)
        print("recorder output (tail):\n" + "\n".join(
            line for line in out_path.read_text(errors="replace").splitlines()
            if not line.startswith("LOG:"))[-3000:], flush=True)
        return 0
    finally:
        recorder.terminate(sitting)
        recorder.terminate(outer)


if __name__ == "__main__":
    sys.exit(main())
