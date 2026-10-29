"""E036 (T57): the comparison of a candidate with the reference fails closed, and the record grammar is read to its
leaves (E032's review classes, PR 243: a container checked but not its contents, a grammar looser than its intent, an
input skipped when missing).

Each rule has a test that fails without the rule. The scripts under test can be swapped: E036_DIR names a directory
that holds compare.py, records.py, families.py and families/ (a copy of experiments/E036-match-port with one rule
taken out, next to a runtime/ it can import), which is how these tests were shown to fail (out/T57/mutation-tests-*.txt).
The records are synthetic (digests of the match's id); the real ones are family.py's."""
import copy
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E036 = Path(os.environ.get("E036_DIR", ROOT / "experiments/E036-match-port"))


def isolated_import(directory, names):
    """The modules `names` of `directory` (in dependency order), loaded under the names e036_<name>. The whole suite runs
    in one process and other tests have a `compare` or a `records` of their own, so none of them is touched: while a
    module executes, its siblings' `import records` finds ours, and afterwards the others' modules are back. sys.path
    is as it was, with the directory and the kit's runtime/ at its end."""
    path, saved = list(sys.path), {n: sys.modules.pop(n) for n in names if n in sys.modules}
    sys.path.insert(0, str(directory))
    loaded = []
    try:
        for n in names:
            spec = importlib.util.spec_from_file_location("e036_" + n, Path(directory) / f"{n}.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules["e036_" + n] = sys.modules[n] = module
            spec.loader.exec_module(module)
            loaded.append(module)
    finally:
        for n in names:
            sys.modules.pop(n, None)
            if n in saved:
                sys.modules[n] = saved[n]
        sys.path[:] = path + [str(directory), str(ROOT / "runtime")]
    return loaded


records, families, compare_module, family = isolated_import(E036, ("records", "families", "compare", "family"))
from original_match.check import EXPECTED_FAMILY  # noqa: E402

COMPARE = E036 / "compare.py"
FAMILIES = {f.name: f for f in families.select("ALL", families.discover())}   # the admitted families: ALL leaves T79's sheet out
EXPECTED = {mid: d for fam in FAMILIES.values() for mid, d in fam.expected().items()}
F40 = sorted(FAMILIES["F40"].expected())
IMAGE = families.image_sha256()
IMAGES = {m.id:m.image_sha256 for f in FAMILIES.values() for m in f.matches}


def dg(*parts):
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()


def blocks(n, *salt):
    return [dg("block", k, *salt) for k in range(n)]


def record(mid, **over):
    """A synthetic completed record of match `mid`, valid under records.py's grammar."""
    n = int(dg(mid)[:6], 16)
    per_minute = [[m, 90 + (n + m) % 50, dg(mid, "minute", m)] for m in range(1, 92)]
    r = {
        "id": mid, "family": mid.split("/")[0], "spec_sha256": EXPECTED[mid], "image_sha256": IMAGES[mid], "kit": "2",
        "mask": [], "error": None, "stopped_at_board": True, "strays": [], "cpu_s": 9.5, "wall_s": 10.25,
        "score": [1, n % 3], "ticks": 4000 + n % 97,
        "draws": {"count": sum(row[1] for row in per_minute), "digest": dg(mid, "draws"), "per_minute": per_minute},
        "board": {"statistics": {k: [(n + i) % 20, (n + 2 * i) % 20] for i, k in enumerate(records.STAT_NAMES)},
                  "bars": [[1000 + n % 50, 2000 + n % 70], [3000 + n % 30, 4000 + n % 40]],
                  "man_of_the_match": 100 + n % 900, "final_score": [1, n % 3], "seed": n % 65536,
                  "screen_sha256": dg(mid, "screen")},
        "templates": {"0": 3, "38": 2, str(n % 60 + 1): 1},
        "result_sha256": dg(mid, "result"), "events": {"count": 900 + n % 50, "sha256": dg(mid, "events")},
        "decisions": [[46, "half_time"]],
        "after": {"seed": n % 65536, "ds": blocks(records.DS_BLOCKS, mid),
                  "ranges": {name: blocks(-(-length // records.BLOCK), mid, name)
                             for name, (_, length) in records.ranges_for_source(IMAGES[mid]).items()}},
        "counts": {},
    }
    r.update(over)
    return r


def incomplete(mid, **over):
    base = record(mid, error="TimeLimit: the match is over its time limit", stopped_at_board=False, score=None,
                  ticks=None, draws=None, board=None, templates=None, result_sha256=None, events=None,
                  decisions=None, after=None)
    base.update(over)
    return base


def without(r, *keys):
    return {k: v for k, v in r.items() if k not in keys}


def edited(r, path, value):
    """A deep copy of r with the leaf at `path` (keys and indexes) replaced."""
    r = copy.deepcopy(r)
    node = r
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return r


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.ref = self.log("ref.jsonl", [record(m) for m in F40])

    def tearDown(self):
        self.tmp.cleanup()

    def log(self, name, recs):
        p = Path(self.tmp.name) / name
        p.write_text("".join((r if isinstance(r, str) else json.dumps(r)) + "\n" for r in recs))
        return p

    def compare(self, cand, *extra, ref=None, family="F40"):
        return subprocess.run([sys.executable, "-B", str(COMPARE), "--family", family, "--candidate", str(cand),
                               "--reference", str(ref or self.ref), *extra], capture_output=True, text=True)

    def matches(self, **replace):
        """The family's records, with those of `replace` ({id: record or None}) put in or left out."""
        out = []
        for m in F40:
            r = replace.get(m, record(m))
            if r is not None:
                out.append(r)
        return out


class CompareFailsClosed(Base):
    def test_identical_family_passes(self):
        r = self.compare(self.log("c.jsonl", self.matches()))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("40 matches expected identical, 40 pass, 0 fail", r.stdout)

    def test_the_reference_may_hold_more_matches(self):
        ref = self.log("r2.jsonl", [record(m) for m in sorted(EXPECTED)])
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches()), ref=ref).returncode, 0)

    # a missing, duplicate or unexpected match
    def test_empty_candidate_is_malformed(self):
        self.assertEqual(self.compare(self.log("c.jsonl", [])).returncode, 2)

    def test_a_missing_match_is_malformed(self):
        r = self.compare(self.log("c.jsonl", self.matches(**{F40[7]: None})))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("missing from the candidate", r.stdout)

    def test_an_unexpected_match_is_malformed(self):
        r = self.compare(self.log("c.jsonl", self.matches() + [record("O8/c1-c2-friendly")]))
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("unexpected in the candidate", r.stdout)

    def test_a_duplicate_match_is_malformed(self):
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches() + [record(F40[0])])).returncode, 2)

    def test_a_missing_reference_match_is_malformed(self):
        ref = self.log("r2.jsonl", [record(m) for m in F40[1:]])
        r = self.compare(self.log("c.jsonl", self.matches()), ref=ref)
        self.assertEqual(r.returncode, 2, r.stdout)
        self.assertIn("missing from the reference", r.stdout)

    def test_a_duplicate_reference_match_is_malformed(self):
        ref = self.log("r2.jsonl", [record(m) for m in F40] + [record(F40[3])])
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches()), ref=ref).returncode, 2)

    # an incomplete match
    def test_an_errored_candidate_with_equal_fields_fails(self):
        for what, bad in (("an error", incomplete(F40[2], error="KeyError: x")),
                          ("no board", record(F40[2], stopped_at_board=False)),
                          ("a stray decision", record(F40[2], strays=["pause"]))):
            with self.subTest(what):
                r = self.compare(self.log("c.jsonl", self.matches(**{F40[2]: bad})))
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("NOT COMPLETED", r.stdout)

    def test_an_incomplete_candidate_without_evidence_fails(self):
        r = self.compare(self.log("c.jsonl", self.matches(**{F40[2]: incomplete(F40[2])})))
        self.assertEqual(r.returncode, 1, r.stdout)

    def test_an_incomplete_reference_is_malformed(self):
        for bad in (incomplete(F40[0], error="KeyError: x"), record(F40[0], stopped_at_board=False),
                    record(F40[0], strays=["pause"])):
            with self.subTest(bad["error"] or bad["strays"] or "no board"):
                ref = self.log("r2.jsonl", [bad if m == F40[0] else record(m) for m in F40])
                r = self.compare(self.log("c.jsonl", self.matches()), ref=ref)
                self.assertEqual(r.returncode, 2, r.stdout)
                self.assertIn("reference", r.stdout)

    # a field that differs
    def test_each_compared_field_fails_when_it_differs(self):
        paths = {"score": ("score", 0), "ticks": ("ticks",), "draws.count": None, "draws.digest": ("draws", "digest"),
                 "draws.per_minute": ("draws", "per_minute", 5, 2), "events": ("events", "sha256"),
                 "board.statistics": ("board", "statistics", "shots", 0), "board.bars": ("board", "bars", 1, 0),
                 "board.man_of_the_match": ("board", "man_of_the_match"), "board.final_score": ("board", "final_score", 0),
                 "board.seed": ("board", "seed"), "templates": ("templates", "0"), "result_sha256": ("result_sha256",),
                 "decisions": ("decisions", 0, 0), "after.seed": ("after", "seed"), "after.ds": ("after", "ds", 3),
                 "board.screen_sha256": ("board", "screen_sha256")}
        self.assertEqual(set(paths) | {"after.ranges"}, set(compare_module.FIELDS))   # a new compared field needs a case
        for field, path in paths.items():
            base = record(F40[4])
            if path is None:
                bad = copy.deepcopy(base)
                bad["draws"]["count"] += 1
                bad["draws"]["per_minute"][0][1] += 1
            else:
                old = base
                for key in path:
                    old = old[key]
                new = dg("other") if isinstance(old, str) and len(old) == 64 else old + 1
                bad = edited(base, path, new)
            with self.subTest(field):
                r = self.compare(self.log("c.jsonl", self.matches(**{F40[4]: bad})))
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn(f"first at {field}", r.stdout)

    def test_every_range_and_the_first_differing_block_is_named(self):
        for name in records.RANGES:
            bad = record(F40[1])
            bad["after"]["ranges"][name][-1] = dg("other")
            r = self.compare(self.log("c.jsonl", self.matches(**{F40[1]: bad})))
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn(f"first at after.ranges.{name} ({name}+0x{(len(bad['after']['ranges'][name]) - 1) * 1024:04X})", r.stdout)
        bad = edited(record(F40[1]), ("after", "ds", 12), dg("other"))
        r = self.compare(self.log("c.jsonl", self.matches(**{F40[1]: bad})))
        self.assertIn("first at after.ds (DS+0x3000)", r.stdout)

    def test_the_first_differing_minute_is_named(self):
        bad = record(F40[0])
        bad["draws"]["per_minute"][36][2] = dg("other")
        bad["draws"]["digest"] = dg("other digest")
        r = self.compare(self.log("c.jsonl", self.matches(**{F40[0]: bad})))
        self.assertEqual(r.returncode, 1, r.stdout)
        # the first difference in field order is the digest; the minute where the draws first differ comes with it
        self.assertIn("first at draws.digest; the draws first differ at minute 37 (reference ", r.stdout)
        bad = record(F40[0])
        bad["draws"]["per_minute"][36][2] = dg("other")
        r = self.compare(self.log("c.jsonl", self.matches(**{F40[0]: bad})))
        self.assertIn("first at draws.per_minute (minute 37 (reference ", r.stdout)

    # --expect differ
    def test_falsifier_caught_by_difference_or_failure(self):
        cand = self.log("c.jsonl", [record(m, ticks=1) if i % 2 else incomplete(m) for i, m in enumerate(F40)])
        r = self.compare(cand, "--expect", "differ")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("caught", r.stdout)

    def test_falsifier_not_caught_on_an_identical_candidate(self):
        r = self.compare(self.log("c.jsonl", self.matches()), "--expect", "differ")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("NOT CAUGHT", r.stdout)

    def test_one_uncaught_match_fails_the_falsifier(self):
        cand = self.log("c.jsonl", [record(m) if m == F40[9] else record(m, ticks=1) for m in F40])
        r = self.compare(cand, "--expect", "differ")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn(f"{F40[9]}:", r.stdout.split("NOT CAUGHT")[0].splitlines()[-1])

    # a leaf missing or malformed: neither identical nor a caught falsifier
    def test_missing_evidence_is_neither_identical_nor_caught(self):
        for keys in (("score", "ticks", "draws", "board", "templates", "result_sha256", "events", "decisions", "after"),
                     ("draws",), ("after",), ("decisions",)):
            for expect in ("identical", "differ"):
                with self.subTest(keys=keys, expect=expect):
                    both = self.log("r2.jsonl", [without(record(m), *keys) for m in F40])
                    cand = self.log("c.jsonl", [without(record(m), *keys) for m in F40])
                    self.assertEqual(self.compare(cand, "--expect", expect, ref=both).returncode, 2)
                    self.assertEqual(self.compare(cand, "--expect", expect).returncode, 2)

    def test_a_malformed_leaf_in_the_candidate_is_malformed_not_a_difference(self):
        for path, bad in ((("board", "statistics", "shots", 1), 256), (("board", "statistics", "shots"), [1]),
                          (("after", "ds", 5), "0" * 63), (("after", "ds", 5), dg("x").upper()),
                          (("draws", "per_minute", 3, 1), 0), (("templates", "0"), 0), (("templates", "67"), 1),
                          (("decisions", 0, 1), "nonsense"), (("score", 0), True), (("ticks", ), 4000.0)):
            for expect in ("identical", "differ"):
                with self.subTest(path=path, bad=bad, expect=expect):
                    cand = self.log("c.jsonl", self.matches(**{F40[6]: edited(record(F40[6]), path, bad)}))
                    r = self.compare(cand, "--expect", expect)
                    self.assertEqual(r.returncode, 2, r.stdout)

    def test_a_container_is_checked_down_to_its_contents(self):
        """E032's class 'a container checked but not its contents': right length, wrong contents."""
        r6 = record(F40[6])
        r6["after"]["ds"] = ["zz" * 32] * records.DS_BLOCKS
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[6]: r6}))).returncode, 2)
        r6 = record(F40[6])
        r6["after"]["ranges"] = {name: ["zz" * 32] * len(v) for name, v in r6["after"]["ranges"].items()}
        if records.RANGES:
            self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[6]: r6}))).returncode, 2)
        r6 = record(F40[6])
        r6["draws"]["per_minute"] = [[1, 5, dg("a")], [2, 5, "short"]]
        r6["draws"]["count"] = 10
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[6]: r6}))).returncode, 2)

    def test_the_range_digests_must_have_the_exact_count(self):
        if not records.RANGES:
            self.skipTest("no range declared")
        name = next(iter(records.RANGES))
        r6 = record(F40[6])
        r6["after"]["ranges"][name] = r6["after"]["ranges"][name][:-1]
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[6]: r6}))).returncode, 2)
        r6["after"]["ranges"][name] = record(F40[6])["after"]["ranges"][name] + [dg("one more")]
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[6]: r6}))).returncode, 2)

    def test_the_draws_per_minute_must_add_up(self):
        r6 = record(F40[6])
        r6["draws"]["count"] += 1
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[6]: r6}))).returncode, 2)

    def test_completion_keys_missing_are_malformed(self):
        cand = self.log("c.jsonl", [without(record(m), "error", "stopped_at_board", "strays") for m in F40])
        for expect in ("identical", "differ"):
            self.assertEqual(self.compare(cand, "--expect", expect).returncode, 2)

    def test_an_unknown_key_is_refused(self):
        """No hooked reference passes as the unhooked one (T59's ports and variant are keys of a later grammar)."""
        for key in ("ports", "variant", "skipped", "engine", "hook_counts"):
            cand = self.log("c.jsonl", self.matches(**{F40[0]: dict(record(F40[0]), **{key: 1})}))
            self.assertEqual(self.compare(cand).returncode, 2, key)
            ref = self.log("r2.jsonl", [dict(record(m), **{key: 1}) if m == F40[0] else record(m) for m in F40])
            self.assertEqual(self.compare(self.log("c2.jsonl", self.matches()), ref=ref).returncode, 2, key)

    def test_evidence_beside_an_error_or_partial_evidence_is_refused(self):
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[1]: record(F40[1], error="x")}))).returncode, 2)
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[1]: record(F40[1], after=None)}))).returncode, 2)
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches(**{F40[1]: incomplete(F40[1], error=None, stopped_at_board=True)}))).returncode, 2)

    # the same run: the declared match, the image, the mask
    def test_another_declaration_image_or_mask_is_refused(self):
        for over in ({"spec_sha256": dg("another seed")}, {"image_sha256": dg("another image")},
                     {"mask": [["DS", 0, 16]]}):
            with self.subTest(over):
                r = self.compare(self.log("c.jsonl", self.matches(**{F40[3]: record(F40[3], **over)})))
                self.assertEqual(r.returncode, 2, r.stdout)
        ref = self.log("r2.jsonl", [record(m, spec_sha256=dg("x")) if m == F40[3] else record(m) for m in F40])
        self.assertEqual(self.compare(self.log("c.jsonl", self.matches()), ref=ref).returncode, 2)

    def test_a_candidate_over_the_same_mask_as_its_reference_passes(self):
        mask = [["DS", 0, 16], ["P", 5000, 64]]
        ref = self.log("r2.jsonl", [record(m, mask=mask) for m in F40])
        self.assertEqual(self.compare(self.log("c.jsonl", [record(m, mask=mask) for m in F40]), ref=ref).returncode, 0)
        self.assertEqual(self.compare(self.log("c2.jsonl", self.matches()), ref=ref).returncode, 2)

    def test_unsorted_or_overlapping_masks_are_refused(self):
        for mask in ([["DS", 100, 16], ["DS", 0, 16]], [["DS", 0, 32], ["DS", 16, 16]], [["X", 0, 1]],
                     [["DS", 0, 0]], [["DS", 65535, 2]], [["DS", 0]]):
            with self.subTest(mask):
                cand = self.log("c.jsonl", [record(m, mask=mask) for m in F40])
                self.assertEqual(self.compare(cand, ref=cand).returncode, 2)

    # --no-screen
    def test_no_screen_leaves_out_only_the_screen(self):
        screen_bad = record(F40[5])
        screen_bad["board"]["screen_sha256"] = dg("other screen")
        cand = self.log("c.jsonl", self.matches(**{F40[5]: screen_bad}))
        self.assertEqual(self.compare(cand).returncode, 1)
        self.assertEqual(self.compare(cand, "--no-screen").returncode, 0)
        self.assertEqual(self.compare(cand, "--no-screen", "--expect", "differ").returncode, 1)
        if records.SCREEN_DS_BLOCKS:
            k = records.SCREEN_DS_BLOCKS[0]
            ds_bad = edited(record(F40[5]), ("after", "ds", k), dg("other screen block"))
            cand = self.log("c2.jsonl", self.matches(**{F40[5]: ds_bad}))
            self.assertEqual(self.compare(cand).returncode, 1)
            self.assertEqual(self.compare(cand, "--no-screen").returncode, 0)
        other = records.SCREEN_DS_BLOCKS and next(k for k in range(records.DS_BLOCKS) if k not in records.SCREEN_DS_BLOCKS) or 0
        bad = edited(record(F40[5]), ("after", "ds", other), dg("a block that is not the screen's"))
        self.assertEqual(self.compare(self.log("c3.jsonl", self.matches(**{F40[5]: bad})), "--no-screen").returncode, 1)
        for field in (("ticks",), ("result_sha256",), ("draws", "digest")):
            bad = edited(record(F40[5]), field, 1 if field == ("ticks",) else dg("x"))
            self.assertEqual(self.compare(self.log("c4.jsonl", self.matches(**{F40[5]: bad})), "--no-screen").returncode, 1)


