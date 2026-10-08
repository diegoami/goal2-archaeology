#!/usr/bin/env python3
"""T34 acceptance sitting on private displays; never uses the owner's display."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder


def main():
    outer = app = sitting = None
    before = set(recorder.SESSIONS.glob("*"))
    try:
        for number in range(740, 760):
            outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "1280x800x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            time.sleep(1)
            if outer.poll() is None:
                break
        if outer.poll() is not None:
            raise RuntimeError("no private outer display")
        env = dict(os.environ, DISPLAY=f":{number}")
        app = subprocess.Popen(["xev", "-name", "T34-other-app"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        sitting = subprocess.Popen(["bash", "runtime/human/play.sh", "--quit-after", "12"], env=env, start_new_session=True)
        deadline = time.monotonic() + 15
        session = None
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
            time.sleep(0.1)
        else:
            raise RuntimeError("opening snapshot never appeared")
        child = dict(env, DISPLAY=meta["display"])
        subprocess.run(["xdotool", "windowfocus", meta["window_id"]], env=child, check=True)
        for key in ("a", "b"):
            subprocess.run(["xdotool", "key", key], env=child, check=True)
            time.sleep(2)
        other = subprocess.check_output(["xdotool", "search", "--name", "T34-other-app"], env=env, text=True).split()[0]
        subprocess.run(["xdotool", "key", "--window", other, "x", "y", "z"], env=env, check=True)
        assert sitting.wait(timeout=25) == 0
        events = [json.loads(line) for line in (session / "keys.jsonl").read_text().splitlines()]
        assert [(e["event"], e["keysym"]) for e in events] == [("press", "a"), ("release", "a"), ("press", "b"), ("release", "b")], events
        index = [json.loads(line) for line in (session / "index.jsonl").read_text().splitlines()]
        bursts = [entry for entry in index if entry["origin"] == "burst"]
        assert len(bursts) == 2, index
        for event, snap in zip(events[1::2], bursts):
            delta = meta["monotonic_start_s"] + snap["elapsed_s"] - event["monotonic_s"]
            assert delta >= 0.5, delta
        print(f"privacy OK: a/b game keys only; outer-app x/y/z excluded; burst snapshots: {len(bursts)}", flush=True)
        print(f"session: {session.relative_to(ROOT)}", flush=True)
        subprocess.run(["python3", "experiments/E015-human-playthrough/keymap.py", str(session.relative_to(ROOT)), "--scripted-keys"], check=True)
    finally:
        for proc in (sitting, app, outer):
            recorder.terminate(proc)


if __name__ == "__main__":
    main()
