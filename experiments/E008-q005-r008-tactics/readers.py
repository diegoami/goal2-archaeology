"""Static: the routines that access country +0x2D or player +0xF, and whether a match engine reaches them.

A routine is listed when its listing (`static/goal-exe/code/`) has an access `es:[di + 0x2d]` or
`add di, 0x2d` and loads the country array pointer `[0xa917]`, or an access `es:[di + 0xf]` or
`add di, 0xf` and loads the player array pointer `[0xa91b]`. That is a filter, not a proof: each
listed routine is read in the decompiled view, and F010's table says what it does. Reachability is
over the direct call edges of `static/goal-exe/calls.tsv` (indirect calls are not followed).
"""
import collections
import glob
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CODE = os.path.join(ROOT, "static", "goal-exe", "code")
CALLS = os.path.join(ROOT, "static", "goal-exe", "calls.tsv")
WATCHED = "0791:9564"  # F005
QUICK = "0791:D733"  # F005

ROUTINE = re.compile(r"; ---- routine (\w+):(\w+)")
ACCESS = {
    "+0x2D": (re.compile(r"es:\[di \+ 0x2d\]|add di, 0x2d$"), "[0xa917]"),
    "+0xF": (re.compile(r"es:\[di \+ 0xf\]|add di, 0xf$"), "[0xa91b]"),
}


def scan(code=CODE):
    """{routine: {field: [(file, line), ...]}} for accesses in routines that load the field's array."""
    hits = collections.defaultdict(lambda: collections.defaultdict(list))
    loads = collections.defaultdict(set)
    for path in sorted(glob.glob(os.path.join(code, "seg_*.asm"))):
        name = os.path.basename(path)
        cur = None
        with open(path) as f:
            for n, line in enumerate(f, 1):
                m = ROUTINE.match(line)
                if m:
                    cur = m.group(1) + ":" + m.group(2)
                    continue
                if cur is None:
                    continue
                low = line.lower().strip()
                for field, (pat, ptr) in ACCESS.items():
                    if ptr in low:
                        loads[cur].add(field)
                    if pat.search(low):
                        hits[cur][field].append((name, n))
    return {r: {k: v for k, v in fs.items() if k in loads[r]} for r, fs in hits.items()
            if any(k in loads[r] for k in fs)}


def edges(calls=CALLS):
    out = collections.defaultdict(set)
    with open(calls) as f:
        for line in f:
            if line.startswith(";") or line.startswith("caller"):
                continue
            a, b, _ = line.rstrip("\n").split("\t")
            out[a].add(b)
    return out


def reach(graph, root):
    seen, stack = {root}, [root]
    while stack:
        for y in graph[stack.pop()]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return seen


def table():
    g = edges()
    w, q = reach(g, WATCHED), reach(g, QUICK)
    rows = []
    for r, fields in sorted(scan().items()):
        where = {k: ", ".join(f"{f}:{n}" for f, n in v) for k, v in sorted(fields.items())}
        rows.append((r, r in w, r in q, where))
    return rows


if __name__ == "__main__":
    for r, inw, inq, where in table():
        print(r, "watched" if inw else "-", "quick" if inq else "-", where)
