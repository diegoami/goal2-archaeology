#!/usr/bin/env python3
"""Issue #141: the deterministic early-save tests (tests.test_human_keys.EarlySaveRuleTests)
against three mutations that remove the early-save rule, one at a time. Each mutation is a text
replacement that must match exactly once; the file's saved contents are written back in a
`finally` (rule 9a). Only EarlySaveRuleTests runs, whose play() has every launch faked: no
mutated recorder ever starts a display or an emulator. The unmutated tree runs first and last.

  python3 experiments/E015-human-playthrough/mutate_141.py \
      --out experiments/E015-human-playthrough/fix-141-mutations-01.log
"""
import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC = ROOT / "runtime/human/recorder.py"
SK = ROOT / "experiments/E015-human-playthrough/scripted_keys.py"

MUTATIONS = [
    ("m1: the Watcher builds its own write watch (the watch started before the launch is not "
     "handed over)", REC,
     "xrun=lambda argv: send_save_event(wid, env), watch=watch,",
     "xrun=lambda argv: send_save_event(wid, env),"),
    ("m2: the write watch starts after the emulator is launched (the pre-PR-112 order)", REC,
     '        watch = WriteWatch(session / "state.sav")\n',
     ""),
    ("m2 (second half: the watch now starts after the launch)", REC,
     '        log(f"dosbox-x started (pid {dbx.pid})")\n',
     '        log(f"dosbox-x started (pid {dbx.pid})")\n'
     '        watch = WriteWatch(session / "state.sav")\n'),
    ("m3: the guard's save-before-the-first-request check is removed", SK,
     "        if seen is None and pre >= recorder.ONE_SAVE_MIN_EVENTS:\n",
     "        if False:\n"),
]
# m2 is two replacements applied together
GROUPS = [[0], [1, 2], [3]]


def run_tests():
    # a fresh bytecode cache per run: m2 moves a line, so the mutated file has the original's
    # size, and a restore within the same second left the mutated .pyc valid for the next run
    # (seen in this script's first run, 2026-10-15)
    with tempfile.TemporaryDirectory() as cache:
        p = subprocess.run([sys.executable, "-m", "unittest", "-v",
                            "tests.test_human_keys.EarlySaveRuleTests"],
                           cwd=ROOT, capture_output=True, text=True, timeout=120,
                           env=dict(os.environ, PYTHONPYCACHEPREFIX=cache))
    return p.returncode, p.stderr.strip().splitlines()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    lines = [f"# fix #141 mutations, {time.strftime('%Y-%m-%dT%H:%M:%S%z')}, HEAD {head}"]
    rc, out = run_tests()
    lines += [f"## unmutated: exit {rc}"] + out[-4:]
    bad = rc != 0
    for group in GROUPS:
        saved = {}
        try:
            for i in group:
                name, path, old, new = MUTATIONS[i]
                if path not in saved:
                    saved[path] = path.read_text()   # the original, written back in `finally`
                text = path.read_text()              # the original, or the group's first edit
                if text.count(old) != 1:
                    raise SystemExit(f"{name}: anchor found {text.count(old)} times")
                path.write_text(text.replace(old, new))
            rc, out = run_tests()
            title = MUTATIONS[group[0]][0]
            lines += [f"## {title}: exit {rc} ({'killed' if rc else 'SURVIVED'})"]
            lines += [ln for ln in out if ln.startswith(("FAIL", "ERROR", "AssertionError"))
                      or " ... " in ln or ln.startswith("Ran ")]
            bad |= rc == 0
        finally:
            for path, text in saved.items():
                path.write_text(text)
    rc, out = run_tests()
    lines += [f"## unmutated again: exit {rc}"] + out[-4:]
    bad |= rc != 0
    Path(a.out).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
