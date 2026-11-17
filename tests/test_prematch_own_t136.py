"""T136/#722: native T/own overrides, private cells/records never printed."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match import screens as S
from original_match.match import Match,Fixture,MatchError,SITE_MENU,MENU_OWN,KEY,OWN_TACTICS,TACTICS
from original_match.image import Image,PLAYERS_PTR,PLAYER_SIZE
from original_match.machine import MEM_SIZE,REGS
from original_match.port.tables import from_record,to_record
from tests.test_route_sealed import _fixtures
from tests.test_prematch_roster_t134 import snapshot,decision
from port_test_runtime import call_in_pypy


def achieved(byte,element,want):
    has=bool(byte & (1 << (element+3)));value=bool(byte & (1 << (element-1)))
    return not has if want is None else has and value is want


def policy_class():
    from original_match.route_team import PreMatchPlan
    class ManualOwn(PreMatchPlan):
        observe_own_entry=observe_own=None
        def _own_select_key(self,s,job):
            word=job[1]
            if self.in_own:
                assert all(achieved(s['own_set'](word),e,v) for e,v in job[2].items())
                self.done.append(job);self.in_own=False;self._next_job()
                return self.select_key(s)
            pool=word not in s['squad']
            if self.pool_pane!=pool:
                self.pool_pane=pool;return S.LEFT
            if pool:here=s['pool_scroll']+s['pool_cursor'];target=s['pool'].index(word)+2
            else:here=s['cursor'];target=s['squad'].index(word)+1
            if here!=target:return S.DOWN if here<target else S.UP
            self.in_own=True;self.oracle_presses=0
            return ord('T')
        def own_key(self,row,own_set,marking_word,team_set,can_mark):
            for element,want in sorted(self.jobs[self.job][2].items()):
                if not achieved(own_set,element,want):
                    if row!=element:return S.DOWN if row<element else S.UP
                    self.oracle_presses+=1;assert self.oracle_presses<=15
                    return S.ENTER
            return S.ESC
    return ManualOwn


def prepare(image,tables,fixture,case):
    prepared=Image(image.memory_component());prepared.tables=tables
    if case=='bench_unavailable':
        managed=next(c for c in (fixture['first'],fixture['second']) if c in prepared.managed_countries())
        word=next(w for w in prepared.squad(managed)[11:] if prepared.players()[w][6]>=2)
        # Declared input variant before either machine is constructed, not a driver write.
        prepared.memory[prepared.far(PLAYERS_PTR)+PLAYER_SIZE*word+14]=0
    return prepared


def drive(m,case,oracle=False,replay=False):
    if oracle:
        factory=m._new_plan;Manual=policy_class()
        def plan(answer,context=None):
            if context!='pre_match':return factory(answer,context)
            p=Manual(m.side,tactics=answer.get('tactics'),subs=answer.get('substitutions'),
                     positions=answer.get('positions'),own=answer.get('own'))
            p.edit_only=bool(answer.get('edit_only'));return p
        m._new_plan=plan
    from dataclasses import asdict
    events=[];keys=[];entries=[];returns=[];rows=[]
    prior=m._key_for
    def key(site):
        if site==SITE_MENU:
            bp=m.m.reg('bp');caller=m.m.where(m.m.frame_word(bp,4),m.m.frame_word(bp,2))
            if caller==MENU_OWN:
                rows.append([entries[-1][0],m.m.rd(S.OWN_ROW),m.m.frame_word(bp,6)&255])
        value=prior(site)
        if value is not None:keys.append([site,value])
        return value
    m._key_for=key
    def entered(again):
        if not again:entries.append([m.m.stack_word(6),m.m.stack_word(4)&255,m.m.rd(KEY,1)])
    def returned(again):
        if not again:
            word=m.m.stack_word(-2)
            returns.append([word,m.m.stack_word(-4)&255,m._player(word,OWN_TACTICS),m.m.rd(KEY,1)])
    m.m.at('1771:4B61',entered);m.m.at('0791:E75D',returned)
    d=decision(m,events);budget=d['substitutions_left'];words=set(d['eleven']+d['bench']+d['pool'])
    group=d['eleven'] if case.startswith('xi') or case in ('all_rows','defaults','already_inherited') else d['bench'] if case.startswith('bench') else d['pool']
    if case=='no_input':jobs=[];word=None
    else:
        if case.endswith('keeper'):word=next(w for w in group if m._player(w,6)==0)
        elif case=='bench_unavailable':word=next(w for w in group if m._player(w,6)>=2 and not m._available(w))
        else:word=next(w for w in group if m._player(w,6)>=2)
        jobs=[{'own_tactics':{word:{1:v}}} for v in (False,True,None)]
        if case=='all_rows':jobs=[{'own_tactics':{word:goals}} for goals in
            ({1:False,2:True,3:False,4:True},{1:True,2:False,3:True,4:False},{e:None for e in range(1,5)})]
        elif case=='already_inherited':jobs.append({'own_tactics':{word:{1:None}}})
        elif case=='defaults':
            jobs=[]
            for default in (False,True):
                jobs.extend([{'tactics':{1:default},'own_tactics':{word:{1:True}}},
                             {'own_tactics':{word:{1:None}}}])
        elif case=='mixed':
            off=d['bench'][-1];on=next(w for w in d['pool'] if m._available(w))
            jobs=[{'substitutions':[[off,on]],'positions':{on:'club'},'tactics':{1:not bool(d['tactics']&1)},
                   'own_tactics':{off:{1:False,2:True},on:{3:True,4:False}}},
                  {'own_tactics':{off:{1:None,2:None},on:{3:None,4:None}}}]
    states=[]
    for job in jobs:
        at=len(events);visits=len(entries)
        m.answer(edit_only=True,**job);d=decision(m,events)
        assert len(entries)-visits==len(job['own_tactics'])
        assert len(returns)==len(entries)
        for player,goals in job['own_tactics'].items():
            byte=m._player(player,OWN_TACTICS)
            assert all(achieved(byte,e,v) for e,v in goals.items())
            for e,v in goals.items():
                if v is None:
                    country=m._player(player,0)
                    default=m.m.read(m._country(country)+TACTICS,1)[0]
                    assert bool(byte & (1 << (e-1)))==bool(default & (1 << (e-1)))
        assert not any(e['kind'] in ('tick','minute','substitution') for e in events[at:])
        assert d['substitutions_left']==budget
        states.append({'squad':d['eleven']+d['bench'],'pool':d['pool'],
                       'own':[[w,m._player(w,OWN_TACTICS)] for w in sorted(words)]})
    if case!='no_input':
        expected=4 if case in ('xi_keeper','pool_keeper','pool_cycle','bench_unavailable') else 5
        if case!='mixed':assert all(n==expected for w,_,n in rows if w==word)
    checks=0
    if replay and jobs:
        loaded=Match.load(m.save());assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
        assert all(loaded.m.reg(r)==m.m.reg(r) for r in REGS);checks+=1
    m.answer()
    for ev in m.events():
        events.append(asdict(ev))
        if ev.kind=='decision':raise AssertionError('unexpected stop before minute')
        if ev.kind=='minute':break
    assert ev.kind=='minute'
    if replay:
        loaded=Match.load(m.save());assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
        assert all(loaded.m.reg(r)==m.m.reg(r) for r in REGS);checks+=1
    base=m.m.far(PLAYERS_PTR)
    return dict(case=case,states=states,keys=keys,entries=entries,returns=returns,rows=rows,
                events=events,draws=m.st['draws'],records=[m.m.read(base+PLAYER_SIZE*w,PLAYER_SIZE) for w in sorted(words)],
                memory=m.m.read(0,MEM_SIZE),regs={r:m.m.reg(r) for r in REGS},replays=checks)


def candidate(state,tables,fixture,context,case,oracle=False):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True,record_draws=True,substitutions=2)
    return drive(m,case,oracle,replay=not oracle)


def guards(state,tables,fixture,context):
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True);d=decision(m,[]);word=d['eleven'][2];pool=d['pool'][0]
    cases=[{65535:{1:True}},{0:{1:True}},{word:{5:True}},{word:{0:False}},{word:{1:1}},
           {word:{True:False}},{word:{}},{word:[]},{word:{1:False},pool:{5:True}}]
    answers=[dict(own_tactics=v) for v in cases]+[
        dict(own_tactics={word:{1:True}},marking={word:65535}),
        dict(own_tactics={word:{1:True}},quick=True)]
    for fields in answers:
        before=snapshot(m)
        try:m.answer(edit_only=True,**fields)
        except ValueError:pass
        else:raise AssertionError('invalid own packet accepted')
        assert snapshot(m)==before
    before=snapshot(m)
    try:m.answer(own_tactics={word:{1:True}})
    except ValueError:pass
    else:raise AssertionError('plain Play own input ignored')
    assert snapshot(m)==before
    m.opts.pop('pre_match_edits');before=snapshot(m)
    try:m.answer(edit_only=True,own_tactics={word:{1:True}})
    except ValueError:pass
    else:raise AssertionError('unconfigured own input accepted')
    assert snapshot(m)==before;m.opts['pre_match_edits']=True
    m.st['waiting']['context']='half_time';before=snapshot(m)
    try:m.answer(own_tactics={pool:{1:True}})
    except ValueError:pass
    else:raise AssertionError('in-match own domain widened')
    assert snapshot(m)==before
    from original_match.route_team import PreMatchPlan
    s=dict(squad=list(range(1,21)),pool=list(range(101,181)),cursor=1,own_set=lambda w:0)
    p=PreMatchPlan(0,own={1:{1:None}});assert p.select_key(s)==ord('T')
    try:p.select_key(s)
    except MatchError:pass
    else:raise AssertionError('lost unchanged T visit acknowledged')
    for entry in ((2,1,ord('T'),0),(1,0,ord('T'),0),(1,1,ord('R'),0)):
        p=PreMatchPlan(0,own={1:{1:None}});p.select_key(s)
        try:p.observe_own_entry(*entry)
        except MatchError:pass
        else:raise AssertionError('wrong own entry accepted')
    for returned in ((2,1,0,27,0),(1,0,0,27,0),(1,1,16,27,0),(1,1,0,0,0),(1,1,0,27,1)):
        p=PreMatchPlan(0,own={1:{1:None}});p.select_key(s);p.observe_own_entry(1,1,ord('T'),16)
        try:p.observe_own(*returned)
        except MatchError:pass
        else:raise AssertionError('wrong own return accepted')
    return len(answers)+3+1+3+5


class OwnTactics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.context,cls.fixture=_fixtures().entry()
    def test_pure_invalid_packets_and_missing_wrong_visits(self):
        self.assertEqual(call_in_pypy('test_prematch_own_t136','guards',args=(
            self.image.state(self.image.tables),to_record(self.image.tables),self.fixture,self.context)),23)
    def test_independent_native_and_port_keys_equal_api_and_replay(self):
        for case in ('xi_cycle','xi_keeper','bench_cycle','bench_unavailable','pool_cycle','pool_keeper',
                     'all_rows','mixed','already_inherited','defaults','no_input'):
            with self.subTest(case=case):
                image=prepare(self.image,self.image.tables,self.fixture,case)
                m=Match(image,Fixture(**self.fixture),engine='original',tail=False,record_draws=True,substitutions=2)
                for r,v in self.context.items():m.m.set_reg(r,v)
                m.opts['pre_match_edits']=True
                native=drive(m,case,oracle=True)
                args=(image.state(image.tables),to_record(image.tables),self.fixture,self.context,case)
                actual=call_in_pypy('test_prematch_own_t136','candidate',args=args)
                manual=call_in_pypy('test_prematch_own_t136','candidate',args=args,kwargs={'oracle':True})
                for field in ('states','keys','entries','returns','rows','events','draws','records'):
                    self.assertTrue(actual[field]==native[field],case+': native '+field)
                    self.assertTrue(actual[field]==manual[field],case+': manual '+field)
                self.assertTrue(actual['memory']==manual['memory'],case+': full RAM')
                self.assertEqual(actual['regs'],manual['regs'])
                self.assertEqual(actual['replays'],1 if case=='no_input' else 2)
                print('T136_RECEIPT '+json.dumps(dict(case=case,input_sha256=image.sha256(),
                    entries=actual['entries'],returns=actual['returns'],rows=actual['rows'],keys=actual['keys'],
                    records_sha256=hashlib.sha256(b''.join(actual['records'])).hexdigest(),
                    memory_sha256=hashlib.sha256(actual['memory']).hexdigest(),all16=actual['regs'],
                    replays=actual['replays'],native_keys_records_events_draws_equal=True,
                    manual_full_memory_all16_equal=True,cross_backend_raw_identity_claimed=False),sort_keys=True),flush=True)


if __name__=='__main__':unittest.main()
