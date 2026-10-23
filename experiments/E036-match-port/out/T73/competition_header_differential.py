"""The original competition header's full-memory/caller-frame effects, synthetic states."""
from pathlib import Path
import random,re,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(738939);failed=0
for interactive,remaining,snapshot in ((0,0,0),(1,0,0),(1,1,0),(1,1,1)):
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  m.write(m.DS*16+0xA923,b'\x00\x01\x00\x90');m.write(m.DS*16+0xA96E,b'\x00\x20\x00\x90')
  m.write(0x90138,remaining.to_bytes(2,'little'))
  m.write(0xAE400+10,interactive.to_bytes(2,'little'));m.write(0xAE400-9,bytes([snapshot]))
  sp,reason=fuzz.run_one(m,False,'1771:8939',[0xE400],{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp))
 (ra,ma,sp),(rb,mb,_)=out;differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(interactive,remaining,snapshot,'differences',safe,'scratch',scratch,flush=True)
print('8939:4 actual-original cases;',failed,'differing',flush=True);sys.exit(bool(failed))
