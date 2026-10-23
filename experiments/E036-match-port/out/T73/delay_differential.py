"""Delay's completed frame against original, retaining all memory/register checks."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl')
a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
failed=0
for count,calibration in ((0,3),(1,3),(5,3),(1,65536),(65535,1)):
 out=[]
 for m in (a,b):
  m.write(0,memory);m.write(0xAE000,bytes([0xA5])*0x1000)
  m.write(m.DS*16+0xA9FF,calibration.to_bytes(4,'little'))
  sp,reason=fuzz.run_one(m,True,'214B:1E09',[count],{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp,reason))
 (ra,ma,sp,sa),(rb,mb,_,sb)=out
 differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 print(count,calibration,'differences',differences,'scratch',scratch,flush=True)
print('1E09:5 actual-original cases;',failed,'differing',flush=True)
sys.exit(bool(failed))
