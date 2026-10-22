"""T67: the addresses whose executions the coverage run counts (L105): the 25 entries of row T67, every branch target
(the listing's loc_ labels) and every fall-through after a conditional jump inside those 25 routines, from
static/goal-exe/code/seg_0791_11.asm (690C-6D4B), seg_0791_12.asm (6D4E-787E) and seg_0791_13.asm (7881-7B21); the
routines between them that are not row T67's (6E11 T59's, 6ECF, 72F2, 73BA) are left out. Prints them comma-separated
(family.py --count)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENTRIES = ["690C", "698E", "69BD", "6AAD", "6AF7", "6B65", "6BF1", "6D4E", "6DEA", "6E6E", "6F01", "6F3E", "6FB6",
           "6FEE", "7069", "70F6", "715A", "717F", "71E8", "7287", "74C2", "7621", "7881", "798D", "7A43"]
lines = []
for part in ("11", "12", "13"):
    lines += (ROOT / f"static/goal-exe/code/seg_0791_{part}.asm").read_text().splitlines()
entries = set(int(e, 16) for e in ENTRIES)
out = set(entries)
inside = False
after_jcc = False
for line in lines:
    m = re.match(r"; ---- routine 0791:([0-9A-F]{4})", line)
    if m:
        inside = int(m.group(1), 16) in entries
        after_jcc = False
        continue
    if line.startswith("; ----") or line.startswith("; data"):
        inside = False
        continue
    if not inside:
        continue
    m = re.match(r"loc_([0-9A-F]{4}):", line)
    if m:
        out.add(int(m.group(1), 16))
        continue
    m = re.match(r"([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s*(\S+)", line)
    if not m:
        continue
    a = int(m.group(1), 16)
    if after_jcc:
        out.add(a)
    op = m.group(2)
    after_jcc = op.startswith("j") and op != "jmp"
print(",".join(f"0791:{a:04X}" for a in sorted(out)))
print(len(out), file=sys.stderr)
