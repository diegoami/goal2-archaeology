"""E032's acceptance gates fail closed (PR 243 review rounds 1 and 2).

- compare.py, the whole-match check: the seed family is required, every record must be a completed match
  with all its evidence well formed, and missing evidence is never equality nor a caught falsifier.
- analyze.py: a coverage table is never made from an incomplete run or one missing its keys.
- pilot_batch.sh and skip_batch.sh: a generator that fails (here: it refuses an existing output) fails the
  batch, and its stale output is never compared.
- plancheck.py: the plan's cost figures equal costs.py's report, and an untied cost figure fails.

The scripts under test can be swapped with environment variables (E032_COMPARE, E032_ANALYZE,
E032_PILOT_BATCH, E032_SKIP_BATCH: paths), which is how these tests were shown to fail on the scripts before
each fix."""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E032 = ROOT / "experiments/E032-match-engine-inventory"
COMPARE = Path(os.environ.get("E032_COMPARE", E032 / "compare.py"))
ANALYZE = Path(os.environ.get("E032_ANALYZE", E032 / "analyze.py"))
PILOT_BATCH = Path(os.environ.get("E032_PILOT_BATCH", E032 / "pilot_batch.sh"))
SKIP_BATCH = Path(os.environ.get("E032_SKIP_BATCH", E032 / "skip_batch.sh"))
PLANCHECK = E032 / "plancheck.py"
COSTS_JSON = E032 / "out/costs-review2-v3.json"
PLAN = ROOT / "docs/match-engine-plan.md"
SEEDS = (0x1234, 0x2345, 0x4C1D)
EVIDENCE = ("draws_digest", "statistics_raw", "templates")


def digest(seed, salt=""):
    return hashlib.sha256(f"{seed}{salt}".encode()).hexdigest()


REAL = json.loads((E032 / "out/timing-delay20-kickoff-20261015.jsonl").read_text().splitlines()[0])


def match(seed, **over):
    """A synthetic completed record: a real record (record_schema.py's full grammar) with its seed, the
    declared seed write, the score, the counts and the digest changed."""
    r = json.loads(json.dumps(REAL))
    r.update(seed=seed, cpu_s=9.0, score=[1, seed % 3], ticks=4000 + seed % 97, draws=180000 + seed,
             draws_digest=digest(seed))
    for i in r["inputs"]:
        if i["what"] == "main seed word DS:7B62":
            i["new"] = seed.to_bytes(2, "little").hex()
    r.update(over)
    return r


