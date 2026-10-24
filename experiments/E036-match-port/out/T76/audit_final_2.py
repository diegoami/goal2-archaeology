"""Bind the completed T76 checks to current source and immutable producers."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,records,family
from original_match import port
from original_match.port import takers
DISPATCH='27b339421e4dda084eeb044c9e1aecdacbe0a831'
RUN='40084230548';BASE='411fdefa0287f984e5c0efc1fb1c585263c67690'
folder=OUT/f'all-actions-1-{RUN}'
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected={mid:d for f in families.discover().values() for mid,d in f.expected().items()}
assert len(expected)==64
profile=family.read_display_profile();assert profile['mask']==[]
assert profile['reference'].endswith('reference-all-set-piece-20261024-v2.jsonl')
reference=compare.load(ROOT/profile['reference']);candidate=compare.load(folder/'all-actions-1.jsonl')
lines,ok=compare.check(reference,candidate,expected,no_screen=True,strict_display=True,image_sha256=families.image_sha256())
assert ok,lines
native=compare.load(OUT/'native-1/own.jsonl')
triples=[]
for mid in expected:
 assert candidate[mid]['ports']==port.available(),(mid,candidate[mid]['ports'])
 assert candidate[mid]['mask']==[]
 for address in sorted(takers.PORTS.entries):
  a=native[mid]['counts'][address];b=candidate[mid]['counts'][address];c=candidate[mid]['port_calls'][address]
  assert a==b==c,(mid,address,a,b,c)
  triples.append({'match':mid,'address':address,'native':a,'candidate_entries':b,'python_calls':c})
manifest=read(folder/'manifest.json')
assert manifest['run_id']==RUN and manifest['sha']==DISPATCH
inputs=manifest['inputs']
for k,v in {'task':'T76','name':'all-actions-1','family':'ALL','ports':'all','shards':'32','time_limit':'6000','stretch_limit':'600'}.items():
 assert inputs[k]==v,(k,inputs.get(k))
assert not inputs.get('only') and not inputs.get('variant')
assert set(inputs['count'].split(','))==set(takers.PORTS.entries)|{'0791:CFAF','0791:9B0F','0791:9E5B'}
dispatch_hashes={}
for p in sorted((ROOT/'runtime/original_match').rglob('*.py')):
 rel=str(p.relative_to(ROOT));raw=subprocess.check_output(['git','show',DISPATCH+':'+rel],cwd=ROOT)
 assert hashlib.sha256(raw).hexdigest()==digest(p),rel
 dispatch_hashes[rel]=digest(p)
validation=OUT/'validation-final-1';source=read(validation/'source.json')
assert source['slot_acquired'] is True
assert source['sources']==read(validation/'source-after.json')
assert all(digest(ROOT/p)==d for p,d in source['sources'].items())
assert read(validation/'results.json')=={'owned-unit':0,'check':0,'annotations':0,'full-suite':0}
owned=(validation/'owned-unit.log').read_text();suite=(validation/'full-suite.log').read_text()
assert re.search(r'Ran 45 tests in [0-9.]+s\s+OK',owned)
match=re.search(r'Ran (\d+) tests in ([0-9.]+)s\s+OK \(skipped=(\d+)\)',suite)
skip_inventory=read(OUT/'skip-inventory-final-1.json')
assert skip_inventory['fixed_baseline']==BASE and skip_inventory['T76_new_skips']==[]
assert skip_inventory['baseline_T85_source_unchanged'] is True
assert match and int(match[1])==skip_inventory['expected_current_tests']==2043
assert int(match[3])==len(skip_inventory['expected_current_skips'])==16
controls=read(OUT/'controls-2/summary.json');assert controls['baseline']==BASE
assert len(controls['results'])==14 and all(r['caught'] for r in controls['results'])
assert all(digest(ROOT/p)==d for p,d in controls['sources'].items())
citations=read(OUT/'citation-endpoints-final-main-1.json')
assert citations['valid_endpoints_verified']==200 and citations['inherited_problem_strings_preserved']==18
assert all(digest(ROOT/p)==d for p,d in citations['sha256'].items())
assert (OUT/'static-after-regeneration-1.exit').read_text().strip()=='0'
raw_old=OUT.parent.parent/'families/S-no-managed-side-reference-20261024-v1.jsonl'
raw_new=ROOT/families.discover()['S'].reference
display_old=OUT.parent.parent/'families/display/reference-all-20261024-v1.jsonl'
assert raw_new.read_bytes().startswith(raw_old.read_bytes())
assert (ROOT/profile['reference']).read_bytes().startswith(display_old.read_bytes())
assert {r['id']:r['spec_sha256'] for r in records.read_log(raw_old)}=={k:v for k,v in expected.items() if k!='S/set-piece-taker'}
observations=[read(OUT/f'{mode}-taker-observations-1.json') for mode in ('original','ported')]
assert observations[0]['observations']==observations[1]['observations']
for d in observations:
 for row in d['observations']:
  assert row['requested']==row['returned']==row['event_player']==row['stored']!=row['current']
local=read(OUT/'local-audit-1.json');assert len(local['entry_call_triples'])==640
assert len(local['falsifiers'])==3 and all(x['caught'] and x['completed'] and x['original_reach']>0 for x in local['falsifiers'].values())
receipt={'milestone':{'ported_exact':10},'matches_each_mode':64,'mask':[],
         'integrated_profile':profile,'integrated_sha256':digest(folder/'all-actions-1.jsonl'),
         'own_sha256':digest(OUT/'own-1/own.jsonl'),'native_sha256':digest(OUT/'native-1/own.jsonl'),
         'entry_call_checks_total':1280,'integrated_entry_call_triples':triples,'dispatch':DISPATCH,
         'dispatch_runtime_hashes':dispatch_hashes,'fixed_baseline':BASE,'unit_controls_caught':14,
         'full_suite':{'tests':int(match[1]),'seconds':float(match[2]),'skips':int(match[3])},
         'source_bound_validation':True,'source_bound_static':True,'old63_prefixes_and_specs_preserved':True,
         'chosen_taker_observations':observations[0]['observations'],'falsifiers':local['falsifiers']}
(OUT/'acceptance-audit-final-2.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('integrated_entry_call_triples','dispatch_runtime_hashes')},indent=2))
