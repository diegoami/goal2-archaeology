#!/usr/bin/env python3
"""T34 r4 probe: how many inotify write/close events ONE real DOSBox-X save
produces on state.sav (the recorder's docstring claims 'many close events; 27
were measured'). Decides whether a completed-write count can map requests to
saves one-to-one. Output: scratch/t34/probe_closes_<pid>.log (git-ignored)."""
import json
import os
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
sys.path.insert(0, str(ROOT / "runtime/driver"))
import recorder

OUT = Path(__file__).with_name(f"probe_closes_{os.getpid()}.log")
events = []
lock = threading.Lock()


def watch(path):
    import ctypes
    import ctypes.util
    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
    fd = libc.inotify_init1(0o4000)
    libc.inotify_add_watch(fd, str(Path(path).parent).encode(), 0x2 | 0x8 | 0x80)
    while True:
        try:
            buf = os.read(fd, 65536)
        except BlockingIOError:
            time.sleep(0.01)
            continue
        i = 0
        with lock:
            while i < len(buf):
                _wd, mask, _c, size = struct.unpack_from("iIII", buf, i)
                name = buf[i + 16:i + 16 + size].rstrip(b"\0").decode(errors="replace")
                i += 16 + size
                if name == Path(path).name:
                    kinds = [k for b, k in ((0x2, "MODIFY"), (0x8, "CLOSE_WRITE"),
                                            (0x80, "MOVED_TO")) if mask & b]
                    events.append((time.monotonic(), "+".join(kinds)))


def main():
    for number in range(780, 800):
        outer = subprocess.Popen(["Xvfb", f":{number}"], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(1)
        if outer.poll() is None:
            break
    env = dict(os.environ, DISPLAY=f":{number}")
    session, meta = recorder.new_session()
    live = session / "state.sav"
    threading.Thread(target=watch, args=(live,), daemon=True).start()
    argv = [os.environ.get("DOSBOX_X", "dosbox-x"), "-conf", str(session / "dosbox.conf"),
            "-fastlaunch", "-nogui", "-nomenu", "-savedir", str(session),
            "-set", f"dosbox savefile={live}"]
    dbx = subprocess.Popen(argv, env=env, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, start_new_session=True)
    wid = recorder.find_window(env, dbx.pid)
    time.sleep(8)                     # the game reaches its first screen
    for k in range(3):                # three saves, 2 s apart
        with lock:
            mark = len(events)
        recorder.send_save_event(wid, env)
        time.sleep(2.0)
        with lock:
            batch = events[mark:]
        print(f"save {k}: {len(batch)} events on state.sav: "
              f"{[k for _, k in batch]}", flush=True)
    recorder.terminate(dbx)
    recorder.terminate(outer)
    with open(OUT, "w") as f:
        f.write("\n".join(json.dumps(e) for e in events))
    print(f"total events: {len(events)}; log: {OUT}")


if __name__ == "__main__":
    main()
