"""Explicit D direct ABI/mutation/host-choice receipts on finalized ORIGINAL-produced inputs."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
from original_match.port import stages
from original_match.port.prove import ProofError
from original_match.machine import MEM_SIZE
from tests.test_port_stage_world import World,host_input
import prove as D
P=D.P


def emit(f,v):
    f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('case','status') if k in v}),flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    test=World();test.setUpClass();raw=test.call;n=0
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124d-direct/1','fixture_kind':test.input_kind,'source_hashes':{
            **D.sources(),str(Path(__file__).relative_to(ROOT)):P.sha(Path(__file__).read_bytes()),
            'tests/test_port_stage_world.py':P.sha((ROOT/'tests/test_port_stage_world.py').read_bytes()),
            str((HERE/'reference.py').relative_to(ROOT)):P.sha((HERE/'reference.py').read_bytes())},
            'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'limits':'declared synthetic direct calls on finalized original-produced group/aggregate/bracket data, not nativecallercontinuations'})
        def capture(target,args=(),**kw):
            nonlocal n
            n+=1;start=time.monotonic();before=kw.get('before');traces=[]
            row={'case':f'direct-{n:03}','target':target,'args':list(args),
                'base_component_sha256':P.sha(test.image.header+bytes(test.image.memory)),
                'before':getattr(before,'__name__',None),'frame':'real caller returnPC; SS:SP3E00 BP3E80; original returnABI'}
            def prepare(m):
                if before:before(m)
                row.update(input_game=P.game(m),input_memory_before_call_frame_sha256=P.sha(m.read(0,MEM_SIZE)),
                    input_seed_word=m.word_at(m.far(0xA978)))
                traces.append(D.observe_draws(m))
            kw['before']=prepare;variant=None
            for value in kw.get('specs',()):
                if isinstance(value,tuple) and value[0] is stages.PORTS:variant=value[1]
            kw['specs']=D.specs(variant)
            try:
                m,p=raw(target,args,**kw)
                emit(f,{**row,'status':'proved','summary':p.summary(),'draws':traces[0],
                    'end':P.game(m),'record_hashes':D.digests(m),'aggregates':P.aggregate_records(m),
                    'elapsed_s':round(time.monotonic()-start,4)})
                return m,p
            except ProofError as exc:
                emit(f,{**row,'status':'falsifier_caught','variant':variant,'difference':str(exc),
                    'draws':traces[0],'elapsed_s':round(time.monotonic()-start,4)})
                raise
        test.call=capture
        for name in sorted(v for v in dir(test) if v.startswith('test_')):getattr(test,name)()
        inverse=pow(0x7ABD,-1,65536)
        for wanted in range(1,9):
            seed=(((wanted-1)*8192+4096-0x1B0F)*inverse)&65535
            def seed_word(m,seed=seed):m.write(m.far(0xA978),seed.to_bytes(2,'little'))
            test.phase_call('1771:71B2','groups',before=seed_word)
        emit(f,{'status':'completed','cases':n})
if __name__=='__main__':main()
