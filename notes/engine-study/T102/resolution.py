#!/usr/bin/env python3
"""Source-derived contest/goal bookkeeping; no original/port engine or match execution."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT,BASE,ROUTINES,pin,sha,write_new,frontier
from flight import draw

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds


def pair(seed,holder,challenger,multiplier=1,*,inclusive=False):
    seed,h=draw(seed,holder&65535)
    seed,c=draw(seed,(challenger*multiplier)&65535)
    return dict(holder=h,challenger=c,won=c>=h if inclusive else c>h,seed=seed)


def finish(seed,event,value,*,quality=False,own_goal=False,reverse=False):
    if event>4:return dict(route='6755',draws=0,seed=seed)
    if quality or own_goal:return dict(route='67B6',draws=0,seed=seed)
    if event not in [3,4]:return dict(route='6755',draws=0,seed=seed)
    if reverse:
        seed,holder=draw(seed,value);seed,opponent=draw(seed,32)
    else:
        seed,opponent=draw(seed,32);seed,holder=draw(seed,value)
    return dict(route='67B6' if holder>opponent else '6755',draws=2,seed=seed,
                holder=holder,opponent=opponent)


def goal(scores,holder_side,*,own_goal=False,offside=False,record_early=False):
    """Normal8326-clear branch, initial replay request clear, not replaying."""
    values=list(scores);side=holder_side^int(own_goal)
    values[side]=(values[side]+1)&255
    provisional=list(values)
    recorded=bool(record_early)
    if offside:
        values[side]=(values[side]-1)&255
        return dict(provisional=provisional,final=values,credited_side=side,recorded=recorded,
                    player_goal_delta=0,after_goal=False,replay_request=False)
    return dict(provisional=provisional,final=values,credited_side=side,recorded=True,
                player_goal_delta=0 if own_goal else 1,after_goal=True,replay_request=True)


def receipt(slot,old_holder,old_air):
    return dict(holder=slot,receiver=0,nearest=0,moving=0,event=0,timer=0,air=old_air,
                commentary19=old_holder!=slot and not old_air)


def log_row(count,*,unlimited=False):
    return count+1 if unlimited else min(11,count+1)


def calculations():
    read,_,sources=load_ds()
    table=[read(0x7f4+i) for i in range(6)]
    assert table==[3,4,10,4,4,1]
    assert [read(0x804+i) for i in range(2)]==[3,9]
    assert [read(0x80c+i) for i in range(5)]==[10,11,4,12,12]
    weak=pair(0,80,30);strong=pair(0,80,30,4)
    assert [weak['holder'],weak['challenger'],weak['won']]==[9,7,False]
    assert [strong['holder'],strong['challenger'],strong['won']]==[9,28,True]
    assert not pair(0,1,1)['won'] and pair(0,1,1,inclusive=True)['won']
    direct=finish(0,3,32);reversed_order=finish(0,3,32,reverse=True)
    assert [direct['opponent'],direct['holder'],direct['route']]==[4,8,'67B6']
    assert reversed_order['route']=='6755'
    assert finish(0,6,100,quality=True)['route']=='6755'
    assert finish(0,0,0,own_goal=True)['route']=='67B6'
    assert finish(0,1,100)['route']=='6755' and finish(0,1,100,quality=True)['route']=='67B6'
    allowed=goal([1,0],0);disallowed=goal([1,0],0,offside=True);own=goal([1,0],0,own_goal=True)
    assert allowed['final']==[2,0] and allowed['recorded'] and allowed['replay_request']
    assert disallowed['provisional']==[2,0] and disallowed['final']==[1,0]
    assert not disallowed['recorded'] and not disallowed['after_goal'] and not disallowed['replay_request']
    assert goal([1,0],0,offside=True,record_early=True)['recorded']
    assert own['final']==[1,1] and own['credited_side']==1 and own['player_goal_delta']==0
    assert log_row(11)==11 and log_row(11,unlimited=True)==12
    assert (90+128)&255==218 and (130+128)&255==2  # byte addition, not generic OR
    explicit_calls={f'watched{w}_keeper{k}':(3 if w else 0)+(1 if k else 0) for w in [False,True] for k in [False,True]}
    assert list(explicit_calls.values())==[0,1,3,4]
    # Flight keeper threshold: difficulty draw occurs before keeping draw.
    seed,difficulty=draw(0,4*20);seed,keeping=draw(seed,30)
    assert [difficulty,keeping]==[9,7]
    seed,near_difficulty=draw(0,4);seed,near_keeping=draw(seed,30)
    assert [near_difficulty,near_keeping]==[1,7]
    selected_receipts=[receipt(9,6,a) for a in [0,1]]
    assert selected_receipts[0]['commentary19'] and not selected_receipts[1]['commentary19']
    assert selected_receipts[1]['air']==1
    return dict(tackle_tables=table,reaction_elements_defending_holding=[3,9],finish_elements=[10,11,4,12,12],
                tackle_without_multiplier=weak,tackle_with_multiplier4=strong,
                conditional_finish=direct,reversed_finish_control=reversed_order,
                goal_allowed=allowed,goal_disallowed=disallowed,own_goal=own,
                selected_receipts_ground_air=selected_receipts,
                celebration_explicit_main_calls=explicit_calls,
                flight_keeper_examples={'travel20':[difficulty,keeping,False],'travel1':[near_difficulty,near_keeping,True]},
                controls={'inclusive-tackle':'rejected:tie must not win','reverse-finish-draws':'rejected:goal route changes',
                          'record-before-offside':'rejected:disallowed goal must not enter scorer record',
                          'unlimited-scorer-log':'rejected:row11 remains final row',
                          'remove-celebration-draws':'rejected:watched nonkeeper has3 body draws, not0',
                          'clear-air-after-selected-receipt':'rejected:8AE9 restores old air1'},
                ds_sources=sources)


def build():
    calc=calculations()
    rows=[
        ('4DA9','Initial random-is-one(18-hardness) or e4 admission, then holder/challenger hardness rolls; challenger strictly larger means foul gate.',
         ['1771:2FFB','26D7(4)','DS:830B'],'Hardness/tactic access is separate from tackling skill; initial draw still occurs with e4 on.'),
        ('539F','Won-ball resolution despite legacy foul name: keeper-holder exemption,old holder delay,possession/deflection/clearance and commentary.',
         ['DS:830B/8303','287C(3)','869F','5E41/408E'],'Winning tackle is not always clean possession.'),
        ('5474','Holder roll first:dribbling10 ground/heading4 air; challenger tackling3/heading4,ground own-half multiplier4 else1; strict larger wins.',
         ['DS:07F4/07F6/07F8','2C54','278A'],'Geometry changes challenger bound; ties do not win.'),
        ('5513','Foul gate then coin between watched foul sequence and won-ball resolution.',
         ['4DA9','8206','539F'],'Foul-predicate success does not alone identify the final card/whistle/possession event.'),
        ('5565','Eligible opposing contact challenge: keeper/outfield duel,foul/clearance branches and possible quiet player-performance+10.',
         ['pitch point','DS:830B/8302/8303/830E','player+12'],'Position/phase gates and a silent performance write affect full outcome.'),
        ('56D9','Pending-offside marker/message request and once-only template66; low-byte return always0.',
         ['DS:830E/8329','26A0','2B0F'],'Notification does not itself stop57AC or award the restart.'),
        ('5729','Nonkeeper off-holding-side go-to-ball gate from own/opposing strip predicates and e6.',
         ['2EB8','2EF0','26D7(6)'],'Stand-ground/sag-back changes whether a record targets the ball.'),
        ('5A33','Install record holder and save/parry commentary; increment stat+5 and clear event only outside8326; clear8324.',
         ['DS:830B/8324/8327','DS:7B7E+10*side+5'],'Save-looking line and committed possession are distinct wrappers.'),
        ('5A8E','Normal take-possession or mode-specific timer clear,template29 through5A33,then own-strip delay or clearance.',
         ['DS:8326','869F','5A33','2EB8'],'Keeper resolution can still start a new launch.'),
        ('5B36','Own-side possession shortcut; ground/air opposing duels; moving-ball threshold uses difficulty before keeper roll,then parry/wide/catch outcomes.',
         ['DS:8302/8303/8324','278A(1/4/10)','835F','DS:07FE/0800'],'Keeping has several contexts; winning a flight threshold is not guaranteed clean catch.'),
        ('5E41','Two axis draw/coin offsets around a record point,then take possession and event6 relaunch.',
         ['DS:0802','869F','34C1'],'Deflection changes holder/launch state, not only ball velocity.'),
        ('5EAB','Take possession,submit32,recompute nearest list,temporarily set80FA to pass toward nearest with384C.',
         ['DS:8311/80FA','2FB1','384C'],'Loose-ball route can become a heading-event launch via80FA.'),
        ('5F06','Cache air8303 and side; air/event-set branch chooses5EAB or deflection route; restore/set final air from a coin.',
         ['DS:8303/8327','CS:5EE6','DS:080A'],'The local named moving is air flag8303, not play flag8302.'),
        ('5F8A','At-ball nonholder reactions use remaining travel,air,geometry and gates for control9/tackling3/heading4 or side table3/9.',
         ['DS:8325/8324','835F','DS:0804/0806/0808','287C'],'Interception/reaction outcome depends on context beyond being on the ball cell.'),
        ('6188','Watched,state-not13,at-ball dispatch: keeper duel or unselected nonholder reaction under additional phase gates.',
         ['DS:9A3E/830C/8326','pitch+12','2CEC'],'Distinct from8AE9 selected-target acquisition.'),
        ('61EC','Stop activity,check substitutions,pick conceding side relative slot10 (own-goal reversal),advance unavailable slot,fill state1.',
         ['DS:8325/830B/7C39','DS:0668','8062','2929'],'Goal restart and substitution management meet at this boundary.'),
        ('6240','State6 celebration/restart movement depends on holder,target,score comparison and own-goal flag; eventually61EC.',
         ['DS:830B/7C39/9B3C','pitch+7/+8','rand16'],'Score affects player targets before the kickoff transition.'),
        ('6337','Keeper holder can transfer to a random available outfielder; watched branch gives holder a random celebration target,quick branch copies point.',
         ['DS:830B/0668/9A3E','rand10/coin/rand5-or25/coin'],'Watched body consumes3 additional main draws even when holder is not a keeper.'),
        ('6443','Normal scorer goals/form and optional top-scorer update;own-goal branch reverses credited log side;11-row saturating goal list and byte-tagged minute.',
         ['player+A/+C','DS:80F0/7BD1','DS:8324/7C39','7CC5'],'Persistent scorer data differs from temporary scoreboard increment.'),
        ('65A4','Holding-side nonkeepers get state6,others0,then6337.',
         ['pitch+12','2B51','045D'],'After-goal formation/celebration state is explicitly rebuilt.'),
        ('65FE','Activity/whistle/targets,normal phase state+AI updates then live form swing;score/own-flag-indexed sound-envelope word832A and quick snapshot request.',
         ['DS:8325/8326/832A/9A3E/9B55','7CC5','C173'],'Goals feed later attributes; sound counter has identified audio readers, not a proven aggression effect.'),
        ('6755','Miss/goalline route places y at39 with sign,submits40/41,sound word20,then goal-kick/free-kick or pending-offside route.',
         ['DS:830E/832A','6F01','82EB'],'A mouth boundary can lead to a restart instead of a score.'),
        ('67B6','Provisional score increment,normal offside rollback before6443;otherwise after_goal and replay bookkeeping.',
         ['DS:9B3C/830E/8326/7C39/0C20/7C37','6443','65FE'],'Final accepted goal differs from provisional goal/disallowed events.'),
    ]
    examples=[
        {'id':'ground-tackle','inputs':{'stage_seed':0,'holder_dribbling':80,'challenger_tackling':30,'multipliers':[1,4]},
         'steps':['holder draws9 first','challenger draws7 at bound30 or28 at bound120','strict comparison;win enters539F,which still has conditional resolution'],
         'prediction':{'without_multiplier':False,'with_multiplier4':True},
         'limits':'Local source draw pairs; eligibility/fouls/possession resolution and natural encounter frequency not simulated.'},
        {'id':'conditional-finish-to-goal','inputs':{'decision_seed':0,'event':3,'quality_flag':0,'own_goal_flag':0,'effective_penalties':32,'score':[1,0],'holder_side':0},
         'steps':['690C opponentrand32=4 then holderrand32=8 ->67B6','normal goal increments score to2,0','with no offside record scorer and invoke after-goal/replay bookkeeping'],
         'prediction':calc['goal_allowed'],
         'limits':'Two connected source projections;67B6 commentary coin/after-goal RNG not simulated or counted. Supplied effective value,not complete original call frame.'},
        {'id':'offside-rollback','inputs':{'score':[1,0],'holder_side':0,'normal_phase':True,'pending_offside':True},
         'steps':['67B6 provisional score2,0','pending flag subtracts it again','return through82EB before scorer/after-goal/replay request'],
         'prediction':calc['goal_disallowed'],'limits':'Provisional display/event exists;does not prove original input reachability or restart management details.'},
        {'id':'selected-reception','inputs':{'receiver':9,'still_selected_830D':9,'old_holder':6,'at_ball':True,'state':5,'old_air':[0,1]},
         'steps':['8AE9 after step acquires through869F under its selected-record predicate','clear selectors/play/event/timer','restore oldair;ground can submit19,air does not'],
         'prediction':calc['selected_receipts_ground_air'],'limits':'Additional8AE9 conditions assumed;partial globals,not full frame/position/drawing effects. No heading gate on this particular path.'},
    ]
    artifacts=['notes/engine-study/T99/contests-v2.json','notes/engine-study/T102/flight.py']
    sources=['runtime/original_match/port/duels.py','runtime/original_match/port/contests.py','runtime/original_match/port/restarts.py',
             'runtime/original_match/port/motion.py','runtime/original_match/port/frame.py','runtime/original_match/port/display.py',
             'static/goal-exe/code/seg_0791_08.asm','static/goal-exe/code/seg_0791_09.asm','static/goal-exe/code/seg_0791_10.asm',
             'static/goal-exe/code/seg_0791_11.asm','static/goal-exe/code/seg_0791_14.asm','static/goal-exe/code/seg_0791_15.asm',
             'notes/engine-study/T95/census-08beac2e-v1.json',*calc['ds_sources']]
    return pin(dict(task='T102c',status='proposed; source-derived explanation',method=__doc__,
                    sections=['Contact is not one contest','From the goal line to an accepted goal','After-goal feedback and random consumption','Worked paths and rewrite limits'],
                    routines=[dict(address='0791:'+a,mechanism=m,fields=f,visible_effect=e,
                                   limits='Source-conditioned mechanism;no new engine execution or whole-match probability.') for a,m,f,e in rows],
                    examples=examples,calculations=calc,census_dispositions=frontier(),
                    supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in artifacts},
                    analysis_sha256=sha(Path(__file__).read_bytes())),
               ['0791:'+a for a in ROUTINES['T102c']]+['0791:690C','0791:698E','0791:8AE9','0791:94E8','0791:9564','0791:94C9'],sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T102/T102c-v1.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: contest/finish literals,score rollback/own-goal/receipt,scorer cap,celebration draws,55 dispositions,6 controls')
    else:write_new(path,data);print('wrote T102c source-derived ledger;no engine execution')


if __name__=='__main__':main()
