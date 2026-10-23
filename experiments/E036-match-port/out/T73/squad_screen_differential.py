"""Squad list/screen vs original on synthetic valid squads, all memory and dead frames."""
from pathlib import Path
import random,re,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(73422);failed=0
cases=[('1771:4D8A',[3],0),('1771:4E22',[0,3],0),('1771:4E22',[2,3],1)]
for target,args,live in cases:
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  for off,pointer in ((0xA917,b'\x00\x30\x00\x90'),(0xA91B,b'\x00\x10\x00\x90'),(0xA923,b'\x00\x40\x00\x90'),
                      (0xA96E,b'\x00\x80\x00\x90'),(0x9B68,b'\x00\x50\x00\x90'),(0x9B6C,b'\x00\x60\x00\x90')):m.write(m.DS*16+off,pointer)
  for word in range(1,21):
   m.write(0x91000+20*word,bytes([3,25,60,40,8,8,4,4,5,0,2,0,20,24,24,0,0,0,55,0]))
   m.write(0x96000+word*11,b'\x01X')
   m.write(0x93000+3*191+(word-1)*2,word.to_bytes(2,'little'))
  m.write(0x93000+3*191+0x2E,b'\x82');m.write(0x95030,b'\x01C')
  m.write(0x9403F,b'\x01\x01\x00');m.write(m.DS*16+0xC1B,b'\x01\x00')
  m.write(m.DS*16+0xC1E,bytes([1,live]));m.write(m.DS*16+0x9B36,b'\x04\x00')
  m.write(m.DS*16+0x9B3A,b'\x04\x02');m.write(m.DS*16+0x9A3E,bytes(80))
  sp,reason=fuzz.run_one(m,True,target,args,{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp))
 (ra,ma,sp),(rb,mb,_)=out;differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(target,args,live,'differences',safe,'scratch',scratch,flush=True)
print('squad screens:',len(cases),'actual-original cases;',failed,'differing',flush=True);sys.exit(bool(failed))
