"""Whistle/note/jingle/off vs actual original, with real library and complete dead frames.

Only synthetic inputs, comparison counts/addresses and register differences leave
this process; differing memory bytes are removed from the reusable fuzz reporter.
"""
from pathlib import Path
import random,re,sys,argparse
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl')
a,_=fuzz.make_machine(img,memory,None);b,_=fuzz.make_machine(img,memory,'display')
rng=random.Random(73187);failed=0
cases=[('214B:1E8D',[],disabled,0,0) for disabled in (0,1)]
cases += [('214B:1EF1',[duration,note,octave],disabled,transpose,3) for disabled,duration,note,octave,transpose in
          ((1,2,11,6,255),(0,1,7,6,0),(0,1,11,6,1),(0,1,9,6,255))]
cases += [('214B:1F87',[count],0,0,calibration) for count,calibration in ((5,9),(1,10),(2,50))]
cases += [('0791:0441',[1],0,speed,10) for speed in (0,1)]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--start-at',type=int,default=0);options=parser.parse_args()
assert 0<=options.start_at<len(cases)
print('continuation starts at case',options.start_at,flush=True)
for trial,(target,args,disabled,transpose,calibration) in list(enumerate(cases))[options.start_at:]:
 out=[];garbage=bytes(rng.randrange(256) for _ in range(0x2000))
 for m in (a,b):
  m.write(0,memory);m.write(0xAD000,garbage);m.write(0x90000,bytes(0x10000))
  m.write(m.DS*16+0xA9FC,bytes([disabled]));m.write(m.DS*16+0xA9FF,calibration.to_bytes(4,'little'))
  m.write(m.DS*16+0x7968,bytes([transpose]));m.write(m.DS*16+0x7966,b'\x02\x00')
  m.write(m.DS*16+0xA923,b'\x00\x02\x00\x90');m.write(0x9023F,bytes([transpose]))
  sp,reason=fuzz.run_one(m,target[:4]=='214B',target,args,{'ax':0xBEEF,'dx':0x1234},10)
  out.append((fuzz.final(m),bytes(m._uc.mem_read(0,fuzz.MEM_SIZE)),sp,reason))
 (ra,ma,sp,sa),(rb,mb,_,sb)=out
 differences,scratch=fuzz.compare(ra,rb,ma,mb,sp,False);failed+=bool(differences)
 safe=[re.sub(r' \(original [0-9A-F]{2}, port [0-9A-F]{2}\)','',s) for s in differences]
 print(trial,target,args,disabled,transpose,calibration,'differences',safe,'scratch',scratch,flush=True)
print('sound chain:',len(cases)-options.start_at,'actual-original cases;',failed,'differing',flush=True)
sys.exit(bool(failed))
