"""Single-draw finite seed laws and 287C quantisation, with explicit entry-seed assumptions."""
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import sys
from rng import MOD,step,draw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha


def probability(f):return {'fraction':str(f),'value':float(f)}


def is_one_count(bound):
    bound&=65535
    return MOD if bound==0 else (MOD+bound-1)//bound


@lru_cache(maxsize=None)
def enumerated_is_one(bound):return sum(draw(s,bound)[1]==1 for s in range(MOD))


def build():
    visited=set();s=0
    while s not in visited:visited.add(s);s=step(s)
    assert s==0 and len(visited)==MOD
    bounds=[0,1,2,3,4,16,18,20,32,33,2048,65535]
    for n in bounds:assert enumerated_is_one(n)==is_one_count(n),n
    bound_rows=[{'bound':n,'is_one_states':is_one_count(n),'exact_is_one':probability(Fraction(is_one_count(n),MOD)),
                 'ideal_uniform_is_one':None if n==0 else probability(Fraction(1,n))} for n in bounds]
    gate_rows=[]
    for value in [0,1,31,32,33,63,64,95,96,127,128,255,256,65535]:
        n=value//32+1;count=MOD-is_one_count(n)
        assert count==sum(draw(s,n)[1]!=1 for s in range(MOD))
        gate_rows.append({'value':value,'bound':n,'pass_states':count,'exact_pass':probability(Fraction(count,MOD)),
                          'ideal_uniform_pass':probability(Fraction(n-1,n))})
    energies=[]
    for byte in [1,2,4,16,30,31,32,33,34,127,128]:
        e=byte if byte<128 else byte-256
        half=-(abs(e)//2) if e<0 else e//2
        follow=(33-e)&65535;holder=half&65535
        energies.append({'energy_byte':byte,'signed_energy':e,'follow_bound':follow,'holder_choice_bound':holder,
                         'follow_is_one':probability(Fraction(is_one_count(follow),MOD)),
                         'holder_choice_is_one':probability(Fraction(is_one_count(holder),MOD)),
                         'scope':'ordinary 1..32' if byte<=32 else 'synthetic raw-byte boundary'})
    wrong_n=32//32
    assert MOD-is_one_count(wrong_n)!=next(r['pass_states'] for r in gate_rows if r['value']==32)
    assert draw(0,0)==(6927,1) and draw(0,1)==(6927,1)
    assert MOD-enumerated_is_one(1)==0
    controls={'drop_gate_plus_one':'caught at value32 (zero rather than32768 passes)',
              'invert_gate_result':'caught at value0 (65536 rather than0 passes)',
              'skip_degenerate_draw':'caught: seed0 must become6927 for bound0 and bound1'}
    return pin({'task':'T99a','sections':['The random stream and its scope','Skill gate thresholds','Other local gates and selection boundaries','Validation and limits'],
                'checks':{'lcg_period':len(visited),'bound_marginals_enumerated':len(bounds),'skill_threshold_rows':len(gate_rows),'mismatches':0,'controls':controls},
                'assumption':'Uniform distribution over all65536 entry seeds; not a statement about a reached call site after conditioning on prior game events.',
                'bounded_draws':bound_rows,'skill_gates':gate_rows,'energy_gates':energies,
                'hardness_chance':[{'hardness':h,'bound':18-h,'exact_is_one':probability(Fraction(is_one_count(18-h),MOD))} for h in [0,1,8,15,16]],
                'analysis_sha256':{p:sha((ROOT/p).read_bytes()) for p in ['notes/engine-study/T99/rng.py','notes/engine-study/T99/gates.py']}},
               ['214B:0688','214B:06B1','214B:06D0','214B:06FA','0791:287C','0791:2B7B','0791:4DA9','0791:5049','0791:1FDD','0791:9ED3'],
               ['runtime/original_match/port/runtime.py','runtime/original_match/port/pilot.py','runtime/original_match/port/geometry.py','runtime/original_match/port/contests.py','static/goal-exe/code/seg_214B_01.asm'])
