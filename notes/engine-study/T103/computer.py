#!/usr/bin/env python3
"""Source-derived AI branch/latch and emergency-role projections; no engine execution."""
from pathlib import Path
import sys
from common import ROOT,make_ledger,run
sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds,s8


def branch(score,side,managed=False,mode8326=False):
    if mode8326:return 'mode-skip'
    if managed:return 'skip'
    gap=abs(s8((s8(score[0])-s8(score[1]))&255))
    ahead=score[side]>score[1-side]
    return 'BD83' if gap<2 else ('BF6B-exclude' if ahead else 'BF6B-include') if gap==2 else ('C0DF' if ahead else 'C01A')


def draw_bits(value,draws,include=True):
    for k in draws:
        value=(value | (1<<(k-1))) if include else (value & ~(1<<(k-1)))
    return value


def emergency(roles,available,removed,heights,read):
    roles=list(roles);selected=None
    if removed==0:
        selected=next((i for i in range(1,11) if available[i]),None)
        if selected is not None:roles[selected]=0
    elif removed in [1,2]:
        counts=[sum(ok and p==r for ok,p in zip(available,roles)) for r in range(14)]
        donor=next((read(0xa29+i) for i in range(1+int(removed==2),6) if counts[read(0xa29+i)]>read(0xa2e+i)),0)
        selected=next((i for i,(p,ok) in enumerate(zip(roles,available)) if p==donor and ok),None) if donor else None
        if selected is not None:roles[selected]=removed
    elif removed in [3,4]:
        roles=[2 if ok and p in [3,4] else p for p,ok in zip(roles,available)]
    elif removed in [12,13]:
        selected=next((i for i,(p,ok) in enumerate(zip(roles,available)) if p in [9,10,11] and ok),None)
        if selected is not None:roles[selected]=read(0xa28+int(heights[selected]>=72))
    return dict(roles=roles,selected_slot=None if selected is None else selected+1)


def calculations():
    read,_,_=load_ds()
    cases=[branch([1,0],0),branch([2,0],0),branch([2,0],1),branch([3,0],0),branch([3,0],1),branch([3,0],0,True),branch([255,0],0)]
    assert cases==['BD83','BF6B-exclude','BF6B-include','C0DF','C01A','skip','BD83']
    assert branch([3,0],1,mode8326=True)=='mode-skip'
    assert draw_bits(0,[2,2])==2 and draw_bits(0,[2,2])!=3
    base=128
    stronger=draw_bits(base,[1,1]);after_gap2=draw_bits(stronger,[1,1,1],False)
    assert [stronger,after_gap2]==[129,128]
    incl=draw_bits(0,[1,1,1,1,1])|32
    assert incl==33 and incl!=63
    # A second C01A call with its latch set makes no new draws/changes.
    again=incl;assert again==33
    roles=[0,2,2,3,4,5,6,7,8,9,13];ok=[True]*11;heights=[70]*11
    keeper_available=ok.copy();keeper_available[1]=False
    keeper=emergency(roles,keeper_available,0,heights,read)
    sweeper=emergency(roles,ok,1,heights,read)
    centre=emergency(roles,ok,2,heights,read)
    fullbacks=emergency(roles,ok,3,heights,read)
    short=emergency(roles,ok,13,heights,read);heights[9]=72;tall=emergency(roles,ok,13,heights,read)
    assert keeper['selected_slot']==3 and keeper['roles'][2]==0
    assert sweeper['selected_slot']==2 and sweeper['roles'][1]==1
    assert centre['selected_slot']==6 and centre['roles'][5]==2
    assert fullbacks['roles'][3:5]==[2,2]
    assert short['selected_slot']==10 and short['roles'][9]==13 and tall['roles'][9]==12
    assert [read(0xa29+i) for i in range(1,6)]==[2,5,6,7,8]
    assert [read(0xa2e+i) for i in range(1,6)]==[1,0,0,0,0]
    assert emergency(roles,[False]*11,0,heights,read)['selected_slot'] is None
    return dict(mode8326_policy_call=False,branch_cases=cases,duplicate_two_draw_mask=2,gap2_reset_and_exclude=[129,128],five_repeats_and6=33,latch_repeat=again,
                emergency_keeper=keeper,emergency_sweeper=sweeper,emergency_centre_back=centre,fullbacks=fullbacks,
                forward_short_tall=[short,tall],donor_priority=[2,5,6,7,8],donor_threshold=[1,0,0,0,0],
                controls={'update-managed-side':'rejected:managedbranchskip',
                          'random-distinct-settings':'rejected:five identicalrand1 plusfixed6 sets33,not63',
                          'gap2-does-not-reset':'rejected:BD83 baseline/stronger step precedes3changes',
                          'ignore-latch':'rejected:secondextremegapcallmakesnonewdraws',
                          'best-keeper-emergency':'rejected:firstavailable3 is selectedwithoutkeepingcomparison',
                          'height-threshold-strict-greater72':'rejected:height72 selects12',
                          'convert-only-one-fullback':'rejected:bothavailable3/4become2'})


