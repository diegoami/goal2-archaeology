import re
import sys
OUT = "/home/diego/projects/goal2-archaeology/.claude/worktrees/agent-ad646f98deb54a897/experiments/E021-m0-whole-match/out/"
KEYS = ("calls per routine", "hooked calls", "uncompared-register", "match:", "branches", "wrapper tallies", "expected counts", "reads ")


def lines(name):
    out = []
    for line in open(OUT + name):
        if any(k in line for k in KEYS):
            out.append(line.strip())
    return out


ok = True
for old, new in (("t46-m1-377e-regression.log", "t48-regression-m1-377e.log"), ("t46-m2-287c.log", "t48-regression-m2-287c.log"),
                 ("t47-m2-draws-run2.log", "t48-regression-m2-draws.log")):
    a, b = lines(old), lines(new)
    same = a == b
    ok &= same
    print(f"{old} vs {new}: {len(a)} / {len(b)} comparable lines (calls per routine, hooked calls, uncompared registers, branch tallies, reads, match): {'IDENTICAL' if same else 'DIFFERENT'}")
    if not same:
        for x, y in zip(a, b):
            if x != y:
                print("  old:", x[:300])
                print("  new:", y[:300])
sys.exit(0 if ok else 1)
