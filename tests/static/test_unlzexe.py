import hashlib
import os
import struct
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "static"))
sys.path.insert(0, HERE)

import lzexe_fixture as fx  # noqa: E402
import unlzexe  # noqa: E402


def make_image():
    """A 'program' with literals, short and long back-references and a long run."""
    parts = [bytes(range(1, 40)), b"ABCABCABC", b"\x00" * 300, bytes(range(1, 40)),
             b"hello, relocation" * 20, bytes(range(200, 256)) * 5]
    # spread of values so that matches at distances above 256 occur
    filler = bytes((i * 37 + (i >> 3)) & 0xFF for i in range(1500))
    img = b"".join(parts) + filler + parts[0] + parts[4]
    return img + b"\x00" * (-len(img) % 16)


def parse_mz(out):
    """The fields of the unpacked file: header words, relocations, image."""
    w = struct.unpack("<14H", out[:0x1C])
    n, hdr = w[3], w[4] * 16
    relocs = [struct.unpack("<HH", out[w[12] + 4 * i:w[12] + 4 * i + 4]) for i in range(n)]
    return w, [(seg, off) for off, seg in relocs], out[hdr:]


def check_relocations(test, out, expected):
    _, relocs, _ = parse_mz(out)
    test.assertEqual(relocs, expected)


class UnlzexeTests(unittest.TestCase):
    def test_round_trip(self):
        img = make_image()
        packed = fx.build_lzexe(img)
        self.assertLess(len(packed), len(img))  # the fixture really compresses
        w, _, got = parse_mz(unlzexe.unpack(packed))
        self.assertEqual(got, img)
        self.assertEqual(w[0], 0x5A4D)
        # file size fields agree with the length
        out = unlzexe.unpack(packed)
        self.assertEqual((w[2] - 1) * 512 + w[1], len(out))

    def test_the_fixture_uses_every_token_form(self):
        """Otherwise a decoder that mishandles a form would still pass the round trip."""
        stats = {}
        fx.compress(make_image(), segment_changes=(10,), stats=stats)
        for form in ("literal", "short", "long", "extended", "far", "segment_change"):
            self.assertGreater(stats.get(form, 0), 0, form)

    def test_entry_point_and_stack_come_from_the_stub(self):
        out = unlzexe.unpack(fx.build_lzexe(make_image(), ip0=0x0123, cs0=0x0456,
                                            sp0=0x0789, ss0=0x0ABC))
        w, _, _ = parse_mz(out)
        self.assertEqual((w[10], w[11], w[8], w[7]), (0x0123, 0x0456, 0x0789, 0x0ABC))

    def test_minalloc_is_packed_minalloc_less_growth(self):
        w, _, _ = parse_mz(unlzexe.unpack(fx.build_lzexe(make_image(), minalloc=0x100, growth=7)))
        self.assertEqual(w[5], 0x100 - 7)

    def test_segment_change_marker_is_a_noop(self):
        img = make_image()
        packed = fx.build_lzexe(img, segment_changes=(10, 700, 701))
        self.assertEqual(parse_mz(unlzexe.unpack(packed))[2], img)

    def test_relocation_table_is_decoded_exactly(self):
        img = make_image()
        # spans: 3, 5 (bytes), 300 (word), 255, 256, 0x10000+ (needs the 0,0,0 step), a far one
        lin = [3, 8, 308, 563, 819, 819 + 0x10005, 819 + 0x10005 + 0xFFF0 * 2 + 30]
        expected = [(a >> 4, a & 15) for a in lin]
        out = unlzexe.unpack(fx.build_lzexe(img, relocs=expected))
        check_relocations(self, out, expected)
        w, _, _ = parse_mz(out)
        self.assertEqual(w[3], len(expected))

    def test_relocated_words_follow_the_load_segment(self):
        """What a loader does with the table: add the load segment to each target word."""
        img = bytearray(make_image())
        targets = [3, 8, 100, 600]
        for t in targets:
            struct.pack_into("<H", img, t, 0x0040 + t)  # unrelocated segment values
        relocs = [(t >> 4, t & 15) for t in targets]
        out = unlzexe.unpack(fx.build_lzexe(bytes(img), relocs=relocs))
        _, table, image = parse_mz(out)
        loaded = bytearray(image)
        load_seg = 0x1000
        for seg, off in table:
            a = seg * 16 + off
            v = struct.unpack_from("<H", loaded, a)[0]
            struct.pack_into("<H", loaded, a, (v + load_seg) & 0xFFFF)
        for t in targets:
            self.assertEqual(struct.unpack_from("<H", loaded, t)[0], 0x0040 + t + load_seg)

    def test_a_test_that_ignores_the_relocation_table_fails(self):
        """If the unpacker dropped the table, check_relocations (used above) must fail."""
        expected = [(0, 3), (0, 8), (19, 4)]
        packed = fx.build_lzexe(make_image(), relocs=expected)
        check_relocations(self, unlzexe.unpack(packed), expected)  # passes with the table
        with mock.patch.object(unlzexe, "read_relocations", return_value=[]):
            dropped = unlzexe.unpack(packed)
        with self.assertRaises(AssertionError):
            check_relocations(self, dropped, expected)
        self.assertNotEqual(dropped, unlzexe.unpack(packed))

    def test_deterministic(self):
        packed = fx.build_lzexe(make_image(), relocs=[(0, 3), (5, 5)])
        a, b = unlzexe.unpack(packed), unlzexe.unpack(packed)
        self.assertEqual(hashlib.sha256(a).digest(), hashlib.sha256(b).digest())

    def test_rejects_other_files(self):
        with self.assertRaises(unlzexe.LzexeError):
            unlzexe.unpack(b"not an exe" * 10)
        with self.assertRaises(unlzexe.LzexeError):
            unlzexe.unpack(fx.build_lzexe(make_image(), signature=b"LZ09"))

    def test_rejects_a_truncated_stream(self):
        packed = fx.build_lzexe(make_image())
        with self.assertRaises(unlzexe.LzexeError):
            unlzexe.unpack(packed[:0x30])

    def test_command_line(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "scratch") if os.path.isdir(
                os.path.join(ROOT, "scratch")) else None) as d:
            src, dst = os.path.join(d, "p.exe"), os.path.join(d, "u.exe")
            packed = fx.build_lzexe(make_image(), relocs=[(0, 3)])
            with open(src, "wb") as f:
                f.write(packed)
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/static/unlzexe.py"), src, dst],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(dst, "rb") as f:
                self.assertEqual(f.read(), unlzexe.unpack(packed))
            self.assertIn(hashlib.sha256(unlzexe.unpack(packed)).hexdigest(), r.stdout)
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools/static/unlzexe.py"), dst, dst + "2"],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1)  # an unpacked file is not LZEXE


RELEASED = os.path.join(ROOT, ".cache", "goal2", "GOAL.EXE")


@unittest.skipUnless(os.path.exists(RELEASED), "the released GOAL.EXE is not in .cache/goal2")
class ReleasedFileTests(unittest.TestCase):
    """Runs only where the private release was downloaded; the original is never in the tree."""

    def test_known_hashes(self):
        with open(RELEASED, "rb") as f:
            data = f.read()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664")
        out = unlzexe.unpack(data)
        self.assertEqual(len(out), 193408)
        self.assertEqual(hashlib.sha256(out).hexdigest(),
                         "6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188")
        w, relocs, image = parse_mz(out)
        self.assertEqual(len(relocs), 1916)
        self.assertEqual(len(image), 185216)


if __name__ == "__main__":
    unittest.main()