class CommandLine(Base):
    def test_unknown_family_and_missing_files_are_malformed(self):
        cand = self.log("c.jsonl", self.matches())
        self.assertEqual(self.compare(cand, family="F41").returncode, 2)
        self.assertEqual(self.compare(cand, family="F40,F40").returncode, 2)
        self.assertEqual(self.compare(cand, family="").returncode, 2)
        r = subprocess.run([sys.executable, "-B", str(COMPARE), "--family", "F40", "--candidate",
                            str(Path(self.tmp.name) / "none.jsonl"), "--reference", str(self.ref)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout)
        r = subprocess.run([sys.executable, "-B", str(COMPARE), "--family", "F40", "--candidate", str(cand),
                            "--reference", str(Path(self.tmp.name) / "none.jsonl")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 2, r.stdout)

    def test_all_asks_for_every_family(self):
        ref = self.log("r2.jsonl", [record(m) for m in sorted(EXPECTED)])
        cand = self.log("c.jsonl", [record(m) for m in sorted(EXPECTED)])
        r = self.compare(cand, ref=ref, family="ALL")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("matches expected identical", r.stdout)
        short = self.log("c2.jsonl", [record(m) for m in sorted(EXPECTED)[1:]])
        self.assertEqual(self.compare(short, ref=ref, family="ALL").returncode, 2)

    def test_each_family_uses_its_own_reference_by_default(self):
        """Without --reference the reference is the family's declared one: the committed log (T57's) compared with
        itself passes, and a missing log is malformed, not a pass."""
        historical=ROOT/FAMILIES["F40"].reference
        extended=ROOT/FAMILIES["S"].reference
        self.assertEqual(FAMILIES["O8"].reference,FAMILIES["F40"].reference)
        self.assertNotEqual(FAMILIES["S"].reference,FAMILIES["F40"].reference)
        original=compare_module.load(historical)
        expected_old={mid:digest for mid,digest in EXPECTED.items() if mid not in ('S/no-managed-side','S/set-piece-taker') and not mid.startswith(('R/','FS/'))}
        lines,ok=compare_module.check(original,original,expected_old,image_sha256=IMAGE)
        self.assertTrue(ok,lines)
        self.assertIn("62 matches expected identical, 62 pass, 0 fail",lines)
        r=subprocess.run([sys.executable,"-B",str(COMPARE),"--family","F40,O8,S","--candidate",str(extended)],
                         capture_output=True,text=True,cwd=self.tmp.name)
        self.assertEqual(r.returncode,0,r.stdout[-500:])
        self.assertIn("64 matches expected identical, 64 pass, 0 fail",r.stdout)
        raw_r=ROOT/FAMILIES['R'].reference
        self.assertNotEqual(raw_r,extended)
        joined=Path(self.tmp.name)/'all75-original.jsonl'
        joined.write_bytes(extended.read_bytes()+raw_r.read_bytes()+(ROOT/FAMILIES['FS'].reference).read_bytes())
        complete=subprocess.run([sys.executable,'-B',str(COMPARE),'--family','ALL','--candidate',str(joined)],capture_output=True,text=True)
        self.assertEqual(complete.returncode,0,complete.stdout[-500:])
        self.assertIn('75 matches expected identical, 75 pass, 0 fail',complete.stdout)
        for oldsize,path in [(62,historical),(63,ROOT/'experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl'),(64,extended)]:
            refused=subprocess.run([sys.executable,'-B',str(COMPARE),'--family','ALL','--candidate',str(path)],capture_output=True,text=True)
            self.assertEqual(refused.returncode,2,(oldsize,refused.stdout))
            self.assertIn('R/',refused.stdout)
        # Historical62 cannot be silently accepted as the now75-match family.
        short=subprocess.run([sys.executable,"-B",str(COMPARE),"--family","F40,O8,S","--candidate",str(historical)],
                             capture_output=True,text=True,cwd=self.tmp.name)
        self.assertEqual(short.returncode,2)
        self.assertIn("S/no-managed-side",short.stdout)
        missing = subprocess.run([sys.executable, "-B", str(COMPARE), "--family", "F40", "--candidate", str(self.ref),
                                  "--reference", str(Path(self.tmp.name) / "none.jsonl")], capture_output=True, text=True)
        self.assertEqual(missing.returncode, 2)

    def test_strict_json_and_encoding(self):
        text = [json.dumps(record(m)) for m in F40]
        good = "\n".join(text) + "\n"
        p = Path(self.tmp.name) / "s.jsonl"
        variants = {
            "NaN": good.replace('"ticks": ' + str(record(F40[0])["ticks"]), '"ticks": NaN', 1),
            "1e999": good.replace('"cpu_s": 9.5', '"cpu_s": 1e999', 1),
            "-Infinity": good.replace('"cpu_s": 9.5', '"cpu_s": -Infinity', 1),
            "duplicate key": good.replace('"kit": "2"', '"kit": "2", "kit": "2"', 1),
            "no final newline": good.rstrip("\n"),
            "BOM": "\ufeff" + good,
        }
        for name, text in variants.items():
            with self.subTest(name):
                self.assertNotEqual(text, good)
                p.write_text(text, encoding="utf-8")
                self.assertEqual(self.compare(p).returncode, 2)
        p.write_bytes(b"\xff\xfe" + good.encode())
        self.assertEqual(self.compare(p).returncode, 2)
        p.write_text(good.replace('"kit": "2"', '"kit": "٢"', 1))
        self.assertEqual(self.compare(p).returncode, 2)
        p.write_text(good)
        self.assertEqual(self.compare(p).returncode, 0)

    def test_a_blank_line_is_skipped_but_a_broken_one_is_not(self):
        p = Path(self.tmp.name) / "b.jsonl"
        p.write_text("\n".join([json.dumps(record(F40[0])), ""] + [json.dumps(record(m)) for m in F40[1:]]) + "\n")
        self.assertEqual(self.compare(p).returncode, 0)
        p.write_text("\n".join([json.dumps(record(m)) for m in F40] + ["{broken"]) + "\n")
        self.assertEqual(self.compare(p).returncode, 2)


class E032Seeds(Base):
    """Done-when 2: the reference's ten E032 seeds equal check.py's EXPECTED_FAMILY, printed per seed."""

    def e032_records(self, **change):
        out = []
        for seed, (score, ticks, draws, digest) in sorted(EXPECTED_FAMILY.items()):
            mid = f"F40/e032-{seed:04x}"
            r = record(mid, score=score, ticks=ticks,
                       draws={"count": draws, "digest": digest, "per_minute": [[1, draws, dg(mid, "m")]]})
            out.append(change.get(mid, r))
        return out

    def run_e032(self, recs, *extra):
        p = self.log("e.jsonl", recs)
        return subprocess.run([sys.executable, "-B", str(COMPARE), "--e032", "--candidate", str(p), *extra],
                              capture_output=True, text=True)

    def test_the_ten_seeds_are_printed_and_equal(self):
        r = self.run_e032(self.e032_records())
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(len(r.stdout.strip().splitlines()), 11)
        self.assertIn("seed 0x0101: score [1, 0] ticks 4279 draws 192967 digest a365b543... equal", r.stdout)

    def test_each_field_that_differs_fails_that_seed(self):
        for field, bad in (("score", [0, 0]), ("ticks", 1), ("draws", {"count": 5, "digest": dg("x"), "per_minute": [[1, 5, dg("y")]]}),
                           ("draws", {"count": 192967, "digest": dg("x"), "per_minute": [[1, 192967, dg("y")]]})):
            mid = "F40/e032-0101"
            score, ticks, draws, digest = EXPECTED_FAMILY[0x0101]
            good = record(mid, score=score, ticks=ticks, draws={"count": draws, "digest": digest, "per_minute": [[1, draws, dg("m")]]})
            with self.subTest(field, bad=bad):
                r = self.run_e032(self.e032_records(**{mid: dict(good, **{field: bad})}))
                self.assertEqual(r.returncode, 1, r.stdout)
                self.assertIn("seed 0x0101", [l for l in r.stdout.splitlines() if "FAIL" in l][0])

    def test_a_missing_incomplete_or_other_match_is_malformed(self):
        recs = self.e032_records()
        self.assertEqual(self.run_e032(recs[1:]).returncode, 2)
        self.assertEqual(self.run_e032([incomplete(recs[0]["id"])] + recs[1:]).returncode, 2)
        self.assertEqual(self.run_e032([dict(recs[0], spec_sha256=dg("other"))] + recs[1:]).returncode, 2)
        self.assertEqual(self.run_e032(recs + [recs[0]]).returncode, 2)
        self.assertEqual(self.run_e032(recs, "--family", "F40").returncode, 2)


class LeafFuzz(unittest.TestCase):
    """E032 round 4's class, for these records: every leaf of a record, changed one way at a time, makes it invalid."""

    @staticmethod
    def leaves(obj, path=()):
        if isinstance(obj, dict):
            for k, v in obj.items():
                yield from LeafFuzz.leaves(v, path + (k,))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                yield from LeafFuzz.leaves(v, path + (i,))
        else:
            yield path, obj

    @staticmethod
    def get(obj, path):
        for k in path:
            obj = obj[k]
        return obj

    def mutations(self, value):
        yield "null" if value is not None else "zero", (None if value is not None else 0)
        yield "list", [value]
        if isinstance(value, bool):
            yield "string", "true"
            yield "int", 1 if value is False else 0
        elif isinstance(value, int):
            yield "bool", True
            yield "string", str(value)
            yield "float", float(value) + 0.5
            yield "huge", 1 << 70
            yield "negative", -1 - abs(value)
        elif isinstance(value, float):
            yield "bool", False
            yield "string", str(value)
            yield "negative", -1.0
            yield "huge", 1e7
        elif isinstance(value, str):
            yield "int", 7
            yield "trailing newline", value + "\n"
            yield "leading space", " " + value
            yield "NUL", value + "\x00"
            yield "shorter", value[:-1]
            yield "longer", value + "0"
            yield "upper", value.upper() if value.upper() != value else value + "A"
            yield "arabic digit", "٢" + value[1:]

    # a change that leaves another valid value is no error: the id and the family are checked against the declared
    # match by compare.py (not by the grammar), and the kit version is any 1-3 digit string
    FREE = {("id",): ("shorter", "longer", "upper"), ("kit",): ("longer",)}

    def test_every_leaf_changed_is_invalid(self):
        base = record(F40[0])
        checked = 0
        for path, value in self.leaves(base):
            if path == ("error",) or path[0] == "mask":
                continue
            for name, bad in self.mutations(value):
                if value is None and name == "zero" or name in self.FREE.get(path, ()):
                    continue
                with self.subTest(path=path, mutation=name):
                    with self.assertRaises(records.SchemaError):
                        records.validate(edited(base, path, bad))
                checked += 1
        self.assertGreater(checked, 1000)

    def test_every_key_removed_and_every_unknown_key_added_is_invalid(self):
        base = record(F40[0])

        def walk(obj, path=()):
            if isinstance(obj, dict):
                yield path
                for k, v in obj.items():
                    yield from walk(v, path + (k,))
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    yield from walk(v, path + (i,))
        objects = list(walk(base))
        for path in objects:
            bad = copy.deepcopy(base)
            self.get(bad, path)["unknown"] = 1
            with self.subTest(added=path):
                with self.assertRaises(records.SchemaError):
                    records.validate(bad)
            if path == ("templates",):
                continue                    # a template with no line is simply absent
            for key in self.get(base, path):
                bad = copy.deepcopy(base)
                del self.get(bad, path)[key]
                with self.subTest(removed=path + (key,)):
                    with self.assertRaises(records.SchemaError):
                        records.validate(bad)
        self.assertGreater(len(objects), 8)

    def test_every_list_one_element_longer_or_shorter_is_invalid_where_the_length_is_fixed(self):
        base = record(F40[0])
        fixed = [("score",), ("board", "bars"), ("board", "bars", 0), ("board", "final_score"), ("after", "ds"),
                 ("decisions", 0), ("draws", "per_minute", 0)] + [("after", "ranges", n) for n in records.RANGES]
        for path in fixed:
            for change in ("longer", "shorter"):
                bad = copy.deepcopy(base)
                node = self.get(bad, path)
                node.append(node[-1]) if change == "longer" else node.pop()
                with self.subTest(path=path, change=change):
                    with self.assertRaises(records.SchemaError):
                        records.validate(bad)

    def test_an_error_text_is_one_clean_ascii_line(self):
        base = incomplete(F40[0])
        records.validate(base)
        for bad in ("a\n", "a\nb", " a", "a ", "caf\u00e9", "a\x00", "a\tb", "", "x" * 201, "\u0662"):
            with self.subTest(repr(bad)):
                with self.assertRaises(records.SchemaError):
                    records.validate(dict(base, error=bad))
        records.validate(dict(base, error="x" * 200))
        records.validate(dict(base, error="E"))

    def test_numbers_are_ints_not_floats_and_floats_are_finite(self):
        base = record(F40[0])
        for nasty in (float("nan"), float("inf"), -0.0, True, "9.5"):
            with self.subTest(nasty=nasty):
                with self.assertRaises(records.SchemaError):
                    records.validate(dict(base, cpu_s=nasty))
        records.validate(dict(base, cpu_s=0))
        records.validate(dict(base, cpu_s=12.5))

    def test_the_valid_synthetic_record_is_valid(self):
        records.validate(record(F40[0]))
        records.validate(incomplete(F40[0]))
        records.validate(record(F40[0], strays=["pause"]))
        self.assertTrue(records.is_completed(record(F40[0])))
        self.assertFalse(records.is_completed(record(F40[0], strays=["pause"])))


class StrictLoads(unittest.TestCase):
    def test_loads_refuses_what_json_loads_accepts(self):
        for text in ('{"a": NaN}', '{"a": Infinity}', '{"a": -Infinity}', '{"a": 1e999}', '{"a": 1, "a": 2}',
                     '{"a": {"b": 1, "b": 1}}'):
            with self.subTest(text):
                json.loads(text)
                with self.assertRaises((ValueError, records.SchemaError)):
                    records.loads(text)
        self.assertEqual(records.loads('{"a": [1, 2.5, "x", null, true]}'), {"a": [1, 2.5, "x", None, True]})
        self.assertFalse(math.isnan(records.loads("[0.5]")[0]))

    def test_dumps_refuses_non_finite(self):
        with self.assertRaises(ValueError):
            records.dumps({"a": float("nan")})


class EngineIdentity(unittest.TestCase):
    """Optional metadata identifies the backend without changing comparison evidence."""
    def test_valid_backend_metadata_and_closed_invalid_values(self):
        legacy = record(F40[0])
        records.validate(legacy)
        original = dict(legacy, engine='original')
        records.validate(original)
        candidate = dict(legacy, engine='port', ports=['pilot'], variant=None,
                         port_calls={'0791:8889': 1})
        records.validate(candidate)
        self.assertEqual(compare_module.differences(original, candidate), [])
        for value in (None, True, 1, '', 'other', ['port']):
            with self.subTest(engine=value):
                with self.assertRaises(records.SchemaError):
                    records.validate(dict(candidate, engine=value))
        with self.assertRaises(records.SchemaError):
            records.validate(dict(legacy, engine='port'))
        with self.assertRaises(records.SchemaError):
            records.validate(dict(candidate, unexpected_metadata='ignored'))


if __name__ == "__main__":
    unittest.main()
