"""Independently compare ALL74 and every physical-entry/Python-call count."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families
from original_match.port import quick,rare
expected={mid:d for fam in families.discover().values() for mid,d in fam.expected().items()}
reference={}
for fam in families.discover().values():reference.update(compare.load(ROOT/fam.reference))
native={**compare.load(OUT/'native-1/own.jsonl'),**compare.load(ROOT/families.discover()['R'].reference)}
own=compare.load(OUT/'own-2/own.jsonl')
receipt={'checks':{},'triples':[]}
for label,records in [('original',native),('own-2',own)]:
 lines,ok=compare.check(reference,records,expected,image_sha256=families.image_sha256());assert ok,lines
 receipt['checks'][label]={'exact_matches':len(records),'full_fields_and_screens':True}
before=json.loads((OUT/'own-2/source-before.json').read_text());after=json.loads((OUT/'own-2/source-after.json').read_text())
assert before==after
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in after.items())
entries=sorted(set(quick.PORTS.entries)|set(rare.PORTS.entries));assert len(entries)==17
for mid in expected:
 assert own[mid]['ports']==['quick','rare'],own[mid]['ports']
 for address in entries:
  a=native[mid]['counts'][address];b=own[mid]['counts'][address];c=own[mid]['port_calls'][address]
  assert a==b==c,(mid,address,a,b,c)
  receipt['triples'].append({'match':mid,'entry':address,'native':a,'physical_entries':b,'python_calls':c})
receipt['totals']={a:sum(row['python_calls'] for row in receipt['triples'] if row['entry']==a) for a in entries}
assert [a for a in entries if receipt['totals'][a]==0]==['0791:C24D']
receipt['frozen_sources_current']=True
receipt['checks']['own-2']['sha256']=hashlib.sha256((OUT/'own-2/own.jsonl').read_bytes()).hexdigest()
branches={'trial':('S/quick-1','0791:B261'),'energy':('S/quick-1','0791:DAC1'),'stats':('S/quick-1','0791:D805')}
witness=compare.load(OUT/'variant-native-1.jsonl')
receipt['falsifiers']={}
for label,(mid,branch) in branches.items():
 candidate=compare.load(OUT/f'mutant-{label}-1.jsonl')
 assert len(candidate)==1
 assert set(candidate)=={mid}
 lines,ok=compare.check(reference,witness,{mid:expected[mid]},image_sha256=families.image_sha256());assert ok,lines
 assert witness[mid]['counts'][branch]>0
 lines,ok=compare.check(reference,candidate,{mid:expected[mid]},expect='differ',image_sha256=families.image_sha256());assert ok,lines
 assert compare.completed(candidate[mid]) is None
 # The unhooked witness's exact branch count is separately retained before mutants.
 binding=json.loads((OUT/'early-source-binding-1.json').read_text())
 assert binding['original_witness_counts'][branch]==witness[mid]['counts'][branch]
 assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in binding['runtime_unchanged_since'].items())
 receipt['falsifiers'][label]={'match':mid,'completed':True,'caught':True,'original_branch':branch,'original_reach':binding['original_witness_counts'][branch]}
controls=json.loads((OUT/'controls-2/summary.json').read_text())
assert controls['baseline']=='186f08cfc9f4ff5f30089b7662ff911a59e16032'
assert len(controls['results'])==12 and all(r['caught'] and r['returncode'] for r in controls['results'])
receipt['controls_caught']=len(controls['results'])
(OUT/'main-local-proof-audit-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='triples'},indent=2))
