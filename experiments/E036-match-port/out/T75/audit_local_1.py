"""Strict local acceptance, physical entries/calls, frozen source and OUT census."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families
from original_match.port import selection
specs={s.id:s.sha256 for f in families.discover().values() for s in f.matches}
ref={}
for f in families.discover().values():ref.update(compare.load(ROOT/f.reference))
assert len(specs)==63
native=compare.load(OUT/'native-1/own.jsonl');own=compare.load(OUT/'own-1/own.jsonl')
checks={};lines=[]
for label,candidate in [('native',native),('menus-selection',own)]:
 report,ok=compare.check(ref,candidate,specs,image_sha256=families.image_sha256());assert ok,report
 lines+=report;checks[label]={'matches':len(candidate),'passed':ok,'sha256':hashlib.sha256((OUT/('native-1' if label=='native' else 'own-1')/'own.jsonl').read_bytes()).hexdigest()}
 assert all(r['mask']==[] for r in candidate.values())
receipts={}
for folder in ('diagnostics-3','own-1','native-1'):
 receipt=json.loads((OUT/folder/'source.json').read_text());mismatch=[]
 for p,digest in receipt['sources'].items():
  if p.startswith('runtime/original_match/') and hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=digest:mismatch.append(p)
 assert not mismatch,(folder,mismatch)
 receipts[folder]={'matches_current_runtime':True,'head':receipt['head']}
ported=sorted(selection.PORTS.entries);out=[r['address'] for r in json.loads((OUT/'static-inventory-1.json').read_text()) if r['classification']=='OUT']
pairs=[]
for mid in specs:
 for address in ported:
  n=native[mid]['counts'][address];entry=own[mid]['counts'][address];calls=own[mid]['port_calls'][address]
  assert n==entry==calls,(mid,address,n,entry,calls)
  pairs.append({'match':mid,'address':address,'native':n,'candidate_entries':entry,'python_calls':calls})
 for address in out:assert native[mid]['counts'][address]==own[mid]['counts'][address]==0,(mid,address)
assert all(any(r['address']==a and r['native']>0 for r in pairs) for a in ported)
controls=json.loads((OUT/'controls-5/summary.json').read_text());assert controls['baseline']=='bf650a337794ffd82e8e1471d45bfb6c5b753fd4';assert len(controls['results'])==24 and all(c['caught'] for c in controls['results'])
for p,digest in controls['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,(p,'control source changed')
mutants=[]
branches={'request-not-set':('0791:E6A9','0791:E44F'),'form-not-swapped':('0791:E20B','0791:E022'),'keeper-check-inverted':('0791:EB89','0791:EA09')}
for variant,(branch,owner) in branches.items():
 cand=compare.load(OUT/'diagnostics-3'/(variant+'.jsonl'));expected={mid:specs[mid] for mid in cand}
 report,ok=compare.check(ref,cand,expected,expect='differ',image_sha256=families.image_sha256());assert ok,report;lines+=report
 for mid,r in cand.items():
  assert native[mid]['counts'][branch]>0 and r['port_calls'][owner]>0
  assert r['variant']=='selection.'+variant
  mutants.append({'variant':variant,'match':mid,'native_branch':branch,'native_branch_count':native[mid]['counts'][branch],'mutant_owner':owner,'mutant_calls':r['port_calls'][owner]})
(OUT/'local-audit-1.log').write_text('\n'.join(lines)+'\n')
(OUT/'local-audit-1.json').write_text(json.dumps({'checks':checks,'sources':receipts,'milestone':{'ported_exact':9,'OUT':9},'entry_call_pairs':pairs,'OUT_zero_pairs':len(specs)*len(out),'controls_caught':24,'mutants':mutants},indent=2)+'\n')
print('ALL63native/own exact;567entry/call triples;567OUTzero pairs;24controls and3mutants caught')
