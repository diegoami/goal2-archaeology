#!/usr/bin/env python3
"""Read-only source/input/registration compatibility; no target or game engine is executed."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
from check import ROOT,write_new,sha
ACCEPTED='55d7a479a7288ea044ceaa315eaff87e2077fdb6'
CRITICAL=['runtime/original_match/port/ball.py','runtime/original_match/port/restarts.py','runtime/original_match/port/geometry.py','runtime/original_match/machine.py','runtime/original_match/port/mem.py','runtime/original_match/port/guest.py','runtime/original_match/image.py','static/goal-exe/code/seg_0791_06.asm','static/goal-exe/code/seg_0791_12.asm']


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path);a=ap.parse_args()
    sources={}
    for p in CRITICAL:
        raw=(ROOT/p).read_bytes();assert raw==subprocess.check_output(['git','show',ACCEPTED+':'+p],cwd=ROOT),p;sources[p]=sha(raw)
    sys.path.insert(0,str(ROOT/'runtime'))
    from original_match import Image,port
    from original_match.assets import reference_image,REFERENCE
    raw=reference_image(ROOT/'.cache/dl');assert sha(raw)==REFERENCE['sha256']
    image=Image.from_bytes(raw)
    assert image.sha256()=='87400f6a866e0798f61a9f3ab3bfcaa322469fa6b238b0061f1b7ab2b6a3f979'
    assert not image.build_problems()
    entries={address:(reg.name,e) for reg,_ in port.load(['all']) for address,e in reg.entries.items()}
    registry={address:dict(module=entries[address][0],ret=entries[address][1].ret,production_stub=entries[address][1].stub) for address in ['0791:34C1','0791:333F','0791:7621','0791:2CC5','23E4:0294','23E4:0279','214B:1EA1']}
    assert registry['0791:34C1']['ret']=='retf 8' and registry['0791:7621']['ret']=='retf 4'
    assert registry['214B:1EA1']['production_stub'] and all(not row['production_stub'] for name,row in registry.items() if name!='214B:1EA1')
    result=dict(scope=__doc__,accepted_study_commit=ACCEPTED,current_source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),unchanged_critical_sha256=sources,input=dict(reference=REFERENCE,memory_component_sha256=image.sha256(),build_problems=[]),registry=registry,engine_invocations=0,limits=['Imports/registration and image hash/build checks only;not proof of routine execution.','Production1EA1is a declared T73sound stub;actual calls and unmasked differences must be reported.'])
    if a.receipt:write_new(a.receipt,result)
    print('PASS: selected physics/machinery unchanged from m6;E006 hashes/build verified;production entries/stub disclosed;zero engine invocations')


if __name__=='__main__':main()
