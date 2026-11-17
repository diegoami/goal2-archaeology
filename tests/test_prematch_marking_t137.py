"""T137/#724: independent native/manual/API marking controls; raw bytes stay private."""
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match import screens as S
from original_match.match import Match,Fixture,MatchError,SITE_MENU,MENU_OWN,KEY,PLAYER_STATUS,OWN_TACTICS
from original_match.image import Image,PLAYERS_PTR,PLAYER_SIZE
from original_match.machine import MEM_SIZE,REGS
from original_match.port.tables import from_record,to_record
from tests.test_route_sealed import _fixtures
from tests.test_prematch_roster_t134 import snapshot,decision
from tests.test_prematch_own_t136 import policy_class as own_policy,achieved
from port_test_runtime import call_in_pypy


def reached(status,word,goal):
    return not (status & 64) if goal is None else bool(status & 64) and word==goal


def policy_class():
    class ManualMark(own_policy()):
        observe_mark_entry=observe_mark_return=observe_mark_visit=None
        def __init__(self,*args,**kwargs):
            self.manual_marks=dict(kwargs.get('marking') or {})
            super().__init__(*args,**kwargs)
        def observe_mark_state(self,status):self.manual_status=status
        def own_key(self,row,own_set,marking_word,team_set,can_mark):
            job=self.jobs[self.job]
            for element,goal in sorted(job[2].items()):
                if not achieved(own_set,element,goal):
                    if row!=element:return S.DOWN if row<element else S.UP
                    return S.ENTER
            if job[1] in self.manual_marks and not reached(self.manual_status,marking_word,self.manual_marks[job[1]]):
                assert can_mark
                if row!=5:return S.DOWN if row<5 else S.UP
                self.oracle_presses+=1;assert self.oracle_presses<=13
                return S.ENTER
            return S.ESC
    return ManualMark


def mark_word(m,word):
    slot=m._squad(m.opts['managed']).index(word)+1
    return m.m.rd(S.MARKING-2+40*m.side+2*slot)


def prepare(image,tables,fixture,case):
    variant=Image(image.memory_component());variant.tables=tables
    managed=next(c for c in (fixture['first'],fixture['second']) if c in variant.managed_countries())
    if case=='unavailable':
        word=next(w for w in variant.squad(managed)[11:] if variant.players()[w][6]>=2)
        variant.memory[variant.far(PLAYERS_PTR)+PLAYER_SIZE*word+14]=0
    if case=='target_skip':
        # Exhaust available reserves so native opponent selection retains one
        # unavailable XI word; guard/cycle assertions use its observed identity.
        other=fixture['second'] if managed==fixture['first'] else fixture['first']
        for word in variant.squad(other)[1:2]+variant.squad(other)[11:]:
            variant.memory[variant.far(PLAYERS_PTR)+PLAYER_SIZE*word+14]=0
    return variant


