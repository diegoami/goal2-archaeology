#!/usr/bin/env python3
"""T61: a table of reach-blocks.jsonl (family.py --count of the block starts of the 22 routines, out/T61/blocks.py): per
block start, the matches that reach it and its executions per match, and the blocks no match of ALL reaches.

    python3 -B experiments/E036-match-port/out/T61/blocksum.py experiments/E036-match-port/out/T61/reach-blocks.jsonl"""
import collections
import json
import sys

rows = [json.loads(line) for line in open(sys.argv[1])]
fam = collections.Counter(r["family"] for r in rows)
addrs = sorted({a for r in rows for a in r["counts"]})
print(f"{len(rows)} matches: {dict(fam)}")
print("address        matches  min  max   total")
not_reached = []
for a in addrs:
    per = [r["counts"].get(a, 0) for r in rows]
    reached = sum(1 for c in per if c)
    if not reached:
        not_reached.append(a)
    else:
        print(f"{a}  {reached:>7} {min(per):>5} {max(per):>6} {sum(per):>9}")
print("not reached by any match:", " ".join(not_reached) if not_reached else "none")
