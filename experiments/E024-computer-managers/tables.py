"""E024: print the data-image tables the computer lineup routines read.

Reads static/goal-exe/data/ds_2581_*.hex (derived extract of the unpacked data segment);
prints DS:099A (8 bytes per role: n, candidates), DS:08D5 (14 x 14, a9b8's score) and the
Pascal sets at DS:693A / 695A / 697A (32 bytes each, element k at bit k % 8 of byte k // 8).
The sets inside code segments (CS:AD0F, AD2F, AD4F, AD6F; 1771:3139, 3159) are read by hand
from the listing in notes.md.
Run from the repository root: python3 -B experiments/E024-computer-managers/tables.py
"""
import glob
import re

mem = {}
for fn in sorted(glob.glob("static/goal-exe/data/ds_2581_*.hex")):
    for ln in open(fn):
        m = re.match(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)", ln)
        if m:
            a = int(m.group(1), 16)
            for i, b in enumerate(m.group(2).split()):
                mem[a + i] = int(b, 16)


def at(a):
    return mem[a]


def setelems(base, nbytes=32):
    return [8 * i + b for i in range(nbytes) for b in range(8) if at(base + i) >> b & 1]


print("DS:099A formation table (role: n candidates)")
for r in range(14):
    row = [at(0x99A + 8 * r + i) for i in range(8)]
    print(f"  role {r:2d}: n={row[0]} cand={row[1:1 + row[0]]} raw={row}")
print("DS:08D5 a9b8 score table [14*pos+role] (rows pos, cols role)")
for p in range(14):
    print(f"  pos {p:2d}:", [at(0x8D5 + 14 * p + r) for r in range(14)])
for name, base in (("693A", 0x693A), ("695A", 0x695A), ("697A", 0x697A)):
    print(f"set DS:{name}:", setelems(base))
print("DS:08CE:", [at(0x8CE + i) for i in range(8)])