def without(r, keys):
    return {k: v for k, v in r.items() if k not in keys}


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
        recs[0] = match(SEEDS[0], draws_digest=digest(SEEDS[0], "other"))
        self.assertNotEqual(self.run_compare(self.log("c.jsonl", recs)).returncode, 0)

    def test_falsifier_caught_by_difference_or_failure(self):
        recs = [match(SEEDS[0], draws_digest=digest(SEEDS[0], "other")),
                match(SEEDS[1], error="timeout", stopped_at_board=False)]
        r = self.run_compare(self.log("c.jsonl", recs), seeds=SEEDS[:2], expect="differ")
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_falsifier_not_caught_fails(self):
        recs = [match(SEEDS[0], draws_digest=digest(SEEDS[0], "other")), match(SEEDS[1])]
        r = self.run_compare(self.log("c.jsonl", recs), seeds=SEEDS[:2], expect="differ")
        self.assertNotEqual(r.returncode, 0, r.stdout)

    # round 2, R3: missing evidence is neither equality nor a caught falsifier
    def test_evidence_missing_in_both_is_not_identical(self):
        ref = self.log("r3.jsonl", [without(match(s), EVIDENCE) for s in SEEDS])
        cand = self.log("c.jsonl", [without(match(s), EVIDENCE) for s in SEEDS])
        self.assertNotEqual(self.run_compare(cand, ref=ref).returncode, 0)

    def test_evidence_missing_in_both_is_not_a_caught_falsifier(self):
        ref = self.log("r3.jsonl", [without(match(s), EVIDENCE) for s in SEEDS])
        cand = self.log("c.jsonl", [without(match(s), EVIDENCE) for s in SEEDS])
        self.assertNotEqual(self.run_compare(cand, ref=ref, expect="differ").returncode, 0)

    def test_evidence_missing_in_candidate_is_not_identical(self):
        cand = self.log("c.jsonl", [without(match(s), EVIDENCE) for s in SEEDS])
        self.assertNotEqual(self.run_compare(cand).returncode, 0)

    def test_evidence_missing_in_candidate_is_not_a_caught_falsifier(self):
        cand = self.log("c.jsonl", [without(match(s), EVIDENCE) for s in SEEDS])
        self.assertNotEqual(self.run_compare(cand, expect="differ").returncode, 0)

    # round 4: the run the caller means, the same start state, an unhooked reference, strict input
    def run_args(self, cand, *extra, ref=None):
        args = [sys.executable, "-B", str(COMPARE), str(ref or self.ref), str(cand),
                "--seeds", ",".join(f"0x{s:04x}" for s in SEEDS), *extra]
        return subprocess.run(args, capture_output=True, text=True)

    def test_field_names_the_run(self):
        cand = self.log("c.jsonl", [match(s, variant="exact", port_calls=5) for s in SEEDS])
        self.assertEqual(self.run_args(cand, "--field", 'variant="exact"').returncode, 0)
        self.assertEqual(self.run_args(cand, "--field", 'variant="bound-36"').returncode, 2)
        self.assertEqual(self.run_args(cand, "--field", 'skipped=["0791:8F10"]').returncode, 2)
        self.assertEqual(self.run_args(cand, "--field", "nonsense=1").returncode, 2)

    def test_hooked_reference_is_refused(self):
        ref = self.log("rh.jsonl", [match(s, skipped=["0791:8F10"]) for s in SEEDS])
        self.assertEqual(self.run_args(self.log("c.jsonl", [match(s) for s in SEEDS]), ref=ref).returncode, 2)

    def test_another_start_state_is_refused(self):
        cand = self.log("c.jsonl", [match(s, start_record="E011-r0002") for s in SEEDS])
        self.assertEqual(self.run_args(cand).returncode, 2)
        cand = self.log("c2.jsonl", [match(s, watchstart_sha256="0" * 64) for s in SEEDS])
        self.assertEqual(self.run_args(cand).returncode, 2)

    def test_loose_seed_arguments_are_refused(self):
        cand = self.log("c.jsonl", [match(0x1234)])         # one seed: a loose parse of 0x1234 would pass
        ok = subprocess.run([sys.executable, "-B", str(COMPARE), str(self.ref), str(cand), "--seeds", "0x1234"],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stdout)
        for seeds in (" 0x1234", "0x1234 ", "0x1_234", "٤٦٦٠", "", "0x01234", "4_660"):
            with self.subTest(seeds=seeds):
                r = subprocess.run([sys.executable, "-B", str(COMPARE), str(self.ref), str(cand), "--seeds", seeds],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 2, r.stdout)

    def test_undecodable_or_bom_logs_are_refused(self):
        p = Path(self.tmp.name) / "bad.jsonl"
        p.write_bytes(b"\xff\xfe" + json.dumps(match(SEEDS[0])).encode())
        self.assertEqual(self.run_args(p).returncode, 2)
        p.write_bytes("﻿".encode() + "".join(json.dumps(match(s)) + "\n" for s in SEEDS).encode())
        self.assertEqual(self.run_args(p).returncode, 2)

    def test_completion_keys_missing_fail(self):
        cand = self.log("c.jsonl", [without(match(s), ("error", "stopped_at_board", "strays")) for s in SEEDS])
        self.assertNotEqual(self.run_compare(cand).returncode, 0)
        self.assertNotEqual(self.run_compare(cand, expect="differ").returncode, 0)


class AnalyzeRefusesIncompleteRuns(unittest.TestCase):
    """The coverage table is not made from a match that did not complete, or from a run missing its keys."""

    def run_analyze(self, drop=(), **over):
        run = {"seed": 0x1234, "score": [1, 1], "ticks": 4146, "draws": 184109, "error": None,
               "stopped_at_board": True, "strays": [],
               "routines": [{"address": "0791:2BE5", "name": "attack_direction", "video_bytes": 0, "exec_match": 10,
                             "instr_match": 340, "instructions_static": 34, "bytes_reached": 66, "size": 66}]}
        run.update(over)
        run = without(run, drop)
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

    def test_run_missing_completion_keys_is_refused(self):
        self.assertNotEqual(self.run_analyze(drop=("error", "stopped_at_board", "strays")).returncode, 0)

    def test_malformed_row_contents_are_refused(self):
        """Round 3 (issue 246's class): the rows' values, not only their keys."""
        good = {"address": "0791:2BE5", "name": "attack_direction", "video_bytes": 0, "exec_match": 10,
                "instr_match": 340, "instructions_static": 34, "bytes_reached": 66, "size": 66}
        for key, bad in (("instructions_static", None), ("instructions_static", "34"), ("exec_match", -1),
                         ("instr_match", True), ("size", 0), ("address", "2BE5"), ("name", None)):
            row = dict(good, **{key: bad})
            with self.subTest(key=key, value=bad):
                self.assertNotEqual(self.run_analyze(routines=[row]).returncode, 0)
        for blocks in ([], [[1]], [[1, 0]], [["1", 2]], None):
            with self.subTest(match_blocks=blocks):
                self.assertNotEqual(self.run_analyze(match_blocks=blocks).returncode, 0)


