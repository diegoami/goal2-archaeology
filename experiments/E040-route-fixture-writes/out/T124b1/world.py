"""Declared synthetic world tournament, prepared with original builders and full silent result updater.

Native CP4 already holds original stage5 draw. We advance only stage/round bytes
at explicit boundaries in bounded synthetic preparation, call original76B1 in
play_round's actual far-call layout, and run every fixture through ORIGINAL6970
in its complete route_fixture parent frame. No fabricated result, group ordering,
manager tag, squad or ranking byte. This is not a natural game continuation: the
original's UI routing for managed matches is deliberately bypassed in preparation.
At the prepared end-of-stage8 boundary, paired original/ported actual play_round
calls exercise world rankings and stage2 construction, with original80DA only.
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
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
from prove import sha,game,digests,emit,public_record,ENTRIES
from original_match import route as R,port
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS
from original_match.match import SS_PARAGRAPH
from original_match.port import stages,Registry
from original_match.port.prove import Prover,ProofError


def source_hashes():
    paths=['runtime/original_match/port/stages.py','runtime/original_match/route.py',
           'runtime/original_match/route_team.py','runtime/original_match/port/prove.py',
           str(Path(__file__).relative_to(ROOT)),str((HERE/'prove.py').relative_to(ROOT))]
    return {p:sha((ROOT/p).read_bytes()) for p in paths}


def word(m,addr,value):m.write(addr,(value&65535).to_bytes(2,'little'))


def context(r):return {'regs':{reg:r.m.reg(reg) for reg in REGS},'waiting_key':r.keys.waiting}


def restore(r,ctx):
    assert set(ctx['regs'])==set(REGS)
    for reg,value in ctx['regs'].items():r.m.set_reg(reg,value)
    r.keys.waiting=ctx['waiting_key']


def checkpoint(r,label):
    data=r.header+r.m.read(0,MEM_SIZE)+r.tail;hash_=sha(data)
    p=ROOT/'.cache/t124b1/world'/f'{label}-{hash_[:16]}.mem'
    p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        with p.open('xb') as out:out.write(data);out.flush();os.fsync(out.fileno())
    assert sha(p.read_bytes())==hash_
    return {'path':str(p.relative_to(ROOT)),'sha256':hash_,'context':context(r)}


def load(cp):
    data=(ROOT/cp['path']).read_bytes();assert sha(data)==cp['sha256']
    r=R.Route(Image(data),entry='play_round',record_writes=False)
    restore(r,cp['context']);return r


def managers(r):
    m=r.m;g=m.far(stages.GAME);c=m.far(stages.COUNTRIES)
    return {'count':m.read(g,1)[0], 'country_tags_sha256':sha(bytes(m.read(c+191*i+46,1)[0] for i in range(129))),
            'managed_squads_sha256':sha(b''.join(m.read(c+191*i,40) for i in range(129) if m.read(c+191*i+46,1)[0]>128))}


def original_call(r,target,ret,sp,bp,args=(),far=False):
    """Original body only; actual caller's far/near frame, original registers outside entry layout preserved."""
    m=r.m;ss=m.seg(SS_PARAGRAPH)
    seg,off=ret.split(':');words=[int(off,16)]+([m.seg(int(seg,16))] if far else [])+list(reversed(args))
    for i,w in enumerate(words):word(m,ss*16+sp+2*i,w)
    seg,off=target.split(':')
    for reg,val in (('ss',ss),('sp',sp),('bp',bp),('ds',m.DS),('es',m.DS),
                    ('cs',m.seg(int(seg,16))),('eip',int(off,16))):m.set_reg(reg,val)
    assert m.run(m.lin(ret),120,fresh=True) is None
    assert m.reg('sp')==sp+2*len(words),(target,m.reg('sp'))


