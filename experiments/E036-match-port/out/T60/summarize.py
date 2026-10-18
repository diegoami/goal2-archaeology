#!/usr/bin/env python3
"""T60: the per-match counts of a family run (family.py --count, or --ports with its port_calls) as a table: for each
address the matches that reach it, the least and most executions in a match, and the total.

    python3 -B experiments/E036-match-port/out/T60/summarize.py LOG.jsonl [--ports]      # --ports: port_calls, not counts
"""
import json
import sys


def main():
    path = sys.argv[1]
    key = "port_calls" if "--ports" in sys.argv else "counts"
    recs = [json.loads(line) for line in open(path)]
    addresses = []
    for r in recs:
        for a in r.get(key, {}):
            if a not in addresses:
                addresses.append(a)
    print(f"{path}: {len(recs)} matches ({', '.join(sorted({r['id'].split('/')[0] for r in recs}))}); key {key}")
    print("address    matches  min/match  max/match  total  | by family: F40 O8 S (matches reaching it)")
    for a in addresses:
        per = [r[key].get(a, 0) for r in recs]
        reach = [p for p in per if p]
        fam = {}
        for r in recs:
            f = r["id"].split("/")[0]
            fam.setdefault(f, [0, 0])
            fam[f][1] += 1
            fam[f][0] += 1 if r[key].get(a, 0) else 0
        print(f"{a}  {len(reach):>3}/{len(recs)}  {min(reach) if reach else 0:>9}  {max(per):>9}  {sum(per):>10}  | "
              + " ".join(f"{f} {c}/{n}" for f, (c, n) in sorted(fam.items())))


if __name__ == "__main__":
    main()
