#!/usr/bin/env python3
"""T39b probe: how DOSBox-X 2024.03.01 behaves around its `hand_pause` event (mapper_pause, "Pause
emulation") when the session's mapper file binds it to F12+P, on a private Xvfb (never :99, never
the owner's display). It prints one JSON line per step; the log is kept beside this script.

    python3 experiments/E015-human-playthrough/probe_pause.py [--event hand_pause|hand_pauseints]

What it asks (each answered by a step's line):
- does F12+P (real XTEST keys, the way a keyboard types them) pause, and does the window title say so
  (DOSBox-X appends " PAUSED", a string in its binary)?
- while paused, does the recorder's save request (the explicit XSendEvent F12+S) write a savestate?
- does a second F12+P resume, and is a key typed while paused delivered to DOS after the resume?
- does a save requested while paused land after the resume (the hazard the recorder must avoid)?
The DOS prompt is enough: pause is the emulator's, not the game's (no GOAL2 file is read here)."""
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

HOLD = 0.15   # the G1 driver's HOSTKEY_HOLD: each step of a host-key chord is held this long


def out(**kw):
    print(json.dumps(kw), flush=True)


def x(env, *args):
    subprocess.run(["xdotool", *args], env=env, check=True)


def chord(env, key):
    """F12 held, `key` pressed and released, F12 released: the host-key chord as typed."""
    x(env, "keydown", "F12")
    time.sleep(HOLD)
    x(env, "keydown", key)
    time.sleep(HOLD)
    x(env, "keyup", key)
    time.sleep(HOLD)
    x(env, "keyup", "F12")


def typed(env, key):
    x(env, "keydown", key)
    time.sleep(0.05)
    x(env, "keyup", key)


def screen_row(path, row_hint="Z:\\>"):
    """The DOS prompt line of the savestate's text screen."""
    import savestate
    text = savestate.Savestate(Path(path).read_bytes()).screen().text()
    rows = [r for r in text.splitlines() if r.startswith(row_hint)]
    return rows[-1] if rows else None


def wait_change(path, sig, secs):
    end = time.monotonic() + secs
    while time.monotonic() < end:
        now = recorder.file_signature(path)
        if now is not None and now != sig and recorder.zip_complete(path) is not None:
            return now
        time.sleep(0.1)
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--event", default="hand_pause", choices=("hand_pause", "hand_pauseints", "minimal"),
                    help="the event F12+P is bound to: hand_pause is the recorder's session mapper "
                         "(recorder.mapper_text()); hand_pauseints ('Pause with interrupts "
                         "enabled') is the alternative, probed for comparison; minimal is a "
                         "mapper file holding the pause bind alone (does a mapper file replace "
                         "the default binds, F12+S among them?)")
    a = ap.parse_args()
    exe = recorder.driver.require_dosbox()
    work = ROOT / "scratch" / f"t39b-probe-{os.getpid()}"
    work.mkdir(parents=True)
    mapper = work / "mapper.map"
    text = recorder.mapper_text()
    if a.event == "hand_pauseints":
        # the same file with F12+P moved from hand_pause to hand_pauseints (no default bind)
        text = text.replace('hand_pause "key 72 host" "key 19 host" ', 'hand_pause "key 72 host" ')
        text = text.replace("hand_pauseints \n", 'hand_pauseints "key 19 host" \n')
        assert '"key 19 host"' in text.split("hand_pauseints", 1)[1].split("\n", 1)[0]
    if a.event == "minimal":
        text = '[SDL2]\nhand_pause "key 72 host" "key 19 host" \n'
    mapper.write_text(text)
    (work / "probe.conf").write_text(f"[sdl]\nfullscreen=false\noutput=surface\nmapperfile={mapper}\n"
                                     "[mixer]\nnosound=true\n[midi]\nmididevice=none\n"
                                     "[dosbox]\nsaveremark=false\n")
    live = work / "state.sav"
    xvfb = dbx = None
    try:
        for number in range(760, 780):
            xvfb = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                    start_new_session=True)
            time.sleep(2)
            if xvfb.poll() is None:
                break
        env = dict(os.environ, DISPLAY=f":{number}")
        dbx = subprocess.Popen([exe, "-conf", str(work / "probe.conf"), "-fastlaunch", "-nogui",
                                "-nomenu", "-savedir", str(work), "-set", f"dosbox savefile={live}"],
                               env=env, stdout=open(work / "dbx.log", "w"), stderr=subprocess.STDOUT,
                               start_new_session=True)
        wid = recorder.find_window(env, dbx.pid, timeout=60)
        time.sleep(2)
        x(env, "windowfocus", "--sync", wid)
        title = lambda: recorder.xdotool(["getwindowname", wid], env=env).stdout.strip()
        out(step="launched", event=a.event, dosbox=recorder.driver.dosbox_version_of(exe), mapper_sha256=
            recorder.sha256(mapper.read_bytes()), title=title())
        typed(env, "a")
        time.sleep(0.3)
        sig = recorder.file_signature(live)
        recorder.send_save_event(wid, env)
        sig = wait_change(live, sig, 5)
        out(step="save while running (XSendEvent F12+S)", written=sig is not None,
            prompt=screen_row(live) if sig else None)
        chord(env, "p")
        time.sleep(0.5)
        out(step="F12+P typed", title=title(), paused="PAUSED" in title())
        pre = recorder.file_signature(live)
        recorder.send_save_event(wid, env)
        during = wait_change(live, pre, 4)
        out(step="save requested while paused (XSendEvent F12+S)", written_while_paused=
            during is not None, prompt=screen_row(live) if during else None, title=title())
        typed(env, "b")
        time.sleep(0.5)
        out(step="key b typed while paused", title=title())
        chord(env, "p")
        time.sleep(0.5)
        out(step="F12+P typed again", title=title(), paused="PAUSED" in title())
        if "PAUSED" in title():
            typed(env, "Pause")
            time.sleep(0.5)
            out(step="Pause key typed (still paused after the second F12+P)", title=title(),
                paused="PAUSED" in title())
        late = wait_change(live, pre if during is None else during, 3)
        out(step="the save requested while paused landed after the resume",
            landed_after_resume=late is not None)
        typed(env, "c")
        time.sleep(0.3)
        sig = recorder.file_signature(live)
        recorder.send_save_event(wid, env)
        sig = wait_change(live, sig, 5)
        out(step="save after resume", written=sig is not None,
            prompt=screen_row(live) if sig else None,
            note="the prompt shows which typed keys DOS received: a, b (typed while paused), c")
        return 0
    finally:
        recorder.terminate(dbx)
        recorder.terminate(xvfb)


if __name__ == "__main__":
    sys.exit(main())
