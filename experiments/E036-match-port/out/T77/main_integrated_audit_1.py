"""Independent ALL74, collector reconciliation and complete API cost audit."""
import concurrent.futures,datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,shards
from original_match import port
from original_match.port import quick,rare
RUN=40090586451;folder=OUT/f'all-actions-1-{RUN}'
path=folder/'all-actions-1.jsonl';candidate=compare.load(path)
expected={mid:d for fam in families.discover().values() for mid,d in fam.expected().items()}
assert len(expected)==len(candidate)==74 and list(candidate)==shards.selected_ids('ALL')
profile=compare.candidate_display_profile(candidate,True);assert profile and profile['mask']==[]
lines,ok=compare.check(compare.load(ROOT/profile['reference']),candidate,expected,no_screen=True,strict_display=True,image_sha256=families.image_sha256());assert ok,lines
with (OUT/'main-integrated-compare-1.log').open('x') as f:f.write('\n'.join(lines)+'\n')
native={**compare.load(OUT/'native-1/own.jsonl'),**compare.load(ROOT/families.discover()['R'].reference)}
entries=sorted(set(quick.PORTS.entries)|set(rare.PORTS.entries));checks=0
for mid,c in candidate.items():
 assert c['ports']==port.available() and not c.get('variant')
 for address in entries:
  assert native[mid]['counts'][address]==c['counts'][address]==c['port_calls'][address],(mid,address)
  checks+=1
samples={}
for number in (15,28):
 for name in (f'shard-{number}.jsonl',f'shard-{number}-run.txt'):
  a=OUT/f'main-actions-sample-{number}'/name;b=folder/name
  assert a.read_bytes()==b.read_bytes(),name
  samples[name]=hashlib.sha256(b.read_bytes()).hexdigest()
dispatch=json.loads((OUT/'all-actions-dispatch-request-1.json').read_text())
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['run_id']==str(RUN) and manifest['run_attempt']=='1'
assert manifest['sha']=='f90dada50cf2d0b2f65b3da5e75a26f5053a79e4'
assert manifest['inputs']==dispatch['inputs']
def fetch(suffix):
 route=f'repos/diegoami/goal2-archaeology/actions/runs/{RUN}'+suffix
 return json.loads(subprocess.check_output(['gh','api',route],cwd=ROOT,text=True))
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 api=dict(zip(('jobs','timing','run'),pool.map(fetch,('/jobs?per_page=100','/timing',''))))
jobs=api['jobs'];assert len(jobs['jobs'])==jobs['total_count']==39
assert all(j['status']=='completed' and j['conclusion']=='success' for j in jobs['jobs'])
assert api['run']['head_sha']==manifest['sha'] and api['run']['status']=='completed' and api['run']['conclusion']=='success'
seconds=sum((datetime.datetime.fromisoformat(j['completed_at'])-datetime.datetime.fromisoformat(j['started_at'])).total_seconds() for j in jobs['jobs'])
billable=sum(value['total_ms'] for value in api['timing']['billable'].values());assert billable==0
for name,payload in api.items():
 with (OUT/f'main-actions-{name}-final-1.json').open('x') as f:json.dump(payload,f,indent=2);f.write('\n')
receipt={'candidate':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'strict_profile_selected':True,'mask':[],'skipped_ds_blocks':[],'exact_matches':len(candidate),'native_entry_call_triples':checks,'modules':port.available(),'independent_samples_equal_collector':samples,'dispatch_manifest_valid':True,'successful_jobs':39,'actual_runner_seconds':seconds,'actual_runner_minutes':seconds/60,'billable_ms':billable}
with (OUT/'main-integrated-final-audit-1.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('modules','independent_samples_equal_collector')},indent=2))
