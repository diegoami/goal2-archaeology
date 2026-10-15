#!/usr/bin/env python3
"""T39c: read an 80x25 text screen back from a video frame (or a crop of one), standard library only.

    python3 tools/screens/video.py crop.png --cols 20 --rows 3 [--scale 2]

A frame is rows of RGB bytes (ffmpeg `-f rawvideo -pix_fmt rgb24`, or a PNG). The text grid is
CELL_W x CELL_H font pixels per cell (T39a's render.py), each font pixel `scale` frame pixels square, from
the offset (x0, y0). Each cell is read by sampling the centre of each of its 8x16 font pixels and mapping
each sample to the nearest of the 16 VGA colours (render.PALETTE), so video compression noise within half
a colour step is tolerated; then:
- one colour in the cell: a blank cell of that background (a solid cell of foreground c, the full block,
  looks the same: both are one appearance, and the comparison is by appearance);
- two or more: the two most frequent colours are fg and bg in either order; the glyph is the font glyph whose
  bitmap equals the ink pattern exactly, else the nearest by the number of differing font pixels (`dist`).
A cell's identity for comparison is its *appearance* (the colour of each of its 128 font pixels), because
chars 0x00, 0x20 and 0xFF are all blank and a blank cell's foreground cannot be seen.
Nothing here chooses a frame: the caller picks it by the snapshot's request window (check.py).
"""
import struct
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import render  # noqa: E402

CELL_W, CELL_H = render.CELL_W, render.CELL_H
PALETTE = render.PALETTE
_NEAREST = {}


def nearest_colour(rgb):
    """Index (0-15) of the VGA colour nearest to an (r, g, b) triple, memoised."""
    hit = _NEAREST.get(rgb)
    if hit is None:
        r, g, b = rgb
        hit = min(range(16), key=lambda i: (PALETTE[i][0] - r) ** 2 + (PALETTE[i][1] - g) ** 2
                  + (PALETTE[i][2] - b) ** 2)
        _NEAREST[rgb] = hit
    return hit


def read_png(data):
    """(width, height, rgb bytes) of an 8-bit RGB PNG with any filter type."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, idat, ihdr = 8, b"", None
    while pos < len(data):
        n, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if tag == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", body)
        elif tag == b"IDAT":
            idat += body
        pos += 12 + n
    w, h, depth, ctype = ihdr[:4]
    if (depth, ctype) != (8, 2):
        raise ValueError("8-bit RGB PNG expected")
    raw, stride = zlib.decompress(idat), 3 * w
    out, prev = bytearray(), bytearray(stride)
    for y in range(h):
        line = raw[y * (stride + 1):(y + 1) * (stride + 1)]
        ft, cur = line[0], bytearray(line[1:])
        for i in range(stride):
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
            elif ft != 0:
                raise ValueError(f"PNG filter type {ft}")
        out += cur
        prev = cur
    return w, h, bytes(out)


def sample_grid(rgb, width, cols, rows, scale=1, x0=0, y0=0):
    """The frame's colour index at the centre of each font pixel: rows*CELL_H lists of cols*CELL_W."""
    half, out = scale // 2, []
    for fy in range(rows * CELL_H):
        base = ((y0 + fy * scale + half) * width + x0 + half) * 3
        need = cols * CELL_W * scale * 3
        line = rgb[base:base + need] if base >= 0 else b""
        line = line + bytes(need - len(line))       # beyond the frame edge reads as black (a wrong offset)
        out.append([nearest_colour((line[i], line[i + 1], line[i + 2]))
                    for i in range(0, cols * CELL_W * 3 * scale, 3 * scale)])
    return out


def glyph_bitmaps(glyphs):
    """{16 row bytes: first char code with that bitmap} and the list of distinct bitmaps."""
    first = {}
    for code, g in enumerate(glyphs):
        first.setdefault(bytes(g), code)
    return first


def _bits(rows):
    return [(row >> (7 - x)) & 1 for row in rows for x in range(CELL_W)]


def cell_appearance(char, attr, glyphs):
    """128 colour indices of a cell as the game draws it (render.pixels' rule)."""
    fg, bg = attr & 0x0F, attr >> 4
    return tuple(fg if b else bg for b in _bits(glyphs[char]))


