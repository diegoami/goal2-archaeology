"""Behavioral red observations of the UNCHANGED original route, before T123.

Actual original execution, not a missing-name check. Reference bytes/checkpoints
stay private. The existing route advances annual boundaries and starts Unicorn;
these contradict the new sealed boundary/denial contracts.
"""
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE,REGS,GuestError
spec=importlib.util.spec_from_file_location('_t123_red_dprepare',HERE.parent/'T124d/prepare.py');D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
sha=D.sha

def emit(f,v):f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno());print(v.get('status',v.get('schema')),flush=True)
def load(cp):return D.load(cp)
def checkpoint(r,label):
    data=r.header+r.m.read(0,MEM_SIZE)+r.tail;digest=sha(data);p=ROOT/'.cache/t123'/f'{label}-{digest[:16]}.mem';p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():p.write_bytes(data)
    assert sha(p.read_bytes())==digest
    return {'path':str(p.relative_to(ROOT)),'sha256':digest,'context':D.context(r)}

def continental():
    receipt=HERE.parent/'T124t/continuation-context.jsonl'
    cp=next(r['checkpoint'] for r in map(json.loads,receipt.read_text().splitlines()) if r.get('status')=='round' and r['round']==3)
    r=load(cp);assert D.game(r.m)['stage']==4 and D.game(r.m)['rounds']==1
    r.m.at('000E:70E6',lambda replay:None if replay else r.m.stop('t123-red-terminal'))
    for n in range(64):
        try:r.call()
        except GuestError:
            if r.m.stop_reason!='t123-red-terminal':raise
            break
    else:raise AssertionError('continental final boundary not reached')
    assert D.game(r.m)['cursor']==D.game(r.m)['count']
    return checkpoint(r,'continental-original-terminal'),{'source':cp,'source_receipt_sha256':sha(receipt.read_bytes()),'original_calls':n+1}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);opts=ap.parse_args();c,cs=continental()
    receipt=HERE.parent/'T124d/natural-inputs-v1.jsonl';w=next(r['before_stage_end']['checkpoint'] for r in map(json.loads,receipt.read_text().splitlines()) if r.get('status')=='constructor-entry' and r['phase']=='qualifying')
    assert w['sha256']=='9ef48afa7657be0284ca6cf0142f0488a7046c09972d7cf430ca5cb8523033f1'
    with Path(opts.out).open('x') as f:
        emit(f,{'schema':'t123-behavior-before/1','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'source_hashes':{p:sha((ROOT/p).read_bytes()) for p in ['runtime/original_match/route.py','runtime/original_match/port/route.py',str(Path(__file__).relative_to(ROOT))]},
          'scope':'actual legacy route behavioral red, not production/sealed pass; original bytes stay private'})
        for case,cp,lineage in [('continental',c,cs),('world',w,{'source_receipt_sha256':sha(receipt.read_bytes())})]:
            r=load(cp);before=D.game(r.m);memory=sha(r.m.read(0,MEM_SIZE));start=time.monotonic();r.call();after=D.game(r.m)
            assert before['stage'] in (4,8) and before['rounds']==1 and before['cursor']==before['count']
            changed=after['stage']!=before['stage'] or after['rounds']!=before['rounds'] or after['year_word']!=before['year_word']
            assert changed and memory!=sha(r.m.read(0,MEM_SIZE))
            emit(f,{'status':'behavioral-red-confirmed','case':case,'expected_contract':'deferred boundary before any fresh route/kit writes',
              'actual_legacy_advances':True,'before':before,'after':after,'input':cp,'lineage':lineage,'elapsed_s':round(time.monotonic()-start,4)})
        data=(ROOT/c['path']).read_bytes()
        from original_match import machine
        with patch.object(machine,'Uc',side_effect=RuntimeError('T123 positive backend-start denial')):
            try:R.Route(Image(data),entry='play_round',record_writes=False)
            except RuntimeError as exc:assert 'positive backend-start denial' in str(exc)
            else:raise AssertionError('legacy route did not require the denied original backend')
        emit(f,{'status':'behavioral-red-confirmed','case':'no-Unicorn-start','actual_legacy_requires_backend_start':True,'positive_denial_active':True})
if __name__=='__main__':main()
