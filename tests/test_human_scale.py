"""#148: play.sh --scale N sizes the game window (DOSBox-X `[render] scaler=normal<N>x`) and the
nested display; 2 by default for the owner's sittings, 1 for scripted sittings. Emulation and
savestates do not change: the scale is in the config (config_sha256) and in meta.json."""
import importlib.util
import subprocess
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

    def test_1x_is_the_driver_config_plus_windowresolution(self):
        # the recorder always sets windowresolution to the scaled game window so DOSBox-X's
        # window cannot open at a default size bigger than the nested Xephyr screen (#174);
        # scale 1 adds the resolution line to the [sdl] section but no [render] section
        with tempfile.TemporaryDirectory() as d:
            base = rec.driver.Driver(workdir=Path(d), game_dir=Path(d) / "game").conf_text()
            conf = rec.conf_for(Path(d), 1)
        self.assertNotEqual(conf, base)                  # windowresolution was added
        self.assertIn("[sdl]\nwindowresolution=720x400\n", conf)
        self.assertNotIn("[render]", conf)

    def test_windowresolution_matches_the_scaled_game_window(self):
        # DOSBox-X's window must be exactly the scaled game window for every supported scale:
        # 720x400 at 1x, 1440x800 at 2x (the issue's case), 2160x1200 at 3x
        self.assertIn("[sdl]\nwindowresolution=720x400\n", self.conf(1))
        self.assertIn("[sdl]\nwindowresolution=1440x800\n", self.conf(2))
        self.assertIn("[sdl]\nwindowresolution=2160x1200\n", self.conf(3))

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


class FitTests(unittest.TestCase):
    """#174: the outer display caps the scale and the nested screen, so a scale taller than the
    display is not used. WSLg's Xwayland reports the Windows desktop's logical size (physical /
    display scale): a 5120x1440 desktop at 200% appears as 2560x720, and 2x's 1440x800 game window
    cannot fit it."""

    def test_the_owners_display_caps_scale_2_and_3_to_1(self):
        self.assertEqual(rec.fit_scale(2560, 720, 2), 1)
        self.assertEqual(rec.fit_scale(2560, 720, 3), 1)

    def test_a_scale_that_fits_is_kept(self):
        self.assertEqual(rec.fit_scale(5120, 1440, 2), 2)
        self.assertEqual(rec.fit_scale(5120, 1440, 3), 3)
        self.assertEqual(rec.fit_scale(1280, 800, 2), 1)   # 1440 wide does not fit 1280
        self.assertEqual(rec.fit_scale(2560, 840, 2), 2)   # 800 game + 40 chrome fits

    def test_a_scale_never_grows_past_the_request(self):
        self.assertEqual(rec.fit_scale(5120, 1440, 1), 1)

    def test_no_scale_fits_a_display_smaller_than_the_game_window(self):
        # R1 (#204): the smallest game window (720x400) does not fit 640x320, so no scale fits and
        # the caller must refuse rather than return a nested screen bigger than the display.
        self.assertIsNone(rec.fit_scale(640, 320, 2))
        self.assertEqual(rec.plan_window(2, None, (640, 320)), (None, None))
        self.assertEqual(rec.plan_window(1, None, (640, 320)), (None, None))

    def test_plan_window_shrinks_scale_and_nested_screen_to_the_display(self):
        self.assertEqual(rec.plan_window(1, None, (2560, 720)), (1, "1280x680"))
        self.assertEqual(rec.plan_window(2, None, (2560, 720)), (1, "1280x680"))
        self.assertEqual(rec.plan_window(3, None, (2560, 720)), (1, "1280x680"))
        self.assertEqual(rec.plan_window(2, None, (5120, 1440)), (2, "1440x800"))
        self.assertEqual(rec.plan_window(3, None, (5120, 1440)), (3, "2160x1200"))

    def test_plan_window_without_a_display_keeps_the_old_behaviour(self):
        self.assertEqual(rec.plan_window(2, None, None), (2, "1440x800"))
        self.assertEqual(rec.plan_window(3, None, None), (3, "2160x1200"))

    def test_plan_window_honours_an_explicit_res_but_caps_the_scale(self):
        self.assertEqual(rec.plan_window(2, "900x700", (2560, 720)), (1, "900x700"))
        self.assertEqual(rec.plan_window(2, "900x700", (5120, 1440)), (2, "900x700"))

    def test_outer_display_size_reads_xdotool(self):
        ok = subprocess.CompletedProcess([], 0, "2560 720\n", "")
        with mock.patch.object(rec, "xdotool", return_value=ok):
            self.assertEqual(rec.outer_display_size({"DISPLAY": ":0"}), (2560, 720))

    def test_outer_display_size_is_none_when_unreadable(self):
        bad = subprocess.CompletedProcess([], 1, "", "Can't open display")
        with mock.patch.object(rec, "xdotool", return_value=bad):
            self.assertIsNone(rec.outer_display_size({"DISPLAY": ":0"}))
        with mock.patch.object(rec, "xdotool",
                               side_effect=subprocess.TimeoutExpired("xdotool", 10)):
            self.assertIsNone(rec.outer_display_size({"DISPLAY": ":0"}))


if __name__ == "__main__":
    unittest.main()
