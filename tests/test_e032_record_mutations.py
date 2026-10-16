"""E032's comparator rejects a record whose evidence is missing, mangled or pathological at ANY level (PR 243
review rounds 3 and 4, issue 246).

Takes a real committed record (the first line of out/timing-delay20-kickoff-20261015.jsonl) and changes one
thing at a time:
- round 3: each comparator-relevant field and each nested value removed, nulled, of the wrong type, out of
  range (`mutations`);
- round 4, a fuzz over EVERY leaf of the record (`fuzz`): strings with a trailing or leading newline, space,
  tab or NUL, an Arabic-Indic digit in place of an ASCII one, upper or lower case where the other is meant,
  one character shorter or longer; numbers as NaN, Infinity, -Infinity, 1e999 (JSON tokens written raw),
  -0.0, a float where an int is meant, a boolean, a numeric string, an int beyond 64 bits, negative; booleans
  and nulls as other types; every object with a duplicated key (written raw: json.loads would keep the last)
  and with an unknown key; every list one element longer; template ids and address keys with the same string
  faults.
Each change is written to BOTH logs and to the CANDIDATE only, and compared under --expect identical and
--expect differ: every case must be MALFORMED (exit 2). A test also checks that no E032 script validates with
re.match/re.search or a `$` anchor.

The comparator under test is loaded from E032_COMPARE (a path) when set (its record_schema.py is the one
beside it), which is how these tests were shown to fail on the round-2 comparator and on round 3's schema."""
import contextlib
import copy
import importlib.util
import io
import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E032 = ROOT / "experiments/E032-match-engine-inventory"
COMPARE = Path(os.environ.get("E032_COMPARE", E032 / "compare.py"))
SOURCE = E032 / "out/timing-delay20-kickoff-20261015.jsonl"
DROP = object()          # a sentinel: remove the field


class Raw:
    """A JSON token written as is (NaN, Infinity, 1e999)."""

    def __init__(self, text):
        self.text = text


def emit(obj, dup=None, path=()):
    """JSON text for obj; Raw values verbatim; the object at path `dup` gets its first key twice."""
    if isinstance(obj, Raw):
        return obj.text
    if isinstance(obj, dict):
        items = list(obj.items())
        if dup == path and items:
            items = [items[0]] + items
        return "{" + ", ".join(f"{json.dumps(k)}: {emit(v, dup, path + (k,))}" for k, v in items) + "}"
    if isinstance(obj, list):
        return "[" + ", ".join(emit(v, dup, path + (i,)) for i, v in enumerate(obj)) + "]"
    return json.dumps(obj)


