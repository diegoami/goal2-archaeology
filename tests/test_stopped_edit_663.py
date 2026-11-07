"""[designed: #663, goal2#599] Synthetic coordinator states isolate stopped-menu control.
Actual original/port menu behavior is proved separately on the admitted E006 input.
"""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from original_match.match import Match, SITE_SELECT
from original_match import screens as S

class StoppedEdit(unittest.TestCase):
    def match(self, context='half_time', allowed=True):
        m = object.__new__(Match)
        m.side = 0
        m.opts = dict(managed=7, first=7, second=19)
        m.st = dict(waiting={'context': context}, answer=None, decisions=[], minute=45,
                    menu_context=context, notice=None, refused=None, pending_subs=[])
        m.m = SimpleNamespace(rd=lambda address, *args: int(allowed))
        m._squad = lambda country: list(range(101,121)) if country == 7 else list(range(201,221))
        m._replay_action = lambda *args: None
        m._extras = lambda answer: None
        m.closed = []
        m._close_plan = lambda plan: m.closed.append(plan)
        m.decisions = []
        m._decide = lambda context, **data: m.decisions.append((context,data))
        m._menu = None
        return m

    def test_answer_is_opt_in_and_legacy_shape_stays_unchanged(self):
        m=self.match()
        m.answer(substitutions=[(105,112)])
        self.assertNotIn('edit_only', m.st['answer'])
        m=self.match()
        m.answer(substitutions=[(105,112)], edit_only=True)
        self.assertTrue(m.st['answer']['edit_only'])
        self.assertIsNone(m.st['waiting'])

    def test_rejects_pause_and_disallowed_edits_before_consuming_decision(self):
        for context,allowed in [('pause',False),('half_time',False),('extra_time',True)]:
            m=self.match(context,allowed)
            with self.assertRaises(ValueError): m.answer(substitutions=[(105,112)], edit_only=True)
            self.assertIsNone(m.st['answer'])
            self.assertEqual(m.st['waiting']['context'],context)

        for changes in ({'substitutions': [(105,112)]}, {'positions': {105: 2}},
                        {'marking': {105: 201}}, {'own_tactics': {105: {1: True}}},
                        {'quick': True}, {'speed': 1}):
            m = self.match('pause', False)
            with self.assertRaises(ValueError):
                m.answer(tactics={5: True}, edit_only=True, **changes)
            self.assertEqual(m.st['waiting']['context'], 'pause')
            self.assertIsNone(m.st['answer'])

    def test_pause_accepts_tactics_only_without_enabling_substitutions(self):
        m = self.match('pause', False)
        m.answer(tactics={1: True, 8: False}, edit_only=True)
        self.assertIsNone(m.st['waiting'])
        self.assertEqual(m.st['answer']['tactics'], {1: True, 8: False})
        self.assertEqual(m.st['answer']['substitutions'], [])
        self.assertTrue(m.st['answer']['edit_only'])

    def test_pause_accepts_an_all_clear_tactics_byte(self):
        m = self.match('pause', False)
        m.answer(tactics=0, edit_only=True)
        self.assertEqual(m.st['answer']['tactics'], {e: False for e in range(1, 9)})

    def test_tactics_edit_returns_a_still_paused_decision_before_play(self):
        m = self.match('pause', False)
        m.answer(tactics={5: True}, edit_only=True)
        m._menu = m._new_plan(m.st['answer'])
        m._menu.in_screen = 'tactics'
        m._menu.menu_key = lambda item: self.fail('must not navigate to Play')
        self.assertIsNone(m._team_menu_key(0))
        self.assertEqual(m.decisions, [('pause', {'substitutions_now': False, 'requested': [], 'edited': True})])
        self.assertEqual(len(m.closed), 1)

    def test_finishing_select_returns_fresh_decision_without_play_key(self):
        m=self.match()
        plan=S.MenuPlan(0,subs=[(105,112)])
        plan.in_screen='select'
        plan.edit_only=True
        m._menu=plan
        self.assertIsNone(m._team_menu_key(plan.item('select')))
        self.assertEqual(plan.steps,['play'])
        self.assertEqual(m.closed,[plan])
        self.assertEqual(plan.menu_reads_after_play,0)
        self.assertEqual(m.decisions[0][0],'half_time')
        self.assertTrue(m.decisions[0][1]['edited'])

    def test_substitution_menu_reentry_consumes_new_answer_once(self):
        m=self.match('substitution')
        m.st['editing_menu']=True
        m.st['answer']={'substitutions':[(105,112)],'edit_only':True}
        m._new_plan=lambda answer: SimpleNamespace(steps=['play'],in_screen=None,
            menu_reads_after_play=0, edit_only=answer.get('edit_only'), closed=False,
            menu_key=lambda item: S.ENTER)
        self.assertIsNone(m._team_menu_key(0))
        self.assertIsNone(m.st['answer'])
        self.assertEqual(len(m.closed),1)
        self.assertEqual(len(m.decisions),1)

    def test_completed_pair_holds_select_without_escape_and_continue_does_not_repeat_it(self):
        m=self.match()
        m._menu=SimpleNamespace(edit_only=True,select_key=lambda state:S.ESC)
        self.assertIsNone(m._key_for(SITE_SELECT))
        self.assertTrue(m.st['editing_select'])
        self.assertEqual(len(m.closed),1)
        m.st['answer']={'substitutions':[]}
        m._new_plan=lambda answer: SimpleNamespace(edit_only=False,select_key=lambda state:S.ESC)
        self.assertEqual(m._key_for(SITE_SELECT),S.ESC)
        self.assertFalse(m.st['editing_select'])
        self.assertEqual(len(m.closed),1)
        self.assertIsNone(m.st['answer'])

if __name__ == '__main__': unittest.main()
