"""T124c constructor/tail differential proofs on actual natural caller frames.

Private input preparation ran original play_round from213/CP1/CP2 until the
real6B55/6E59 entry, with no edited stage/group/result. Each arm resumes that
same original frame through constructor, original76B1 return and play_round77C2.
No managed match is replayed by the differential arms; its fresh original
preparation provenance, decisions and checkpoints are retained separately.
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
from collections import Counter

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
from original_match import port
from original_match.port import Registry,stages
from original_match.port.prove import Prover,ProofError
from original_match.machine import MEM_SIZE,REGS
from tests.test_port_stage_continental import Continental,host_seed_six
from tests.test_port_stages import IMAGE_SHA
import prepare as P
sha=P.sha;game=P.game


def sources():
    paths=['runtime/original_match/port/stages.py','runtime/original_match/port/runtime.py',
       'runtime/original_match/port/entrypoints.py','runtime/original_match/port/attributes.py',
       'runtime/original_match/port/update.py','runtime/original_match/port/display.py',
       'runtime/original_match/port/_display_finals.py','runtime/original_match/port/prove.py',
       'runtime/original_match/route.py','runtime/original_match/route_team.py','runtime/original_match/match.py',
       'tests/test_port_stage_continental.py',str(Path(__file__).relative_to(ROOT)),
       str((HERE/'prepare.py').relative_to(ROOT))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def emit(f,value):
    f.write(json.dumps(value,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:value[k] for k in ('case','status','elapsed_s') if k in value}),flush=True)


def specs(variant=None):
    wanted=set(stages.PORTS.entries)-{'1771:8208','1771:76B1'}
    wanted|={'214B:0018','214B:003C','214B:007B','214B:06B1','1771:0B77','1771:10E7','1771:5C94','1771:5CCB'}
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for a,e in reg.entries.items():
            if a in wanted:assert not e.stub;sub._add(e)
        if sub.entries:
            sub.variants=dict(reg.variants);result.append((sub,variant if reg.name=='stages' else None))
    assert {a for reg,_ in result for a in reg.entries}==wanted
    return result


def observe_draws(m):
    trace=[];sites={'1771:6B7E':8,'1771:6BBB':4}
    def entry(replay):
        if replay:return
        stack=m.reg('ss')*16+m.reg('sp');ret=m.where(m.word_at(stack+2),m.word_at(stack))
        if ret in sites:trace.append({'return':ret,'bound':m.word_at(stack+4),'seed_before':m.rd(0x7B62)})
    m.at('214B:06B1',entry)
    for site in sites:
        def returned(replay,site=site):
            if not replay:
                assert trace and trace[-1]['return']==site and 'value' not in trace[-1]
                trace[-1].update(value=m.reg('ax'),seed_after=m.rd(0x7B62))
        m.at(site,returned)
    return trace


def digests(m):
    return {name:sha(m.read(m.far(ptr),n)) for name,ptr,n in (
        ('countries129',0xA917,191*129),('players3061',0xA91B,20*3061),('manager_region',0xA91F,768),
        ('group_tables',0xA933,0x1C00),('game',0xA923,128),('fixture_lists129',0xA92F,0x48*129),
        ('fixture_region',0xA92B,8*game(m)['count']))}


def natural(f,case,prepared,variant):
    records=[json.loads(l) for l in prepared.read_text().splitlines()];last=records[-1]
    assert last['status']=='builder-entry' and last['case']==case
    cp=last['checkpoint'];golden=last['expected_post_tail_golden']
    start=time.monotonic();reference=P.load(cp);before=game(reference.m)
    reference_draws=observe_draws(reference.m)
    assert reference.m.run(reference.m.lin('000E:77C2'),300,fresh=True) is None
    assert reference.m.reg('sp')==0x3EEE
    original=reference.m.read(0,MEM_SIZE)
    original_component=reference.header+original+reference.tail
    golden_data=(ROOT/golden['path']).read_bytes();assert sha(golden_data)==golden['sha256']
    reference_golden_equal=original_component==golden_data
    r=P.load(cp);draws=observe_draws(r.m);inst=port.install(r.m,specs(variant));p=Prover(r.m,inst)
    try:assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
    except ProofError as exc:
        emit(f,{'case':case,'status':'falsifier_caught','variant':variant,'difference':str(exc),
                'input_sha256':cp['sha256'],'summary':p.summary(),'elapsed_s':round(time.monotonic()-start,4)})
        if not variant:raise
        return
    assert not variant,'uncaught mutant'
    assert r.m.reg('sp')==0x3EEE
    assert digests(r.m)==digests(reference.m)
    assert r.record==reference.record
    assert draws==reference_draws
    memory=r.m.read(0,MEM_SIZE);spans=[]
    for i,(x,y) in enumerate(zip(original,memory)):
        if x==y:continue
        if spans and i==spans[-1][1]:spans[-1][1]+=1
        else:spans.append([i,i+1])
    regs={n:[reference.m.reg(n),r.m.reg(n)] for n in REGS if reference.m.reg(n)!=r.m.reg(n)}
    target=last['target'];assert p.summary()[target]['proved']==1
    if case=='groups':assert Counter(v['return'] for v in draws)=={'1771:6B7E':4,'1771:6BBB':32}
    else:assert not draws
    emit(f,{'case':case,'status':'completed','scope':'natural original constructor-entry frame through actualplay_roundreturn77C2',
         'preparation_receipt_sha256':sha(prepared.read_bytes()),'input_sha256':cp['sha256'],
         'start':before,'end':game(r.m),'summary':p.summary(),'calls':dict(inst.calls),'draws':draws,
         'records_equal':True,'ordered_record_sha256':sha(json.dumps(P.public_record(r.record),sort_keys=True).encode()),
         'record_hashes':digests(r.m),'all_memory_equal':memory==original,'memory_difference_spans':spans,
         'returned_register_differences':regs,'waiting_key_equal':r.keys.waiting==reference.keys.waiting,
         'reference_post_tail_golden':golden['sha256'],'reference_equals_T124t_golden':reference_golden_equal,
         'reference_component_sha256':sha(original_component),'elapsed_s':round(time.monotonic()-start,4)})
    assert all(v['before']==0 for v in p.summary().values())


def direct(f):
    test=Continental();test.setUpClass();raw=test.call;n=0
    def capture(target,args=(),**kw):
        nonlocal n
        n+=1;start=time.monotonic();row={'case':f'direct-{n:03}','target':target,'args':list(args),
            'input_kind':'declared synthetic valid native-country/group/completed-semifinal frame',
            'base_state_sha256':IMAGE_SHA,'game_edits':kw.get('game',{}),
            'frame':'real caller returnPC; SS:SP3E00 BP3E80; constructor has no arguments',
            'before_mutation':getattr(kw.get('before'),'__name__',None)}
        before=kw.get('before');traces=[]
        def prepare(m):
            if before:before(m)
            row['input_memory_before_declared_call_frame_sha256']=sha(m.read(0,MEM_SIZE))
            row['input_seed_word']=m.word_at(m.far(0xA978))
            traces.extend([observe_draws(m)])
        kw['before']=prepare
        # All real direct and indirect helper implementations, including selected06B1/inline0688.
        variant=None
        for value in kw.get('specs',()):
            if isinstance(value,tuple) and value[0] is stages.PORTS:variant=value[1]
        kw['specs']=specs(variant)
        try:
            m,p=raw(target,args,**kw)
            emit(f,{**row,'status':'proved','summary':p.summary(),'end':game(m),'record_hashes':digests(m),
                    'draws':traces[0],'elapsed_s':round(time.monotonic()-start,4)})
            return m,p
        except ProofError as exc:
            emit(f,{**row,'status':'falsifier_caught','difference':str(exc),'draws':traces[0],
                    'elapsed_s':round(time.monotonic()-start,4)})
            raise
    test.call=capture
    for name in sorted(v for v in dir(test) if v.startswith('test_')):getattr(test,name)()
    # Derived controlled input words target each possible FIRST original host
    # draw, using the inverse of the confirmed odd LCG multiplier (F004). The
    # real06B1 still executes and its result is compared against the original.
    inverse=pow(0x7ABD,-1,65536)
    for wanted in range(1,9):
        seed=(((wanted-1)*8192+4096-0x1B0F)*inverse)&65535
        def seed_word(m,seed=seed):m.write(m.far(0xA978),seed.to_bytes(2,'little'))
        m,p=capture('1771:6B55',specs=test.specs(),game={0x3C:3,0x3D:1,0x40:0},before=seed_word)
        assert m.word_at(m.far(0xA923)+0x2E)==m.word_at(m.far(0xA933)+0x1C0+wanted*0x38-0x1F8)
    emit(f,{'status':'completed','cases':n})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=('groups','semis','finals','direct'),required=True)
    ap.add_argument('--prepared');ap.add_argument('--variant');ap.add_argument('--out',required=True);a=ap.parse_args()
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124c/1','case':a.case,'variant':a.variant,'source_hashes':sources(),
                'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                'model':'inherited Codex GPT-6 family; exact variant unavailable',
                'limits':'standardT59 dead/scratch; extra fullmemory/16regs only when measured; original ageing/rollover reference only'})
        if a.case=='direct':direct(f)
        else:natural(f,a.case,Path(a.prepared),a.variant)
if __name__=='__main__':main()
