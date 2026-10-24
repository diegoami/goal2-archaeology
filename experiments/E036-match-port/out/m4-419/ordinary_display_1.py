"""Corrected display versus native T86 ordinary match, including every DS byte."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import heavy_slot
heavy_slot.take('m4-419-ordinary-display',weight=1)
import family,families,image_sources,records,compare
spec=families.load_family(OUT/'source-specs-1/G13.json').matches[0];image=image_sources.load(spec.image,ROOT/'.cache/m4-419');refs=[];memory=[];results=[]
for mode,ports in [('reference',()),('display',('display',))]:
 held=[];rec=family.run_match(image,spec,ports=ports,display_profile=True,watch=lambda m:held.append(m.m),time_limit=6000,stretch_limit=600,counts=['1771:9509','1771:883F','1771:937C','1771:8CCF'])
 with (OUT/f'G13-ordinary-{mode}-1.jsonl').open('x') as f:f.write(records.dumps(rec)+'\n')
 data=held[0].read(held[0].DS*16,0x10000);memory.append(data);refs.append(rec)
 results.append({'mode':mode,'completed':records.is_completed(rec),'score':rec['score'],'DS_AAB2':data[0xAAB2],'counts':rec['counts'],'mask':rec['mask']})
receipt={'input_edits':[],'results':results,'strict_differences':compare.differences(*refs,no_screen=True,strict_display=True),'DS_differing_bytes':sum(a!=b for a,b in zip(*memory))}
with (OUT/'ordinary-display-1.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt),flush=True)
assert all(x['completed'] and x['score']==[1,0] and x['DS_AAB2']==6 for x in results)
assert not receipt['strict_differences'] and receipt['DS_differing_bytes']==0
