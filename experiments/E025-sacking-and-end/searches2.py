#!/usr/bin/env python3
"""E025 (T51 round 2): the broadened inventory of the state fields, any instruction form.

    python3 -B experiments/E025-sacking-and-end/searches2.py > searches2.log

searches.py (round 1, log kept unchanged) accepted only `cmp` for the stage byte and only the
`es:[di + d]` form. This one lists, for the year word +0x38, the displayed year +0x3A and the stage
byte +0x3C of the state block [DS:A923], EVERY instruction of the listing that carries the
displacement 0x38, 0x3A or 0x3C with any base register, or loads it as an immediate added to a
pointer (`add reg, 0x3X`). Hits on other records (country, player, fixture) share the displacement
and are in the list: each hit is classified by hand in notes.md, section "Inventory".
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "static" / "goal-exe" / "code"
rx = re.compile(r"\+ 0x3[8ac]\]|(?:add|lea|mov) [a-z]+, (?:\[[a-z]+ \+ )?0x3[8ac]\]?$")
for f in sorted(CODE.glob("seg_*.asm")):
    for i, ln in enumerate(f.read_text(errors="replace").splitlines(), 1):
        if rx.search(ln.split(";")[0].rstrip()):
            print(f"{f.name}:{i}: {ln[:100].rstrip()}")
print("-- listed above: every instruction with displacement 0x38/0x3a/0x3c or an add of those immediates")