class ReadersParseStrictly(unittest.TestCase):
    """Round 4: every E032 reader of JSON refuses NaN/Infinity tokens, overflowing numbers and duplicate keys."""

    def run_on(self, script, text, extra=()):
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "in.json"
            src.write_text(text)
            return subprocess.run([sys.executable, "-B", str(script), str(src), *[str(Path(d) / e) for e in extra]],
                                  capture_output=True, text=True)

    def test_analyze_refuses_loose_json(self):
        good = json.dumps({"seed": 1, "score": [0, 0], "ticks": 1, "draws": 1, "error": None, "stopped_at_board": True,
                           "strays": [], "routines": [{"address": "0791:2BE5", "name": "a", "video_bytes": 0,
                                                        "exec_match": 1, "instr_match": 1, "instructions_static": 1,
                                                        "bytes_reached": 1, "size": 1}]})
        self.assertEqual(self.run_on(ANALYZE, good, ["o.md"]).returncode, 0)
        for bad in (good.replace('"ticks": 1', '"ticks": 1, "ticks": 1'), good.replace('"ticks": 1', '"ticks": NaN'),
                    good.replace('"ticks": 1', '"ticks": 1e999')):
            self.assertNotEqual(self.run_on(ANALYZE, bad, ["o.md"]).returncode, 0)

    def test_plancheck_refuses_loose_json(self):
        good = COSTS_JSON.read_text()
        for bad in (good.replace('"hooked_mean": 18.0', '"hooked_mean": NaN'),
                    good.replace('"hooked_mean": 18.0', '"hooked_mean": 1e999'),
                    good.replace('"hooked_mean": 18.0', '"hooked_mean": 18.0, "hooked_mean": 18.0')):
            self.assertNotEqual(bad, good)
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "c.json"
                p.write_text(bad)
                r = subprocess.run([sys.executable, "-B", str(PLANCHECK), str(p)], capture_output=True, text=True)
                self.assertNotEqual(r.returncode, 0)


class BatchesNeverCompareStaleOutput(unittest.TestCase):
    """Round 2, R1/R2: with a stamp already used, every generator refuses; the batch must fail and not pass
    on the committed (stale) logs. The test runs only when every output of that stamp exists, so no
    generator can start a real emulation."""
    STAMP = "review1"

    def run_batch(self, script, outputs):
        missing = [p for p in outputs if not (E032 / "out" / p).is_file()]
        if missing:
            self.skipTest(f"outputs of stamp {self.STAMP} missing: {missing}")
        env = dict(os.environ)
        env.pop("E032_OUT", None)
        return subprocess.run(["sh", str(script), self.STAMP], cwd=ROOT, capture_output=True, text=True,
                              env=env, timeout=600)

    def test_pilot_batch_with_a_used_stamp_fails(self):
        outs = [f"pilot-{v}-{self.STAMP}.jsonl" for v in ("coin-swapped", "bound-36", "no-picture")] + \
               [f"pilot-exact-8seeds-{self.STAMP}.jsonl"]
        r = self.run_batch(PILOT_BATCH, outs)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("batch exit 0", r.stdout)

    def test_skip_batch_with_a_used_stamp_fails(self):
        outs = [f"skip-0791-{a}-{self.STAMP}.jsonl" for a in
                ("8537", "8E24", "8F10", "9079", "0481", "1829", "0425", "0441", "94E8", "9372")] + \
               [f"skip-display-set-{self.STAMP}.jsonl"]
        r = self.run_batch(SKIP_BATCH, outs)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("batch exit 0", r.stdout)


class PlanFiguresEqualTheReport(unittest.TestCase):
    """Round 2, R4: every cost figure on the plan's page is tied to costs.py's report."""

    def run_check(self, plan):
        return subprocess.run([sys.executable, "-B", str(PLANCHECK), str(COSTS_JSON), str(plan)],
                              capture_output=True, text=True)

    def test_the_plan_matches_the_report(self):
        r = self.run_check(PLAN)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_a_changed_figure_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "plan.md"
            p.write_text(PLAN.read_text().replace("49.5", "45.0"))
            self.assertNotEqual(self.run_check(p).returncode, 0)

    def test_an_untied_cost_figure_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "plan.md"
            p.write_text(PLAN.read_text() + "\nThe review also takes 99 CPU hours.\n")
            self.assertNotEqual(self.run_check(p).returncode, 0)


if __name__ == "__main__":
    unittest.main()
