#!/usr/bin/env python3
"""T61: the reach of each falsifier's branch in the matches it is run on (the counts of reach-blocks.jsonl, L105: counted
before the falsifier is run).

    python3 -B experiments/E036-match-port/out/T61/falsifier_reach.py experiments/E036-match-port/out/T61/reach-blocks.jsonl O8"""
import json
import sys

BRANCHES = {
    "skill-divisor-31 (3A06: the divisor 0x20, 3A71)": ["1771:3A06"],
    "foot-sets-swapped (3179: the set tests 31B6 and 31D0)": ["1771:31AE", "1771:31C8"],
    "tactic-element-2-for-1 (3431: element 1 of the in-set path, 3483)": ["1771:3471"],
    "unavailable-bit-6 (3216: the element 6 test, 3251)": ["1771:3251"],
    "mark-hi-excl (3E2F: the upper bound, 3E6E)": ["1771:3E60", "1771:3E73"],
}
rows = [json.loads(line) for line in open(sys.argv[1])]
rows = [r for r in rows if r["family"] == sys.argv[2]]
print(f"family {sys.argv[2]}: {len(rows)} matches")
for name, addrs in BRANCHES.items():
    for a in addrs:
        per = [r["counts"].get(a, 0) for r in rows]
        print(f"{name}  {a}: reached in {sum(1 for c in per if c)} of {len(per)} matches, {min(per)}-{max(per)} times a match")
