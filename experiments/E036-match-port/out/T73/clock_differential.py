"""Clock bodies against actual original, including nested Pascal argument order and dead frames.

Inputs are synthetic numbers/colour/target; original bytes remain process-local.
"""
from pathlib import Path
import random,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl')
a,_=fuzz.make_machine(img,memory,None)
b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(73054)
failed=0
for number in (0,1,7,9,10,45,90,99,100):
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x1000))
 for m in (a,b):
  m.write(0,memory);m.write(0x90000,bytes(0x10000));m.write(0xAE000,garbage)
  m.write(m.DS*16+0xA96A,b'\x00\x02\x00\x90')
  sp,reason=fuzz.run_one(m,False,'0791:054C',[0x12,number],{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp,reason))
 (ra,ma,sp,sa),(rb,mb,_,sb)=out
 differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False)
 failed+=bool(differences)
 print(number,'differences',differences,'scratch',scratch,flush=True)
print('054C/04C9/0481:9 actual-original cases;',failed,'differing',flush=True)
sys.exit(bool(failed))