def _dist(p, q):
    """Sum of absolute RGB differences between two palette indices."""
    return sum(abs(x - y) for x, y in zip(PALETTE[p], PALETTE[q]))


def decode_cell(pix, glyphs, first):
    """(char, attr, dist) for one cell's 128 colour indices; dist counts font pixels that differ from
    the chosen glyph (0 = exact match)."""
    counts = {}
    for c in pix:
        counts[c] = counts.get(c, 0) + 1
    order = sorted(counts, key=lambda c: (-counts[c], c))
    if len(order) == 1:
        return 0x20, order[0] << 4, 0
    a, b = order[0], order[1]
    best = None
    for fg, bg in ((b, a), (a, b)):
        ink = [1 if _dist(p, fg) <= _dist(p, bg) else 0 for p in pix]
        key = bytes(int("".join(map(str, ink[r * 8:r * 8 + 8])), 2) for r in range(CELL_H))
        if key in first:
            cand = (0, first[key], fg | bg << 4)
        else:
            cand = None
            for code, g in enumerate(glyphs):
                d = sum(x != y for x, y in zip(ink, _bits(g)))
                if cand is None or d < cand[0]:
                    cand = (d, code, fg | bg << 4)
        if best is None or cand[0] < best[0]:
            best = cand
    return best[1], best[2], best[0]


def decode_frame(rgb, width, glyphs, cols=80, rows=25, scale=1, x0=0, y0=0):
    """(chars, attrs, dists): bytes, bytes and a list, cols*rows long, read from RGB bytes."""
    grid, first = sample_grid(rgb, width, cols, rows, scale, x0, y0), glyph_bitmaps(glyphs)
    chars, attrs, dists = bytearray(), bytearray(), []
    for cy in range(rows):
        for cx in range(cols):
            pix = [grid[cy * CELL_H + py][cx * CELL_W + px] for py in range(CELL_H) for px in range(CELL_W)]
            ch, at, d = decode_cell(pix, glyphs, first)
            chars.append(ch)
            attrs.append(at)
            dists.append(d)
    return bytes(chars), bytes(attrs), dists


def find_grid(rgb, width, height, glyphs, scale, rows_sample=3, cols_sample=None):
    """(x0, y0, score) of the offset of the text grid at `scale`, or None when the frame holds no ink.
    The score is the number of cells, over`rows_sample` evenly spaced text rows and the first `cols_sample` columns, that match a glyph exactly. Offsets searched: 0..8*scale-1 by 0..16*scale-1."""
    if not any(rgb[i] > 64 for i in range(0, len(rgb), 3 * 7)):
        return None
    first = glyph_bitmaps(glyphs)
    cols, rows = width // (CELL_W * scale) - 1, height // (CELL_H * scale) - 1
    cols = min(cols, cols_sample or cols)
    best = None
    for y0 in range(CELL_H * scale):
        for x0 in range(CELL_W * scale):
            hit = 0
            for r in range(0, rows, max(1, rows // rows_sample)):
                g = sample_grid(rgb, width, cols, 1, scale, x0, y0 + r * CELL_H * scale)
                for cx in range(cols):
                    pix = [g[py][cx * CELL_W + px] for py in range(CELL_H) for px in range(CELL_W)]
                    if len(set(pix)) > 1 and decode_cell(pix, glyphs, first)[2] == 0:
                        hit += 1
            if best is None or hit > best[2]:
                best = (x0, y0, hit)
    return best


def png_rows(width, height, colour_rows):
    """RGB rows for render.png from rows of colour indices."""
    return [b"".join(bytes(PALETTE[c]) for c in row) for row in colour_rows]


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("png", type=Path)
    ap.add_argument("--cols", type=int, default=80)
    ap.add_argument("--rows", type=int, default=25)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--x0", type=int, default=0)
    ap.add_argument("--y0", type=int, default=0)
    a = ap.parse_args(argv)
    w, h, rgb = read_png(a.png.read_bytes())
    glyphs = render.fallback_font()
    chars, attrs, dists = decode_frame(rgb, w, glyphs, a.cols, a.rows, a.scale, a.x0, a.y0)
    for r in range(a.rows):
        print(bytes(chars[r * a.cols:(r + 1) * a.cols]).decode("cp437").replace("\x00", " ").rstrip())
    print(f"cells with dist>0: {sum(1 for d in dists if d)}/{len(dists)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
