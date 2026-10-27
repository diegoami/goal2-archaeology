#!/usr/bin/env python3
"""Record/index audit with legacy analytical-helper checks; no guest/port engine execution."""
import argparse
import json
from pathlib import Path
import sys
from check import ROOT,BASE,pin,sha,write_new

sys.path.insert(0,str(ROOT/'runtime'))
from model.keeping import skill_value
sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds


def site(part,pc):
    path=f'static/goal-exe/code/seg_0791_{part}.asm'
    hits=[(n,line) for n,line in enumerate((ROOT/path).read_text().splitlines(),1) if line.startswith(pc+' ')]
    assert len(hits)==1,(path,pc)
    n,line=hits[0]
    return dict(file=path,line=n,instruction=line)


def calculations():
    source='experiments/E020-q018-condition-performance/records/contest-001.json'
    old=json.loads((ROOT/source).read_text())
    ct=bytes.fromhex(old['class_table_DS_6D25']);pt=bytes.fromhex(old['profile_table_DS_6DCD'])
    read,ds,ds_sources=load_ds();windows=[]
    for profile,club,element,wanted in [(8,13,12,107),(16,2,3,135)]:
        try:skill_value(180,profile,club,element,ct,pt)
        except IndexError:error='IndexError'
        else:raise AssertionError('legacy short-window defect did not reproduce')
        ci=12*club+element;klass=read(0x6d25+ci);pi=12*profile+klass
        extended=skill_value(180,profile,club,element,ds[0x6d25:0x6d25+169],ds[0x6dcd:0x6dcd+205])
        assert extended==wanted
        windows.append(dict(profile=profile,club=club,element=element,class_index=ci,profile_index=pi,
                            old_result=error,extended_result=extended,literal_expected=wanted))
    assert len(ct)==168 and len(pt)==192 and windows[0]['class_index']==168 and windows[1]['profile_index']==193
    max_profile_index=max(12*p+read(0x6d25+12*c+e) for p in range(1,17) for c in range(14) for e in range(1,13))
    assert max_profile_index==204
    assert 0!=107  # zero padding is not an evidence-backed extension
    squad=list(range(101,111))+[314]
    resolved=next((i for i,player in enumerate(squad,1) if player==314),12)
    assert resolved==11 and resolved!=314
    assert ((56+2*4)&255)==64 and ((250+2*7)&255)==8 and (250+2*7)!=8
    gates=[e for e in range(1,13) if read(0x769+e)]
    assert gates==[2,4,11,12] and gates!=[2,4,12]
    sites={pc:site(part,pc) for part,pc in [('17','A36A'),('20','C712'),('20','C718'),
           ('14','8A26'),('14','8A5B'),('14','8A79'),('14','8AA5'),('14','8AC1'),
           ('23','EC89'),('20','CCEC'),('20','CCEF'),('02','0BD0')]}
    assert '[0xa91b]' in sites['C712']['instruction']
    assert '[di + 0xf], 0' in sites['C718']['instruction']
    assert '[di + 0xf], 5' in sites['A36A']['instruction']
    assert ', 0xd' in sites['EC89']['instruction'] and ', 0xb' in sites['CCEC']['instruction']
    assert 'jbe ' in sites['CCEF']['instruction'] and ', 0x258' in sites['0BD0']['instruction']
    report='experiments/E036-match-port/out/T68/compare-falsifier-run-direction-4-39891997938.txt'
    historical=(ROOT/report).read_text()
    assert historical.count('NOT CAUGHT: identical: FAIL')==8
    assert '8 matches expected differ, 0 pass, 8 fail' in historical
    current=json.loads((ROOT/'notes/engine-study/T97/transient-v5.json').read_text())
    field=next(f for f in current['records']['pitch']['fields'] if f['offset']==17)
    assert field['name']=='cached_skill_extra' and '20E3' in field['meaning'] and '34C1' in field['meaning']
    assert 'player-identity' in current['state_groups']['marking']['DS:9976+10*side+2*role, role=1..5']
    return dict(window_cases=windows,maximum_profile_index=max_profile_index,role_identity314_resolves_slot=resolved,cache56_leader4=64,
                extra_gate_elements=gates,source_sites=sites,historical_uncaught_count=8,
                controls={'zero-pad-window':'rejected:0 differs from107','identity-as-slot':'rejected:314 differs from11',
                          'omit-cache-wrap':'rejected:264 differs from8','omit-element11':'rejected:incomplete gate set'},
                ds_sources=ds_sources,legacy_window_source=source,historical_report=report)


