#!/usr/bin/env python3
"""Issue #141: reproduce the early-save sitting's flake and time each of its waits.

Runs the exact command of tests.test_human_keys.EarlySaveTests (scripted_keys.py --sleep 2
--keys a;b;c --seed 34, DOSBox-X behind the test's slow_start_dosbox wrapper with its 6 s
freeze, GOAL2_RECORDER_TEST_EARLY_SAVE=1) `--runs` times, one after the other, optionally
pinned to `--cpus` with `--load` busy loops on the same CPUs (a CI runner's few slow cores).
A watcher polls the sessions folder every 50 ms and records, from the launch: the session
folder, meta.json's window_id, the live state.sav, index.jsonl (the opening snapshot
scripted_keys waits for), and the exit. Each run is one JSON line in `--out`, flushed at
once; the session folder is removed afterwards, as the test does.

  python3 experiments/E015-human-playthrough/repro_141.py --runs 10 --cpus 0 --load 2 \
      --out experiments/E015-human-playthrough/fix-141-repro-before-01.log
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
from tests import test_human_keys as t   # noqa: E402  (slow_start_dosbox and the recorder module)

WANT = "a save before the first request is owned by no request line"


def busy():
    while True:
        pass


def classify(rc, out):
    if rc == 1 and WANT in out:
        return "pass"
    for needle in ("opening snapshot never appeared", "window bind failed",
                   "early save never written", "no private outer display",
                   "acceptance guard FAILED", "AssertionError", "Traceback"):
        if needle in out:
            return needle
    return f"rc {rc}"


def traced_wrapper(tmp, delay, trace):
    """The test's slow_start_dosbox wrapper, the same freeze, with each step stamped (wall clock)
    into `trace`: the launch and its DISPLAY, every class window the helper saw with its pid, the
    STOP, the CONT, or the helper giving up."""
    sys.path.insert(0, str(ROOT / "runtime" / "driver"))
    import driver
    real = driver.dosbox_x()
    wrapper = Path(tmp) / "dosbox-x-slow"
    wrapper.write_text("#!/bin/sh\n"
                       f'case "$1" in -version) exec "{real}" "$@";; esac\n'
                       f'T="{trace}"\n'
                       "pid=$$\n"
                       'echo "$(date +%s.%N) launch pid=$pid display=$DISPLAY" >> "$T"\n'
                       "(\n"
                       "  n=0\n"
                       '  while [ $n -lt 300 ]; do\n'
                       '    for w in $(xdotool search --class dosbox 2>/dev/null); do\n'
                       '      p="$(xdotool getwindowpid $w 2>/dev/null)"\n'
                       '      echo "$(date +%s.%N) seen w=$w pid=$p n=$n" >> "$T"\n'
                       '      if [ "$p" = "$pid" ]; then\n'
                       '        kill -STOP $pid; echo "$(date +%s.%N) stop" >> "$T"\n'
                       '        sleep DELAY_S; kill -CONT $pid; echo "$(date +%s.%N) cont" >> "$T"; exit 0\n'
                       "      fi\n"
                       "    done\n"
                       "    n=$((n+1)); sleep 0.02\n"
                       "  done\n"
                       '  echo "$(date +%s.%N) giveup n=$n" >> "$T"\n'
                       ") >/dev/null 2>&1 &\n"
                       f'exec "{real}" "$@"\n'.replace("DELAY_S", str(delay)))
    wrapper.chmod(0o755)
    return dict(os.environ, DOSBOX_X=str(wrapper))


def probe_x(trace, done, wall0, rows):
    """Once the trace names the nested display: time `xdotool search --class dosbox` (and the pid
    of each window) every 0.1 s, as find_window asks it. Rows are (s from launch, call s, [pids])."""
    display = None
    while not done.is_set() and display is None:
        try:
            for line in Path(trace).read_text().splitlines():
                if " launch " in line:
                    display = line.split("display=")[1].strip()
        except OSError:
            pass
        time.sleep(0.05)
    env = dict(os.environ, DISPLAY=display or "")
    while not done.is_set():
        a = time.time()
        try:
            p = subprocess.run(["xdotool", "search", "--class", "dosbox"], env=env,
                               capture_output=True, text=True, timeout=30)
            pids = []
            for w in p.stdout.split():
                q = subprocess.run(["xdotool", "getwindowpid", w], env=env, capture_output=True,
                                   text=True, timeout=30)
                pids.append(q.stdout.strip() or None)
        except subprocess.TimeoutExpired:
            pids = ["timeout"]
        rows.append((round(a - wall0, 2), round(time.time() - a, 2), pids))
        time.sleep(0.1)


def one(cpus, delay, trace=False):
    sessions = t.rec.SESSIONS
    before = set(sessions.glob("*")) if sessions.is_dir() else set()
    marks = {}
    done = threading.Event()
    t0 = time.monotonic()
    wall0 = time.time()

    def watch():
        while not done.is_set():
            fresh = (set(sessions.glob("*")) if sessions.is_dir() else set()) - before
            now = round(time.monotonic() - t0, 2)
            for s in fresh:
                marks.setdefault("session", now)
                try:
                    if json.loads((s / "meta.json").read_text()).get("window_id"):
                        marks.setdefault("window_id", now)
                except (OSError, ValueError):
                    pass
                if (s / "state.sav").exists():
                    marks.setdefault("state_sav", now)
                if (s / "index.jsonl").exists():
                    marks.setdefault("index", now)
            time.sleep(0.05)

    w = threading.Thread(target=watch, daemon=True)
    w.start()
    probe_rows = []
    with tempfile.TemporaryDirectory() as tmp:
        tracef = Path(tmp) / "trace.txt"
        if trace:
            env = dict(traced_wrapper(tmp, delay, tracef), GOAL2_RECORDER_TEST_EARLY_SAVE="1")
            pr = threading.Thread(target=probe_x, args=(tracef, done, wall0, probe_rows),
                                  daemon=True)
            pr.start()
        else:
            env = dict(t.slow_start_dosbox(tmp, delay), GOAL2_RECORDER_TEST_EARLY_SAVE="1")
        argv = [sys.executable, str(ROOT / "experiments/E015-human-playthrough/scripted_keys.py"),
                "--sleep", "2", "--keys", "a;b;c", "--seed", "34"]
        if cpus:
            argv = ["taskset", "-c", cpus] + argv
        try:
            r = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=240)
            rc, out = r.returncode, r.stdout + r.stderr
        except subprocess.TimeoutExpired as e:
            rc, out = "timeout", str(e)
        marks["exit"] = round(time.monotonic() - t0, 2)
        done.set()
        w.join()
        traced = []
        if trace and tracef.exists():
            for line in tracef.read_text().splitlines():
                stamp, rest = line.split(" ", 1)
                traced.append((round(float(stamp) - wall0, 2), rest))
    fresh = (set(sessions.glob("*")) if sessions.is_dir() else set()) - before
    for s in fresh:
        shutil.rmtree(s, ignore_errors=True)
    log = [ln for ln in out.splitlines() if ln.startswith("[")][:12]
    row = {"rc": rc, "result": classify(rc, out), "marks_s": marks, "log": log,
           "tail": out.splitlines()[-1:] if out else []}
    if trace:
        # the helper's seen lines can be hundreds: keep the first, the STOP/CONT/giveup ones
        seen = [x for x in traced if x[1].startswith("seen")]
        row["trace"] = [x for x in traced if not x[1].startswith("seen")] + seen[:3]
        row["trace_seen_lines"] = len(seen)
        slow = [r for r in probe_rows if r[1] >= 0.5]
        row["probe"] = {"calls": len(probe_rows), "slow_calls": slow[:20],
                        "max_call_s": max((r[1] for r in probe_rows), default=None),
                        "first_any": next((r[0] for r in probe_rows if r[2]), None),
                        "first_pid": next((r[0] for r in probe_rows if any(r[2])), None)}
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--cpus", default="", help="taskset CPU list for the sitting and the load")
    ap.add_argument("--load", type=int, default=0, help="busy loops pinned to --cpus")
    ap.add_argument("--delay", type=float, default=6, help="the wrapper's freeze (the test's 6 s)")
    ap.add_argument("--label", default="")
    ap.add_argument("--trace", action="store_true",
                    help="a stamped copy of the wrapper and an X-latency probe (diagnostics)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    hogs = []
    for _ in range(a.load):
        argv = [sys.executable, "-c", "while True: pass"]
        if a.cpus:
            argv = ["taskset", "-c", a.cpus] + argv
        hogs.append(subprocess.Popen(argv))
    counts = {}
    try:
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps({"start": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "label": a.label,
                                "runs": a.runs, "cpus": a.cpus, "load": a.load, "trace": a.trace,
                                "delay": a.delay, "head": subprocess.run(
                                    ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                    capture_output=True, text=True).stdout.strip()}) + "\n")
            f.flush()
            for i in range(a.runs):
                row = dict(one(a.cpus, a.delay, a.trace), run=i + 1)
                counts[row["result"]] = counts.get(row["result"], 0) + 1
                f.write(json.dumps(row) + "\n")
                f.flush()
                print(i + 1, row["result"], row["marks_s"], row.get("trace", ""),
                      row.get("probe", ""), flush=True)
            f.write(json.dumps({"summary": counts, "runs": a.runs}) + "\n")
    finally:
        for h in hogs:
            h.kill()
            h.wait()
    print(counts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
