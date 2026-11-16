"""T134/#717: DEA6 word swaps, native re-sort and public full-roster inputs.

Original bytes remain private. Cross-backend first-minute raw identity is not
claimed (T80 representation/#709); exact native word lists/keys/events/draws are.
"""
import copy
import hashlib
import json
import sys
import unittest
from collections import Counter
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match.match import Match,Fixture,PLAYER_POSITION,MatchError
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS
from original_match.port.tables import from_record,to_record
from tests.test_route_sealed import _fixtures
from port_test_runtime import call_in_pypy


def snapshot(m):
    return (m.m.read(0,MEM_SIZE),{r:m.m.reg(r) for r in REGS},copy.deepcopy(m.opts),
            copy.deepcopy(m.st),copy.deepcopy(m._queue),copy.deepcopy(getattr(m,'_replay_actions',None)),
            copy.deepcopy(m._frame_state()))


def decision(m,events):
    for ev in m.events():
        events.append(asdict(ev))
        if ev.kind=='decision':
            assert ev.data['context']=='pre_match'
            return ev.data
    raise AssertionError('pre_match decision missing')


def wanted(m,d,case):
    xi,bench,pool=d['eleven'],d['bench'],d['pool']
    pos=lambda w:m._player(w,PLAYER_POSITION)
    if case=='starter_same':
        return [[a,b] for i,a in enumerate(xi) for b in xi[i+1:] if pos(a)==pos(b)][:1]
    if case=='starter_different':return [[xi[0],next(w for w in xi[1:] if pos(w)!=pos(xi[0]))]]
    if case.startswith('bench_pool') or case=='batch':
        off=bench[0]
        on=next(w for w in pool if m._available(w) and ((pos(w)!=pos(off)) if case.endswith('different') else pos(w)==pos(off)))
        if case=='batch':
            starter=next(w for w in xi if pos(w)==pos(off))
            return [[off,on],[on,starter],[starter,off]]
        return [[off,on]]
    if case=='reversed':
        off=bench[0];return [[off,next(w for w in xi if pos(w)==pos(off))]]
    off=xi[-1]
    if case=='xi_bench':return [[off,next(w for w in bench if pos(w)==pos(off))]]
    if case=='xi_pool':return [[off,next(w for w in pool if pos(w)==pos(off) and m._available(w))]]
    raise AssertionError(case)


def raw_swap(squad,pool,pair):
    a,b=pair;squad=list(squad);pool=list(pool);i=squad.index(a)
    if b in squad:
        j=squad.index(b);squad[i],squad[j]=squad[j],squad[i]
    else:
        j=pool.index(b);squad[i],pool[j]=pool[j],squad[i]
    return squad,[w for w in pool if w]


def drive(m,case,replay=False):
    events,keys,swaps=[],[],[];before=[None];pairs=[]
    previous=m._key_for
    def key(site):
        v=previous(site)
        if v is not None:keys.append([site,v])
        return v
    m._key_for=key
    def dea6(again):
        if again:return
        # [confirmed: F031/T128 caller frame] DEA6's near argument is the
        # SELECT frame pointer, whose byte -1 is the already-marked flag.
        parent=m.m.stack_word(2)
        if m.m.read(m.m.reg('ss')*16+parent-1,1)[0]:
            before[0]=(m._squad(m.opts['managed']),m._pool())
    def swapped(again):
        if again:return
        assert before[0] is not None and len(swaps)<len(pairs)
        expected=raw_swap(*before[0],pairs[len(swaps)])
        now=(m._squad(m.opts['managed']),m._pool())
        assert now==expected,'native word swap differs from requested pair'
        swaps.append(dict(pair=pairs[len(swaps)],before_squad=before[0][0],
                          after_raw_squad=now[0],after_raw_pool=now[1]))
        before[0]=None
    m.m.at('0791:DEA6',dea6);m.m.at('0791:DF29',swapped)
    d=decision(m,events);initial=copy.deepcopy(d);pairs[:]=wanted(m,d,case);assert pairs
    budget=d['substitutions_left'];at=len(events)
    m.answer(edit_only=True,substitutions=pairs)
    d=decision(m,events)
    assert len(swaps)==len(pairs),'missing original word-swap visit'
    last=swaps[-1]
    assert Counter(d['eleven'])==Counter(last['after_raw_squad'][:11])
    assert Counter(d['bench'])==Counter(last['after_raw_squad'][11:])
    assert d['pool']==last['after_raw_pool']
    assert d['substitutions_left']==budget
    assert not any(e['kind'] in ('tick','minute','substitution') for e in events[at:])
    if case.startswith('bench_pool'):
        assert set(d['eleven'])==set(initial['eleven'])
        assert pairs[0][1] in d['bench'] and pairs[0][0] in d['pool']
    if case.startswith('starter_'):
        assert set(d['eleven'])==set(initial['eleven'])
    replay_checks=0
    if replay:
        loaded=Match.load(m.save())
        assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
        assert all(loaded.m.reg(r)==m.m.reg(r) for r in REGS)
        replay_checks+=1
    edited=dict(eleven=d['eleven'],bench=d['bench'],pool=d['pool'],tactics=d['tactics'])
    m.answer()
    for ev in m.events():
        events.append(asdict(ev))
        if ev.kind=='decision':raise AssertionError('unexpected decision before first minute')
        if ev.kind=='minute':break
    assert ev.kind=='minute' and m.st['log']['substitutions']==[]
    if replay:
        loaded=Match.load(m.save())
        assert loaded.m.read(0,MEM_SIZE)==m.m.read(0,MEM_SIZE)
        assert all(loaded.m.reg(r)==m.m.reg(r) for r in REGS)
        replay_checks+=1
    return dict(case=case,pairs=pairs,edited=edited,swaps=swaps,keys=keys,events=events,
                draws=m.st['draws'],replay_checks=replay_checks,
                memory_sha256=hashlib.sha256(m.m.read(0,MEM_SIZE)).hexdigest(),
                all16={r:m.m.reg(r) for r in REGS})


