"""T68 (copied from out/T67): per-address totals and the number of ALL matches reaching each counted address, from the unported coverage
log (coverage-unported-<run id>/coverage-unported.jsonl), with the listing's instruction count per unreached block (L105)."""
import json, sys
from pathlib import Path
log = Path(sys.argv[1])
recs = [json.loads(l) for l in log.read_text().splitlines() if l.strip()]
fam = {}
addrs = list(recs[0]["counts"])
for a in addrs:
    tot = sum(r["counts"][a] for r in recs)
    n = sum(1 for r in recs if r["counts"][a])
    per = {}
    for r in recs:
        f = r["id"].split("/")[0]
        per[f] = per.get(f, 0) + (1 if r["counts"][a] else 0)
    print(f"{a}\t{tot}\t{n}/{len(recs)}\t" + " ".join(f"{k}={v}" for k, v in sorted(per.items())))
