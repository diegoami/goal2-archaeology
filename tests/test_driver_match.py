"""The match player (T10, runtime/driver/match.py) against a scripted fake driver: which keys it
sends, when, and when it stops or aborts. No DOSBox-X."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import match  # noqa: E402
import savestate  # noqa: E402


def screen(rows=("", "", ""), last="", extra=""):
    """A text screen whose rows 1-3, columns 31-66, hold `rows`, with `extra` on row 10 and `last` on row 24."""
    lines = [" " * 80 for _ in range(25)]
    for i, r in enumerate(rows):
        lines[1 + i] = (" " * 31 + r).ljust(80)[:80]
    lines[10] = extra.ljust(80)[:80]
    lines[24] = last.ljust(80)[:80]
    return savestate.Screen("".join(lines).encode("cp437"), bytes([7] * 2000))


class FakeState:
    def __init__(self, sc):
        self.sc = sc

    def screen(self):
        return self.sc


class FakeDriver:
    """d.read() returns the scripted screens in order; the last one repeats."""

    def __init__(self, screens):
        self.screens, self.i, self.sent, self.logged = list(screens), 0, [], []

    def keys(self, *names):
        self.sent.append((self.i, names))

    def log(self, what):
        self.logged.append(what)

    def read(self):
        sc = self.screens[min(self.i, len(self.screens) - 1)]
        self.i += 1
        return {"utc": "t"}, FakeState(sc), b""


class Clock:
    """A clock that advances one second per call."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        self.t += 1.0
        return self.t


LIVE1 = screen(("a pass", "a run", "a shot"))
LIVE2 = screen(("a run", "a shot", "a save"))
HALF = screen(("x", "y", "---- HALF TIME ----"), last="          hit any key")
TEAM = screen(("x", "y", "---- HALF TIME ----"), extra="  location:Denmark")
SECOND = screen(("Brolin to take kick off", "", ""))
FULL = screen(("x", "y", "---- FULL TIME ----"))
FULL_KEY = screen(("x", "y", "---- FULL TIME ----"), last="          hit any key")
REPLAY = screen(("**** GOAL **** by Nilsson", "", ""), last="Do you want an action replay? (Y/N)")


class PlayTest(unittest.TestCase):
    def play(self, arm, screens, **kw):
        d = FakeDriver(screens)
        keys, reads, _ = match.play(d, arm, clock=Clock(), **kw)
        return d, keys, reads

    def test_starting_burst_per_arm(self):
        d, keys, _ = self.play("quick", [LIVE1, FULL, FULL])
        self.assertEqual(d.sent[0], (0, ("Enter", "r")))
        d, keys, _ = self.play("watched", [LIVE1, FULL, FULL])
        self.assertEqual(d.sent[0], (0, ("Enter", "Right", "Right", "Right", "Right", "Right")))
        self.assertEqual(len(d.sent), 1)

    def test_unknown_arm_refused(self):
        with self.assertRaises(ValueError):
            match.play(FakeDriver([FULL]), "slow", clock=Clock())

    def test_no_key_on_a_stable_screen_that_is_not_a_wait(self):
        # the kick-off pause and the action-replay prompt are stable for long and get no key
        d, keys, _ = self.play("watched", [SECOND] * 8 + [REPLAY] * 8 + [LIVE1, FULL, FULL])
        self.assertEqual(len(d.sent), 1)
        self.assertEqual([k for _, k, _ in keys], ["Enter"] + ["Right"] * 5)

    def test_enter_on_hit_any_key_and_team_screen_only_when_stable(self):
        d, keys, _ = self.play("quick", [LIVE1, HALF, HALF, TEAM, TEAM, SECOND, LIVE2, FULL, FULL])
        self.assertEqual([(k, why) for _, k, why in keys[2:]], [("Enter", "hit any key"), ("Enter", "team screen")])
        self.assertEqual([i for i, _ in d.sent[1:]], [3, 5])  # after the second equal read of each

    def test_one_read_of_hit_any_key_gets_no_key(self):
        d, keys, _ = self.play("quick", [LIVE1, HALF, LIVE2, FULL, FULL])
        self.assertEqual(len(d.sent), 1)

    def test_full_time_with_hit_any_key_ends_without_a_key(self):
        d, keys, reads = self.play("watched", [LIVE1, FULL_KEY, FULL_KEY, FULL_KEY])
        self.assertEqual(len(d.sent), 1)
        self.assertEqual(reads, 3)

    def test_full_time_needs_two_equal_reads(self):
        d, keys, reads = self.play("quick", [LIVE1, FULL, LIVE2, FULL, FULL])
        self.assertEqual(reads, 5)

    def test_a_key_not_acted_on_aborts(self):
        with self.assertRaises(match.MatchError):
            self.play("quick", [LIVE1] + [HALF] * 40)

    def test_no_second_key_while_the_first_is_pending(self):
        screens = [LIVE1] + [HALF] * (match.KEY_TAKEN_READS + 1) + [TEAM, TEAM, SECOND, FULL, FULL]
        d, keys, _ = self.play("quick", screens)
        self.assertEqual([why for _, _, why in keys[2:]], ["hit any key", "team screen"])

    def test_timeout(self):
        with self.assertRaises(match.MatchError):
            self.play("quick", [LIVE1, LIVE2] * 100, timeout=20)


class WantsKeyTest(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(match.wants_key(HALF), "hit any key")
        self.assertEqual(match.wants_key(TEAM), "team screen")
        self.assertIsNone(match.wants_key(FULL_KEY))
        self.assertIsNone(match.wants_key(REPLAY))
        self.assertIsNone(match.wants_key(LIVE1))


if __name__ == "__main__":
    unittest.main()
