"""Local opposed/selection families and explicitly scoped finite-stream examples."""
from bisect import bisect_left
from collections import Counter
import csv
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import sys
from rng import MOD,draw,s16
from gates import probability

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from check import pin,sha
from tables import load_ds

CALLERS={
 '0791:1FDD':'Strictly better skill replaces an eligible incumbent; selection, no outcome draw.',
 '0791:287C':'Single-player quantised skill gate, covered by T99a.',
 '0791:34C1':'Shot/header reach from max(timer+5,(V+pitch_extra)//3); event3/4 continuation is indexed but not reduced to a fresh complete path probability here.',
 '0791:3B15':'Kicking reach max(30,rand(V2//4)); still draws when the floor makes the result constant.',
 '0791:3EF8':'Two reach modes: heading V4/div6/floor20 or kicking V2/div4/floor30, selected by argument/table.',
 '0791:47C5':'Marking versus feinting comparison changes a random offset weight by a divided difference; not a binary duel.',
 '0791:5474':'Holder dribbling10 or heading4 draw first; challenger tackling3 or heading4, factor4 only in the ground/2C54 geometry branch; strict signed word win.',
 '0791:5B36':'Ground duel: holder10 vs keeper1 plus conditional1 INSIDE keeper bound; air duel: holder4 vs doubled keeper1. In-flight catch is a separate travel/penalty-threshold wide comparison.',
 '0791:690C':'Conditional finish on events3/4: rand(selected holder skill) > rand32, constant opponent draw first; flags/set predicates can bypass this contest.',
 '0791:9ED3':'Shootout taker ordering by element12, including keeper; preserve loop/swap/tie behaviour, not a random chance.',
 '0791:D5C1':'Quick foul: unsigned deterministic own tackling3 < other dribbling10, tactic/chance gate then opposed hardness draws; not the quick goal-trial mechanism.'}


def cmp_value(raw,add,mode):return s16(raw+add) if mode=='word' else s16(raw)+add


