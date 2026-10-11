#!/usr/bin/env python3
"""Mutation check for T39a's tests: each mutation breaks one behaviour in a file, the named test
module must fail, and the file is written back from its saved contents in a `finally` (CLAUDE.md
rule 9a). Prints one line per mutation: `killed` when the tests failed, `SURVIVED` when they passed.

    python3 tools/screens/mutation_check.py
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MUTATIONS = [
    # (file, old, new, test module, what it breaks)
    ("static/screens/kinds.tsv", "manager-menu\t+find option ;; +F1help", "manager-menu\t+Hit",
     "tests.test_screens", "a rule keyed on a common word merges screens"),
    ("static/screens/kinds.tsv", "+Do you want to watch this match", "+watch this match",
     "tests.test_screens", "a rule that stops matching leaves states unknown"),
    ("static/screens/catalogue.tsv", "\tEsc-exit\t", "\tEsc-leave\t",
     "tests.test_screens", "a quote that is not on the screen"),
    ("static/screens/catalogue.tsv", "burst: manager-menu -> fixtures-watch", "burst: manager-menu -> fixtures-auto",
     "tests.test_screens", "a run row whose after kind is not the state's kind"),
    ("static/screens/catalogue.tsv", "\tscreen\t", "\t\t",
     "tests.test_screens", "a row without a source"),
    ("tools/screens/render.py", "return PALETTE[attr & 0x0F], PALETTE[attr >> 4]", "return PALETTE[attr & 0x0F], PALETTE[(attr >> 4) & 7]",
     "tests.test_screens_render", "blink: bit 7 of the attribute dropped from the background"),
    ("tools/screens/render.py", "FONT_BASE = savestate.VGA_TEXT_BASE + 2", "FONT_BASE = savestate.VGA_TEXT_BASE + 3",
     "tests.test_screens_render", "the font read one byte off"),
    ("tools/screens/render.py", "CELL_W, CELL_H = 8, 16", "CELL_W, CELL_H = 9, 16",
     "tests.test_screens_render", "a 9-dot cell"),
    ("tools/screens/build.py", 'REAL_SITTINGS = ("E015-r0003", "E015-r0007", "E015-r0008")',
     'REAL_SITTINGS = ("E015-r0003", "E015-r0004", "E015-r0007", "E015-r0008")',
     "tests.test_screens", "a scripted acceptance sitting counted as play"),
]


def main():
    bad = 0
    for rel, old, new, module, what in MUTATIONS:
        path = ROOT / rel
        saved = path.read_text(encoding="utf-8")
        try:
            if old not in saved:
                print(f"NOT APPLIED  {rel}: {what}")
                bad += 1
                continue
            path.write_text(saved.replace(old, new, 1), encoding="utf-8", newline="\n")
            # -B: a mutation and its restore can leave a file the same size within the same second,
            # and a .pyc written from the mutant would then be read as the restored file's.
            r = subprocess.run([sys.executable, "-B", "-m", "unittest", module], cwd=ROOT,
                               capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
            killed = r.returncode != 0
            print(f"{'killed' if killed else 'SURVIVED':12s} {rel}: {what}")
            bad += 0 if killed else 1
        finally:
            path.write_text(saved, encoding="utf-8", newline="\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
