#!/usr/bin/env python3
"""Render a state's 80x25 text screen as a PNG, as the game shows it.

    python3 tools/screens/render.py <record|run id> <state> [-o out.png] [--from DIR ...]
    python3 tools/screens/render.py --savestate file.sav [-o out.png]

A record keeps only the text and a digest of the screen, not its attributes, so the picture is
made from the state's savestate (a release asset of the experiment, never committed): found by its
name under --from directories (default: .cache/evidence/<exp> from tools/verify_evidence.py and
scratch/human/sessions/*/snapshots) and checked against the sha256 in evidence/<exp>/<run>.manifest.json.

Standard library only (zlib and struct write the PNG).
- Size: 80 columns x 8 pixels by 25 rows x 16 pixels = 640x400. The 9th dot column of DOSBox-X's
  720x400 text mode is not drawn; box-drawing glyphs are 8 dots wide here.
- Colours: the 16 standard VGA text colours (the DAC's power-on palette, not read from the
  savestate). Attribute bits 0-3 are the foreground, bits 4-7 the background: blink is off, so
  bit 7 is a bright background, as the owner's DOSBox-X shows it (blink as bright background off).
- Glyphs: the font the savestate itself holds, VGA plane 2 of the Vga component: glyph c's rows
  are at stream offset FONT_BASE + 4 * (32 * c + row). That offset is measured here, not from F001
  (which calibrated only the text page): on E015-r0007 state 16 the stream holds the smiley glyph
  rows 7e 81 a5 81 81 bd 99 81 81 7e at plane-2 address 32 + 2, the text page's own base
  (F001) is plane 0 of address 0, and the rendered screens read as the game (checked by eye on
  states 16 and 76, and by tests/test_screens_render.py on a synthetic stream). If the font fails
  font_ok (a text mode that never loaded one), the pinned 8x16 font
  static/screens/font-goal-8x16.bin (the font GOAL itself loads, 4096 bytes taken from the same
  place in E015-r0007 state 16) is used instead and the run says so.
"""
import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

sys.path.insert(0, str(common.ROOT / "runtime" / "driver"))
import savestate  # noqa: E402

CELL_W, CELL_H = 8, 16
FONT_BASE = savestate.VGA_TEXT_BASE + 2     # VGA address 0 of plane 2 (F001: planes interleaved, 4 bytes per address)
GLYPH_STRIDE = 32                           # bytes of plane 2 per glyph; the first 16 are the 8x16 rows
# The pinned fallback: the 4096 bytes (256 glyphs x 16 rows) read the same way from E015-r0007 state 16
# (snap-0016-20261011T141020Z.sav, sha256 da454ee6... in evidence/E015/E015-r0007.manifest.json, DOSBox-X
# 2024.03.01 text mode with the font GOAL itself loads), committed as a derived extract.
FALLBACK_FONT = common.ROOT / "static" / "screens" / "font-goal-8x16.bin"
FALLBACK_FONT_SHA256 = "a8bad6fd78475a6bc2a05438c19207a9bb8c0f4f4099f60384e158cdc3eba580"
FALLBACK_NAME = "font-goal-8x16.bin (the font GOAL loads, read from E015-r0007 state 16)"

PALETTE = [
    (0x00, 0x00, 0x00), (0x00, 0x00, 0xAA), (0x00, 0xAA, 0x00), (0x00, 0xAA, 0xAA),
    (0xAA, 0x00, 0x00), (0xAA, 0x00, 0xAA), (0xAA, 0x55, 0x00), (0xAA, 0xAA, 0xAA),
    (0x55, 0x55, 0x55), (0x55, 0x55, 0xFF), (0x55, 0xFF, 0x55), (0x55, 0xFF, 0xFF),
    (0xFF, 0x55, 0x55), (0xFF, 0x55, 0xFF), (0xFF, 0xFF, 0x55), (0xFF, 0xFF, 0xFF),
]


def attribute_colours(attr):
    """(foreground, background) RGB of a text attribute byte; blink off, so bit 7 is intensity."""
    return PALETTE[attr & 0x0F], PALETTE[attr >> 4]


