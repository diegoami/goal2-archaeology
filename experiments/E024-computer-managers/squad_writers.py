"""E024: candidate writers of the country record's squad words (country array at [DS:A917], 0xBF a record).

A heuristic scan of static/goal-exe/code/*.asm: every routine that loads the far pointer [0xa917]
and, within the next 14 instructions, stores a WORD through es:[di+...] (mov/xchg/`214B:007B` swap calls
are listed separately by calls.tsv). Output: routine, line of the load, line of the store. Not a proof of
absence: a store through a pointer saved earlier (a local far pointer) is missed; the routines found are
then read by hand in notes.md.
Run from the repository root: python3 -B experiments/E024-computer-managers/squad_writers.py
"""
import glob
import re

routine = None
for fn in sorted(glob.glob("static/goal-exe/code/seg_*.asm")):
    lines = open(fn).read().split("\n")
    for i, ln in enumerate(lines):
        m = re.match(r"^; ---- routine ([0-9A-F]{4}:[0-9A-F]{4})", ln)
        if m:
            routine = m.group(1)
        if "ptr [0xa917]" in ln and "les" in ln:
            for j in range(i + 1, min(i + 15, len(lines))):
                s = lines[j]
                if re.search(r"mov word ptr es:\[di", s) and re.search(r"es:\[di[^\]]*\], ", s):
                    print(f"{routine} {fn.split('/')[-1]}:{i + 1} load, store at :{j + 1}  {s.strip()[:70]}")
                    break