def drive(m,case,oracle=False,replay=False):
    if oracle:
        factory=m._new_plan;Manual=policy_class()
        def plan(answer,context=None):
            if context!='pre_match':return factory(answer,context)
            p=Manual(m.side,tactics=answer.get('tactics'),subs=answer.get('substitutions'),
                     positions=answer.get('positions'),own=answer.get('own'),marking=answer.get('marking'))
            p.edit_only=bool(answer.get('edit_only'));return p
        m._new_plan=plan
    from dataclasses import asdict
    events=[];keys=[];entries=[];returns=[];calls=[];called=[];results=[];rows=[]
    prior=m._key_for
    def key(site):
        if site==SITE_MENU:
            bp=m.m.reg('bp');caller=m.m.where(m.m.frame_word(bp,4),m.m.frame_word(bp,2))
            if caller==MENU_OWN:rows.append([entries[-1][0],m.m.rd(S.OWN_ROW),m.m.frame_word(bp,6)&255])
        value=prior(site)
        if value is not None:keys.append([site,value])
        return value
    m._key_for=key
    def entered(again):
        if not again:entries.append([m.m.stack_word(6),m.m.stack_word(4)&255])
    def returned(again):
        if not again:returns.append([m.m.stack_word(-2),m.m.stack_word(-4)&255])
    def marking(again):
        if not again:
            bp=m.m.stack_word(2);calls.append([m.m.frame_word(bp,8),m.m.frame_word(bp,6)&255,m.m.rd(S.OWN_ROW)])
    def marked(again):
        if not again:
            bp=m.m.reg('bp');player=m.m.frame_word(bp,8)
            called.append([player,m.m.frame_word(bp,6)&255,m.m.rd(S.OWN_ROW)])
            results.append([player,m._player(player,PLAYER_STATUS),mark_word(m,player)])
    m.m.at('1771:4B61',entered);m.m.at('0791:E75D',returned)
    m.m.at('1771:49B8',marking);m.m.at('1771:4C2B',marked)
    d=decision(m,events);budget=d['substitutions_left']
    squad=d['eleven']+d['bench'];other=m._squad(m.opts['second'] if m.opts['managed']==m.opts['first'] else m.opts['first'])
    words=sorted(set(squad+d['pool']+other));out=lambda group:next(w for w in group if m._player(w,6)>=2 and m._available(w))
    targets=[w for w in other[1:11] if w and m._available(w)]
    word=out(d['bench'] if case=='bench' else d['eleven'])
    goals=[0,targets[-1],None]
    jobs=[{'marking':{word:v}} for v in goals]
    if case=='already_met':jobs=[{'marking':{word:v}} for v in (None,None,0,0,targets[-1],targets[-1],None,None)]
    if case=='multi':jobs=[{'marking':{word:targets[-1],out(d['bench']):targets[0]}},{'marking':{word:None,out(d['bench']):0}}]
    if case=='target_skip':jobs=[{'marking':{word:targets[-1]}},{'marking':{word:None}}]
    if case=='mixed':
        off=out(d['bench']);on=out(d['pool']);word=on
        jobs=[{'substitutions':[[off,on]],'positions':{on:2},'tactics':{1:not bool(d['tactics']&1)},
               'own_tactics':{on:{1:False,2:True}},'marking':{on:targets[-1]}},
              {'own_tactics':{on:{1:None,2:None}},'marking':{on:None}}]
    if case in ('keeper','pool','unavailable'):
        word=(next(w for w in d['eleven'] if m._player(w,6)==0) if case=='keeper' else out(d['pool'])
              if case=='pool' else next(w for w in d['bench'] if m._player(w,6)>=2 and not m._available(w)))
        jobs=[{'own_tactics':{word:{1:True}}}]
    if case=='no_input':jobs=[]
    if case in ('keeper','pool','unavailable','target_skip'):
        badword=word;badtarget=next(w for w in other[1:11] if not m._available(w)) if case=='target_skip' else 0
        before=snapshot(m)
        try:m.answer(edit_only=True,marking={badword:badtarget})
        except ValueError:pass
        else:raise AssertionError('ineligible native marking request accepted')
        assert snapshot(m)==before
    states=[]
    for job in jobs:
        at=len(events);visits=len(entries);m.answer(edit_only=True,**job);d=decision(m,events)
        assert len(entries)>visits and len(entries)==len(returns)
        assert calls==called
        for w,goal in job.get('marking',{}).items():assert reached(m._player(w,PLAYER_STATUS),mark_word(m,w),goal)
        for w,goals in job.get('own_tactics',{}).items():assert all(achieved(m._player(w,OWN_TACTICS),e,v) for e,v in goals.items())
        assert not any(e['kind'] in ('minute','tick','substitution') for e in events[at:])
        assert d['substitutions_left']==budget
        states.append(dict(squad=d['eleven']+d['bench'],pool=d['pool'],marks=m.m.read(m.m.DS*16+S.MARKING,80),
                           status=[[w,m._player(w,PLAYER_STATUS)] for w in words]))
    if case=='target_skip':
        assert all(target!=badtarget for player,status,target in results) and len(calls)==len(targets)+2
    if case in ('keeper','pool','unavailable'):assert all(n==4 for w,r,n in rows if w==word) and not calls
    elif case!='no_input':assert all(n==5 for w,r,n in rows if w==word) and calls
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
    return dict(case=case,states=states,keys=keys,entries=entries,returns=returns,calls=calls,called=called,results=results,rows=rows,
                events=events,draws=m.st['draws'],records=[m.m.read(base+PLAYER_SIZE*w,PLAYER_SIZE) for w in words],
                countries=[m.m.read(m._country(c),191) for c in (m.opts['first'],m.opts['second'])],
                memory=m.m.read(0,MEM_SIZE),regs={r:m.m.reg(r) for r in REGS},replays=checks)