def savestate_font(vga):
    """256 glyphs of 16 row bytes from the plane-2 font in the inflated Vga stream, or None."""
    if len(vga) < FONT_BASE + 4 * (GLYPH_STRIDE * 255 + CELL_H):
        return None
    return [bytes(vga[FONT_BASE + 4 * (GLYPH_STRIDE * c + r)] for r in range(CELL_H)) for c in range(256)]


def font_ok(glyphs):
    """A loaded VGA font: space is blank, the full block (DB) is solid, and letters have ink."""
    if glyphs is None:
        return False
    return (glyphs[0x20] == bytes(CELL_H) and glyphs[0xDB] == b"\xff" * CELL_H
            and all(any(glyphs[c]) for c in b"AEgx0"))


def fallback_font():
    data = FALLBACK_FONT.read_bytes()
    if hashlib.sha256(data).hexdigest() != FALLBACK_FONT_SHA256:
        raise ValueError(f"{FALLBACK_FONT} does not match its pinned sha256")
    return [data[c * CELL_H:(c + 1) * CELL_H] for c in range(256)]


def font_for(ss):
    """(glyphs, name of the font source)."""
    glyphs = savestate_font(ss.vga)
    if font_ok(glyphs):
        return glyphs, "the savestate's VGA plane 2"
    return fallback_font(), FALLBACK_NAME


def pixels(chars, attrs, glyphs):
    """Rows of RGB bytes: 25 x 16 = 400 rows of 640 pixels."""
    rows = []
    for text_row in range(savestate.ROWS):
        cells = [(chars[text_row * savestate.COLS + c], attrs[text_row * savestate.COLS + c])
                 for c in range(savestate.COLS)]
        for y in range(CELL_H):
            row = bytearray()
            for ch, attr in cells:
                fg, bg = attribute_colours(attr)
                bits = glyphs[ch][y]
                for x in range(CELL_W):
                    row += bytes(fg if bits >> (7 - x) & 1 else bg)
            rows.append(bytes(row))
    return rows


def png(rows, width, height):
    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + r for r in rows)              # filter type 0 (none) on every row
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def render_savestate(ss):
    """(PNG bytes, font source name) for a parsed Savestate."""
    glyphs, source = font_for(ss)
    scr = ss.screen()
    return png(pixels(scr.chars, scr.attrs, glyphs), savestate.COLS * CELL_W, savestate.ROWS * CELL_H), source


def find_savestate(run_id, state, dirs):
    """The savestate of a record state: found by name, verified by the manifest's sha256."""
    rec = common.read_record(run_id)
    if state not in rec["states"]:
        raise SystemExit(f"{run_id} has no state {state}")
    name = Path(rec["states"][state]["file"]).name
    manifest = common.ROOT / "evidence" / run_id.split("-")[0] / f"{run_id}.manifest.json"
    want = {f["name"]: f["sha256"] for f in json.loads(manifest.read_text())["files"]}.get(name)
    exp = run_id.split("-")[0]
    candidates = [Path(d) / name for d in dirs]
    candidates.append(common.ROOT / ".cache" / "evidence" / exp / name)
    candidates += sorted((common.ROOT / "scratch" / "human" / "sessions").glob(f"*/snapshots/{name}"))
    for p in candidates:
        if p.is_file():
            if want and hashlib.sha256(p.read_bytes()).hexdigest() != want:
                raise SystemExit(f"{p} does not match the sha256 in {manifest.name}")
            return p
    raise SystemExit(f"{name} not found; fetch it: python3 tools/verify_evidence.py {exp}, or pass --from DIR")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("record", nargs="?")
    ap.add_argument("state", nargs="?", type=int)
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--from", dest="dirs", action="append", default=[])
    ap.add_argument("--savestate", type=Path)
    a = ap.parse_args(argv)
    if a.savestate:
        path, label = a.savestate, a.savestate.stem
    elif a.record and a.state is not None:
        run_id = Path(a.record).stem
        path, label = find_savestate(run_id, a.state, a.dirs), f"{run_id}-state{a.state:04d}"
    else:
        ap.error("a record and a state, or --savestate")
    data, source = render_savestate(savestate.Savestate(path))
    out = a.out or Path(f"{label}.png")
    out.write_bytes(data)
    print(f"wrote {out} (640x400, font: {source})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
