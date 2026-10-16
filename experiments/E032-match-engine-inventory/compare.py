#!/usr/bin/env python3
"""E032: the whole-match acceptance check. Compares a candidate log with a reference log, match by match
(same seed), and FAILS CLOSED.

    python3 -B experiments/E032-match-engine-inventory/compare.py <reference.jsonl> <candidate.jsonl> --seeds 0x1234,0x2345 [--expect identical|differ]

--seeds is the seed family the candidate must hold: exactly these seeds, each once. The reference must
hold each of them (it may hold more: a family can be a subset of a bigger reference log), each once.

Every record is validated before anything is compared, recursively, against the one schema in
record_schema.py (PR 243 review rounds 1-3, issue 246): the fields every record carries (seed, error,
stopped_at_board, strays, cpu_s) and, for a COMPLETED record (no error, stopped at the full-time board, no
stray key wait), every piece of evidence the comparison uses down to its values: the score bytes, ticks,
draws, the digest, the 11 statistics rows with their labels, value pairs and addresses, and the templates'
ids and counts. A record that fails validation makes the log MALFORMED: it never counts as equal, nor as a
difference. Every reference record of the family must be completed.

Logs are read strictly (record_schema.loads: UTF-8, no NaN/Infinity, no overflowing number, no duplicate key).
The reference must be unhooked matches of the original (no skipped/ported/variant/hook_counts/port_calls),
reference and candidate must name the same start state (start_record, watchstart_sha256), and each
`--field KEY=JSON` (repeatable) names the run the candidate must be (e.g. variant="bound-36" or
skipped=["0791:8F10"]), so a log of another run cannot stand in (round 4).

--expect identical (the default, a port or a skip accepted): every candidate record must be completed too,
and equal to its reference in score, ticks, draws, the draws digest, the board's raw statistics and the
commentary's template counts.

--expect differ (a falsifier caught): every candidate record must differ from its reference in one of those
fields, or be a match that did not complete (a falsifier that hangs or errors is caught as well).

Prints one line per seed and a summary; exits 0 only when every expected seed passes, 1 when a seed fails
its expectation, and 2 on a malformed log or family (an unreadable line, a record that fails validation, a
duplicate seed, a missing or unexpected seed, an empty family)."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import record_schema  # noqa: E402

FIELDS = ("score", "ticks", "draws", "draws_digest", "statistics_raw", "templates")


class Malformed(Exception):
    pass


def completed(r):
    """None when the (validated) record is a completed match, else why not."""
    why = []
    if r["error"] is not None:
        why.append(f"error {r['error']!r}")
    if r["stopped_at_board"] is not True:
        why.append("did not stop at the full-time board")
    if r["strays"]:
        why.append(f"strays {r['strays']!r}")
    return "; ".join(why) or None


def validate(r, where):
    """Raise Malformed unless the record conforms to record_schema (see the module's text)."""
    try:
        record_schema.validate(r)
    except record_schema.SchemaError as e:
        raise Malformed(f"{where}: {e}")


def load(path):
    """Seed -> record. Strict: UTF-8, one JSON object per line (record_schema.loads: no NaN/Infinity, no
    overflowing number, no duplicate key), every record valid, every seed once. Blank lines are skipped."""
    out = {}
    try:
        text = Path(path).read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise Malformed(f"{path}: {e}")
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        try:
            r = record_schema.loads(line)
        except (ValueError, RecursionError) as e:
            raise Malformed(f"{path}:{n}: not strict JSON ({e})")
        validate(r, f"{path}:{n}")
        if r["seed"] in out:
            raise Malformed(f"{path}:{n}: seed 0x{r['seed']:04x} appears twice")
        out[r["seed"]] = r
    return out


HOOK_KEYS = ("skipped", "ported", "variant", "hook_counts", "port_calls")
SEED_ARG = re.compile(r"0x[0-9a-fA-F]{1,4}|[0-9]{1,5}")


def check(ref, cand, seeds, expect, fields=()):
    """(lines, passed) for the family; raises Malformed on a missing or unexpected seed, an incomplete or
    hooked reference, two start states, or a candidate record whose declared run (`fields`: key, value
    pairs such as variant or skipped) is not the one the caller names (round 4)."""
    for seed, r in ref.items():
        hooked = [k for k in HOOK_KEYS if k in r]
        if hooked:
            raise Malformed(f"reference seed 0x{seed:04x} is not an unhooked match of the original ({hooked})")
    for seed, r in cand.items():
        for key, value in fields:
            if key not in r or r[key] != value or type(r[key]) is not type(value):
                raise Malformed(f"candidate seed 0x{seed:04x}: {key} is {r.get(key)!r}, not {value!r}")
    missing_ref = [s for s in seeds if s not in ref]
    missing = [s for s in seeds if s not in cand]
    unexpected = sorted(set(cand) - set(seeds))
    if missing_ref or missing or unexpected:
        raise Malformed("seed family mismatch: " + "; ".join(
            f"{what}: {', '.join(f'0x{s:04x}' for s in lst)}" for what, lst in (
                ("missing from the reference", missing_ref), ("missing from the candidate", missing),
                ("unexpected in the candidate", unexpected)) if lst))
    for seed in seeds:
        why = completed(ref[seed])
        if why:
            raise Malformed(f"reference seed 0x{seed:04x} is not a completed match ({why})")
        for key in ("start_record", "watchstart_sha256"):      # the same start state, or no comparison
            if ref[seed][key] != cand[seed][key]:
                raise Malformed(f"seed 0x{seed:04x}: {key} differs ({ref[seed][key]!r} / {cand[seed][key]!r})")
    lines, passed = [], 0
    for seed in seeds:
        a, b = ref[seed], cand[seed]
        bad = completed(b)
        diff = [f for f in FIELDS if a[f] != b[f]] if not bad else []
        head = (f"seed 0x{seed:04x}: score {a['score']} ticks {a['ticks']} draws {a['draws']} "
                f"cpu {a.get('cpu_s')} s -> {b.get('cpu_s')} s; ")
        if expect == "identical":
            ok = not bad and not diff
            verdict = ("identical" if ok else
                       f"NOT COMPLETED ({bad})" if bad else "DIFFER: " + ", ".join(diff))
        else:
            ok = bool(bad or diff)
            verdict = (f"caught: not completed ({bad})" if bad else
                       "caught: differ in " + ", ".join(diff) if diff else "NOT CAUGHT: identical")
        passed += ok
        lines.append(head + verdict + ("" if ok else ": FAIL"))
    lines.append(f"{len(seeds)} seeds expected {expect}, {passed} pass, {len(seeds) - passed} fail")
    return lines, passed == len(seeds)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("reference")
    ap.add_argument("candidate")
    ap.add_argument("--seeds", required=True, help="the expected seed family, comma-separated (0x.. or decimal)")
    ap.add_argument("--expect", choices=("identical", "differ"), default="identical")
    ap.add_argument("--field", action="append", default=[], metavar="KEY=JSON",
                    help="every candidate record must hold KEY with exactly this JSON value (e.g. variant=\"bound-36\", "
                         "skipped=[\"0791:8F10\"]): the run the caller means, not another one")
    a = ap.parse_args(argv)
    try:
        seeds = []
        for s in a.seeds.split(","):
            if not SEED_ARG.fullmatch(s):
                raise Malformed(f"--seeds: {s!r} is not 0x + 1-4 hex digits or 1-5 decimal digits")
            seeds.append(int(s, 0))
        if len(set(seeds)) != len(seeds):
            raise Malformed("a seed repeated in --seeds")
        fields = []
        for f in a.field:
            key, sep, value = f.partition("=")
            if not sep or key not in record_schema.REQUIRED + record_schema.OPTIONAL:
                raise Malformed(f"--field {f!r}: not KEY=JSON with a record key")
            try:
                fields.append((key, record_schema.loads(value)))
            except ValueError as e:
                raise Malformed(f"--field {f!r}: {e}")
        lines, ok = check(load(a.reference), load(a.candidate), seeds, a.expect, fields)
    except Malformed as e:
        print(f"MALFORMED: {e}")
        return 2
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
