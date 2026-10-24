"""Reconcile native0723 entry counts with T67's already accepted inlinewalkoff service."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'experiments/E036-match-port'),str(ROOT/'runtime')]
import compare,families
oldpath=ROOT/'experiments/E036-match-port/out/T67/coverage-unported-39873774715/coverage-unported.jsonl'
newpath=OUT/'coverage-unhooked-1.jsonl'
candpath=OUT/'all-actions-final-1-40074025808/all-actions-final-1.jsonl'
old=compare.load(oldpath);new=compare.load(newpath);candidate=compare.load(candpath)
spec={m.id:m.sha256 for f in families.discover().values() for m in f.matches if m.id in old}
assert len(old)==62
lines,ok=compare.check(new,old,spec,image_sha256=families.image_sha256())
assert ok,lines[-5:]
rows=[]
for mid,row in candidate.items():
    count=row['counts']['214B:0723'];calls=row['port_calls']['214B:0723'];native=new[mid]['counts']['214B:0723']
    assert count==calls
    if mid in old:
        inline=old[mid]['counts']['0791:78F1']
    else:
        assert mid=='S/no-managed-side' and row['port_calls']['0791:7881']==0
        inline=0
    assert count+inline==native,(mid,count,inline,native)
    rows.append({'id':mid,'counted_entry':count,'python_entry_calls':calls,'unhooked_entry':native,
                 'archived_native_walkoff_poll_site_count':inline,'reconciled':True})
report={'native_old62_full_fields':lines[-1],'matches':63,'nonzero_inline_matches':sum(r['archived_native_walkoff_poll_site_count']>0 for r in rows),
        'explanation':'Existing T67 calls mem.keypressed directly in7881 inner22-slot loop;78F1 precedes native78F4call. Logical service polls match the original while entry counters correctly count only actual entry calls.',
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (oldpath,newpath,candpath,ROOT/'runtime/original_match/port/restarts.py')},'rows':rows}
(OUT/'inline-poll-reconciliation-1.json').open('x').write(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
