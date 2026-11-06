"""T124b1 immutable synthetic-call and natural play_round continuation receipts.

Static first: named seg1771 part5, raw114B and5EE1..6616 determine frames,
loop order, word wrap, unsigned sorts, signed score clamp and ELSE best ranks.
Differential runs corroborate these transcriptions, including full T59 ordered
live/caller writes and strict returned registers; dead frames and scratch regs
retain T59's declared limits. Original bytes remain in ignored .cache only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from tests.test_port_stage_qualifying import Rankings, ENTRIES, word
from tests.test_port_stages import IMAGE_SHA
from original_match import port, route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE, REGS
from original_match.port import Registry, stages
from original_match.port.prove import Prover, ProofError


def sha(data):
    return hashlib.sha256(data).hexdigest()


def public_record(value):
    if isinstance(value,bytes):return {'bytes_sha256':sha(value),'length':len(value)}
    if isinstance(value,(list,tuple)):return [public_record(v) for v in value]
    if isinstance(value,dict):return {k:public_record(v) for k,v in value.items()}
    return value


def sources():
    paths=['runtime/original_match/port/stages.py','runtime/original_match/route.py',
           'runtime/original_match/route_team.py','runtime/original_match/port/prove.py',
           'tests/test_port_stage_qualifying.py',str(Path(__file__).relative_to(ROOT))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def game(m):
    g=m.far(stages.GAME)
    return {'cursor':m.word_at(g+0x26),'count':m.word_at(g+0x28),
            'stage':m.read(g+0x3C,1)[0],'rounds':m.read(g+0x3D,1)[0],
            'mode':m.read(g+0x40,1)[0],'year_word':m.word_at(g+0x38)}


def digests(m):
    return {key:sha(m.read(m.far(ptr),length)) for key,ptr,length in
            [('countries_all129',stages.COUNTRIES,191*129),('managers_all256',stages.MANAGERS,3*256),
             ('game',stages.GAME,0x80),('group_tables',stages.TABLES,0x1C00),
             ('fixtures_full_calendar',stages.FIXTURES,8*game(m)['count'])]}


def emit(f,v):
    f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('case','status','elapsed_s') if k in v}),flush=True)


def synthetic(f):
    test=Rankings(); test.setUpClass()
    raw=test.call
    n=0
    def capture(target,args=(),**kw):
        nonlocal n
        start=time.monotonic();n+=1
        row={'case':f'synthetic-{n:03}', 'target':target,'args':list(args),
             'game_edits':kw.get('game',{}),
             'input_kind':'declared synthetic direct frame on published E006-r0001',
             'base_state_sha256':IMAGE_SHA,
             'frame':'real caller return PC, SS:SP=3E00, BP=3E80; Pascal link retained',
             'before_mutation':getattr(kw.get('before'),'__name__',None)}
        before=kw.get('before')
        def input_hash(m):
            if before:before(m)
            row['input_memory_before_declared_call_frame_sha256']=sha(m.read(0,MEM_SIZE))
        kw['before']=input_hash
        try:
            m,p=raw(target,args,**kw)
            row.update(status='proved',summary=p.summary(),end=game(m),record_hashes=digests(m),
                       returned={r:m.reg(r) for r in REGS})
            emit(f,{**row,'elapsed_s':round(time.monotonic()-start,4)})
            return m,p
        except ProofError as exc:
            row.update(status='falsifier_caught',difference=str(exc),elapsed_s=round(time.monotonic()-start,4))
            emit(f,row)
            raise
    test.call=capture
    for name in sorted(x for x in dir(test) if x.startswith('test_')):
        getattr(test,name)()
    # Explicit singleton/equal unsigned quicksort and both counters' wrap.
    def sort_equal(m):
        word(m,m.DS*16+0x9B56,0x9BFD);word(m,m.DS*16+0x9B58,m.DS)
        m.write(m.DS*16+0x9BFE,bytes(range(1,9)))
        for c in range(1,9):word(m,m.far(stages.COUNTRIES)+191*c+47,65535)
    for lo,hi in ((1,1),(1,8),(4,5)):
        capture('1771:5EE1',(lo,hi,0x3E80),before=sort_equal)
    # Each managed score extreme and best-rank ELSE branch both exercised. All
    # countries retain native manager associations and valid squads/continents.
    for mode in (0,1):
        for value in (0,1,127,128,255):
            def score_extremes(m,value=value):
                for tag in range(256):m.write(m.far(stages.MANAGERS)+3*tag+2,bytes([value]))
                for c in range(1,129):
                    cp=m.far(stages.COUNTRIES)+191*c
                    m.write(cp+40,bytes([255 if c%2 else 1,255]))
                for manager in range(1,m.read(m.far(stages.GAME),1)[0]+1):
                    m.write(m.far(stages.GAME)+7+manager,bytes([255]))
                    m.write(m.far(stages.GAME)+13+manager,bytes([255]))
            capture('1771:63A4',game={0x40:mode,0x3C:2 if not mode else 5},before=score_extremes)
    emit(f,{'status':'completed','cases':n})


def route_from_checkpoint():
    receipt=ROOT/'experiments/E040-route-fixture-writes/out/T124t/continuation-context.jsonl'
    assert sha(receipt.read_bytes())=='5916ab9562dd296c324d92f90dcc2eb643af2861323f6fddcafab404e63bade6'
    rows=[json.loads(line) for line in receipt.read_text().splitlines()]
    row=next(v for v in rows if v.get('status')=='round' and v['round']==3)
    cp=row['checkpoint'];data=(ROOT/cp['path']).read_bytes()
    assert sha(data)==cp['sha256']=='4c1c7635ecf50d8a1eaed2bcb5fd56e4351f9c320eaacc1a4a013cb01b7190ff'
    r=R.Route(Image(data),entry='play_round',record_writes=False)
    assert set(cp['context']['regs'])==set(REGS)
    for reg,val in cp['context']['regs'].items():r.m.set_reg(reg,val)
    r.keys.waiting=cp['context']['waiting_key']
    assert game(r.m)=={'stage':4,'rounds':1,'mode':0,'cursor':1353,'count':1361,'year_word':0}
    return r,cp


def natural(f,variant=None):
    start=time.monotonic()
    reference,cp=route_from_checkpoint()
    reference.round()
    emit(f,{'case':'natural-original','status':'completed-round','checkpoint_sha256':cp['sha256'],
            'end':game(reference.m),'record_hashes':digests(reference.m),
            'record_sha256':sha(json.dumps(public_record(reference.record),sort_keys=True).encode()),
            'elapsed_s':round(time.monotonic()-start,4)})
    r,cp=route_from_checkpoint()
    reg=Registry('stages','T124b1 seven ranking helpers only, original outer builder')
    for a in ENTRIES:reg._add(stages.PORTS.entries[a])
    reg.variants=dict(stages.PORTS.variants)
    inst=port.install(r.m,[(reg,variant)])
    p=Prover(r.m,inst)
    try:r.round()
    except ProofError as exc:
        emit(f,{'case':'natural-'+str(variant),'status':'falsifier_caught','difference':str(exc),
                'summary':p.summary(),'elapsed_s':round(time.monotonic()-start,4)})
        if not variant:raise
        return
    if variant:raise AssertionError('natural falsifier not caught')
    assert digests(r.m)==digests(reference.m),'full country/manager/calendar/game records differ'
    assert r.record==reference.record,'full ordered route RNG/key/team/match/events differ'
    a,b=reference.m.read(0,MEM_SIZE),r.m.read(0,MEM_SIZE)
    changed=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    # Report every whole-memory difference rather than silently normalizing it.
    spans=[]
    for i in changed:
        if spans and i==spans[-1][1]:spans[-1][1]+=1
        else:spans.append([i,i+1])
    regs_diff={reg:{'original':reference.m.reg(reg),'port':r.m.reg(reg)} for reg in REGS
               if reference.m.reg(reg)!=r.m.reg(reg)}
    emit(f,{'case':'natural-seven-helpers','status':'completed-round',
        'input_kind':'unmodified T124t round3 checkpoint; original final fixtures/year rollover and qualifying builder',
        'checkpoint_sha256':cp['sha256'],'start':{'stage':4,'rounds':1,'cursor':1353,'count':1361,'year_word':0},
        'end':game(r.m),'summary':p.summary(),'calls':dict(inst.calls),
        'records_equal':True,'record_hashes':digests(r.m),
        'memory_sha256':{'original':sha(a),'port':sha(b)},'memory_difference_spans':spans,
        'returned_register_differences':regs_diff,'waiting_key_equal':r.keys.waiting==reference.keys.waiting,
        'elapsed_s':round(time.monotonic()-start,4)})
    assert all(v['before']==0 for v in p.summary().values())
    emit(f,{'status':'completed'})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=('synthetic','natural'),required=True)
    ap.add_argument('--variant');ap.add_argument('--out',required=True);a=ap.parse_args()
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124b1/1','mode':a.mode,'variant':a.variant,
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'source_hashes':sources(),
            'normalization':'standard T59 per-call dead frames and scratch registers only; full natural record hashes separately compared',
            'model':'inherited Codex GPT-6 family, exact variant unavailable'})
        if a.mode=='synthetic':synthetic(f)
        else:natural(f,a.variant)

if __name__=='__main__':main()
