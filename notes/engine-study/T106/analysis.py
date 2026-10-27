#!/usr/bin/env python3
"""Audit committed T106 construction, observations and resource accounting; never run the engine."""
import argparse,copy,json,subprocess,sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from check import ROOT,sha,write_new,validate
from construction import image,MEM_SIZE
from runner import Budget

BASE=Path(__file__).resolve().parent


def read(path):return json.loads(path.read_text())


def ref(path):return dict(path=str(path.relative_to(ROOT)),sha256=sha(path.read_bytes()))


@lru_cache(maxsize=None)
def blob(commit,path):return subprocess.check_output(['git','show',commit+':'+path],cwd=ROOT)


def validate_record(item,record,reservation,outcome,digest):
    assert record['completed'] is True and record['process_exit']==0
    assert record['spec']==item['spec'] and record['logical']==item['spec']['logical']
    assert record['input_memory_sha256']==item['input']['memory_sha256']
    assert record['manifest_sha256']==reservation['manifest_sha256']==digest
    assert record['seq']==reservation['seq']==outcome['seq']
    assert record['batch']==reservation['batch']==outcome['batch']
    assert reservation['logical']==record['logical'] and outcome['completed'] is True
    assert not record['native_instruction_attempts'] and record['frames_remaining']==0
    assert record['cpu_s']<=5 and record['active_wall_s']<=10
    if item['spec']['required_prediction'] is not None:
        assert record['observed']==item['spec']['required_prediction']


def record_negatives(item,record,reservation,outcome,digest):
    results={}
    for label in ['completion','input','reservation','prediction']:
        i,r,s,o=map(copy.deepcopy,[item,record,reservation,outcome])
        if label=='completion':r['completed']=False
        elif label=='input':r['input_memory_sha256']='0'*64
        elif label=='reservation':s['logical']='missing'
        else:r['observed']={'invented':True}
        try:validate_record(i,r,s,o,digest)
        except AssertionError:results[label]='rejected'
        else:raise AssertionError('negative escaped: '+label)
    return results


