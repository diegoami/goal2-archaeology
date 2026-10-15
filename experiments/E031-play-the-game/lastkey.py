#!/usr/bin/env python3
"""Print the game's last key code (DS:A976, DS:A977: `214B:08DD` stores the code it read there, extended
keys as scan + 0x64) and the BIOS keyboard buffer (0040:001A head, 0040:001C tail, 0040:001E..003D) of a
savestate: what reached the game. Usage: lastkey.py <file.sav>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "runtime" / "driver"))
import savestate  # noqa: E402

s = savestate.Savestate(Path(sys.argv[1]).read_bytes())
a976, a977 = s.ds_bytes(0xA976, 2)
bda = s.memory(0x41A, 0x24)
head, tail = int.from_bytes(bda[0:2], "little"), int.from_bytes(bda[2:4], "little")
print(f"DS:A976={a976:02x} DS:A977={a977:02x} head={head:04x} tail={tail:04x} buffer={bda[4:].hex(' ')}")
f1, f2 = s.memory(0x417, 2)
f3 = s.memory(0x496, 1)[0]
# 0040:0017 bit 0 right shift, 1 left shift, 2 ctrl, 3 alt; 0040:0018 bit 0 left ctrl, 1 left alt; 0040:0096 bit 2 right ctrl, 3 right alt
print(f"shift flags 0417={f1:08b} 0418={f2:08b} 0496={f3:08b}")
