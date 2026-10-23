"""T73: isolate observational memory-hook behavior; outputs counts/records, never bytes."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'runtime'));sys.path.insert(0,str(ROOT/'experiments/E036-match-port'))
import family,families,records
from original_match import Image
from original_match.assets import reference_image
from unicorn import UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ_AFTER,UC_HOOK_CODE
from unicorn import x86_const as X
mode=sys.argv[1];out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
counts={'reads':0,'writes':0}
registers={'none':[],'cs':[X.UC_X86_REG_CS],'eip':[X.UC_X86_REG_EIP],'esp':[X.UC_X86_REG_ESP],
           'ss':[X.UC_X86_REG_SS],'sp':[X.UC_X86_REG_SP],
           'all':[X.UC_X86_REG_CS,X.UC_X86_REG_EIP,X.UC_X86_REG_ESP,X.UC_X86_REG_SS]}
def watch(match):
 m=match.m;ds=m.DS*16
 def hook(uc,access,address,size,value,data):
  counts['reads' if access==16 else 'writes']+=1
  for r in registers.get(mode,[]):uc.reg_read(r)
 
 if mode=='code':
  m.uc.hook_add(UC_HOOK_CODE,lambda *args: None)
 kinds=UC_HOOK_MEM_READ_AFTER if mode=='after' else UC_HOOK_MEM_WRITE if mode=='write' else UC_HOOK_MEM_READ if mode!='both' else UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE
 
 if mode=='nonstack':
  m.uc.hook_add(kinds,hook,begin=ds,end=ds+0xAD0F)
  m.uc.hook_add(kinds,hook,begin=ds+0xED10,end=ds+65535)
 else:
  m.uc.hook_add(kinds,hook,begin=ds,end=ds+65535)
spec=next(m for m in families.discover()['O8'].matches if m.id=='O8/c1-c2-friendly')
r=family.run_match(Image.from_bytes(reference_image(family.DEFAULT_CACHE)),spec,watch=watch,time_limit=6000,stretch_limit=6000)
(out/'record.jsonl').open('x').write(records.dumps(r)+'\n')
print(mode,counts,r['error'],r['score'],r['ticks'],flush=True)
