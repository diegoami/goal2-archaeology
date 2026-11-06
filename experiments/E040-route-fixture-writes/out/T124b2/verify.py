"""Verify source/receipt hashes and final B2 acceptance assertions, no original bytes needed."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
index=json.loads((HERE/'acceptance/index.json').read_text())
for key in ('sources','receipts'):
    for name,expected in index[key].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,name
for name in ('natural-draws-v3.jsonl','world-draws-v3.jsonl'):
    rows=[json.loads(l) for l in (HERE/name).read_text().splitlines()];v=rows[-1]
    assert v['status']=='completed' and v['records_equal'] and v['all_memory_equal'] and v['waiting_key_equal']
    assert not v['memory_difference_spans'] and not v['returned_register_differences']
    assert v['summary']['1771:6730']['proved']==1
    assert all(s['before']==0 for s in v['summary'].values())
    assert v['draw_site_counts']=={'1771:680D':64,'1771:682C':64,'1771:68E2':32}
    assert len(v['draws'])==160
    for site,n in (('1771:680D',8),('1771:682C',8),('1771:68E2',4)):
        assert {r['value'] for r in v['draws'] if r['return']==site}==set(range(1,n+1))
rows=[json.loads(l) for l in (HERE/'direct-draws-v3.jsonl').read_text().splitlines()]
assert rows[-1]=={'cases':16,'status':'completed'}
assert sum(r.get('status')=='proved' for r in rows)==14
assert sum(r.get('status')=='falsifier_caught' for r in rows)==2
seed=[r for r in rows if r.get('status')=='proved' and r.get('seed_service_entries')]
assert len(seed)==5
for r in seed:
    incoming=r['seed_service_entries'][0];saved=r['seed_service_returns'][0]
    assert (incoming['cx'],incoming['dx'])==(saved['seed_7B62'],saved['seed_7B64'])
    assert saved['ax']==0x2C00|(incoming['ax']&255)
for name in ('natural-mutant-draw-final.jsonl','natural-mutant-group-final.jsonl'):
    assert [json.loads(l) for l in (HERE/name).read_text().splitlines()][-1]['status']=='falsifier_caught'
assert 'Ran 30 tests' in (HERE/'focused-final.log').read_text()
assert (HERE/'focused-final.log').read_text().rstrip().endswith('OK')
assert 'FAILED (errors=17)' in (HERE/'exact-final-tests-before/unit.log').read_text()
assert json.loads((HERE/'static-call-audit-final.json').read_text())['static_call_sites']==17
print('T124b2 acceptance PASS: source/receipt hashes,17calls,30focused tests,exact old failure,natural/world full equality,160ordered draws/allchoices,16directcalls,seedCX/DX/AH and required mutants')
