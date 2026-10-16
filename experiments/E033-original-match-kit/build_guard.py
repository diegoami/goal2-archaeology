#!/usr/bin/env python3
"""E033 (PR 251 review R1): generate runtime/original_match/build.py, the build guard's data, from the registered
GOAL.EXE, and check it against the listing, the data extract and every image at hand.

    python3 -B experiments/E033-original-match-kit/build_guard.py --exe GOAL.EXE --reads out/ds-reads-<stamp>.json \
        --log out/build-guard-<stamp>.json

The registered GOAL.EXE (set goal2-a949da2f, packed sha256 a6928b0b..., the release goal2-original asset) is unpacked
with tools/static/unlzexe.py (sha256 6fd8c5ef..., the file static/goal-exe/README.md says the listing was made from).
What the guard covers:
- code: every byte of the load module's code, image 00000..2580F (153,616 bytes, every routine of every segment), the
  1,916 relocated words compared with the load segment taken off (the loader's fixups);
- data: the initialised data (DS:0000..7B6F) that the measured matches read and never wrote (ds_reads.py), compared
  with the executable's initial bytes.
Digests are per block (code 0x1000 bytes, data 0x400 bytes of DS), so a refusal names where the image differs. The
generated module holds positions and digests only, no byte of the original."""
import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "static"))
sys.path.insert(0, str(ROOT / "runtime"))
import unlzexe  # noqa: E402

PACKED_SHA = "a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664"
UNPACKED_SHA = "6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188"
CODE_SIZE, CODE_BLOCK = 0x25810, 0x1000          # static/goal-exe/README.md: code 0000..2580F, data segment 2581
DS_IMAGE, DS_INIT, DATA_BLOCK = 0x25810, 0x7B70, 0x400   # the initialised data: image 25810..2D37F
SEGMENTS = (0x0000, 0x000E, 0x0791, 0x16D6, 0x1771, 0x2138, 0x2139, 0x214B, 0x235C, 0x2382, 0x23E4)   # README table
OUT = ROOT / "runtime" / "original_match" / "build.py"


def listing_bytes():
    """Image offset -> byte, from the listing's instruction and `db` lines (pstr lines are left out)."""
    out = {}
    for p in sorted((ROOT / "static/goal-exe/code").glob("seg_*.asm")):
        seg = int(p.name.split("_")[1], 16)
        for line in p.read_text().splitlines():
            m = re.match(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)", line) or re.match(
                r"^([0-9A-F]{4})\s+db ((?:[0-9A-F]{2} ?)+)", line)
            if m:
                a = seg * 16 + int(m.group(1), 16)
                for i, b in enumerate(m.group(2).split()):
                    out[a + i] = int(b, 16)
    return out


