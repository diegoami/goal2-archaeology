#!/usr/bin/env python3
"""E025 (T51): the static searches F025 cites, as one reproducible script.

    python3 -B experiments/E025-sacking-and-end/searches.py

Reads only static/goal-exe/code/*.asm and calls.tsv (no game run). Every search below is one the
finding names when it says "never"; the output lists every hit so a reviewer can check the count.
The committed output is searches.log.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "static" / "goal-exe" / "code"
files = sorted(CODE.glob("seg_*.asm"))


def lines(f):
    return f.read_text(errors="replace").splitlines()


def hits(label, pattern):
    rx = re.compile(pattern)
    n = 0
    print(f"## {label}  /{pattern}/")
    for f in files:
        for i, ln in enumerate(lines(f), 1):
            if rx.search(ln):
                print(f"{f.name}:{i}: {ln[:100].rstrip()}")
                n += 1
    print(f"-- {n} hits\n")


# 1. every write that could set the sacked flag [bp-2] of 000E:4E0E from a nested routine
hits("accesses of a parent frame's [bp-2] (ss:[di-2])", r"ss:\[di - 2\]")
# 2. every call of unmanage_country 000E:01FA (a near call, so 'call 0x1fa' inside segment 000E)
hits("near calls of 000E:01FA", r"call 0x1fa\b")
hits("far calls of 000E:01FA", r"call far 000e:01fa")
# 3. every access to the game state's year word (+0x38), displayed year (+0x3A), stage (+0x3C)
hits("accesses of [A923]+0x38 / +0x3A", r"es:\[di \+ 0x3[8a]\]")
hits("compares of [A923]+0x3C", r"cmp .*es:\[di \+ 0x3c\]")
# 4. build-constant tests: 'mov al, N' straight into 'or al, al'
print("## constant-folded boolean tests ('mov al, 0|1' followed by 'or al, al')")
n = 0
for f in files:
    ls = lines(f)
    for i in range(len(ls) - 1):
        if re.search(r"mov al, [01]$", ls[i]) and "or al, al" in ls[i + 1]:
            print(f"{f.name}:{i + 1}: {ls[i][:60].rstrip()} / {ls[i + 1][:40].strip()}")
            n += 1
print(f"-- {n} hits\n")
# 5. callers of the Halt routine 23E4:00D8 (calls.tsv)
print("## callers of 23E4:00D8 (Halt) in calls.tsv")
n = 0
for ln in (ROOT / "static/goal-exe/calls.tsv").read_text().splitlines():
    p = ln.split("\t")
    if len(p) >= 2 and p[1] == "23E4:00D8":
        print(ln)
        n += 1
print(f"-- {n} hits\n")
# 6. every displacement 0xBE (the country byte 0B77 tests)
hits("references of an 0xBE displacement", r"\+ 0xbe\]")
# 7. callers of country_list_screen 1771:26B9, with the instructions just before
print("## calls of 1771:26B9 with the 4 instructions before")
for f in files:
    ls = lines(f)
    for i, ln in enumerate(ls):
        if re.search(r"call far 1771:26B9|call 0x26b9\b", ln):
            ctx = " | ".join(x[20:60].strip() for x in ls[max(0, i - 4):i + 1])
            print(f"{f.name}:{i + 1}: {ctx}")
print()
