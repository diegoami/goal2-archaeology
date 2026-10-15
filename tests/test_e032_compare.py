"""E032's whole-match acceptance check fails closed (PR 243 review, R1 and R2).

Runs experiments/E032-match-engine-inventory/compare.py as a program on synthetic logs. The comparator
under test can be swapped with the environment variable E032_COMPARE (a path), which is how these tests
were shown to fail on the comparator before the fix (it compared only the seeds both logs held, and ignored
error, stopped_at_board and strays)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPARE = Path(os.environ.get("E032_COMPARE", ROOT / "experiments/E032-match-engine-inventory/compare.py"))
SEEDS = (0x1234, 0x2345, 0x4C1D)


def match(seed, **over):
    r = {"seed": seed, "error": None, "stopped_at_board": True, "strays": [], "cpu_s": 9.0,
         "score": [1, seed % 3], "ticks": 4000 + seed % 97, "draws": 180000 + seed, "draws_digest": f"d{seed:x}",
         "statistics_raw": [{"row_label": "Shots", "raw_bytes": [3, 4]}], "templates": {"38": 2}}
    r.update(over)
    return r


class CompareFailsClosed(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ref = self.log("ref.jsonl", [match(s) for s in SEEDS])

    def tearDown(self):
        self.tmp.cleanup()

    def log(self, name, records):
        p = Path(self.tmp.name) / name
        p.write_text("".join(json.dumps(r) + "\n" for r in records))
        return p

    def run_compare(self, cand, seeds=SEEDS, expect=None, ref=None):
        args = [sys.executable, "-B", str(COMPARE), str(ref or self.ref), str(cand),
                "--seeds", ",".join(f"0x{s:04x}" for s in seeds)]
        if expect:
            args += ["--expect", expect]
        return subprocess.run(args, capture_output=True, text=True)

    def test_identical_family_passes(self):
        r = self.run_compare(self.log("c.jsonl", [match(s) for s in SEEDS]))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_empty_candidate_fails(self):
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", [])).returncode, 0)

    def test_truncated_candidate_fails(self):
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", [match(s) for s in SEEDS[:2]])).returncode, 0)

    def test_unexpected_seed_fails(self):
        recs = [match(s) for s in SEEDS] + [match(0x9999)]
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_duplicate_seed_fails(self):
        recs = [match(s) for s in SEEDS] + [match(SEEDS[0])]
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_errored_record_with_equal_fields_fails(self):
        recs = [match(s) for s in SEEDS]
        recs[1] = match(SEEDS[1], error="KeyWaitError: undeclared key wait", stopped_at_board=False)
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_not_stopped_at_board_fails(self):
        recs = [match(s) for s in SEEDS]
        recs[0] = match(SEEDS[0], stopped_at_board=False)
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_strays_fail(self):
        recs = [match(s) for s in SEEDS]
        recs[2] = match(SEEDS[2], strays=["000E:045D"])
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_errored_reference_fails(self):
        ref = self.log("r2.jsonl", [match(SEEDS[0], error="x", stopped_at_board=False)] + [match(s) for s in SEEDS[1:]])
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", [match(s) for s in SEEDS]), ref=ref).returncode, 0)

    def test_differing_field_fails(self):
        recs = [match(s) for s in SEEDS]
        recs[0] = match(SEEDS[0], draws_digest="other")
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_falsifier_caught_by_difference_or_failure(self):
        recs = [match(SEEDS[0], draws_digest="other"), match(SEEDS[1], error="timeout", stopped_at_board=False)]
        r = self.run_compare(self.log("c.jsonl", recs), seeds=SEEDS[:2], expect="differ")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_falsifier_not_caught_fails(self):
        recs = [match(SEEDS[0], draws_digest="other"), match(SEEDS[1])]
        r = self.run_compare(self.log("c.jsonl", recs), seeds=SEEDS[:2], expect="differ")
        self.assertNotEqual(r.returncode, 0, r.stdout)


ANALYZE = Path(os.environ.get("E032_ANALYZE", ROOT / "experiments/E032-match-engine-inventory/analyze.py"))


class AnalyzeRefusesIncompleteRuns(unittest.TestCase):
    """The coverage table is not made from a match that did not complete (the same class as R1/R2)."""

    def run_analyze(self, **over):
        run = {"seed": 0x1234, "score": [1, 1], "ticks": 4146, "draws": 184109, "error": None,
               "stopped_at_board": True, "strays": [],
               "routines": [{"address": "0791:2BE5", "name": "attack_direction", "video_bytes": 0, "exec_match": 10,
                             "instr_match": 340, "instructions_static": 34, "bytes_reached": 66, "size": 66}]}
        run.update(over)
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "cov.json"
            src.write_text(json.dumps(run))
            return subprocess.run([sys.executable, "-B", str(ANALYZE), str(src), str(Path(d) / "parts.md")],
                                  capture_output=True, text=True)

    def test_completed_run_is_tabulated(self):
        self.assertEqual(self.run_analyze().returncode, 0)

    def test_errored_run_is_refused(self):
        self.assertNotEqual(self.run_analyze(error="KeyWaitError", stopped_at_board=False).returncode, 0)

    def test_run_with_strays_is_refused(self):
        self.assertNotEqual(self.run_analyze(strays=["000E:045D"]).returncode, 0)


if __name__ == "__main__":
    unittest.main()