def build(r,stage,rounds):
    m=r.m;g=m.far(stages.GAME);before=game(m)
    m.write(g+0x3C,bytes([stage,rounds]))
    edits=[{'offset':0x3C,'old':before['stage'],'new':stage},
           {'offset':0x3D,'old':before['rounds'],'new':rounds}]
    # play_round BP3EEA, locals8 bytes, call far76B1 at70F4; real return70F9.
    ss=m.seg(SS_PARAGRAPH);word(m,ss*16+0x3EEA,0x3FF6)
    original_call(r,'1771:76B1','000E:70F9',0x3EDE,0x3EEA,far=True)
    return {'before':before,'edits':edits,'reason':'bounded declared synthetic stage/round dispatch; original constructor and all helpers unmodified',
            'after':game(m)}


def simulate_calendar(r):
    m=r.m;g=m.far(stages.GAME);start=m.word_at(g+0x26);end=m.word_at(g+0x28)
    ss=m.seg(SS_PARAGRAPH);parent=0x3EDE
    # Exact route_fixture parent locals/frame (6CA7..6CC1, 7012pushBP/call7013).
    word(m,ss*16+parent,0x3EEA);word(m,ss*16+parent+2,0x70D4)
    word(m,ss*16+parent-0x10,m.rd(stages.GAME));word(m,ss*16+parent-0xE,m.rd(stages.GAME+2))
    word(m,ss*16+parent-6,start);m.write(ss*16+parent-2,b'\0')
    complete=[]
    for index in range(start,end):
        assert m.word_at(g+0x26)==index
        fx=m.far(stages.FIXTURES)+8*(index-1)
        kind=m.read(fx+2,1)[0]
        # Real6970 uses the fixture at the cursor and calls D47E,B7FA,B602,D050,
        # BC5D twice and complete score/table/key page paths; no isolated RNG stub.
        original_call(r,'000E:6970','000E:7016',0x3EC4,parent,(parent,))
        assert m.word_at(g+0x26)==index+1
        assert m.read(fx,1)[0]<254
        complete.append({'fixture':index,'kind':kind,'record_sha256':sha(m.read(fx,8))})
    return {'start':start,'end':end,'fixtures':complete,'update':'original6970 including D47E,B7FA,B602,D050,BC5D and pages',
            'rng_records_sha256':sha(json.dumps(public_record(r.record),sort_keys=True).encode())}


def prepare(out):
    start=time.monotonic();receipt=ROOT/'experiments/E040-route-fixture-writes/out/T124t/continuation-context.jsonl'
    assert sha(receipt.read_bytes())=='5916ab9562dd296c324d92f90dcc2eb643af2861323f6fddcafab404e63bade6'
    cp4=next(json.loads(line)['checkpoint'] for line in receipt.read_text().splitlines()
             if json.loads(line).get('status')=='round' and json.loads(line)['round']==4)
    assert cp4['sha256']=='3eeb9e4b48bfa95b271c6bbef1cd90628d9a91218048530427e6e5588efed890'
    if out.exists():
        previous=[json.loads(line) for line in out.read_text().splitlines()]
        header=previous[0];assert header['source_hashes']==source_hashes()
        steps=[v for v in previous if v.get('status')=='prepared-step'];r=load(steps[-1]['checkpoint']) if steps else load(cp4)
        done=len(steps)
    else:r=load(cp4);done=0
    plan=[('qualifying',None,None),('playoffs',6,1),('world-groups',7,1),
          ('last16',8,4),('quarters',8,3),('semis',8,2),('finals',8,1)]
    with out.open('a' if out.exists() else 'x') as f:
        if not done:emit(f,{'schema':'t124b1-world-prepare/1','input_kind':'declared synthetic original-constructor/result lineage',
            'source_checkpoint':cp4['sha256'],'source_hashes':source_hashes(),
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'limits':'synthetic dispatch edits and bypassed UI routing; no natural full-world-season claim'})
        for index,(label,stage,rounds) in enumerate(plan):
            if index<done:continue
            tags=managers(r);before=game(r.m)
            all_squads_before=sha(b''.join(r.m.read(r.m.far(stages.COUNTRIES)+191*i,40) for i in range(129)))
            constructed=build(r,stage,rounds) if stage else {'before':before,'edits':[],'after':before}
            simulated=simulate_calendar(r)
            assert managers(r)==tags,'preparation changed manager count/tags or managed squad words'
            cp=checkpoint(r,label)
            emit(f,{'status':'prepared-step','step':index,'label':label,'constructor':constructed,
                'silent_updates':simulated,'checkpoint':cp,'record_hashes':digests(r.m),
                'manager_and_squad_invariants':tags,
                'all_squads_before_sha256':all_squads_before,
                'all_squads_after_sha256':sha(b''.join(r.m.read(r.m.far(stages.COUNTRIES)+191*i,40) for i in range(129))),
                'computer_squad_changes':'original A3DE calls B11F/52CC only when0B77 false; managed squads invariant',
                'end':game(r.m),'elapsed_s':round(time.monotonic()-start,4)})
        assert game(r.m)['stage']==8 and game(r.m)['rounds']==1
        assert game(r.m)['cursor']==game(r.m)['count']
        knockout=r.m.word_at(r.m.far(stages.GAME)+0x2A)
        assert game(r.m)['count']==knockout+16
        emit(f,{'status':'prepared','final_checkpoint':cp,'world_knockout_start':knockout,
                'third_place_fixture':knockout+14,'final_fixture':knockout+15})


