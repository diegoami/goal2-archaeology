"""Resumable NATURAL input preparation for all three continental constructor branches.

Original Route/RouteMatch only: no port installed, no edited stage/group/result
bytes. Starts published213 for6B55, acceptedCP1 for6E59semis andCP2 forfinals.
At actual constructor entry, preserves full memory+16CPUregs+waiting_key with
its already-pushed real76B1 caller frame. Also retains the prior70E6 boundary
for original in-season ageing work. Construction/tail proofs use these inputs,
so long managed matches are played once rather than once per differential arm.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE.parent.parent)]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS,GuestError
from runner import expected

STATE='53b69d3dfb964e77-snap-0213-20261011T142027Z.sav'
RECEIPT=ROOT/'experiments/E040-route-fixture-writes/out/T124t/continuation-context.jsonl'


def sha(data):return hashlib.sha256(data).hexdigest()


def public_record(v):
    if isinstance(v,bytes):return {'length':len(v),'sha256':sha(v)}
    if isinstance(v,(list,tuple)):return [public_record(x) for x in v]
    if isinstance(v,dict):return {k:public_record(x) for k,x in v.items()}
    return v


def source_hashes():
    paths=['runtime/original_match/route.py','runtime/original_match/route_team.py','runtime/original_match/match.py',
           'runtime/original_match/machine.py','runtime/original_match/port/stages.py',str(Path(__file__).relative_to(ROOT))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def rows():
    assert sha(RECEIPT.read_bytes())=='5916ab9562dd296c324d92f90dcc2eb643af2861323f6fddcafab404e63bade6'
    return {v['round']:v for v in map(json.loads,RECEIPT.read_text().splitlines()) if v.get('status')=='round'}


def game(m):
    g=m.far(0xA923)
    return {'stage':m.read(g+0x3C,1)[0],'rounds':m.read(g+0x3D,1)[0],
            'cursor':m.word_at(g+0x26),'count':m.word_at(g+0x28),'mode':m.read(g+0x40,1)[0],
            'year_word':m.word_at(g+0x38)}


def restore(r,ctx):
    assert set(ctx['regs'])==set(REGS)
    for name,value in ctx['regs'].items():r.m.set_reg(name,value)
    r.keys.waiting=ctx['waiting_key']


def load(cp):
    data=(ROOT/cp['path']).read_bytes();assert sha(data)==cp['sha256']
    r=R.Route(Image(data),entry='play_round',record_writes=False)
    restore(r,cp['context']);return r


def checkpoint(r,label):
    # Within an original instruction hook the CPU is at that instruction before
    # execution. No emulation thread can mutate it during this synchronous read.
    assert not r.m.frames and not r.m.muted
    data=r.header+r.m.read(0,MEM_SIZE)+r.tail;h=sha(data)
    path=ROOT/'.cache/t124c'/f'{label}-{h[:16]}.mem'
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    assert sha(path.read_bytes())==h
    return {'path':str(path.relative_to(ROOT)),'sha256':h,
            'context':{'regs':{n:r.m.reg(n) for n in REGS},'waiting_key':r.keys.waiting}}


def emit(f,value):
    f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k] for k in ('case','status','call','end','elapsed_s') if k in value}),flush=True)


def prepare(case,out,resume):
    goldens=rows();source_round={'groups':0,'semis':1,'finals':2}[case]
    target='1771:6B55' if case=='groups' else '1771:6E59'
    golden=goldens[source_round+1]['checkpoint']
    previous=[]
    if resume:
        previous=[json.loads(l) for l in out.read_text().splitlines()]
        assert previous[0]['source_hashes']==source_hashes()
        if previous[-1]['status']=='builder-entry':return
    if previous and any(v.get('checkpoint') for v in previous):
        cp=next(v['checkpoint'] for v in reversed(previous) if v.get('checkpoint'))
        r=load(cp)
    elif source_round:
        cp=goldens[source_round]['checkpoint'];r=load(cp)
    else:
        data=(ROOT/'.cache/dl'/STATE).read_bytes();assert sha(data)==expected(STATE)
        r=R.Route(Image.from_savestate(data),entry='play_round',record_writes=False)
        cp={'state':STATE,'sha256':sha(data)}
    initial=game(r.m)
    found=[];before_end=[]
    def pre_end(replay):
        if not replay:before_end.append({'checkpoint':checkpoint(r,case+'-before-stage-end'),'game':game(r.m)})
    def builder_entry(replay):
        if not replay:
            found.append({'checkpoint':checkpoint(r,case+'-builder-entry'),'game':game(r.m)})
            r.m.stop('t124c-builder-entry')
    r.m.at('000E:70E6',pre_end)
    r.m.at(target,builder_entry)
    start=time.monotonic();completed=sum(v.get('status')=='returned-call' for v in previous)
    with out.open('a' if resume else 'x') as f:
        if not resume:emit(f,{'schema':'t124c-natural-prepare/1','case':case,'source':cp,'start':initial,
            'target':target,'expected_post_tail_golden':golden,'source_hashes':source_hashes(),
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'scope':'actual original play_round/RouteMatch/legal-eleven; no ports and no stage/group/result edits'})
        for number in range(completed+1,65):
            before=len(r.record)
            try:r.call()
            except GuestError as exc:
                if not found or str(exc)!='play_round stopped: t124c-builder-entry':raise
            entries=r.record[before:]
            common={'case':case,'call':number,'end':game(r.m),
                'matches':[v[1] for v in entries if v[0]=='match'],
                'teams':[v[1] for v in entries if v[0]=='team'],
                'ordered_record_sha256':sha(json.dumps(public_record(entries),sort_keys=True).encode()),
                'elapsed_s':round(time.monotonic()-start,4)}
            if found:
                assert before_end
                emit(f,{**common,'status':'builder-entry','target':target,
                    'checkpoint':found[-1]['checkpoint'],'before_stage_end':before_end[-1],
                    'expected_post_tail_golden':golden})
                return
            emit(f,{**common,'status':'returned-call','checkpoint':checkpoint(r,case+f'-call-{number}')})
    raise AssertionError('no constructor in64actualplay_round calls')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=('groups','semis','finals'),required=True)
    ap.add_argument('--out',required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    prepare(a.case,Path(a.out),a.resume)
if __name__=='__main__':main()
