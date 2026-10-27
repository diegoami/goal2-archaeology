#!/usr/bin/env python3
"""Source-derived receiver/holder decisions; no Match or original/port engine execution."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT,BASE,ROUTINES,pin,sha,write_new

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds


def receiver(candidates,cutoff,long_mode,coins,*,always_replace=False,first_coin=False,inclusive_long=False,first_fallback=False):
    """Eligible candidates supplied in descending slot order; no full fixture model."""
    selected=None;used=0;trace=[]
    for slot,distance in candidates:
        qualifies=(distance>=cutoff if inclusive_long else distance>cutoff) if long_mode else distance<=cutoff
        if not qualifies:
            trace.append(dict(slot=slot,distance=distance,accepted=False,reason='distance'));continue
        accept=True
        if selected is not None or first_coin:
            draw=coins[used];used+=1;accept=bool(draw) or always_replace
        if accept:selected=slot;cutoff=distance
        trace.append(dict(slot=slot,distance=distance,accepted=accept,reason='eligible first or replacement coin'))
    fallback=selected is None
    if fallback:
        for slot,_ in sorted(candidates):
            selected=slot
            if first_fallback:break
    return dict(selected=selected,final_cutoff=cutoff,coins=used,fallback=fallback,trace=trace)


def holder_choice(role,push,x,y,first_table,second_table,*,midfield_pass=False,forward_pass=False,inclusive_cross=False):
    forward=y>=24+first_table if inclusive_cross else y>24+first_table
    if forward and abs(x)>3:return 'cross',1
    if y<-8:return 'pass',1
    if second_table==1:return 'pass',2
    if role in [3,4]:return ('dribble' if push else 'pass'),2
    if role in [7,8]:return ('dribble' if push and not midfield_pass else 'pass'),2
    if role in [10,11]:return 'dribble',2
    if role in [12,13]:return ('pass' if forward_pass else 'dribble'),2
    return 'pass',2


def calculations():
    read,_,sources=load_ds()
    assert [read(0x778+i) for i in range(2)]==[2,24]
    candidates=[(11,4),(10,3),(9,2)]
    short=receiver(candidates,2+3,False,[0,1])
    assert short['selected']==9 and short['coins']==2 and not short['fallback']
    fallback=receiver(candidates,24+3,True,[])
    assert fallback['selected']==11 and fallback['fallback'] and fallback['coins']==0
    normal=receiver(candidates,5,False,[0,0])
    altered=receiver(candidates,5,False,[0,0],always_replace=True)
    assert normal['selected']==11 and altered['selected']==9
    premature=receiver(candidates,5,False,[0,1,1],first_coin=True)
    assert premature['coins']==3 and premature['coins']!=short['coins']
    eq_normal=receiver([(11,5),(10,6)],5,True,[0])
    eq_altered=receiver([(11,5),(10,6)],5,True,[0],inclusive_long=True)
    assert eq_normal['selected']==10 and eq_altered['selected']==11
    assert receiver(candidates,27,True,[],first_fallback=True)['selected']==9
    assert [holder_choice(3,p,0,0,3,3)[0] for p in [False,True]]==['pass','dribble']
    assert holder_choice(7,True,0,0,3,3,midfield_pass=True)[0]=='pass'
    assert holder_choice(7,True,0,0,3,3,midfield_pass=False)[0]=='dribble'
    assert holder_choice(3,False,4,27,3,3)==('pass',2)
    assert holder_choice(3,False,4,28,3,3)==('cross',1)
    assert holder_choice(3,False,4,27,3,3,inclusive_cross=True)==('cross',1)
    assert [read(0x7e4+i) for i in range(2)]==[4,3]
    # Raw CS set, not a decompiler flag interpretation: membership gates3D38.
    lines=(ROOT/'static/goal-exe/code/seg_0791_06.asm').read_text().splitlines()
    raw=b''.join(bytes.fromhex(next(s for s in lines if s.startswith(pc+' ')).split('db ',1)[1].split(';',1)[0])
                 for pc in ['3D18','3D28'])
    cross_roles=[p for p in range(14) if raw[p//8]&(1<<(p%8))]
    assert len(raw)==32 and cross_roles==[2,12]
    return dict(short_selection=short,long_fallback=fallback,cross_target_roles=cross_roles,
                short_long_cutoff_bases=[2,24],forward_pass_bounds_role13_role12=[4,3],
                holder_role3_push_off_on=['pass','dribble'],cross_strict_edge={'at27':['pass',2],'at28':['cross',1]},
                controls={'always-replace':'rejected:winner9 instead of11 on two failed replacement coins',
                          'coin-for-first':'rejected:3 selection coins instead of2',
                          'inclusive-long-distance':'rejected:winner11 instead of10 at equality edge',
                          'first-fallback':'rejected:winner9 instead of11',
                          'inclusive-cross':'rejected:cross/1 table read instead of pass/2 at equality'},
                ds_sources=sources)


def build():
    calc=calculations()
    rows=[
        ('2FB1','Strict nearest Manhattan scans over available nonholder/nonchasing outfielders, with separate goal-side nearest.',
         ['DS:8311/830F','DS:82F6','pitch+0/+1/+6/+12'],'Selects chase/reaction candidates; first equal-distance slot wins.'),
        ('30EA','Map relative squad slot through the pitch record side base.',
         ['DS:0668','pitch+6','2974'],'Receiver loops visit the correct global pitch slots.'),
        ('3111','Long mode from effective e3 or own-half nonkeeper; descending distance-qualified scan with conditional replacement coins, then ascending fallback.',
         ['DS:0778','261A','player tactic','pitch coordinates/state'],'Receiver preference, not guaranteed range or passing accuracy.'),
        ('3323','Call3111 then forward its full returnedAX to384C.',
         ['receiver slot argument','guest returnAX'],'Select and launch toward receiver; preserve ABI beyond decompiled char type.'),
        ('333F','If activity off enable it; otherwise mark first eligible teammate beyond opposite line with timer0, saving point and flag.',
         ['DS:8325/830E/830A/8317/8329','DS:82E3','pitch+10'],'Prepares delayed offside candidate rather than immediately awarding a foul.'),
        ('384C','If no pending offside, prepare self/receiver target, receiver state5 and830C; launch6 or11, then flight/commentary/chase tail.',
         ['DS:830E/830C/8303/80FA/8313','pitch+12','34C1'],'Pass or self-directed dribble shares mechanics; attempted launch is not a goal.'),
        ('3B9E','Target a slot, choose event by passer half, submit commentary3, coin flight flag and begin chase.',
         ['DS:078C/830C/8303','target point'],'Half-dependent launch wrapper with its own draw/state order.'),
        ('3BEE','Pending offside routes to82EB; otherwise coin chooses selected pass or long ball.',
         ['DS:830E','main RNG'],'Offside short-circuits the pass/long coin.'),
        ('3D38','First available nonself outfielder in role set{2,12} and opposing goal strip supplies cross point.',
         ['CS:3D18','player+6','2EF0','2996'],'Cross target depends on played role and geometry, not an explicit height term here.'),
        ('3DF6','Use selected cross point or random fallback, sentinel830C=FF, launch5, submit line, clear830C, choose flight flag and begin chase.',
         ['DS:830C/8303','261A','34C1'],'Crossing branch has no persistent selected-receiver slot after its tail.'),
        ('4E28','Strict advanced-wide cross, forced deep/table pass, then role/e1-specific pass or self-directed dribble.',
         ['player+6','261A','26D7(1)','DS:07E4'],'Action choice changes tactics-to-football effect and random consumption.'),
        ('500C','Read opposite side keeper state13.',
         ['DS:0668','DS:830B','pitch+12'],'Keeper delay can alter holder shot choice.'),
        ('5049','Holder-at-feet branch updates depth/target; keeper throw area or outfield shot/clearance/pass/dribble gates.',
         ['2C29','player+E','26D7(2)','DS:07E5','DS:8303'],'Energy controls an action opportunity bound, not movement distance.'),
        ('533B','For selected receiver, target current ball for keeper/timer<10, otherwise projected endpoint8313.',
         ['DS:830C/8300/82F6/8313','pitch+7'],'Receiver can run to projected arrival rather than chase current ball.'),
        ('57AC','State5 priority: offside, holder opportunity, receive target, challenge, then ball/marking target and depth; special keeper-holder branch.',
         ['pitch+12','DS:830B/830C/830D/8327','474D'],'First accepting branch changes which later decisions and draws run.'),
        ('58E1','Keep target at own point, decrement positive timer, switch state at zero entry or keeper special case.',
         ['pitch+7/+10/+12','DS:8302/8300'],'Chase delay affects future eligibility; detailed countdown is inT101.'),
    ]
    examples=[
        {'id':'selected-short-pass','inputs':{'holder_slot':6,'holder_point':[0,0],'role':7,'effective_e1':0,'effective_e2':1,'effective_e3':0,
                                             'eligible_receivers_desc':[[11,4],[10,3],[9,2]],'cutoff_table_byte':3,'replacement_coins':[0,1]},
         'steps':['Assume57AC holder branch and outside shot/clearance contexts; e2 coin admits4E28',
                  '4E28 advanced/deep/forced-pass checks fail; role7/e1off selects3323',
                  '3111 short cutoff5; first11 accepted, coin0 keeps11 over10, coin1 selects9',
                  '384C writes receiver state5,830C=9 and event6 through34C1 when80FA=0',
                  'Assume launch gate passes, travel<11, no offside; ground ordinary tail submits commentary template8'],
         'prediction':{'receiver':9,'selection_main_coins':2,'selection_table_reads':1,'score_change_at_selection':0},
         'limits':'Partial source-conditioned sequence with supplied draws; no complete legal fixture, seeded run or exact velocity/state differential. Commentary can be deduplicated; flight/resolution are separate slices.'},
        {'id':'long-fallback','inputs':{'long_mode':True,'table_byte':3,'distances_desc':[[11,4],[10,3],[9,2]]},
         'steps':['cutoff27; no distance qualifies','ascending fallback retains last available nonholder'],
         'prediction':{'receiver':11,'distance':4,'selection_coins':0},
         'limits':'Other candidates unavailable in this supplied list; fallback drops first-pass distance/state/ahead filters. Demonstrates no absolute long-distance guarantee.'},
        {'id':'holder-cross-boundary','inputs':{'role':3,'effective_push':0,'x':4,'directed_y':[27,28],'first_table_byte':3,'second_table_byte':3},
         'steps':['threshold27; equality failscross then passes throughrole selection','28>27 selects cross before second table read'],
         'prediction':[['pass',2],['cross',1]],'limits':'Only4E28 local branch; table reads are not fresh main-seed draws.'},
    ]
    sources=['runtime/original_match/port/ball.py','runtime/original_match/port/contests.py','runtime/original_match/port/geometry.py',
             'static/goal-exe/code/seg_0791_05.asm','static/goal-exe/code/seg_0791_06.asm',
             'static/goal-exe/code/seg_0791_07.asm','static/goal-exe/code/seg_0791_09.asm',*calc['ds_sources']]
    return pin(dict(task='T102a',status='proposed; source-derived explanation',method=__doc__,
                    sections=['Who is considered','Holder choices and two random sources','From selection to a pass','Worked decisions and rewrite boundaries'],
                    routines=[dict(address='0791:'+a,mechanism=m,fields=f,visible_effect=e,
                                   limits='Conditional source mechanism; no fresh original/port execution or natural frequency claim.') for a,m,f,e in rows],
                    examples=examples,calculations=calc,analysis_sha256=sha(Path(__file__).read_bytes())),
               ['0791:'+a for a in ROUTINES['T102a']]+['0791:261A','0791:2C54','0791:2EF0','0791:2F28'],sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T102/T102a-v1.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: receiver scan/fallback/coin order,role and cross thresholds,CS cross roles,5 altered-rule controls')
    else:write_new(path,data);print('wrote T102a source-derived ledger; no engine execution')


if __name__=='__main__':main()