def prove(prepared,out,variant):
    rows=[json.loads(line) for line in prepared.read_text().splitlines()];last=rows[-1]
    assert last['status']=='prepared';cp=last['final_checkpoint']
    start=time.monotonic();reference=load(cp);reference.round()
    r=load(cp);reg=Registry('stages','T124b1 seven helpers in synthetic world8->2 actualplay_round')
    for a in ENTRIES:reg._add(stages.PORTS.entries[a])
    reg.variants=dict(stages.PORTS.variants);inst=port.install(r.m,[(reg,variant)]);p=Prover(r.m,inst)
    with out.open('x') as f:
        emit(f,{'schema':'t124b1-world-proof/1','input_kind':'declared synthetic world end-of-calendar frame',
            'input_checkpoint_sha256':cp['sha256'],'preparation_sha256':sha(prepared.read_bytes()),
            'source_hashes':source_hashes(),'variant':variant,
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()})
        try:r.round()
        except ProofError as exc:
            emit(f,{'status':'falsifier_caught','difference':str(exc),'summary':p.summary()})
            if not variant:raise
            return
        assert not variant,'uncaught mutant'
        assert digests(r.m)==digests(reference.m)
        assert r.record==reference.record
        a,b=reference.m.read(0,MEM_SIZE),r.m.read(0,MEM_SIZE)
        diffs=[]
        for i,(x,y) in enumerate(zip(a,b)):
            if x==y:continue
            if diffs and i==diffs[-1][1]:diffs[-1][1]+=1
            else:diffs.append([i,i+1])
        regs={reg:[reference.m.reg(reg),r.m.reg(reg)] for reg in REGS if reference.m.reg(reg)!=r.m.reg(reg)}
        emit(f,{'status':'completed','start':game(load(cp).m),'end':game(r.m),'summary':p.summary(),
            'records_equal':True,'record_hashes':digests(r.m),'all_memory_equal':a==b,
            'memory_difference_spans':diffs,'returned_register_differences':regs,
            'waiting_key_equal':reference.keys.waiting==r.keys.waiting,
            'elapsed_s':round(time.monotonic()-start,4)})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepare',action='store_true');ap.add_argument('--prepared')
    ap.add_argument('--variant');ap.add_argument('--out',required=True);a=ap.parse_args()
    if a.prepare:prepare(Path(a.out))
    else:prove(Path(a.prepared),Path(a.out),a.variant)
if __name__=='__main__':main()
