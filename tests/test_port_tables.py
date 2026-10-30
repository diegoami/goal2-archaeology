"""T80a: the port's constant tables (static/goal-exe/tables) and tools/static/port_tables.py's check.

The committed tables pass the check; a single mutated byte in either table fails it; the hex format
reads back exactly; extract refuses a GOAL.EXE whose slices are not the manifest's."""
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tool():
    spec = importlib.util.spec_from_file_location("port_tables_t80a", ROOT / "tools/static/port_tables.py")
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def run_check(module):
    out = StringIO()
    with redirect_stdout(out):
        code = module.check()
    return code, out.getvalue()


class PortTables(unittest.TestCase):
    def setUp(self):
        self.t = tool()
        self.tmp = Path(tempfile.mkdtemp());self.addCleanup(shutil.rmtree, self.tmp)

    def test_the_committed_tables_pass(self):
        code, text = run_check(self.t)
        self.assertEqual(code, 0, text)
        manifest = json.loads(self.t.MANIFEST.read_text())
        self.assertEqual(len(manifest["code_data"]), 173)
        self.assertEqual(sum(n for _, n in manifest["code_data"]), 11572)
        self.assertEqual(manifest["ds"]["length"], 0x7B70)

    def test_a_mutated_byte_in_either_table_fails(self):
        for name in ("ds.hex", "code_data.hex"):
            with self.subTest(table=name):
                folder = self.tmp / name;shutil.copytree(self.t.TABLES, folder)
                ds, code = self.t.read_tables(folder)
                ds, code = (bytes([ds[0] ^ 1]) + ds[1:], code) if name == "ds.hex" else (ds, bytes([code[0] ^ 1]) + code[1:])
                self.t.write_tables(folder, ds, code)
                self.t.TABLES = folder;self.t.MANIFEST = folder / "manifest.json"
                code_, text = run_check(self.t)
                self.assertEqual(code_, 1, text)
                self.assertIn("differ from the manifest's digests", text)
                self.t = tool()

    def test_the_hex_format_reads_back(self):
        for data in (b"", bytes(range(256)) * 3, b"\x00" * 1000 + b"\x01", b"A" * 64 + b"B" * 31):
            self.assertEqual(self.t.from_hex(self.t.to_hex(data, "t")), data)

    def test_extract_refuses_another_goal_exe(self):
        if not self.t.REGISTERED.exists():
            self.skipTest("the registered GOAL.EXE is not in .cache/artifacts")
        image = bytearray(self.t.image_of(self.t.REGISTERED.read_bytes()))
        unpacked = self.t.REGISTERED.read_bytes()
        import unlzexe
        exe = bytearray(unlzexe.unpack(unpacked))
        header = int.from_bytes(exe[8:10], "little") * 16
        exe[header + self.t.DS_IMAGE] ^= 0xFF                    # one data byte of the image changed
        bad = self.tmp / "GOAL.EXE";bad.write_bytes(bytes(exe))
        with self.assertRaises(SystemExit):
            self.t.extract(bad, self.tmp / "out")
        good = self.t.extract(self.t.REGISTERED, self.tmp / "good")
        self.assertEqual(good, self.t.read_tables(self.t.TABLES))
        self.assertEqual(len(image) > self.t.DS_IMAGE, True)


if __name__ == "__main__":
    unittest.main()
