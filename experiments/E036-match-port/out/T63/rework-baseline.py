"""Verify the rework tests fail on the reviewed 92f861d implementation."""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
REVIEWED = "92f861d6242799cc6f51bc0ef72d3176785603eb"
PORT = "runtime/original_match/port/positioning.py"


def main():
    old = subprocess.run(["git", "show", f"{REVIEWED}:{PORT}"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout
    with tempfile.TemporaryDirectory(prefix="t63-rework-before-") as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / "runtime", root / "runtime")
        shutil.copytree(ROOT / "tests", root / "tests")
        (root / PORT).write_text(old)
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", "-v", "tests.test_port_positioning"],
                                cwd=root, capture_output=True, text=True)
    failures = re.findall(r"^FAIL: (\w+)", result.stderr, re.MULTILINE)
    print(f"reviewed source {REVIEWED}; current rework tests; exit {result.returncode}")
    print("failures:", ", ".join(failures))
    for line in result.stderr.splitlines():
        if line.startswith("Ran ") or line.startswith("FAILED"):
            print(line)
    assert result.returncode != 0
    assert "test_marking_slot_skill_comparison_keeps_incumbent_on_guest_stack" in failures
    assert "test_marking_assignment_continues_after_marker_calls" in failures
    assert "test_empty_marking_slot_is_cleared_without_candidate" in failures
    assert "ERROR:" not in result.stderr


if __name__ == "__main__":
    main()
