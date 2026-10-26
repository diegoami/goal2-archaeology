#!/usr/bin/env python3
"""Recount retained original foot probes and pin the derived-trait source ledger."""
import argparse
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha,write_new

LABELS=['keeping','kicking','tackling','heading','marking','passing','crossing','feinting','control','dribbling','shooting','penalties']
TRUTH='experiments/E028-formations-positions/out/foot-truth-20261013T142802Z.tsv'


def build():
    rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader((s for s in (ROOT/TRUTH).read_text().splitlines() if not s.startswith('#')),delimiter='\t')]
    def rule(r,swapped=False):
        p,c,f,t=r['played_pos'],r['club_pos'],r['foot_index'],r['is_two_footed']
        left,right=({4,8,11},{3,7,10}) if swapped else ({3,7,10},{4,8,11})
        return int((not t and f!=0 and p in left) or (f==0 and p in right) or ((p==0)!=(c==0)))
    counts={'cases':len(rows),'rule_mismatches':sum(rule(r)!=r['3179_original'] for r in rows),
            'swapped_sets_mismatches':sum(rule(r,True)!=r['3179_original'] for r in rows),
            'two_left_on_right_flank':sum(r['is_two_footed']==1 and r['foot_index']==0 and r['played_pos'] in {4,8,11} for r in rows),
            'two_left_on_right_flank_without_gk_mismatch':sum(r['is_two_footed']==1 and r['foot_index']==0 and r['played_pos'] in {4,8,11} and r['club_pos']!=0 for r in rows),
            'gk_mismatch':sum((r['played_pos']==0)!=(r['club_pos']==0) for r in rows),
            'same_position':sum(r['played_pos']==r['club_pos'] for r in rows)}
    assert counts=={'cases':2352,'rule_mismatches':0,'swapped_sets_mismatches':660,'two_left_on_right_flank':102,'two_left_on_right_flank_without_gk_mismatch':96,'gk_mismatch':312,'same_position':168},counts
    stored=json.loads((ROOT/'notes/engine-study/T96/fields.json').read_text())
    roles={f['name']:f['effect_and_lifetime'] for f in stored['records']['player']['fields']}
    traits={
      'height':{'inputs':[7,'player index mod 12'],'reader':'1771:2FAD','use':'Card and computer tactical/role adjustment via 0791:BEC7; no direct aerial-contest read is established by this call census.'},
      'foot_index':{'inputs':[7,'player index mod 3'],'reader':'1771:3088','use':'Placement and substitution-role checks; displayed two-footedness is a separate predicate.'},
      'two_footed':{'inputs':[2,5],'reader':'1771:3041','use':'Sum equals 30; the wrong-foot exemption is asymmetric.'},
      'hardness':{'inputs':[3,5],'reader':'1771:2FFB','use':'Profile minus ceiling low bit; foul and injury decisions and initial tactic choices.'},
      'leadership':{'inputs':[1,3,5],'reader':'1771:30D9','use':'Signed division remainder, then age gate; captain/leader selection, with first-in-scan ties.'},
      'availability':{'inputs':[14,16],'reader':'1771:3216','use':'Signed energy below 1 or status element 8/6/3; not identical to the screen injury predicate.'},
      'performance_display':{'inputs':[18,19],'reader':'1771:3827','use':'Blank/encoded rating word mapped to text buckets; distinct from skills.'}}
    addresses=['1771:3947','1771:3A06','0791:278A','1771:2FAD','1771:3088','1771:3041','1771:3179','1771:2FFB','1771:30D9','1771:3216','1771:3827','0791:1F3C','0791:20E3','0791:8062','1771:3EF8','0791:BEC7','0791:A9B8','0791:AAE8']
    return pin({'task':'T96b','sections':['Derived skills','Characteristics and context','Flags, performance and availability','Field roles and access boundaries','Known asymmetry and evidence limits'],
                'skills':[{'element':i,'label':label,'stored_inputs':[4,5,7]} for i,label in enumerate(LABELS,1)],
                'traits':traits,'field_roles':roles,'field_ledger_sha256':sha((ROOT/'notes/engine-study/T96/fields.json').read_bytes()),
                'access_boundaries':['Primary named readers versus transitive callers','Computed field selectors and raw memory helpers','Whole-record swaps/copies and replay snapshots','Player index, current pitch and country/fixture context outside the record'],
                'retained_original_foot_probe':{'counts':counts,'two_true_fixture':{'peak_age':15,'skill_profile':15},'two_false_fixture':{'peak_age':0,'skill_profile':0},'scope':'Synthetic routine calls; no new original execution or natural-play frequency'},
                'range_valid_static_example':{'player_index':1,'club_position':2,'played_position':4,'peak_age':25,'skill_profile':5,'foot_index':0,'two_footed':True,'out_of_place':1,'scope':'Static range-valid tuple; not newly executed or observed in play'},
                'analysis_sha256':sha(Path(__file__).read_bytes())},addresses,
               [TRUTH,'experiments/E028-formations-positions/foot_truth.py','static/goal-exe/calls.tsv','runtime/original_match/port/attributes.py','static/goal-exe/code/seg_1771_05.asm',
                'findings/F008-the-player-screen-draws-12-skills-as-bars-derived-from-three-record-bytes.md','findings/F028-formations-are-posts-by-position-code-and-out-of-position-costs-one-halving-flag.md'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args()
    path=ROOT/'notes/engine-study/T96/derived.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data,'derived ledger/source or retained counts differ'
        print('PASS: 12 skill elements, 17 stored-field dispositions, 2352 retained foot calls / zero rule mismatches')
    else:
        write_new(path,data);print('wrote derived-trait ledger; retained original foot data recounted')


if __name__=='__main__':main()
