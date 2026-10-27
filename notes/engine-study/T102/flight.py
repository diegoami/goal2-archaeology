#!/usr/bin/env python3
"""Source-derived launch/flight arithmetic with supplied branches; no engine execution."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT,BASE,ROUTINES,pin,sha,write_new

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds,s8,s16


def signed_byte(value):
    return s8(value&255)


def direction(value):
    return 1 if value>0 else -1


def launch(ball,target,event,value=0,extra=0,*,keeper=False,own_strip=False,same_receiver=True,halve=False,extra_penalty=False):
    """Projection only where the conditional miscue branch is bypassed."""
    dx,dy=[signed_byte(t-b) for b,t in zip(ball,target)]
    a,b=abs(dx),abs(dy);vx=vy=0
    if a>b:
        vx=direction(dx);timer=a
        if b>=a//2:vy=direction(dy);timer=(timer+b)&65535
    else:
        vy=direction(dy);timer=b
        if a>0 and a>=b//2:
            vx=direction(dx);timer=(timer+a)&65535
            if b>=a//2:vy*=2
    base_timer=timer
    if event==6:
        if timer>20:event=7
        elif keeper and own_strip:event=8
    if event in [1,2]:timer=max((timer+5)&65535,((value+extra)&65535)//3)
    elif event in [3,4]:timer=max((timer+5)&65535,((value+(extra if extra_penalty else 0))&65535)//3)
    elif event!=8 and timer>1 and not same_receiver:
        raise ValueError('miscue branch needs separate supplied outcome; outside this projection')
    adjusted=timer;divisor=2 if halve else abs(vx)+abs(vy)
    timer=max(2,timer//divisor)&65535
    return dict(delta=[dx,dy],velocity=[vx,vy],velocity_words=[vx&65535,vy&65535],base_timer=base_timer,
                event=event,adjusted_timer=adjusted,divisor=divisor,timer=timer,
                projected=[signed_byte(p+v*timer) for p,v in zip(ball,[vx,vy])])


def draw(seed,bound):
    seed=(seed*0x7abd+0x1b0f)&65535
    return seed,(seed*bound>>16)+1


def shot_flight_tail(event,seed,*,skip_unused_coin=False):
    count=0
    if event==2:return dict(air=True,seed=seed,draws=count)
    if skip_unused_coin and event!=4:
        coin=False
    else:
        seed,r=draw(seed,2);count+=1;coin=r==1
    air=coin and event==4
    if not air:
        seed,r=draw(seed,3);count+=1;air=r==1
    return dict(air=air,seed=seed,draws=count)


def ball_step(point,velocity,timer,air):
    candidate=[signed_byte(p+(v&255)) for p,v in zip(point,velocity)]
    remaining=(timer-1)&65535 if timer else 0
    travel=((abs(s16(velocity[0]&65535))+abs(s16(velocity[1]&65535)))*remaining)&65535
    kept_air=bool(air and travel>=3)
    accepted=abs(candidate[0])<=9 and abs(candidate[1])<=39
    current=candidate if accepted else list(point)
    return dict(candidate=candidate,point=current,timer=remaining,travel=travel,air=kept_air,
                wide_accepted=accepted,outside_play=abs(current[0])>8 or abs(current[1])>37)


def calculations():
    read,_,sources=load_ds()
    assert [signed_byte(read(0x7920+i)) for i in range(2)]==[-1,1]
    event_elements={str(e):read(0x779+e) for e in range(1,12)}
    assert list(event_elements.values())==[11,4,12,12,7,6,6,1,2,2,4]
    modes=[[read(base+i) for base in [0x796,0x798,0x79a,0x79c]] for i in range(2)]
    assert modes==[[4,6,11,20],[2,4,10,30]]
    examples=[launch([0,0],[8,3],1,90,12),launch([0,0],[4,8],3,90,12),
              launch([0,0],[7,14],6),launch([0,0],[1,0],6),launch([0,0],[0,0],6),
              launch([0,20],[0,38],1,98,56)]
    assert [(e['velocity'],e['timer'],e['projected']) for e in examples]==[
        ([1,0],34,[34,0]),([1,2],10,[10,20]),([1,2],7,[7,14]),
        ([1,-1],2,[2,-2]),([0,-1],2,[0,-2]),([0,1],51,[0,71])]
    assert launch([0,0],[7,14],6,halve=True)['projected']==[10,20]
    assert launch([0,0],[4,8],3,90,12,extra_penalty=True)['timer']==11
    assert [0,0]!=examples[4]['velocity']
    ordinary=shot_flight_tail(1,0);optimised=shot_flight_tail(1,0,skip_unused_coin=True)
    assert ordinary['air']==optimised['air']==True
    assert [ordinary['draws'],optimised['draws']]==[2,1]
    normal_next=draw(ordinary['seed'],100)[1];changed_next=draw(optimised['seed'],100)[1]
    assert [normal_next,changed_next]==[97,24]
    assert shot_flight_tail(2,0)==dict(air=True,seed=0,draws=0)
    first_step=ball_step([0,20],[0,1],51,False)
    boundary=ball_step([0,37],[0,1],1,True)
    assert first_step['point']==[0,21] and first_step['timer']==50 and first_step['travel']==50
    assert boundary['point']==[0,38] and boundary['outside_play'] and boundary['timer']==0 and not boundary['air']
    edge=ball_step([0,0],[0,1],3,True)
    assert edge['travel']==2 and not edge['air'] and (1*3>=3)
    assert ball_step([0,0],[256,0],2,True)['point']==[0,0]
    assert ball_step([0,0],[256,0],2,True)['travel']==256
    return dict(event_elements=event_elements,mode_not9_and_mode9=modes,launch_examples=examples,
                ordinary_shot_tail=ordinary,skip_unused_coin_control=optimised,next_common_rand100=[normal_next,changed_next],
                first_shot_step=first_step,boundary_step=boundary,air_threshold_step=edge,
                controls={'universal-halving':'rejected:projection[10,20] instead of[7,14]',
                          'extra-on-penalty-event3':'rejected:timer11 instead of10',
                          'zero-vector-idle':'rejected:original velocity[0,-1]',
                          'remove-unused-shot-coin':'rejected:next rand10024 instead of97',
                          'air-test-before-countdown':'rejected:remaining travel2 must clear air'},
                ds_sources=sources)


def build():
    calc=calculations()
    rows=[
        ('34C1','Byte-difference vector/base timer; event6 rewrite; two skill-duration branches or conditional miscue; divide by absolute-velocity sum, min2, project endpoint.',
         ['ball+6/+8/+A','DS:8327/8302/830B/830C/8323/8313','pitch+F/+11','DS:0779'],'Coarse launch trajectory and future receiver/difficulty state, not exact target arrival.'),
        ('3B15','Use kicking2/4 draw with minimum30, add directed longitudinal reach, launch10 and set flight.',
         ['278A(2)','DS:830C/8303','2BE5'],'A skill floor can hide range changes while still consuming the draw.'),
        ('3C20','Increment side statistic+4 only while8326 is clear.',
         ['DS:7B7E+10*side+4','DS:8326'],'A separate counted outcome; not every attempted shot increments this helper.'),
        ('3C3F','Nonheader two-coin ball-x jitter, conditional80FB quality flag, mirrored goal target, launch, commentary,stat+3 and event-specific flight tail.',
         ['DS:80FB/8324/8326/830C/8303','DS:0646','DS:078E','287C'],'Attempt count and submitted commentary differ from later scoring/on-target resolution.'),
        ('3EC5','Wrap3C3F with event1 and supplied low-byte commentary template.',
         ['event1','template argument'],'Ordinary shot entry shares common launch/shot mechanics.'),
        ('3EDF','Wrap3C3F with event2 and template14h.',
         ['event2','template20'],'Heading branch skips shot-x jitter and has deterministic flight tail.'),
        ('3EF8','Input mode9 selects kicking2/div4/floor30/emitted10; other modes select heading4/div6/floor20/emitted11.',
         ['DS:0796/0798/079A/079C','278A','DS:830C/8303'],'Input mode is not the emitted launch event; heading can determine clearance reach.'),
        ('3FAD','Coin/keeper branch chooses wide random sign-based target or narrow long target, launches supplied event, sets flight and submits21/22.',
         ['player point','rand8/rand40','34C1','DS:8303'],'Clearance can deliberately aim beyond playable width/length.'),
        ('408E','Coin chooses random target or table/skill long target, with input mode11.',
         ['main coin','3FAD/3EF8'],'Same broad action has different target and draw pathways.'),
        ('40BC','Holder outside own half, beyond opposite marker,abs(y)<35,abs(x)<4.',
         ['DS:830B/82E3','2C54'],'Geometry opens the advanced central holder branch; no explicit skill read here.'),
        ('4151','Test current holder point with own-strip predicate; on success clear via3FAD input9.',
         ['DS:830B','2EB8','3FAD'],'Despite historical keeper name, this body does not itself test keeper slot.'),
        ('835F','Low word of (absolute word vx+absolute word vy)*remaining timer.',
         ['ball+6/+8/+A'],'Remaining travel feeds flight flags and contests; it is not a standalone speed/height byte.'),
        ('83A2','Compute candidate from low velocity bytes; decrement timer before air test, wide-bound placement/drawing, then strict-bound offside/restart dispatch.',
         ['ball+0/+1/+6/+8/+A/+D','DS:830E/830C/830A/830D/8325/8327'],'Ball boundary crossing is a transition into resolution, not an unconditional goal.'),
        ('869F','Install holder slot; clear timer,receiver/challenger selectors,play/flight flags and event.',
         ['DS:830B/830C/830D/8302/8303/8327','ball+A'],'Possession is several state writes; a caller can subsequently restore a flag.'),
        ('593B','Conditional woodwork chance, event/template guards; negate both velocities, quarter timer with floor1,submit line and clear8324.',
         ['DS:07FC/8324/8327','ball+6/+8/+A'],'Bounce changes direction and remaining duration; quartering timer is not quartering velocity.'),
        ('59B3','Active-mode nonkeeper moving ball at abs(y)=37,abs(x)<2 may call593B with table template; inactive path leaves return local unwritten.',
         ['DS:8325/8324/830B','DS:07FA','ball point/timer'],'Woodwork eligibility and stack-residue boundary must not be silently normalised.'),
    ]
    examples=[
        {'id':'launch-divisor','inputs':{'ball':[0,0],'target':[7,14],'event':6,'same_receiver':True},
         'steps':['byte deltas7,14 -> vector(1,2),base timer21','event6 ->7','divide21 by3;minimum2'],
         'prediction':{'event':7,'timer':7,'projected':[7,14]},
         'limits':'Miscue bypassed by equal slot selectors; supplied arithmetic state, not a natural observed fixture.'},
        {'id':'shot-range-and-step','inputs':{'ball':[0,20],'target':[0,38],'event':1,'effective_shooting':98,'cached_extra':56},
         'steps':['vector(0,1),base18','max(18+5,(98+56)//3)=51','divisor1 ->timer51,projected(0,71)','one supplied step ->(0,21),timer50,travel50'],
         'prediction':calc['first_shot_step'],
         'limits':'Supplied effective value/cache, jitter netzero and no intervening boundary/contest; projected endpoint is not actual final location or a goal guarantee.'},
        {'id':'unused-shot-coin','inputs':{'event':1,'tail_entry_seed':0},
         'steps':['source consumes coin even though event1 discards its result','rand3 follows;both original andskip-coin control setair','next commonrand100 differs'],
         'prediction':{'normal_draws':2,'optimised_draws':1,'next_rand100':[97,24]},
         'limits':'Tail-only arithmetic start, not the full shot entry seed or an observed seeded match.'},
        {'id':'boundary','inputs':{'point':[0,37],'velocity':[0,1],'timer':1,'air':True,'pending_offside':False},
         'steps':['timer0 thenair clears','wide bounds accept(0,38)','strict bounds reject;centre/forward side dispatches690C'],
         'prediction':calc['boundary_step'],'limits':'690C finish/restart outcome is not simulated here; no automatic goal or penalty-award inference.'},
    ]
    artifacts=['notes/engine-study/T102/launch-helper-v1.md','notes/engine-study/T99/contests-v2.json']
    sources=['runtime/original_match/port/ball.py','runtime/original_match/port/motion.py','runtime/original_match/port/contests.py',
             'static/goal-exe/code/seg_0791_05.asm','static/goal-exe/code/seg_0791_06.asm','static/goal-exe/code/seg_0791_07.asm',
             'static/goal-exe/code/seg_0791_09.asm','static/goal-exe/code/seg_0791_14.asm','static/goal-exe/code/seg_23E4_01.asm',
             *calc['ds_sources']]
    return pin(dict(task='T102b',status='proposed; source-derived explanation',method=__doc__,
                    sections=['Aiming, event and skill are separate','Launch vector and duration','Shot and flight bookkeeping','Worked boundaries and limitations'],
                    routines=[dict(address='0791:'+a,mechanism=m,fields=f,visible_effect=e,
                                   limits='Source-conditioned mechanism; no new engine execution or natural-frequency proof.') for a,m,f,e in rows],
                    examples=examples,calculations=calc,supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in artifacts},
                    assistance={'agent':'/root/launch_arithmetic','requested_model':'gpt-6.1-sol','requested_effort':'xhigh',
                                'effective_settings':'not exposed','role':'bounded read-only implementation assistance, not independent review'},
                    analysis_sha256=sha(Path(__file__).read_bytes())),
               ['0791:'+a for a in ROUTINES['T102b']]+['0791:287C','0791:278A','0791:2E00','0791:2DCA','0791:29B3'],sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T102/T102b-v1.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: six launch literals,event/mode tables,shot-tail seed divergence,ball-step boundaries,5 altered-rule controls')
    else:write_new(path,data);print('wrote T102b source-derived ledger; no engine execution')


if __name__=='__main__':main()
