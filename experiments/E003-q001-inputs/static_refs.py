#!/usr/bin/env python3
"""E003's static search (T08): every reference to the Dos unit's clock routines in segment 235C,
including indirect ones, in the unpacked GOAL.EXE (never committed; make it with
`python3 tools/static/unlzexe.py .cache/goal2/GOAL.EXE <out.exe>`, sha256 6fd8c5ef...).

    python3 experiments/E003-q001-inputs/static_refs.py <unpacked GOAL.EXE>

A far pointer or far call to 235C:xxxx in the load module carries a relocation entry for its segment
word (the segment is relocated at load time), so listing every relocated word equal to 235C, with
the word before it (the offset) and the byte before that (9A for `call far`), finds every direct
far call, stored far pointer and `mov reg, seg 235C`. It also lists every `B4 2C` (mov ah, 2Ch)
in the image. Prints raw findings only."""
import hashlib
import struct
import sys

UNPACKED_SHA256 = "6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188"  # static/goal-exe/README.md
DOS_SEG = 0x235C
CLOCK = {0x006C: "GetDate (INT 21h AH=2Ah)", 0x008E: "SetDate (AH=2Bh)", 0x00A2: "GetTime (AH=2Ch)",
         0x00C7: "SetTime (AH=2Dh)"}


def main(path):
    d = open(path, "rb").read()
    if hashlib.sha256(d).hexdigest() != UNPACKED_SHA256:
        raise SystemExit(f"{path} is not the unpacked GOAL.EXE of static/goal-exe/README.md")
    # MZ header: word 6 = relocation count, word 8 = header paragraphs, word 0x18 = relocation table offset
    nrel = struct.unpack_from("<H", d, 6)[0]
    hpar = struct.unpack_from("<H", d, 8)[0]
    relofs = struct.unpack_from("<H", d, 0x18)[0]
    img = d[hpar * 16:]
    rels = {s * 16 + o for o, s in (struct.unpack_from("<HH", d, relofs + 4 * i) for i in range(nrel))}
    print(f"{nrel} relocations; load module {len(img)} bytes")
    refs = [(r - 2, struct.unpack_from("<H", img, r - 2)[0], img[r - 3]) for r in sorted(rels)
            if struct.unpack_from("<H", img, r)[0] == DOS_SEG]
    print(f"relocated words equal to {DOS_SEG:04X}: {len(refs)}")
    for at, off, before in refs:
        print(f"  image {at:05X}: {DOS_SEG:04X}:{off:04X}  byte before {before:02X}{' (call far)' if before == 0x9A else ''}")
    for off, name in CLOCK.items():
        n = sum(1 for _, o, _ in refs if o == off)
        print(f"{DOS_SEG:04X}:{off:04X} {name}: {n} reference(s)")
    i = img.find(b"\xb4\x2c")
    while i >= 0:
        print(f"B4 2C (mov ah, 2Ch) at image {i:05X}: {img[i:i + 6].hex(' ')}")
        i = img.find(b"\xb4\x2c", i + 1)


if __name__ == "__main__":
    main(sys.argv[1])
