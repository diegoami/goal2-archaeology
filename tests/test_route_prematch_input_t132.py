"""T132 pre-match team input on the real held F1F6 Match; original assets remain private.

Surgical controls on the configuration, the published `pre_match` decision, answer()
legality and the installed plan; the original-backed driven proof (DEA6's own keys,
complete state) is T132's Done-when 2 and runs with the sealed fixtures.
"""
import sys
from pathlib import Path
import unittest
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'runtime')]
from original_match.match import Match, Fixture, MatchError
from original_match.route_team import PreMatchPlan
from tests.test_route_sealed import _fixtures


class Configuration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image, cls.context, cls.fixture = _fixtures().entry()

    def match(self):
        return Match.from_route_entry(self.image, Fixture(**self.fixture), self.context)

    def test_pre_match_edits_is_a_boolean_validated_atomically_like_the_other_flags(self):
        for value in (0, 1, None, 'yes', []):
            with self.subTest(value=value):
                m = self.match()
                with self.assertRaises(ValueError):
                    m.configure_route_entry(pre_match_edits=value)
                self.assertIsNone(m.opts.get('pre_match_edits'))
                m.configure_route_entry(pre_match_edits=True)
                self.assertIs(m.opts['pre_match_edits'], True)

    def test_default_configuration_stays_exactly_the_entry(self):
        m = self.match()
        before = (m.st.copy(), m.opts.copy())
        m.configure_route_entry()
        self.assertEqual((m.st, m.opts), before)
        self.assertIsNone(m.opts.get('pre_match_edits'))


class PreMatchMenu(unittest.TestCase):
    """The decision publication and plan installation inside _team_menu_key need the machine
    running (T127 found the same: _decide's flush validates pending writes); they are proven by
    T132's driven Done-when 2. Here: what a fresh entry can prove."""

    @classmethod
    def setUpClass(cls):
        cls.image, cls.context, cls.fixture = _fixtures().entry()

    def match(self, **config):
        m = Match.from_route_entry(self.image, Fixture(**self.fixture), self.context)
        m.configure_route_entry(**config)
        m.st['menu_context'] = 'pre_match'
        return m

    def test_unconfigured_pre_match_menu_plays_unseen_as_before(self):
        m = self.match()                                    # no pre_match_edits
        self.assertIsNotNone(m._team_menu_key(1))            # a key: the plain play plan, no decision
        self.assertEqual(m.st['decisions'], [])
        self.assertIsNone(m.st['waiting'])

    def test_new_plan_builds_the_original_dea6_plan_for_pre_match_answers(self):
        m = self.match(pre_match_edits=True)
        eleven, bench = m._squad(m.opts['managed'])[:11], m._squad(m.opts['managed'])[11:]
        plan = m._new_plan({'substitutions': [[eleven[10], bench[0]]], 'tactics': {8: True}, 'edit_only': True},
                           'pre_match')
        self.assertIsInstance(plan, PreMatchPlan)
        self.assertEqual(plan.jobs, [('sub', eleven[10], bench[0])])
        self.assertEqual(plan.steps, ['tactics', 'select', 'play'])
        self.assertIs(plan.edit_only, True)
        empty = m._new_plan({'substitutions': [], 'tactics': {}}, 'pre_match')
        self.assertEqual((empty.jobs, empty.steps), ([], ['play']))
        other = m._new_plan({'substitutions': [[eleven[10], bench[0]]]})
        self.assertNotIsInstance(other, PreMatchPlan)        # other menus keep MenuPlan unchanged

    def test_a_played_refusal_raises_on_unconfigured_entries(self):
        from types import SimpleNamespace
        m = self.match()
        m._menu = SimpleNamespace(steps=['play'], in_screen=None, menu_reads_after_play=1)
        m.st['message'] = 'TOO MANY KEEPERS'
        with self.assertRaises(MatchError):
            m._team_menu_key(1)


class AnswerLegality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image, cls.context, cls.fixture = _fixtures().entry()

    def match(self, configured):
        m = Match.from_route_entry(self.image, Fixture(**self.fixture), self.context)
        if configured:
            m.configure_route_entry(pre_match_edits=True)
        m.st['waiting'] = {'context': 'pre_match', 'eleven': m._squad(m.opts['managed'])[:11],
                           'bench': m._squad(m.opts['managed'])[11:]}
        return m

    def squad(self, m):
        s = m._squad(m.opts['managed'])
        return s[10], s[11]

    def test_edit_only_tactics_and_swaps_are_legal_on_a_configured_entry(self):
        for answer in ({'tactics': {8: True}}, {'substitutions': [list(self.squad(self.match(True)))]},
                       {'tactics': {1: False}, 'substitutions': [list(self.squad(self.match(True)))]}):
            with self.subTest(answer=answer):
                m = self.match(True)
                m.answer(edit_only=True, **answer)
                self.assertIs(m.st['answer']['edit_only'], True)

    def test_every_other_edit_and_every_unconfigured_edit_refuses(self):
        off, on = self.squad(self.match(True))
        cases = [{'tactics': {8: True}},                                          # unconfigured entry
                 {'positions': {off: 3}}, {'marking': {off: 0}}, {'own_tactics': {off: {1: True}}},  # not pre-match inputs
                 {'tactics': {8: True}, 'positions': {off: 3}},                   # mixed with a non-input
                 {}]                                                             # nothing to make
        for configured, answer in [(False, cases[0])] + [(True, c) for c in cases[1:]]:
            with self.subTest(configured=configured, answer=answer):
                m = self.match(configured)
                with self.assertRaises(ValueError):
                    m.answer(edit_only=True, **answer)
                self.assertIsNone(m.st.get('answer'))

    def test_a_plain_answer_plays_and_carries_the_generic_validations(self):
        m = self.match(True)
        m.answer()                                          # play on: no edit, no deferral
        self.assertNotIn('edit_only', m.st['answer'])
        bad = self.match(True)
        with self.assertRaises(ValueError):
            bad.answer(substitutions=[[12345, 54321]])      # the generic squad-membership rule


if __name__ == '__main__':
    unittest.main()
