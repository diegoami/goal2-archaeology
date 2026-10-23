"""T68 milestone (copied from out/T67): per routine of row T68, whether the port's calls equal the counted entries in every match of a log, the
matches reaching it and its calls per match (min, median, max); writes a calls-per-match TSV next to the summary."""
import json, statistics, sys
recs = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
tsv = sys.argv[2]
addrs = sorted(a for a in recs[0]["port_calls"] if a in recs[0]["counts"])   # row T68
ok = True
with open(tsv, "w") as f:
    f.write("match\t" + "\t".join(addrs) + "\n")
    for r in recs:
        f.write(r["id"] + "\t" + "\t".join(str(r["port_calls"][a]) for a in addrs) + "\n")
for a in addrs:
    calls = [r["port_calls"][a] for r in recs]
    equal = all(r["port_calls"][a] == r["counts"][a] for r in recs)
    ok &= equal
    print(f"{a}: calls == entries in every match: {equal}; reached in {sum(1 for c in calls if c)}/{len(recs)}; "
          f"per match min {min(calls)} median {statistics.median(calls)} max {max(calls)}")
print("ALL EQUAL" if ok else "MISMATCH")
sys.exit(0 if ok else 1)
