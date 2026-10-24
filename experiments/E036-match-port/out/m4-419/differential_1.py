"""Direct native differentials: synthetic parent frames, native callees, all memory."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port'),str(ROOT/'experiments/E036-match-port/out/T60')]
import heavy_slot
heavy_slot.take('m4-419-differential',weight=1)
import fuzz,image_sources
from original_match import port
from original_match.port import _display_finals
image=image_sources.load('T86-stage8',ROOT/'.cache/m4-419');memory=bytes(image.memory[:fuzz.MEM_SIZE]).ljust(fuzz.MEM_SIZE,b'\0')
a,_=fuzz.make_machine(image,memory,None);b,_=fuzz.make_machine(image,memory,None);port.install(b,[(_display_finals.PORTS,None)])
PARENT=0xD000;CHILD=0xD100
cases=[]
for target in _display_finals.PORTS.entries:
 for snapshot in (0,1):
  for interactive in (0,1):cases.append((target,snapshot,interactive))
results=[]
for target,snapshot,interactive in cases:
 outputs=[];entry=_display_finals.PORTS.entries[target]
 for m in (a,b):
  m.write(0,memory);m.frames.clear()
  m.write(fuzz.SS*16+fuzz.SP0-0x3000,bytes([0xA5])*0x3000)
  def w(off,val,n=2):m.write(fuzz.SS*16+off,val.to_bytes(n,'little'))
  w(PARENT-9,snapshot,1);w(PARENT-8,20);w(PARENT-6,20);w(PARENT-4,3);w(PARENT-2,3);w(PARENT+10,interactive,1);w(CHILD+4,PARENT)
  m.write(m.DS*16+0x79AE,b'\1');m.write(m.DS*16+0xA976,b'\x1b')
  args=[PARENT]
  if target.endswith(('91CE','937C')):args=[CHILD]
  if target.endswith('8A5D'):args=[PARENT,1]
  if target.endswith('8CCF'):args=[PARENT,23,8,4,9,2392]
  if target.endswith(('5C94','5CCB')):
   ptr=m.far(0xA92B)+8*(2392-1);args=[ptr & 15,ptr>>4]
  sp,reason=fuzz.run_one(m,entry.far,target,args,{'ax':0xBEEF,'dx':0x1234,'bp':0x5678},30)
  outputs.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp,reason))
 (ra,ma,sp,reasona),(rb,mb,_,reasonb)=outputs
 differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False)
 differences=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',x) for x in differences]
 result={'target':target,'snapshot':snapshot,'interactive':interactive,'differences':differences,'scratch':scratch,'all_memory_equal':ma==mb,'arithmetic_flags_compared':False,'memory_sha256':hashlib.sha256(ma).hexdigest(),'returned':ra['eip']==rb['eip']==0x10,'reasons':[reasona,reasonb]}
 results.append(result);print(json.dumps(result),flush=True)
with (OUT/'differential-1.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
assert all(r['returned'] and not r['differences'] and not r['scratch'] and r['all_memory_equal'] for r in results),results
