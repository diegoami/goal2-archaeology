#!/usr/bin/env python3
"""Local source-derived marking/leader calculations, without executing an engine."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT, BASE, ROUTINES, pin, sha, write_new

sys.path.insert(0, str(ROOT / 'notes/engine-study/T98'))
from tables import load_ds, s8


def select(candidates, *, replace_equal=False):
    """Available candidates in visit order, normal nonnegative score domain."""
    winner, best = None, -1
    for identity, score, unavailable in candidates:
        if unavailable:
            continue
        if score > best or (replace_equal and score == best):
            winner, best = identity, score
    return winner


def displacement(marking, feinting, point, direction, roll):
    bound = 1 + (max(0, feinting-marking) // 16)
    assert 1 <= roll <= bound
    return bound, [point[0], s8((point[1]-direction*roll) & 255)]


def calculations():
    read, _, sources = load_ds()
    taker_elements = [read(0x0764+k) for k in range(2,6)]
    assert taker_elements == [7,12,12,2]
    starts = [read(0x0764+(role == 5))+1 for role in range(2,6)]
    assert starts == [2,2,2,1]
    leadership = [(72-4)%8//2, (72-4)%8]
    assert leadership == [2,4]  # ages20/21, positive difference only
    candidates = [(101,4,False),(102,4,False),(103,7,True)]
    assert select(candidates) == 101 and select(candidates,replace_equal=True) == 102
    assert ((56+2*4)&255) == 64
    assert ((250+2*7)&255) == 8  # representable cache edge, not a natural-fixture claim
    assert (250+2*7) != ((250+2*7)&255)
    # 4438/44C1 use strict rectangular bounds, not radial distance.
    post_edges = [abs(dx)<4 and abs(dy)<9 for dx,dy in [(3,8),(4,8),(3,9)]]
    player_edges = [abs(dx)<4 and abs(dy)<6 for dx,dy in [(3,5),(4,5),(3,6)]]
    assert post_edges == player_edges == [True,False,False]
    bound, target = displacement(48,81,[2,-2],1,3)
    assert (bound,target) == (3,[2,-5])
    assert [1+max(0, f-48)//16 for f in [48,63,64,79,80,81]] == [1,1,2,2,3,3]
    passes = {str(e):[r for r in range(1,7) if r<e] for e in [1,2,6,7]}
    assert passes == {'1':[],'2':[1],'6':[1,2,3,4,5],'7':[1,2,3,4,5,6]}
    # 47C5 first rejects target_y * target_direction <0. Opposed directions
    # imply target_y * marker_direction <=0. The nonwrapping displacement
    # subtracts roll>=1 in that frame, so the subsequent half-pitch guard passes.
    assert (-2 * -1) >= 0 and (-5 * 1) < 0
    assert [2,-2-2] != target  # omit the +1 in the displacement bound
    assert (6 <= 6) != (6 < 6)  # inclusive energy comparison changes this edge
    return dict(taker_elements=taker_elements,taker_first_slots=starts,leadership_age20_age21=leadership,
                captain_choice=101,cache_before56_after64=64,cache_wrap_example=8,
                post_zone_edges=post_edges,player_zone_edges=player_edges,
                marking_bound=bound,marking_target=target,energy_accepted_draws=passes,
                controls={'replace-tie':'rejected:102 instead of101','omit-bound-plus-one':'rejected:target[2,-4] instead of[2,-5]',
                          'inclusive-energy':'rejected:draw6 must fail at energy6','omit-cache-wrap':'rejected:264 instead of8'},
                ds_sources=sources)


def build():
    calc = calculations()
    rows = [
        ('1F3C','Scan first eleven available players for strictly greater leadership; first tie wins.',
         ['country.squad','1771:30D9','1771:3216'],'Captain choice; all-unavailable return remains inherited stack state.'),
        ('1FDD','Select captain/set-piece table role by strictly greater effective skill, despite historical marker name.',
         ['DS:9976+10*side+2*role','DS:0764','278A'],'Chosen player identity, not opponent man-marking assignment.'),
        ('20E3','Managed/menu-context captain and taker branches, followed by twice captain leadership added to each cached extra byte.',
         ['DS:0C1F','DS:9978+10*side','pitch+11'],'Team-wide skill-extra contribution where278A later gates it.'),
        ('2218','Swap squad words, saved-form bytes and marking words together; caller handles pitch records and holder remapping.',
         ['country.squad','DS:9B07','DS:9A3E'],'Assignment and form stay attached during the surrounding sort.'),
        ('4438','Strict post-centred rectangle, with role depth adjustment outside state9.',
         ['pitch+9/+A','DS:07BE+role','2BE5'],'Zone eligibility for fallback marking target.'),
        ('44C1','Strict player-centred rectangle excluding holder and state13.',
         ['pitch+0/+1/+6/+12','DS:830B','2BE5'],'Proximity branch used by play decisions.'),
        ('47C5','Use assigned opponent identity or last eligible in-zone opponent; reject opponent own half, displace longitudinal target by a skill-dependent draw.',
         ['DS:9A3E','278A(5/8)','4A28 frame target'],'Target follows or lags an opponent; selection is not a binary tackle contest.'),
        ('4A28','Holding-side energy reset or defending post fallback; keeper exception; marker copy requires context, strict energy and half-pitch guards.',
         ['pitch+7','player+E','DS:8325','26D7(1/5)','2B7B'],'Changes target, consuming draws even when a later guard rejects the copy.'),
    ]
    examples = [
        {'id':'marking-sequence','inputs':{'marking':48,'opponent_feinting':81,'opponent_point':[2,-2],
                                         'direction':1,'displacement_draw':3,'energy':6,'energy_draw':5},
         'steps':['4A28 first sets a post destination via4354','47C5 resolves an available target outside its own half',
                  'bound=1+(81-48)//16=3; adjusted target(2,-5)','draw5<energy6 and adjusted y*direction<0 -> copy'],
         'prediction':calc['marking_target'],'limits':'Assume bound players, accepted identity and nonwrapping coordinates; no full fixture execution or frequency.'},
        {'id':'captain-cache','inputs':{'rating':72,'profile':4,'ages':[20,21],'base_extra':56},
         'steps':['positive signed remainder(72-4)%8=4','under21 halves to2, age21 retains4','20E3 adds twice that leadership to all eleven bytes'],
         'prediction':{'age20_extra':60,'age21_extra':64},
         'limits':'After one captain application following binding;278A extra/event gate still applies; not every element gains this amount.'},
        {'id':'half-pitch-candidate','inputs':{'marker_direction':'d','target_direction':'-d','nonwrapping':True,'roll':'>=1'},
         'steps':['accepted target implies y*(-d)>=0','so y*d<=0','adjusted_y*d=y*d-roll<0'],
         'prediction':'The e5=0 follow guard passes under these assumptions, so e5 cannot change this copy decision.',
         'limits':'Static candidate for T108; byte wrap, unusual directions and all caller contexts require separate audit; e5 still changes depth tables.'},
    ]
    sources=['runtime/original_match/port/positioning.py','runtime/original_match/port/geometry.py',
             'runtime/original_match/port/attributes.py','runtime/original_match/port/frame.py',
             'static/goal-exe/code/seg_0791_03.asm','static/goal-exe/code/seg_0791_04.asm',
             'static/goal-exe/code/seg_0791_07.asm','static/goal-exe/code/seg_0791_08.asm',
             'static/goal-exe/code/seg_1771_05.asm','static/goal-exe/code/seg_1771_06.asm',*calc['ds_sources']]
    return pin({'task':'T101b','status':'proposed; source-derived explanation','method':__doc__,
                'sections':['Assignment and identity','Following an opponent','Leaders and worked examples'],
                'routines':[dict(address='0791:'+a,mechanism=m,fields=f,visible_effect=e,
                                 limits='Local mechanism; no new full-match observation or natural frequency.') for a,m,f,e in rows],
                'examples':examples,'calculations':calc,'analysis_sha256':sha(Path(__file__).read_bytes())},
               ['0791:'+a for a in ROUTINES['T101b']]+['1771:3EF8','1771:3E2F','1771:30D9','0791:230C','0791:2C54'],
               sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T101/T101b-v1.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: taker roles, leader/cache arithmetic, strict zone/energy edges, marking sequence and 4 controls')
    else:
        write_new(path,data);print('wrote T101b source-derived ledger; no engine execution')


if __name__=='__main__':
    main()
