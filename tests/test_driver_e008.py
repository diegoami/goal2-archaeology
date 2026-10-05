"""E008 (T19, Q005): the one-byte savestate edit (runtime/driver/savestate.py with_memory), the ranks
and rating of experiments/E008-*/summarise.py, and the listing filter of experiments/E008-*/readers.py.

The synthetic savestate is written here with literal offsets (F001: guest address 0 at offset 0x78 of
the inflated Memory component), not from the module; the GOAL.DAT blocks are planted at the offsets
static/goal-dat/blocks.tsv gives (blocks 8 and 9: 0xA0F2 and 0xA173, 129 one-byte records)."""
import importlib.util
import io
import sys
import tempfile
import unittest
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402

HERE = ROOT / "experiments" / "E008-q005-r008-tactics"
sys.path.insert(0, str(HERE))


def load_by_path(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


summarise = load_by_path("e008_summarise", "experiments/E008-q005-r008-tactics/summarise.py")
readers = load_by_path("e008_readers", "experiments/E008-q005-r008-tactics/readers.py")

TRAILER = b"\x01\x02\x03\x04\x05\x06\x07\x08"   # DOSBox-X writes 8 bytes after the Memory stream


def synthetic(mem):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("CPU", b"cpu bytes", compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("Memory", zlib.compress(b"\0" * 0x78 + mem, 1) + TRAILER, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("Vga", zlib.compress(b"\0" * 16), compress_type=zipfile.ZIP_STORED)
    return buf.getvalue()


class WithMemory(unittest.TestCase):
    def setUp(self):
        self.mem = bytes(range(256)) * 16
        self.data = synthetic(self.mem)

    def test_edits_only_the_named_bytes(self):
        out = savestate.with_memory(self.data, 0x123, b"\xee")
        got = savestate.Savestate(out).memory(0, len(self.mem))
        want = bytearray(self.mem)
        want[0x123] = 0xEE
        self.assertEqual(got, bytes(want))

    def test_other_components_order_compression_and_trailer_kept(self):
        out = savestate.with_memory(self.data, 0, b"\x99\x98")
        a, b = zipfile.ZipFile(io.BytesIO(self.data)), zipfile.ZipFile(io.BytesIO(out))
        self.assertEqual([(i.filename, i.compress_type) for i in a.infolist()], [(i.filename, i.compress_type) for i in b.infolist()])
        for n in ("CPU", "Vga"):
            self.assertEqual(a.read(n), b.read(n))
        d = zlib.decompressobj()
        d.decompress(b.read("Memory"))
        self.assertEqual(d.unused_data, TRAILER)

    def test_outside_memory_refused(self):
        with self.assertRaises(ValueError):
            savestate.with_memory(self.data, len(self.mem), b"\x00")


class Ranks(unittest.TestCase):
    def dat(self, order8, order9):
        b = bytearray(0xA1F4)
        b[0xA0F2 + 1:0xA0F2 + 129] = bytes(order8)
        b[0xA173 + 1:0xA173 + 129] = bytes(order9)
        return bytes(b)

    def test_positions_become_ranks(self):
        order8 = list(range(128, 0, -1))           # world rank k is country 129 - k
        order9 = list(range(1, 129))               # continent position i is country i
        rk = summarise.ranks(self.dat(order8, order9))
        self.assertEqual(rk[1], (1, 128, 1))
        self.assertEqual(rk[33], (1, 96, 2))       # position 33: first of continent 2
        self.assertEqual(rk[128], (32, 1, 4))

    def test_not_a_permutation_refused(self):
        with self.assertRaises(ValueError):
            summarise.ranks(self.dat([1] * 128, list(range(1, 129))))

    def test_rating_formula(self):
        # 1771:10E7 at world 1, continent 1, rank 1: ((5-1)*(33-1) + (129-1)) // 2 = 128
        self.assertEqual(summarise.rating(1, 1, 1), 128)
        self.assertEqual(summarise.rating(32, 128, 4), (1 * 1 + 1) // 2)

    def test_order(self):
        rows = [{"continent": k, "mean": m} for k, m in ((1, 4.0), (2, 3.0), (3, 2.0), (4, 1.0))]
        self.assertTrue(summarise.order_holds(rows))
        rows[1]["mean"] = 1.5
        self.assertFalse(summarise.order_holds(rows))


LISTING = """; ---- routine 1771:0001  (found by: call)
0001  C4 3E 17 A9     les di, ptr [0xa917]
0005  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
; ---- routine 1771:0010  (found by: call)
0010  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
; ---- routine 1771:0020  (found by: call)
0020  C4 3E 1B A9     les di, ptr [0xa91b]
0024  81 C7 0F 00     add di, 0xf
0028  26 8A 45 2D     mov al, byte ptr es:[di + 0x2d]
"""


class Readers(unittest.TestCase):
    def test_access_counted_only_with_its_array_pointer(self):
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / "seg_1771_01.asm").write_text(LISTING)
            got = readers.scan(t)
        self.assertEqual(sorted(got), ["1771:0001", "1771:0020"])
        self.assertEqual(got["1771:0001"], {"+0x2D": [("seg_1771_01.asm", 3)]})
        self.assertEqual(got["1771:0020"], {"+0xF": [("seg_1771_01.asm", 8)]})

    def test_reach_follows_edges(self):
        g = {"a": {"b"}, "b": {"c"}, "c": set(), "d": {"a"}}
        import collections
        g = collections.defaultdict(set, g)
        self.assertEqual(readers.reach(g, "a"), {"a", "b", "c"})


if __name__ == "__main__":
    unittest.main()
