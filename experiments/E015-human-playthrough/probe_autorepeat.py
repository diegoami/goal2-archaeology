#!/usr/bin/env python3
"""T39b rework round 2: how a held key reaches the key logger on the nested display, with the X
server's own event times. A private Xvfb stands in for the owner's desktop and a Xephyr for the
recorder's nested display (never :99, never the owner's). `xinput test-xi2 --root` runs on the
nested display, as the recorder's logger does. A key is held on the outer display with the Xephyr
window focused, so the outer server's autorepeat reaches Xephyr as its host input, as the owner's
held keys did in sitting 20261011-215411 (release/press pairs). The probe prints each raw event
with its server time (`time:` in xinput's output), and the gaps between each repeat release and
the press after it, and between a real release and a new press.

    python3 experiments/E015-human-playthrough/probe_autorepeat.py"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    work = ROOT / "scratch" / f"t39b-probe-autorepeat-{os.getpid()}"
    work.mkdir(parents=True)
    procs = []
    try:
        for n in range(860, 880):
            outer = subprocess.Popen(["Xvfb", f":{n}", "-screen", "0", "1024x768x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     start_new_session=True)
            time.sleep(2)
            if outer.poll() is None:
                break
        procs.append(outer)
        oenv = dict(os.environ, DISPLAY=f":{n}")
        for m in range(880, 900):
            xe = subprocess.Popen(["Xephyr", f":{m}", "-screen", "640x480", "-title", f"probe-{m}"],
                                  env=oenv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                  start_new_session=True)
            time.sleep(2)
            if xe.poll() is None:
                break
        procs.append(xe)
        nenv = dict(os.environ, DISPLAY=f":{m}")
        subprocess.run(["xset", "r", "on"], env=oenv)
        subprocess.run(["xset", "r", "rate", "250", "30"], env=oenv)
        log = open(work / "xi2.out", "w")
        xi = subprocess.Popen(["stdbuf", "-oL", "xinput", "test-xi2", "--root"], env=nenv,
                              stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        procs.append(xi)
        time.sleep(1)
        wid = subprocess.run(["xdotool", "search", "--name", f"^probe-{m}$"], env=oenv,
                             capture_output=True, text=True).stdout.split()[0]
        subprocess.run(["xdotool", "windowfocus", "--sync", wid], env=oenv)
        subprocess.run(["xdotool", "mousemove", "--window", wid, "100", "100"], env=oenv)
        time.sleep(0.5)
        subprocess.run(["xdotool", "keydown", "p"], env=oenv)       # held: the outer autorepeat
        time.sleep(1.2)
        subprocess.run(["xdotool", "keyup", "p"], env=oenv)
        time.sleep(0.12)
        subprocess.run(["xdotool", "key", "p"], env=oenv)           # a separate press after it
        time.sleep(0.5)
        xi.terminate()
        xi.wait()
        events = []
        kind = None
        for line in (work / "xi2.out").read_text().splitlines():
            if line.startswith("EVENT"):
                kind = ("press" if "(RawKeyPress)" in line else
                        "release" if "(RawKeyRelease)" in line else None)
                t = None
            elif kind and line.strip().startswith("time:"):
                t = int(line.split(":", 1)[1])
            elif kind and line.strip().startswith("detail:"):
                events.append((kind, int(line.split(":", 1)[1]), t))
                kind = None
        for e in events:
            print(e)
        gaps = [b[2] - a[2] for a, b in zip(events, events[1:]) if a[0] == "release" and b[0] == "press"]
        print("release -> next press gaps (server ms):", gaps)
        return 0
    finally:
        for p in reversed(procs):
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()


if __name__ == "__main__":
    sys.exit(main())