def candidate(state,tables,fixture,context,case,oracle=False):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True,record_draws=True,substitutions=2)
    return drive(m,case,oracle,replay=not oracle)


class Marking(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.context,cls.fixture=_fixtures().entry()
    def test_independent_native_and_port_keys_equal_api_and_replay(self):
        for case in ('xi','bench','already_met','mixed','multi','target_skip','keeper','pool','unavailable','no_input'):
            with self.subTest(case=case):
                image=prepare(self.image,self.image.tables,self.fixture,case)
                m=Match(image,Fixture(**self.fixture),engine='original',tail=False,record_draws=True,substitutions=2)
                for r,v in self.context.items():m.m.set_reg(r,v)
                m.opts['pre_match_edits']=True
                native=drive(m,case,oracle=True)
                args=(image.state(image.tables),to_record(image.tables),self.fixture,self.context,case)
                actual=call_in_pypy('test_prematch_marking_t137','candidate',args=args)
                manual=call_in_pypy('test_prematch_marking_t137','candidate',args=args,kwargs={'oracle':True})
                for field in ('states','keys','entries','returns','calls','called','results','rows','events','draws','records','countries'):
                    self.assertTrue(actual[field]==native[field],case+': native '+field)
                    self.assertTrue(actual[field]==manual[field],case+': manual '+field)
                self.assertTrue(actual['memory']==manual['memory'],case+': full RAM');self.assertEqual(actual['regs'],manual['regs'])
                self.assertEqual(actual['replays'],1 if case=='no_input' else 2)
                print('T137_RECEIPT '+json.dumps(dict(case=case,input_sha256=image.sha256(),entries=actual['entries'],
                    calls=actual['calls'],rows=actual['rows'],keys=actual['keys'],
                    records_sha256=hashlib.sha256(b''.join(actual['records']+actual['countries'])).hexdigest(),
                    memory_sha256=hashlib.sha256(actual['memory']).hexdigest(),all16=actual['regs'],
                    replays=actual['replays'],native_keys_records_events_draws_equal=True,
                    manual_full_memory_all16_equal=True,cross_backend_raw_identity_claimed=False),sort_keys=True),flush=True)


def guards(state,tables,fixture,context):
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True);d=decision(m,[])
    word=next(w for w in d['bench'] if m._available(w) and m._player(w,6)>=2)
    other=m._squad(m.opts['second'] if m.opts['managed']==m.opts['first'] else m.opts['first'])
    keeper=next(w for w in d['eleven'] if m._player(w,6)==0);pool=d['pool'][0]
    cases=[{65535:0},{0:None},{True:0},{'bad':0},{word:True},{word:False},{word:-1},
           {word:'0'},{word:65535},{word:other[0]},{word:other[11]},{word:word},{keeper:None},{pool:0}]
    answers=[dict(marking=x) for x in cases]+[dict(marking=[]),
             dict(marking={word:0},positions={word:0}),
             dict(marking={word:0},positions={word:1}),
             dict(marking={word:0},substitutions=[[word,pool]]),
             dict(marking={word:0},positions={word:14}),
             dict(marking={word:0},own_tactics={word:{5:True}}),
             dict(marking={word:0},quick=True)]
    for fields in answers:
        before=snapshot(m)
        try:m.answer(edit_only=True,**fields)
        except ValueError:pass
        else:raise AssertionError('invalid marking packet accepted')
        assert snapshot(m)==before
    before=snapshot(m)
    try:m.answer(marking={word:None})
    except ValueError:pass
    else:raise AssertionError('plain Play marking ignored')
    assert snapshot(m)==before
    m.opts.pop('pre_match_edits');before=snapshot(m)
    try:m.answer(edit_only=True,marking={word:0})
    except ValueError:pass
    else:raise AssertionError('unconfigured marking accepted')
    assert snapshot(m)==before;m.opts['pre_match_edits']=True
    # A legal exchange changes the public domain; the old word cannot mark from pool.
    incoming=next(w for w in d['pool'] if m._available(w) and m._player(w,6)>=2)
    m.answer(edit_only=True,substitutions=[[word,incoming]]);decision(m,[])
    before=snapshot(m)
    try:m.answer(edit_only=True,marking={word:0})
    except ValueError:pass
    else:raise AssertionError('stale pool word marking accepted')
    assert snapshot(m)==before
    m.st['waiting']['context']='half_time';before=snapshot(m)
    try:m.answer(marking={incoming:0})
    except ValueError:pass
    else:raise AssertionError('in-match XI-only marking domain widened')
    assert snapshot(m)==before;m.st['waiting']['context']='pre_match'
    m.answer(edit_only=True,marking={incoming:0});decision(m,[])
    assert reached(m._player(incoming,PLAYER_STATUS),mark_word(m,incoming),0)
    from original_match.route_team import PreMatchPlan
    screen=dict(squad=list(range(1,21)),pool=list(range(101,181)),cursor=1,own_set=lambda w:0)
    def plan():
        p=PreMatchPlan(0,marking={1:0});assert p.select_key(screen)==ord('T')
        p.observe_own_entry(1,1,ord('T'),0);p.observe_mark_state(0)
        assert p.own_key(5,0,0,0,True)==S.ENTER
        return p
    count=len(answers)+4
    for args in ((2,1,13,5),(1,0,13,5),(1,1,27,5),(1,1,13,4)):
        p=plan()
        try:p.observe_mark_entry(*args)
        except MatchError:pass
        else:raise AssertionError('wrong row5 entry accepted')
        count+=1
    for args in ((2,1,13,5),(1,0,13,5),(1,1,27,5),(1,1,13,4)):
        p=plan();p.observe_mark_entry(1,1,13,5)
        try:p.observe_mark_return(*args)
        except MatchError:pass
        else:raise AssertionError('wrong row5 return accepted')
        count+=1
    for missing in ('entry','return','own_return','goal'):
        p=plan()
        if missing!='entry':p.observe_mark_entry(1,1,13,5)
        if missing not in ('entry','return'):p.observe_mark_return(1,1,13,5)
        if missing!='own_return':p.observe_own(1,1,0,27,0)
        try:p.observe_mark_visit(1,0 if missing=='goal' else 64,0)
        except MatchError:pass
        else:raise AssertionError('lost marking witness or goal acknowledged')
        count+=1
    # Actual driver mutation: native goal bytes alone cannot replace the call witness.
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True);d=decision(m,[])
    word=next(w for w in d['eleven'] if m._available(w) and m._player(w,6)>=2)
    factory=m._new_plan
    def missing_return(answer,context=None):
        p=factory(answer,context)
        if context=='pre_match':p.observe_mark_return=lambda *args:None
        return p
    m._new_plan=missing_return;m.answer(edit_only=True,marking={word:0})
    try:decision(m,[])
    except MatchError:pass
    else:raise AssertionError('actual missing row5 return acknowledged')
    return count+1


class Guards(unittest.TestCase):
    def test_refusals_stale_repair_and_real_missing_return(self):
        image,context,fixture=_fixtures().entry()
        self.assertEqual(call_in_pypy('test_prematch_marking_t137','guards',args=(
            image.state(image.tables),to_record(image.tables),fixture,context)),38)


if __name__=='__main__':unittest.main()
