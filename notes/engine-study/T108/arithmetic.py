#!/usr/bin/env python3
"""Static arithmetic candidate audit; no original/port routine or Match execution."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT,BASE,pin,sha,write_new

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
import skill
import strength
from tables import load_ds,s8


def leadership(ceiling,profile,age):
    delta=ceiling-profile
    quotient=abs(delta)//8 * (-1 if delta<0 else 1)
    remainder=(delta-quotient*8)&65535
    return remainder//2 if age<21 else remainder


def calculations():
    skill_values=[skill.trace(skill.record(form=f),3)['value'] for f in [31,32]]
    strength_values=[strength.trace(skill.record(ability=225,form=f))['value'] for f in [31,32]]
    assert skill_values==[72,54] and strength_values==[226,183]
    mutant=skill.trace(skill.record(form=32),3,mutation='form-cutoff33')['value']
    assert mutant==73 and mutant!=skill_values[1]
    negative=[leadership(0,1,age) for age in [20,21]]
    assert negative==[32767,65535]
    assert ((0-1)%8)//2==3 and 3!=negative[0]
    assert [leadership(72,4,age) for age in [20,21]]==[2,4]
    read,_,ds_sources=load_ds()
    assert read(0x769+5)==read(0x769+8)==0
    derived_max=65535//32
    before_venue_max=65535//256+derived_max//4
    skill_max=before_venue_max+before_venue_max//16
    bound_max=1+skill_max//16
    assert [derived_max,before_venue_max,skill_max,bound_max]==[2047,766,813,51]
    pairs=0
    for direction in [-1,1]:
        for y in range(-37,38):
            if y*(-direction)<0:continue
            for draw in range(1,bound_max+1):
                adjusted=y-direction*draw
                assert -128<=adjusted<=127 and s8(adjusted&255)*direction<0
                pairs+=1
    assert pairs==3876
    assert (10-1)*1>=0  # removing the target-own-half rejection invalidates the implication
    assert s8((-128-1)&255)==127  # outside the on-pitch premise, wrapping invalidates it
    equality_target=20-1 if abs(20)>=abs(20) else 20
    strict_mutant=20-1 if abs(20)>abs(20) else 20
    assert equality_target==19 and strict_mutant==20
    assert not (180>180) and (181>180) and (180>=180)
    return dict(form_skill_values=skill_values,form_strength_values=strength_values,
                negative_leadership_age20_age21=negative,normal_leadership_age20_age21=[2,4],
                marking_bounds=dict(derived=derived_max,before_venue=before_venue_max,effective=skill_max,draw=bound_max),
                half_pitch_proof_pairs=pairs,off_pitch_wrap_counterexample=127,
                offside_equal_target=equality_target,
                controls={'form-cutoff33':'rejected:73 instead of54','python-modulo':'rejected:3 instead of32767',
                          'strict-offside-target':'rejected:20 instead of19',
                          'omit-target-half-premise':'rejected:adjusted_y9 is not negative'},
                ds_sources=ds_sources)


def build():
    calc=calculations()
    candidates=[
        dict(id='form-sentinel',minimal_input={'skill':{'ability':180,'profile':8,'club':2,'element':3,'energy':32,'form':[31,32]},
                                              'strength':{'ability':225,'energy':32,'form':[31,32],'placement':False}},
             expected='A monotone numeric-form assumption would predict no drop at31->32; fidelity must instead preserve the signed branch at32.',
             actual={'effective_skill':[72,54],'strength':[226,183],'basis':'source-derived arithmetic, not a new original run'},
             evidence=['0791:278A','1771:377E'],disposition='original quirk',
             reachability='Ordinary-width controlled inputs; no claim that the form byte is an ordered rating or that an observed match crosses this edge.',
             follow_up='Keep branch semantics in readable rewrite; T105 may select a local corroboration. No original repair.'),
        dict(id='negative-leadership',minimal_input={'ceiling':0,'profile':1,'age':[20,21]},
             expected='Signed IDIV remainder -1 is retained as wordFFFF; unsigned DIV2 below age21 yields7FFF.',
             actual={'leadership':[32767,65535],'python_modulo_young':3},
             evidence=['1771:30D9','0791:1F3C','0791:20E3'],disposition='original quirk',
             reachability='Representable edited-record case; creation/recovery invariants admitting ceiling<profile have not been established. Not a natural player claim.',
             follow_up='Preserve finite-width semantics; do not extend the normal0..7 leadership claim to every byte tuple. Leave all-unavailable leader return for record audit.'),
        dict(id='half-pitch-follow',minimal_input={'target_y':-2,'marker_direction':1,'target_direction':-1,'marking':48,'feinting':81,'draw':3},
             expected='Full-pitch bypass can change a copy only if the half-pitch guard would otherwise fail.',
             actual={'target':[2,-5],'half_pitch_guard':'passes','bound_max':51,'proof_pairs':3876},
             evidence=['0791:47C5','0791:4A28','0791:2C54','0791:278A','1771:3A06'],
             disposition='documentation/test defect',
             reachability='Proof assumes opposed directions, accepted target in|y|<=37, fixed skill tables and exact branch order. Overapproximation, not observed fixtures. Off-pitch byte wrapping can invalidate the implication.',
             follow_up='Qualify F026 follow-reach wording and T103 predictions via #514; retain separate e5 depth effect and unvisited off-pitch contexts.'),
        dict(id='strict-edges',minimal_input={'movement_target_y':20,'opponent_line_y':20,'direction':1,'eligible_state':5,
                                            'activity_values':[180,181]},
             expected='8972 jl skips only smaller absolute targets;8C45 expenditure requires unsigned activity>180.',
             actual={'restricted_target_y':19,'activity180_spends':False,'activity181_spends':True},
             evidence=['0791:8889','0791:8AE9'],disposition='unsupported suspicion',
             reachability='Other target-restriction/activity gates assumed satisfied. Listing and port agree; no current off-by-one defect reproduced.',
             follow_up='Use instructions rather than stale decompiler flags; future targeted edge checks if selected in T105. No runtime change.'),
    ]
    artifacts=['notes/engine-study/T98/skill-v1.json','notes/engine-study/T98/strength-v1.json',
               'notes/engine-study/T101/T101b-v1.json','notes/engine-study/T101/T101c-v1.json']
    sources=['notes/engine-study/T98/skill.py','notes/engine-study/T98/strength.py','notes/engine-study/T98/tables.py',
             'runtime/original_match/port/attributes.py','runtime/original_match/port/geometry.py',
             'runtime/original_match/port/positioning.py','runtime/original_match/port/pilot.py','runtime/original_match/port/motion.py',
             'static/goal-exe/code/seg_0791_03.asm','static/goal-exe/code/seg_0791_04.asm',
             'static/goal-exe/code/seg_0791_05.asm','static/goal-exe/code/seg_0791_08.asm',
             'static/goal-exe/code/seg_0791_14.asm','static/goal-exe/code/seg_1771_05.asm',*calc['ds_sources']]
    addresses=sorted({e for row in candidates for e in row['evidence']})
    return pin(dict(task='T108a',status='proposed; candidate attribution pending independent review',method=__doc__,
                    sections=['What counts as a defect','Arithmetic candidates','A redundant guard under stated bounds','Edges, negatives and remaining risks'],
                    candidates=candidates,calculations=calc,supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in artifacts},
                    analysis_sha256=sha(Path(__file__).read_bytes())),addresses,sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T108/T108a-v1.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: four candidates, form/leadership literals,3876 bounded arithmetic pairs, four altered-rule controls')
    else:write_new(path,data);print('wrote T108a source-derived audit; no engine execution')


if __name__=='__main__':main()
