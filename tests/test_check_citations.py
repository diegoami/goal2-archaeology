"""A finding whose citations exist passes; a missing run or an uncited bullet fails (DW4)."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"


def run_check(finding: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/check_citations.py",
         str(FIXTURES / "citations" / finding), "--runs", str(FIXTURES / "runs")],
        cwd=REPO_ROOT, capture_output=True, text=True)


class CheckCitationsTest(unittest.TestCase):
    def test_missing_run_id_exits_1(self):
        result = run_check("finding-missing.md")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("E900-r9999", result.stdout)

    def test_all_citations_exist_exits_0(self):
        result = run_check("finding-good.md")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_citation_on_a_bullet_second_line_exits_0(self):
        # toy-archaeology#12: the only citation sits on a bullet's continuation line.
        result = run_check("finding-wrapped.md")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_wrapped_bullet_without_any_citation_exits_1(self):
        result = run_check("finding-wrapped-empty.md")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("cites no run id", result.stdout)


if __name__ == "__main__":
    unittest.main()
