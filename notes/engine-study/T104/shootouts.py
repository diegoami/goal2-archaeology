#!/usr/bin/env python3
"""Source-derived extra-time/order/shootout bookkeeping; no engine or key execution."""
from pathlib import Path
import sys
from common import ROOT,make_ledger,run

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds,s8


def speed(value):
    if value<5:value+=1
    return max(2,value)


def descending(rows):
    result=list(rows)
    for i in range(len(result)-1):
        for j in range(i+1,len(result)):
            if result[j][1]>result[i][1]:result[i],result[j]=result[j],result[i]
    return result


def tally(outcomes,initial=(0,0),starting=0):
    score=list(initial);remaining=[5,5];side=starting;round_no=1;trace=[]
    continues=lambda:score[0]<=score[1]+remaining[1] and score[1]<=score[0]+remaining[0]
    for made in outcomes:
        if not continues():break
        score[side]=(score[side]+int(made))&255
        if remaining[side]:remaining[side]-=1
        if side==starting and remaining[side]==0:remaining[1-side]=1
        if side!=starting:round_no=(round_no+1)&65535
        trace.append(dict(side=side,made=bool(made),score=score.copy(),remaining=remaining.copy(),round_after=round_no))
        side=1-side
    return dict(score=score,remaining=remaining,round=round_no,kicks=len(trace),continues=continues(),trace=trace)


def prompt(keys,role=3):
    mode='prompt'
    for key in keys:
        if mode=='board':mode='prompt';continue
        if key=='space' and role!=1:mode='board'
        elif key=='enter':return 'highlighted-player'
    return None


