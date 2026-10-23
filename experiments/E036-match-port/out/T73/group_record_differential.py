"""Group rows and stage headers vs original, all memory including dead frames."""
from pathlib import Path
import random,re,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(738);failed=0
cases=[('1771:8A87',phase,snapshot,0) for phase,snapshot in ((0,0),(1,0),(0,1),(1,1))]
cases += [('1771:5AC4',flag,snapshot,leader) for snapshot,flag,leader in ((0,0,0),(0,1,7),(1,0,0),(1,1,7))]
for target,phase,snapshot,leader in cases:
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  for off,pointer in ((0xA923,b'\x00\x01\x00\x90'),(0xA96E,b'\x00\x80\x00\x90'),(0xA917,b'\x00\x20\x00\x90'),
                      (0xA933,b'\x00\x30\x00\x90'),(0x9B68,b'\x00\x50\x00\x90')):m.write(m.DS*16+off,pointer)
  m.write(0x92000+3*191+0x2C,b'\x01')
  for country in range(1,9):m.write(0x95000+country*16,b'\x01X')
  m.write(0xAE400-8,b'\x03\x00');m.write(0xAE400-4,b'\x02\x00');m.write(0xAE400-9,bytes([snapshot]))
  for index in range(1,5):
   base=0x93000+index*8+112+448+phase*0x700+snapshot*0xE00-0x200
   m.write(base,(index+3).to_bytes(2,'little')+bytes([index,index+1,index+2,index+10,index+20,index+30]))
  m.write(0x90138,b'\x03\x00\x04\x00');m.write(0x90140,b'\x01')
  m.write(0x9012C+(5 if snapshot else 1)*2,leader.to_bytes(2,'little'))
  args=[0xE400,phase] if target=='1771:8A87' else [1,snapshot,phase]
  sp,reason=fuzz.run_one(m,False,target,args,{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp))
 (ra,ma,sp),(rb,mb,_)=out;differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(target,phase,snapshot,leader,'differences',safe,'scratch',scratch,flush=True)
print('group records:',len(cases),'actual-original cases;',failed,'differing',flush=True);sys.exit(bool(failed))
