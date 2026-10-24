"""Ordinary T86 fixture before/after control; no input-memory edits."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import heavy_slot
heavy_slot.take('m4-419-old-stubs',weight=1)
import family,families,image_sources,records,compare
from original_match import port
from original_match.port import _display_finals
spec=families.load_family(OUT/'source-specs-1/G13.json').matches[0];image=image_sources.load(spec.image,ROOT/'.cache/m4-419')
reg=port._module_registry('display');saved={a:reg.entries[a] for a in _display_finals.PORTS.entries}
results=[];memory=[];refs=[]
try:
 for mode,ports in [('reference',()),('old-stubs',('display',))]:
  if mode=='old-stubs':
   for a,e in saved.items():reg.entries[a]=port.Entry(a,e.ret,lambda m,v:None,'old-stub',stub='pre-419 removal')
  held=[]
  rec=family.run_match(image,spec,ports=ports,display_profile=True,watch=lambda m:held.append(m.m),time_limit=6000,stretch_limit=600,counts=['1771:9509'])
  with (OUT/f'G13-before-{mode}-1.jsonl').open('x') as f:f.write(records.dumps(rec)+'\n')
  machine=held[0];data=machine.read(machine.DS*16,0x10000);memory.append(data);refs.append(rec)
  results.append({'mode':mode,'completed':records.is_completed(rec),'score':rec['score'],'DS_AAB2':data[0xAAB2],'9509_calls':rec['counts']['1771:9509']})
finally:reg.entries.update(saved)
receipt={'input_edits':[],'results':results,'strict_differences':compare.differences(*refs,no_screen=True,strict_display=True),'DS_differing_bytes':sum(a!=b for a,b in zip(*memory))}
with (OUT/'old-stubs-reproduction-1.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt),flush=True)
assert all(x['completed'] and x['score']==[1,0] and x['9509_calls']==1 for x in results)
assert [x['DS_AAB2'] for x in results]==[6,3] and receipt['strict_differences']
