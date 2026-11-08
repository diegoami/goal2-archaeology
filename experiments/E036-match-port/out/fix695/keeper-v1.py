"""#695 bounded prepared caller-flag control, not a natural keeper injury or replacement."""
import argparse,builtins,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--engine',choices=('original','port'),required=True)
p.add_argument('--side',type=int,choices=(0,1),required=True);p.add_argument('--keeper',type=int,choices=(0,1),required=True)
p.add_argument('--response',choices=('dismiss','timeout'),required=True);p.add_argument('--out',type=Path,required=True)
a=p.parse_args();assert not a.out.exists()
if a.engine=='port':
 assert sys.implementation.name=='pypy';imp=builtins.__import__
 def deny(name,*args,**kw):
  if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
  return imp(name,*args,**kw)
 builtins.__import__=deny
 try:__import__('unicorn')
 except ImportError:pass
 else:raise AssertionError('denial failed')
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
from original_match.machine import REGS
from original_match.match import KEYPRESSED,KP_WAIT,SITE_NOTICE,SITE_SELECT
from original_match import screens as S
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
fixture=Fixture(7,19,index=21) if a.side==0 else Fixture(19,7,index=21)
m=Match(Image.from_savestate(raw),fixture,managed=7,seed=0x1234,substitutions=5,ticks=True,record_draws=True,
 delay_byte=0,engine=a.engine,substitution_control=True,timeout_s=600)
assert m.side==a.side
keys=[];waits=[];edits=[];paused=False;sent=False;acked=False;prepared=False;answered=False;forced=None

def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def regs():return {r:m.m.reg(r) for r in REGS}
class Tap:
 def site_enter(self,linear,replay,**kw):
  if replay or kw.get('fired'):return
  if linear==m.m.lin('0791:CC2E') and m.m.stack_word(0)==0x8042:
   row=m._screen_raw()[3840:4000];text=bytes(row[::2]);phrase=b'HAS NO GOALKEEPER' if a.keeper else b'SUBSTITUTION OPPORTUNITY'
   start=text.find(phrase);assert start>=0
   waits.append(dict(polls=m.m.stack_word(2),key_polls=0,delays=0,row_sha256=hashlib.sha256(row).hexdigest(),
    phrase=phrase.decode(),phrase_column=start+1,phrase_attributes=list(row[2*start+1:2*(start+len(phrase)):2]),
    hint_attributes=list(row[131:160:2])))
  elif linear==m.m.lin(KEYPRESSED) and waits:
   site=m.m.where(m.m.stack_word(2),m.m.stack_word(0))
   if site==KP_WAIT and m.m.frame_word(m.m.reg('bp'),2)==0x8042:waits[-1]['key_polls']+=1
  elif linear==m.m.lin('214B:1E09') and waits:
   site=m.m.where(m.m.stack_word(2),m.m.stack_word(0))
   if site=='0791:CC65' and m.m.frame_word(m.m.reg('bp'),2)==0x8042:
    assert m.m.stack_word(4)==10;waits[-1]['delays']+=1
 def site_leave(self,*args,**kwargs):pass
m.m.site_tap=Tap();m.m.at('214B:1E09',lambda replay:None)
previous=m._key_for

def key(site):
 value=previous(site)
 if value is not None:keys.append([site,value])
 return value
