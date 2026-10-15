#!/usr/bin/env python3
"""Issue #141: does the key logger's reader (`xinput test-xi2 --root` on a fresh Xephyr) exit by
itself on a loaded machine, and with what message? Each trial: a private Xvfb (:770-:779) and an
Xephyr on it (:760-:769), started as recorder.start_nested starts Xephyr (its argv), then the
logger exactly as KeyLogger.start runs it but with stderr kept; after `--hold` seconds, whether it
still runs, its exit code and stderr. Pinned to `--cpus` with `--load` busy loops. Every process
it starts is stopped at the end of each trial.

  python3 experiments/E015-human-playthrough/probe_logger_141.py --trials 10 --cpus 0 --load 4 \
      --out experiments/E015-human-playthrough/fix-141-probe-logger-01.log
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime/human"))
import recorder  # noqa: E402


def pinned(argv, cpus):
    return (["taskset", "-c", cpus] + argv) if cpus else argv


def first_up(argv_for, numbers, env, cpus):
    for n in numbers:
        p = subprocess.Popen(pinned(argv_for(n), cpus), env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        time.sleep(1.5)
        if p.poll() is None:
            return n, p
    raise RuntimeError(f"no display free in {list(numbers)}")


def trial(cpus, hold):
    procs = []
    try:
        n_out, xvfb = first_up(lambda n: ["Xvfb", f":{n}", "-screen", "0", "1280x800x24"],
                               range(770, 780), dict(os.environ), cpus)
        procs.append(xvfb)
        outer = dict(os.environ, DISPLAY=f":{n_out}")
        n_in, xephyr = first_up(lambda n: ["Xephyr", f":{n}", "-screen", "640x400", "-title",
                                           f"probe-141-{n}"], range(760, 770), outer, cpus)
        procs.append(xephyr)
        nested = dict(os.environ, DISPLAY=f":{n_in}")
        t0 = time.monotonic()
        logger = subprocess.Popen(pinned(["stdbuf", "-oL", "xinput", "test-xi2", "--root"], cpus),
                                  env=nested, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                  text=True, start_new_session=True)
        procs.append(logger)
        end = t0 + hold
        while time.monotonic() < end and logger.poll() is None:
            time.sleep(0.1)
        rc = logger.poll()
        err = ""
        if rc is not None:
            err = logger.stderr.read()[-400:]
        return {"outer": n_out, "nested": n_in, "exited": rc is not None, "rc": rc,
                "after_s": round(time.monotonic() - t0, 2) if rc is not None else None,
                "stderr": err}
    finally:
        for p in reversed(procs):
            recorder.terminate(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--trials", type=int, default=10)
    ap.add_argument("--hold", type=float, default=15.0)
    ap.add_argument("--cpus", default="")
    ap.add_argument("--load", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    hogs = [subprocess.Popen(pinned([sys.executable, "-c", "while True: pass"], a.cpus))
            for _ in range(a.load)]
    exits = 0
    try:
        with open(a.out, "a", encoding="utf-8") as f:
            f.write(json.dumps({"start": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "trials": a.trials,
                                "hold": a.hold, "cpus": a.cpus, "load": a.load}) + "\n")
            for i in range(a.trials):
                row = dict(trial(a.cpus, a.hold), trial=i + 1)
                exits += row["exited"]
                f.write(json.dumps(row) + "\n")
                f.flush()
                print(row, flush=True)
            f.write(json.dumps({"summary": {"exited": exits, "trials": a.trials}}) + "\n")
    finally:
        for h in hogs:
            h.kill()
            h.wait()
    return 0


if __name__ == "__main__":
    sys.exit(main())
