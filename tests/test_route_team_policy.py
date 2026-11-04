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


if __name__ == "__main__":
    unittest.main()
