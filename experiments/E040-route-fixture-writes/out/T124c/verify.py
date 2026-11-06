"""Verify public C acceptance hashes and measured assertions, without original memory bytes."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
index=json.loads((HERE/'acceptance/index.json').read_text())
for group in ('sources','receipts'):
    for name,expected in index[group].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
for case,target,count in (('groups','1771:6B55',1345),('semis','1771:6E59',1353),('finals','1771:6E59',1361)):
    data=[json.loads(l) for l in (HERE/f'{case}-v1.jsonl').read_text().splitlines()];v=data[-1]
    assert v['status']=='completed' and v['summary'][target]['proved']==1
    assert all(s['before']==0 for s in v['summary'].values())
    assert v['all_memory_equal'] and v['records_equal'] and v['waiting_key_equal']
    assert not v['memory_difference_spans'] and not v['returned_register_differences']
    assert v['reference_equals_T124t_golden'] and v['reference_component_sha256']==v['reference_post_tail_golden']
    assert v['end']['count']==count
    prep=[json.loads(l) for l in (HERE/f'natural-{case}-input-v1.jsonl').read_text().splitlines()]
    assert prep[-1]['status']=='builder-entry' and prep[-1]['checkpoint']['sha256']==v['input_sha256']
    assert len(prep[-1]['checkpoint']['context']['regs'])==16
    assert len(prep[-1]['before_stage_end']['checkpoint']['context']['regs'])==16
for name in ('natural-mutant-host-v1.jsonl','natural-mutant-third-v1.jsonl'):
    assert [json.loads(l) for l in (HERE/name).read_text().splitlines()][-1]['status']=='falsifier_caught'
rows=[json.loads(l) for l in (HERE/'direct-v1.jsonl').read_text().splitlines()]
assert rows[-1]=={'cases':14,'status':'completed'}
assert sum(v.get('status')=='proved' for v in rows)==12
assert sum(v.get('status')=='falsifier_caught' for v in rows)==2
for site,n in (('1771:6B7E',8),('1771:6BBB',4)):
    assert {d['value'] for v in rows for d in v.get('draws',[]) if d['return']==site and 'value'in d}==set(range(1,n+1))
assert 'Ran 36 tests' in (HERE/'focused-final.log').read_text()
assert (HERE/'focused-final.log').read_text().rstrip().endswith('OK')
assert 'FAILED (errors=7)' in (HERE/'exact-final-tests-before/unit.log').read_text()
assert json.loads((HERE/'static-call-audit-final.json').read_text())['static_call_sites']==15
assert sum(json.loads((HERE/'instruction-counts.json').read_text()).values())==439
assert json.loads((HERE/'preserved-functions.json').read_text())['old_functions_unchanged']==29
print('T124c acceptance PASS: source/receipt hashes,439instructions/15calls,29oldfunctions,36tests/exactoldfailure,three natural tails full equality/T124tgoldens,14directcases/allhost+permutationchoices,requiredmutants and16CPU/key contexts')