def candidate(state,tables,fixture,context,case):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    image=Image.from_state(state,from_record(tables))
    m=Match.from_route_entry(image,Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True,record_draws=True,substitutions=2)
    return drive(m,case,replay=True)


def guards(state,tables,fixture,context):
    assert sys.implementation.name=='pypy'
    m=Match.from_route_entry(Image.from_state(state,from_record(tables)),Fixture(**fixture),context)
    m.configure_route_entry(pre_match_edits=True)
    d=decision(m,[]);xi,bench=d['eleven'],d['bench']
    cases=[[[xi[0],xi[0]]],[[xi[0],65535]],[[65535,bench[0]]],
           [[xi[0],bench[0]],[65535,xi[1]]],[[bench[0],0]]]
    for pairs in cases:
        before=snapshot(m)
        try:m.answer(edit_only=True,substitutions=pairs)
        except (ValueError,TypeError):pass
        else:raise AssertionError('invalid batch accepted')
        assert snapshot(m)==before
    # Synthetic wrong-phase guard: admitting the same public pair during play
    # must retain the legacy XI/bench restriction without executing a match.
    m.st['waiting']['context']='half_time'
    before=snapshot(m)
    try:m.answer(substitutions=[[xi[0],xi[1]]])
    except ValueError:pass
    else:raise AssertionError('in-match starter pair accepted')
    assert snapshot(m)==before
    from original_match.route_team import PreMatchPlan
    s={'squad':list(range(1,21)),'pool':list(range(101,181)),'cursor':1}
    p=PreMatchPlan(0,subs=[[1,2]])
    p.sub_marked=True
    p.select_key(s)  # second Enter: real witness has not occurred
    try:p.select_key(s)
    except MatchError:pass
    else:raise AssertionError('membership-only/no-swap acknowledgement')
    return len(cases)+2


class RosterDomains(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.image,cls.context,cls.fixture=_fixtures().entry()

    def test_invalid_batches_and_unobserved_swaps_are_pure_or_refused(self):
        self.assertEqual(call_in_pypy('test_prematch_roster_t134','guards',args=(
            self.image.state(self.image.tables),to_record(self.image.tables),self.fixture,self.context)),7)

    def test_domains_follow_original_word_swap_and_sorted_blocks(self):
        for case in ('starter_same','starter_different','bench_pool_same','bench_pool_different',
                     'reversed','batch','xi_bench','xi_pool'):
            with self.subTest(case=case):
                m=Match(self.image,Fixture(**self.fixture),engine='original',tail=False,
                        record_draws=True,substitutions=2)
                assert m.m.read(0,MEM_SIZE)==bytes(self.image.memory[:MEM_SIZE])
                for r,v in self.context.items():m.m.set_reg(r,v)
                m.opts['pre_match_edits']=True  # original keyboard-policy declaration only
                native=drive(m,case)
                actual=call_in_pypy('test_prematch_roster_t134','candidate',args=(
                    self.image.state(self.image.tables),to_record(self.image.tables),self.fixture,self.context,case))
                for field in ('pairs','edited','swaps','keys','events','draws'):
                    self.assertTrue(actual[field]==native[field],case+': '+field)
                self.assertEqual(actual['replay_checks'],2)
                print('T134_RECEIPT '+json.dumps(dict(case=case,pairs=actual['pairs'],
                    edited=actual['edited'],native_word_swaps=actual['swaps'],
                    keys=actual['keys'],draw_count=len(actual['draws']),event_count=len(actual['events']),
                    native_keys_events_draws_lists_equal=True,full_replay_checks=2,
                    port_memory_sha256=actual['memory_sha256'],port_all16=actual['all16'],
                    original_memory_sha256=native['memory_sha256'],original_all16=native['all16'],
                    source_entry_sha256=self.image.sha256(),fixture=self.fixture,
                    table_sha256=dict(self.image.tables.sha256),cross_backend_raw_identity_claimed=False),sort_keys=True),flush=True)


if __name__=='__main__':unittest.main()
