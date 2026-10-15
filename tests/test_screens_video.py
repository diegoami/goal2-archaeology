"""T39c tools/screens/video.py: the decoder reads text and colours back from pixels.

Three committed crops (experiments/E022-video-screens/crops, made by make_crops.py) are 25x3 cells at 2x with
+-12 noise per channel. They are synthetic stand-ins for video frames, because the sitting's video holds
no game pixels (E022 notes.md). The expected text and foreground attributes are literals read from the
snapshots the crops were cut from (sitting 20261011-161003, snapshots 101 and 150)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "screens"))

import render  # noqa: E402
import video  # noqa: E402

CROPS = ROOT / "experiments" / "E022-video-screens" / "crops"
EXPECT = {
    "crop-a.png": ([" (c) NE'93│ │        tact",
                    " ┌─┐┌─┐┌─┐│ │ ┌───┐│ subs",
                    " │ ││ ││ ││ │ │   ││┌─┐┬ "], {(0, 10): 0x3, (1, 1): 0x3, (1, 4): 0x3}),
    "crop-b.png": (["┌name──────────┬age┬caps┬",
                    "│L D Agostini  │ 25│   0│",
                    "├position──────┴───┼club┴"], {(0, 1): 0x4, (1, 1): 0xC, (1, 5): 0xC}),
    "crop-c.png": (["│P Signori     │ 33│   0│",
                    "├position──────┴───┼club┴",
                    "│striker           │strik"], {(0, 1): 0xE, (1, 1): 0x4, (1, 9): 0x7}),
}


def lines(chars, cols):
    text = [" " if c in (0, 0x20, 0xFF) else bytes([c]).decode("cp437") for c in chars]
    return ["".join(text[r:r + cols]) for r in range(0, len(text), cols)]


class DecodeCropTests(unittest.TestCase):
    def decode(self, name, **kw):
        w, h, rgb = video.read_png((CROPS / name).read_bytes())
        self.assertEqual((w, h), (400, 96))
        return video.decode_frame(rgb, w, render.fallback_font(), 25, 3, 2, **kw)

    def test_text_and_foreground_are_read_exactly(self):
        for name, (text, fg) in EXPECT.items():
            with self.subTest(crop=name):
                chars, attrs, dists = self.decode(name)
                self.assertEqual(lines(chars, 25), text)
                self.assertEqual(max(dists), 0)
                for (row, col), want in fg.items():
                    self.assertEqual(attrs[row * 25 + col] & 0x0F, want, (row, col))

    def test_a_wrong_grid_offset_is_not_read_as_exact(self):
        chars, attrs, dists = self.decode("crop-b.png", x0=1)
        self.assertNotEqual(lines(chars, 25), EXPECT["crop-b.png"][0])

    def test_find_grid_locates_the_offset(self):
        w, h, rgb = video.read_png((CROPS / "crop-b.png").read_bytes())
        pad = 3
        shifted = bytearray(bytes(3 * (w + pad) * (h + pad)))
        for y in range(h):
            o = ((y + pad) * (w + pad) + pad) * 3
            shifted[o:o + 3 * w] = rgb[y * w * 3:(y + 1) * w * 3]
        x0, y0, score = video.find_grid(bytes(shifted), w + pad, h + pad, render.fallback_font(), 2, rows_sample=1, cols_sample=6)
        # sampling at x0 + scale//2 reads the same font pixel from x0 = pad - 1 and x0 = pad
        self.assertIn(x0, (pad - 1, pad))
        self.assertIn(y0, (pad - 1, pad))
        chars, attrs, dists = video.decode_frame(bytes(shifted), w + pad, render.fallback_font(), 25, 3, 2, x0, y0)
        self.assertEqual(lines(chars, 25), EXPECT["crop-b.png"][0])

    def test_a_cell_whose_ink_is_the_majority_colour_keeps_fg_and_bg(self):
        glyphs = render.fallback_font()
        first = video.glyph_bitmaps(glyphs)
        dense = [c for c in range(256) if sum(bin(b).count("1") for b in glyphs[c]) > 64 and glyphs[c] != b"\xff" * 16]
        self.assertTrue(dense)
        for code in dense:
            pix = video.cell_appearance(code, 0x1E, glyphs)        # yellow on blue
            ch, at, dist = video.decode_cell(pix, glyphs, first)
            # a glyph and its inverse with swapped colours (0x07 and 0x08) look the same: appearance decides
            self.assertEqual((video.cell_appearance(ch, at, glyphs), dist), (pix, 0), code)

    def test_a_black_frame_has_no_grid_and_decodes_to_blank(self):
        rgb = bytes(3 * 400 * 96)
        self.assertIsNone(video.find_grid(rgb, 400, 96, render.fallback_font(), 2))
        chars, attrs, dists = video.decode_frame(rgb, 400, render.fallback_font(), 25, 3, 2)
        self.assertEqual(set(chars), {0x20})
        self.assertEqual(set(attrs), {0})


if __name__ == "__main__":
    unittest.main()
