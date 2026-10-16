#!/usr/bin/env python3
"""E033: the kit's tests at a given commit, run with unicorn blocked (as this repository's CI, which installs no
unicorn, runs them). Before f73a916 the package imported unicorn at import time and the test module errored;
from f73a916 the emulator-free tests run and the others skip.

    python3 -B experiments/E033-original-match-kit/no_unicorn_at_head.py <repo> <commit>"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT, COMMIT = Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else "HEAD"
tmp = Path(tempfile.mkdtemp())
(tmp / "runtime" / "original_match").mkdir(parents=True)
(tmp / "tests").mkdir()
names = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", COMMIT, "runtime/original_match/"],
                       capture_output=True, text=True, check=True).stdout.split()
for name in names + ["tests/test_original_match.py"]:
    data = subprocess.run(["git", "-C", str(ROOT), "show", f"{COMMIT}:{name}"], capture_output=True, check=True).stdout
    (tmp / name).write_bytes(data)
(tmp / "tests" / "__init__.py").write_text("")
sys.modules["unicorn"] = None          # `import unicorn` raises ImportError
sys.path.insert(0, str(tmp))
suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_original_match")
r = unittest.TextTestRunner(verbosity=0).run(suite)
print(f"{COMMIT} without unicorn: tests run {r.testsRun}, errors {len(r.errors)}, failures {len(r.failures)}, "
      f"skipped {len(r.skipped)}")
