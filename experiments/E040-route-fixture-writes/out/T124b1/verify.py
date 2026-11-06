"""Verify the final source-bound acceptance index, without original guest bytes."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
index=json.loads((HERE/'acceptance/index.json').read_text())
for group in ('sources','receipts'):
    for path,expected in index[group].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
for p in ('natural-final.jsonl','world-proof-v2.jsonl'):
    rows=[json.loads(l) for l in (HERE/p).read_text().splitlines()]
    value=next(v for v in rows if v.get('case')=='natural-seven-helpers') if p.startswith('natural') else rows[-1]
    assert value['records_equal'] and value['waiting_key_equal']
    assert not value['memory_difference_spans'] and not value['returned_register_differences']
    assert all(v['before']==0 for v in value['summary'].values())
    assert value['summary']['1771:63A4']['proved']==1
synthetic=[json.loads(l) for l in (HERE/'synthetic-final.jsonl').read_text().splitlines()]
assert synthetic[-1]=={'status':'completed','cases':27}
assert sum(v.get('status')=='proved' for v in synthetic)==25
assert sum(v.get('status')=='falsifier_caught' for v in synthetic)==2
for p in ('natural-mutant-bonus-v3.jsonl','natural-mutant-score-v3.jsonl'):
    assert [json.loads(l) for l in (HERE/p).read_text().splitlines()][-1]['status']=='falsifier_caught'
world=[json.loads(l) for l in (HERE/'world-prepare-v4.jsonl').read_text().splitlines()]
steps=[v for v in world if v.get('status')=='prepared-step']
assert len(steps)==7 and sum(len(v['silent_updates']['fixtures']) for v in steps)==1040
assert world[-1]['status']=='prepared'
assert world[-1]['world_knockout_start']==2385 and world[-1]['final_fixture']==2400
assert 'Ran 23 tests' in (HERE/'focused-final.log').read_text()
assert (HERE/'focused-final.log').read_text().rstrip().endswith('OK')
assert json.loads((HERE/'static-call-audit-final.json').read_text())['static_call_sites']==28
print('T124b1 acceptance index: source and receipt hashes, natural/world equality, 27 synthetic calls, mutants, 1040 original preparation results, focused tests and 28 calls PASS')
