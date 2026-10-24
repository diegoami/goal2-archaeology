"""Locate the new original write; keep its mismatch as diagnostic, not a reference."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import family,families,image_sources,heavy_slot
heavy_slot.take('m4-419-original-write-trace',weight=1)
spec=families.load_family(OUT/'source-specs-1/FS.json').matches[0]
image=image_sources.load(spec.image,ROOT/'.cache/dl');writes=[]
def watch(match):
 m=match.m;target=m.load*16+0x5A3CE
 def changed(address,size,value):
  if address<=target<address+size:
   pc=m.pc()-m.load*16
   seg=max(s for s in (0,0xE,0x791,0x16D6,0x1771,0x2138,0x2139,0x214B,0x235C,0x2382,0x23E4) if s*16<=pc)
   writes.append({'writer':f'{seg:04X}:{pc-seg*16:04X}','program_relative_address':hex(address-m.load*16),'size':size})
 m.on_write(target,target,changed)
rec=family.run_match(image,spec,time_limit=600,stretch_limit=120,watch=watch)
with (OUT/'original-write-trace-1.json').open('x') as f:json.dump({'source_sha256':spec.image_sha256,'writes':writes,'checker_error':rec['error']},f,indent=2);f.write('\n')
assert writes and rec['error'] and rec['error'].startswith('UndeclaredWrite'),rec['error']
print(writes,flush=True)
