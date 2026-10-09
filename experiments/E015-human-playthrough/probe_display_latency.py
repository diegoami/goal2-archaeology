#!/usr/bin/env python3
"""T34 probe: the raw-key logger's delivery latency, and Xephyr's exit on a busy display.

Both numbers ground recorder.py's [designed] constants (a probe log, not a finding):
- CAPTURE_MARGIN_S bounds the delay between a key's real delivery to the nested X server and
  the logger stamping it (monotonic_s). Measured here with the logger's own KeyLogger thread
  and the main Python thread kept busy (GIL contention, the realistic worst case), keys sent
  with XTestFakeKeyEvent so the send time is not polluted by spawning xdotool.
- NESTED_START_S bounds Xephyr's window wait: a Xephyr asked for a busy display number exits
  almost immediately; measured here by starting one on an Xvfb's display number.

    python3 experiments/E015-human-playthrough/probe_display_latency.py
"""
import ctypes
import ctypes.util
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder


def private_xvfb(first, last):
    for number in range(first, last):
        proc = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "800x600x24"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        time.sleep(1)
        if proc.poll() is None:
            return proc, dict(os.environ, DISPLAY=f":{number}")
        proc.wait()
    raise RuntimeError(f"no free display in {first}..{last - 1}")


def fake_key(display, keycode, down):
    xtst = ctypes.CDLL(ctypes.util.find_library("Xtst"))
    xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int]
    xtst.XTestFakeKeyEvent.restype = ctypes.c_int
    return xtst.XTestFakeKeyEvent(display, keycode, 1 if down else 0, 0)


def main():
    outer, env = private_xvfb(810, 830)
    try:
        # Xlib handles for XTEST and the keycode
        xlib = ctypes.CDLL("libX11.so.6")
        xlib.XOpenDisplay.argtypes, xlib.XOpenDisplay.restype = [ctypes.c_char_p], ctypes.c_void_p
        xlib.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        xlib.XKeysymToKeycode.restype = ctypes.c_ubyte
        xlib.XFlush.argtypes = [ctypes.c_void_p]
        xlib.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
        display = xlib.XOpenDisplay(env["DISPLAY"].encode())
        assert display, "cannot open the probe display"
        keycode = xlib.XKeysymToKeycode(display, ord("a"))
        # the production logger, on this display only (the outer-display argument names a
        # display that does not exist and is never opened)
        log_path = Path(recorder.SELFTEST.parent / "t34-tmp") / "probe-keys.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if log_path.exists():
            log_path.unlink()
        logger = recorder.KeyLogger(env, ":65530-unused", log_path)
        logger.start()
        time.sleep(1)          # let the reader thread reach its read loop
        sends = []
        for i in range(200):
            # keep the main thread busy so the reader thread's stamping is GIL-delayed
            spin_until = time.monotonic() + 0.002
            while time.monotonic() < spin_until:
                sum(j * j for j in range(64))
            t0 = time.monotonic()
            fake_key(display, keycode, True)
            xlib.XSync(display, 0)
            fake_key(display, keycode, False)
            xlib.XSync(display, 0)
            sends.append(t0)
        time.sleep(1)          # let the last events drain
        logger.stop()
        events = [json.loads(line) for line in log_path.read_text().splitlines()]
        presses = [e for e in events if e["event"] == "press" and e["keysym"] == "a"]
        assert len(presses) == 200, f"expected 200 raw presses, saw {len(presses)}"
        latencies = sorted(e["monotonic_s"] - t0 for t0, e in zip(sends, presses))
        med = statistics.median(latencies)
        print(f"XI2 delivery latency, 200 XTEST presses, main thread busy: "
              f"median {med * 1000:.2f} ms, max {latencies[-1] * 1000:.2f} ms, "
              f"min {latencies[0] * 1000:.2f} ms")
        xlib.XCloseDisplay.argtypes = [ctypes.c_void_p]
        xlib.XCloseDisplay(display)

        # a Xephyr asked for this (busy) display number: time from spawn to exit
        starts = []
        for _ in range(5):
            t0 = time.monotonic()
            busy = subprocess.Popen(["Xephyr", env["DISPLAY"], "-screen", "800x600",
                                     "-nolisten", "tcp"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    start_new_session=True)
            busy.wait(timeout=10)
            starts.append(time.monotonic() - t0)
        print(f"Xephyr exit on a busy display number, 5 trials: "
              f"median {statistics.median(starts) * 1000:.1f} ms, max {max(starts) * 1000:.1f} ms")
        return 0
    finally:
        recorder.terminate(outer)


if __name__ == "__main__":
    sys.exit(main())