def build():
    calc=calculations()
    rows=[
      ('0791:BBFF','Storecurrentcountrytacticbyte then3431 fornonzero20squadwords withoutclear.', ['country+2D','player+F'],'Currentteamchange canrederivepersonaloverrides.'),
      ('0791:BC5D','Clearall20ownbytes;BBFF R008;sort52CC;XIplayedrolesfromR011.', ['9B7C','9F02','player+F/+6'],'Reset is notmerelyrestoringteamtactics;order precedesroleassignment.'),
      ('0791:BD03','Sum377E forbothXI andcompareunsigned strictgreater.', ['country.squad','377E'],'Tieisnotstronger;differentfromrank/managerability orwatchedskill.'),
      ('0791:BD83','RestoreR008;side1host+stronger sets1;strongerincludesrand6twice;clearbothlatches.', ['80FC','8332/8334','BBFF'],'Drawscanrepeat;settings7/8remainbaseline.'),
      ('0791:BF6B','BD83 resetthen3rand6 includeswhenbehind orexcludeswhenahead.', ['BBFF','scorebranch'],'Not3distinctsettingsandnoteditofoldcurrentbytealone.'),
      ('0791:C173','Normal-play8326clear caller only;after-goal policy:managedskip,abs signed-bytegap<2 BD83,==2 BF6B,>2 extremeahead/behind.', ['9B3C','0B77','65FE'],'Notperiodicfirst-minuteAIchange;rawscorewrapcontextmustbequalified.'),
      ('0791:BEC7','Firstavailableplayed9..11 convertedbyheight<72 to13,else12;returnafterfirst.', ['2FAD','0A28'],'Heightchangesrolepolicyhere,notdirectheadingconteststrength.'),
      ('0791:C01A','Ifincludelatchclear,5rand5includesandfixed6,BBFF,setlatch;slot9not12/13 permitsBEC7+230C.', ['8332','player+6'],'Onceperstretch;laterBD83 resetslatch. Existingstrikerselsewheredonotsufficeforslot9test.'),
      ('0791:C0DF','Ifexcludelatchclear,5rand5excludesandfixed6,BBFF,setlatch.', ['8334','country+2D'],'Noextraformationconversioninthisroutine.'),
      ('0791:C24D','Emergencykeeper:firstavailableoutfieldslot2..11 becomesplayed0.', ['3216','player+6'],'No keeping/height/strengthmaximisation.'),
      ('0791:C2A8','AvailableXIrolecounts;request1priorityindex1..5,request2index2..5;firstsurplusdonor thenfirstavailableidentity.', ['0A29/0A2E','player+6'],'No surplus meansnochange;strictcount>threshold.'),
      ('0791:C406','EveryavailableXIplayed3/4 becomes2.', ['CSC3E6','player+6'],'Convertsallmatchingavailablefullbacks,notjustone.'),
      ('0791:C48D','Dispatchremovedplayed0->C24D;1/2->C2A8;3/4->C406;12/13->BEC7;then230C.', ['pitch+D','player+6','country.squad'],'Role repair/removal flow differsfromordinarybenchsubstitution.'),
    ]
    examples=[
      dict(id='gap-and-managed',inputs={'scores':[3,0],'side0_managed':True,'side1_managed':False},steps=['managedside0skip','signedgap3','side1unsignedbehind invokesC01A'],prediction={'side0':'skip','side1':'C01A'},limits='Sourcepolicyprojection;noactualgoalornewAIexecution.'),
      dict(id='duplicate-settings',inputs={'old_mask':0,'include_latch':0,'rand5':[1,1,1,1,1]},steps=['fivetimesinclude1','includefixed6','setlatch','repeatcallreturns'],prediction={'mask':33,'fresh_draws_first':5,'fresh_draws_repeat':0},limits='Suppliedlegaldraws;doesnotgenerateRNGorassumeindependence.'),
      dict(id='emergency-centreback',inputs={'requested_role':2,'available_roles':[0,2,2,3,4,5,6,7,8,9,13]},steps=['skippriorityindex1role2','firstsurplusrole5count1>0','firstrole5slot6 becomes2'],prediction={'slot':6,'new_role':2},limits='Conditionalinnerrepair;notafullnaturalremovalfixture.'),
      dict(id='height-role-switch',inputs={'first_available_forward_slot':10,'played_role':9,'heights':[71,72]},steps=['BEC7choosesfirstavailable9..11','71<72 ->13','72>=72 ->12','returnwithoutotherconversions'],prediction={'new_roles':[13,12]},limits='Representableconditionalheightvalues;noaverageaerial/goalbenefitestablished.'),
    ]
    return make_ledger('T103c',Path(__file__).resolve(),['When the computer changes tactics','Repeated draws, latches and resets','Emergency role repair','Worked checks and remaining limits'],rows,examples,calc,['discipline','rare','postmatch'],addresses=['0791:A3DE','0791:65FE','0791:230C','1771:377E','1771:2FAD','1771:3216'])


if __name__=='__main__':run('T103c',build)
