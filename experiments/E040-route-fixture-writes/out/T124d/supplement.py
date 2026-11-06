"""Controlled managed-continent supplement on NEW corrected original-produced inputs.

Starts finalized corrected-synthetic playoff-entry frame. Only explicit consistent
manager-country transfer is applied (to a qualifying runner-up, not a participant).
Paired7090tail proves broad marking/copy order; ORIGINAL arm alone then produces
complete16playoff results and actualouter8757/85F7/group-entry context.
All oldB1v4world phases are excluded; no host scores/ranks/winnerflags.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
from original_match import port
from original_match.machine import MEM_SIZE,REGS,GuestError
from original_match.port.prove import Prover,ProofError
from tests.test_port_stage_world import move_manager
import prove as D

_spec=importlib.util.spec_from_file_location('_t124d_reference_supplement',HERE/'reference.py')
REF=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(REF)
P=D.P


def emit(f,v):
    f.write(json.dumps(v,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({k:v[k] for k in ('status','phase') if k in v}),flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--prepared',required=True);ap.add_argument('--variant')
    ap.add_argument('--out',required=True);a=ap.parse_args()
    records=[json.loads(l) for l in Path(a.prepared).read_text().splitlines()]
    row=next(v for v in records if v.get('status')=='corrected-phase' and v['phase']=='playoffs')
    cp=row['entry'];ref=P.load(cp);r=P.load(cp)
    old=ref.m.read(ref.m.far(0xA91F)+3*129,1)[0]
    selected=move_manager(ref.m,3,1);assert move_manager(r.m,3,1)==selected
    control=REF.save_part({'component':REF.component(ref),'context':P.context(ref)},'controlled-continent3-playoff-entry')
    start=time.monotonic()
    assert ref.m.run(ref.m.lin('000E:77C2'),300,fresh=True) is None
    inst=port.install(r.m,D.specs(a.variant));prover=Prover(r.m,inst)
    with Path(a.out).open('x') as f:
        emit(f,{'schema':'t124d-controlled/1','input_kind':'declared synthetic manager ownership control on finalizedoriginalpipeline',
            'source_receipt_sha256':P.sha(Path(a.prepared).read_bytes()),'source_entry_sha256':cp['sha256'],
            'controlled_input':control,'transfer':{'old_country':old,'new_country':selected[0],'manager':1,'continent':3},
            'variant':a.variant,'code_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'source_hashes':{str(Path(__file__).relative_to(ROOT)):P.sha(Path(__file__).read_bytes()),**D.sources(),
                             str((HERE/'reference.py').relative_to(ROOT)):P.sha((HERE/'reference.py').read_bytes())}})
        try:assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
        except ProofError as exc:
            emit(f,{'status':'falsifier_caught','difference':str(exc),'summary':prover.summary()})
            if not a.variant:raise
            return
        assert not a.variant,'uncaught managedmark mutant'
        assert D.digests(r.m)==D.digests(ref.m) and r.record==ref.record
        memory_equal=r.m.read(0,MEM_SIZE)==ref.m.read(0,MEM_SIZE)
        regs={n:[ref.m.reg(n),r.m.reg(n)] for n in REGS if ref.m.reg(n)!=r.m.reg(n)}
        copies=P.aggregate_records(ref.m)
        for i,v in enumerate(copies):
            assert v['aggregate']['sha256']==v['legs'][0]['sha256']
            assert v['aggregate']['score_or_mark']==(254 if i<4 else 255)
            assert selected[0] not in (v['legs'][0]['side4'],v['legs'][0]['side6'])
        after_cp=REF.save_part({'component':REF.component(ref),'context':P.context(ref)},'controlled-continent3-after-playoffs')
        emit(f,{'status':'paired-playoffs','summary':prover.summary(),'record_hashes':D.digests(r.m),
            'all_memory_equal':memory_equal,'returned_register_differences':regs,'records_equal':True,
            'waiting_key_equal':ref.keys.waiting==r.keys.waiting,'copies':copies,'reference_after':after_cp})
        assert memory_equal and not regs
        # Continue ONLY original reference, without any port. This new lineage
        # explicitly includes actual706E outer finalization of all aggregates.
        simulated=REF.simulate_calendar(ref);visits=[];found=[]
        def finalizer(replay):
            if not replay:
                m=ref.m;s=m.reg('ss')*16+m.reg('sp');visits.append(m.where(m.word_at(s+2),m.word_at(s)))
        def group_entry(replay):
            if not replay:
                found.append(REF.save_part({'component':REF.component(ref),'context':P.context(ref)},'controlled-continent3-groups-entry'))
                ref.m.stop('controlled-groups-entry')
        ref.m.at('1771:8757',finalizer);ref.m.at('1771:71B2',group_entry)
        try:ref.call()
        except GuestError as exc:assert str(exc)=='play_round stopped: controlled-groups-entry' and found
        assert '000E:706E' in visits
        aggregates=P.aggregate_records(ref.m)
        assert all(v['aggregate']['score_or_mark']<254 for v in aggregates)
        emit(f,{'status':'completed','original_complete_playoff_updates':simulated,'outer_finalizer_visits':visits,
            'groups_entry':found[0],'finalized_aggregates':aggregates,'end':P.game(ref.m),
            'elapsed_s':round(time.monotonic()-start,4)})
if __name__=='__main__':main()
