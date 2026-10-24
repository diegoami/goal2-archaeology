"""T74 (adapted from out/T72): the addresses whose executions the coverage run counts (L105): the 27 entries of row T74,
every branch target (the listing's loc_ labels) and every fall-through after a conditional jump inside those 27
routines, from static/goal-exe/code/seg_0791_*.asm and seg_1771_*.asm. Prints them comma-separated (family.py
--count); --entries prints the 12 entries only."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENTRIES = {'0791': ['7FCF', '92FC', '9372', 'ED8A'], '1771': ['1981', '4859', '4925', '4952', '49B8', '4B61'], '214B': ['04F8', '0566', '0723', '08DD', '0983', '0993', '09A7', '13F6', '1452', '14AC', '1507', '1560', '158E', '15B1', '1765'], '235C': ['0000', '000B']}
if "--entries" in sys.argv:
    print(",".join(f"{s}:{e}" for s, es in ENTRIES.items() for e in es))
    sys.exit(0)
out = set()
for seg, names in ENTRIES.items():
    lines = []
    for path in sorted((ROOT / "static/goal-exe/code").glob(f"seg_{seg}_*.asm")):
        lines += path.read_text().splitlines()
    entries = set(int(e, 16) for e in names)
    found = set()
    inside = False
    after_jcc = False
    for line in lines:
        m = re.match(rf"; ---- routine {seg}:([0-9A-F]{{4}})", line)
        if m:
            inside = int(m.group(1), 16) in entries
            if inside:
                found.add(int(m.group(1), 16))
                out.add((seg, int(m.group(1), 16)))
            after_jcc = False
            continue
        if line.startswith("; ----") or line.startswith("; data"):
            inside = False
            continue
        if not inside:
            continue
        m = re.match(r"loc_([0-9A-F]{4}):", line)
        if m:
            out.add((seg, int(m.group(1), 16)))
            continue
        m = re.match(r"([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s*(\S+)", line)
        if not m:
            continue
        a = int(m.group(1), 16)
        if after_jcc:
            out.add((seg, a))
        op = m.group(2)
        after_jcc = op.startswith("j") and op != "jmp"
    if found != entries:
        sys.exit(f"routines not found in the listing: {sorted(entries - found)}")
print(",".join(f"{s}:{a:04X}" for s, a in sorted(out)))
print(len(out), file=sys.stderr)
