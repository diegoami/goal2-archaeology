"""Public D/#673 source-bound acceptance assertions; optional private input hash verification."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]

def rows(name):return [json.loads(l) for l in (HERE/name).read_text().splitlines()]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--private',action='store_true');a=ap.parse_args()
    index=json.loads((HERE/'acceptance/index.json').read_text())
    for group in ('sources','receipts'):
        for name,h in index[group].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    natural=rows('natural-inputs-v1.jsonl');assert natural[-1]['status']=='completed'
    phases=('playoffs','groups','last16','quarters','semis','finals','qualifying')
    assert [v['phase'] for v in natural if v.get('status')=='constructed']==list(phases)
    for phase in phases:
        v=rows(f'natural-{phase}-v1.jsonl')[-1]
        assert v['status']=='completed' and v['all_memory_equal'] and v['records_equal'] and v['waiting_key_equal']
        assert not v['memory_difference_spans'] and not v['returned_register_differences']
        assert v['reference_matches_prepared_tail'] and all(s['before']==0 for s in v['summary'].values())
        if phase=='qualifying':assert len(v['draws'])==160 and v['end']['year_word']==2
    direct=rows('direct-v1.jsonl');assert direct[-1]=={'cases':19,'status':'completed'}
    assert sum(v.get('status')=='proved' for v in direct)==16
    assert sum(v.get('status')=='falsifier_caught' for v in direct)==3
    for site,n in (('1771:71D1',8),('1771:71E0',2),('1771:720D',4)):
        assert {d['value'] for v in direct for d in v.get('draws',[]) if d['return']==site and 'value'in d}==set(range(1,n+1))
    for name in ('natural-host-mutant-v1.jsonl','natural-third-mutant-v1.jsonl','controlled-mark-mutant-v1.jsonl'):
        assert rows(name)[-1]['status']=='falsifier_caught'
    controlled=rows('controlled-playoffs-v1.jsonl');paired=next(v for v in controlled if v['status']=='paired-playoffs')
    assert paired['all_memory_equal'] and paired['records_equal'] and not paired['returned_register_differences']
    assert controlled[-1]['status']=='completed' and '000E:706E' in controlled[-1]['outer_finalizer_visits']
    corrected=rows('corrected-synthetic-v1.jsonl');assert corrected[-1]['status']=='completed' and corrected[-1]['fixtures']==1040
    for v in corrected:
        if v.get('status')=='corrected-phase':assert any(x['return']=='000E:706E' for x in v['finalizer_visits'])
    validity=json.loads((HERE/'world-validity-final.json').read_text());assert len(validity['checks'])==3
    assert all(v['original85F7_idempotent'] and v['aggregate_leg_relationships'] for v in validity['checks'])
    assert 'Ran 45 tests' in (HERE/'focused-final.log').read_text() and (HERE/'focused-final.log').read_text().rstrip().endswith('OK')
    assert 'FAILED (errors=12)' in (HERE/'exact-final-tests-before/unit.log').read_text()
    assert json.loads((HERE/'static-call-audit-final.json').read_text())['static_call_sites']==27
    assert sum(json.loads((HERE/'instruction-counts.json').read_text()).values())==661
    assert json.loads((HERE/'preserved-functions.json').read_text())['old_functions_unchanged']==31
    if a.private:
        checked=set()
        def walk(v):
            if isinstance(v,dict):
                if 'path'in v and 'sha256'in v and 'context'in v:
                    p=ROOT/v['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'];assert len(v['context']['regs'])==16;checked.add(v['path'])
                for x in v.values():walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(natural);walk(corrected);walk(controlled)
        print('Private checkpoints:',len(checked),'full-memory hashes and16CPU/key contexts PASS')
    print('T124d/#673 acceptance PASS: source/receipt hashes,661instructions/27calls,31oldfunctions,45tests/exactoldfailure,seven natural tails/fullmemory/16regs/records,realworld8->2qualifying,finalized24aggregate sets,corrected8757lineage,19directcases and requiredmutants')
if __name__=='__main__':main()
