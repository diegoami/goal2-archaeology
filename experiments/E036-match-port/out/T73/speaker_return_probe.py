"""Original kit speaker return registers, not device/memory dumps."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/E036-match-port/out/T60'))
import fuzz
img,memory=fuzz.setup(ROOT/'.cache/dl');m,_=fuzz.make_machine(img,memory,None)
for target in ('214B:1E75','214B:1E8D'):
 for disabled in (0,1):
  m.write(0,memory);m.write(m.DS*16+0xA9FC,bytes([disabled]))
  sp,reason=fuzz.run_one(m,True,target,[],{'ax':0x1234,'dx':0xABCD},10)
  print(target,'disabled',disabled,'AX',hex(m.reg('ax')),'DX',hex(m.reg('dx')),flush=True)