def ideal_pair(a,b,own_add=0,opp_add=0,mode='word'):
    a=max(1,a&65535);b=max(1,b&65535)
    if mode=='word' and own_add==opp_add==0 and max(a,b)<=32767:
        m=min(b,a-1)
        return Fraction(m*(m+1)//2+b*(a-1-m),a*b)
    opponents=sorted(cmp_value(v,opp_add,mode) for v in range(1,b+1))
    return Fraction(sum(bisect_left(opponents,cmp_value(v,own_add,mode)) for v in range(1,a+1)),a*b)


@lru_cache(maxsize=None)
def marginal(n):
    n&=65535
    if n==0:return [(1,MOD)]
    out=[(k,(k*MOD+n-1)//n-((k-1)*MOD+n-1)//n) for k in range(1,n+1)]
    assert sum(c for _,c in out)==MOD
    return out


def independent_quantised(a,b,own_add=0,opp_add=0,mode='word'):
    opponents=sorted((cmp_value(v,opp_add,mode),count) for v,count in marginal(b))
    values=[v for v,_ in opponents];mass=[0]
    for _,count in opponents:mass.append(mass[-1]+count)
    wins=sum(count*mass[bisect_left(values,cmp_value(v,own_add,mode))] for v,count in marginal(a))
    return Fraction(wins,MOD*MOD)


def serial_pair(seed,a,b,own_add=0,opp_add=0,mode='word',reverse=False,ties=False):
    if reverse:seed,x=draw(seed,a);seed,y=draw(seed,b)
    else:seed,y=draw(seed,b);seed,x=draw(seed,a)
    x,y=cmp_value(x,own_add,mode),cmp_value(y,opp_add,mode)
    return (x>=y if ties else x>y),seed


def attempt(seed,own,opp,reverse=False,ties=False):
    pairs=[(own[2],opp[2]),(own[3],(2*opp[1])&65535),(own[3],opp[0])]
    draws=0
    for a,b in pairs:
        won,seed=serial_pair(seed,a,b,reverse=reverse,ties=ties);draws+=2
        if not won:return False,seed,draws
    return True,seed,draws


def build():
    grid=0
    for a in range(1,9):
        for b in range(1,9):
            brute=Fraction(sum(x>y for x in range(1,a+1) for y in range(1,b+1)),a*b)
            assert ideal_pair(a,b)==brute;(grid:=grid+1)
    pair_rows=[]
    for name,a,b,add,mode in [('equal100',100,100,0,'word'),('tackle-factor4',400,100,0,'word'),
      ('ground-keeper-bound-plus1',101,100,0,'word'),('air-keeper-double',200,100,0,'word'),
      ('inflight-catch-offset50',100,200,50,'wide'),('finish-versus32',100,32,0,'word'),
      ('zero-own-bound',0,10,0,'word'),('equal1',1,1,0,'word'),('synthetic-signed-bound40000',40000,100,0,'word')]:
        wins=wrong_order=wrong_ties=0;witness=None
        for seed in range(MOD):
            won,_=serial_pair(seed,a,b,opp_add=add,mode=mode)
            reversed_won,_=serial_pair(seed,a,b,opp_add=add,mode=mode,reverse=True)
            tied_won,_=serial_pair(seed,a,b,opp_add=add,mode=mode,ties=True)
            wins+=won;wrong_order+=won!=reversed_won;wrong_ties+=won!=tied_won
            if witness is None and won!=reversed_won:witness=seed
        pair_rows.append({'name':name,'own_bound':a,'opponent_bound':b,'opponent_add_after_signed_extension':add,'comparison':mode,
                          'ideal_uniform':probability(ideal_pair(a,b,opp_add=add,mode=mode)),
                          'independent_quantised':probability(independent_quantised(a,b,opp_add=add,mode=mode)),
                          'serial_lcg':probability(Fraction(wins,MOD)),'winning_entry_seeds':wins,
                          'order_control_different_outcomes':wrong_order,'tie_control_different_outcomes':wrong_ties,'first_order_witness_seed':witness})
    assert next(r for r in pair_rows if r['name']=='equal1')['tie_control_different_outcomes']==MOD
    assert next(r for r in pair_rows if r['name']=='equal100')['order_control_different_outcomes']>0
    fit=[242,1022,1045,433];tired=[181,778,770,341]
    attempts=[]
    for name,own,opp in [('equal-two-bounds',[2,1,2,2],[2,1,2,2]),('F021-fit-v-tired',fit,tired),('F021-tired-v-fit',tired,fit)]:
        wins=order=ties=end_diff=0;counts=Counter()
        for seed in range(MOD):
            won,end,n=attempt(seed,own,opp);other,other_end,_=attempt(seed,own,opp,reverse=True);inclusive,_,_=attempt(seed,own,opp,ties=True)
            wins+=won;counts[n]+=1;order+=won!=other;ties+=won!=inclusive;end_diff+=end!=other_end
        pairs=[(own[2],opp[2]),(own[3],2*opp[1]),(own[3],opp[0])]
        ideal=Fraction(1);quantised=Fraction(1)
        for a,b in pairs:ideal*=ideal_pair(a,b);quantised*=independent_quantised(a,b)
        attempts.append({'name':name,'own_lines_gk_def_mid_atk':own,'opponent_lines_gk_def_mid_atk':opp,
                         'ideal_independent':probability(ideal),'independent_quantised':probability(quantised),
                         'serial_lcg':probability(Fraction(wins,MOD)),'winning_entry_seeds':wins,'draw_count_cases':{str(k):v for k,v in sorted(counts.items())},
                         'order_control_different_outcomes':order,'order_control_different_end_seeds':end_diff,'tie_control_different_outcomes':ties})
    calls=list(csv.DictReader((s for s in (ROOT/'static/goal-exe/calls.tsv').read_text().splitlines() if not s.startswith(';')),delimiter='\t'))
    actual={r['caller']:int(r['count']) for r in calls if r['callee']=='0791:278A'}
    assert set(actual)==set(CALLERS) and sum(actual.values())==24
    read,_,table_sources=load_ds()
    selectors={f'DS:{base:04X}':[read(base+i) for i in range(n)] for base,n in [(0x7F4,2),(0x7F6,2),(0x7F8,2),(0x78E,2),(0x7FE,2),(0x800,2),(0x80C,5)]}
    return pin({'task':'T99b','sections':['What the original compares','Local opposed probabilities','Quick attempts and stream dependence','Coverage and evidence limits'],
                'checks':{'ideal_formula_grid_cases':grid,'formula_mismatches':0,'entry_seeds_per_serial_example':MOD,'pair_examples':len(pair_rows),'attempt_examples':len(attempts),'direct_skill_callers':len(actual),'static_skill_call_sites':sum(actual.values()),'order_and_tie_controls':'caught'},
                'seed_law':'Uniform all65536 entry seeds with fixed inputs; no assertion about reached game call-site distributions.',
                'caller_map':{a:{'static_call_sites':actual[a],'reading':CALLERS[a]} for a in sorted(CALLERS)},
                'selector_tables':selectors,'pairs':pair_rows,'attempts':attempts,
                'analysis_sha256':{p:sha((ROOT/p).read_bytes()) for p in ['notes/engine-study/T99/contests.py','notes/engine-study/T99/rng.py','notes/engine-study/T99/gates.py','notes/engine-study/T98/tables.py']}},
               list(CALLERS)+['0791:B19D','0791:4DA9','0791:7EEF','214B:0688'],
               table_sources+['static/goal-exe/calls.tsv','runtime/original_match/port/duels.py','runtime/original_match/port/contests.py','runtime/original_match/port/quick.py',
                             'static/goal-exe/code/seg_0791_10.asm','findings/F022-contest-sites-287c-5474-5d69-and-the-branches-e011-takes.md'])
