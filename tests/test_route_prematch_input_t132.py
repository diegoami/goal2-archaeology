"""T132 pre-match team input on the real held F1F6 Match; original assets remain private.

Surgical controls on the configuration, the published `pre_match` decision, answer()
legality and the installed plan; the original-backed driven proof (DEA6's own keys,
complete state) is T132's Done-when 2 and runs with the sealed fixtures. The pool arm
(#709's continuation): the made pool of F011, answer() pool exchanges and the driven
pool-to-squad swap through DEA6 with DBFA's gate asked.
"""
import sys
from pathlib import Path
import unittest
sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'runtime')]
from original_match.match import Match, Fixture, MatchError, PLAYER_POSITION
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
        pool_word = m._pool()[0]                            # [F011] a made-pool word rides the same jobs
        self.assertEqual(m._new_plan({'substitutions': [[eleven[10], pool_word]], 'edit_only': True},
                                     'pre_match').jobs, [('sub', eleven[10], pool_word)])
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

    def test_a_pool_word_is_a_legal_pre_match_incoming_and_only_there(self):
        m = self.match(True)
        off, pool_word = m._squad(m.opts['managed'])[10], m._pool()[0]
        m.answer(edit_only=True, substitutions=[[off, pool_word]])
        self.assertEqual(m.st['answer']['substitutions'], [[off, pool_word]])
        never_made = self.match(True)                       # [F011] only manager 1's block is made here:
        with self.assertRaises(ValueError):                 # manager 2's first word is neither bench nor pool
            never_made.answer(edit_only=True,
                              substitutions=[[never_made._squad(m.opts['managed'])[10], pool_word + 80]])
        unconfigured = self.match(False)
        with self.assertRaises(ValueError):
            unconfigured.answer(edit_only=True, substitutions=[[off, pool_word]])


class PoolReader(unittest.TestCase):
    """[F011] The entry holds the managed manager's made pool: eighty words 0xA01..0xA50
    (manager 1's block; the words past it are zero), position-sorted as 1771:5532 left it,
    disjoint from the squad's records. The screen's own state words (scroll +0x52, cursor
    +0x5E) are the plan's to drive, proven in Driven below."""

    @classmethod
    def setUpClass(cls):
        cls.image, cls.context, cls.fixture = _fixtures().entry()

    def match(self):
        return Match.from_route_entry(self.image, Fixture(**self.fixture), self.context)

    def test_the_entry_holds_the_managed_managers_made_pool(self):
        m = self.match()
        pool, squad = m._pool(), m._squad(m.opts['managed'])
        self.assertEqual(len(pool), 80)
        self.assertTrue(all(0xA01 <= w <= 0xA50 for w in pool))       # F011: manager 1's 2561..2640
        self.assertFalse(set(pool) & set(w for w in squad if w))      # records past the 2560 squad words

    def test_the_pool_is_position_sorted_as_sort_pool_left_it(self):
        m = self.match()
        positions = [m._player(w, PLAYER_POSITION) for w in m._pool()]
        self.assertEqual(positions, sorted(positions))                # F011: sorted ascending by +6, keepers first


