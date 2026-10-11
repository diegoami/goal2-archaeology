#!/usr/bin/env python3
"""T39b rehearsal of the owner's test sitting, on private displays (never :99, never the owner's):
the recorder (play.sh) under a private Xvfb, keys typed into the game window on its nested
display as real XTEST keys, two pauses (F12+P, resumed with the Pause key), the second typed in
the middle of a key burst, a key typed while paused, two notes (note.py) and two live views
(live.py) while the sitting runs. Then the checks the owner's record must pass:

- pauses.jsonl holds pause, resume, pause, resume, and the index a `resume` snapshot after each;
- no save request opened while DOSBox-X was paused;
- the presses in keys.jsonl are the keys typed (privacy: nothing else);
- live.py printed the newest screen twice and left nothing in the session folder but the
  recorder's own files and the notes.

    python3 experiments/E015-human-playthrough/scripted_pause.py

Prints the session folder; extract it with extract.py --runs-dir <scratch dir> (a rehearsal is not
an E015 record)."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder  # noqa: E402

HOLD = 0.12     # a human's key hold, about; the G1 driver holds host-key steps 0.15 s
RECORDER_FILES = {"cap", "dosclock", "game", "snapshots", "requests", "dosbox.conf", "mapper.map",
                  "meta.json", "session.log", "keys.jsonl", "index.jsonl", "requests.jsonl",
                  "pauses.jsonl", "state.sav", "notes.jsonl"}
XDOTOOL_MODIFIERS = {"Alt_L", "Alt_R", "Shift_L", "Shift_R", "Control_L", "Control_R"}


def main():
    try:
        recorder.driver.require_dosbox()
    except RuntimeError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    before = set(recorder.SESSIONS.glob("*"))
    outer = sitting = None
    try:
        for number in range(780, 800):
            outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                     start_new_session=True)
            time.sleep(2)
            if outer.poll() is None:
                break
        env = dict(os.environ, DISPLAY=f":{number}")
        quit_after = 70
        sitting = subprocess.Popen(["bash", "runtime/human/play.sh", "--quit-after", str(quit_after)],
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
        wid = meta["window_id"]

        def x(*args):
            subprocess.run(["xdotool", *args], env=child, check=True)

        def key(name):
            x("keydown", name)
            time.sleep(HOLD)
            x("keyup", name)

        def pause_chord():
            x("keydown", "F12")
            time.sleep(HOLD)
            key("p")
            time.sleep(HOLD)
            x("keyup", "F12")

        def note(text):
            subprocess.run([sys.executable, "runtime/human/note.py", str(session), text],
                           cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

        def live_view(n):
            out = subprocess.run([sys.executable, "runtime/human/live.py", str(session)], cwd=ROOT,
                                 check=True, capture_output=True, text=True).stdout
            print(f"--- live.py call {n} ---\n{out}", flush=True)
            return out

        typed = []
        x("windowfocus", wid)
        time.sleep(8)                      # GOAL boots to its title screen
        key("a"); typed.append("a")
        time.sleep(1.5)
        # pause 1, typed after a settled burst
        pause_chord(); typed += ["F12", "p"]
        time.sleep(1.0)
        first = live_view(1)
        note("rehearsal note 1: paused on the title screen")
        time.sleep(3)
        key("x"); typed.append("x")       # typed while paused: DOSBox-X drops it
        time.sleep(1)
        key("Pause"); typed.append("Pause")
        time.sleep(3)
        note("rehearsal note 2: resumed")
        # pause 2, in the middle of a burst: b, then F12+P 0.2 s later
        key("b"); typed.append("b")
        time.sleep(0.2)
        pause_chord(); typed += ["F12", "p"]
        time.sleep(4)
        key("Pause"); typed.append("Pause")
        time.sleep(3)
        key("c"); typed.append("c")
        time.sleep(2)
        second = live_view(2)
        assert sitting.wait(timeout=quit_after + 60) == 0
        meta = json.loads((session / "meta.json").read_text())
        t0 = meta["monotonic_start_s"]
        pauses = [json.loads(line) for line in (session / "pauses.jsonl").read_text().splitlines()]
        spans = [(p["monotonic_s"], r["monotonic_s"]) for p, r in zip(pauses[0::2], pauses[1::2])]
        print("pauses.jsonl:", json.dumps(pauses), flush=True)
        assert [p["event"] for p in pauses] == ["pause", "resume"] * 2, pauses
        index = [json.loads(line) for line in (session / "index.jsonl").read_text().splitlines()]
        requests = [json.loads(line) for line in (session / "requests.jsonl").read_text().splitlines()]
        print("snapshots:", [(e["seq"], e["origin"], e["request_s"]) for e in index], flush=True)
        for lo, hi in spans:
            inside = [r for r in requests if lo <= t0 + r["request_s"] <= hi]
            assert not inside, ("a save request opened while paused", inside)
            after = [e for e in index if e["origin"] == "resume" and t0 + e["request_s"] >= hi]
            assert after, ("no resume snapshot after the pause ending", hi)
        events = [json.loads(line) for line in (session / "keys.jsonl").read_text().splitlines()]
        presses = [e["keysym"] for e in events if e["event"] == "press"]
        print("presses:", presses, flush=True)
        # xdotool presses a modifier of its own before F12 on the nested display (Alt_L in the
        # -01 run: its keysym lookup, not a key the rehearsal typed); a keyboard sends none
        added = [k for k in presses if k in XDOTOOL_MODIFIERS]
        assert [k for k in presses if k not in XDOTOOL_MODIFIERS] == typed, (presses, typed)
        print(f"modifiers xdotool added: {added}", flush=True)
        assert "newest snapshot" in first and "newest snapshot" in second
        extra = {p.name for p in session.iterdir()} - RECORDER_FILES
        assert not extra, ("files in the session no recorder or note wrote", extra)
        notes = (session / "notes.jsonl").read_text().splitlines()
        assert len(notes) == 2, notes
        print(f"rehearsal OK: 2 pauses, {len(index)} snapshots, {len(presses)} presses, 2 notes",
              flush=True)
        print(f"session: {session.relative_to(ROOT)}", flush=True)
        return 0
    finally:
        recorder.terminate(sitting)
        recorder.terminate(outer)


if __name__ == "__main__":
    sys.exit(main())
