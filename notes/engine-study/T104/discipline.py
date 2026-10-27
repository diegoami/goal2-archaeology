#!/usr/bin/env python3
"""Source-derived foul/status/form projections; no original/port engine execution."""
from pathlib import Path
import sys
from common import ROOT,make_ledger,run

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import s8,s16


def may_lose(managed,reds,injuries,available_squad):
    return reds+injuries<3 and (managed or available_squad>11)


def form(live,delta,persist,saved):
    new=min(255,max(1,s16((s8(live)+delta)&65535)))
    return new,(min(32,s8(new))&255) if persist else saved


def card_attempt(table_byte,booked,rare_draw_is_one=False):
    if table_byte<4:return 'red-attempt' if booked else 'yellow'
    return 'red-attempt' if rare_draw_is_one else 'none'


def injury_target(offender_hardness,victim_hardness):
    return 'offender' if offender_hardness<victim_hardness else 'victim'


def calculations():
    cap=[may_lose(True,1,1,11),may_lose(False,1,1,11),may_lose(False,1,1,12),may_lose(True,0,3,20)]
    assert cap==[True,False,True,False]
    assert (0<3)!=may_lose(True,0,3,20)  # ignoring injury counter breaks shared cap
    yellow=0x40|(1<<4);red=(yellow|(1<<5))&~(1<<4)
    assert [yellow,red]==[0x50,0x60]
    ai_tactics=(0x08|0x80)&~0x08
    assert ai_tactics==0x80 and ai_tactics&0x80 and not ai_tactics&0x08
    assert card_attempt(2,False)=='yellow' and card_attempt(2,True)=='red-attempt'
    assert card_attempt(4,False,False)=='none' and card_attempt(4,False,True)=='red-attempt'
    assert injury_target(3,6)=='offender' and injury_target(6,6)=='victim'
    changes=[form(16,-2,True,16),form(16,2,False,16),form(31,2,True,31),form(1,-2,True,1),form(127,1,True,31)]
    assert changes==[(14,14),(18,16),(33,32),(1,1),(128,128)]
    assert min(32,128)!=changes[-1][1]
    assert form(16,2,True,16)!=(18,16)
    added=lambda value:value+1 if value<5 else value
    assert [added(v) for v in [4,5,6]]==[5,5,6]
    opposite=lambda slot:slot+11 if slot<12 else slot-11
    assert [opposite(s) for s in [1,5,11,12,16,22]]==[12,16,22,1,5,11]
    assert 16+11!=opposite(16)
    referee_component={str(flag):(10 if flag==0 else 0) for flag in [0,1]}
    assert referee_component=={'0':10,'1':0}
    return dict(loss_cap_examples=cap,yellow_red_status_from_protect_zone=[yellow,red],ai_booking_own_tactics=ai_tactics,
                card_value_classes={'0..3':['yellow','red-attempt-if-already-booked'],'4..15':'one-in32 main attempt'},
                injury_tie_target='victim',live_saved_form_cases=[list(v) for v in changes],
                added_time_edges=[5,5,6],offside_opposite_slots=[12,16,22,1,5,11],referee_main_draw_component=referee_component,
                controls={'ignore-injury-count':'rejected:shared cap already3','omit-ai-depth-guard':'rejected:11 available does not pass unmanaged guard',
                          'persist-team-swing':'rejected:saved16 must stay16','unsigned-saved-form-cap':'rejected:128 differs from32 on edited signed edge',
                          'always-add11-opponent-slot':'rejected:16 maps5,not27'})


