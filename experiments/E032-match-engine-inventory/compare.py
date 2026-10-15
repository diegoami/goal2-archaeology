#!/usr/bin/env python3
"""E032: the whole-match acceptance check. Compares a candidate log with a reference log, match by match
(same seed), and FAILS CLOSED.

    python3 -B experiments/E032-match-engine-inventory/compare.py <reference.jsonl> <candidate.jsonl> --seeds 0x1234,0x2345 [--expect identical|differ]

--seeds is the seed family the candidate must hold: exactly these seeds, each once. The reference must
hold each of them (it may hold more: a family can be a subset of a bigger reference log), each once.
Every reference record must be a completed match: no error, stopped at the full-time board, no undeclared
key-wait strays (the 000E wait family's log is empty).

--expect identical (the default, a port or a skip accepted): every candidate record must be a completed
match too, and equal to its reference in score, ticks, main-seed draws, the draws digest, the board's raw
statistics and the commentary's template counts.

--expect differ (a falsifier caught): every candidate record must differ from its reference in one of those
fields, or be a match that did not complete (a falsifier that hangs or errors is caught as well).

Prints one line per seed and a summary; exits 0 only when every expected seed passes, 1 otherwise, and 2 on
a malformed log or family (a duplicate seed, a missing or unexpected seed)."""
import argparse
import json
import sys

FIELDS = ("score", "ticks", "draws", "draws_digest", "statistics_raw", "templates")


class Malformed(Exception):
    pass


def load(path):
    out = {}
    with open(path) as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            r = json.loads(line)
            if r["seed"] in out:
                raise Malformed(f"{path}:{n}: seed 0x{r['seed']:04x} appears twice")
            out[r["seed"]] = r
    return out


def completed(r):
    """None when the record is a completed match, else why not."""
    why = []
    if r.get("error") is not None:
        why.append(f"error {r['error']!r}")
    if r.get("stopped_at_board") is not True:
        why.append("did not stop at the full-time board")
    if r.get("strays") != []:
        why.append(f"strays {r.get('strays')!r}")
    return "; ".join(why) or None


def check(ref, cand, seeds, expect):
    """(lines, passed) for the family; raises Malformed on a missing or unexpected seed."""
    missing_ref = [s for s in seeds if s not in ref]
    missing = [s for s in seeds if s not in cand]
    unexpected = sorted(set(cand) - set(seeds))
    if missing_ref or missing or unexpected:
        raise Malformed("seed family mismatch: " + "; ".join(
            f"{what}: {', '.join(f'0x{s:04x}' for s in lst)}" for what, lst in (
                ("missing from the reference", missing_ref), ("missing from the candidate", missing),
                ("unexpected in the candidate", unexpected)) if lst))
    lines, passed = [], 0
    for seed in seeds:
        a, b = ref[seed], cand[seed]
        bad_ref = completed(a)
        if bad_ref:
            lines.append(f"seed 0x{seed:04x}: REFERENCE NOT A COMPLETED MATCH ({bad_ref}): FAIL")
            continue
        bad = completed(b)
        diff = [f for f in FIELDS if a.get(f) != b.get(f)]
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
        seeds = [int(s, 0) for s in a.seeds.split(",") if s.strip()]
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
