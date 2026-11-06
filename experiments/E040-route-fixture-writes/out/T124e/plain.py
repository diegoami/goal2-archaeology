"""Bounded fully ported60CB, no original instructions/fallback, versus original.

The original actual-entry context and key policy are identical. Full original
code stays inert data on PortMachine; all reached entries must be real ports.
Ordered byte writes outside the dedicated caller-dead stack are compared.
"""
import argparse
import json
import sys
import time
from pathlib import Path
from unittest.mock import patch
import proof as P
from original_match import route as R,port
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS
from original_match.port.engine import PortMachine
from original_match.port import Registry


def specs():
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for e in reg.entries.values():
            if not e.stub and e.address not in ('214B:0723','214B:08DD'):sub._add(e)
        if sub.entries:result.append((sub,None))
    return result


def load(cp,plain):
    data=(P.ROOT/cp['path']).read_bytes();assert P.sha(data)==cp['sha256']
    if plain:
        with patch.object(R,'Machine',PortMachine):r=R.Route(Image(data),entry='play_round',record_writes=False)
        port.install(r.m,specs())
    else:r=R.Route(Image(data),entry='play_round',record_writes=False)
    P.D.restore(r,cp['context']);return r


def run(cp,plain,phase):
    r=load(cp,plain);m=r.m;events=[];minimum=[m.reg('sp')]
    def writes(a,size,value):
        minimum[0]=min(minimum[0],m.reg('sp'))
        events.extend((a+i,(value>>(8*i))&255) for i in range(size))
    m.on_write(0,MEM_SIZE-1,writes)
    pages=P.pages(r,phase+('-plain' if plain else '-original'),True)
    assert m.run(m.lin('000E:7152'),120,fresh=True) is None
    return r,pages,events,minimum[0]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
    rows=list(map(json.loads,Path(a.input).read_text().splitlines()));cp=rows[-1]['checkpoint'];start=time.monotonic()
    with Path(a.out).open('x') as f:
        P.emit(f,{'schema':'t124e-fully-ported/1','phase':a.phase,'source_hashes':{**P.sources(),str(Path(__file__).relative_to(P.ROOT)):P.sha(Path(__file__).read_bytes())},'input_sha256':cp['sha256'],
                  'mechanism':'PortMachine: no opcode runner/Unicorn/original fallback; real ports including009C+0644; actualRoute key services preempt0723/08DD as in reference'})
        ref,rp,rw,rs=run(cp,False,a.phase);r,pp,pw,ps=run(cp,True,a.phase)
        end=cp['context']['regs']['ESP']&65535;ss=cp['context']['regs']['SS']*16
        low=min(rs,ps);dead=(ss+low,ss+end)
        keep=lambda events:[v for v in events if not dead[0]<=v[0]<dead[1]]
        original=ref.m.read(0,MEM_SIZE);candidate=r.m.read(0,MEM_SIZE)
        spans=[]
        for i,(x,y) in enumerate(zip(original,candidate)):
            if x==y or dead[0]<=i<dead[1]:continue
            if spans and i==spans[-1][1]:spans[-1][1]+=1
            else:spans.append([i,i+1])
        strip=lambda xs:[{k:v for k,v in x.items() if k!='private_capture'} for x in xs]
        regs={n:[ref.m.reg(n),r.m.reg(n)] for n in REGS if ref.m.reg(n)!=r.m.reg(n)}
        P.emit(f,{'status':'completed','phase':a.phase,'pages_equal':strip(pp)==strip(rp),'pages':pp,'reference_pages':rp,
          'ordered_live_byte_writes_equal':keep(rw)==keep(pw),'reference_live_byte_writes':len(keep(rw)),'candidate_live_byte_writes':len(keep(pw)),
          'dead_stack_linear':list(dead),'memory_difference_spans_outside_dead_stack':spans,'register_differences':regs,
          'records_equal':ref.record==r.record,'waiting_key_equal':ref.keys.waiting==r.keys.waiting,'elapsed_s':round(time.monotonic()-start,4)})
        assert not spans and keep(rw)==keep(pw) and strip(pp)==strip(rp) and ref.record==r.record and ref.keys.waiting==r.keys.waiting
        # StandardT59 scratch remains measured, never promoted to strict equality.
        assert not(set(regs)-{'EBX','ECX','ESI','EDI','ES','EFLAGS'}),regs
if __name__=='__main__':main()
