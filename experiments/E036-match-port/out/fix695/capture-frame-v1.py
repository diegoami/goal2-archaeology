"""Capture one ORIGINAL actual8062entry after a real independent request; private bytes only."""
import argparse,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
from original_match.machine import REGS
p=argparse.ArgumentParser();p.add_argument('--side',type=int,choices=(0,1),required=True);p.add_argument('--private',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
assert not a.out.exists() and not a.private.exists();a.private.mkdir(parents=True)
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
fixture=Fixture(7,19,index=21) if a.side==0 else Fixture(19,7,index=21)
m=Match(Image.from_savestate(raw),fixture,managed=7,seed=0x1234,substitutions=5,ticks=True,record_draws=True,
 delay_byte=0,engine='original',substitution_control=True,timeout_s=600)
paused=sent=acked=False;captured=None

def capture(replay):
 global captured
 if replay or captured is not None or not acked:return
 assert m.m.rd(0x9B40,1)==1
 memory=m.m.read(0,0x110000);(a.private/'memory.bin').write_bytes(memory)
 (a.private/'header.bin').write_bytes(m.image_header);(a.private/'tail.bin').write_bytes(m.image_tail)
 fields={name:copy.deepcopy(getattr(m,name)) for name in ['opts','st','inputs','side','image_sha256','fixture_ptr','end_lin','timeout_s']}
 fields.update(load=m.m.load,registers={r:m.m.reg(r) for r in REGS})
 (a.private/'coordinator.json').write_text(json.dumps(fields,sort_keys=True))
 captured=dict(input_memory_sha256=hashlib.sha256(memory).hexdigest(),
  coordinator_sha256=hashlib.sha256((a.private/'coordinator.json').read_bytes()).hexdigest(),
  registers=fields['registers'],side=m.side,request_byte=1)
m.m.at('0791:8062',capture)
for event in m.events():
 if event.kind=='tick' and event.minute>=2 and not paused:m.pause();paused=True
 if event.kind!='decision':continue
 if event.data['context']=='pause':
  if not sent:m.answer(request_substitution=True,edit_only=True);sent=True
  else:assert event.data['request_substitution'] is True;acked=True;m.answer()
 elif captured is not None:break
 else:m.answer(opportunity='timeout') if event.data['context']=='substitution_opportunity' else m.answer()
assert captured is not None
value={**captured,'private_path':str(a.private),'method':'unmodified original actual8062entry after real key request; genuine endpoint side',
 'original_asset_sha256':hashlib.sha256(raw).hexdigest(),
 'sources_sha256':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'runtime/original_match/match.py',ROOT/'runtime/original_match/screens.py',Path(__file__)]}}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print('PASS captured original8062entry side',a.side)
