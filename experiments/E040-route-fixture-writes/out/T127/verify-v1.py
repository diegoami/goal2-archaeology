"""Verify immutable final-source T127 receipts only; never collects/runs an engine."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
binding=json.loads((HERE/'accepted-default-binding-v1.json').read_text())
baseline=json.loads((HERE/binding['baseline_receipt']).read_text())
assert sha(HERE/binding['baseline_receipt'])==binding['baseline_receipt_sha256']
assert sha(HERE/binding['producer'])==binding['producer_sha256']==baseline['script_sha256']
assert baseline['accepted_source']=='c6a5e1134cf7b9e3796fb9a3c48b1d3ac59b6af4'
assert baseline['accepted_match_sha256']=='e949159c9cc77f4d195bc9b150c67dfd913ba447417375122bc58db1bca97f92'
assert baseline['differences']=={'EFLAGS':[70,2]}
assert baseline['raw_private_sha256']==binding['private_pair_sha256']
assert binding['t127_match_sha256']==sha(ROOT/'runtime/original_match/match.py')
checks=('complete_state_equal','events_equal','ordered_draws_equal','news_equal',
        'all16_actual_transfer_equal','other15_returned_equal','entry_configuration_pure',
        'invalid_resume_pure','positive_denials')
current={}
for path in sorted(HERE.glob('proof-*.json')):
 row=json.loads(path.read_text())
 if row.get('schema')!='t127-entry-config/1':continue
 if not all((ROOT/name).is_file() and sha(ROOT/name)==value for name,value in row['sources'].items()):continue
 assert all(row[k] is True for k in checks),path.name
 assert row['update_calls'].count('0791:B7FA')==row['update_calls'].count('1771:8757')==1
 assert row['same_result_except_declared_execution_metadata']==['image_sha256','ports']
 original=row['raw_returned_registers']['original'];port=row['raw_returned_registers']['port']
 assert set(original)==set(port) and len(original)==16
 assert all(original[k]==port[k] for k in original if k!='EFLAGS')
 if row['controlled']:
  assert row['draw_count']>0 and row['request_operations']==[True,False,True] and row['opportunity_accepted']
 else:assert row['accepted_default_within_backend_equal'] and row['request_operations']==[]
 current[row['controlled']]=path.name
assert set(current)=={False,True},'two current-source default/controlled receipts required; no collection fallback'
print('T127 final-source receipts PASS:',current,'; raw EFLAGS retained, no cross-backend flag fidelity claim')
