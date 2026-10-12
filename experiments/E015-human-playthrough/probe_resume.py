#!/usr/bin/env python3
"""T39b (Scope 5, 6): what ends DOSBox-X 2024.03.01's pause, besides the Pause key. The owner's
sitting 20261011-215411 logged a resume with no key in keys.jsonl (+86.1 s, +145.8 s); this probe
pauses with F12+P (the session mapper) on a private Xvfb and tries, one at a time, each thing that
could have resumed it, reading the window title after each:

    python3 experiments/E015-human-playthrough/probe_resume.py

- focus: another window takes the focus, then the game window again;
- click: a mouse click in the game window;
- sendevent: `xdotool key --window <wid> Pause` (XSendEvent);
- xtest-focused: `xdotool keydown/keyup Pause` (XTEST) with the game window focused;
- f12p: F12+P again (XTEST);
- a recorder save request (XSendEvent F12+S) while paused.
One JSON line per try; the DOS prompt is enough (the pause is the emulator's)."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "human"))
import recorder  # noqa: E402


def main():
    exe = recorder.driver.require_dosbox()
    work = ROOT / "scratch" / f"t39b-probe-resume-{os.getpid()}"
    work.mkdir(parents=True)
    (work / "mapper.map").write_text(recorder.mapper_text())
    (work / "probe.conf").write_text(
        f"[sdl]\nfullscreen=false\noutput=surface\nmapperfile={work / 'mapper.map'}\n"
        "[mixer]\nnosound=true\n[midi]\nmididevice=none\n[dosbox]\nsaveremark=false\n")
    xvfb = dbx = other = None
    try:
        for number in range(820, 840):
            xvfb = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    start_new_session=True)
            time.sleep(2)
            if xvfb.poll() is None:
                break
        env = dict(os.environ, DISPLAY=f":{number}")
        dbx = subprocess.Popen([exe, "-conf", str(work / "probe.conf"), "-fastlaunch", "-nogui",
                                "-nomenu", "-set", f"dosbox savefile={work / 'state.sav'}"],
                               env=env, stdout=open(work / "dbx.log", "w"), stderr=subprocess.STDOUT,
                               start_new_session=True)
        wid = recorder.find_window(env, dbx.pid, timeout=60)
        other = subprocess.Popen(["xev", "-name", "probe-other"], env=env, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(2)
        owid = subprocess.run(["xdotool", "search", "--name", "^probe-other$"], env=env,
                              capture_output=True, text=True).stdout.split()[0]

        def x(*args):
            subprocess.run(["xdotool", *args], env=env, check=True)

        def paused():
            return recorder.window_paused(wid, env)

        def pause():
            x("windowfocus", "--sync", wid)
            x("keydown", "F12")
            time.sleep(0.15)
            x("keydown", "p")
            time.sleep(0.15)
            x("keyup", "p")
            time.sleep(0.15)
            x("keyup", "F12")
            time.sleep(0.6)
            return paused()

        def resume_with_pause_key():
            x("windowfocus", "--sync", wid)
            x("keydown", "Pause")
            time.sleep(0.05)
            x("keyup", "Pause")
            time.sleep(0.6)

        tries = {
            "focus": lambda: (x("windowfocus", "--sync", owid), time.sleep(0.5),
                              x("windowfocus", "--sync", wid)),
            "click": lambda: (x("mousemove", "--window", wid, "100", "100"), x("click", "1")),
            "sendevent": lambda: x("key", "--window", wid, "Pause"),
            "save-request": lambda: recorder.send_save_event(wid, env),
            "f12p": lambda: pause(),
            "xtest-unfocused": lambda: (x("windowfocus", "--sync", owid), x("keydown", "Pause"),
                                        time.sleep(0.05), x("keyup", "Pause"),
                                        x("windowfocus", "--sync", wid)),
            "xtest-focused": lambda: resume_with_pause_key(),
        }
        for name, act in tries.items():
            was = pause()
            act()
            time.sleep(1.0)
            now = paused()
            print(json.dumps({"try": name, "paused_before": was, "paused_after": now,
                              "resumed": bool(was) and now is False}), flush=True)
            if now:
                resume_with_pause_key()
        return 0
    finally:
        for p in (other, dbx, xvfb):
            recorder.terminate(p)


if __name__ == "__main__":
    sys.exit(main())
