"""List the routines that read a player's position bytes (+6 played, +7 club) in the named view and in the listing.
Writes readers-named.tsv (typed `.position` / `.club_position` in static/goal-exe/named/*.c) and
readers-asm.tsv (the listing: `les di, ptr [0xa91b]` (the players array) with an `es:[di + 6|7]` read within 8
instructions, before the next `les`). Both are counts of syntactic sites, not a proof of semantics.
usage: python3 -B readers.py OUTDIR"""
import re, sys, os, glob
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "goal-exe")
out = sys.argv[1]
os.makedirs(out, exist_ok=True)
names = {}
for line in open(os.path.join(ROOT, "annotations", "routines.tsv")):
    p = line.rstrip("\n").split("\t")
    if len(p) > 1 and re.match(r"[0-9A-F]{4}:[0-9A-F]{4}$", p[0]):
        names[p[0]] = p[1]
rows = []
for f in sorted(glob.glob(os.path.join(ROOT, "named", "seg_*.c"))):
    cur = None
    for n, line in enumerate(open(f), 1):
        m = re.match(r"// ---- ([0-9A-F]{4}:[0-9A-F]{4})\s+(\S+)", line)
        if m:
            cur = (m.group(1), m.group(2)); continue
        if line.startswith("//"):
            continue
        for fld in ("club_position", "position"):
            if re.search(r"\b%s\b" % fld, line):
                rows.append((cur[0] if cur else "?", cur[1] if cur else "?", fld, os.path.basename(f), n, line.strip()[:110]))
                break
with open(os.path.join(out, "readers-named.tsv"), "w") as o:
    o.write("routine\tname\tfield\tfile\tline\ttext\n")
    for r in rows:
        o.write("\t".join(map(str, r)) + "\n")
asm = []
for f in sorted(glob.glob(os.path.join(ROOT, "code", "seg_*.asm"))):
    cur = None
    lines = open(f).read().split("\n")
    for i, line in enumerate(lines):
        m = re.match(r"; ---- routine ([0-9A-F]{4}:[0-9A-F]{4})", line)
        if m:
            cur = m.group(1); continue
        if "ptr [0xa91b]" in line and "les di" in line:
            for j in range(i + 1, min(i + 9, len(lines))):
                if "les di" in lines[j] or "call" in lines[j] and j > i + 3:
                    break
                mm = re.search(r"es:\[di \+ ([67])\]", lines[j])
                if mm and "mov" in lines[j] or mm and "cmp" in lines[j]:
                    asm.append((cur, names.get(cur, ""), "+" + mm.group(1), os.path.basename(f), j + 1, lines[j].strip()[:100]))
                    break
with open(os.path.join(out, "readers-asm.tsv"), "w") as o:
    o.write("routine\tname\tfield\tfile\tline\ttext\n")
    for r in asm:
        o.write("\t".join(map(str, r)) + "\n")
print("named rows", len(rows), "asm rows", len(asm))
