"""Ordinary watched-match input through the kit's real poll/key services.

Intervention: append A7 to the existing poll_keys input queue at minute 1 (as
pause() queues Enter). No guest memory/CPU edits. Stop at minute 2; these are
explicit input-prefix checks, not completed-family records or new goldens.
"""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
from original_match.assets import reference_image
results=[]
for ports in (None,['menus','display']):
 image=Image.from_bytes(reference_image(ROOT/'.cache/dl'))
 match=Match(image,Fixture(7,19,index=40),managed=7,seed=1,ports=ports,timeout_s=120)
 entered=[]
 match.m.at('214B:1E5A',lambda replay:entered.append(1) if not replay else None)
 queued=False;initial=None;last=None
 for event in match.events():
  if event.kind=='decision':match.answer()
  if event.kind=='minute':
   if event.minute==1 and not queued:
    initial=match.m.rd(0xA9FC,1)
    match.st['poll_keys'].append(0xA7);queued=True
   elif event.minute>=2 and queued:
    last=event.minute;break
 final=match.m.rd(0xA9FC,1)
 assert initial is not None and last==2 and final==int(initial==0)
 assert len(entered)==1 and not match.st['poll_keys']
 results.append({'ports':ports or [],'queued_at_minute':1,'observed_at_minute':last,
                 'key':0xA7,'guest_memory_or_CPU_intervention':False,
                 'native_routine_entries':len(entered),'before_mute':initial,'after_mute':final,
                 'complete_match':False})
assert results[0]['before_mute']==results[1]['before_mute'] and results[0]['after_mute']==results[1]['after_mute']
with (OUT/'poll-integration-1.json').open('x') as f:json.dump(results,f,indent=2);f.write('\n')
print('PASS: original and menus+display consume A7 through actual watched-match key poll and toggle mute')
