#!/usr/bin/env python3
"""Source-pinned live record layouts, aliases and state-family ledger."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha,write_new


def f(offset,width,name,meaning):return dict(offset=offset,width=width,name=name,meaning=meaning)


def build():
    prefix=[f(0,1,'x','Signed lateral coordinate; contributes to screen row in drawing.'),f(1,1,'y','Signed longitudinal coordinate; contributes to screen column.'),
            f(2,2,'old_position','Previous packed coordinate used to restore the old occupancy cell.'),f(4,2,'glyph','Character/attribute word drawn into the pitch occupancy picture.')]
    pitch=prefix+[f(6,1,'pitch_slot','Pitch identity 1..22, not the played-position code. Below12 selects engine side1.'),
      f(7,2,'destination','Packed target x/y bytes; used by target tests and movement.'),f(9,2,'post','Packed home/post x/y from played role.'),
      f(11,1,'x_offset','Signed lateral target offset.'),f(12,1,'depth_offset','Signed longitudinal depth/target offset.'),
      f(13,2,'player_index','Persistent player-record index, re-bound from the squad slot.'),f(15,1,'run_direction','Direction/state-of-motion byte; activity accounting tests unsigned <5.'),
      f(16,1,'state_timer','State-dependent countdown (including chase/walk-off routes); not a global game minute.'),
      f(17,1,'manager_extra','A260 stores manager_bonus(player.country)+32; assigned to all bound players, later gated by skill/event.'),
      f(18,1,'state','Action-handler dispatch code, distinct from player status flags.'),f(19,1,'placement_flag','Cached 3179 result; 278A halves derived skill when nonzero.'),
      f(20,2,'activity','Update counter; 8AE9 can spend energy after >180 while live play is enabled; reset separately from energy.')]
    ball=prefix+[f(6,2,'velocity_x','Signed word used by travel computation; step code reads its low byte.'),f(8,2,'velocity_y','Signed word used by travel computation; step code reads its low byte.'),f(10,2,'timer','Remaining ball-step timer.')]
    sprite=prefix+[f(6,1,'target_x','Referee target lateral/screen-row coordinate.'),f(7,1,'target_y','Referee target longitudinal/screen-column coordinate.')]
    records={n:{'size':size,'fields':fields} for n,size,fields in [('pitch',22,pitch),('ball',12,ball),('sprite',8,sprite),('marker-prefix',6,prefix)]}
    for name,r in records.items():assert sorted(k for a in r['fields'] for k in range(a['offset'],a['offset']+a['width']))==list(range(r['size'])),name
    groups={
      'clock':{'DS:8319':'byte half-length threshold; adjacent831A is kickoff side, not its high byte','DS:831B':'word regular remaining count','DS:831D':'word subtick countdown, reload36','DS:831F':'word displayed/elapsed count','DS:8321':'word accumulated added time','DS:8325':'byte live-clock/activity gate','DS:8326':'byte end-time flag'},
      'score-statistics':{'DS:9B3C':'two committed score bytes, also scratch during quick trials; write-site semantics matter','DS:7B7E':'20 statistic bytes, ten per side, including injuries not one of the nine displayed rows','DS:80F2,80F6':'two pairs of raw bar counters; legacy variable names do not establish caption/meaning','DS:7C3A':'man-of-the-match player word'},
      'rng':{'DS:A978':'far pointer to main RNG word, normally7B62','DS:7B62':'main16-bit LCG state','DS:8337+k, k=1..255':'precomputed foul draw bytes; entry zero at 8337 is unused by the foul reader','DS:8437':'foul-table index, wraps255to1','DS:8336..8337':'separate sound-seed word; high byte aliases unused foul-table entry zero','DS:9974':'original replay snapshot of main RNG word'},
      'marking':{'DS:9A3E':'quick flag byte; overlaps dummy marking row0, not an active marking word','DS:9A3E+40*t+2*s':'marking words for active squad slots; index/lifetime must be read in context','DS:9976':'fixture-group byte copied from pre-play fixture +1 by A3DE and read by E929 for the group table','DS:9976+10*side+2*role, role=1..5':'captain/set-piece taker slot words; base offset zero is not a taker entry'},
      'restart':{'DS:8302':'ball/play gate; nominal ball+0C','DS:8303':'in-flight/ball-phase flag; nominal ball+0D','DS:830B,830C,830D':'holder/challenger/nearest pitch-slot selectors','DS:8324':'shootout-specific control flag','DS:8327':'ball-event/action code','DS:7C2A':'live current-fixture far pointer; A3DE writes it at A437/A43A','DS:9B34':'two current country words','DS:9B3A':'two substitution-budget bytes'},
      'occupancy':{'DS:7C16':'far pointer to live pitch picture read by move tests','DS:7C1E':'background-picture pointer used for restoration','DS:82E2,82E8':'two six-byte offside-marker prefixes','DS:82EE':'eight-byte referee sprite','DS:82F6':'ball core plus adjacent flags','DS:80FC':'second-team-is-host byte inside nominal pitch row0'},
      'save-decisions':{'DS:9B30..9B33':'replay snapshot of country words 9B34..9B37; 15B9 writes at 17DE/17E1; 0C65 restores at 0CDE/0CE1 and 11BD/11C0','DS:9B38..9B39':'replay snapshot of substitution-budget bytes 9B3A..9B3B; 15B9 writes at 17E8','DS:9B07':'per-side/squad saved form snapshot; not the live player form byte','DS:9B55,7C37':'original snapshot/replay request flags','Match.st':'host-side phase/decision/event bookkeeping, separate from original DS','Match.save/load':'adapter save/replay reconstruction of live port frames; distinct from original action replay'}}
    addresses=['0791:A260','0791:A2E6','0791:A375','0791:8537','0791:86D0','0791:8E24','0791:8F10','0791:9119','0791:83A2','0791:835F','0791:8AE9','0791:278A','0791:2974','0791:2BB1','0791:970C','0791:97D0','0791:2648','0791:261A','0791:15B9','0791:0C65','0791:94C9','0791:9372']
    return pin({'task':'T97b','sections':['Live records and coordinate conventions','State families and lifetimes','Aliases and cached values','Occupancy, randomness and continuation boundaries'],
                'records':records,'state_groups':groups,'ball_logical_extent':14,
                'screen_cell':'buffer + 0x90E + s8(x)*160 + s8(y)*2',
                'pitch_slot_map':{'side0':'12..22','side1':'1..11','keepers':[1,12]},
                'analysis_sha256':sha(Path(__file__).read_bytes())},addresses+['0791:A3DE','0791:E929','0791:1FDD','0791:F3F2','214B:0688'],
               ['runtime/original_match/port/motion.py','runtime/original_match/port/geometry.py','runtime/original_match/port/discipline.py','runtime/original_match/port/frame.py','runtime/original_match/port/setup.py','runtime/original_match/match.py','runtime/original_match/README.md','static/goal-exe/annotations/fields.tsv','static/goal-exe/annotations/globals.tsv','static/goal-exe/code/seg_0791_02.asm','static/goal-exe/code/seg_0791_03.asm','static/goal-exe/code/seg_0791_15.asm','static/goal-exe/code/seg_0791_17.asm','static/goal-exe/code/seg_0791_23.asm','static/goal-exe/code/seg_0791_24.asm'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args();path=ROOT/'notes/engine-study/T97/transient-v2.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data,'transient ledger/source differs';print('PASS: pitch22, ball12, sprite8 and marker6 byte covers; seven state families; source pins/aliases')
    else:write_new(path,data);print('wrote live layouts, seven state groups and explicit aliases')


if __name__=='__main__':main()