def build():
    calc=calculations()
    candidates=[
        dict(id='table-windows',minimal_input={'ability':180,'cases':[[8,13,12],[16,2,3]],'window_lengths':[168,192]},
             expected='One-based class index168 requires169 bytes; profile index204 requires205 bytes at retained DS bases.',
             actual=calc['window_cases'],evidence=['1771:3A06','runtime/model/keeping.py'],disposition='documentation/test defect',
             reachability='Ordinary declared helper domains; reproduced here in the legacy analytical helper. Memory-faithful port reads full memory and does not use those short windows.',
             follow_up='#477 remains open for versioned complete/rebased windows and helper-domain coverage; never zero-pad retained evidence.'),
        dict(id='cache-and-identities',minimal_input={'initial_extra':56,'captain_leadership':4,'stored_taker_identity':314,'squad_slot':11},
             expected='20E3 adds2*leadership to cached byte;278A gates skill use and34C1 events1/2 directly read it for duration;6B65 maps stored player identity to first matching squad slot.',
             actual={'complete_extra':64,'direct_34C1_reader_events':[1,2],'resolved_slot':11,'wrapped_extra_at250_lead7':8,'current_ledger':'transient-v5.json'},
             evidence=['0791:A260','0791:20E3','0791:6B65','0791:A920','0791:1F3C'],disposition='documentation/test defect',
             reachability='Ordinary identity/cache mechanism; wrap example is representable only. All-unavailable1F3C retains an uninitialised winner local, with natural reachability unresolved.',
             follow_up='Corrected foundation prose and additive v5 ledger in this slice; #514 retains attribution/reachability context; no formula-input or runtime change.'),
        dict(id='uncaught-initial-direction',minimal_input={'intervention':'A36A pitch+F assignment5->4','historical_family':'O8,8 retained cases'},
             expected='An observable writer mutation would change at least one compared record; source direction remains5.',
             actual={'historical_identical':8,'before_move':'8889 assigns direction on both on-target and coin paths',
                     'C718':'persistent player+F tactics cleared, not pitch direction'},
             evidence=['0791:A2E6','0791:C5DC','0791:8889','0791:8AE9'],disposition='unresolved',
             reachability='Writer reached historically; no complete read-before-overwrite/alias proof through every earlier state handler. No fresh mutation run. Minimal change identified, full-state minimisation remains unavailable.',
             follow_up='#375 stays open: distinguish dead store on reached paths from observation blind spot before changing proof or dropping the write.'),
        dict(id='existing-edge-coverage',minimal_input={'mutations':['position-loop13->12','captain-invalid>11->>=11','Y/N-wait600->601']},
             expected='Literal listing edges are inclusive role13, valid captain slot11 and600-poll Y/N wait.',
             actual={'source_matches_port':True,'historical_review':'#412 reports all three mutants pass25 units; captain edge also survives seven S comparisons'},
             evidence=['0791:EA09','0791:CC7B','0791:0B7C'],disposition='documentation/test defect',
             reachability='Role13 and slot11 are admitted values; this slice checks instructions and reuses historical review, not a new test/mutant execution. Y/N600 differs from captain-prompt1000.',
             follow_up='#412 stays open for the three missing focused tests; do not claim current family/unit coverage proves these edges.'),
        dict(id='annotation-claims',minimal_input={'element':11,'mirror_point':[-3,-27],'direction':-1},
             expected='Gate table adds extra for11;2C86 multiplies both signed coordinate bytes by direction.',
             actual={'gate_elements':calc['extra_gate_elements'],'mirrored_point':[3,27],'clamp_in_2C86':False},
             evidence=['0791:278A','0791:2C86','0791:4354'],disposition='documentation/test defect',
             reachability='Source/table contradictions in old annotation text, not new engine bugs. Current guide uses instruction-backed meanings.',
             follow_up='#494/#512 remain open for scoped annotation regeneration; raw/named history and existing source pins preserved.'),
    ]
    artifacts=['notes/engine-study/T97/transient-v5.json','notes/engine-study/T98/window-repro-v1.json',
               'notes/engine-study/T98/validation-scope-v1.json','notes/engine-study/T108/T108a-v1.json',
               'notes/engine-study/T108/historical-issues-v1.json']
    sources=['runtime/model/keeping.py','runtime/original_match/port/attributes.py','runtime/original_match/port/positioning.py',
             'runtime/original_match/port/discipline.py','runtime/original_match/port/pilot.py',
             'runtime/original_match/port/selection.py','runtime/original_match/port/takers.py',
             calc['legacy_window_source'],calc['historical_report'],
             'static/goal-exe/code/seg_0791_02.asm','static/goal-exe/code/seg_0791_04.asm',
             'static/goal-exe/code/seg_0791_05.asm','static/goal-exe/code/seg_0791_14.asm',
             'static/goal-exe/code/seg_0791_17.asm','static/goal-exe/code/seg_0791_20.asm',
             'static/goal-exe/code/seg_0791_23.asm',*calc['ds_sources']]
    addresses=sorted({e for row in candidates for e in row['evidence'] if ':' in e})
    return pin(dict(task='T108b',status='proposed; candidate attribution pending independent review',method=__doc__,
                    sections=['Windows and identity','A surviving mutation is not a dead-store proof','Test and annotation limits'],
                    candidates=candidates,calculations=calc,supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in artifacts},
                    analysis_sha256=sha(Path(__file__).read_bytes())),addresses,sources,source_commit=BASE)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true')
    args=ap.parse_args();data=build();path=ROOT/'notes/engine-study/T108/T108b-v2.json'
    if args.check:
        assert json.loads(path.read_text())==data
        print('PASS: five candidates,2 legacy IndexErrors,identity/cache checks,source edges/historical8 uncaught,4 controls')
    else:write_new(path,data);print('wrote T108b audit; legacy analytical checks only, no guest/port engine execution')


if __name__=='__main__':main()
