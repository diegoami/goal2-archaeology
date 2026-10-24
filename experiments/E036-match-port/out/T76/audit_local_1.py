"""Closed-schema full-field identity, physical entries and actual Python calls."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families
from original_match.port import takers
expected={mid:d for fam in families.discover().values() for mid,d in fam.expected().items()}
reference={}
for f in families.discover().values():reference.update(compare.load(ROOT/f.reference))
native=compare.load(OUT/'native-1/own.jsonl');own=compare.load(OUT/'own-1/own.jsonl')
receipt={'milestone':{'ported_exact':10},'checks':{},'sources':{},'entry_call_triples':[]}
for label,records in [('native-1',native),('own-1',own)]:
 lines,ok=compare.check(reference,records,expected,image_sha256=families.image_sha256());assert ok,lines
 path=OUT/label/'own.jsonl';receipt['checks'][label]={'matches':len(records),'passed':ok,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 source=json.loads((OUT/label/'source.json').read_text())
 assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in source['sources'].items()),label
 receipt['sources'][label]={'head':source['head'],'current':True}
for mid in expected:
 assert own[mid]['ports']==['takers']
 for address in sorted(takers.PORTS.entries):
  a=native[mid]['counts'][address];b=own[mid]['counts'][address];c=own[mid]['port_calls'][address]
  assert a==b==c,(mid,address,a,b,c)
  receipt['entry_call_triples'].append({'match':mid,'address':address,'native':a,'candidate_entries':b,'python_calls':c})
receipt['totals']={address:sum(row['python_calls'] for row in receipt['entry_call_triples'] if row['address']==address)
                   for address in sorted(takers.PORTS.entries)}
assert all(receipt['totals'].values()),receipt['totals']
branches={'enter-keeps-current':('S/set-piece-taker','0791:CFAF'),
          'extra-time-short':('S/ko-42-sudden-death','0791:9B0F'),
          'order-no-pushback':('S/ko-42-sudden-death','0791:9E5B')}
receipt['falsifiers']={}
for variant,(mid,at) in branches.items():
 candidate=compare.load(OUT/f'mutant-{variant}-1.jsonl')
 lines,ok=compare.check(reference,candidate,{mid:expected[mid]},expect='differ',image_sha256=families.image_sha256())
 assert ok and native[mid]['counts'][at]>0,(variant,lines)
 assert compare.completed(candidate[mid]) is None,variant
 receipt['falsifiers'][variant]={'caught':True,'completed':True,'match':mid,'original_branch':at,
                                'original_reach':native[mid]['counts'][at]}
frozen=json.loads((OUT/'probe-source-4.json').read_text())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest for p,digest in frozen.items())
receipt['falsifier_source_matches_current']=True
(OUT/'local-audit-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'checks':receipt['checks'],'totals':receipt['totals'],'entry_call_triples':len(receipt['entry_call_triples']),
                  'falsifiers':receipt['falsifiers']},indent=2))
