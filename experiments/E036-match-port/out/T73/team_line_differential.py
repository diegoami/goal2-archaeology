"""Signed line bars and live role accumulation vs original, including complete frames."""
from pathlib import Path
import random,re,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(7311);failed=0
cases=[('1771:11E1',15,54,(-1,-8,1028,1024)),('1771:11E1',20,54,(257,4,0,3)),
       ('1771:1289',0,54,(0,0,0,0)),('1771:1289',1,0xFF38,(0,0,0,0))]
for target,arg,hybrid,values in cases:
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  for off,pointer in ((0xA917,b'\x00\x30\x00\x90'),(0xA91B,b'\x00\x10\x00\x90'),(0xA96E,b'\x00\x80\x00\x90')):m.write(m.DS*16+off,pointer)
  m.write(m.DS*16+0x9B34,b'\x03\x00\x04\x00')
  for position in range(6):m.write(m.DS*16+0xD7C+position,bytes([position]))
  performances=[55,54,10055,0,hybrid,0]+[65535]*5
  for word,performance in enumerate(performances,1):
   m.write(0x91000+20*word+6,bytes([word-1 if word<=6 else 0]));m.write(0x91000+20*word+18,performance.to_bytes(2,'little'))
   for country in (3,4):m.write(0x93000+country*191+(word-1)*2,word.to_bytes(2,'little'))
  for index,value in enumerate(values):
   m.write(m.DS*16+0x9B47+4*index,(value&65535).to_bytes(2,'little'));m.write(m.DS*16+0x9B49+4*index,b'\xfe\xca')
  sp,reason=fuzz.run_one(m,False,target,[arg],{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp))
 (ra,ma,sp),(rb,mb,_)=out;differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(target,arg,hybrid,values,'differences',safe,'scratch',scratch,flush=True)
print('team line:',len(cases),'actual-original cases;',failed,'differing',flush=True);sys.exit(bool(failed))
