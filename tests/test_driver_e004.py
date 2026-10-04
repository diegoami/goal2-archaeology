"""E004's runner (T10, experiments/E004-q002-quick-result/run.py): the pre-match path, the minute list,
the run-id reservation and the start-state refusal, with fakes in place of DOSBox-X."""
import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
_spec = importlib.util.spec_from_file_location("e004_run", ROOT / "experiments" / "E004-q002-quick-result" / "run.py")
e004 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e004)

import driver  # noqa: E402
import savestate  # noqa: E402


def screen(last="", extra=""):
    lines = [" " * 80 for _ in range(25)]
    lines[10] = extra.ljust(80)[:80]
    lines[24] = last.ljust(80)[:80]
    return savestate.Screen("".join(lines).encode("cp437"), bytes([7] * 2000))


CAPTAIN = screen(last="<-select  CAPTAIN                C-computer select")
TEAM = screen(last="Hit INS to turn automatic action replay OFF", extra="  location:Denmark")
OTHER = screen(last="something else")


class ScreensTest(unittest.TestCase):
    def test_captain_and_team_screens(self):
        self.assertTrue(e004.at_captain(CAPTAIN))
        self.assertFalse(e004.at_captain(TEAM))
        self.assertEqual(e004.extra_key(TEAM), "Enter")
        self.assertIsNone(e004.extra_key(CAPTAIN))
        self.assertIsNone(e004.extra_key(OTHER))


class MinutesTest(unittest.TestCase):
    def test_range(self):
        self.assertEqual(e004.minutes("10:58-11:01"), ["10:58:00", "10:59:00", "11:00:00", "11:01:00"])
        self.assertEqual(len(e004.minutes("10:00-11:39")), 100)

    def test_refusals(self):
        for bad in ("10:00", "10:00-9:00", "11:00-10:59", "1000-1100"):
            with self.assertRaises(ValueError, msg=bad):
                e004.minutes(bad)

    def test_state_names(self):
        self.assertEqual(e004.state_name("13:37:00"), "e004-1337")
        self.assertIn("--dos-time 13:37:00", e004.remake_command("e004-1337"))


class ReserveTest(unittest.TestCase):
    def test_next_free_number_over_records_and_reservations(self):
        with tempfile.TemporaryDirectory() as tmp:
            out, ids = Path(tmp) / "runs", Path(tmp) / "ids"
            out.mkdir()
            (out / "E004-r0003.json").write_text("{}")
            with mock.patch.object(e004, "OUT", out), mock.patch.object(e004, "IDS", ids):
                self.assertEqual(e004.reserve_id(), 4)
                self.assertEqual(e004.reserve_id(), 5)
                (ids / "9").mkdir()
                self.assertEqual(e004.reserve_id(), 10)


class LoadStateTest(unittest.TestCase):
    def test_a_state_with_another_layout_is_refused_with_the_remake_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            states = Path(tmp)
            (states / "e004-1000.sav").write_bytes(b"x")
            meta = {"sha256": driver.sha256(b"x"), "screen_digest": "0", "game_dir": str(driver.GAME_DIR), "config": {}}
            (states / "e004-1000.json").write_text(json.dumps(meta))  # no drive_layout: made before T08 round 4
            with mock.patch.object(driver, "STATES", states), \
                    mock.patch.object(driver.StartState.__init__, "__defaults__", (states,)):
                with self.assertRaises(SystemExit) as cm:
                    e004.load_state("e004-1000")
            self.assertIn("refused", str(cm.exception))
            self.assertIn("make-state --dos-time 10:00:00", str(cm.exception))


class FakeDriver:
    """Fresh launch: the title, then one screen per key from `after_keys`."""

    def __init__(self, after_keys, *a, **kw):
        self.after, self.k, self.sent = list(after_keys), 0, []
        self.last = ({"utc": "t", "local": "l", "tz": "z"}, mock.Mock())
        self.launched = None

    def launch(self, st, **kw):
        return OTHER

    def keys(self, *names):
        self.sent.extend(names)

    def settle(self, prev, what=""):
        sc = self.after[min(self.k, len(self.after) - 1)]
        self.k += 1
        return sc

    def terminate(self):
        return True


class GoTest(unittest.TestCase):
    """Run.go() for a fresh launch: the match starts only at the captain screen."""

    def go(self, after_keys):
        fake = FakeDriver(after_keys)
        args = argparse.Namespace(dos_date="10/04/2026", batch="t")
        with mock.patch.object(e004.driver, "Driver", lambda *a, **kw: fake), \
                mock.patch.object(e004.Run, "add_full", lambda *a, **kw: None), \
                mock.patch.object(e004.Run, "record", lambda self, status, gone: status), \
                mock.patch.object(e004.traceback, "print_exc"), \
                mock.patch.object(e004.match, "play", return_value=([], 0, 0.0)) as play:
            status = e004.Run("sample", "quick", 1, args, "c", dos_time="10:00:00").go()
        return status, fake, play

    def test_captain_reached_directly(self):
        n = len(e004.TO_MAIN + e004.TO_CAPTAIN)
        status, fake, play = self.go([OTHER] * (n - 1) + [CAPTAIN])
        self.assertEqual(status, "completed")
        self.assertEqual(fake.sent, e004.TO_MAIN + e004.TO_CAPTAIN)
        play.assert_called_once()

    def test_team_screen_then_captain(self):
        n = len(e004.TO_MAIN + e004.TO_CAPTAIN)
        status, fake, play = self.go([OTHER] * (n - 1) + [TEAM, CAPTAIN])
        self.assertEqual(status, "completed")
        self.assertEqual(fake.sent, e004.TO_MAIN + e004.TO_CAPTAIN + ["Enter"])

    def test_no_match_without_the_captain_screen(self):
        n = len(e004.TO_MAIN + e004.TO_CAPTAIN)
        status, fake, play = self.go([OTHER] * n + [OTHER])
        self.assertTrue(status.startswith("aborted: RuntimeError: not at the captain screen"))
        play.assert_not_called()


if __name__ == "__main__":
    unittest.main()
