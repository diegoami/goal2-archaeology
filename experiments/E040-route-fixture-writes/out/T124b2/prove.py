"""T124b2 full-builder composition, original call-frame oracles and immutable receipts.

Static first: named1771 parts4/5; raw1771_08 56E4..577E and1771_09
6730..6B54; raw23E4_02 11D7..11E3. Every direct callee of6730 is a
real registered port here (including the library003C/0018/007B/06B1),
so leaf-scratch equality cannot hide an initial-year CX seed mismatch.
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
from original_match import port
from original_match.port import Registry,stages
from original_match.port.prove import Prover,ProofError
from original_match.machine import MEM_SIZE,REGS
from original_match.image import Image
from original_match import route as R
from tests.test_port_stage_qualifying import Draw,ENTRIES,DRAW_ENTRIES
from tests.test_port_stages import IMAGE_SHA


def imported(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

B1=imported('t124b1_proof',HERE.parent/'T124b1/prove.py')
previous=sys.modules.get('prove')
sys.modules['prove']=B1
WORLD=imported('t124b1_world',HERE.parent/'T124b1/world.py')
if previous is None:del sys.modules['prove']
else:sys.modules['prove']=previous
sha=B1.sha;game=B1.game;digests=B1.digests;public_record=B1.public_record


def emit(f,value):
    f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k] for k in ('case','status','elapsed_s') if k in value}),flush=True)


def sources():
    paths=['runtime/original_match/port/stages.py','runtime/original_match/port/runtime.py',
       'runtime/original_match/port/entrypoints.py','runtime/original_match/port/attributes.py',
       'runtime/original_match/port/update.py','runtime/original_match/port/prove.py',
       'runtime/original_match/route.py','runtime/original_match/route_team.py',
       'tests/test_port_stage_qualifying.py',str(Path(__file__).relative_to(ROOT)),
       'experiments/E040-route-fixture-writes/out/T124b1/prove.py',
       'experiments/E040-route-fixture-writes/out/T124b1/world.py']
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def specs(variant=None):
    wanted=set(stages.PORTS.entries)-{'1771:8208','1771:76B1'}
    # Four new routines + all T124b1 ranking helpers + old fixture helpers;
    # original outer76B1/stage_end/80DA remain original reference code.
    wanted|={'214B:0018','214B:003C','214B:007B','214B:06B1','1771:0B77','1771:10E7','1771:5C94','1771:5CCB'}
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for address,e in reg.entries.items():
            if address in wanted:
                assert not e.stub,(address,e.stub)
                sub._add(e)
        if sub.entries:
            sub.variants=dict(reg.variants)
            result.append((sub,variant if reg.name=='stages' else None))
    actual={a for reg,_ in result for a in reg.entries}
    assert actual==wanted,(wanted-actual,actual-wanted)
    return result


def returned(m):return {reg:m.reg(reg) for reg in REGS}


def paired(f,kind,variant):
    if kind=='natural':
        make=lambda:B1.route_from_checkpoint()[0]
        cp=B1.route_from_checkpoint()[1]
        description='unmodified T124tCP3: original final fixtures/rollover, actualplay_round4->5'
    else:
        path=HERE.parent/'T124b1/world-prepare-v4.jsonl'
        rows=[json.loads(line) for line in path.read_text().splitlines()]
        assert rows[-1]['status']=='prepared'
        cp=rows[-1]['final_checkpoint']
        assert cp['sha256']=='f5610eca4a222f2b761f5207bd126b29623c23b1e6e6f4425389ab1e374b0fc0'
        make=lambda:WORLD.load(cp)
        description='declared synthetic world: original-built/results lineage B1worldv4; actualplay_round8->2'
    start=time.monotonic();reference=make();before=game(reference.m)
    reference.round()
    r=make();inst=port.install(r.m,specs(variant));p=Prover(r.m,inst)
    try:r.round()
    except ProofError as exc:
        emit(f,{'case':kind,'status':'falsifier_caught','variant':variant,'difference':str(exc),
                'checkpoint_sha256':cp['sha256'],'summary':p.summary(),'elapsed_s':round(time.monotonic()-start,4)})
        if not variant:raise
        return
    assert not variant,'mutant not caught'
    assert digests(r.m)==digests(reference.m),'full country/manager/game/calendar records differ'
    assert r.record==reference.record,'full ordered RNG/key/team/match/events differ'
    a,b=reference.m.read(0,MEM_SIZE),r.m.read(0,MEM_SIZE)
    spans=[]
    for i,(x,y) in enumerate(zip(a,b)):
        if x==y:continue
        if spans and i==spans[-1][1]:spans[-1][1]+=1
        else:spans.append([i,i+1])
    diff={reg:[reference.m.reg(reg),r.m.reg(reg)] for reg in REGS if reference.m.reg(reg)!=r.m.reg(reg)}
    emit(f,{'case':kind,'status':'completed','input_kind':description,
         'checkpoint_sha256':cp['sha256'],'start':before,'end':game(r.m),
         'summary':p.summary(),'calls':dict(inst.calls),'installed':sorted(p.names),
         'records_equal':True,'record_hashes':digests(r.m),'all_memory_equal':a==b,
         'memory_difference_spans':spans,'returned_register_differences':diff,
         'waiting_key_equal':reference.keys.waiting==r.keys.waiting,
         'elapsed_s':round(time.monotonic()-start,4)})
    assert p.summary()['1771:6730']['proved']==1
    assert all(v['before']==0 for v in p.summary().values())


def direct(f):
    test=Draw();test.setUpClass();raw=test.call;n=0
    def capture(target,args=(),**kw):
        nonlocal n
        n+=1;start=time.monotonic()
        row={'case':f'direct-{n:03}','target':target,'args':list(args),
             'input_kind':'declared synthetic direct frame on native E006-r0001',
             'base_state_sha256':IMAGE_SHA,'game_edits':kw.get('game',{}),
             'frame':'real caller returnPC; SS:SP3E00 BP3E80; original locals/arguments',
             'before_mutation':getattr(kw.get('before'),'__name__',None)}
        before=kw.get('before')
        def input_hash(m):
            if before:before(m)
            row['input_memory_before_declared_call_frame_sha256']=sha(m.read(0,MEM_SIZE))
            row['seed_service_entries']=[]
            row['seed_service_returns']=[]
            def entry(replay):
                if not replay:row['seed_service_entries'].append({n:m.reg(n) for n in ('ax','cx','dx','sp','bp','ss','ds')})
            def after(replay):
                if not replay:row['seed_service_returns'].append({'ax':m.reg('ax'),'cx':m.reg('cx'),'dx':m.reg('dx'),
                    'seed_7B62':m.rd(0x7B62),'seed_7B64':m.rd(0x7B64)})
            if target in ('1771:6730','23E4:11D7'):
                m.at('23E4:11D7',entry)
                m.at('1771:67A8',after)
        kw['before']=input_hash
        # Force ALL real library helper implementations in whole initial-year
        # builder cases and reuse exact same complete callee set as route proof.
        if target=='1771:6730':
            variant=None
            for value in kw.get('specs',()):
                if isinstance(value,tuple) and value[0] is stages.PORTS:variant=value[1]
            kw['specs']=specs(variant)
        try:
            m,p=raw(target,args,**kw)
            if row['seed_service_entries']:
                assert len(row['seed_service_entries'])==len(row['seed_service_returns'])==1
                incoming=row['seed_service_entries'][0];saved=row['seed_service_returns'][0]
                assert (incoming['cx'],incoming['dx'])==(saved['seed_7B62'],saved['seed_7B64'])
                assert saved['ax']==(0x2C00|(incoming['ax']&255))
            row.update(status='proved',summary=p.summary(),end=game(m),record_hashes=digests(m),
                       returned=returned(m),elapsed_s=round(time.monotonic()-start,4))
            emit(f,row);return m,p
        except ProofError as exc:
            emit(f,{**row,'status':'falsifier_caught','difference':str(exc),'elapsed_s':round(time.monotonic()-start,4)})
            raise
    test.call=capture
    for name in sorted(v for v in dir(test) if v.startswith('test_')):getattr(test,name)()
    emit(f,{'status':'completed','cases':n})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',required=True,choices=('natural','world','direct'))
    ap.add_argument('--variant');ap.add_argument('--out',required=True);a=ap.parse_args()
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124b2/1','mode':a.mode,'variant':a.variant,'source_hashes':sources(),
                'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'model':'inherited Codex GPT-6 family; exact variant unavailable',
                'limits':'standard T59 per-call dead/scratch; extra final memory/register differences reported explicitly; original rollover remains reference code'})
        if a.mode=='direct':direct(f)
        else:paired(f,a.mode,a.variant)
if __name__=='__main__':main()
