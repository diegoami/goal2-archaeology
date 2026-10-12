"""T39a render.py: a savestate's text screen to a PNG, decoded here with the standard library.

The synthetic savestate carries the text page at the offsets F001 measured and a font at the offsets
render.py's docstring names, both written as literals here, so a renderer that reads a byte off, or
paints a bit-7 attribute as blink, fails. The committed PNGs of E015-r0007 states 16 and 76 are
decoded too, at cells whose attribute bytes were read from those savestates."""
import contextlib
import hashlib
import io
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "screens"))
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import render  # noqa: E402
import savestate  # noqa: E402

TEXT_BASE = 0x86024            # F001: text page in the inflated Vga stream, 8 bytes a cell
FONT_AT = 0x86026              # plane 2 of VGA address 0 (measured on E015-r0007 state 16)
CELL = 8
CELL_W, CELL_H = 8, 16


def decode_png(data):
    """(width, height, rows of RGB tuples) of an 8-bit truecolour, unfiltered-or-filtered PNG."""
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, ihdr = 8, b"", None
    while pos < len(data):
        n, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        assert struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])[0] == zlib.crc32(tag + body) & 0xFFFFFFFF
        if tag == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    w, h, depth, ctype = ihdr[:4]
    assert (depth, ctype) == (8, 2), "8-bit RGB expected"
    raw = zlib.decompress(idat)
    stride = 1 + 3 * w
    rows, prev = [], bytes(3 * w)
    for y in range(h):
        line = raw[y * stride:(y + 1) * stride]
        ft, cur = line[0], bytearray(line[1:])
        for i in range(len(cur)):
            a = cur[i - 3] if i >= 3 else 0
            b = prev[i]
            c = prev[i - 3] if i >= 3 else 0
            if ft == 1:
                cur[i] = (cur[i] + a) & 255
            elif ft == 2:
                cur[i] = (cur[i] + b) & 255
            elif ft == 3:
                cur[i] = (cur[i] + (a + b) // 2) & 255
            elif ft == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            else:
                assert ft == 0
        rows.append(bytes(cur))
        prev = bytes(cur)
    return w, h, [[tuple(r[3 * x:3 * x + 3]) for x in range(w)] for r in rows]


def cell_pixels(rows, text_row, col):
    return {rows[text_row * CELL_H + y][col * CELL_W + x] for y in range(CELL_H) for x in range(CELL_W)}


def synthetic(font=True, chars=None, attrs=None):
    """A savestate whose cell (r, c) is chars/attrs[r*80+c]; glyph c of the font is c's low bits
    written as a distinct stripe pattern, except 0x20 (blank) and 0xDB (solid)."""
    chars = chars or bytearray([0x20] * 2000)
    attrs = attrs or bytearray([0x07] * 2000)
    vga = bytearray(max(TEXT_BASE + CELL * 2000, FONT_AT + 4 * 32 * 256) + 64)
    for i in range(2000):
        vga[TEXT_BASE + CELL * i] = chars[i]
        vga[TEXT_BASE + CELL * i + 1] = attrs[i]
    if font:
        for c in range(256):
            for r in range(16):
                if c == 0x20:
                    row = 0x00
                elif c == 0xDB:
                    row = 0xFF
                else:
                    row = 0x80 | ((c + r) & 0x7F)       # ink at the leftmost dot, so every letter has some
                vga[FONT_AT + 4 * (32 * c + r)] = row
    mem = bytearray(savestate.MEM_BASE + 0x1000)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Vga", zlib.compress(bytes(vga)))
        z.writestr("Memory", zlib.compress(bytes(mem)))
    return savestate.Savestate(buf.getvalue())


class SyntheticRender(unittest.TestCase):
    def setUp(self):
        chars = bytearray([0x20] * 2000)
        attrs = bytearray([0x07] * 2000)
        chars[0], attrs[0] = 0xDB, 0x4E                  # solid block: foreground 0xE (yellow) on red
        attrs[1] = 0x9F                                  # blank, bit 7 set: background 9 (bright blue), no blink
        chars[80 * 24 + 79], attrs[80 * 24 + 79] = 0xDB, 0x02   # last cell: solid, foreground green
        data, self.source = render.render_savestate(synthetic(True, chars, attrs))
        self.w, self.h, self.rows = decode_png(data)

    def test_size_is_80x25_cells_of_8x16(self):
        self.assertEqual((self.w, self.h), (640, 400))

    def test_three_named_cells_have_their_attribute_colours(self):
        self.assertEqual(cell_pixels(self.rows, 0, 0), {(0xFF, 0xFF, 0x55)})       # solid, fg 0xE
        self.assertEqual(cell_pixels(self.rows, 0, 1), {(0x55, 0x55, 0xFF)})       # blank, bg 9: bit 7 is intensity
        self.assertEqual(cell_pixels(self.rows, 24, 79), {(0x00, 0xAA, 0x00)})     # last cell, fg 2
        self.assertEqual(cell_pixels(self.rows, 0, 2), {(0x00, 0x00, 0x00)})       # blank, bg 0

    def test_glyph_rows_come_from_the_savestates_font(self):
        chars = bytearray([0x20] * 2000)
        chars[5] = 0x41
        attrs = bytearray([0x1E] * 2000)                 # yellow on blue
        _, _, rows = decode_png(render.render_savestate(synthetic(True, chars, attrs))[0])
        fg, bg = (0xFF, 0xFF, 0x55), (0x00, 0x00, 0xAA)
        for y in range(16):                              # glyph 0x41: dot 0 inked, dot 1 ink iff bit 6 of (0x41+y)
            bits = 0x80 | ((0x41 + y) & 0x7F)
            expect = [fg if bits >> (7 - x) & 1 else bg for x in range(8)]
            self.assertEqual(rows[y][5 * 8:5 * 8 + 8], expect, f"row {y}")
        self.assertEqual(self.source, "the savestate's VGA plane 2")

    def test_font_missing_uses_the_pinned_fallback_and_says_so(self):
        chars = bytearray([0x20] * 2000)
        chars[0] = 0xDB
        data, source = render.render_savestate(synthetic(False, chars))
        self.assertIn("font-goal-8x16.bin", source)
        _, _, rows = decode_png(data)
        self.assertEqual(cell_pixels(rows, 0, 0), {(0xAA, 0xAA, 0xAA)})            # the pinned font's 0xDB is solid

    def test_fallback_font_is_pinned(self):
        self.assertEqual(len(render.fallback_font()), 256)
        original = render.FALLBACK_FONT_SHA256
        render.FALLBACK_FONT_SHA256 = "0" * 64
        try:
            with self.assertRaises(ValueError):
                render.fallback_font()
        finally:
            render.FALLBACK_FONT_SHA256 = original

    def test_main_writes_the_png_of_a_savestate_file(self):
        chars = bytearray([0x20] * 2000)
        chars[0] = 0xDB
        ss = synthetic(True, chars)
        with tempfile.TemporaryDirectory() as d:
            sav = Path(d) / "x.sav"
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w") as z:
                z.writestr("Vga", zlib.compress(bytes(ss.vga)))
                z.writestr("Memory", zlib.compress(bytes(ss.mem)))
            sav.write_bytes(buf.getvalue())
            out = Path(d) / "x.png"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(render.main(["--savestate", str(sav), "-o", str(out)]), 0)
            self.assertEqual(decode_png(out.read_bytes())[:2], (640, 400))


class CommittedPngs(unittest.TestCase):
    """The PNGs of E015-r0007 states 16 and 76. The attribute bytes of these cells were read from
    the savestates (the record keeps no attributes): state 16 (7,50) is a blank on attribute 0x70
    (background 7, light grey), (0,60) a blank on 0x02 (black); state 76 (1,42) a blank on 0x8A,
    whose bit 7 is bright background (dark grey 55,55,55), not blink."""

    def png(self, state):
        return decode_png((ROOT / "static" / "screens" / "png" / f"E015-r0007-state{state:04d}.png").read_bytes())

    def test_state_16(self):
        w, h, rows = self.png(16)
        self.assertEqual((w, h), (640, 400))
        self.assertEqual(cell_pixels(rows, 7, 50), {(0xAA, 0xAA, 0xAA)})
        self.assertEqual(cell_pixels(rows, 0, 60), {(0x00, 0x00, 0x00)})

    def test_state_76(self):
        w, h, rows = self.png(76)
        self.assertEqual((w, h), (640, 400))
        self.assertEqual(cell_pixels(rows, 1, 42), {(0x55, 0x55, 0x55)})



class ResolveStateFromCache(unittest.TestCase):
    """#143: a state fetched from the release is named <sha256[:16]>-<name>; no session folder exists."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name)
        self.data = b"fake savestate bytes"
        self.sha = hashlib.sha256(self.data).hexdigest()
        self.name = "snap-0016-x.sav"
        self.asset = f"{self.sha[:16]}-{self.name}"

    def test_finds_hash_prefixed_file(self):
        (self.cache / self.asset).write_bytes(self.data)
        got = render.resolve_state(self.name, self.sha, self.asset, [], self.cache)
        self.assertEqual(got, self.cache / self.asset)

    def test_refuses_wrong_bytes(self):
        (self.cache / self.asset).write_bytes(b"other bytes")
        with self.assertRaises(SystemExit):
            render.resolve_state(self.name, self.sha, self.asset, [], self.cache)


if __name__ == "__main__":
    unittest.main()