def build():
    calc=calculations()
    rows=[
        ('7881','Save/clear activity and interaction flags,state12,targetexit;direct update/draw loop,then offpitch sentinel andstate0,restore flags.', ['8325/9B41/8302','0640/0642','pitch+12','8AE9/8537'],'Unavailable player can still be animated off;no970C inside wrapper.'),
        ('798D','Set status element5,booking stat+7,added-time increment below5;unmanaged personal override forces e4 off.', ['player+10/+F','7B85','8321','33CD'],'Yellow has no direct form write;future risk/control changes separately.'),
        ('7A43','Require reds+injuries<3;unmanaged side additionally needs>11 available among20 squad words.', ['7B86/7B87','country.squad','3216','0B77'],'Both card and injury attempts can be suppressed by context.'),
        ('7B24','Set sent-off element6,clear booked element5,increment reds stat+8.', ['player+10','7B86'],'Other status bits remain;red is distinct from a live pitch state.'),
        ('7B77','After cap allow:line/marker,red status,walkoff,time increment,own form-2 saved,opposite availableXI live+2,management/removal follow-up.', ['7A43','7CC5','9B07','2974','C48D/9B40'],'Opponent selection uses opposite pitch side2974,not a possession-side boolean.'),
        ('7CC5','Signed live form plusword delta clamped1..255;persist flag writes min32 of signed newbyte to9B07.', ['player+C','9B07','2BB1/2974'],'Live and saved form differ;byte signedness matters outside normal range.'),
        ('7D56','If available/cap allow:line,energy0,walkoff,form-2 saved,time/stat;AI replacement or managed injury notice when allowed.', ['player+E/+C','7B87','9B3A/9B40','C88D'],'Immediate injury uses energy0;duration/recovery belongs to later processing.'),
        ('7E60','Stop activity,whistle,ten holder/challenger sprite/referee passes,then marker handling and830Aclear.', ['8325','830B/C','9119(mode)','830A'],'Mode0 referee component consumes10 main draws;mode1 component does not.'),
        ('7EEF','First table byte:yellow/second-yellow red orconditional1in32 red attempt;second table byte1:injure lower hardness,tie victim.', ['261A','8437','player+10','2FFB','830B/C'],'Cards and injuries can both be attempted;guards/callee effects determine completion.'),
        ('8206','Install offender selectors,own-strip/coin bail;else lines,whistle1,foul counter,cache penalty geometry,dispatch card/injury,then penalty/free kick.', ['830C/D','7B84','7EEF','2EB8','6ECF/6FB6'],'A foul predicate alone does not guarantee a recorded foul or penalty.'),
        ('82EB','Pending offside ->offender selector,whistle0,saved ball point,opposite same-relative holder,recompute nearest and free-kick route.', ['830E/C/D/B','8317','7920','2FB1/6FB6'],'Offside restarts do not call the card/injury dispatch on this path.'),
    ]
    rows=[('0791:'+a,m,f,e) for a,m,f,e in rows]
    examples=[
        dict(id='booked-foul-and-injury',inputs={'first_table_byte':2,'already_booked':True,'second_table_byte':1,'offender_hardness':6,'victim_hardness':6},
             steps=['red attempt under7A43','second explicit table read still controls injury attempt','equal hardness choosesvictim;injure again checks availability/loss cap'],
             prediction={'card_attempt':'red','injury_target':'victim'},limits='Supplied table/identity context,not a complete foul run. Re-sorting/substitution and guard changes can suppress later effects.'),
        dict(id='red-form-lifetimes',inputs={'sent_off_form':16,'opponent_form':16,'saved_form':16,'loss_cap_passes':True},
             steps=['sentoff status6 clearsbook5 andwalksoff','own liveform14,saved14','each available opposite-side liveform18,saved16'],
             prediction={'sent_off':[14,14],'opponent':[18,16]},limits='Only7CC5 projections;full walkoff/referee/substitution RNG not counted. Numeric form increases are not uniformly beneficial at32.'),
        dict(id='unmanaged-loss-guard',inputs={'reds':1,'injuries':1,'available_squad':[11,12]},steps=['sharedloss2<3','unmanagedrequiresavailable>11'],
             prediction=[False,True],limits='20-player availability count,not only on-pitch player count;initial valid-team/lifecycle invariants not proved here.'),
        dict(id='offside-whistle-and-index',inputs={'offside_slot':16,'saved_ball_point':'8317','whistle_mode':0},
             steps=['offender16,nearest0','ten mode0 referee updates','restore8317;opposite relative slot5;nearest recompute andFK'],
             prediction={'initial_awarded_holder':5,'referee_component_main_draws':10},limits='Component count only,not total82EB draw count. Later restart can repick taker;no original-key evidence added.'),
    ]
    return make_ledger('T104b',Path(__file__).resolve(),['Foul admission, consequences and guards','Status, form and injury lifetimes','Animation, offside and random sources','Worked paths and limits'],
                       rows,examples,calc,['restarts','discipline','rare','attributes','motion','geometry'],
                       addresses=['1771:33CD','1771:3216','0791:261A','0791:9119','0791:2974'],
                       sources=['findings/F002-static-inventory.md'])


if __name__=='__main__':run('T104b',build)
