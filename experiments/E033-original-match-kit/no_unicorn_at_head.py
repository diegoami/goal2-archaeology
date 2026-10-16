"""The committed (HEAD) package and tests, run with unicorn blocked: before the lazy import, the module errors."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(sys.argv[1])
tmp = Path(tempfile.mkdtemp())
(tmp / "runtime" / "original_match").mkdir(parents=True)
(tmp / "tests").mkdir()
names = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", "HEAD", "runtime/original_match/"],
                       capture_output=True, text=True, check=True).stdout.split()
for name in names + ["tests/test_original_match.py"]:
    data = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{name}"], capture_output=True, check=True).stdout
    (tmp / name).write_bytes(data)
(tmp / "tests" / "__init__.py").write_text("")
sys.modules["unicorn"] = None
sys.path.insert(0, str(tmp))
suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_original_match")
r = unittest.TextTestRunner(verbosity=0).run(suite)
print("HEAD code without unicorn: tests run", r.testsRun, "errors", len(r.errors), "skipped", len(r.skipped))
