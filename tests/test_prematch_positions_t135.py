"""T135/#720: native R/C, independent key policy and replay; hashes only in receipts."""
import copy
import hashlib
import json
import sys
import unittest
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match import screens as S
from original_match.match import Match,Fixture,PLAYER_POSITION,MatchError
from original_match.image import Image,PLAYERS_PTR,PLAYER_SIZE
from original_match.machine import MEM_SIZE,REGS
from original_match.port.tables import from_record,to_record
from tests.test_route_sealed import _fixtures
from tests.test_prematch_roster_t134 import snapshot,decision
from port_test_runtime import call_in_pypy


def policy_class():
    from original_match.route_team import PreMatchPlan
    class ManualPositions(PreMatchPlan):
        # Independent position-key service: no production position driver or
        # return witness. Test hooks independently record actual4952 visits.
        observe_position=None
        observe_position_entry=None
        def _position_key(self,s,job):
            word,target=job[1:]
            in_pool=word not in s['squad']
            if self.pool_pane!=in_pool:
                self.pool_pane=in_pool
                return self.act(S.LEFT)
            if in_pool:
                here=s['pool_scroll']+s['pool_cursor'];want=s['pool'].index(word)+2
            else:here=s['cursor'];want=s['squad'].index(word)+1
            if here!=want:return S.DOWN if here<want else S.UP
            if target=='club':
                pending=getattr(self,'oracle_club',None)
                if pending is None:
                    self.oracle_club=(word,s['club_position'](word))
                    return ord('C')
                assert pending==(word,s['position'](word))
                self.oracle_club=None
            elif s['position'](word)!=target:
                self.presses+=1;assert self.presses<=14
                return ord('R')
            self.done.append(job);self._next_job()
            return self.select_key(s)
    return ManualPositions


def drive(m,case,oracle=False,replay=False):
    if oracle:
        factory=m._new_plan;Manual=policy_class()
        def plan(answer,context=None):
            if context!='pre_match':return factory(answer,context)
            p=Manual(m.side,tactics=answer.get('tactics'),subs=answer.get('substitutions'),
                     positions=answer.get('positions'))
            p.edit_only=bool(answer.get('edit_only'));return p
        m._new_plan=plan
    events=[];keys=[];visits=[];entries=[]
    previous=m._key_for
    def key(site):
        value=previous(site)
        if value is not None:keys.append([site,value])
        return value
    m._key_for=key
    def returned(again):
        if not again:
            word=m.m.stack_word(-2)
            visits.append([word,m._player(word,PLAYER_POSITION),m.m.rd(0xA976,1)])
    def entered(again):
        if not again:entries.append([m.m.stack_word(4),m.m.rd(0xA976,1)])
    m.m.at('1771:4952',entered);m.m.at('0791:E72A',returned)
    d=decision(m,events);budget=d['substitutions_left']
    all_words=set(d['eleven']+d['bench']+d['pool'])
    # Stable caller packet order across CPython/PyPy; a set is not an input policy.
    original={w:m._player(w,PLAYER_POSITION) for w in sorted(all_words)}
    if case=='no_input':jobs=[]
    else:
        domain=case.split('_')[0]
        word=(d['eleven'] if domain=='xi' else d['bench'] if domain=='bench' else d['pool'])[0]
        pos=m._player(word,PLAYER_POSITION);club=m._player(word,7)
        if 'club' in case:
            prep=club if case.endswith('equal') else (club+1)%14
            jobs=[{'positions':{word:prep}},{'positions':{word:'club'}}]
        elif case=='pool_wrap':jobs=[{'positions':{word:13}},{'positions':{word:0}}]
        elif case=='xi_same':jobs=[{'positions':{word:pos}}]
        elif case=='pool_mix':
            off=d['bench'][-1];on=next(w for w in d['pool'] if m._available(w))
            jobs=[{'substitutions':[[off,on]],'tactics':{8:not bool(d['tactics']&128)},
                   'positions':{off:(original[off]+1)%14,on:(original[on]+1)%14}}]
        else:jobs=[{'positions':{word:(pos+1)%14}}]
    states=[]
    for job in jobs:
        before=len(visits);at=len(events)
        m.answer(edit_only=True,**job);d=decision(m,events)
        for word,goal in job['positions'].items():
            assert m._player(word,PLAYER_POSITION)==(m._player(word,7) if goal=='club' else goal)
            if goal=='club':
                assert sum(v[0]==word and v[2]==ord('C') for v in visits[before:])==1
        assert d['substitutions_left']==budget
        assert not any(e['kind'] in ('tick','minute','substitution') for e in events[at:])
        states.append({'squad':d['eleven']+d['bench'],'pool':d['pool'],
                       'positions':[[w,m._player(w,PLAYER_POSITION),m._player(w,7)] for w in sorted(all_words)]})
    replay_checks=0
    if replay and jobs:
        loaded=Match.load(m.save())
        assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
        assert all(loaded.m.reg(r)==m.m.reg(r) for r in REGS);replay_checks+=1
    # Restore roles by real keys before Play; temporary wrap/club cases may
    # otherwise create an invalid XI. No guest-memory fixture patch is used.
    restore={w:p for w,p in original.items() if m._player(w,PLAYER_POSITION)!=p}
    if restore:
        m.answer(edit_only=True,positions=restore);d=decision(m,events)
    m.answer()
    for ev in m.events():
        events.append(asdict(ev))
        if ev.kind=='decision':raise AssertionError('unexpected decision before minute')
        if ev.kind=='minute':break
    assert ev.kind=='minute'
    if replay:
        loaded=Match.load(m.save())
        assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
        assert all(loaded.m.reg(r)==m.m.reg(r) for r in REGS);replay_checks+=1
    base=m.m.far(PLAYERS_PTR)
    records=[[w,m.m.read(base+PLAYER_SIZE*w,PLAYER_SIZE)] for w in sorted(all_words)]
    return dict(case=case,states=states,keys=keys,visits=visits,entries=entries,events=events,draws=m.st['draws'],
                records=records,memory=m.m.read(0,MEM_SIZE),regs={r:m.m.reg(r) for r in REGS},
                replay_checks=replay_checks)


