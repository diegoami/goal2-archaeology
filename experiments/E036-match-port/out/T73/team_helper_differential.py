"""Team-panel helper ABI and wrapping aggregates against the actual original."""
from pathlib import Path
import random,re,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(7313);failed=0
cases=[('1771:0947',[130,0x8800,0x9000],0,0),('1771:0AF8',[24,10,0],0,0),
       ('1771:0AF8',[24,10,130],0,0),('1771:0AF8',[24,10,130],9,0),
       ('1771:1527',[25,8,3],0,0),('1771:13D0',[3],0,0),('1771:13D0',[3],0,128)]
for target,args,status,morale in cases:
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  for off,pointer in ((0xA917,b'\x00\x30\x00\x90'),(0xA91B,b'\x00\x10\x00\x90'),(0xA91F,b'\x00\x01\x00\x90'),
                      (0xA923,b'\x00\x40\x00\x90'),(0xA96E,b'\x00\x80\x00\x90'),(0x9B68,b'\x00\x50\x00\x90'),
                      (0x9B6C,b'\x00\x60\x00\x90'),(0x9B78,b'\x00\x70\x00\x90'),(0x9B74,b'\x00\x71\x00\x90')):m.write(m.DS*16+off,pointer)
  for word in range(1,21):
   m.write(0x91000+20*word,bytes([3,25,60,40,8,8,4,4,5,0,2,0,0,20,10,0,0,0,55,0]))
   m.write(0x96000+word*11,b'\x01X');m.write(0x93000+3*191+(word-1)*2,word.to_bytes(2,'little'))
  m.write(0x91000+20+12,bytes([morale]));m.write(0x93000+3*191+0x2E,b'\x82')
  m.write(0x95030,b'\x01C');m.write(0x97000+130,b'A');m.write(0x97100+130*13,b'\x0cLongManagerX')
  m.write(0x90100+130*3+1,bytes([status]));m.write(m.DS*16+0xC1E,b'\x01\x00')
  sp,reason=fuzz.run_one(m,target in ('1771:0947','1771:0AF8'),target,args,{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp))
 (ra,ma,sp),(rb,mb,_)=out;differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(target,args,status,morale,'differences',safe,'scratch',scratch,flush=True)
print('team helpers:',len(cases),'actual-original cases;',failed,'differing',flush=True);sys.exit(bool(failed))
