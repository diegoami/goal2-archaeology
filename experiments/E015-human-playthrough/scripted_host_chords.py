#!/usr/bin/env python3
"""Fix #175 rehearsal, on private displays (never the owner's): the recorder (play.sh) under a private
Xvfb; GOAL is advanced past its start screen, then F12 is held (as the recorder's F12+S save send
holds it) and R and L are typed inside that hold, the reproduction of issue 175 (R inside the
send window was F12+R, hand_reset). The game screen (live.py's newest snapshot) before and after
must be equal and GOAL still running. Run against the fixed mapper the screens are equal; against
the default one (mapper.map from the unmodified default binds, `--mapper default`, which swaps
runtime/human/recorder.py's HOST_BINDS_KEPT for a pass-through in a scratch copy of the recorder)
the machine resets.

    python3 experiments/E015-human-playthrough/scripted_host_chords.py [--mapper fixed|default]
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
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
        env = dict(os.environ, DISPLAY=f":{number}")
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

        def screen():
            time.sleep(2.5)   # a snapshot after the last key (burst quiet + save)
            out = subprocess.run([sys.executable, "runtime/human/live.py", str(session)], cwd=ROOT,
                                 check=True, capture_output=True, text=True).stdout
            return out.split("keys since", 1)[0] if "keys since" in out else out

        x("windowfocus", meta["window_id"])
        time.sleep(10)
        for k in filter(None, a.steps.split(",")):
            key(k); time.sleep(1.5)
        time.sleep(3)
        first = screen()
        print("--- screen before ---\n" + first, flush=True)
        # the hold: F12 down (the save send's F12), R and L typed inside it, F12 up
        x("keydown", "F12"); time.sleep(HOLD)
        key("r"); time.sleep(HOLD); key("l"); time.sleep(HOLD)
        x("keyup", "F12")
        time.sleep(12)    # long enough for a reset to reach GOAL's start screen again
        second = screen()
        print("--- screen after ---\n" + second, flush=True)
        body = lambda s: s.split("\n")[2:]
        same = body(first) == body(second)
        print(f"mapper={a.mapper} screens_equal={same} dosbox_alive={recorder_alive(sitting)}", flush=True)
        print(f"session: {session.relative_to(ROOT)}", flush=True)
        return 0 if same else 1
    finally:
        recorder.terminate(sitting)
        recorder.terminate(outer)
        p = ROOT / "runtime/human/_recorder_default_mapper.py"
        if p.exists():
            p.unlink()


def recorder_alive(p):
    return p.poll() is None


if __name__ == "__main__":
    sys.exit(main())
