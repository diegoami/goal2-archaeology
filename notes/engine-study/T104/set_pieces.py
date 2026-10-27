#!/usr/bin/env python3
"""Source-derived restart placement and phase examples, without engine execution."""
from pathlib import Path
import sys
from common import ROOT, make_ledger, run

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds,s8


def step(value):return 1 if value>0 else -1


def spot(kind,ball,taker,direction):
    x,y=ball
    return {7:[8*step(x),y],8:[2*step(x),-33*direction],9:[8*step(x),36*step(y)],
            10:[0,28*direction],11:list(ball)}.get(kind,list(taker))


def attack_zone(point,role,direction):
    read,_,_=load_ds();x,y=point
    return y*direction>=0 and abs(y)>=role+12 and abs(x)<=read(0x776+(abs(y)>28))


def corner_step(timer,phase,at_target=True,*,immediate=False):
    if not at_target:return timer,phase,'walk'
    if phase:return timer,phase,'cross-and-state5'
    if timer:
        timer=(timer-1)&255
        if not immediate:return timer,0,'countdown'
    return timer,1,'ready-line-and-playflag0'


def code_set(address,parts):
    data=[]
    lines='\n'.join((ROOT/f'static/goal-exe/code/seg_0791_{p}.asm').read_text() for p in parts).splitlines()
    for pc in [address,address+16]:
        row=next(s for s in lines if s.startswith(f'{pc:04X} '))
        data.extend(bytes.fromhex(row.split('db ',1)[1].split(';',1)[0]))
    return [i for i in range(256) if data[i//8]&(1<<(i%8))]


def wall_points(point,direction):
    """7621 wall placement after its defending/geometry/slot predicates pass."""
    x,y=point
    if abs(y)<26:
        xs=step(x);ys=direction if abs(x)>=5 else 0
        anchor_x=int(x/2)-2*xs;anchor_y=y+5*direction-2*ys
    else:
        xs,ys=0,1
        anchor_x=x+(1 if x<0 else -1)*3
        anchor_y=((abs(y)-26)//2+28)*(1 if y<0 else -1)
    return [[anchor_x+xs*k,anchor_y+ys*k] for k in range(5)]


def calculations():
    read,_,_=load_ds()
    points=[spot(7,[9,12],[0,0],1),spot(8,[-1,-39],[0,0],1),spot(9,[0,39],[0,0],-1),
            spot(10,[5,20],[0,0],-1),spot(11,[-3,17],[0,0],1)]
    assert points==[[8,12],[-2,-33],[-8,36],[0,-28],[-3,17]]
    assert spot(9,[0,39],[0,0],-1)!=[8,-36]  # spot signs are from ball, not team mirroring
    depths=[s8(read(0x812+i)) for i in range(14)]
    assert depths==[0,5,7,10,10,14,16,15,15,17,18,18,19,14]
    fixed={hex(a):[s8(read(a)),s8(read(a+1))] for a in [0x640,0x642,0x644,0x820,0x822,0x824]}
    assert fixed=={'0x640':[11,0],'0x642':[-8,0],'0x644':[-9,0],
                   '0x820':[0,-1],'0x822':[-2,-1],'0x824':[-2,0]}
    snapshot=code_set(0x6bd1,['11']);wall_slots=code_set(0x7601,['12'])
    assert snapshot==[7,8,9,10,11] and wall_slots==[7,8,9,10,11]
    current=[0,25];new_spot=spot(9,[8,39],current,1)
    timer=3+10+10*attack_zone(current,5,1)
    wrong=3+10+10*attack_zone(new_spot,5,1)
    assert timer==23 and wrong==13
    sequence=[];t,p=2,0
    for _ in range(4):
        t,p,event=corner_step(t,p);sequence.append([t,p,event])
    assert sequence==[[1,0,'countdown'],[0,0,'countdown'],[0,1,'ready-line-and-playflag0'],[0,1,'cross-and-state5']]
    assert corner_step(1,0,immediate=True)!=(0,0,'countdown')
    assert corner_step(2,0,False)==(2,0,'walk')
    assert not attack_zone([0,20],13,1) and attack_zone([0,20],1,1)
    assert not attack_zone([0,12],1,1) and attack_zone([0,12],0,1)
    named=lambda x,y:y>=18 and abs(x)<=4
    assert [named(4,17),named(4,18),named(5,18)]==[False,True,False]
    assert int(-8/2)+0-1==-5 and 15+1*3==18  # throw-near receiver supplied coin1/0 and draw3
    near_wall=wall_points([0,25],1);far_wall=wall_points([0,26],1)
    assert near_wall==[[2,30],[1,30],[0,30],[-1,30],[-2,30]]
    assert far_wall==[[-3,-28],[-3,-27],[-3,-26],[-3,-25],[-3,-24]]
    assert far_wall!=[[-3,28],[-3,29],[-3,30],[-3,31],[-3,32]]
    return dict(spots=points,kickoff_depths=depths,fixed_points=fixed,snapshot_kinds=snapshot,wall_relative_slots=wall_slots,
                corner_current_point_timer=timer,incorrect_spot_point_timer=wrong,corner_sequence=sequence,
                free_kick_temporary_role={'original13_at20':False,'temporary1_at20':True,'role1_at12':False,'keeper0_at12':True},
                near_free_kick_taker_edges=[False,True,False],throw_receiver_point=[-5,18],
                wall_at25=near_wall,wall_at26=far_wall,
                controls={'mirror-corner-by-team':'rejected:ball-sign corner[-8,36] differs',
                          'timer-from-restart-spot':'rejected:13 instead of23','ready-on-decrement-to-zero':'rejected:ready one call too early',
                          'role1-is-keeper0':'rejected:attacking-zone threshold differs at12',
                          'normalise-far-wall-sign':'rejected:source far-wall y is negative for positive spot26'})


def build():
    calc=calculations()
    rows=[
        ('690C','Boundary finish chooses miss/goal/conditional event3/4 roll and clears mode/quality flags.', ['8327','7C39','80FB','8324'],'Shared finish fromT102; restart name does not mean penalty award.'),
        ('698E','Own-goal-line branch:keeper or coin ->corner,else event0+own-goal flag ->690C.', ['830B','8327','7C39'],'Own-goal routing depends on last holder and branch,not just crossing geometry.'),
        ('69BD','State1 targets post+role-depth,with holding-side last-slot and holder overrides;arrived holder state2,others0.', ['0812','0820/0822','pitch+7/+C/+12','8326'],'Starting shape and kickoff readiness depend on played roles and slot identities.'),
        ('6AAD','State2 waits all other required records ready;request snapshot,clear selectors/phase,launch6 toward mirrored0824,all state5.', ['9B55','830C/8323','0824'],'Kickoff is gated by multi-player readiness,not only the taker.'),
        ('6AF7','State3 targets exit unless already sentinel;arrived becomesstate4 and point/destination0644,then redraw.', ['0640/0642/0644','pitch+0/+7/+12'],'Half-end/walk-off coordinate states are not origin0,0.'),
        ('6B65','Resolve stored own-player identity to first squad slot1..11,or12 absent.', ['9976+10*side+2*role','country squad'],'Stored taker ID is distinct from global pitch slot.'),
        ('6BF1','Install holder and advance availability,clear selectors,set playflag1 with timer0,all statekind;choose spot and taker countdown.', ['830B/C/D/8302/8300','8315','9B55','8323','261A'],'Taker walks to a spot;playflag1 does not always mean a travelling ball.'),
        ('6D4E','Managed prompt or automatic skill pick;resolve ID,fall back nearest when absent,then6BF1.', ['9976','6B65','8311','CC7B','1FDD'],'Role-based selection is conditional on award and management context.'),
        ('6DEA','Submit restart line,then increment specified statistic on current awarded/holder side.', ['7B7E+10*side+n','2996'],'Corners/free-kicks counters are explicit writes,separate from display text.'),
        ('6E11','Normal-mode throw stoppage clears pending offside,checks subs,uses opposite nearest,starts7,submits line/message.', ['8326','830E','8311','8062'],'Throw taker uses nearest selector rather than one of named role2..5 picks.'),
        ('6E6E','Normal-mode corner uses opposite side role2/state9,marks830A,counts corner,sets marker direction.', ['8326','9976','830A','7B7E','26A0'],'Corner award crosses substitution,taker and state-placement boundaries.'),
        ('6F01','Normal-mode goal-kick or own-area free kick uses role5/state8;flag changes text/statistic.', ['8326','6D4E(5,8)','6DEA'],'A displayed free kick can use goal-kick-style mechanics and kicking-selected taker.'),
        ('6F3E','Clear offside/check subs;central directedy>=18 andabsx<=4 usesrole4,state11;else nearest,state11;countFK.', ['8311','6D4E(4,11)','6DEA'],'Named free-kick selection has a narrower trigger than all free-kick awards.'),
        ('6FB6','Choose own-area goal-kick-style free kick or ordinary free-kick route.', ['2EB8','2996','6F01/6F3E'],'Restart identity depends on the foul location/context.'),
        ('6FEE','At-target thrower counts down,thenmarksready,then next ready update launches to nearest andallstate5.', ['pitch+10','8323','8302','3B9E'],'Arrival,countdown,ready line and launch are separate updates.'),
        ('7069','State7 routes taker to6FEE,near selector to coin/roll target,others4B64.', ['8311','82F6/82F7','pitch+7/+8'],'Other players keep making target/draw decisions during the restart.'),
        ('70F6','At-target corner taker countdown->ready->cross3DF6,allstate5.', ['8323','pitch+10','8302'],'No single elapsed-time constant substitutes for this state machine.'),
        ('715A','State9 dispatches taker70F6 andothers4B64.', ['830B','pitch+12'],'Corner formation/targets remain coupled to ordinary destination logic.'),
        ('717F','Area-clear scan over22 records excludes keeper slots/holder;any outfielder in holder area blocks.', ['2EB8','045D','pitch point'],'Goal-kick readiness depends on other players leaving the area.'),
        ('71E8','At restart spot wait area clear,step target back togoal line/markready,then long-ball;offspot redirect via8315.', ['8315','8323','830C/D','3B15'],'Goal-kick has an extra positioning phase instead of ordinary countdown alone.'),
        ('7287','State8 taker71E8;keeper slots usepost,players in holder area targety0,others4B64.', ['2EB8','045D','pitch+7/+8'],'Clearing the area is part of the restart transition.'),
        ('74C2','Ready free-kick taker waits opposite keeper atabs y37,temporarilysetsplayedrole1 acrosscoin/attack-zone test,restores,then shot4 or pass.', ['player+6','8323','2F28','3C3F/3323'],'Temporary role1 changes shot eligibility;it is sweeper code,not keeper0.'),
        ('7621','State11 taker74C2;defending relative slots7..11 formwall under spot guards;others4B64 with defender spacing.', ['CS:7601','2BB1','8315','pitch+7/+8/+12'],'Wall selection uses relative squad slots,not role/skill number.'),
        ('6ECF','Penalty stoppage clears offside,whistle/checksubs,role3/state10,counts penalty andsets8324.', ['830E','8062','6D4E','7B7E+2','8324'],'Penalty setup differs from ordinary guarded throw/corner paths.'),
        ('72F2','State10 taker moves through spot,waitsallstate0,sets run-up target,different normal/shootout line,then shot3/state5.', ['8315','8323','8326','830C/D','3C3F'],'Penalty timing/readiness is a distinct machine from free kicks.'),
        ('73BA','State10 active taker72F2;others mode/keeper/side-specific waiting points andstate0 whenarrived.', ['8326','0822/084E','pitch+7/+8/+12'],'Waiting-player placement affects penalty readiness.'),
    ]
    rows=[('0791:'+a,m,f,e) for a,m,f,e in rows]
    examples=[
        dict(id='corner-setup-to-kick',inputs={'ball':[8,39],'chosen_taker_current':[0,25],'played_role':5,'direction':1,'table_byte':3,'initial_phase':0},
             steps=['spot(8,36);install holder,clearC/D,playflag1,timer0,allstate9,snapshot request',
                    'taker countdown23 from current attacking-zone predicate;walking updates do not spend it',
                    'at-target positive countdown decrements;zero-entry readies andstopsplayflag;nextreadycall cross/state5'],
             prediction={'spot':[8,36],'countdown':23,'ready_and_launch_separate':True},
             limits='Source-conditioned setup/handler sequence,not a full legal fixture or observed duration. Managed choice/natural key input not exercised.'),
        dict(id='free-kick-context',inputs={'spot':[0,20],'original_role':13,'temporary_role':1,'opposing_keeper_abs_y':37,'coin':True},
             steps=['near-central award can pickrole4','at-target countdownready','role1 across2F28 opensattackingzone','restore13 before shot event4'],
             prediction={'normal_role13_zone':False,'temporary_role1_zone':True,'launch_event':4,'launch_skill':12,'initial_quality_skill':11},
             limits='Other74C2 readiness gates assumed;keeping role0 is not substituted. No measured free-kick success probability.'),
        dict(id='countdown-edge',inputs={'timer':2,'phase':0,'at_target':True},steps=calc['corner_sequence'],
             prediction=['countdown','countdown','ready','cross'],limits='Eligible taker updates,not game minutes/host time. Entire player placement not simulated.'),
        dict(id='far-wall-candidate',inputs={'spots':[[0,25],[0,26]],'kicker_direction':1,'defending_relative_slots':[7,8,9,10,11]},
             steps=['defending,forward-facing kick andabsY-absX>10 guards assumed','nearbranch y25 gives wall row30','farbranch y26 usesopposite-sign7920 selector;direct stores have no later mirror'],
             prediction={'at25':calc['wall_at25'],'at26':calc['wall_at26']},
             limits='Instruction-derived candidate quirk;port matches. Natural free-kick reachability/frequency and whole-match consequence not established;no sign fix authorised.'),
    ]
    return make_ledger('T104a',Path(__file__).resolve(),['A restart is a phase transition','Spot, taker and placement rules','Ready, wait and execute','Worked paths and evidence limits'],
                       rows,examples,calc,['restarts','rare','geometry','takers'],addresses=['0791:2F28','0791:2A15','0791:28B2'],
                       artifacts=['notes/engine-study/T102/T102c-v1.json'])


if __name__=='__main__':run('T104a',build)
