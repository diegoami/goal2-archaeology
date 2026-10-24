"""Fresh all-module finals runs with the CLI's expanded module-name metadata."""
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]

def run_source(name):
 import family,families,image_sources,records,compare
 from original_match import port
 spec=families.load_family(OUT/'source-specs-1'/f'{name}.json').matches[0]
 image=image_sources.load(spec.image,ROOT/('.cache/dl' if name=='FS' else '.cache/m4-419'))
 names=port.spec_names(port.load(['all']));assert len(names)==21 and 'display' in names
 addresses=['1771:'+a for a in ('958D','883F','89C1','89FE','8A5D','8CCF','8D84','9028','91CE','937C','9509','5C94','5CCB')]
 start=time.time();rec=family.run_match(image,spec,ports=names,display_profile=True,counts=addresses,time_limit=6000,stretch_limit=600)
 path=OUT/f'{name}-all-4.jsonl'
 with path.open('x') as f:f.write(records.dumps(rec)+'\n')
 candidate=compare.load(path);reference=compare.load(OUT/f'{name}-reference-3.jsonl')
 lines,ok=compare.check(reference,candidate,{spec.id:spec.sha256},no_screen=True,strict_display=True,image_sha256={spec.id:spec.image_sha256})
 assert ok and rec['ports']==names and rec['mask']==[],lines
 result={'id':spec.id,'score':rec['score'],'strict_identical':True,'modules':names,'seconds':time.time()-start,'record_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 print(json.dumps(result),flush=True);return result

if __name__=='__main__':
 import heavy_slot
 heavy_slot.take('m4-419-normalized-all',weight=2)
 from concurrent.futures import ProcessPoolExecutor
 with ProcessPoolExecutor(max_workers=2) as pool:results=list(pool.map(run_source,['FS','G13']))
 with (OUT/'normalized-all-4.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
