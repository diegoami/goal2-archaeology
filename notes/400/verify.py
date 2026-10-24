#!/usr/bin/env python3
"""[designed: T86] Verify original-loader provenance and read-only machine-frame evidence."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'notes/400'))
from collect import SOURCE_SHA,manager_frame

def main():
 source=ROOT/'.cache/G4C.GL';assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA
 records=[]
 for folder in sorted((ROOT/'notes/400').glob('load-r*')):
  rec=json.loads((folder/'record.json').read_text());assert rec['source_sha256']==SOURCE_SHA
  steps=[json.loads(line) for line in (folder/'steps.jsonl').read_text().splitlines()]
  assert steps and all(s['screen'] and s['digest'] for s in steps)
  assert hashlib.sha256((ROOT/'.cache/400'/folder.name/'game/G4C.GL').read_bytes()).hexdigest()==SOURCE_SHA
  for cp in rec['checkpoints']:
   raw=(ROOT/cp['file']).read_bytes();assert hashlib.sha256(raw).hexdigest()==cp['sha256']
   image,regs,hits=manager_frame(raw);assert not image.build_problems()
   assert hits==[cp['bp']] and regs['SS']==cp['ss'] and cp['site']=='000E:75D1'
   assert rec['keys'][-4:]==['g','4','c','Return']
   assert any('Please enter name of saved game' in s['screen'] for s in steps)
   assert 'Holland' in steps[-1]['screen'] and 'Belgium' in steps[-1]['screen']
  records.append((folder.name,rec['status'],len(rec['checkpoints'])))
 assert len(records)==3 and sum(n for _,_,n in records)==1
 delivery=json.loads((ROOT/'notes/400/delivery.json').read_text())
 assert delivery['source_sha256']==SOURCE_SHA and delivery['readback_verified'] is True
 raw=(ROOT/delivery['readback_file']).read_bytes()
 digest=hashlib.sha256(raw).hexdigest();assert digest==delivery['sha256']
 assert delivery['file']==f'g13-{digest[:16]}-g4c-loaded-manager.sav'
 assert delivery['private']=='goal2drive:'+delivery['file']
 accepted=json.loads((ROOT/'notes/400/load-r3/record.json').read_text())['checkpoints'][0]
 assert accepted['sha256']==digest
 image,_,hits=manager_frame(raw);assert len(hits)==1 and not image.build_problems()
 ds=image.DS*16
 assert delivery['post_load_rng']=={f'DS:{o:04X}':int.from_bytes(image.memory[ds+o:ds+o+2],'little') for o in (0x7B62,0x7B64)}
 print('PASS original G4C source hash, unchanged copies, complete key/screen trace, build guard and unique manager read frame:',records)
if __name__=='__main__':main()
