import importlib.util
import os
import struct
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "static"))

HAVE_CAPSTONE = importlib.util.find_spec("capstone") is not None
if HAVE_CAPSTONE:
    import goalexe  # noqa: E402
    import listing  # noqa: E402


def tiny_exe(relocs=True):
    """An MZ file of one 0x60-byte image: segment 0 calls far into segment 2 and loads segment 4.
    seg 0 (0x00): call far 0002:0000 ; mov dx, 0004 ; mov ds, dx ; jmp $ (end)
    seg 2 (0x20): push bp ; mov bp, sp ; mov ax, [0x0010] ; pop bp ; retf
    seg 4 (0x40): data"""
    img = bytearray(0x60)
    img[0:5] = bytes([0x9A, 0x00, 0x00, 0x02, 0x00])
    img[5:8] = bytes([0xBA, 0x04, 0x00])
    img[8:10] = bytes([0x8E, 0xDA])
    img[10:12] = bytes([0xEB, 0xFE])
    img[0x20:0x20 + 9] = bytes([0x55, 0x89, 0xE5, 0xA1, 0x10, 0x00, 0x5D, 0xCB, 0x90])
    img[0x40:0x44] = b"data"
    rel = [(0, 3), (0, 6)] if relocs else []
    hdr = bytearray(0x200)
    struct.pack_into("<14H", hdr, 0, 0x5A4D, (0x200 + 0x60) % 512, 2, len(rel), 0x20, 0, 0xFFFF, 0, 0x100, 0, 0, 0, 0x1C, 0)
    for k, (seg, off) in enumerate(rel):
        struct.pack_into("<HH", hdr, 0x1C + 4 * k, off, seg)
    return bytes(hdr + img)


@unittest.skipUnless(HAVE_CAPSTONE, "capstone is not installed (pip install -r tools/static/requirements.txt in a venv)")
class ListingTests(unittest.TestCase):
    def test_segments_entry_and_far_target(self):
        im = goalexe.Image(tiny_exe())
        self.assertEqual(im.far_segments, [0, 2])
        self.assertEqual(im.ds, 4)
        dis = goalexe.Disassembly(im)
        self.assertIn(0x20, dis.starts)          # the far-call target is a routine start
        self.assertIn("far", dis.starts[0x20])
        self.assertIn(0x20, dis.ins)             # and its code was decoded

    def test_relocated_words_are_named_in_the_listing(self):
        im = goalexe.Image(tiny_exe())
        dis = goalexe.Disassembly(im)
        self.assertIn("call far 0002:0000", listing.fmt_ins(im, 0, dis.ins[0], 0))
        self.assertIn("relocated segment word 0004", listing.fmt_ins(im, 5, dis.ins[5], 0))

    def test_without_the_relocation_table_the_far_call_is_not_followed(self):
        im = goalexe.Image(tiny_exe(relocs=False))
        dis = goalexe.Disassembly(im)
        self.assertNotIn("far", dis.starts.get(0x20, set()))   # only the prologue scan finds it
        self.assertIn("prologue", dis.starts.get(0x20, set()))

    def test_rendering_marks_data_and_routines(self):
        im = goalexe.Image(tiny_exe())
        dis = goalexe.Disassembly(im)
        text = "\n".join(listing.render_segment(im, dis, 2, 4))
        self.assertIn("; ---- routine 0002:0000  (found by: far)", text)
        self.assertIn("push bp", text)
        self.assertIn("retf", text)


if __name__ == "__main__":
    unittest.main()
