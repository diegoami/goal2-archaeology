#!/usr/bin/env python3
"""E032: how much of the engine a seed family reaches, and what it never reaches.

    python3 -B experiments/E032-match-engine-inventory/union.py <out.md> <coverage.json> [<coverage.json> ...]

From coverage.py outputs that carry `match_blocks` (the blocks reached between kick-off and full time): per
part (analyze.py's parts), the code bytes reached by each seed and by the union, against the parts' size;
then the FRONTIER: routines that reached engine routines call (static/goal-exe/calls.tsv) but that no seed
reached, with their size and annotation name. The frontier is what a seed family from this start state does
not exercise (the rare paths a port needs other start states, or edited ones, to check). Refused if <out.md>
exists."""
import bisect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E032-match-engine-inventory"))
from analyze import incomplete, part  # noqa: E402
from coverage import routines  # noqa: E402


def main():
    out = Path(sys.argv[1])
    if out.exists():
        sys.exit(f"refused: {out} exists")
    runs = [json.loads(Path(p).read_text()) for p in sys.argv[2:]]
    if not runs:
        sys.exit("refused: no coverage runs given")
    seeds = [r["seed"] for r in runs]
    if len(set(seeds)) != len(seeds):
        sys.exit("refused: a seed appears twice")
    for p, r in zip(sys.argv[2:], runs):
        why = incomplete(r) or (None if "match_blocks" in r else "no match_blocks (a coverage run before they were kept)")
        if why:
            sys.exit(f"refused: {p} is not a completed match ({why})")
    starts, info, names = routines()

    def owner(img):
        i = bisect.bisect_right(starts, img) - 1
        return starts[i] if i >= 0 else None

    def byteset(run):
        s = set()
        for img, size in run["match_blocks"]:
            s.update(range(img, img + size))
        return s

    sets = [byteset(r) for r in runs]
    union = set().union(*sets)
    reached_routines = {owner(b) for b in union}
    rows = {}
    for r in runs:
        for row in r["routines"]:
            rows.setdefault(row["address"], row)

    def img_of(addr):
        seg, off = (int(x, 16) for x in addr.split(":"))
        return seg * 16 + off

    per_part = {}
    for img in reached_routines:
        a = info[img]["address"]
        row = rows.get(a)
        if row is None:
            continue
        p = part(row)
        d = per_part.setdefault(p, {"size": 0, "union": 0, "each": [0] * len(runs)})
        lo, hi = img, img + info[img]["size"]
        d["size"] += info[img]["size"]
        d["union"] += sum(1 for b in union if lo <= b < hi)
        for i, s in enumerate(sets):
            d["each"][i] += sum(1 for b in s if lo <= b < hi)
    lines = ["# E032 coverage of a seed family: " + ", ".join(f"0x{r['seed']:04x}" for r in runs), "",
             "Code bytes reached between kick-off and full time, per part, by each seed and by their union, "
             "against the size of the part's reached routines.", "",
             "| part | size (bytes) | each seed | union |", "| --- | --- | --- | --- |"]
    for p, d in sorted(per_part.items(), key=lambda kv: (kv[0].startswith(("UI", "LIB", "sound")), kv[0])):
        each = " / ".join(f"{100 * e / d['size']:.0f}%" for e in d["each"])
        lines.append(f"| {p} | {d['size']:,} | {each} | {100 * d['union'] / d['size']:.0f}% |")
    # the frontier: callees of reached engine routines that no seed reached
    calls = {}
    for line in (ROOT / "static/goal-exe/calls.tsv").read_text().splitlines():
        if line.startswith((";", "caller")):
            continue
        a, b, _ = line.split("\t")
        calls.setdefault(a, set()).add(b)
    frontier = {}
    for img in reached_routines:
        a = info[img]["address"]
        row = rows.get(a)
        if row is None or part(row).startswith(("UI", "LIB", "sound")):
            continue
        for callee in calls.get(a, ()):
            ci = img_of(callee)
            if ci in info and ci not in reached_routines and callee[:4] in ("0791", "1771"):
                frontier.setdefault(callee, set()).add(a)
    lines += ["", f"Frontier: {len(frontier)} routines called from reached engine routines that no seed reached "
              f"({sum(info[img_of(c)]['instructions'] for c in frontier):,} static instructions, their own code only).", "",
              "| routine | name | instructions | called from |", "| --- | --- | --- | --- |"]
    for c in sorted(frontier):
        lines.append(f"| {c} | {names.get(c, ('', ''))[0]} | {info[img_of(c)]['instructions']} | {' '.join(sorted(frontier[c]))} |")
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
