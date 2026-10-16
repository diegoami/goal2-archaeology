#!/usr/bin/env python3
"""E033: export runtime/original_match at a commit into a directory, and run named tests of the CURRENT test module
against it (to show a new test failing before its fix).

    python3 -B experiments/E033-original-match-kit/old_kit.py <commit> <dir> [test names...]

The package is written to <dir>/original_match (from `git show <commit>:runtime/original_match/<file>`), so
stamps.py and save_boundaries.py can take --kit <dir>. With test names, the current tests/test_original_match.py is
loaded with that package first on the path and the named tests run; each one's outcome is printed."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def export(commit, target):
    pkg = Path(target) / "original_match"
    pkg.mkdir(parents=True, exist_ok=False)
    names = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", commit, "runtime/original_match/"],
                           capture_output=True, text=True, check=True).stdout.split()
    for name in names:
        data = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{name}"], capture_output=True, check=True).stdout
        (pkg / Path(name).name).write_bytes(data)
    return pkg


def main():
    commit, target, tests = sys.argv[1], sys.argv[2], sys.argv[3:]
    export(commit, target)
    print(f"exported runtime/original_match at {commit} to {target}/original_match")
    if not tests:
        return
    sys.path.insert(0, target)
    sys.path.insert(1, str(ROOT))
    import original_match
    assert original_match.__file__.startswith(str(Path(target).resolve())) or original_match.__file__.startswith(target)
    for name in tests:
        suite = unittest.defaultTestLoader.loadTestsFromName(f"tests.test_original_match.{name}")
        r = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
        verdict = "passes" if r.wasSuccessful() else ("FAILS" if r.failures else "ERRORS")
        detail = (r.failures or r.errors)[0][1].strip().splitlines()[-1] if not r.wasSuccessful() else ""
        print(f"{commit} {name}: {verdict}  {detail[:160]}")


if __name__ == "__main__":
    main()
