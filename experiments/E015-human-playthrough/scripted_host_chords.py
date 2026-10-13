#!/usr/bin/env python3
"""Fix #175 rehearsal, on private displays (never the owner's): the recorder (play.sh) under a private
Xvfb. GOAL is advanced to PLAYER 1 SELECT YOUR COUNTRY and a stable frame is waited for (two
identical consecutive frames). A key then triggers the recorder's real save request; its
send_save_event, under the test hook GOAL2_RECORDER_TEST_SEND_HOLD_S, pauses 0.3 s after F12's real
press and stamps the edges into a file. The script polls that file and, within about a millisecond of
F12-down, taps R and L (XTEST), so R and L fall inside the real F12+S send window (the log prints
the window, the R and L stamps, and inside_window). The frame before and after must be equal and
GOAL running. The fixed mapper leaves the game where it was; the default one (--mapper default:
a scratch copy of the recorder with the host-bind strip disabled) resets the machine.

    python3 experiments/E015-human-playthrough/scripted_host_chords.py [--mapper fixed|default] --steps n,1
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder  # noqa: E402

HOLD = 0.12


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapper", choices=("fixed", "default"), default="fixed")
    ap.add_argument("--steps", default="")     # keys to advance past the start screen, comma separated
    a = ap.parse_args()
    recorder.driver.require_dosbox()
    before = set(recorder.SESSIONS.glob("*"))
    outer = sitting = None
    try:
        for number in range(800, 820):
            outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     start_new_session=True)
            time.sleep(2)
            if outer.poll() is None:
                break
        mark = Path(tempfile.mkdtemp()) / "send-mark.txt"
        env = dict(os.environ, DISPLAY=f":{number}", GOAL2_RECORDER_TEST_SEND_HOLD_S="0.3",
                   GOAL2_RECORDER_TEST_SEND_MARK=str(mark))
        entry = ["bash", "runtime/human/play.sh"]
        if a.mapper == "default":
            # the recorder as it was before the fix: the host binds of every event stay
            scratch = ROOT / "runtime/human/_recorder_default_mapper.py"
            text = (ROOT / "runtime/human/recorder.py").read_text()
            assert 'if line.startswith("hand_") and line.split' in text
            scratch.write_text(text.replace('if line.startswith("hand_") and line.split',
                                            'if False and line.split', 1))
            entry = [sys.executable, str(scratch)]
        sitting = subprocess.Popen([*entry, "--scale", "1", "--quit-after", "90", "--fresh"],
                                   cwd=ROOT, env=env, start_new_session=True)
        deadline = time.monotonic() + 60
        session = meta = None
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
            raise RuntimeError("the opening snapshot never appeared")
        child = dict(env, DISPLAY=meta["display"])
        x = lambda *args: subprocess.run(["xdotool", *args], env=child, check=True)

        def key(name):
            x("keydown", name); time.sleep(HOLD); x("keyup", name)

        x("windowfocus", meta["window_id"])
        time.sleep(8)
        for k in filter(None, a.steps.split(",")):
            key(k); time.sleep(1.5)
        seq0, first = stable(session, "SELECT YOUR COUNTRY", 0)
        print("--- screen before (stable: two identical frames, seq %d) ---\n" % seq0 + first, flush=True)
        # trigger a real save request: a key, then the recorder's burst quiet -> send_save_event
        # (F12+S via XSendEvent), held open by the test hook; R and L are typed once its F12-down
        # is stamped, so they land inside the real send window.
        quiet_since, seen = time.monotonic(), mark.read_text()
        while time.monotonic() - quiet_since < 5 or seen.count("down") != seen.count("up"):
            time.sleep(0.2)          # no send in flight, none new for 5 s
            now = mark.read_text()
            if now != seen:
                seen, quiet_since = now, time.monotonic()
        before_lines = len(seen.splitlines())
        t_end = time.monotonic() + 30
        fake = FakeKeys(meta["display"])    # one open connection: a press lands within ~1 ms
        key("Shift_L")
        t_end = time.monotonic() + 30
        while len(mark.read_text().splitlines()) <= before_lines and time.monotonic() < t_end:
            time.sleep(0.0005)
        t_r0 = time.time(); fake.tap("r"); t_r1 = time.time()
        t_l0 = time.time(); fake.tap("l"); t_l1 = time.time()
        while len(mark.read_text().splitlines()) <= before_lines + 1 and time.monotonic() < t_end:
            time.sleep(0.01)
        lines = [line.split() for line in mark.read_text().splitlines()[before_lines:]]
        down = float(lines[0][1])       # the first send's window: R and L were typed right after it
        assert lines[0][0] == "down" and lines[1][0] == "up", lines
        up = float(lines[1][1])
        eps = 0.001   # the stamps are rounded to 1 ms
        inside = down - eps <= t_r0 and t_r1 < up and down - eps <= t_l0 and t_l1 < up
        print(f"send window {down:.3f}..{up:.3f}; R {t_r0:.3f}..{t_r1:.3f}; L {t_l0:.3f}..{t_l1:.3f}; "
              f"inside_window={inside}", flush=True)
        seq1, second = stable(session, None, seq0 + 1)
        print("--- screen after (stable, seq %d) ---\n" % seq1 + second, flush=True)
        body = lambda s: s.split("\n")[2:]
        same = body(first) == body(second)
        print(f"mapper={a.mapper} inside_window={inside} screens_equal={same} "
              f"dosbox_alive={recorder_alive(sitting)}", flush=True)
        print(f"session: {session.relative_to(ROOT)}", flush=True)
        if not inside:
            return 2
        return 0 if same else 1
    finally:
        recorder.terminate(sitting)
        recorder.terminate(outer)
        p = ROOT / "runtime/human/_recorder_default_mapper.py"
        if p.exists():
            p.unlink()


class FakeKeys:
    """XTEST key taps on one open connection (libXtst through ctypes)."""
    def __init__(self, display):
        import ctypes as c
        self.x11, self.tst = c.CDLL("libX11.so.6"), c.CDLL("libXtst.so.6")
        self.x11.XOpenDisplay.restype = c.c_void_p
        self.x11.XOpenDisplay.argtypes = [c.c_char_p]
        self.x11.XKeysymToKeycode.argtypes = [c.c_void_p, c.c_ulong]
        self.x11.XFlush.argtypes = [c.c_void_p]
        self.tst.XTestFakeKeyEvent.argtypes = [c.c_void_p, c.c_uint, c.c_int, c.c_ulong]
        self.d = self.x11.XOpenDisplay(display.encode())
        assert self.d, "cannot open " + display

    def tap(self, name):
        code = self.x11.XKeysymToKeycode(self.d, ord(name))
        self.tst.XTestFakeKeyEvent(self.d, code, 1, 0)
        self.x11.XFlush(self.d)
        time.sleep(0.05)
        self.tst.XTestFakeKeyEvent(self.d, code, 0, 0)
        self.x11.XFlush(self.d)


def frame(session):
    out = subprocess.run([sys.executable, "runtime/human/live.py", str(session)], cwd=ROOT,
                         check=True, capture_output=True, text=True).stdout
    out = out.split("keys since", 1)[0] if "keys since" in out else out
    m = re.search(r"seq (\d+)", out)
    return (int(m.group(1)) if m else 0), out


def stable(session, expect, min_seq, timeout=60):
    """Poll until two consecutive frames are identical (bodies), at least min_seq, and contain
    `expect` when given; returns (seq, frame). Never a fixed sleep."""
    deadline = time.monotonic() + timeout
    prev = None
    while time.monotonic() < deadline:
        seq, out = frame(session)
        body = out.split("\n")[2:]
        if seq >= min_seq and (expect is None or expect in out) and body == prev:
            return seq, out
        prev = body if seq >= min_seq else None
        time.sleep(2)
    raise RuntimeError("no stable frame" + (f" containing {expect!r}" if expect else ""))


def recorder_alive(p):
    return p.poll() is None


if __name__ == "__main__":
    sys.exit(main())