def data_extract():
    """DS offset -> byte, from static/goal-exe/data/ds_2581_*.hex (32 a row, '*' repeats the row above)."""
    out, last, last_off = {}, None, None
    for p in sorted((ROOT / "static/goal-exe/data").glob("ds_2581_*.hex")):
        for line in p.read_text().splitlines():
            if line.startswith(";"):
                continue
            if line.strip() == "*":
                last_off = "repeat"
                continue
            m = re.match(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)", line)
            if not m:
                continue
            off = int(m.group(1), 16)
            row = [int(b, 16) for b in m.group(2).split()]
            if last_off == "repeat" and last is not None:
                fill = last[1] + len(last[0])
                while fill < off:
                    for i, b in enumerate(last[0]):
                        out[fill + i] = b
                    fill += len(last[0])
            for i, b in enumerate(row):
                out[off + i] = b
            last, last_off = (row, off), off
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", required=True)
    ap.add_argument("--reads", required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    packed = Path(a.exe).read_bytes()
    if hashlib.sha256(packed).hexdigest() != PACKED_SHA:
        sys.exit("GOAL.EXE is not the registered build's (packed sha256)")
    exe = unlzexe.unpack(packed)
    if hashlib.sha256(exe).hexdigest() != UNPACKED_SHA:
        sys.exit("the unpacked GOAL.EXE is not the one the listing was made from")
    w = struct.unpack("<14H", exe[:0x1C])
    module = exe[w[4] * 16:]
    relocs = sorted(seg * 16 + off for off, seg in (struct.unpack_from("<HH", exe, w[12] + 4 * i) for i in range(w[3])))
    assert len(relocs) == 1916 and max(relocs) + 2 <= CODE_SIZE, "relocations outside the code"
    code = module[:CODE_SIZE]
    # cross-checks: the listing's instruction and db bytes, the data extract's initialised data
    lst = listing_bytes()
    listing_diff = [o for o, b in lst.items() if o < CODE_SIZE and code[o] != b]
    ext = data_extract()
    data_init = module[DS_IMAGE:DS_IMAGE + DS_INIT]
    extract_diff = [o for o, b in ext.items() if o < DS_INIT and data_init[o] != b]
    reads = json.loads(Path(a.reads).read_text())
    # a byte the matches only read but that the game changed before them (start-up, menus) is a variable too:
    # left out when any image at hand differs there from the executable (first found: DS:7968, which 1771:06FE
    # sets to 4 and 1771:07A0 counts up; read by the sound routine 214B:1EF1)
    sys.path.insert(0, str(ROOT / "runtime"))
    from original_match.image import Image as _Image
    covered = sorted(o for s, n in reads["ranges"] for o in range(s, s + n))
    changed = set()
    for p in sorted((ROOT / ".cache/dl").iterdir()):
        img = _Image.from_savestate(p.read_bytes())
        ds = img.DS * 16
        changed |= {o for o in covered if img.memory[ds + o] != data_init[o]}
    kept = [o for o in covered if o not in changed]
    ranges, start, prev = [], None, None          # runs, split at DATA_BLOCK boundaries
    for o in kept + [None]:
        if o is not None and start is not None and o == prev + 1 and o % DATA_BLOCK:
            prev = o
            continue
        if start is not None:
            ranges.append((start, prev - start + 1))
        start = prev = o
    code_sha = [hashlib.sha256(code[i:i + CODE_BLOCK]).hexdigest() for i in range(0, CODE_SIZE, CODE_BLOCK)]
    blocks = {}
    for start, n in ranges:
        blocks.setdefault(start // DATA_BLOCK, bytearray()).extend(data_init[start:start + n])
    data_sha = {b: hashlib.sha256(bytes(v)).hexdigest() for b, v in sorted(blocks.items())}
    deltas = [relocs[0]] + [b - a for a, b in zip(relocs, relocs[1:])]
    text = f'''"""The build guard's data (generated by experiments/E033-original-match-kit/build_guard.py; not edited by hand).

From the registered GOAL.EXE (set goal2-a949da2f; packed sha256 {PACKED_SHA[:16]}..., unpacked
{UNPACKED_SHA[:16]}..., the file the listing static/goal-exe/ was made from): the digests of its code, image
00000..{CODE_SIZE - 1:05X} in blocks of 0x{CODE_BLOCK:X} bytes, with its {len(relocs)} relocated words as the file holds them
(the image has the load segment added: Image.build_problems takes it off), and of the initialised data a match
reads and never writes ({sum(n for _, n in ranges)} bytes of DS:0000..{DS_INIT - 1:04X} in {len(ranges)} ranges, measured by
ds_reads.py), in blocks of 0x{DATA_BLOCK:X} bytes of DS. Positions and digests only: no byte of the original."""
CODE_SIZE, CODE_BLOCK, DATA_BLOCK = 0x{CODE_SIZE:X}, 0x{CODE_BLOCK:X}, 0x{DATA_BLOCK:X}
SEGMENTS = ({", ".join(f"0x{s:04X}" for s in SEGMENTS)})   # the code segments' paragraphs, for naming a block
RELOCATION_DELTAS = "{",".join(f"{d:x}" for d in deltas)}"
CODE_SHA256 = {tuple(code_sha)!r}
DATA_RANGES = {tuple(ranges)!r}
DATA_SHA256 = {data_sha!r}
'''
    OUT.write_text(text)
    # every image at hand must pass; a changed byte of each kind must not
    import importlib
    import original_match.build as build
    importlib.reload(build)
    import original_match.image as image
    importlib.reload(image)
    images = {}
    for p in sorted((ROOT / ".cache/dl").iterdir()):
        img = image.Image.from_savestate(p.read_bytes())
        images[p.name] = image.build_problems(img.memory, img.load)
    rec = {"exe_packed_sha256": PACKED_SHA, "exe_unpacked_sha256": UNPACKED_SHA, "relocations": len(relocs),
           "code_bytes": CODE_SIZE, "code_blocks": len(code_sha),
           "listing_bytes_compared": sum(1 for o in lst if o < CODE_SIZE), "listing_differences": len(listing_diff),
           "extract_bytes_compared": sum(1 for o in ext if o < DS_INIT), "extract_differences": len(extract_diff),
           "data_bytes": sum(n for _, n in ranges), "data_ranges": len(ranges), "data_blocks": len(data_sha),
           "data_left_out_as_changed_in_an_image": [f"DS:{o:04X}" for o in sorted(changed)],
           "reads_record": str(Path(a.reads).relative_to(ROOT)) if Path(a.reads).is_absolute() else a.reads,
           "images": images, "generated": str(OUT.relative_to(ROOT)),
           "generated_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}
    with open(log, "x") as f:
        json.dump(rec, f, indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != "images"}, indent=1))
    print("images:", {k: (v or "pass") for k, v in images.items()})


if __name__ == "__main__":
    main()
