#!/usr/bin/env python3
"""Issue #141: what the test suite leaves running before the early-save sitting starts.

Runs the suite's tests that come before tests.test_human_keys.EarlySaveTests in `unittest
discover` order (every module named before test_human_keys, then test_human_keys' classes before
EarlySaveTests), then lists the processes started since that are still alive, with their CPU
share: a leftover emulator, X server or busy thread is load the sitting's own waits must absorb.

  python3 experiments/E015-human-playthrough/leftovers_141.py \
      --out experiments/E015-human-playthrough/fix-141-leftovers-01.log
"""
import argparse
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def prefix_ids():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))
    ids = []

    def walk(s):
        for t in s:
            if isinstance(t, unittest.TestSuite):
                yield from walk(t)
            else:
                yield t.id()
    for i in walk(suite):
        if i.startswith("test_human_keys.EarlySaveTests"):
            break
        ids.append(i)
    return ids


def snapshot(since_boot_s):
    p = subprocess.run(["ps", "-eo", "pid,ppid,pcpu,etimes,stat,cmd", "--sort=-pcpu"],
                       capture_output=True, text=True)
    rows = []
    for line in p.stdout.splitlines()[1:]:
        parts = line.split(None, 5)
        if len(parts) < 6 or int(parts[3]) > since_boot_s or int(parts[0]) == os.getpid():
            continue
        if parts[5].startswith("ps "):
            continue
        rows.append(line[:200])
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="", help="a substring the test ids must hold (a narrower prefix)")
    a = ap.parse_args()
    ids = [i for i in prefix_ids() if a.only in i]
    t0 = time.monotonic()
    p = subprocess.run([sys.executable, "-m", "unittest", *ids], cwd=ROOT / "tests",
                       capture_output=True, text=True)
    elapsed = int(time.monotonic() - t0) + 1
    rows = snapshot(elapsed)
    time.sleep(10)
    later = snapshot(elapsed + 11)
    out = [f"# fix #141 leftovers {time.strftime('%Y-%m-%dT%H:%M:%S%z')}: {len(ids)} tests "
           f"before EarlySaveTests (filter {a.only!r}), {elapsed} s, exit {p.returncode}",
           p.stderr.strip().splitlines()[-1] if p.stderr.strip() else "",
           "## processes started during the prefix and alive right after it"] + rows + [
           "## the same, 10 s later"] + later
    Path(a.out).write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    sys.exit(main())
