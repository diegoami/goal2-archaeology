"""Fixture/country text ports vs original, all memory and complete caller frames."""
from pathlib import Path
import random,re,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(7376);failed=0
cases=[('1771:0FB1',[54,8,country],1,3,0) for country in (0,3)]
cases += [('1771:76FA',[58,8,0x100,0x9000],kind,first,flag) for kind,first,flag in ((0,3,0),(1,254,0),(1,3,0),(1,3,1),(1,3,2))]
cases += [('1771:77C3',[58,8,0x100,0x9000],kind,first,flag) for kind,first,flag in ((0,3,0),(1,254,0),(1,3,2))]
for target,args,kind,first,flag in cases:
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  for off,pointer in ((0xA96E,b'\x00\x80\x00\x90'),(0xA917,b'\x00\x20\x00\x90'),(0x9B68,b'\x00\x50\x00\x90')):m.write(m.DS*16+off,pointer)
  m.write(0x95030,b'\x01X');m.write(0x95040,b'\x01Y')
  m.write(0x90100,bytes([first,1,kind,flag,3,0,4,0]))
  sp,reason=fuzz.run_one(m,target=='1771:76FA',target,args,{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp))
 (ra,ma,sp),(rb,mb,_)=out;differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(target,args,kind,first,flag,'differences',safe,'scratch',scratch,flush=True)
print('fixture text:',len(cases),'actual-original cases;',failed,'differing',flush=True);sys.exit(bool(failed))