def load_compare():
    sys.modules.pop("record_schema", None)        # the schema beside the comparator under test
    spec = importlib.util.spec_from_file_location("e032_compare_under_test", COMPARE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def real_record():
    return json.loads(SOURCE.read_text().splitlines()[0])


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


def rename_key(rec, path, old, new):
    r = copy.deepcopy(rec)
    d = r
    for k in path:
        d = d[k]
    items = [(new if k == old else k, v) for k, v in d.items()]
    d.clear()
    d.update(items)
    return r


def mutations(rec):
    """Round 3: (name, path, value)."""
    out = []
    wrong_type = {"seed": "4660", "error": 5, "stopped_at_board": "true", "strays": "none", "cpu_s": "8.3",
                  "score": "1-1", "ticks": "4146", "draws": 1.5, "draws_digest": 5, "statistics_raw": {},
                  "templates": []}
    for k in wrong_type:
        out.append((f"{k} removed", (k,), DROP))
        if k != "error":
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


ARABIC = {str(d): chr(0x660 + d) for d in range(10)}


def string_faults(v):
    out = [v + "\n", "\n" + v, v + " ", " " + v, v + "\t", v + "\x00", v[:-1] if v else "x", v + (v[-1:] or "x")]
    if v.upper() != v:
        out.append(v.upper())
    if v.lower() != v:
        out.append(v.lower())
    digit = next((c for c in v if c in ARABIC), None)
    if digit:
        out.append(v.replace(digit, ARABIC[digit], 1))
    return [x for x in out if x != v]


def key_faults(k, path):
    out = string_faults(k)
    if path == ("templates",):
        # one digit more or less is another real template id (valid evidence of another match), not a fault
        out = [x for x in out if x not in (k[:-1], k + k[-1:])]
    return [x for x in out + ["0" + k, "+" + k, k + ".0", "-" + k] if x != k]


def fuzz(rec):
    """Round 4: (name, text of the mutated record). Every leaf, key and container of the record."""
    out = []
    float_fields = {("cpu_s",), ("wall_s",)}

    def walk(obj, path):
        if isinstance(obj, dict):
            out.append((f"{path} duplicated key", emit(rec, dup=path)))
            out.append((f"{path} unknown key", emit(apply(rec, path + ("zz_unknown",), 1))))
            if path in (("templates",), ("hook_counts",)):
                for k in list(obj):
                    for bad in key_faults(k, path):
                        out.append((f"{path} key {k!r} -> {bad!r}", emit(rename_key(rec, path, k, bad))))
            for k, v in obj.items():
                walk(v, path + (k,))
            return
        if isinstance(obj, list):
            if obj:
                out.append((f"{path} one element longer", emit(apply(rec, path, obj + [obj[-1]]))))
            for i, v in enumerate(obj):
                walk(v, path + (i,))
            return
        if isinstance(obj, bool):
            values = [1, 0, "true", None, Raw("NaN")]
        elif obj is None:
            values = ["", " ", "\n", 0, False, [], Raw("NaN")]
        elif isinstance(obj, str):
            values = string_faults(obj)
        elif isinstance(obj, int):
            values = [Raw("NaN"), Raw("Infinity"), Raw("-Infinity"), Raw("1e999"), -0.0, float(obj), True,
                      str(obj), 2 ** 70, -1] + ([-obj] if obj > 0 else [])
        else:   # float
            values = [Raw("NaN"), Raw("Infinity"), Raw("-Infinity"), Raw("1e999"), -0.0, True, str(obj), 2 ** 70,
                      -1.0] + ([-obj] if obj > 0 else [])
        if isinstance(obj, int) and not isinstance(obj, bool) and path in float_fields:
            values = [v for v in values if not isinstance(v, float) or v != float(obj)]
        for v in values:
            out.append((f"{path} = {v.text if isinstance(v, Raw) else repr(v)}", emit(apply(rec, path, v))))

    walk(rec, ())
    return out


class Compare:
    @classmethod
    def setUpClass(cls):
        cls.compare = load_compare()
        cls.rec = real_record()
        cls.tmp = tempfile.TemporaryDirectory()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_text(self, ref_text, cand_text, expect):
        d = Path(self.tmp.name)
        (d / "ref.jsonl").write_text(ref_text + "\n")
        (d / "cand.jsonl").write_text(cand_text + "\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            try:
                rc = self.compare.main([str(d / "ref.jsonl"), str(d / "cand.jsonl"), "--seeds",
                                        f"0x{self.rec['seed']:04x}", "--expect", expect])
            except Exception as e:          # an uncaught exception is not a clean MALFORMED
                return f"raised {type(e).__name__}", buf.getvalue()
        return rc, buf.getvalue()

    def all_malformed(self, cases):
        real = json.dumps(self.rec)
        failures = []
        for name, text in cases:
            for where, ref, cand in (("both logs", text, text), ("candidate only", real, text)):
                for expect in ("identical", "differ"):
                    rc, _ = self.run_text(ref, cand, expect)
                    if rc != 2:
                        failures.append(f"{name}, {where}, --expect {expect}: exit {rc}")
        return failures


class EveryMutationIsMalformed(Compare, unittest.TestCase):
    def test_the_real_record_is_accepted(self):
        real = json.dumps(self.rec)
        self.assertEqual(self.run_text(real, real, "identical")[0], 0)
        self.assertEqual(self.run_text(real, real, "differ")[0], 1)     # an unchanged copy is not caught

    def test_every_mutation_is_malformed(self):
        cases = [(name, json.dumps(apply(self.rec, path, value))) for name, path, value in mutations(self.rec)]
        self.assertGreater(len(cases), 150)
        failures = self.all_malformed(cases)
        self.assertEqual(failures, [], f"{len(failures)} of {4 * len(cases)} cases not MALFORMED:\n" +
                         "\n".join(failures))


class EveryPathologicalValueIsMalformed(Compare, unittest.TestCase):
    def test_round4_review_cases(self):
        r = self.rec
        tid = "38" if "38" in r["templates"] else next(iter(r["templates"]))
        cases = [("digest + newline", emit(apply(r, ("draws_digest",), r["draws_digest"] + "\n"))),
                 ("template id + newline", emit(rename_key(r, ("templates",), tid, tid + "\n"))),
                 ("cpu_s NaN", emit(apply(r, ("cpu_s",), Raw("NaN")))),
                 ("cpu_s 1e999", emit(apply(r, ("cpu_s",), Raw("1e999"))))]
        failures = self.all_malformed(cases)
        self.assertEqual(failures, [], "\n".join(failures))

    def test_the_fuzz_is_malformed(self):
        cases = fuzz(self.rec)
        self.assertGreater(len(cases), 1000)
        failures = self.all_malformed(cases)
        self.assertEqual(failures, [], f"{len(failures)} of {4 * len(cases)} cases not MALFORMED:\n" +
                         "\n".join(failures))


class NoLooseValidationPatterns(unittest.TestCase):
    """Round 4: every pattern in the E032 scripts validates the whole string (re.fullmatch), never a prefix
    (re.match), a substring (re.search) or up to a final newline (`$`)."""

    def test_no_match_search_or_dollar_anchor(self):
        bad = []
        for p in sorted(E032.glob("*.py")):
            for n, line in enumerate(p.read_text().splitlines(), 1):
                code = line.split("#", 1)[0]
                if re.search(r"\.(match|search)\(", code) or re.search(r"\$[\"']", code):
                    bad.append(f"{p.name}:{n}: {line.strip()}")
        self.assertEqual(bad, [], "\n".join(bad))

    def test_the_schema_uses_ascii_digit_classes(self):
        self.assertNotIn(r"\d", (E032 / "record_schema.py").read_text())


if __name__ == "__main__":
    unittest.main()
