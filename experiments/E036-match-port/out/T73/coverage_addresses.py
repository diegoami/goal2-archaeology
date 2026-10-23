"""T73 (adapted from out/T68): the addresses whose executions the coverage run counts (L105): the 88 entries of row T73,
every branch target (the listing's loc_ labels) and every fall-through after a conditional jump inside those 88
routines, from static/goal-exe/code/seg_0791_*.asm and seg_1771_*.asm. Prints them comma-separated (family.py
--count); --entries prints the 88 entries only."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ENTRIES = {'0791': ['0000', '006C', '0106', '0425', '0441', '0481', '04C9', '054C', '05C6', '0691', '0712', '0C65', '15B9', '1829', '8F10', '9079', '94C9', '94E8', 'A699', 'A75D', 'C50C'], '1771': ['0947', '0AF8', '0F58', '0FB1', '11E1', '1289', '13D0', '1527', '157D', '2EE5', '2F37', '3827', '3947', '3AE2', '3B3F', '3BD3', '42BC', '4D8A', '4E22', '50F1', '5AC4', '5C94', '5CCB', '76FA', '77C3', '883F', '8939', '89C1', '89FE', '8A5D', '8A87', '8CA2', '8CCF', '8D84', '8E9A', '9028', '91CE', '937C', '9509', '958D'], '214B': ['00DB', '00FF', '0123', '01A3', '0205', '026D', '02C8', '0350', '0625', '0643', '0661', '0755', '13C5', '1E09', '1E5A', '1E75', '1E8D', '1EA1', '1EBC', '1EF1', '1F87'], '2382': ['0099', '00E7', '016D', '0215', '04FC', '0608']}
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
