"""Append a current disposition to every immutable round-1 audit row."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
prior=ROOT/'experiments/E036-match-port/out/m4-408/removal-state-audit-2.json'
audit=copy.deepcopy(json.loads(prior.read_text()));reg=port._module_registry('display')
for row in audit['rows']:
 entry=reg.entries[row['address']]
 row['current_disposition']='retained-full-body' if entry.stub is None else 'remaining-bounded-removal'
 if row['address'] in ('1771:1E5A','1771:1E8D'):raise AssertionError('wrong segment')
 if row['address'] in ('214B:1E5A','214B:1E8D'):row['correction_issue']=408
 elif entry.stub is None:row['correction_issue']=419
row_count=sum(r['current_disposition']=='retained-full-body' for r in audit['rows'])
audit.update(prior_audit=str(prior.relative_to(ROOT)),correction_issue=419,original_audit_rows_unchanged_except_added_current_fields=True,current_retained_of_original_31=row_count,current_remaining_removals=31-row_count,display_retained=sum(e.stub is None for e in reg.entries.values()),display_stubs=sum(e.stub is not None for e in reg.entries.values()),scope_warning='Zero counts are sample coverage only. #419 supplies an ordinary-use counterexample and retains twelve bodies; all remaining removals keep the bounded #416 scope. No universal purity or unreachability claim.')
assert (row_count,audit['display_retained'],audit['display_stubs'])==(14,71,17)
with (OUT/'removal-state-audit-3.json').open('x') as f:json.dump(audit,f,indent=2);f.write('\n')
print('31 audit rows;14 corrected retained bodies,17 remaining bounded removals; display71 retained/17 stubs')
