"""T124e original natural announcement captures and paired actual-tail proofs.

No producer ports, data edits, or fabricated caller frames. All original private
inputs are hash checked with their complete16CPU/key context restored. Public
pages are hashes/scalars; exact cells/decoded lines remain ignored private files.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import route as R,port
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS,GuestError
from original_match.port.prove import Prover
from original_match.news import capture_news_page,news_pages
from tests.test_port_stage_news import specs
_sp=importlib.util.spec_from_file_location('_t124e_dprepare',HERE.parent/'T124d/prepare.py')
D=importlib.util.module_from_spec(_sp);_sp.loader.exec_module(D)
sha=D.sha


def sources():
    paths=['runtime/original_match/route.py','runtime/original_match/route_team.py',
      'runtime/original_match/match.py','runtime/original_match/machine.py',
      'runtime/original_match/image.py','runtime/original_match/news.py',
      'tests/test_port_stage_news.py',str(Path(__file__).relative_to(ROOT))]
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'runtime/original_match/port').glob('*.py'))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def emit(f,v):
    f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno());print(v.get('status',v.get('schema')),flush=True)


def checkpoint(r,label):
    assert not r.m.frames and not r.m.muted
    data=r.header+r.m.read(0,MEM_SIZE)+r.tail;h=sha(data)
    p=ROOT/'.cache/t124e'/f'{label}-{h[:16]}.mem';p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_bytes(data)
    assert sha(p.read_bytes())==h
    return {'path':str(p.relative_to(ROOT)),'sha256':h,'context':D.context(r)}


def load(cp):
    data=(ROOT/cp['path']).read_bytes();assert sha(data)==cp['sha256']
    r=R.Route(Image(data),entry='play_round',record_writes=False)
    D.restore(r,cp['context']);assert not r.m._ports
    return r


def source(phase):
    if phase=='continental':
        path=HERE.parent/'T124c/natural-groups-input-v1.jsonl'
        rows=list(map(json.loads,path.read_text().splitlines()))
        return next(v['checkpoint'] for v in rows if v.get('status')=='builder-entry'),path
    if phase=='world-qualifying':
        path=HERE.parent/'T124t/continuation-context.jsonl'
        assert sha(path.read_bytes())=='5916ab9562dd296c324d92f90dcc2eb643af2861323f6fddcafab404e63bade6'
        return next(v['checkpoint'] for v in map(json.loads,path.read_text().splitlines()) if v.get('status')=='round' and v['round']==3),path
    path=HERE.parent/'T124d/natural-inputs-v1.jsonl'
    target='groups' if phase=='world-finals' else 'qualifying'
    return next(v['checkpoint'] for v in map(json.loads,path.read_text().splitlines()) if v.get('status')=='constructor-entry' and v['phase']==target),path


def pages(r,label,private=False):
    rows=[];m=r.m
    def entry(replay):
        if replay or m.muted:return
        s=m.reg('ss')*16+m.reg('sp');ret=m.word_at(s)
        if ret!=0x6625:return
        bp=m.reg('bp');country=m.frame_word(bp,6);g=m.far(0xA923)
        tag=m.read(m.far(0xA917)+191*country+46,1)[0]
        cursor=m.read(g+1,1)[0]
        snap=capture_news_page(m,return_address='000E:6625',country=country,manager=tag,
              flags_words=tuple(m.word_at(s+i) for i in (2,4,6)),waiting_key=r.keys.waiting,
              pushed_back=bool(m.rd(R.PUSHED_BACK,1)),key_code=m.rd(R.KEY,1))
        lines=news_pages(snap)[0]
        row={'index':len(rows),'country':country,'manager_tag':tag,'manager_cursor':cursor,
             'flags_words':list(snap.flags_words),'cells_sha256':sha(snap.cells),
             'lines_sha256':sha(json.dumps(lines,ensure_ascii=False).encode()),
             'waiting_key':r.keys.waiting,'pushed_back':snap.pushed_back,'key_code':snap.key_code}
        assert tag==128+cursor
        if private:
            d=ROOT/'.cache/t124e/pages';d.mkdir(parents=True,exist_ok=True)
            p=d/f'{label}-{len(rows)}-{row["cells_sha256"][:16]}.json'
            value={'cells_hex':snap.cells.hex(),'decoded_lines':lines,'metadata':row}
            data=json.dumps(value,ensure_ascii=False,sort_keys=True).encode()
            if not p.exists():p.write_bytes(data)
            assert p.read_bytes()==data
            row['private_capture']={'path':str(p.relative_to(ROOT)),'sha256':sha(data)}
        rows.append(row)
    m.at('000E:05F6',entry)
    return rows


def prepare(phase,out):
    cp,path=source(phase);r=load(cp);found={};m=r.m
    def entry(replay):
        if replay:return
        found['checkpoint']=checkpoint(r,phase+'-entry');found['game']=D.game(m)
        m.stop('t124e-announcement-entry')
    m.at('000E:60CB',entry)
    with out.open('x') as f:
        emit(f,{'schema':'t124e-natural-input/1','phase':phase,'source':cp,'source_receipt':str(path.relative_to(ROOT)),
                'source_receipt_sha256':sha(path.read_bytes()),'source_hashes':sources(),
                'scope':'unmodified actual original continuation; annualrollover referenceONLY'})
        if phase=='world-qualifying':
            for n in range(20):
                try:r.call()
                except GuestError:
                    if not found:raise
                if found:break
            else:raise AssertionError('announcement not reached')
        else:assert m.run(m.lin('000E:77C2'),120,fresh=True)=='t124e-announcement-entry'
        assert found
        emit(f,{'status':'announcement-entry','phase':phase,**found})
    return found


def prove(phase,prepared,out,variant=None):
    rows=list(map(json.loads,prepared.read_text().splitlines()));cp=rows[-1]['checkpoint']
    start=time.monotonic();ref=load(cp);rp=pages(ref,phase+'-original',True)
    assert ref.m.run(ref.m.lin('000E:77C2'),120,fresh=True) is None
    r=load(cp);pp=pages(r,phase+'-candidate',True)
    inst=port.install(r.m,specs(variant));p=Prover(r.m,inst)
    with out.open('x') as f:
        emit(f,{'schema':'t124e-natural-proof/1','phase':phase,'source_hashes':sources(),'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'input_sha256':cp['sha256'],'input_receipt_sha256':sha(prepared.read_bytes()),'model':'inherited Codex GPT-6 family; exact variant unavailable'})
        assert r.m.run(r.m.lin('000E:77C2'),120,fresh=True) is None
        strip=lambda xs:[{k:v for k,v in x.items() if k!='private_capture'} for x in xs]
        assert strip(pp)==strip(rp) and pp
        regs={n:[ref.m.reg(n),r.m.reg(n)] for n in REGS if ref.m.reg(n)!=r.m.reg(n)}
        memory=ref.m.read(0,MEM_SIZE)==r.m.read(0,MEM_SIZE)
        emit(f,{'phase':phase,'status':'completed','pages':pp,'reference_pages':rp,'summary':p.summary(),
          'all_memory_equal':memory,'register_differences':regs,'records_equal':ref.record==r.record,
          'waiting_key_equal':ref.keys.waiting==r.keys.waiting,
          'ordered_record_sha256':sha(json.dumps(D.public(r.record),sort_keys=True).encode()),
          'rng_events':sum(e[0]=='rng' for e in r.record),'end':D.game(r.m),'elapsed_s':round(time.monotonic()-start,4)})
        assert memory and not regs and ref.record==r.record and ref.keys.waiting==r.keys.waiting


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',required=True,choices=['continental','world-qualifying','world-finals','next-continental'])
    ap.add_argument('--prepare',action='store_true');ap.add_argument('--input');ap.add_argument('--out',required=True);a=ap.parse_args()
    if a.prepare:prepare(a.phase,Path(a.out))
    else:prove(a.phase,Path(a.input),Path(a.out))
if __name__=='__main__':main()