def build(analysis_commit=None):
    commit=analysis_commit or subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip()
    reservations={r['seq']:r for r in Budget().read('reservations')}
    outcomes={r['seq']:r for r in Budget().read('outcomes')}
    actual_budget=Budget().audit();assert not actual_budget['unclosed_invocations'] and not actual_budget['unclosed_batches']
    assert not actual_budget['failed_invocations'] and len(reservations)==len(outcomes)==48
    img=image();initial=bytes(img.memory[:MEM_SIZE]).ljust(MEM_SIZE,b'\0')
    rows=[];all_records=[];all_pairs=[];provenance=[];roles=Counter();negative=None
    for group,task,version in [('launch','T106a',2),('wall','T106b',1)]:
        ledger_path=BASE/f'{task}-v{version}.json';ledger=read(ledger_path);validate(task,ledger)
        folder=BASE/group;manifest_path=folder/'manifest-v1.json';manifest=read(manifest_path);digest=sha(manifest_path.read_bytes())
        matches=[p for p in (folder/'out').glob('*-batch.json') if read(p)['manifest_sha256']==digest]
        assert len(matches)==1;batch_path=matches[0];batch=read(batch_path);assert batch['error'] is None
        comparisons_path=next((folder/'out').glob('*-comparisons.json'));comparison=read(comparisons_path)
        assert comparison['manifest_sha256']==digest
        assert len(batch['records'])==len(manifest['invocations'])=={'launch':12,'wall':36}[group]
        records={}
        for entry in batch['records']:
            p=ROOT/entry['path'];assert sha(p.read_bytes())==entry['sha256'];record=read(p)
            assert record['logical'] not in records;records[record['logical']]=(p,record)
        executions=set()
        for item in manifest['invocations']:
            p,r=records[item['spec']['logical']];s=reservations[r['seq']];o=outcomes[r['seq']]
            validate_record(item,r,s,o,digest);assert o['record_path']==str(p.relative_to(ROOT)) and o['record_sha256']==sha(p.read_bytes())
            assert s['group']==group and s['cpu_reserve_s']==5 and s['wall_reserve_s']==10
            assert r['cpu_s']==o['cpu_s'] and r['active_wall_s']==o['active_wall_s']
            execution=r['execution_commit'];executions.add(execution)
            assert blob(execution,str(manifest_path.relative_to(ROOT)))==manifest_path.read_bytes()
            assert subprocess.run(['git','merge-base','--is-ancestor',manifest['construction_commit'],execution],cwd=ROOT).returncode==0
            memory=bytearray(initial)
            for patch in item['input']['patches']:
                start=patch['linear'];after=bytes.fromhex(patch['after_hex'])
                assert start>=img.DS*16 and start+len(after)<=MEM_SIZE
                assert sha(memory[start:start+len(after)])==patch['before_sha256']
                memory[start:start+len(after)]=after
            assert sha(memory)==item['input']['memory_sha256'] and len(memory)==item['input']['memory_size']
            assert memory[img.load*16:img.DS*16]==initial[img.load*16:img.DS*16]
            all_records.append(dict(**ref(p),seq=r['seq'],role=r['spec']['role'],case=r['spec']['case'],backend=r['spec']['backend']))
            roles[r['spec']['role']]+=1
            if negative is None:negative=record_negatives(item,r,s,o,digest)
        for source,digest_source in manifest['source_sha256'].items():
            assert sha(blob(manifest['construction_commit'],source))==digest_source
            for execution in executions:assert sha(blob(execution,source))==digest_source
        for pair in comparison['comparisons']:
            ro=read(ROOT/pair['original_record']['path']);rp=read(ROOT/pair['port_record']['path'])
            assert ro['spec']['backend']=='original' and rp['spec']['backend']=='port'
            assert pair['memory_equal']==(ro['full_memory_sha256']==rp['full_memory_sha256'])
            assert pair['abi_equal']==(ro['abi_registers']==rp['abi_registers'] and not ((ro['registers']['eflags']^rp['registers']['eflags'])&0x400))
            assert pair['register_differences']==[n for n in ro['registers'] if ro['registers'][n]!=rp['registers'][n]] or set(pair['register_differences'])=={n for n in ro['registers'] if ro['registers'][n]!=rp['registers'][n]}
            assert (pair['memory_diff_count']==0)==pair['memory_equal']
            assert len(pair['memory_diff_first_offsets'])==min(pair['memory_diff_count'],128)
            all_pairs.append(dict(case=pair['case'],slot=pair['slot'],field_equal=ro['observed']==rp['observed'],memory_equal=pair['memory_equal'],abi_equal=pair['abi_equal'],all_registers_equal=ro['registers']==rp['registers'],memory_diff_count=pair['memory_diff_count'],register_differences=pair['register_differences']))
        rows.extend(ledger['cases']);provenance.append(dict(group=group,ledger=ref(ledger_path),manifest=ref(manifest_path),batch=ref(batch_path),comparisons=ref(comparisons_path),construction_commit=manifest['construction_commit'],execution_commits=sorted(executions),source_sha256=manifest['source_sha256'],control_outcomes=ledger['control_outcomes']))
    assert roles==dict(baseline=36,repeat=4,guard=4,mutant=2,**{'no-effect':2})
    assert len(all_pairs)==18 and all(p['field_equal'] and p['abi_equal'] for p in all_pairs)
    assert {r['seq'] for r in all_records}==set(reservations)==set(outcomes)
    assert actual_budget==read(BASE/'wall/out/manifest-v1-260dc6a3659b-batch.json')['budget']
    own=str(Path(__file__).resolve().relative_to(ROOT));sources={own:sha(Path(__file__).read_bytes())}
    for name in ['T106a-v2.json','T106b-v1.json','construction.py','runner.py','check.py']:
        p=BASE/name;sources[str(p.relative_to(ROOT))]=sha(p.read_bytes())
    return dict(task='T106c',analysis_commit=commit,method=__doc__,limits=[
        'Proposed single-call corroboration pending ES-R3;not natural incidence,whole-match fidelity or scoring effect inference.',
        'exact in slice ledgers means full-memory plus declared return ABI equality;all captured register equality is separately reported.',
        'Full memory snapshots contain original bytes and are not published;retained comparisons record hashes,all observed differing offsets(up to128),not their byte values. No new execution in this analysis.',
        'Production sound stub is reached by launch calls;callee-stack residue attribution remains #591. Wall arithmetic flags differ under the declared scratch policy;caller liveness belongs to T109.',
        'Owner deferred T107;no matches,no effect interval or null result. Revised proposal required before spending.',
    ],source_sha256=sources,source_commits={p:commit for p in sources},budget=actual_budget,cases=rows,
        summary=dict(cases=6,ordinary_invocations=36,baseline_pairs=18,field_equal_pairs=sum(p['field_equal'] for p in all_pairs),abi_equal_pairs=sum(p['abi_equal'] for p in all_pairs),memory_equal_pairs=sum(p['memory_equal'] for p in all_pairs),all_registers_equal_pairs=sum(p['all_registers_equal'] for p in all_pairs),complete_memory_and_registers_equal_pairs=sum(p['memory_equal'] and p['all_registers_equal'] for p in all_pairs),roles=dict(roles),failures=[],deviations=['Launch full-memory equality failed;15bytes differ in each of3pairs.','Wall complete-register equality failed;arithmetic EFLAGS differ in each of15pairs.'],remaining_invocations=60-actual_budget['invocations']),
        record_negative_controls=negative,provenance=provenance,records=sorted(all_records,key=lambda r:r['seq']),pair_summary=all_pairs)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
    report_path=BASE/'report-v1.json';ledger_path=BASE/'T106c-v1.json'
    previous=read(report_path) if a.check else None;report=build(previous['analysis_commit'] if previous else None)
    ledger={k:v for k,v in report.items() if k not in ['provenance','records','pair_summary']}
    if a.check:
        assert report==previous and ledger==read(ledger_path)
        validate('T106c',ledger);print('PASS:6cases/36ordinary/48total;construction+source+raw+budget integrity;all disagreements retained;no engine calls')
    else:
        write_new(report_path,report);write_new(ledger_path,ledger);print('wrote immutable integrated report and6case ledger;zero engine calls')


if __name__=='__main__':main()
