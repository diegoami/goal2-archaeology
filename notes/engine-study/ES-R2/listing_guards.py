#!/usr/bin/env python3
"""Literal source expectations with altered-listing negative controls; not engine execution."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
EXPECTED={
 'seg_0791_06.asm':{'3884':'call 0x2eb8','3889':'je 0x388e','388B':'jmp 0x3b0f','3692':'mov al, byte ptr es:[di + 0x11]','3698':'add ax, dx','369F':'div cx'},
 'seg_0791_14.asm':{'8972':'jl 0x89e5','8C45':'jbe 0x8c61'},
 'seg_1771_12.asm':{'870A':'jae 0x8723'},
 'seg_1771_06.asm':{'3F47':'cmp byte ptr es:[di + 6], 1','3F4C':'jne 0x3f5f','3F59':'xor ax, ax','3F5B':'mov word ptr [di - 0x65be], ax'},
 'seg_0791_11.asm':{'6642':'cmp byte ptr [0x8326], 0','6647':'je 0x664c','6649':'jmp 0x66df','665C':'call 0xc173'},
 'seg_0791_09.asm':{'50FB':'jmp 0x532c','51AB':'jmp 0x532c','528F':'jmp 0x532c','52DB':'jmp 0x532c','52DD':'mov ax, 2','5324':'je 0x532c','5329':'call 0x4e28','532C':'jmp 0x5332'},
}


def validate(lines):
    for (file,pc),line in lines.items():assert line.rstrip().endswith(' '+EXPECTED[file][pc]),(file,pc,line)


def build():
    lines={};sources={}
    for file,sites in EXPECTED.items():
        path=ROOT/'static/goal-exe/code'/file;raw=path.read_bytes();sources[str(path.relative_to(ROOT))]=hashlib.sha256(raw).hexdigest()
        for pc in sites:
            matches=[(n,l) for n,l in enumerate(raw.decode().splitlines(),1) if l.startswith(pc+' ')]
            assert len(matches)==1,(file,pc)
            lines[file,pc]=matches[0][1]
    validate(lines);negatives=[]
    for key in lines:
        altered=dict(lines);altered[key]=key[1]+'  90              nop'
        try:validate(altered)
        except AssertionError:negatives.append({'file':key[0],'pc':key[1],'alteration':'nop','result':'rejected'})
        else:raise AssertionError('negative escaped '+str(key))
    return dict(scope=__doc__,source_sha256=sources,expectations=[dict(file=f,pc=pc,expected=EXPECTED[f][pc],actual=line) for (f,pc),line in lines.items()],negative_controls=negatives)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--receipt',type=Path);a=ap.parse_args();data=build()
    if a.receipt:
        with a.receipt.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    print(f'PASS: {len(data["expectations"])} literal source expectations; {len(data["negative_controls"])} altered-instruction controls rejected; no engine calls')


if __name__=='__main__':main()
