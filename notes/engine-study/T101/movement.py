#!/usr/bin/env python3
"""Source-derived movement/occupancy examples; no original or port routine execution."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT, BASE, ROUTINES, pin, sha, write_new

sys.path.insert(0, str(ROOT / 'notes/engine-study/T98'))
from tables import load_ds, s8


def attempt(old, direction, character, attribute, *, live=True, exempt=False):
    read, _, _ = load_ds()
    point = list(old)
    for code, axis, step in [(1,0,-1),(2,0,1),(3,1,-1),(4,1,1)]:
        if direction == code:
            point[axis] = s8((point[axis]+step)&255)
    if direction == 5:
        accepted = True
    elif abs(point[0])>8 or abs(point[1])>37:
        accepted = False
    else:
        blocked = bool(read(0x648+character//8)&(1<<(character%8)))
        accepted = not live or exempt or attribute == 0x0d or not blocked
    return {'candidate':point,'direction':direction,'accepted':accepted}


def energy(counter, direction, current, live):
    counter = (counter+(direction<5)) & 65535
    if live and counter>180:
        return 0, current-(s8(current)>1)
    return counter,current


def offside_line(ys, direction):
    return min([0]+[y*direction for y in ys])*direction


def referee_target(ball_y, draw):
    assert draw in [1,2]
    y = min(ball_y+1,30+draw) if ball_y>0 else max(ball_y-1,-30-draw)
    x = max(-5,min(5,int(y/4)+1))
    return [x,y]


def calculations():
    read, _, sources = load_ds()
    blockers = [i for i in range(256) if read(0x648+i//8)&(1<<(i%8))]
    assert 1 in blockers and 32 not in blockers
    trace = [attempt([0,0],2,1,7),attempt([0,0],4,32,7)]
    assert trace == [{'candidate':[1,0],'direction':2,'accepted':False},
                     {'candidate':[0,1],'direction':4,'accepted':True}]
    assert attempt([0,0],2,1,13)['accepted']
    assert attempt([0,0],2,1,7,live=False)['accepted']
    assert attempt([0,0],2,1,7,exempt=True)['accepted']
    assert attempt([0,37],2,32,7)['accepted']
    assert not attempt([0,37],4,32,7)['accepted']
    assert attempt([8,37],5,1,7)['accepted']
    assert energy(179,2,10,True) == (180,10)
    assert energy(180,2,10,True) == (0,9)
    assert energy(180,5,10,True) == (180,10)
    assert energy(180,2,1,True) == (0,1)
    assert energy(180,2,10,False) == (181,10)
    timer,state,chase = 4,13,[]
    for _ in range(5):
        if timer:
            timer -= 1
        else:
            state = 5
        chase.append([timer,state])
    assert chase == [[3,13],[2,13],[1,13],[0,13],[0,5]]
    lines = [offside_line([10,20],1),offside_line([-8,-2,10],1),offside_line([8,2,-10],-1)]
    assert lines == [0,-8,8]
    assert referee_target(-1,1) == [1,-2] and referee_target(37,2) == [5,32]
    assert max(-5,min(5,(-2//4)+1)) != referee_target(-1,1)[0]
    assert min([10,20]) != lines[0]
    # A different glyph has overwritten a sprite's old cell: 8E24 must preserve it.
    old_cell, own_glyph, background = 0x0710,0x0701,0x0720
    kept = background if old_cell==own_glyph else old_cell
    assert kept == 0x0710 and kept != background
    assert trace[0]['candidate'] != trace[1]['candidate']
    return dict(blocking_characters=blockers,blocked_step=trace,
                supplied_draws={'initial_axis_coin':1,'failed_step_retry_draw':4,'total_main_draws':2},
                offside_examples=lines,referee_examples=[referee_target(-1,1),referee_target(37,2)],
                chase_countdown_from4=chase,
                energy_edges={'179_running':[180,10],'180_running':[0,9],'180_standing':[180,10],
                              'energy1_floor':[0,1],'clock_off':[181,10]},
                sprite_other_glyph_preserved=kept,
                controls={'ignore-occupancy':'rejected:accepts[1,0], loses retry draw',
                          'omit-zero-offside-initializer':'rejected:10 instead of0',
                          'referee-floor-division':'rejected:target x0 instead of1',
                          'unconditional-sprite-erasure':'rejected:background replaces another glyph'},
                ds_sources=sources)


def frontier():
    path=ROOT/'notes/engine-study/T95/census-08beac2e-v1.json'
    census=json.loads(path.read_text())
    rows=[r for r in census['routines'] if r['module'] in {'positioning','motion','pilot'}]
    routing={'0791:'+a:task for task,addresses in ROUTINES.items() for a in addresses}
    routing.update({'0791:'+a:'T102' for a in ['835F','83A2','869F']})
    assert len(rows)==len(routing)==28
    assert {r['address'] for r in rows}==set(routing)
    return [{'address':r['address'],'module':r['module'],'owner':routing[r['address']]} for r in rows]


def build():
    calc=calculations()
    rows=[
        ('4D3F','Eligible outfield/keeper-in-strip enters state13, target=current point, draw-table countdown+4 and keeper+10.',
         ['pitch+7/+10/+12','261A','2EB8'],'Chase/recovery delay; no guaranteed travel toward the ball.'),
        ('8537','Restore/draw player glyph in live occupancy; move held ball relative to run direction and draw ball.',
         ['DS:7C16/7C1E','pitch+0/+2/+4/+F','DS:82F6'],'Display writes affect later collision tests and held-ball coordinates.'),
        ('8889','Conditional offside target restriction, then target test, axis coin and86D0 retries from old drawn position.',
         ['pitch+7/+8/+F','DS:82E3','CS:8869','DS:0648'],'At most one accepted cardinal move or standstill; retry draws change RNG.'),
        ('8AE9','State handler, run step, activity count, possible possession, drawing and live energy expenditure in that order.',
         ['pitch+12/+14','player+E','DS:8325','DS:8302/8303/830D'],'Target/action updates precede motion; energy can fall after activity>180.'),
        ('8C67','Reset one offside-line sprite to x=8*direction,y=0,old=current.',
         ['DS:82E2+6*side','2BE5'],'Half-start line initialisation.'),
        ('8CCA','Reset both lines, then initialise referee point/old/target to(1,0).',
         ['DS:82EE..82F5'],'Referee/line continuation starts from defined coordinates.'),
        ('8CF5','Minimum of zero and all ten outfield directed y values, mirror back, draw line; optional marker.',
         ['DS:82E2','DS:8328','DS:8304/8308','DS:82F7'],'Line geometry and subsequent target restriction/marker feedback.'),
        ('8E24','Restore old cell only if its full glyph still belongs to sprite; store old=current and draw new glyph.',
         ['DS:7C16/7C1E','sprite+0/+2/+4'],'Avoid erasing another glyph; modifies live occupancy.'),
        ('90C5','Write marker glyph and x, offset y by direction table indexed by glyph; draw unless quick flag.',
         ['DS:8304','DS:9A3E','DS:7920'],'Message/offside marker placement is a state write, not pure output.'),
        ('9119','Ordinary referee target uses one rand2, signed division/clamp, guarded axis steps and background blocker rollback.',
         ['referee+0/+2/+6','DS:82F7','DS:7C1E','DS:0648'],'Referee changes occupancy and consumes RNG even if no movement follows.'),
    ]
    examples=[
        {'id':'blocked-step','inputs':{'old':[0,0],'destination':[1,0],'initial_coin':1,'first_cell':[1,7],'retry_draw5':4,'retry_cell':[32,7]},
         'steps':calc['blocked_step'],'prediction':{'final':[0,1],'direction':4,'main_draws':2},
         'limits':'Supplied draw values and ordinary live outfielder, not holder/challenger/keeper; no complete seeded fixture execution.'},
        {'id':'energy-edge','inputs':{'activity':180,'direction':2,'energy':10,'live':True},
         'steps':['increment to181','strict>180 passes','energy10>1 ->9; activity reset0'],
         'prediction':[0,9],'limits':'Only8AE9 expenditure tail; other energy writers and opportunity frequency remain separate.'},
        {'id':'offside-zero','inputs':{'outfield_directed_y':[10,20],'direction':1},
         'steps':['initial minimum0','neither positive value replaces0'],
         'prediction':0,'limits':'Other eight values also nonnegative; no automatic interpretation as modern second-last-defender law.'},
    ]
    sources=['runtime/original_match/port/motion.py','runtime/original_match/port/pilot.py',
             'runtime/original_match/port/positioning.py','runtime/original_match/port/frame.py',
             'notes/engine-study/T95/census-08beac2e-v1.json',
             'static/goal-exe/code/seg_0791_05.asm','static/goal-exe/code/seg_0791_08.asm',
             'static/goal-exe/code/seg_0791_14.asm','static/goal-exe/code/seg_0791_15.asm',*calc['ds_sources']]
    return pin({'task':'T101c','status':'proposed; source-derived explanation','method':__doc__,
                'sections':['Targets become steps','The picture is occupancy','Offside, referee and worked boundaries'],
                'routines':[dict(address='0791:'+a,mechanism=m,fields=f,visible_effect=e,
                                 limits='Local source rule; no new engine execution or whole-match effect estimate.') for a,m,f,e in rows],
                'examples':examples,'calculations':calc,'census_dispositions':frontier(),
                'analysis_sha256':sha(Path(__file__).read_bytes())},
               ['0791:'+a for a in ROUTINES['T101c']]+['0791:86D0','0791:2DCA','0791:58E1','0791:57AC'],
               sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T101/T101c-v1.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: blocked-step/attribute/exemption/boundary cases, energy/offside/referee edges, 28 census dispositions, 4 controls')
    else:
        write_new(path,data);print('wrote T101c source-derived ledger; no engine execution')


if __name__=='__main__':
    main()
