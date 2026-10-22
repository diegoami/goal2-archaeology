"""T66: the addresses whose executions the coverage run counts (L105): the 14 entries of row T66, every branch target
(the listing's loc_ labels) and every fall-through after a conditional jump, from 5B36 to 68E9 in
static/goal-exe/code/seg_0791_10.asm and seg_0791_11.asm. Prints them comma-separated (family.py --count)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENTRIES = ["5B36", "5E41", "5EAB", "5F06", "5F8A", "6188", "61EC", "6240", "6337", "6443", "65A4", "65FE", "6755",
           "67B6"]
LO, HI = 0x5B36, 0x68EA
lines = []
for part in ("10", "11"):
    lines += (ROOT / f"static/goal-exe/code/seg_0791_{part}.asm").read_text().splitlines()
out = set(int(e, 16) for e in ENTRIES)
after_jcc = False
for line in lines:
    m = re.match(r"loc_([0-9A-F]{4}):", line)
    if m and LO <= int(m.group(1), 16) < HI:
        out.add(int(m.group(1), 16))
        continue
    m = re.match(r"([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s*(\S+)", line)
    if not m:
        continue
    a = int(m.group(1), 16)
    if not LO <= a < HI:
        after_jcc = False
        continue
    if after_jcc:
        out.add(a)
    op = m.group(2)
    after_jcc = op.startswith("j") and op != "jmp"
print(",".join(f"0791:{a:04X}" for a in sorted(out)))
print(len(out), file=sys.stderr)
