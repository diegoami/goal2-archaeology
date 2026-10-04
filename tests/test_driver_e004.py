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
        for bad in ("10:00", "10:00-9:00", "11:00-10:59", "1000-1100", "x10:00-10:03", "10:00-10:03x"):
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


    def test_an_id_taken_meanwhile_is_skipped(self):
        """Another slot reserves the same number between the scan and the mkdir: the next is taken."""
        with tempfile.TemporaryDirectory() as tmp:
            out, ids = Path(tmp) / "runs", Path(tmp) / "ids"
            out.mkdir()
            real_mkdir = Path.mkdir
            raced = []

            def racing_mkdir(path, *a, **kw):
                if path.parent == ids and not raced:
                    raced.append(path.name)
                    real_mkdir(path)  # the other slot's reservation lands first
                return real_mkdir(path, *a, **kw)
            with mock.patch.object(e004, "OUT", out), mock.patch.object(e004, "IDS", ids), \
                    mock.patch.object(Path, "mkdir", racing_mkdir):
                self.assertEqual(e004.reserve_id(), 2)
            self.assertEqual(raced, ["1"])


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


_sspec = importlib.util.spec_from_file_location("e004_summarise", ROOT / "experiments" / "E004-q002-quick-result" / "summarise.py")
summ = importlib.util.module_from_spec(_sspec)
_sspec.loader.exec_module(summ)


class SummariseTest(unittest.TestCase):
    """The parts of summarise.py that decide what is printed as identical, counted or tested."""

    def test_scoreboard(self):
        rows = [""] * 25
        rows[1] = " ┌─┐┌─┐┌─┐│ │DENMARK--------│ 0│Jansson wins the toss"
        rows[3] = " └─┤└─┘└─┤│ │SWEDEN---------│12│---- FULL TIME ----"
        self.assertEqual(summ.scoreboard("\n".join(rows)), ("DENMARK", 0, "SWEDEN", 12))

    def test_stats_screen(self):
        text = "│  Bookings     1  ││  Bookings     3  │\n│  Red cards    0  └┘  Red cards    2  │"
        self.assertEqual(summ.stats_screen(text), {"Bookings": (1, 3), "Red cards": (0, 2)})
        self.assertEqual(summ.stats_screen("no statistics"), {})

    def test_disallowed_goal_is_the_one_followed_by_offside(self):
        lines = [[1, 66, 1, "** LINESMAN FLAGS **"], [2, 38, 1, "GOAL by Vilfort"], [3, 54, 1, "Andersen is OFFSIDE"],
                 [4, 38, 0, "GOAL by Rush"], [5, 49, 1, "Laudrup to take kick off"]]
        self.assertEqual(summ.disallowed(lines), [[2, 38, 1, "GOAL by Vilfort"]])

    def test_same(self):
        a = {"score": ("A", 1, "B", 0), "events": [["goal", 0, "x"]], "seed": "0x1", "lines": [[1]]}
        self.assertTrue(summ.same(a, dict(a)))
        for k, v in (("score", ("A", 1, "B", 1)), ("events", []), ("seed", "0x2")):
            self.assertFalse(summ.same(a, dict(a, **{k: v})), k)
        self.assertTrue(summ.same(a, dict(a, lines=[[2]])))
        self.assertFalse(summ.same(a, dict(a, lines=[[2]]), lines=True))

    def record(self, score_bytes, events, lines):
        """A completed run/1 record with the fields load() reads (field names as run.py writes them)."""
        rows = [""] * 25
        rows[1] = " ┌─┐┌─┐┌─┐│ │DENMARK--------│ %d│x" % score_bytes[1]
        rows[3] = " └─┤└─┘└─┤│ │SPAIN----------│ %d│---- FULL TIME ----" % score_bytes[0]
        obs = [("full time: text screen rows 0-24, CP437", "\n".join(rows)),
               ("full time: text screen 80x25, chars+attributes", "d" * 64),
               ("full time: word at DS:7B62 of GOAL.EXE", "0x1234 (34 12)"),
               ("full time: score bytes DS:9B3C, DS:9B3D (engine teams 0 and 1)", f"{score_bytes[0]} {score_bytes[1]}"),
               ("events among them (templates ...)", json.dumps(events)),
               ("commentary lines of the match in order", json.dumps(lines)),
               ("commentary lines between successive reads", json.dumps({"deltas": [len(lines)], "gaps": []})),
               ("keys sent from the key that starts the match", "[]"),
               ("match: savestate reads from the starting keys", "3 reads, 20.0 s")]
        return {"run_id": "E004-r9999", "arm": "quick-fresh-time-102300", "status": "completed",
                "actions": {"args": ["sample", "--arm", "quick", "--dos-time", "10:23:00"]},
                "observations": [{"step": 1, "source": "memory", "field": f, "value": v} for f, v in obs]}

    def test_load_takes_goals_from_the_score_bytes_and_the_rest_from_the_commentary(self):
        # E004-r0053's case, and more: Laudrup scores three times and Hierro twice, each with no line
        # between, so `0791:1C78` keeps one goal line each; the score bytes say 2 (Spain) and 3. The
        # event list holds 4 goal lines, 2 disallowed (followed by an offside line), so neither the
        # lines (4), the lines less the disallowed (2) nor either score byte alone gives the 5 goals. One booking, one sending off and one injury come from the commentary
        # (the score bytes cannot give them), and a goal line followed by an offside line is not counted.
        lines = [[1, 59, 1, "Piechnik wins the toss"], [2, 38, 1, "**** GOAL **** by Laudrup"],
                 [3, 50, 0, "Hierro BOOKED"], [4, 51, 0, "Hierro SENT OFF"], [5, 52, 1, "Olsen INJURED"],
                 [6, 38, 1, "**** GOAL **** by Vilfort"], [7, 54, 1, "Vilfort is OFFSIDE"],
                 [8, 38, 0, "**** GOAL **** by Hierro"], [9, 49, 1, "Laudrup to take kick off"],
                 [10, 38, 0, "**** GOAL **** by Salinas"], [11, 54, 0, "Salinas is OFFSIDE"]]
        events = [["goal", 1, "**** GOAL **** by Laudrup"], ["booking", 0, "Hierro BOOKED"], ["sending off", 0, "Hierro SENT OFF"],
                  ["injury", 1, "Olsen INJURED"], ["goal", 1, "**** GOAL **** by Vilfort"],
                  ["goal", 0, "**** GOAL **** by Hierro"], ["goal", 0, "**** GOAL **** by Salinas"]]
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "E004-r9999.json"
            p.write_text(json.dumps(self.record((2, 3), events, lines)))
            r = summ.load(p)
        self.assertEqual(r["counts"], {"goals": 5, "bookings": 1, "sendings off": 1, "injuries": 1})
        self.assertEqual(r["commentary_goals"], 2)   # four goal lines, two disallowed
        self.assertEqual(r["score"], ("DENMARK", 3, "SPAIN", 2))

    def test_tests_separate_equal_from_different_samples(self):
        import random
        self.assertGreater(summ.perm_test([1, 2, 1, 2] * 10, [2, 1, 2, 1] * 10, random.Random(1)), 0.5)
        self.assertLess(summ.perm_test([0] * 30, [3] * 30, random.Random(1)), 0.001)
        self.assertLess(summ.sign_flip([2] * 30, random.Random(1)), 0.001)
        self.assertGreater(summ.sign_flip([1, -1] * 15, random.Random(1)), 0.5)


if __name__ == "__main__":
    unittest.main()
