"""E032's comparator rejects a record whose evidence is missing or mangled at ANY level (PR 243 review round
3, issue 246).

Takes a real committed record (the first line of out/timing-delay20-kickoff-20261015.jsonl), mutates one
comparator-relevant field at a time (remove it, null it, give it the wrong type, put it out of range), at every
level: the record's fields, each of the 11 statistics rows and each of their fields and values, the
templates' ids and counts. Each mutation is applied to BOTH logs and to the CANDIDATE only, and compared under
both --expect identical and --expect differ; every one of these must be MALFORMED (exit 2): missing or mangled
evidence is never equality nor a caught falsifier.

The comparator under test is loaded from E032_COMPARE (a path) when set, which is how these tests were shown to
fail on the comparator of round 2 (a537d31)."""
import contextlib
import copy
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E032 = ROOT / "experiments/E032-match-engine-inventory"
COMPARE = Path(os.environ.get("E032_COMPARE", E032 / "compare.py"))
SOURCE = E032 / "out/timing-delay20-kickoff-20261015.jsonl"
DROP = object()          # a sentinel: remove the field


def load_compare():
    spec = importlib.util.spec_from_file_location("e032_compare_under_test", COMPARE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def real_record():
    return json.loads(SOURCE.read_text().splitlines()[0])


def mutations(rec):
    """(name, path, value): set rec[path] to value (DROP removes it)."""
    out = []
    wrong_type = {"seed": "4660", "error": 5, "stopped_at_board": "true", "strays": "none", "cpu_s": "8.3",
                  "score": "1-1", "ticks": "4146", "draws": 1.5, "draws_digest": 5, "statistics_raw": {},
                  "templates": []}
    for k in wrong_type:
        out.append((f"{k} removed", (k,), DROP))
        if k != "error":                       # null is error's valid value
            out.append((f"{k} null", (k,), None))
        out.append((f"{k} wrong type", (k,), wrong_type[k]))
    for k in ("seed", "ticks", "draws", "cpu_s"):
        out.append((f"{k} a boolean", (k,), True))
    out += [("error empty", ("error",), ""), ("strays not strings", ("strays",), [5]),
            ("seed out of range", ("seed",), 0x10000), ("cpu_s negative", ("cpu_s",), -1.0),
            ("ticks zero", ("ticks",), 0), ("ticks negative", ("ticks",), -1), ("draws zero", ("draws",), 0),
            ("digest short", ("draws_digest",), rec["draws_digest"][:63]),
            ("digest upper case", ("draws_digest",), rec["draws_digest"].upper()),
            ("digest not hex", ("draws_digest",), "z" * 64)]
    for name, v in (("one", [1]), ("three", [1, 1, 1]), ("a string", [1, "1"]), ("a null", [1, None]),
                    ("negative", [-1, 1]), ("a boolean", [1, True]), ("over a byte", [256, 0])):
        out.append((f"score {name}", ("score",), v))
    rows = rec["statistics_raw"]
    out += [("statistics empty", ("statistics_raw",), []), ("statistics ten rows", ("statistics_raw",), rows[:10]),
            ("statistics twelve rows", ("statistics_raw",), rows + [rows[0]]),
            ("statistics rows swapped", ("statistics_raw",), [rows[1], rows[0]] + rows[2:])]
    for i, row in enumerate(rows):
        val = "raw_bytes" if "raw_bytes" in row else "raw_words"
        other = "raw_words" if val == "raw_bytes" else "raw_bytes"
        top = 256 if val == "raw_bytes" else 0x10000
        p = ("statistics_raw", i)
        out += [(f"row {i} null", p, None), (f"row {i} a list", p, [1, 2]), (f"row {i} empty", p, {})]
        for k in ("row_label", "address", val):
            out += [(f"row {i} {k} removed", p + (k,), DROP), (f"row {i} {k} null", p + (k,), None),
                    (f"row {i} {k} wrong type", p + (k,), 5 if k != val else "x")]
        out += [(f"row {i} label changed", p + ("row_label",), row["row_label"] + "x"),
                (f"row {i} address changed", p + ("address",), "DS:0000"),
                (f"row {i} extra key", p + ("extra",), 1),
                (f"row {i} other value key", p + (other,), [0, 0])]
        for name, v in (("one", [1]), ("three", [1, 1, 1]), ("a null", [1, None]), ("a string", [1, "2"]),
                        ("negative", [-1, 0]), ("too big", [top, 0]), ("a boolean", [True, 0]),
                        ("a float", [1.5, 0])):
            out.append((f"row {i} {val} {name}", p + (val,), v))
    tid = next(iter(rec["templates"]))
    out += [("templates empty", ("templates",), {})]
    for name, key in (("not a number", "x"), ("out of range", "300"), ("negative", "-1"), ("leading zero", "07")):
        out.append((f"template id {name}", ("templates", key), 1))
    for name, v in (("null", None), ("a string", "2"), ("zero", 0), ("negative", -1), ("a boolean", True),
                    ("a float", 1.5), ("a list", [1])):
        out.append((f"template count {name}", ("templates", tid), v))
    return out


def apply(rec, path, value):
    r = copy.deepcopy(rec)
    d = r
    for k in path[:-1]:
        d = d[k]
    if value is DROP:
        if isinstance(d, dict):
            d.pop(path[-1], None)
        else:
            del d[path[-1]]
    else:
        d[path[-1]] = value
    return r


class EveryMutationIsMalformed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compare = load_compare()
        cls.rec = real_record()
        cls.tmp = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_compare(self, ref, cand, expect):
        d = Path(self.tmp.name)
        (d / "ref.jsonl").write_text(json.dumps(ref) + "\n")
        (d / "cand.jsonl").write_text(json.dumps(cand) + "\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = self.compare.main([str(d / "ref.jsonl"), str(d / "cand.jsonl"), "--seeds",
                                    f"0x{self.rec['seed']:04x}", "--expect", expect])
        return rc, buf.getvalue()

    def test_the_real_record_is_accepted(self):
        self.assertEqual(self.run_compare(self.rec, self.rec, "identical")[0], 0)

    def test_every_mutation_is_malformed(self):
        failures = []
        cases = mutations(self.rec)
        self.assertGreater(len(cases), 150)
        for name, path, value in cases:
            bad = apply(self.rec, path, value)
            for where, ref, cand in (("both logs", bad, bad), ("candidate only", self.rec, bad)):
                for expect in ("identical", "differ"):
                    rc, text = self.run_compare(ref, cand, expect)
                    if rc != 2:
                        failures.append(f"{name}, {where}, --expect {expect}: exit {rc}")
        self.assertEqual(failures, [], f"{len(failures)} of {4 * len(cases)} cases not MALFORMED:\n" +
                         "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
