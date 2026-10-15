"""play.sh --cycles: the emulated CPU speed of a sitting. 8000 fixed cycles by default (about a 386
at 33 MHz, the owner 2026-10-15); N, max and auto are accepted; the value is in the config and meta.json."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("human_recorder_cycles", ROOT / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


class CyclesTests(unittest.TestCase):
    def conf(self, cycles, scale=1):
        with tempfile.TemporaryDirectory() as d:
            return rec.conf_for(Path(d), scale, cycles)

    def test_default_is_fixed_8000(self):
        self.assertEqual(rec.DEFAULT_CYCLES, "fixed 8000")
        self.assertIn("\ncycles=fixed 8000\n", self.conf(rec.DEFAULT_CYCLES))

    def test_accepted_values(self):
        self.assertEqual(rec.parse_cycles("25000"), "fixed 25000")
        self.assertEqual(rec.parse_cycles("fixed 3000"), "fixed 3000")
        self.assertEqual(rec.parse_cycles("MAX"), "max")
        self.assertEqual(rec.parse_cycles("auto"), "auto")
        self.assertIn("\ncycles=fixed 25000\n", self.conf("25000", 2))

    def test_refused_values(self):
        for bad in ("0", "-5", "fast", "", "8000 cycles"):
            with self.assertRaises(ValueError, msg=bad):
                rec.parse_cycles(bad)

    def test_no_cycles_keeps_the_driver_config(self):
        self.assertIn("\ncycles=max\n", self.conf(None))


if __name__ == "__main__":
    unittest.main()
