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
from original_match.machine import Machine,MEM_SIZE,REGS
from original_match.port.engine import PortMachine
from original_match.port import Registry,PortError


def specs():
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for e in reg.entries.values():
            if not e.stub:sub._add(e)
        if sub.entries:result.append((sub,None))
    return result


class RouteKeys:
    """Existing Route.Keys policy/state through the real menu ports' key API.

    Only the original service boundary is adapted: same answers, record rows,
    DS key-byte writes and AL; port returns implement the ABI. No new policy.
    """
    def __init__(self,r):self.r=r
    def keypressed(self,site):
        r=self.r;has,source=r.keys.poll(site,r)
        r.record.append(('key',site,'poll',r.keys.waiting if has else None,source))
        return has
    def key(self,site):
        r=self.r;key,source=r.keys.read(site,r)
        r.record.append(('key',site,'read',key,source))
        r._write("08DD's key (0947 DS:A976, 097C DS:A977)",r.m.DS*16+R.KEY,bytes([key,key]))
        r.m.set_reg('ax',(r.m.reg('ax')&0xFF00)|key)
        return key


def pushed_entry(r,replay):
    if r.m.rd(R.PUSHED_BACK,1):
        r.record.append(('key',r._site(),'read',r.m.rd(R.KEY,1),'pushed-back'))


def load(cp,plain,pushed=False):
    data=(P.ROOT/cp['path']).read_bytes();assert P.sha(data)==cp['sha256']
    if plain:
        # Suppress duplicate Route return_from handlers ONLY on this arm; the
        # actual menu ports consume the same existing policy through RouteKeys.
        with patch.object(R,'Machine',PortMachine),patch.object(R.Route,'_on_poll',lambda r,replay:None),patch.object(R.Route,'_on_read',pushed_entry):
            r=R.Route(Image(data),entry='play_round',record_writes=False)
        r.t124e_inst=port.install(r.m,specs(),keys=RouteKeys(r))
        assert type(r.m) is PortMachine and not hasattr(r.m,'_uc')
    else:r=R.Route(Image(data),entry='play_round',record_writes=False)
    P.D.restore(r,cp['context'])
    if pushed:r.m.wr(R.PUSHED_BACK,1,1);r.m.wr(R.KEY,0x50,1)
    return r


def run(cp,plain,phase,pushed=False):
    r=load(cp,plain,pushed);m=r.m;events=[];minimum=[m.reg('sp')]
    def writes(a,size,value):
        minimum[0]=min(minimum[0],m.reg('sp'))
        events.extend((a+i,(value>>(8*i))&255) for i in range(size))
    m.on_write(0,MEM_SIZE-1,writes)
    pages=P.pages(r,phase+('-pushed' if pushed else '')+('-plain' if plain else '-original'),True)
    if plain:
        with patch.object(Machine,'run',side_effect=AssertionError('opcode/original fallback')),patch.object(Image,'from_savestate',side_effect=AssertionError('original savestate fallback')):
            assert m.run(m.lin('000E:7152'),120,fresh=True) is None
    else:assert m.run(m.lin('000E:7152'),120,fresh=True) is None
    return r,pages,events,minimum[0]


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--phase',required=True);ap.add_argument('--out',required=True);ap.add_argument('--pushed-back',action='store_true');a=ap.parse_args()
    rows=list(map(json.loads,Path(a.input).read_text().splitlines()));cp=rows[-1]['checkpoint'];start=time.monotonic()
    with Path(a.out).open('x') as f:
        P.emit(f,{'schema':'t124e-fully-ported/1','phase':a.phase,'source_hashes':{**P.sources(),str(Path(__file__).relative_to(P.ROOT)):P.sha(Path(__file__).read_bytes())},'input_sha256':cp['sha256'],
                  'mechanism':'raw Image of supplied actual-entry memory, no sealed-state/table claim; PortMachine all real ports including009C+0644+0723+08DD; SAME Route.Keys policy through real-port adapter; no original opcode/savestate fallback',
                  'pushed_back_control':a.pushed_back})
        ref,rp,rw,rs=run(cp,False,a.phase,a.pushed_back);r,pp,pw,ps=run(cp,True,a.phase,a.pushed_back)
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
        # Positive controls bind the normalization to this exact observed own
        # below-entry-SP interval, excluding return words and live caller args.
        def differences(x,y):return [i for i,(a,b) in enumerate(zip(x,y)) if a!=b and not dead[0]<=i<dead[1]]
        controls={}
        for name,address,expected in [('below_dead',dead[0]-1,True),('inside_low',dead[0],False),
             ('inside_high',dead[1]-1,False),('return_word',dead[1],True),
             ('caller_country_argument',dead[1]+4,True),('rng_7B62',r.m.DS*16+0x7B62,True),('rng_8336',r.m.DS*16+0x8336,True)]:
            changed=bytearray(candidate);changed[address]^=1
            caught=bool(differences(original,changed));assert caught==expected
            controls[name]={'linear':address,'caught':caught,'expected':expected}
        controls['ordered_live_write_drop']=keep(rw)!=keep(pw)[1:];assert controls['ordered_live_write_drop']
        guard=load(cp,True);guard.m.set_reg('cs',guard.m.seg(0xE));guard.m.set_reg('eip',0x7152)
        try:guard.m.run(guard.m.lin('000E:77C2'),1,fresh=True)
        except PortError as exc:assert 'no registered port/return' in str(exc);backend_guard=str(exc)
        else:raise AssertionError('unregistered original instruction executed')
        calls={k:v for k,v in r.t124e_inst.calls.items() if v}
        assert calls['214B:009C']>0 and calls['23E4:0644']>0
        P.emit(f,{'status':'completed' ,'phase':a.phase,'pages_equal':strip(pp)==strip(rp),'pages':pp,'reference_pages':rp,
          'ordered_live_byte_writes_equal':keep(rw)==keep(pw),'reference_live_byte_writes':len(keep(rw)),'candidate_live_byte_writes':len(keep(pw)),
          'dead_stack_linear':list(dead),'memory_difference_spans_outside_dead_stack':spans,'register_differences':regs,
          'records_equal':ref.record==r.record,'reached_real_ports':calls,'normalization_controls':controls,
          'unregistered_original_guard':backend_guard,'backend_no_uc':not hasattr(r.m,'_uc'),
          'ordered_record_sha256':P.sha(json.dumps(P.D.public(r.record),sort_keys=True).encode()),'waiting_key_equal':ref.keys.waiting==r.keys.waiting,'elapsed_s':round(time.monotonic()-start,4)})
        assert not spans and keep(rw)==keep(pw) and strip(pp)==strip(rp) and ref.record==r.record and ref.keys.waiting==r.keys.waiting
        # StandardT59 scratch remains measured, never promoted to strict equality.
        assert not(set(regs)-{'EBX','ECX','ESI','EDI','ES','EFLAGS'}),regs
if __name__=='__main__':main()