class Driven(unittest.TestCase):
    """The real flow on the sealed entry: the original's own DEA6 makes the swap, the decision
    returns edited, and play kicks off. The original-backed Prover comparison of Done-when 2
    (complete state, ordered writes, the key sequence against the original run) stays with the
    heavy rig; this is the behavioural proof on the actual machine."""

    @classmethod
    def setUpClass(cls):
        cls.image, cls.context, cls.fixture = _fixtures().entry()

    def drive(self):
        m = Match.from_route_entry(self.image, Fixture(**self.fixture), self.context)
        m.configure_route_entry(pre_match_edits=True)
        for ev in m.events():
            if ev.kind == 'decision' and ev.data['context'] == 'pre_match':
                return m, ev.data
        raise AssertionError('no pre_match decision')

    def test_a_consumer_swap_is_made_by_the_original_and_play_kicks_off(self):
        m, first = self.drive()
        pos = dict((w, c) for w, c in first['positions'])
        off = first['eleven'][-1]
        on = next(w for w in first['bench'] if w and pos.get(w) == pos[off])
        # [T132 Done-when 2, at T124t's site-visit strength] Every swap the flow makes is the
        # original's own code: DEA6 is visited with the mark, EA09 validates, and each key the
        # plan presses goes through a real key read (captured by wrapping the plan's act).
        dea6, ea09, keys = [], [], []
        m.m.at('0791:DEA6', lambda replay: replay or dea6.append(m.m.rd(0x0C1B)))
        m.m.at('0791:EA09', lambda replay: replay or ea09.append(1))
        real_new_plan = Match._new_plan

        def logged_new_plan(match, answer, context=None):
            plan = real_new_plan(match, answer, context)
            act = plan.act
            plan.act = lambda key: (keys.append(key), act(key))[1]
            match._menu = plan
            return plan
        import unittest.mock as mock
        with mock.patch.object(Match, '_new_plan', logged_new_plan):
            m.answer(edit_only=True, substitutions=[[off, on]])
            second = None
            for ev in m.events():
                if ev.kind == 'decision':
                    second = ev.data
                    break
            self.assertEqual((second['context'], second.get('edited'), second.get('refused')),
                             ('pre_match', True, None))
            self.assertTrue(on in second['eleven'] and off not in second['eleven'])
            m.answer()                                          # play
            played = []
            for ev in m.events():
                played.append(ev.kind)
                if ev.kind == 'minute':
                    break
        self.assertIn('commentary', played)
        self.assertGreaterEqual(m.st['minute'], 1)
        self.assertEqual(m.st['log']['substitutions'], [])  # a line-up change, not a substitution event
        self.assertTrue(dea6, 'DEA6 was never visited: the swap was not the original\'s own')
        self.assertTrue(ea09, 'EA09 never validated the eleven')
        self.assertTrue(keys and all(0 <= k <= 255 for k in keys))

    def test_a_pool_exchange_is_made_by_the_original_and_play_kicks_off(self):
        m, first = self.drive()
        self.assertEqual(first.get('pool'), m._pool())      # the decision publishes the made pool
        pos = dict((w, c) for w, c in first['positions'])
        off = first['eleven'][-1]
        on = next(w for w in first['pool'] if m._player(w, PLAYER_POSITION) == pos[off])
        # [T132 pool arm, #709; T128's pool-to-squad case] The exchange is the original's own
        # code: the pane toggle (E6C7-E6D4) is a screen key, the pool-pane Enter asks DBFA before
        # DEA6 marks, the squad-pane Enter completes through DEA6, EA09 validates the eleven.
        dea6, dbfa, ea09, keys = [], [], [], []
        m.m.at('0791:DEA6', lambda replay: replay or dea6.append(m.m.rd(0x0C1B)))
        m.m.at('0791:DBFA', lambda replay: replay or dbfa.append(1))
        m.m.at('0791:EA09', lambda replay: replay or ea09.append(1))
        real_new_plan = Match._new_plan

        def logged_new_plan(match, answer, context=None):
            plan = real_new_plan(match, answer, context)
            act = plan.act
            plan.act = lambda key: (keys.append(key), act(key))[1]
            match._menu = plan
            return plan
        import unittest.mock as mock
        with mock.patch.object(Match, '_new_plan', logged_new_plan):
            m.answer(edit_only=True, substitutions=[[off, on]])
            second = None
            for ev in m.events():
                if ev.kind == 'decision':
                    second = ev.data
                    break
            self.assertEqual((second['context'], second.get('edited'), second.get('refused')),
                             ('pre_match', True, None))
            self.assertTrue(on in second['eleven'] and off not in second['eleven'])
            self.assertIn(off, second['pool'])              # the word-list exchange: the outgoing word sits in the pool
            self.assertNotIn(on, second['pool'])
            m.answer()                                          # play
            played = []
            for ev in m.events():
                played.append(ev.kind)
                if ev.kind == 'minute':
                    break
        self.assertIn('commentary', played)
        self.assertGreaterEqual(m.st['minute'], 1)
        self.assertEqual(m.st['log']['substitutions'], [])  # a line-up change, not a substitution event
        self.assertTrue(dea6, 'DEA6 was never visited: the exchange was not the original\'s own')
        self.assertTrue(dbfa, 'DBFA was never asked: the pool-pane Enter skipped the gate')
        self.assertTrue(ea09, 'EA09 never validated the eleven')
        self.assertTrue(keys and all(0 <= k <= 255 for k in keys))
        self.assertIn(0xAE, keys)                           # the pane toggle key, pressed both ways

    def test_chained_edits_continue_inside_the_select_screen(self):
        """[T132 continuation, found by goal2 T170m] An edit-only answer after a select-screen
        edit continues inside the screen (editing_select); the continuation must build the
        pre-match plan again, so a chained tactics -> swap -> pool-exchange flow makes every
        edit through the original's own route."""
        m, first = self.drive()
        pos = dict((w, c) for w, c in first['positions'])
        element, byte = 8, first['tactics']
        want = not bool(byte >> (element - 1) & 1)
        off = first['eleven'][-1]
        on = next(w for w in first['bench'] if w and pos.get(w) == pos[off])
        m.answer(edit_only=True, tactics={element: want})          # closes the menu: no select yet
        second = None
        for ev in m.events():
            if ev.kind == 'decision':
                second = ev.data
                break
        self.assertEqual(bool(second['tactics'] >> (element - 1) & 1), want)
        m.answer(edit_only=True, substitutions=[[off, on]])        # keeps SELECT TEAM open
        third = None
        for ev in m.events():
            if ev.kind == 'decision':
                third = ev.data
                break
        self.assertIn(on, third['eleven'])
        pool_off = third['eleven'][-1]                             # the continuation answer:
        pool_word = next(w for w in third['pool'] if m._player(w, PLAYER_POSITION) == pos[pool_off])
        m.answer(edit_only=True, substitutions=[[pool_off, pool_word]])
        fourth = None
        for ev in m.events():
            if ev.kind == 'decision':
                fourth = ev.data
                break
        self.assertEqual((fourth['context'], fourth.get('edited'), fourth.get('refused')),
                         ('pre_match', True, None))
        self.assertIn(pool_word, fourth['eleven'])
        self.assertNotIn(pool_off, fourth['eleven'])
        self.assertIn(pool_off, fourth['pool'])                    # the word-list exchange both ways
        self.assertNotIn(pool_word, fourth['pool'])
        m.answer()                                                # play
        for ev in m.events():
            if ev.kind == 'minute':
                break
        self.assertGreaterEqual(m.st['minute'], 1)
        self.assertEqual(m.st['log']['substitutions'], [])

    def test_a_tactics_toggle_is_made_by_the_original_editor_before_kick_off(self):
        m, first = self.drive()
        element, byte = 8, first['tactics']
        want = not bool(byte >> (element - 1) & 1)
        m.answer(edit_only=True, tactics={element: want})
        for ev in m.events():
            if ev.kind == 'decision':
                second = ev.data
                break
        self.assertEqual((second['context'], second.get('edited'), second.get('refused')),
                         ('pre_match', True, None))
        self.assertEqual(bool(second['tactics'] >> (element - 1) & 1), want)
        m.answer()                                          # play
        played = []
        for ev in m.events():
            played.append(ev.kind)
            if ev.kind == 'minute':
                break
        self.assertIn('commentary', played)

    def test_the_flush_guard_still_fails_an_unexplained_eleven_change_outside_pre_match(self):
        from original_match.machine import GuestError
        m, first = self.drive()
        squad = m._squad(m.opts['managed'])
        baseline = squad[:10] + [squad[11]]                 # one membership difference from the live eleven
        m.st['squads'][m.side] = baseline
        m.st['menu_context'] = 'pause'                      # not the pre-match menu: still refused
        with self.assertRaises(GuestError):
            m._flush()
        m2, _ = self.drive()                                # at the pre-match menu: the managed line-up
        squad2 = m2._squad(m2.opts['managed'])
        m2.st['squads'][m2.side] = squad2[:10] + [squad2[11]]
        m2.st['menu_context'] = 'pre_match'
        m2._flush()                                         # no GuestError: the baseline takes the line-up


if __name__ == '__main__':
    unittest.main()
