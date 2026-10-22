"""T69: in every record, each counted address (--count, T69's 14 routines) equals its port's calls.
    python3 -B experiments/E036-match-port/out/T69/count-check-20261022.py LOG..."""
import json
import sys
for path in sys.argv[1:]:
    recs = [json.loads(l) for l in open(path) if l.strip()]
    bad = [(r["id"], a) for r in recs for a, n in r["counts"].items() if r["port_calls"].get(a) != n]
    reached = {a: sum(1 for r in recs if r["counts"][a]) for a in recs[0]["counts"]}
    print(f"{path}: {len(recs)} records, {len(recs[0]['counts'])} counted routines, "
          f"{'calls equal the counted entries in every match' if not bad else f'DIFFER: {bad[:5]}'}; matches reaching each: {reached}")
