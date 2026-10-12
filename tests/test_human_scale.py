"""#148: play.sh --scale N sizes the game window (DOSBox-X `[render] scaler=normal<N>x`) and the
nested display; 2 by default for the owner's sittings, 1 for scripted sittings. Emulation and
savestates do not change: the scale is in the config (config_sha256) and in meta.json."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("human_recorder_scale", ROOT / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


class ScaleTests(unittest.TestCase):
    def conf(self, scale):
        with tempfile.TemporaryDirectory() as d:
            return rec.conf_for(Path(d), scale)

    def test_1x_is_the_driver_config_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            base = rec.driver.Driver(workdir=Path(d), game_dir=Path(d) / "game").conf_text()
            self.assertEqual(rec.conf_for(Path(d), 1), base)
        self.assertNotIn("[render]", self.conf(1))

    def test_2x_adds_the_scaler_before_autoexec(self):
        conf = self.conf(2)
        self.assertIn("[render]\nscaler=normal2x forced\n[autoexec]\n", conf)
        self.assertEqual(conf.count("[render]"), 1)
        # everything after [autoexec] is the autoexec itself: the scaler must come before it
        self.assertNotIn("scaler", conf.split("[autoexec]", 1)[1])

    def test_a_scale_outside_1_to_3_is_refused(self):
        for bad in (0, 4):
            with self.assertRaises(ValueError):
                self.conf(bad)

    def test_the_nested_display_fits_the_scaled_window(self):
        self.assertEqual(rec.nested_res(1), "1280x800")       # as before #148
        self.assertEqual(rec.nested_res(2), "1440x800")       # the issue's 2x
        self.assertEqual(rec.nested_res(3), "2160x1200")

    def test_play_defaults_to_2x_and_takes_1x(self):
        with mock.patch.object(rec, "play", return_value=0) as play:
            rec.main(["play"])
            self.assertEqual(play.call_args.kwargs["scale"], 2)
            self.assertIsNone(play.call_args.kwargs["res"])
            rec.main(["play", "--scale", "1"])
            self.assertEqual(play.call_args.kwargs["scale"], 1)
        with self.assertRaises(SystemExit):
            rec.main(["play", "--scale", "4"])


if __name__ == "__main__":
    unittest.main()
