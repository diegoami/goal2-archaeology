"""The basic blocks of row T62's routines, from the listing (static/goal-exe/code/seg_0791_14.asm, seg_0791_15.asm):
every label and every instruction after a conditional jump, per routine. Prints the addresses as family.py --count
takes them (L105: the reach of each branch counted on the unhooked kit). No byte of the original is printed.

    python3 -B experiments/E036-match-port/out/T62/blocks.py [--list]"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ROUTINES = ("835F", "83A2", "8537", "869F", "8AE9", "8C67", "8CCA", "8CF5", "8E24", "90C5", "9119")
FILES = ("static/goal-exe/code/seg_0791_14.asm", "static/goal-exe/code/seg_0791_15.asm")
INSN = re.compile(r"^([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s*(\S+)")
CONDITIONAL = re.compile(r"^j(?!mp)")


def blocks():
    out = {}
    for f in FILES:
        routine, after_jcc = None, False
        for line in (ROOT / f).read_text().splitlines():
            m = re.match(r"; ---- routine 0791:([0-9A-F]{4})", line)
            if m:
                routine = m.group(1) if m.group(1) in ROUTINES else None
                after_jcc = False
                if routine:
                    out[routine] = [routine]
                continue
            if routine is None:
                continue
            lab = re.match(r"^loc_([0-9A-F]{4}):", line)
            if lab:
                if lab.group(1) not in out[routine]:
                    out[routine].append(lab.group(1))
                continue
            m = INSN.match(line)
            if not m:
                continue
            addr, op = m.groups()
            if after_jcc and addr not in out[routine]:
                out[routine].append(addr)
            after_jcc = bool(CONDITIONAL.match(op))
    return out


if __name__ == "__main__":
    b = blocks()
    if "--list" in sys.argv:
        for r in ROUTINES:
            print(r, " ".join(sorted(b[r])))
    else:
        print(",".join(f"0791:{a}" for r in ROUTINES for a in sorted(b[r])))
