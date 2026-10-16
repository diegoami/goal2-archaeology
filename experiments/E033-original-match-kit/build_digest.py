#!/usr/bin/env python3
"""E033: runtime/original_match's REGISTERED_BUILD, computed from the listing of the registered GOAL.EXE
(static/goal-exe/code: the unpacked executable of set goal2-a949da2f) at the kit's BUILD_SITES. The same digest
comes from every image at hand (E006-r0001, E006-r0005, E011-r0001 watchstart and half time, E010-r0001 half
time), so the sites hold no relocated byte for load segment 0x823.

    python3 -B experiments/E033-original-match-kit/build_digest.py"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match.image import BUILD_SITES  # noqa: E402

CODE = ROOT / "static" / "goal-exe" / "code"
listing = {}
for path in sorted(CODE.glob("seg_*.asm")):
    seg = path.name.split("_")[1]
    for line in path.read_text().splitlines():
        m = re.match(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)", line)
        if m:
            off = int(m.group(1), 16)
            for i, b in enumerate(m.group(2).split()):
                listing[(seg, off + i)] = int(b, 16)
h = hashlib.sha256()
for address, n in BUILD_SITES:
    seg, off = address.split(":")
    h.update(bytes(listing[(seg, int(off, 16) + i)] for i in range(n)))
print(h.hexdigest())
