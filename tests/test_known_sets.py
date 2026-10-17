"""The registered successor set (T11, U21): `goal2-67cf27d6` declares the runtime writes F001
observed (`*.GL`, `*.SUM`), keeps its predecessor's ten files, and the two entries of
artifacts/known.json name each other in their notes; the driver verifies and names the successor."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import driver  # noqa: E402

sys.path.insert(0, str(ROOT))
from tests import netskip  # noqa: E402
from tools import fetch_artifact  # noqa: E402

PREDECESSOR = "goal2-a949da2f"
SUCCESSOR = "goal2-67cf27d6"
SETS = {entry["manifest"]["id"]: entry
        for entry in json.loads((ROOT / "artifacts" / "known.json").read_text(encoding="utf-8"))["sets"]}
RELEASED = ROOT / ".cache" / "artifacts" / SUCCESSOR


class KnownSetsTest(unittest.TestCase):
    @netskip.needs_pinned_tools
    def test_the_pinned_tool_validates_both_sets(self):
        result = subprocess.run([sys.executable, "tools/register_artifact.py", "validate"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(f"known.json ok ({len(SETS)} sets)", result.stdout)

    def test_the_successor_declares_exactly_the_writes_f001_observed(self):
        self.assertEqual(["*.GL", "*.SUM"], SETS[SUCCESSOR]["manifest"]["runtime_writes"])

    def test_the_successors_files_equal_the_predecessors(self):
        self.assertEqual(SETS[PREDECESSOR]["manifest"]["files"],
                         SETS[SUCCESSOR]["manifest"]["files"])

    def test_the_sets_name_each_other_and_the_evidence_in_their_notes(self):
        # U21: the successor's notes name the predecessor and the run and finding that showed the
        # writes; the predecessor's notes name the successor.
        self.assertIn(SUCCESSOR, SETS[PREDECESSOR]["notes"])
        self.assertIn(PREDECESSOR, SETS[SUCCESSOR]["notes"])
        self.assertIn("E001", SETS[SUCCESSOR]["notes"])
        self.assertIn("F001", SETS[SUCCESSOR]["notes"])


@unittest.skipUnless(RELEASED.is_dir(),
                     f"the successor's release copy is not in {RELEASED.relative_to(ROOT)}")
class DriverSetTest(unittest.TestCase):
    # A folder left by a fetch that failed offline is not a release copy (#236).
    @netskip.needs(f"release set {SUCCESSOR}", lambda: fetch_artifact.fetch(SUCCESSOR))
    def test_verify_release_verifies_and_names_the_successor(self):
        self.assertEqual(SUCCESSOR, driver.verify_release(RELEASED))

    def test_the_driver_constants_set_id_is_the_successor(self):
        self.assertEqual(SUCCESSOR, driver.SET_ID)


if __name__ == "__main__":
    unittest.main()
