"""T127 supported configuration of the real held F1F6 Match; original assets remain private."""
import copy
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'runtime')]
from original_match.match import Match,Fixture,SEED
from original_match.machine import MEM_SIZE,REGS
from tests.test_route_sealed import _fixtures


def snapshot(m):
    return (m.m.read(0,MEM_SIZE),tuple(m.m.reg(k) for k in REGS),copy.deepcopy(m.opts),
            copy.deepcopy(m.st),copy.deepcopy(m.inputs),
            {a:len(v) for a,v in m.m._handlers.items()},len(m.m._writes))


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image,cls.context,cls.fixture=_fixtures().entry()

    def match(self):
        return Match.from_route_entry(self.image,Fixture(**self.fixture),self.context)

    def test_all_default_configuration_preserves_entry_and_options(self):
        m=self.match();before=snapshot(m)
        self.assertIsNone(m.configure_route_entry())
        self.assertEqual(snapshot(m),before)
        with self.assertRaises(ValueError):m.configure_route_entry()
        self.assertEqual(snapshot(m),before)

    def test_boolean_validation_is_atomic_and_failure_does_not_consume(self):
        for field in ('ticks','record_draws','set_piece','live_players','substitution_control'):
            for value in (0,1,None,'yes',[]):
                with self.subTest(field=field,value=value):
                    m=self.match();before=snapshot(m)
                    with self.assertRaises(ValueError):m.configure_route_entry(**{field:value,'captain':m._squad(m.opts['managed'])[0]})
                    self.assertEqual(snapshot(m),before)
                    m.configure_route_entry()

    def test_captain_and_budget_validation_precedes_every_change(self):
        invalid=[{'captain':v} for v in (True,0,-1,3061,self.match()._squad(self.fixture['first'])[11])]
        invalid += [{'substitutions':v} for v in (True,-1,256,[],[1],[1,2,3],[True,2],[0,256],'5')]
        for options in invalid:
            with self.subTest(options=options):
                m=self.match();before=snapshot(m)
                with self.assertRaises(ValueError):m.configure_route_entry(ticks=True,record_draws=True,**options)
                self.assertEqual(snapshot(m),before);m.configure_route_entry()

    def test_options_detach_budget_and_preserve_complete_incoming_context(self):
        for budget in (0,255,[0,255],(5,5),None):
            m=self.match();before=snapshot(m);captain=m._squad(m.opts['managed'])[0]
            m.configure_route_entry(captain=captain,substitutions=budget,ticks=True,set_piece=True,
                                    live_players=True,substitution_control=True)
            after=snapshot(m)
            self.assertEqual(after[:2],before[:2]);self.assertEqual(after[3:],before[3:])
            self.assertEqual(m.opts['substitutions'],[budget,budget] if type(budget)is int else list(budget) if budget is not None else None)
            if isinstance(budget,list):budget[0]=7;self.assertEqual(m.opts['substitutions'],[0,255])
            self.assertEqual(m.opts['captain'],captain)
            for field in ('ticks','set_piece','live_players','substitution_control'):self.assertIs(m.opts[field],True)
            configured=snapshot(m)
            with self.assertRaises(ValueError):m.configure_route_entry(record_draws=True)
            self.assertEqual(snapshot(m),configured)

    def test_draw_recorder_is_installed_once_without_reinstalling_hooks(self):
        m=self.match();before=snapshot(m)
        with patch.object(m,'_hooks',side_effect=AssertionError('hooks rerun')):
            m.configure_route_entry(record_draws=True)
        after=snapshot(m);self.assertEqual(after[:2],before[:2]);self.assertEqual(after[3:6],before[3:6])
        self.assertEqual(after[6],before[6]+1)
        m.st['recording']=True;old=m.m.rd(SEED);m.m.write_as(m.m.DS*16+SEED,2,(old+1)&65535,m.m.pc())
        self.assertEqual(len(m.st['draws']),1)
        self.assertEqual(m.st['draws'][0][2:],[old,(old+1)&65535])

    def test_lazy_events_creation_allows_configuration_but_replay_capture_locks_it(self):
        a=self.match();b=self.match();iterator=b.events()
        self.assertEqual(snapshot(a),snapshot(b))
        a.configure_route_entry(ticks=True);b.configure_route_entry(ticks=True)
        self.assertEqual(snapshot(a),snapshot(b));iterator.close()
        c=self.match();c._replay_start();before=snapshot(c)
        with self.assertRaises(ValueError):c.configure_route_entry(ticks=True)
        self.assertEqual(snapshot(c),before)

    def test_unknown_and_setup_options_are_rejected_without_consumption(self):
        for key in ('seed','reference_seed','delay_byte','players','countries','managed','fixture','index','engine','tail','ports','prove','opts'):
            m=self.match();before=snapshot(m)
            with self.assertRaises(TypeError):m.configure_route_entry(**{key:True})
            self.assertEqual(snapshot(m),before);m.configure_route_entry()

    def test_ordinary_loaded_and_changed_entry_targets_refuse_without_changes(self):
        ordinary=Match(self.image,Fixture(**self.fixture),engine='port',tail=False)
        loaded=Match.load(self.match().save())
        moved=self.match();moved.m.set_reg('eax',moved.m.reg('eax')^1)
        for m in (ordinary,loaded,moved):
            before=snapshot(m)
            with self.assertRaises(ValueError):m.configure_route_entry()
            self.assertEqual(snapshot(m),before)
