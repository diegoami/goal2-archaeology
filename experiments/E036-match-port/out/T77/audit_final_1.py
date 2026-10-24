"""Final acceptance from frozen source, strict records and immutable receipts."""
from pathlib import Path
import collections,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,records
BASE='186f08cfc9f4ff5f30089b7662ff911a59e16032'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads((OUT/p).read_text())
expected={k:v for f in families.discover().values() for k,v in f.expected().items()};assert len(expected)==74
raw={}
for f in families.discover().values():raw.update(compare.load(ROOT/f.reference))
native={**compare.load(OUT/'native-1/own.jsonl'),**compare.load(ROOT/families.discover()['R'].reference)}
own=compare.load(OUT/'own-2/own.jsonl')
folder=OUT/sys.argv[1];integrated_path=folder/'all-actions-1.jsonl';integrated=compare.load(integrated_path)
results={}
for label,reference,candidate,screen in [('native',raw,native,False),('own',raw,own,False),('integrated',None,integrated,True)]:
 profile=compare.candidate_display_profile(candidate,screen)
 if screen:
  assert profile is not None and profile['mask']==[]
  reference=compare.load(ROOT/profile['reference'])
 lines,ok=compare.check(reference,candidate,expected,no_screen=screen,image_sha256=families.image_sha256(),strict_display=screen)
 assert ok,lines
 results[label]={'matches':len(candidate),'strict_display':screen,'sha256':sha(integrated_path if screen else OUT/'own-2/own.jsonl') if label!='native' else None}
entries=[r['entry'] for r in read('listing-inventory-1.json')];assert len(entries)==17
triples=[];totals=collections.Counter()
for mid in expected:
 for entry in entries:
  n=native[mid]['counts'][entry];totals[entry]+=n
  for mode,candidate in [('own',own),('integrated',integrated)]:
   physical=candidate[mid]['counts'][entry];calls=candidate[mid]['port_calls'][entry]
   assert n==physical==calls,(mode,mid,entry,n,physical,calls)
   triples.append({'mode':mode,'match':mid,'entry':entry,'native':n,'physical':physical,'python_calls':calls})
assert [entry for entry in entries if totals[entry]==0]==['0791:C24D']
assert all(len(r['ports'])==21 and 'quick' in r['ports'] and 'rare' in r['ports'] and r['mask']==[] and not r.get('variant') for r in integrated.values())
assert read('own-2/source-before.json')==read('own-2/source-after.json')
for path,digest in read('own-2/source-before.json').items():assert sha(ROOT/path)==digest,path
binding=read('all-actions-dispatch-source-1.json')
assert binding['head']=='f90dada50cf2d0b2f65b3da5e75a26f5053a79e4'
for path,digest in binding['sources'].items():
 assert sha(ROOT/path)==digest,path
 assert hashlib.sha256(subprocess.check_output(['git','show',binding['head']+':'+path],cwd=ROOT)).hexdigest()==digest,path
for file in ('family.py','families.py','compare.py','records.py'):
 path='experiments/E036-match-port/'+file;assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT),path
validation=read('validation-final-1/results.json');assert validation=={'owned-unit':0,'check':0,'annotations':0,'full-suite':0}
source=read('validation-final-1/source.json')['sources'];assert source==read('validation-final-1/source-after.json')
for path,digest in source.items():assert sha(ROOT/path)==digest,path
skips=read('skip-inventory-final-1.json');assert skips['fixed_baseline']==BASE and skips['actual_final_tests']==2065 and len(skips['inherited_skips'])==16 and not skips['T77_skips']
controls=read('controls-2/summary.json');assert controls['baseline']==BASE and len(controls['results'])==12 and all(r['caught'] for r in controls['results'])
for path,digest in controls['sources'].items():assert sha(ROOT/path)==digest,path
falsifiers=[]
for name in ('trial','energy','stats'):
 path=OUT/f'mutant-{name}-1.jsonl';candidate=compare.load(path);assert len(candidate)==1 and all(compare.completed(r) is None for r in candidate.values())
 lines,ok=compare.check(raw,candidate,{mid:expected[mid] for mid in candidate},expect='differ',image_sha256=families.image_sha256());assert ok,lines
 falsifiers.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'completed_caught':True})
witness=compare.load(OUT/'variant-native-1.jsonl')['S/quick-1']['counts'];assert all(witness[e]>0 for e in ('0791:B261','0791:DAC1','0791:D805'))
search=read('bounded-search-summary-final-1.json');assert search['completed_executions']==258 and search['keeper_entry_count']==0
reproduction=read('generation-reproduction-1.json')
for path,digest in reproduction['reproduced_byte_identical'].items():assert sha(ROOT/path)==digest,path
reference_audit=read('main-reference-extension-audit-1.json');assert reference_audit['baseline']==BASE and reference_audit['old_specs_preserved']==64 and reference_audit['R_display_independently_recorded'] and reference_audit['mask']==[]
for path,digest in reference_audit['sha256'].items():assert sha(ROOT/path)==digest,path
assert (OUT/'static-after-regeneration-1.exit').read_text().strip()=='0'
receipt={'milestone':{'exact_on_both_ALL74_modes':16,'READ':['0791:C24D']},'fixed_baseline':BASE,'modes':results,'mask':[],'triples':triples,'entry_call_checks_total':len(triples),'original_call_totals':dict(totals),'falsifiers':falsifiers,'original_falsifier_branch_counts':witness,'validation':validation,'tests':2065,'inherited_skips':16,'bounded_search_completed_executions':258,'dispatch_head':binding['head'],'dispatch_inputs_match_current_source':True,'generator_reproduced':True,'immutable_reference_audit':'main-reference-extension-audit-1.json'}
(OUT/'acceptance-audit-final-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS:16 exact,1 READ;74 matches in each mode;2516 triples;2065 tests/16 inherited skips;three reached caught falsifiers')
