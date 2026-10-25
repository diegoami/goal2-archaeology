"""T94: unmodified original TEAM label routines and complete-panel checks."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('manager_probe', ROOT/'notes/429/probe.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
Image, Original, glyphs, sha = helper.Image, helper.Original, helper.glyphs, helper.sha


def pstr(g, address):
    n = g.mem(address, 1)[0]
    return g.mem(address+1, n)


def label(g, table, band):
    return pstr(g, g.DS*16+0x6EB4+16*g.mem(g.DS*16+table+band, 1)[0])


def screen_setup(g):
    g.put(g.DS*16+0xA96E, b'\0\0'+(0x7A00).to_bytes(2, 'little'))
    g.put(0x7A000, b'\x20\x07'*2000)


def cells(g, row, col, n):
    return g.mem(0x7A000+160*(row-1)+2*(col-1), 2*n)[::2]


def drawn(original, address, args, payload, row, col, far, pop):
    g = original.g
    screen_setup(g)
    original.call(address, args, far=far, pop=pop)
    assert cells(g,row,col,len(payload)) == payload, (address,args,glyphs(payload))
    assert cells(g,row,col+len(payload),1) == b' ', (address, 'extra cell')
    return glyphs(payload)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists(): raise SystemExit('immutable output already exists')
    sources=[('E010-r0001',ROOT/'.cache/dl/e1dee7e2f5ad443e-E010-r0001-halftime.sav'),
             ('E006-r0001',ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav')]
    receipts=[]
    for run,path in sources:
        raw=path.read_bytes()
        record=json.loads((ROOT/'runs'/run.split('-')[0]/(run+'.json')).read_text())
        assert sha(raw) in [o.get('sha256') for o in record['outputs']]
        image=Image.from_savestate(raw)
        assert not helper.build_problems(image.memory,image.load)
        original=Original(image);g=original.g
        rows=[]
        for country in range(1,129):
            rec=g.mem(g.far(0xA917)+191*country,191)
            rating=((5-rec[44])*(33-rec[42])+129-rec[43])//2
            assert 1<=rating<=128
            manager=rec[46]
            status=g.mem(g.far(0xA91F)+3*manager+1,1)[0]
            skill_payload=label(g,0x7884,(rating-1)//8)
            status_payload=(b'' if manager==0 else pstr(g,g.lin('1771:0AF0')) if status==0
                            else label(g,0x7894,(status-1)//8))
            skill=drawn(original,'1771:1527',[25,8,country],skill_payload,8,25,False,6)
            status_text=drawn(original,'1771:0AF8',[24,10,manager],status_payload,10,24,True,6)
            rows.append(dict(country=country,continent=rec[44],continental_rank=rec[42],world_rank=rec[43],
                             rating=rating,manager=manager,status_byte=status,
                             skill=skill,status=None if manager==0 else status_text))
        panels=[]
        for country in (12,27,128):
            screen_setup(g)
            original.call('1771:157D',[country],far=False,pop=2)
            row=rows[country-1]
            for key,line,col in [('skill',8,25),('status',10,24)]:
                expected=row[key] or ''
                assert glyphs(cells(g,line,col,len(expected)))==expected,(run,country,key)
            panels.append(dict(country=country,skill=row['skill'],status=row['status'],
                               row8=glyphs(cells(g,8,1,40)),row10=glyphs(cells(g,10,1,40))))
        receipts.append(dict(run=run,base_sha256=sha(raw),countries=rows,panels=panels))
    # Independent synthetic boundaries in a private copied machine, not natural country states.
    statuses=[]
    manager=134
    for value in range(256):
        g.put(g.far(0xA91F)+3*manager+1,bytes([value]))
        payload=pstr(g,g.lin('1771:0AF0')) if value==0 else label(g,0x7894,(value-1)//8)
        text=drawn(original,'1771:0AF8',[24,10,manager],payload,10,24,True,6)
        statuses.append(dict(status_byte=value,text=text))
    assert drawn(original,'1771:0AF8',[24,10,0],b'',10,24,True,6)==''
    skills=[]
    # continent4/rank32 gives (129-world)/2: hit every integer rating1..64;
    # continent1/rank1 gives (257-world)/2: hit every rating65..128.
    for rating in range(1,129):
        continent,crank,world=(4,32,129-2*rating) if rating<=64 else (1,1,257-2*rating)
        address=g.far(0xA917)+191*128
        for off,value in ((44,continent),(42,crank),(43,world)):
            g.put(address+off,bytes([value]))
        original.call('1771:10E7',[128],far=True,pop=2)
        assert g.reg('ax')==rating
        payload=label(g,0x7884,(rating-1)//8)
        text=drawn(original,'1771:1527',[25,8,128],payload,8,25,False,6)
        skills.append(dict(rating=rating,continent=continent,continental_rank=crank,world_rank=world,text=text))
    receipt=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 producer_sha256=sha(Path(__file__).read_bytes()),helper_sha256=sha((ROOT/'notes/429/probe.py').read_bytes()),
                 unicorn=helper.unicorn.__version__,method='isolated original routines and full original TEAM drawing; synthetic call frames, no behavior hooks',
                 bound_per_call='2seconds/500000instructions',states=receipts,
                 synthetic_statuses=statuses,synthetic_skills=skills,manager_zero_draws_nothing=True,
                 source_hashes={p:sha((ROOT/p).read_bytes()) for p in [
                     'static/goal-exe/code/seg_1771_02.asm','static/goal-exe/code/seg_1771_03.asm']})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(receipt,indent=2,ensure_ascii=True)+'\n')
    print('256 genuine country/state label pairs; 6 complete original TEAM panels; 256 status and 128 skill controls exact')
    print(json.dumps(receipts[0]['countries'][11]))
    print(json.dumps(receipts[0]['panels'][0]))


if __name__=='__main__': main()
