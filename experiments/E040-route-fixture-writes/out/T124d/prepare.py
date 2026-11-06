"""T124d PRIMARY natural original world continuation and #673 prerequisite repair.

No port installed, no stage/group/result/calendar edits, no managed UI bypass.
Starts accepted nativeT124tCP4, records actual original play_round/RouteMatch/
legal-eleven continuation through7090/71B2/four74BEbranches, then REALworldfinals
and next6730 after original8->2 rollover(reference ONLY). Resumable percall and
constructor-entry/tail; all input/context bytes remain ignored/private.
This producer depends only on original Route/Match/Machine/Image and its own
source. Port-module implementation is independent and NEVER installed here.
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
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS,GuestError

PHASES=[('playoffs','1771:7090',6,1),('groups','1771:71B2',7,1),
        ('last16','1771:74BE',8,4),('quarters','1771:74BE',8,3),
        ('semis','1771:74BE',8,2),('finals','1771:74BE',8,1),('qualifying','1771:6730',2,1)]
RECEIPT=ROOT/'experiments/E040-route-fixture-writes/out/T124t/continuation-context.jsonl'


def sha(v):return hashlib.sha256(v).hexdigest()


def public(v):
    if isinstance(v,bytes):return {'length':len(v),'sha256':sha(v)}
    if isinstance(v,(list,tuple)):return [public(x) for x in v]
    if isinstance(v,dict):return {k:public(x) for k,x in v.items()}
    return v


def source_hashes():
    paths=['runtime/original_match/route.py','runtime/original_match/route_team.py','runtime/original_match/match.py',
           'runtime/original_match/machine.py','runtime/original_match/image.py',str(Path(__file__).relative_to(ROOT))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def game(m):
    g=m.far(0xA923)
    return {'stage':m.read(g+0x3C,1)[0],'rounds':m.read(g+0x3D,1)[0],
            'cursor':m.word_at(g+0x26),'count':m.word_at(g+0x28),
            'mode':m.read(g+0x40,1)[0],'year_word':m.word_at(g+0x38)}


def fixture(m,n):
    p=m.far(0xA92B)+8*(n-1);b=m.read(p,8)
    return {'index':n,'score_or_mark':b[0],'second_score_or_group':b[1],
            'kind':b[2],'winner_flag':b[3],'side4':int.from_bytes(b[4:6],'little'),
            'side6':int.from_bytes(b[6:8],'little'),'sha256':sha(b)}


def aggregate_records(m,start=2001):
    return [{'aggregate':fixture(m,2401+i),'legs':[fixture(m,start+2*i),fixture(m,start+2*i+1)]} for i in range(8)]


def context(r):return {'regs':{n:r.m.reg(n) for n in REGS},'waiting_key':r.keys.waiting}


def restore(r,ctx):
    assert set(ctx['regs'])==set(REGS)
    for n,v in ctx['regs'].items():r.m.set_reg(n,v)
    r.keys.waiting=ctx['waiting_key']


def load(cp):
    data=(ROOT/cp['path']).read_bytes();assert sha(data)==cp['sha256']
    r=R.Route(Image(data),entry='play_round',record_writes=False)
    restore(r,cp['context']);assert not r.m._ports
    return r


def checkpoint(r,label):
    assert not r.m.frames and not r.m.muted
    data=r.header+r.m.read(0,MEM_SIZE)+r.tail;h=sha(data)
    path=ROOT/'.cache/t124d/natural'/f'{label}-{h[:16]}.mem';path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    assert sha(path.read_bytes())==h
    return {'path':str(path.relative_to(ROOT)),'sha256':h,'context':context(r)}


def emit(f,value):
    f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k] for k in ('status','phase','call','end','elapsed_s') if k in value}),flush=True)


def original_cp4():
    assert sha(RECEIPT.read_bytes())=='5916ab9562dd296c324d92f90dcc2eb643af2861323f6fddcafab404e63bade6'
    cp=next(v['checkpoint'] for v in map(json.loads,RECEIPT.read_text().splitlines()) if v.get('status')=='round' and v['round']==4)
    assert cp['sha256']=='3eeb9e4b48bfa95b271c6bbef1cd90628d9a91218048530427e6e5588efed890'
    return cp


def prepare(out,resume):
    old=[json.loads(l) for l in out.read_text().splitlines()] if resume else []
    if old:
        assert old[0]['source_hashes']==source_hashes()
        if old[-1]['status']=='completed':return
        cp=next(v['checkpoint'] for v in reversed(old) if v.get('checkpoint'))
    else:cp=original_cp4()
    r=load(cp)
    if not old:assert game(r.m)=={'stage':5,'rounds':1,'cursor':1361,'count':2001,'mode':1,'year_word':1}
    state={'index':sum(v.get('status')=='constructed' for v in old),'capture':True,'found':None,'before_end':None}
    finalizers=[];start=time.monotonic();calls=max((v.get('call',0) for v in old),default=0)
    def pre_end(replay):
        if not replay:state['before_end']={'checkpoint':checkpoint(r,f"before-stage-end-{state['index']}"),'game':game(r.m)}
    def finalizer(replay):
        if not replay:
            m=r.m;s=m.reg('ss')*16+m.reg('sp')
            finalizers.append({'return':m.where(m.word_at(s+2),m.word_at(s)), 'game':game(m)})
    def entry(replay,address):
        if replay or not state['capture']:return
        phase,target,stage,rounds=PHASES[state['index']]
        assert address==target,(phase,address,target)
        g=game(r.m);assert (g['stage'],g['rounds'])==(stage,rounds),(phase,g)
        state['found']={'phase':phase,'target':target,'checkpoint':checkpoint(r,phase+'-entry'),
                        'before_stage_end':state['before_end'],'entry_game':g,'aggregates':aggregate_records(r.m)}
        r.m.stop('t124d-builder-entry')
    r.m.at('000E:70E6',pre_end);r.m.at('1771:8757',finalizer)
    for address in sorted({v[1] for v in PHASES}):r.m.at(address,lambda replay,a=address:entry(replay,a))
    pending=old[-1] if old and old[-1]['status']=='constructor-entry' else None
    with out.open('a' if resume else 'x') as f:
        if not resume:emit(f,{'schema':'t124d-primary/1','source':cp,'start':game(r.m),'source_hashes':source_hashes(),
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'scope':'originalCP4/Route/RouteMatch/legal11; no ports, no stage/group/result/calendar edits or UI bypass; original rollover reference only'})
        while state['index']<len(PHASES):
            phase,target,stage,rounds=PHASES[state['index']]
            if pending is None:
                before=len(r.record);final_before=len(finalizers);calls+=1
                try:r.call()
                except Exception as exc:
                    if not (isinstance(exc,GuestError) and state['found'] and str(exc)=='play_round stopped: t124d-builder-entry'):
                        emit(f,{'status':'blocked','phase':phase,'call':calls,'checkpoint':checkpoint(r,phase+'-blocked'),
                            'error_type':type(exc).__name__,'error_sha256':sha(str(exc).encode()),'end':game(r.m)})
                        raise
                entries=r.record[before:]
                common={'phase':phase,'call':calls,'end':game(r.m),
                    'matches':[v[1] for v in entries if v[0]=='match'],'teams':[v[1] for v in entries if v[0]=='team'],
                    'ordered_record_sha256':sha(json.dumps(public(entries),sort_keys=True).encode()),
                    'finalizer_visits':finalizers[final_before:],'elapsed_s':round(time.monotonic()-start,4)}
                if not state['found']:
                    emit(f,{**common,'status':'returned-call','checkpoint':checkpoint(r,phase+f'-call-{calls}')})
                    continue
                pending={**common,**state['found'],'status':'constructor-entry'}
                assert pending['before_stage_end']
                emit(f,pending)
            state['capture']=False
            before=len(r.record)
            assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
            assert r.m.reg('sp')==0x3EEE
            emit(f,{'status':'constructed','phase':phase,'target':target,'input_checkpoint':pending['checkpoint'],
                'checkpoint':checkpoint(r,phase+'-constructed'),'end':game(r.m),'aggregates':aggregate_records(r.m),
                'ordered_record_sha256':sha(json.dumps(public(r.record[before:]),sort_keys=True).encode()),
                'elapsed_s':round(time.monotonic()-start,4)})
            state.update(index=state['index']+1,capture=True,found=None,before_end=None);pending=None
        emit(f,{'status':'completed','phases':[v[0] for v in PHASES],'end':game(r.m),'elapsed_s':round(time.monotonic()-start,4)})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--resume',action='store_true');a=ap.parse_args()
    prepare(Path(a.out),a.resume)
if __name__=='__main__':main()
