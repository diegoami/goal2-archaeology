"""E024: remap `named/seg_SSSS_NN.c:LINE` citations after the named view was regenerated.

    python3 -B experiments/E024-computer-managers/remap_named_citations.py [--apply] [--base REF] FILE...

Regenerating static/goal-exe/named/ with new annotation rows moves routines between the numbered parts of a
segment (seg_0791_08.c ... seg_0791_11.c) and shifts lines inside them. This script maps every citation of the
form `named/seg_SSSS_NN.c:ITEMS` (also `static/goal-exe/named/...`), ITEMS being a comma list of lines `N` or
ranges `N-M`, in the FILEs from the view at REF (default origin/main) to the working tree's view: the lines of a
segment's parts are concatenated in part order, matched with difflib (whole lines, no junk heuristic), and a
cited line is mapped to the line that is equal to it in the new view; a cited line the regeneration changed (an
annotated routine's comment, a retyped expression) is mapped to the nearest preceding matched line and
reported as `approx`. Every changed item is printed as

    file:line  old -> new  (exact|approx; same code text: yes|NO) | the old line's text

where `same code text` compares the text of the old line at REF with the text of the new line it maps to.
`--all` ignores FILEs and reads every tracked .md of spec/ docs/ findings/ experiments/ README.md CLAUDE.md as it is
AT REF (so a file already remapped in the working tree is verified against its old numbers); it never writes.
Without --apply it only prints; with --apply it rewrites the FILEs in place. A citation of an unchanged
location is left alone. A range whose ends land in different parts is written `named/seg_A.c:N-last` is NOT
attempted: it is rewritten as two items `named/seg_A.c:N, named/seg_B.c:M` and flagged `split`.
"""
import difflib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAMED = ROOT / "static/goal-exe/named"
CITE = re.compile(r"named/seg_([0-9A-F]{4})_([0-9]{2})\.c:([0-9]+(?:[-–][0-9]+)?(?:,[0-9]+(?:[-–][0-9]+)?)*)")


def parts(seg, ref):
    """[(part file name, lines)] of segment seg at ref ('' = the working tree), in part order."""
    if ref:
        out = subprocess.run(["git", "ls-tree", "--name-only", ref, "static/goal-exe/named/"],
                             capture_output=True, text=True, cwd=ROOT).stdout.split()
        names = sorted(Path(n).name for n in out if Path(n).name.startswith(f"seg_{seg}_") and n.endswith(".c"))
    else:
        names = sorted(p.name for p in NAMED.glob(f"seg_{seg}_*.c"))
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
    text = ({w: t for w, t in zip(owhere, old)}, {w: t for w, t in zip(nwhere, new)})
    return m, text


def main(argv):
    apply = "--apply" in argv
    base = "origin/main"
    if "--base" in argv:
        base = argv[argv.index("--base") + 1]
    files = [a for a in argv if not a.startswith("--") and a != base]
    from_base = "--all" in argv        # --all: every tracked .md under spec/ docs/ findings/ experiments/, read AT REF
    if from_base:
        listing = subprocess.run(["git", "ls-tree", "-r", "--name-only", base, "spec", "docs", "findings", "experiments",
                                  "README.md", "CLAUDE.md"], capture_output=True, text=True, cwd=ROOT).stdout.split()
        files = [x for x in listing if x.endswith(".md")]
    maps = {}
    for f in files:
        p = Path(f)
        text = (subprocess.run(["git", "show", f"{base}:{f}"], capture_output=True, text=True, cwd=ROOT).stdout
                if from_base else p.read_text())

        def one(seg, part, n, line):
            if seg not in maps:
                maps[seg] = mapping(seg, base)
            mp, (otext, ntext) = maps[seg]
            key = (f"seg_{seg}_{part}.c", n)
            if key not in mp:
                return key, key, True, True
            new, exact = mp[key]
            same = otext.get(key, "") == ntext.get(new, None)
            if new != key:
                print(f"{f}:{line}  named/{key[0]}:{n} -> named/{new[0]}:{new[1]}  "
                      f"({'exact' if exact else 'approx'}; same code text: {'yes' if same else 'NO'}) | "
                      f"{otext.get(key, '').strip()[:60]}")
            return key, new, exact, same

        def repl(m):
            seg, part, items = m.group(1), m.group(2), m.group(3)
            line = text.count("\n", 0, m.start()) + 1
            outs, cur = [], None
            changed = False
            for item in items.split(","):
                ends = re.split("[-–]", item)
                mapped = []
                for e in ends:
                    key, new, exact, same = one(seg, part, int(e), line)
                    mapped.append(new)
                    changed |= new != key
                if len(mapped) == 2 and mapped[0][0] != mapped[1][0]:
                    print(f"{f}:{line}  range {item} split across {mapped[0][0]} and {mapped[1][0]} (split)")
                    outs += [mapped[0], mapped[1]]
                elif len(mapped) == 2:
                    outs.append((mapped[0][0], f"{mapped[0][1]}-{mapped[1][1]}"))
                else:
                    outs.append((mapped[0][0], str(mapped[0][1])))
            if not changed:
                return m.group(0)
            s, cur = "", None
            for fn_, ln_ in outs:
                if fn_ != cur:
                    s += ("" if not s else ", ") + f"named/{fn_}:{ln_}"
                    cur = fn_
                else:
                    s += f",{ln_}"
            return s
        out = CITE.sub(repl, text)
        if apply and not from_base and out != text:
            p.write_text(out)


if __name__ == "__main__":
    main(sys.argv[1:])