def calculations():
    read,_,_=load_ds()
    kinds=[i for i in range(256) if read(0x693a+i//8)&(1<<(i%8))]
    assert kinds==[4]+list(range(8,204))
    assert [k in kinds for k in [1,4,7,8,101,203,204]]==[False,True,False,True,True,True,False]
    assert [speed(v) for v in [0,1,2,4,5,9,255]]==[2,2,3,5,5,9,255]
    assert min(5,9+1)!=speed(9)
    assert [600*10,1000*10]==[6000,10000]  # nominal calibration units,not measured host time
    assert not prompt(['space','enter']) and prompt(['space','enter','enter'])=='highlighted-player'
    assert prompt(['space','enter'],role=1)=='highlighted-player'
    ranked=descending([(1,100),(2,80),(3,80)])
    assert ranked[0][0]==1
    assert descending([(1,80),(2,80),(3,100)])==[(3,100),(2,80),(1,80)]
    # Auto order may contain unavailable top11.6BF1/2A15 choosescurrent beforeA006 advances order cursor.
    order=[11,5,2,3,4,6,7,8,9,10,1];available=set(range(1,11));chosen=order[0]
    while chosen not in available:chosen=2 if chosen==11 else chosen+1
    assert chosen==2 and order[1]==5 and chosen!=5
    partial=[2,3,4,5,6,7,8,9]+[0,0,0]
    assert partial[8]==0  # fixed11 cursor's first probe after eighth entry;dummy availability unresolved
    early=tally([True,False]*5)
    assert early['kicks']==6 and early['score']==[3,0] and not early['continues']
    after_first_sd=tally([False]*10+[True],initial=(2,2))
    full_sd=tally([False]*10+[True,False],initial=(2,2))
    assert after_first_sd['score']==[3,2] and after_first_sd['continues']
    assert full_sd['kicks']==12 and full_sd['score']==[3,2] and not full_sd['continues']
    direction=[]
    for side in [0,1]:
        half=s8((-side)&255);flag=int(half<0 or 0>half)
        direction.append(s8(read(0x7920+(flag^side))))
    assert direction==[-1,-1]
    assert [read(0x720+i) for i in [0x11,0x1d,0x26]]==[0,20,40]
    return dict(decider_set=kinds,speed_edges=[2,2,3,5,5,9,255],nominal_poll_units=[6000,10000],
                extra_time_entry={'remaining':31,'elapsed':89,'half_threshold':15,'subtick':0,'end_flag':0,'permission':1},
                after_first_eligible_clock_advance={'remaining':30,'elapsed':90},shootout_kicker_directions=direction,
                first_auto_fallback={'top_order_entry':11,'unavailable':[11],'actual_first':2,'second_order_entry':5},
                managed_partial_next_probe=0,early_stop=early,sudden_death_after_first=after_first_sd,sudden_death_complete=full_sd,
                f098_score_boundary={'fixture_goal_bytes':[2,2],'working_tally':[3,2],'fixture_result':0},
                shootout_goal_effect={'working_score_delta':1,'normal_player_goal_delta':0,'normal_scorer_log':False,'goal_commentary_perf_delta':40},
                controls={'wrong-extra-entry30':'rejected:first eligible remaining29,not30','outfield-only-ranking':'rejected:keeper1 is highest in supplied order',
                          'filter-before-current-kick':'rejected:first5 instead of2','stop-after-first-sudden-death-kick':'rejected:other side must getitskick',
                          'space-dismissal-commits':'rejected:secondEnter onlydismissesboard','clamp-raw-speed9':'rejected:9 remains9',
                          'count-pk-in-normal-player-goals':'rejected:normal6443 branch skipped','overwrite-fixture-with-working-pk-tally':'rejected:F098 updatesresult only'})


def build():
    calc=calculations()
    rows=[
        ('0B7C','Y/N prompt waits600 polls,returnsYes onlyforwaitingY;otherkey/no-keyNo.', ['CC2E','A976','prompttext'],'Replay/save/summary question isdistinctfromtakerprompt1000polls.'),
        ('0C0B','Unsigned speed/delaybyte incrementsbelow5 thenminimum2;largervaluespreserved.', ['game+3F'],'Shootout temporarilychangespace andrestoresoldbyte later.'),
        ('9B0C','FirstETwrapper setsremaining31,elapsed89,half15,subtick/endflag0,permission1,managedmenu if80FD,startingselector,983F.', ['831B/831F/8319/831D/8326','9B41','80FD/831A'],'ETclockentry valuesarepartofclock/directionprotocol,notliteral31minutes.'),
        ('9B5B','SecondETwrapper grantspermission,optionalmanagedmenu,oppositekickoffselector,983F.', ['9B41','80FD/831A','830B'],'UsesremainingETclock ratherthanindependentnewmatchinitialisation.'),
        ('9B93','Managedshootoutorder selectsallavailableplayers,avoidsduplicates;Enterappend,Escundo,finishatavailablecount.', ['parent12-byteper-sideorder','3216','playercards'],'Order canhavefewerthan11entries;genuineinputs andzero-entrycursor behaviorneedtheir ownlimits.'),
        ('9ED3','Fillall11pitchslotsincludingkeeper;descendingpairwise effectivepenalties12sort,noavailabilityfilterhere.', ['278A(12)','parentorderarrays'],'Unavailableentryinrankarraydoesnotmeanthatplayernecessarilytakescurrentkick.'),
        ('A006','Set8319=-side,setupcurrentorderedtaker,thenadvanceordercursor1..11pastavailability;mode8324andwatchedsweepsuntilkick/flightsettles.', ['8319/8324/8325','6BF1/2A15','parentcursor','9564'],'Currentfallbackandnext-orderadvancement areseparate;clockbytesrepurposedfordirection.'),
        ('A10A','Savedpace,forcewatched,selectorders,remainingkicks/rounds,andearly/suddendeathloopusingworkingtally;restorepaceandquickflag.', ['9A3E/9A3F','831D','9B3C','parentstackcounters'],'Fiveinitialkicks thenequalisation logic;normalstatistics/scorer handlingisphase-dependent.'),
        ('CC2E','Speakeroff;up ton keypolls eachfollowedbycalibrateddelay10 whennokey;zero n no loop.', ['0723','1E09(10)'],'Nominalwaitunitsnotmatchclockticks ormeasuredhostduration.'),
        ('CC7B','Validatecurrentpickavailability/slot<=11,automaticfallback,C/Enter/Esc/timeoutchoices,boardSpaceextra readforroles2..5,returnplayerID.', ['9976','6B65','1F3C/1FDD','1000polls','CF3A'],'Spaceboarddismissaldoesnotcommittaker;selection identitynotasquadslot.'),
    ]
    rows=[('0791:'+a,m,f,e) for a,m,f,e in rows]
    examples=[
        dict(id='sudden-death-pair',inputs={'initial_working_score':[2,2],'initial10outcomes':'allmiss','next_pair':[True,False],'starting_side':0},
             steps=['after10tied,bothremaining0','firstSDscore3,2 resetsopponentremaining1,continue','secondside misses,remaining0,0,stop'],
             prediction={'kicks':12,'working_score':[3,2],'round':7},limits='Supplied bookkeeping outcomes,not12original kicks. F098fixturegoalbytes remain2,2 atthatboundary;result becomes0.'),
        dict(id='unavailable-top-entry',inputs={'unmanaged_order':[11,5,2,3,4,6,7,8,9,10,1],'unavailable_slot':11,'side_base':0},
             steps=['A006calls6BF1 onentry11','2A15wraps toavailable2forcurrentkick','nextordercursor2 names5'],
             prediction={'first_kicker':2,'next_order_entry':5},limits='Source-conditioned availability example,notobservedfrequency. Partialmanagedzero-entryavailability remainsunresolved.'),
        dict(id='taker-board-read',inputs={'role':3,'keys':['Space','Enter','Enter']},steps=['Spaceopensboard','firstEnterdismissesboard','nextpromptEnterselectsavailablehighlight'],
             prediction={'selected':'highlighted-player','requires_board_dismissal':True},limits='Source stateprojection,notgenuinekey-input evidence;#400gaps remain.'),
        dict(id='mode-dependent-goal',inputs={'shootout_end_mode_8326':1,'goal_template':38},steps=['67B6workingtallyincrement','skipnormal6443/playergoal/log branch','1EB5stillappliesgoalcommentarydelta before ring'],
             prediction=calc['shootout_goal_effect'],limits='Named-player commentary contextassumed;MOM/post-fixturereaders stillneedphase-awareinterpretation. No newenginecall.'),
    ]
    return make_ledger('T104d',Path(__file__).resolve(),['Extra time and overloaded clock state','Ordering, eligibility and one kick','Round stopping and score representations','Prompts, timing and evidence limits'],
                       rows,examples,calc,['takers','restarts','frame','geometry','duels'],
                       addresses=['0791:F098','0791:A3DE','0791:2BE5','0791:2A15','0791:1EB5','0791:1E53','0791:67B6'],
                       sources=['findings/F023-the-stage-builders-write-the-competition-calendar-from-ranked-pots-and-a-points-sort-with-no-coin.md'])


if __name__=='__main__':run('T104d',build)
