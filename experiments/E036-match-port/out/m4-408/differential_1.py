"""Original-vs-display sound toggle/off, full memory including dead frames."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
image,memory=fuzz.setup(ROOT/'.cache/dl')
native,_=fuzz.make_machine(image,memory,None)
ported,_=fuzz.make_machine(image,memory,'display')
results=[]
for target in ('214B:1E5A','214B:1E8D'):
 for disabled in (0,1,2,255):
  for ax,flags in ((0xBEEF,0x202),(0x1234,0x602)):
   outputs=[]
   for machine in (native,ported):
    machine.write(0,memory)
    machine.write(fuzz.SS*16+fuzz.SP0-0x100,bytes([0xA5])*0x100)
    machine.write(machine.DS*16+0xA9FC,bytes([disabled]))
    sp,reason=fuzz.run_one(machine,True,target,[],{'ax':ax,'dx':0x1234,'bp':0x5678,'eflags':flags},10)
    regs=fuzz.final(machine);data=bytes(machine._uc.mem_read(0,fuzz.MEM_SIZE))
    assert regs['cs']==0x9F00 and regs['eip']==0x10,(target,reason)
    outputs.append((regs,data,sp))
   (a,ma,sp),(b,mb,_)=outputs
   differences,scratch=fuzz.compare(a,b,ma,mb,sp,True)
   safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
   results.append({'target':target,'disabled':disabled,'AX_input':ax,'flags_input':flags,
                   'differences':safe,'scratch':scratch,'all_registers_equal':a==b,
                   'all_memory_equal':ma==mb,'memory_sha256':hashlib.sha256(ma).hexdigest()})
with (OUT/'differential-1.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
assert all(not r['differences'] and not r['scratch'] and r['all_registers_equal'] and r['all_memory_equal'] for r in results),results
print('PASS:',len(results),'actual-original cases; strict registers/flags and every memory byte, including dead frames')
