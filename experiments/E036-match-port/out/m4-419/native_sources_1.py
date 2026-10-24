"""Unhooked originals first; source-specific hashes, no guest edits or projection copies."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import heavy_slot
heavy_slot.take('m4-419-native-sources',weight=1)
import family,families,image_sources,records
addresses=['1771:'+a for a in ('958D','883F','89C1','89FE','8A5D','8CCF','8D84','9028','91CE','937C','9509','5C94','5CCB')]
results=[]
for name,cache in [('FS',ROOT/'.cache/dl'),('G13',ROOT/'.cache/m4-419')]:
 spec=families.load_family(OUT/'source-specs-1'/f'{name}.json').matches[0]
 image=image_sources.load(spec.image,cache)
 start=time.time();rec=family.run_match(image,spec,counts=addresses,time_limit=600,stretch_limit=120)
 with (OUT/f'{name}-native-raw-1.jsonl').open('x') as f:f.write(records.canonical(rec)+'\n')
 results.append({'id':spec.id,'source':spec.image,'source_sha256':spec.image_sha256,'source_memory_sha256':image.sha256(),'record_sha256':hashlib.sha256((OUT/f'{name}-native-raw-1.jsonl').read_bytes()).hexdigest(),'score':rec['score'],'error':rec['error'],'completed':rec['error'] is None and rec['stopped_at_board'],'seconds':time.time()-start,'counts':rec['counts']})
 print(json.dumps(results[-1]),flush=True)
with (OUT/'native-source-feasibility-1.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
assert all(r['completed'] for r in results),results
