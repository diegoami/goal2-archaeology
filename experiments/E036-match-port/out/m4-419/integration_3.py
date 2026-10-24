"""Separate unhooked display references, then display/all on two pinned sources."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import heavy_slot
heavy_slot.take('m4-419-integration',weight=1)
import family,families,image_sources,records,compare
addresses=['1771:'+a for a in ('958D','883F','89C1','89FE','8A5D','8CCF','8D84','9028','91CE','937C','9509','5C94','5CCB')]
results=[]
for name,cache in [('FS',ROOT/'.cache/dl'),('G13',ROOT/'.cache/m4-419')]:
 spec=families.load_family(OUT/'source-specs-1'/f'{name}.json').matches[0]
 image=image_sources.load(spec.image,cache);reference=None
 for mode,ports in [('reference',()),('display',('display',)),('all',('all',))]:
  start=time.time();rec=family.run_match(image,spec,counts=addresses,ports=ports,display_profile=True,time_limit=6000,stretch_limit=600)
  path=OUT/f'{name}-{mode}-3.jsonl'
  with path.open('x') as f:f.write(records.dumps(rec)+'\n')
  records.validate(rec)
  if mode=='reference':reference=rec
  diffs=compare.differences(reference,rec,no_screen=True,strict_display=True)
  result={'id':spec.id,'mode':mode,'score':rec['score'],'error':rec['error'],'completed':records.is_completed(rec),'differences':diffs,'seconds':time.time()-start,'record_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'counts':rec['counts'],'port_calls':rec.get('port_calls',{})}
  results.append(result);print(json.dumps(result),flush=True)
with (OUT/'integration-3.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
assert all(r['completed'] and not r['differences'] for r in results),results
