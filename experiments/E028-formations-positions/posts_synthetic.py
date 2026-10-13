"""Beyond block 10: compare the Python port of 0791:419C with the original on synthetic elevens (sorted ascending, as 230C leaves
them): every code repeated 2, 3, 4 and 5 times, and 3000 random elevens (seeded). Includes the |x| > 4 separation branch
(codes 3, 4, 7, 8, 10, 11 twice in a row), which no block-10 eleven reaches.
usage: python3 -B posts_synthetic.py <GOAL.EXE> OUTDIR   -> OUTDIR/posts-synthetic-<UTC>.log"""
import os, random, sys
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from foot_truth import load, Guest
from posts import emulate, port
from ds import load_full
psha, usha, image = load(sys.argv[1])
g = Guest(image); ds = load_full()
cases, bad, branch_hi = [], 0, 0
rnd = random.Random(54)
for code in range(14):
    for k in (2, 3, 4, 5):
        rest = [rnd.randrange(14) for _ in range(11 - k)]
        cases.append(sorted([code] * k + rest))
for _ in range(3000):
    cases.append(sorted(rnd.randrange(14) for _ in range(11)))
for poss in cases:
    a, b = emulate(g, poss, poss)
    p = port(poss, ds)
    if a != p or b != p:
        bad += 1
    if any(poss[i] == poss[i - 1] and poss[i] in (3, 4, 7, 8, 10, 11) for i in range(1, 11)):
        branch_hi += 1
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
os.makedirs(sys.argv[2], exist_ok=True)
msg = "packed GOAL.EXE %s\nelevens %d, port differs from the original 419C: %d, elevens reaching the |x|>4 branch: %d\n" % (psha, len(cases), bad, branch_hi)
open(os.path.join(sys.argv[2], "posts-synthetic-%s.log" % ts), "x").write(msg)
print(msg)
