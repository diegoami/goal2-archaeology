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

--expect identical (the default, a port or a skip accepted): every candidate record must be completed too,
and equal to its reference in score, ticks, draws, the draws digest, the board's raw statistics and the
commentary's template counts.

--expect differ (a falsifier caught): every candidate record must differ from its reference in one of those
fields, or be a match that did not complete (a falsifier that hangs or errors is caught as well).

Prints one line per seed and a summary; exits 0 only when every expected seed passes, 1 when a seed fails
its expectation, and 2 on a malformed log or family (an unreadable line, a record that fails validation, a
duplicate seed, a missing or unexpected seed, an empty family)."""
import argparse
import json
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
    out = {}
    try:
        f = open(path)
    except OSError as e:
        raise Malformed(f"{path}: {e}")
    with f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                r = json.loads(line)
            except ValueError as e:
                raise Malformed(f"{path}:{n}: not JSON ({e})")
            validate(r, f"{path}:{n}")
            if r["seed"] in out:
                raise Malformed(f"{path}:{n}: seed 0x{r['seed']:04x} appears twice")
            out[r["seed"]] = r
    return out


def check(ref, cand, seeds, expect):
    """(lines, passed) for the family; raises Malformed on a missing or unexpected seed or an incomplete
    reference."""
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
    a = ap.parse_args(argv)
    try:
        try:
            seeds = [int(s, 0) for s in a.seeds.split(",") if s.strip()]
        except ValueError as e:
            raise Malformed(f"--seeds: {e}")
        if not seeds:
            raise Malformed("an empty seed family")
        if len(set(seeds)) != len(seeds):
            raise Malformed("a seed repeated in --seeds")
        lines, ok = check(load(a.reference), load(a.candidate), seeds, a.expect)
    except Malformed as e:
        print(f"MALFORMED: {e}")
        return 2
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
