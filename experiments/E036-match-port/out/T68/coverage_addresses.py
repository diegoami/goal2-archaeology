"""T68: the addresses whose executions the coverage run counts (L105): the 20 entries of row T68, every branch target
(the listing's loc_ labels) and every fall-through after a conditional jump inside those 20 routines, from
static/goal-exe/code/seg_0791_*.asm (7CC5-7FCE, 8062-835E, A260-A374, A920-AC66, BBFF-BC5C, BD03-BEC6, BF6B-C019,
C173-C24C, C5DC-CAAF; the routines between them that are not row T68's are left out). Prints them comma-separated
(family.py --count); --entries prints the 20 entries only."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENTRIES = ["7CC5", "7D56", "7E60", "7EEF", "8062", "8206", "82EB", "A260", "A2E6", "A920", "A9B8", "AAE8", "BBFF",
           "BD03", "BD83", "BF6B", "C173", "C5DC", "C7EB", "C88D"]
if "--entries" in sys.argv:
    print(",".join(f"0791:{e}" for e in ENTRIES))
    sys.exit(0)
lines = []
for path in sorted((ROOT / "static/goal-exe/code").glob("seg_0791_*.asm")):
    lines += path.read_text().splitlines()
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
