#!/usr/bin/env python3
"""Write mapper-nohost.map: DOSBox-X 2024.03.01's default binds (runtime/human/dosbox-x-2024.03.01-default.map)
with the savestate on Scroll Lock alone (SDL scancode 71) and the load on Print Screen alone (70), both
taken from the guest, so the driver never presses the host key F12. Under Xvfb the guest's BIOS showed
Left Alt held from the launch on (0040:0017 bit 3, 0040:0018 bit 1) and every F-key arrived as Alt+F-key
(0x69 for F2, 0x8C for F12 in the BIOS buffer): see the guide's "function keys" section."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "runtime" / "human" / "dosbox-x-2024.03.01-default.map"
CHANGES = {'hand_savestate "key 22 host" \n': 'hand_savestate "key 71" \n',
           'hand_loadstate "key 15 host" \n': 'hand_loadstate "key 70" \n',
           'key_printscreen "key 70" \n': 'key_printscreen \n',
           'key_scrolllock "key 71" \n': 'key_scrolllock \n',
           # a screenshot (PNG in <work>/cap) on Pause alone: the one way to see a screen a savestate
           # cannot be taken on (the help viewer, F1: DOSBox-X dies in the savestate, code -6)
           'hand_scrshot "key 19 host" \n': 'hand_scrshot "key 72" \n',
           'key_pause "key 72" \n': 'key_pause \n'}

text = SRC.read_text()
for old, new in CHANGES.items():
    if text.count(old) != 1:
        raise SystemExit(f"{old!r} is not in {SRC} exactly once")
    text = text.replace(old, new)
(HERE / "mapper-nohost.map").write_text(text)
print("wrote", HERE / "mapper-nohost.map")
