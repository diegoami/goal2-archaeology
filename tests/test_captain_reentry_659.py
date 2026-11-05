"""[derived: #659/goal2#593] Kickoff overrides are not later captain choices.

These are declared synthetic coordinator-control states, not original-match evidence.
The live report has the withdrawn captain at squad slot14 and the guest highlight at3.
"""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from original_match.match import Match
from original_match import screens as S


class CaptainReentry(unittest.TestCase):
    def match(self, kickoff=None):
        match = object.__new__(Match)
        machine = SimpleNamespace(DS=0x1000, cursor=5, seed=0)
        machine.stack_word = lambda offset: {0: 0xCED9, 2: 1, 4: 0}[offset]
        machine.reg = lambda register: 0x100
        machine.frame_word = lambda bp, offset: machine.cursor
        machine.far = lambda pointer: 0x30000
        machine.rd = lambda address: machine.seed
        match.m = machine
        match.side = 0
        match.opts = dict(managed=7, captain=105, seed=0, delay_byte=0, set_piece=True)
        match.st = dict(prompt=None, kickoff_seed=kickoff, recording=kickoff is not None, answer=None)
        match.squad = list(range(101, 121))
        match._squad = lambda country: match.squad
        match.declarations = []
        match._declare = lambda *args: match.declarations.append(args)
        return match

    def test_initial_explicit_captain_is_still_selected(self):
        match = self.match()
        match.m.cursor = 3
        match._on_prompt(False)
        self.assertEqual(match._captain_key(), S.DOWN)
        match.m.cursor = 5
        self.assertEqual(match._captain_key(), S.ENTER)
        self.assertIsNone(match.st['prompt'])

    def test_withdrawn_captain_is_not_forced_from_bench_slot_fourteen(self):
        match = self.match(kickoff=0)
        match.squad[4], match.squad[13] = match.squad[13], match.squad[4]
        match.m.cursor = 3
        match._on_prompt(False)
        self.assertEqual(match._captain_key(), S.ENTER)
        self.assertIsNone(match.st['prompt'])

    def test_later_captain_choice_uses_the_guests_eligible_default(self):
        match = self.match(kickoff=123)
        match.m.cursor = 3
        match._on_prompt(False)
        self.assertEqual(match._captain_key(), S.ENTER)

    def test_zero_kickoff_seed_and_delay_are_not_reapplied_later(self):
        match = self.match()
        match._on_prompt(False)
        match._on_wait(False)
        self.assertEqual(len(match.declarations), 2)
        self.assertEqual(match.st['kickoff_seed'], 0)
        self.assertTrue(match.st['recording'])
        self.assertEqual(match._captain_key(), S.ENTER)
        match.declarations.clear()
        match.m.seed = 999
        match._on_prompt(False)
        match._on_wait(False)
        self.assertEqual(match.declarations, [])
        self.assertEqual(match.st['kickoff_seed'], 0)
        self.assertTrue(match.st['recording'])

    def test_set_piece_target_selection_is_preserved(self):
        match = self.match(kickoff=0)
        match.st['prompt'] = dict(role=2, target=106, waited=True)
        match.m.cursor = 3
        self.assertEqual(match._captain_key(), S.DOWN)
        match.m.cursor = 6
        self.assertEqual(match._captain_key(), S.ENTER)


if __name__ == '__main__':
    unittest.main()
