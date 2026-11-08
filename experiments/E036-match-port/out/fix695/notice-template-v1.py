"""Static packed-template decode, transcribed from214B0147; no game execution."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'runtime'))
from original_match.port.tables import from_hex
path=ROOT/'static/goal-exe/tables/ds.hex';raw=from_hex(path.read_text())

def decode(offset):
 start=int.from_bytes(raw[offset:offset+2],'little')-1;rows,cols=raw[offset+2:offset+4]
 pos=offset+4;attr=last=0;out=[]
 for row in range(rows):
  cells=[]
  while len(cells)<cols:
   byte=raw[pos];pos+=1
   if byte==255:attr=raw[pos];pos+=1;continue
   if byte==0:
    count=raw[pos];pos+=1;cells.extend([last]*count)
   else:last=byte|(attr<<8);cells.append(last)
  assert len(cells)==cols
  out.append({'row':(start+row*80)//80+1,'column':start%80+1,
    'text':bytes(v&255 for v in cells).decode('cp437'),'attributes':[v>>8 for v in cells]})
 return {'offset':f'{offset:04X}','rows':out}
print(json.dumps({'method':'static214B0147 packed-template decoding; not behavioral corroboration',
 'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'ordinary':decode(0x5B30),'keeper':decode(0x5B66)},indent=2))
