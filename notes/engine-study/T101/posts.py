#!/usr/bin/env python3
"""Source-derived post/target arithmetic; no Match, guest code or synthetic engine call."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT, BASE, ROUTINES, pin, sha, write_new

sys.path.insert(0, str(ROOT / 'notes/engine-study/T98'))
from tables import load_ds, s8


def byte(x):
    return s8(x & 255)


def start_posts(codes):
    read, _, _ = load_ds()
    posts = []
    for code in codes:
        x, y = s8(read(0x079e + 2 * code)), s8(read(0x079f + 2 * code))
        if posts and posts[-1] == [x, y]:
            if abs(x) <= 4:
                x = byte(x + 3)
                posts[-1][0] = byte(posts[-1][0] - 3)
            else:
                x = byte(x - (1 if x > 0 else -1) * 3)
                posts[-1][1] = byte(posts[-1][1] - 3)
        posts.append([x, y])
    return posts


def group(code, own, push):
    read, _, _ = load_ds()
    if code == 0:
        return 4
    flag = code > 11 or (push and own)
    return read(0x07ba + 2 * (code > 4) + flag)


def destination(post, depth, draw, direction, *, floor=False):
    x, y = post
    offset = draw
    if depth < 2:
        offset -= x // 2 if floor else int(x / 2)
    own = [byte(x + offset), byte(y + depth)]
    return [byte(v * direction) for v in own]


def calculations():
    read, _, sources = load_ds()
    posts = start_posts(list(range(14)))
    expected = [[0,-37],[0,-36],[0,-35],[-6,-33],[6,-33],[0,-31],[0,-28],
                [-5,-27],[5,-27],[0,-24],[-7,-22],[7,-22],[0,-21],[0,-18]]
    assert posts == expected
    assert start_posts([2,2]) == [[-3,-35],[3,-35]]
    assert start_posts([7,7]) == [[-5,-30],[-2,-27]]
    assert start_posts([2,2,2]) == [[-3,-35],[3,-35],[0,-35]]
    assert [group(2,True,p) for p in [False,True]] == [3,2]
    assert [group(7,True,p) for p in [False,True]] == [2,1]
    assert group(12,False,False) == 1 and group(0,False,False) == 4
    attack = [[read(0x07db + 4*e + g) for g in range(1,4)] for e in range(2)]
    defence = [[[read(0x07cb + 8*e5 + 4*e6 + g) for g in range(1,4)]
                for e6 in range(2)] for e5 in range(2)]
    assert attack == [[60,45,25],[60,50,35]]
    assert defence == [[[0,0,0],[15,10,2]],[[10,5,0],[45,25,5]]]
    # Strict 4532 limit, with its separate group-2 advancement predicate assumed true.
    assert [45 + (45 < limit) for limit in [attack[0][1],attack[1][1]]] == [45,46]
    assert min(defence[1][1][0], min(2*abs(10),42)) == 20
    # 4354 draw(5)=3 means raw jitter zero. Signed IDIV truncates -5/2 to -2.
    assert destination([-5,-27],0,0,-1) == [3,27]
    assert destination([-5,-27],0,0,-1,floor=True) == [2,27]
    # Conditional 57AC -> 4A28(4354, no accepted marker) -> 474D. Target uses pre-step depth.
    seq = []
    depth = 26
    for _ in range(2):
        before = depth
        target = destination([-5,-27],depth,0,1)
        depth -= depth > 25  # class 2 ahead-of-ball predicate assumed true
        seq.append({'depth_before':before,'destination':target,'depth_after':depth})
    assert seq == [{'depth_before':26,'destination':[-5,-1],'depth_after':25},
                   {'depth_before':25,'destination':[-5,-2],'depth_after':25}]
    controls = {'floor-instead-of-idiv':'rejected: [2,27] differs from literal [3,27]',
                'advance-at-equal-limit':'rejected: depth45 would become46 with ordinary limit45',
                'step-before-target':'rejected: first target would be [-5,-2], not [-5,-1]',
                'separate-wide-posts-symmetrically':'rejected: prior y must fall3, current x moves inward3'}
    assert (45 + (45 <= 45)) != 45
    assert destination([-5,-27],25,0,1) != seq[0]['destination']
    assert [[-8,-27],[-2,-27]] != start_posts([7,7])
    return dict(posts=posts,attack_limits=attack,defence_limits=defence,zonal_sequence=seq,
                controls=controls,ds_sources=sources)


def build():
    calc = calculations()
    mechanisms = [
        ('419C','Played code indexes post table; adjacent equal posts get asymmetric separation.',
         ['player+6','pitch+9/+A','DS:079E','DS:7920'],'Starting shape and slot-order dependence.'),
        ('42CB','Keeper group4; otherwise table selects class from code range, possession and effective element1.',
         ['player+6','DS:07BA','26D7(1)','2B51'],'Controls which depth-table column applies.'),
        ('4354','Choose lateral jitter, centre shallow depth with signed division, add post/offset and mirror both bytes.',
         ['pitch+7..+C','player+6','pitch+12','2C86'],'Produces a destination; does not move or clamp the player.'),
        ('4532','Strict depth<attack limit; class-dependent ball/tactic/coin predicate yields one or zero.',
         ['pitch+C','DS:07DB','26D7(1/7)'],'One-cell advance only on a passing predicate.'),
        ('4649','Strict depth>defence limit; class-dependent ahead-of-ball and slot2/code1 predicates.',
         ['pitch+C','DS:07CB','26D7(5/6)'],'One-cell retreat can stop above the numeric target.'),
        ('474D','Possession and defender-ahead gate choose addition or subtraction; defending slot2 centres lateral offset.',
         ['pitch+B/+C','player+6','2BB1','2D10'],'Persistent target-depth update, separate from actual motion.'),
        ('4B64','Keeper mirrors post; state9/state11-special use draw table; otherwise depth resets from tactical tables and ball-dependent bounds, then4A28.',
         ['pitch+7/+C/+12','DS:82F7','DS:07CB/07DB','CS:4B44'],'Can replace incremental depth with a jump to a bounded reset value.'),
    ]
    examples = [
        {'id':'zonal-target-before-step','inputs':{'code':7,'post':[-5,-27],'depth':26,'direction':1,'e5':1,'e6':1,'jitter_draw':3},
         'steps':calc['zonal_sequence'],'prediction':'Targets (-5,-1), then (-5,-2); first call stores depth25 after building its target.',
         'limits':'Conditional source sequence:57AC early branches clear,4A28 selected,no accepted marker; ahead-of-ball true. No complete fixture or observed visit frequency.'},
        {'id':'offside-line-control-threshold','inputs':{'group':2,'depth':45,'advancement_predicate':True,'e7':[0,1]},
         'steps':['ordinary limit45 -> strict test false -> depth45','trap limit50 -> true -> depth46'],
         'prediction':'Toggle element7 changes this one update by one depth cell; no direct offside detection toggle.',
         'limits':'Hold class, geometry and branch eligibility fixed; whole-match effect and RNG alignment are not inferred.'},
        {'id':'negative-odd-centering','inputs':{'post':[-5,-27],'depth':0,'draw5':3,'direction':-1},
         'steps':['jitter0 - trunc(-5/2) =2','own target(-3,-27)','mirror both bytes'],
         'prediction':[3,27],'limits':'Byte arithmetic projection; floor division yields the wrong x=2.'},
    ]
    sources = ['runtime/original_match/port/positioning.py','runtime/original_match/port/geometry.py',
               'static/goal-exe/code/seg_0791_05.asm','static/goal-exe/code/seg_0791_07.asm',
               'static/goal-exe/code/seg_0791_08.asm','static/goal-exe/code/seg_0791_09.asm',*calc['ds_sources']]
    return pin({'task':'T101a','status':'proposed; source-derived explanation',
                'method':__doc__,'sections':['Posts and effective controls','Depth and destination updates','Worked sequences and limits'],
                'routines':[dict(address='0791:'+a,mechanism=m,fields=f,visible_effect=e,
                                 limits='Local branch rule; no new match-frequency or full-fixture claim.') for a,m,f,e in mechanisms],
                'examples':examples,'calculations':calc,'analysis_sha256':sha(Path(__file__).read_bytes())},
               ['0791:'+a for a in ROUTINES['T101a']]+['0791:26D7','0791:2BE5','0791:2C86','0791:57AC'],
               sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T101/T101a-v1.json'
    if args.check:
        assert json.loads(path.read_text()) == data
        print('PASS: 14 posts, duplicate rules, 6 attack/12 defence limits, 3 worked examples and 4 arithmetic/order controls')
    else:
        write_new(path,data)
        print('wrote T101a source-derived ledger; no engine execution')


if __name__=='__main__':
    main()
