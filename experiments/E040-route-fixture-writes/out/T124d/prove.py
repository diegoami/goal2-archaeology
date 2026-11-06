"""Natural D constructor/tail and #673 full-qualifying regression proofs.

Each arm resumes the SAME actual original constructor-entry CPU/frame/key
context from fresh nativeCP4 continuation. No long prefix replay or invented
call. Real registered helpers only; all eight aggregates beyond ordinary
calendarcount are decoded/hashed explicitly. Original rollover remains reference.
"""
import argparse
import hashlib
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
import prepare as P
sha=P.sha;game=P.game


def sources():
    paths=['runtime/original_match/port/stages.py','runtime/original_match/port/runtime.py',
      'runtime/original_match/port/entrypoints.py','runtime/original_match/port/attributes.py',
      'runtime/original_match/port/update.py','runtime/original_match/port/display.py',
      'runtime/original_match/port/_display_finals.py','runtime/original_match/port/prove.py',
      'runtime/original_match/route.py','runtime/original_match/route_team.py','runtime/original_match/match.py',
      str(Path(__file__).relative_to(ROOT)),str((HERE/'prepare.py').relative_to(ROOT))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def emit(f,v):
    f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('phase','status','elapsed_s') if k in v}),flush=True)


def specs(variant=None):
    wanted=set(stages.PORTS.entries)-{'1771:8208','1771:76B1'}
    wanted|={'214B:0018','214B:003C','214B:007B','214B:06B1','23E4:025D','1771:0B77','1771:10E7','1771:5C94','1771:5CCB'}
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for a,e in reg.entries.items():
            if a in wanted:assert not e.stub;sub._add(e)
        if sub.entries:sub.variants=dict(reg.variants);result.append((sub,variant if reg.name=='stages' else None))
    assert {a for reg,_ in result for a in reg.entries}==wanted
    return result


def observe_draws(m):
    trace=[];sites={'1771:71D1':8,'1771:71E0':2,'1771:720D':4,
                   '1771:680D':8,'1771:682C':8,'1771:68E2':4}
    def entry(replay):
        if replay:return
        s=m.reg('ss')*16+m.reg('sp');ret=m.where(m.word_at(s+2),m.word_at(s))
        if ret in sites:trace.append({'return':ret,'bound':m.word_at(s+4),'seed_before':m.rd(0x7B62)})
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
       ('all_fixtures_through_aggregate2408',0xA92B,8*2408))}


def paired(f,phase,prepared,variant):
    rows=[json.loads(l) for l in prepared.read_text().splitlines()]
    entry=next(v for v in rows if v.get('status')=='constructor-entry' and v['phase']==phase)
    after=next(v for v in rows if v.get('status')=='constructed' and v['phase']==phase)
    cp=entry['checkpoint'];start=time.monotonic();ref=P.load(cp);before=game(ref.m)
    refdraws=observe_draws(ref.m)
    assert ref.m.run(ref.m.lin('000E:77C2'),300,fresh=True) is None
    original=ref.m.read(0,MEM_SIZE);component=ref.header+original+ref.tail
    assert sha(component)==after['checkpoint']['sha256'],'fresh original tail differs from prepared original tail'
    r=P.load(cp);draws=observe_draws(r.m);inst=port.install(r.m,specs(variant));p=Prover(r.m,inst)
    try:assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
    except ProofError as exc:
        emit(f,{'phase':phase,'status':'falsifier_caught','variant':variant,'difference':str(exc),
                'input_sha256':cp['sha256'],'summary':p.summary(),'elapsed_s':round(time.monotonic()-start,4)})
        if not variant:raise
        return
    assert not variant,'uncaught mutant'
    assert r.m.reg('sp')==ref.m.reg('sp')==0x3EEE
    assert digests(r.m)==digests(ref.m)
    assert r.record==ref.record and draws==refdraws
    memory=r.m.read(0,MEM_SIZE);spans=[]
    for i,(a,b) in enumerate(zip(original,memory)):
        if a==b:continue
        if spans and i==spans[-1][1]:spans[-1][1]+=1
        else:spans.append([i,i+1])
    regs={n:[ref.m.reg(n),r.m.reg(n)] for n in REGS if ref.m.reg(n)!=r.m.reg(n)}
    target=entry['target'];assert p.summary()[target]['proved']==1
    if phase=='groups':assert Counter(v['return'] for v in draws)=={'1771:71D1':1,'1771:71E0':1,'1771:720D':8}
    elif phase=='qualifying':assert Counter(v['return'] for v in draws)=={'1771:680D':64,'1771:682C':64,'1771:68E2':32}
    else:assert not draws
    emit(f,{'phase':phase,'status':'completed','scope':'actual natural constructor-entry frame throughplay_roundreturn77C2; originalrolloverREFERENCEONLY',
        'input_sha256':cp['sha256'],'preparation_receipt_sha256':sha(prepared.read_bytes()),
        'start':before,'end':game(r.m),'summary':p.summary(),'calls':dict(inst.calls),'draws':draws,
        'all_memory_equal':memory==original,'memory_difference_spans':spans,'returned_register_differences':regs,
        'waiting_key_equal':r.keys.waiting==ref.keys.waiting,'records_equal':True,
        'ordered_record_sha256':sha(json.dumps(P.public(r.record),sort_keys=True).encode()),'record_hashes':digests(r.m),
        'aggregates':P.aggregate_records(r.m),'original_tail_sha256':sha(component),
        'reference_matches_prepared_tail':True,'elapsed_s':round(time.monotonic()-start,4)})
    assert all(v['before']==0 for v in p.summary().values())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=[v[0] for v in P.PHASES],required=True)
    ap.add_argument('--prepared',required=True);ap.add_argument('--variant');ap.add_argument('--out',required=True);a=ap.parse_args()
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124d-natural-proof/1','phase':a.phase,'variant':a.variant,'source_hashes':sources(),
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'model':'inherited Codex GPT-6 family; exact variant unavailable',
            'limits':'standardT59 dead/scratch; strongerfullmemory/16regs onlyasmeasured; naturalprimary, no oldB1v4inputs'})
        paired(f,a.phase,Path(a.prepared),a.variant)
if __name__=='__main__':main()
