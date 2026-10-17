import json
from collections import defaultdict
rows = [r for r in json.load(open("notes/T297/before-20261017-jobs.json")) if r["created"] >= "2026-10-12" and r["event"] == "pull_request" and r["job"] == "checks" and r["conclusion"] != "skipped"]
b = defaultdict(list)
for r in rows:
    b[r["branch"]].append(r)
first = later = canc = 0
fb = lb = cb = 0
for br, rs in b.items():
    rs.sort(key=lambda r: r["created"])
    seen = False
    for r in rs:
        m = -(-int(r["secs"]) // 60)
        if r["conclusion"] == "cancelled":
            canc += 1; cb += m
        elif not seen:
            first += 1; fb += m; seen = True
        else:
            later += 1; lb += m
print("branches", len(b), "first completed", first, fb, "later completed (rework)", later, lb, "cancelled", canc, cb)
