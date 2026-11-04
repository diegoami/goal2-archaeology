"""T124t: the route harness chooses, then the original makes, a legal eleven."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match.route_team import choose_eleven


class ChoiceTests(unittest.TestCase):
    def setUp(self):
        self.squad = list(range(1, 21))
        self.players = {w: {6: 1 + (w - 2) // 3, 14: 20, 16: 0} for w in self.squad}
        self.players[1][6] = 0
        for w in (2, 3):
            self.players[w][6] = 1
        self.players[12][6] = 0

    def pick(self):
        return choose_eleven(self.squad, lambda w, f: self.players[w][f])

    def test_keeps_the_legal_eleven(self):
        self.assertEqual(self.pick(), [])

    def test_replaces_injured_keeper_with_the_first_legal_keeper(self):
        self.players[1][14] = 0
        self.assertEqual(self.pick(), [(1, 12)])

    def test_all_three_status_bits_and_signed_energy_are_unavailable(self):
        for value in (4, 32, 128):
            with self.subTest(status=value):
                self.players[1][16] = value
                self.assertEqual(self.pick(), [(1, 12)])
        self.players[1][16] = 0
        for value in (0, 128, 255):
            with self.subTest(energy=value):
                self.players[1][14] = value
                self.assertEqual(self.pick(), [(1, 12)])

    def test_empty_slot_replaced_without_trying_to_mark_it(self):
        self.squad[0] = 0
        self.assertEqual(self.pick(), [(0, 12)])

    def test_no_legal_eleven_stops(self):
        self.players[1][14] = self.players[12][14] = 0
        with self.assertRaisesRegex(ValueError, "legal eleven"):
            self.pick()


class KeyLogTests(unittest.TestCase):
    def test_pushed_back_read_is_recorded_even_without_a_policy_callback(self):
        from unittest.mock import Mock, patch
        from original_match.route_team import RouteMatch
        from original_match.match import Match, PUSHED_BACK, KEY
        match = RouteMatch.__new__(RouteMatch)
        match.m = Mock()
        match.m.rd.side_effect = lambda field, size: 1 if field == PUSHED_BACK else 13
        match.m.stack_word.side_effect = lambda off: {0: 0x1234, 2: 0x5678}[off]
        match.m.where.return_value = "0791:1234"
        match.st = {"menu_context": "pre_match"}
        match.team_keys = []
        with patch.object(Match, "_on_readkey") as original:
            match._on_readkey(False)
        original.assert_called_once_with(False)
        self.assertEqual(match.team_keys, [{"site": "0791:1234", "key": 13, "context": "pre_match",
                                           "source": "pushed-back"}])


class CheckpointTests(unittest.TestCase):
    def test_checkpoint_hash_checked_before_loading_guest_bytes(self):
        import hashlib
        import importlib.util
        import tempfile
        from unittest.mock import patch
        path = ROOT / "experiments/E040-route-fixture-writes/out/T124t/prove.py"
        spec = importlib.util.spec_from_file_location("t124t_prove", path)
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory() as tmp:
            checkpoint = Path(tmp) / "round.mem"
            checkpoint.write_bytes(b"complete checkpoint")
            sha = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
            with patch.object(runner, "Image", return_value="image") as image:
                self.assertEqual(runner.load_checkpoint(checkpoint, sha), "image")
                image.assert_called_once_with(b"complete checkpoint")
                checkpoint.write_bytes(b"truncated")
                with self.assertRaisesRegex(ValueError, "checkpoint hash mismatch"):
                    runner.load_checkpoint(checkpoint, sha)
                self.assertEqual(image.call_count, 1)


STATE = ROOT / ".cache/dl/53b69d3dfb964e77-snap-0213-20261011T142027Z.sav"
try:
    import unicorn
    HAVE_UNICORN = True
except ImportError:
    HAVE_UNICORN = False


@unittest.skipUnless(HAVE_UNICORN and STATE.is_file(), "unicorn and E015-r0007 state 213 required (E040 runner --fetch)")
class OriginalMenuTests(unittest.TestCase):
    """Synthetic unavailable starters on a published state; every swap and EA09 validation is original code."""
    def make(self, empty=False, multiple=False):
        import hashlib
        from original_match.image import Image, PLAYERS_PTR, PLAYER_SIZE
        from original_match.match import Fixture, PLAY_MATCH
        from original_match.route_team import RouteMatch
        data = STATE.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "53b69d3dfb964e777c689d439d3bf434600f8891e391cab5c45fd863787d2a94")
        match = RouteMatch(Image.from_savestate(data), Fixture(first=16, second=3, index=22, kind=2))
        squad = match._squad(16)
        if empty:
            match.m.write(match._country(16), b"\0\0")
        else:
            for word in squad[:3] if multiple else squad[:1]:
                match.m.write(match.m.far(PLAYERS_PTR) + PLAYER_SIZE * word + 14, b"\0")
        swaps, validations = [], []
        match.m.at("0791:DEA6", lambda replay: replay or swaps.append(match.m.rd(0x0C1B)))
        match.m.at("0791:EA09", lambda replay: replay or validations.append(1))
        match.m.at(PLAY_MATCH, lambda replay: replay or match.m.stop("menu-accepted"))
        return match, swaps, validations

    def accepted(self, match):
        self.assertEqual(match.m.run(match.end_lin, 120, fresh=True), "menu-accepted")
        self.assertEqual(choose_eleven(match._squad(16), match._player), [])
        self.assertTrue(match.team_keys)
        self.assertTrue(any(k["site"] == "0791:E61F" for k in match.team_keys))
        self.assertTrue(all(0 <= k["key"] <= 255 for k in match.team_keys))

    def test_original_swaps_injured_keeper_and_validates(self):
        match, swaps, validations = self.make()
        self.accepted(match)
        self.assertEqual(len(swaps), 2)
        self.assertTrue(validations)
        self.assertNotIn(301, match._squad(16)[:11])
        self.assertIn(312, match._squad(16)[:11])

    def test_empty_starter_is_replaced_by_marking_incoming_first(self):
        match, swaps, validations = self.make(empty=True)
        self.accepted(match)
        self.assertEqual(len(swaps), 2)
        self.assertTrue(validations)
        self.assertGreater(swaps[0], 11)
        self.assertLessEqual(swaps[1], 11)
        self.assertNotIn(0, match._squad(16)[:11])

    def test_reads_live_squad_after_original_sorts_between_swaps(self):
        match, swaps, validations = self.make(multiple=True)
        self.accepted(match)
        self.assertEqual(len(swaps), 6)
        self.assertTrue(validations)
        self.assertTrue({301, 302, 314}.isdisjoint(match._squad(16)[:11]))

    def test_falsifier_play_without_selection_is_refused_by_original(self):
        from unittest.mock import patch
        from original_match.match import MatchError
        match, swaps, validations = self.make()
        with patch("original_match.route_team.choose_eleven", return_value=[]):
            with self.assertRaisesRegex(MatchError, "ineligible player"):
                match.m.run(match.end_lin, 120, fresh=True)
        self.assertFalse(swaps)
        self.assertTrue(validations)


if __name__ == "__main__":
    unittest.main()
