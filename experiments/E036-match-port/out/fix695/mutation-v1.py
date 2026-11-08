"""Registered selection.request-not-set omission must fail the actual request-ack oracle."""
import argparse,builtins,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists()
assert sys.implementation.name=='pypy'
original_import=builtins.__import__
def deny(name,*args,**kw):
 if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
 return original_import(name,*args,**kw)
builtins.__import__=deny
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
def arm(variant):
 m=Match(Image.from_savestate(raw),Fixture(7,19,index=21),managed=7,seed=0x1234,substitutions=5,
  ticks=True,delay_byte=0,engine='port',ports=[variant] if variant else None,substitution_control=True)
 paused=asked=False
 for event in m.events():
  if event.kind=='tick' and event.minute>=2 and not paused:m.pause();paused=True
  if event.kind!='decision':continue
  if event.data['context']!='pause':m.answer(opportunity='timeout') if event.data['context']=='substitution_opportunity' else m.answer();continue
  if not asked:m.answer(request_substitution=True,edit_only=True);asked=True
  else:
   assert event.data['edited'] and event.data['request_substitution'] is True,'actual paused request acknowledgement must be true'
   return
 raise AssertionError('request ack not reached')
arm(None)
rejected=False
try:arm('selection.request-not-set')
except AssertionError as error:
 assert str(error)=='actual paused request acknowledgement must be true'
 rejected=True
assert rejected,'omission survived the same request acknowledgement oracle'
value={'positive_real_key_request_ack_pass':True,'registered_mutant':'selection.request-not-set',
 'mutant_rejected_by_same_actual_ack_oracle':True,'raw_original_bytes_published':False,
 'source_sha256':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'runtime/original_match/match.py',ROOT/'runtime/original_match/screens.py',Path(__file__)]}}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print('PASS:actual request positive; registered request-not-set omission rejected')
