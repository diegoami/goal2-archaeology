"""Diagnostic of the final00FF saved-BP cell, never mask evidence or raw bytes.

Entry-safe stack reads identify return/caller and BP/SP addresses. Native WRITE
callbacks read no registers. Output contains only addresses, identifiers, hashes
and equality predicates; original memory is never serialized.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import family,families,records,compare
from original_match import Image
from original_match.assets import reference_image
from unicorn import UC_HOOK_MEM_WRITE
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
image=Image.from_bytes(reference_image(family.DEFAULT_CACHE))
spec=next(m for m in families.discover()['O8'].matches if m.id=='O8/c1-c2-friendly')
reports={}
for name,ports in [('original',()),('display',('display',))]:
 report={'entries':0,'target_entry':None,'native_writes':0,'host_writes':0,'port_writes':0,'last_write':None}
 def watch(match):
  m=match.m;ds=m.DS*16;target=ds+0xE9D6;last={}
  def entered(replay):
   if replay:return
   bp,sp=m.reg('bp'),m.reg('sp');ss=m.reg('ss')
   ip,cs=m.stack_word(0),m.stack_word(2)
   last.clear();last.update({'return':m.where(cs,ip),'sp_ds_offset':ss*16+sp-ds,'bp_ds_offset':ss*16+bp-ds,'bp_ss_offset':bp})
   report['entries']+=1
   if ss*16+sp-ds==0xE9D8:report['target_entry']=dict(last)
  m.at('214B:00FF',entered)
  def stamp(kind,address,data):
   if address<=target and address+len(data)>=target+2:
    word=data[target-address:target-address+2]
    report[kind+'_writes']+=1
    frames=[f.describe() for f in m.frames]
    funcs=[]
    if kind=='host':
     frame=sys._getframe(2)
     while frame is not None and len(funcs)<10:
      funcs.append(frame.f_code.co_name);frame=frame.f_back
    report['last_write']={'kind':kind,'entry':dict(last),'equals_entry_bp':int.from_bytes(word,'little')==last.get('bp_ss_offset'),
      'word_sha256':hashlib.sha256(word).hexdigest(),'port_frames':frames,'host_functions':funcs, 'instruction_P_offset':None if kind=='host' else m.pc()-m.load*16}
  def written(address,size,value):
   if address<=target and address+size>=target+2:
    stamp('port' if m._pc_override is not None else 'native',address,value.to_bytes(size,'little'))
  m.on_write(ds,target+1,written)
  assert m.write_tap is None
  m.write_tap=lambda address,data:stamp('host',address,data)
 record=family.run_match(image,spec,ports=ports,time_limit=120,stretch_limit=30,watch=watch)
 (out/(name+'-record.jsonl')).open('x').write(records.dumps(record)+'\n')
 reports[name]=report
 if record['error']:raise SystemExit(record['error'])
ref=compare.load(ROOT/'experiments/E036-match-port/out/T73/coverage-unported-desktop-20261023/coverage-unported.jsonl')
a=compare.load(out/'original-record.jsonl');e=families.discover()['O8'].expected()
lines,ok=compare.check(ref,a,{k:e[k] for k in a},image_sha256=families.image_sha256())
(out/'original-compare.txt').open('x').write('\n'.join(lines)+'\n')
(out/'trace.json').open('x').write(json.dumps({'warning':'NEVER mask evidence','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'original_exact':ok,'reports':reports},indent=2)+'\n')
print('original exact',ok,flush=True);print(json.dumps(reports,indent=2),flush=True)
sys.exit(not ok)