m._key_for=key
private=ROOT/'.cache/fix695'/a.out.stem;private.mkdir(parents=True,exist_ok=False)
initial=None;input_hash=None;initial_regs=None
for event in m.events():
 if event.kind=='tick':
  if answered:
   assert not a.keeper;forced=False;break
  if not paused and event.minute>=2:m.pause();paused=True
  continue
 if event.kind!='decision':continue
 d=event.data;context=d['context']
 if context=='pause':
  if not sent:m.answer(request_substitution=True,edit_only=True);sent=True
  else:
   assert d['request_substitution'] is True and not d['substitutions_now'];acked=True;m.answer()
  continue
 if context=='substitution_opportunity':
  assert acked and not answered
  if not prepared:
   assert not d['keeper_unavailable'];assert m.m.stack_word(0)==0x80F0
   assert m.m.stack_word(2)&255==a.side;assert m.m.stack_word(4)&255==0
   before=m.m.read(0,0x110000);initial_regs=regs()
   ss=m.m.reg('ss')*16;sp=m.m.reg('sp');bp=m.m.reg('bp')
   if a.keeper:
    # Explicit mechanical flag injection only. Physiology remains unchanged;
    # no DS latch, player record, budget or live CPU register is fabricated.
    for address in (ss+((sp+4)&65535),ss+((bp-4)&65535)):
     old=m.m.read(address,1);m.m.write(address,b'\1');edits.append(dict(linear=address,before=old.hex(),after='01'))
   prepared_memory=m.m.read(0,0x110000)
   changed=[i for i,(x,y) in enumerate(zip(before,prepared_memory)) if x!=y]
   assert changed==sorted([e['linear'] for e in edits])
   assert regs()==initial_regs
   assert m.m.rd(S.SUBS_REQUEST,1)==1 and m.m.rd(S.SUBS_ALLOWED,1)==1
   input_hash=hashlib.sha256(prepared_memory).hexdigest();(private/'input.bin').write_bytes(prepared_memory)
   initial={'ticks':m.st['ticks'],'rng':[m.m.rd(0x7B62),m.m.rd(0x8336)],'squad':m._squad(7)}
   prepared=True
   if a.keeper:
    # Transparent coordinator refresh at the same held7FCF entry: no guest
    # instruction advances before the observer republishes the changed frame.
    m.st['waiting']=None
    continue
  assert d['keeper_unavailable'] is bool(a.keeper)
  assert d['timeout_polls']==(1000 if a.keeper else 400) and d['poll_ms']==10
  assert m.m.read(0,0x110000)==(private/'input.bin').read_bytes()
  assert regs()==initial_regs
  m.answer(opportunity=a.response);answered=True
  continue
 if context=='substitution' and answered:
  assert a.keeper and d['substitutions_now'];forced=True;break
 m.answer()
assert forced is bool(a.keeper) and answered and len(waits)==1
assert waits[0]['polls']==(1000 if a.keeper else 400)
assert waits[0]['key_polls']==(waits[0]['polls'] if a.response=='timeout' else 1)
assert waits[0]['delays']==(waits[0]['polls'] if a.response=='timeout' else 0)
if a.keeper:
 assert m.st['ticks']==initial['ticks'];assert m.m.rd(0xA977,1)==S.ESC
 assert m._squad(7)==initial['squad'];assert m.m.rd(S.SUBS_LEFT+m.side,1)==5
 assert [m.m.rd(0x7B62),m.m.rd(0x8336)]==initial['rng']
if a.response=='dismiss':assert [SITE_NOTICE,S.ESC] in keys
else:assert not [k for k in keys if k[0]==SITE_NOTICE]
memory=m.m.read(0,0x110000);(private/'after.bin').write_bytes(memory)
value={'engine':a.engine,'side':a.side,'keeper':bool(a.keeper),'response':a.response,'completed':True,
 'method':'real natural request to7FCF, then declared mechanical caller-flag control; not natural keeper injury/replacement',
 'injected_bytes':edits,'coordinator_refresh':'waiting cleared to republish same held-entry metadata after explicitly prepared flags' if a.keeper else None,
 'input_sha256':input_hash,'input_registers':initial_regs,'forced_menu':forced,'waits':waits,'keys':keys,
 'after_physical_sha256':hashlib.sha256(memory).hexdigest(),'after_registers':regs(),
 'rng':[m.m.rd(0x7B62),m.m.rd(0x8336)],'private_path':str(private),
 'sources_sha256':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'runtime/original_match/match.py',ROOT/'runtime/original_match/screens.py',Path(__file__)]}}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'engine':a.engine,'keeper':bool(a.keeper),'response':a.response,'forced_menu':forced,'waits':waits}),flush=True)
