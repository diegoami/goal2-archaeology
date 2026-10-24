"""Independently verify a downloaded Actions ZIP and strict selected-case proof."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,shards
from original_match import port
from original_match.port import quick,rare
number=int(sys.argv[1]);folder=OUT/f'main-actions-sample-{number}'
artifact=json.loads((folder/'artifact-metadata.json').read_text())
assert artifact['workflow_run']['id']==40090586451
assert artifact['workflow_run']['head_sha']=='f90dada50cf2d0b2f65b3da5e75a26f5053a79e4'
assert hashlib.sha256((folder/f'shard-{number}.zip').read_bytes()).hexdigest()==artifact['digest'].removeprefix('sha256:')
candidate=compare.load(folder/f'shard-{number}.jsonl')
plan=next(s for s in shards.plan(shards.selected_ids('ALL'),37) if s['shard']==number)
assert set(candidate)==set(plan['only'].split(','))
declared={mid:d for fam in families.discover().values() for mid,d in fam.expected().items()}
expected={mid:declared[mid] for mid in candidate}
profile=compare.candidate_display_profile(candidate,True);assert profile and profile['mask']==[]
reference=compare.load(ROOT/profile['reference'])
lines,ok=compare.check(reference,candidate,expected,no_screen=True,strict_display=True,image_sha256=families.image_sha256());assert ok,lines
(folder/'compare.log').write_text('\n'.join(lines)+'\n')
native={**compare.load(OUT/'native-1/own.jsonl'),**compare.load(ROOT/families.discover()['R'].reference)}
entries=sorted(set(quick.PORTS.entries)|set(rare.PORTS.entries));checks=0
for mid,c in candidate.items():
 assert c['ports']==port.available(),(mid,c['ports'],port.available())
 for address in entries:
  assert native[mid]['counts'][address]==c['counts'][address]==c['port_calls'][address],(mid,address)
  checks+=1
runlog=(folder/f'shard-{number}-run.txt').read_text()
assert 'HEAD: '+artifact['workflow_run']['head_sha'] in runlog and 'exit 0 finished' in runlog
receipt={'run':40090586451,'head':artifact['workflow_run']['head_sha'],'artifact_id':artifact['id'],'zip_sha256':artifact['digest'].removeprefix('sha256:'),'strict_exact_matches':len(candidate),'matches':list(candidate),'mask':[],'skipped_ds_blocks':[],'native_physical_python_triples':checks,'modules':port.available(),'source_log_valid':True,'sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file() and p.name!='audit.json'}}
(folder/'audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ('sha256','modules')},indent=2))