def candidate(state,tables,fixture,context,case,oracle=False):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True,record_draws=True,substitutions=2)
    return drive(m,case,oracle,replay=not oracle)


def guards(state,tables,fixture,context):
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True)
    d=decision(m,[]);word=d['eleven'][0];pool=d['pool'][0]
    answers=[dict(positions={65535:3}),dict(positions={0:3}),dict(positions={word:14}),
             dict(positions={word:-1}),dict(positions={word:True}),dict(positions={word:'bad'}),
             dict(positions={word:3,65535:4}),dict(positions={word:2},own_tactics={word:{5:True}}),
             dict(positions={word:2},marking={word:0}),dict(positions={word:2},quick=True)]
    for answer in answers:
        before=snapshot(m)
        try:m.answer(edit_only=True,**answer)
        except ValueError:pass
        else:raise AssertionError('invalid pre-match input accepted')
        assert snapshot(m)==before
    for fields in (dict(positions={word:2}),dict(positions={word:'club'})):
        before=snapshot(m)
        try:m.answer(**fields)
        except ValueError:pass
        else:raise AssertionError('plain Play silently accepted position')
        assert snapshot(m)==before
    m.opts.pop('pre_match_edits');before=snapshot(m)
    try:m.answer(edit_only=True,positions={word:2})
    except ValueError:pass
    else:raise AssertionError('unconfigured position accepted')
    assert snapshot(m)==before
    m.opts['pre_match_edits']=True;m.st['waiting']['context']='half_time'
    for pos in ({word:'club'},{pool:2}):
        before=snapshot(m)
        try:m.answer(positions=pos)
        except ValueError:pass
        else:raise AssertionError('in-match rule widened')
        assert snapshot(m)==before
    from original_match.route_team import PreMatchPlan
    s=dict(squad=list(range(1,21)),pool=list(range(101,181)),cursor=1,
           position=lambda w:2,club_position=lambda w:2)
    p=PreMatchPlan(0,positions={1:'club'});assert p.select_key(s)==ord('C')
    try:p.select_key(s)
    except MatchError:pass
    else:raise AssertionError('lost already-equal C call acknowledged')
    for returned in ((2,2,ord('C')),(1,3,ord('C')),(1,2,0)):
        p=PreMatchPlan(0,positions={1:'club'});p.select_key(s);p.observe_position_entry(1,ord('C'))
        try:p.observe_position(*returned)
        except MatchError:pass
        else:raise AssertionError('wrong position return accepted')
    for entry in ((2,ord('C')),(1,ord('R'))):
        p=PreMatchPlan(0,positions={1:'club'});p.select_key(s)
        try:p.observe_position_entry(*entry)
        except MatchError:pass
        else:raise AssertionError('wrong position entry accepted')
    return len(answers)+2+1+2+4+2


class Positions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.context,cls.fixture=_fixtures().entry()

    def test_invalid_packets_and_position_witnesses(self):
        self.assertEqual(call_in_pypy('test_prematch_positions_t135','guards',args=(
            self.image.state(self.image.tables),to_record(self.image.tables),self.fixture,self.context)),21)

    def test_original_and_independent_port_policy_equal_api(self):
        for case in ('xi_next','bench_next','pool_next','xi_club','bench_club','pool_club',
                     'xi_club_equal','bench_club_equal','pool_club_equal','pool_wrap','xi_same','pool_mix','no_input'):
            with self.subTest(case=case):
                m=Match(self.image,Fixture(**self.fixture),engine='original',tail=False,
                        record_draws=True,substitutions=2)
                for r,v in self.context.items():m.m.set_reg(r,v)
                m.opts['pre_match_edits']=True  # reference key-policy declaration only
                native=drive(m,case,oracle=True)
                args=(self.image.state(self.image.tables),to_record(self.image.tables),self.fixture,self.context,case)
                actual=call_in_pypy('test_prematch_positions_t135','candidate',args=args)
                manual=call_in_pypy('test_prematch_positions_t135','candidate',args=args,kwargs={'oracle':True})
                for field in ('states','keys','visits','entries','events','draws','records'):
                    self.assertTrue(actual[field]==native[field],case+': native '+field)
                    self.assertTrue(actual[field]==manual[field],case+': manual '+field)
                self.assertTrue(actual['memory']==manual['memory'],case+': full port memory')
                self.assertEqual(actual['regs'],manual['regs'])
                self.assertEqual(actual['replay_checks'],1 if case=='no_input' else 2)
                print('T135_RECEIPT '+json.dumps(dict(case=case,states=actual['states'],
                    keys=actual['keys'],position_entries=actual['entries'],position_returns=actual['visits'],
                    records_sha256=hashlib.sha256(b''.join(v for _,v in actual['records'])).hexdigest(),
                    memory_sha256=hashlib.sha256(actual['memory']).hexdigest(),all16=actual['regs'],
                    original_keys_events_draws_records_equal=True,manual_full_memory_all16_equal=True,
                    replay_checks=actual['replay_checks'],source_entry_sha256=self.image.sha256(),
                    cross_backend_raw_identity_claimed=False),sort_keys=True),flush=True)


if __name__=='__main__':unittest.main()
