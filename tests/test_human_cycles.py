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

    def test_scripted_sittings_keep_the_driver_config(self):
        self.assertEqual(rec.default_cycles(None, None), "fixed 8000")
        self.assertIsNone(rec.default_cycles(None, 30.0))
        self.assertEqual(rec.default_cycles("max", None), "max")
        self.assertEqual(rec.default_cycles("5000", 30.0), "5000")

    def test_play_without_cycles_calls_new_session_as_before(self):
        # the old signature: test doubles and callers that pass no cycles
        import inspect
        self.assertIsNone(inspect.signature(rec.play).parameters["cycles"].default)

    def test_no_cycles_keeps_the_driver_config(self):
        self.assertIn("\ncycles=max\n", self.conf(None))


class CadenceTests(unittest.TestCase):
    def test_owner_sittings_tick_every_5_s_scripted_keep_20(self):
        self.assertEqual(rec.default_cadence(None, None), 5.0)
        self.assertEqual(rec.default_cadence(None, 30.0), rec.CADENCE_S)
        self.assertEqual(rec.CADENCE_S, 20.0)
        self.assertEqual(rec.default_cadence(2.5, None), 2.5)

    def test_cadence_must_be_positive(self):
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                rec.default_cadence(bad, None)

    def test_watcher_takes_the_cadence(self):
        import inspect
        p = inspect.signature(rec.Watcher).parameters["cadence_s"]
        self.assertEqual(p.default, rec.CADENCE_S)


if __name__ == "__main__":
    unittest.main()
