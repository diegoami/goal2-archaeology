"""E024: remap `named/seg_SSSS_NN.c:LINE` citations after the named view was regenerated.

    python3 -B experiments/E024-computer-managers/remap_named_citations.py [--apply] [--base REF] FILE...

Regenerating static/goal-exe/named/ with new annotation rows moves routines between the numbered parts of a
segment (seg_0791_08.c ... seg_0791_11.c) and shifts lines inside them. This script maps every citation of the
form `named/seg_SSSS_NN.c:LINE` (also `static/goal-exe/named/...`) in the FILEs from the view at REF (default
origin/main) to the working tree's view: the lines of a segment's parts are concatenated in part order, matched
with difflib (whole lines, no junk heuristic), and a cited line is mapped to the line that is equal to it in
the new view; a cited line the regeneration changed (an annotated routine's comment, a retyped expression) is
mapped to the nearest preceding matched line and reported as `approx`. Without --apply it only prints
`file:line  old -> new  (exact|approx)`; with --apply it rewrites the FILEs in place.
Only the parts that differ between REF and the working tree are remapped; a citation of an unchanged part is
left alone.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMED = ROOT / "static/goal-exe/named"
CITE = re.compile(r"(named/seg_([0-9A-F]{4})_([0-9]{2})\.c):([0-9]+)")


def parts(seg, ref):
    """[(part file name, lines)] of segment seg at ref ('' = the working tree), in part order."""
    names = sorted(p.name for p in NAMED.glob(f"seg_{seg}_*.c"))
    if ref:
        out = subprocess.run(["git", "ls-tree", "--name-only", ref, "static/goal-exe/named/"],
                             capture_output=True, text=True, cwd=ROOT).stdout.split()
        names = sorted(Path(n).name for n in out if Path(n).name.startswith(f"seg_{seg}_") and n.endswith(".c"))
    res = []
    for n in names:
        if ref:
            text = subprocess.run(["git", "show", f"{ref}:static/goal-exe/named/{n}"], capture_output=True,
                                  text=True, cwd=ROOT).stdout
        else:
            text = (NAMED / n).read_text()
        res.append((n, text.split("\n")))
    return res


def build(seg, ref):
    flat, where = [], []
    for n, lines in parts(seg, ref):
        for i, ln in enumerate(lines, 1):
            flat.append(ln)
            where.append((n, i))
    return flat, where


def mapping(seg, base):
    old, owhere = build(seg, base)
    new, nwhere = build(seg, "")
    sm = difflib.SequenceMatcher(None, old, new, autojunk=False)
    m = {}
    last = 0
    for tag, a1, a2, b1, b2 in sm.get_opcodes():
        for k in range(a1, a2):
            if tag == "equal":
                m[owhere[k]] = (nwhere[b1 + (k - a1)], True)
                last = b1 + (k - a1)
            else:
                m[owhere[k]] = (nwhere[min(b1, len(new) - 1)] if b1 < len(new) else nwhere[last], False)
    return m


def main(argv):
    apply = "--apply" in argv
    base = "origin/main"
    if "--base" in argv:
        base = argv[argv.index("--base") + 1]
    files = [a for a in argv if not a.startswith("--") and a != base]
    maps = {}
    for f in files:
        p = Path(f)
        text = p.read_text()

        def repl(m):
            seg, part = m.group(2), m.group(3)
            if seg not in maps:
                maps[seg] = mapping(seg, base)
            key = (f"seg_{seg}_{part}.c", int(m.group(4)))
            if key not in maps[seg]:
                return m.group(0)
            (nf, nl), exact = maps[seg][key]
            if (nf, nl) == key:
                return m.group(0)
            new = f"named/{nf}:{nl}"
            line = text.count("\n", 0, m.start()) + 1
            print(f"{f}:{line}  {m.group(0)} -> {new}  ({'exact' if exact else 'approx'})")
            return new
        out = CITE.sub(repl, text)
        if apply and out != text:
            p.write_text(out)


if __name__ == "__main__":
    main(sys.argv[1:])
