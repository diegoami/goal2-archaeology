"""Tone divisor/body ABI vs original, device output omitted by the candidate."""
from pathlib import Path
import random,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl')
a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(731)
failed=0
for disabled,frequency in ((1,0),(1,440),(0,1),(0,440),(0,32768),(0,65535)):
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x1000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAE000,garbage);m.write(m.DS*16+0xA9FC,bytes([disabled]))
  sp,reason=fuzz.run_one(m,True,'214B:1EBC',[frequency],{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp,reason))
 (ra,ma,sp,sa),(rb,mb,_,sb)=out
 differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 print(disabled,frequency,'differences',differences,'scratch',scratch,flush=True)
print('1EBC:6 actual-original cases;',failed,'differing',flush=True)
sys.exit(bool(failed))
