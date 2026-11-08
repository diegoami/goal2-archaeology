"""#695 bounded prepared8062entry control, not a natural keeper injury/replacement."""
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
from original_match.match import PITCH, PITCH_SIZE
from original_match.image import PLAYERS_PTR,PLAYER_SIZE
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

def prepare_caller(replay):
 global prepared,input_hash,initial_regs,initial
 if replay or prepared or not acked:return
 assert m.m.rd(S.SUBS_REQUEST,1)==1
 before=m.m.read(0,0x110000);initial_regs=regs()
 if a.keeper:
  slot=m.m.rd(0x0668+m.side,1)+1
  word=m.m.word_at(m.m.DS*16+PITCH+PITCH_SIZE*slot+13)
  assert word in m._squad(7)[:11] and m._player(word,6)==0
  address=m.m.far(PLAYERS_PTR)+PLAYER_SIZE*word+14
  old=m.m.read(address,1);assert old!=b'\0'
  m.m.write(address,b'\0')
  edits.append(dict(linear=address,before=old.hex(),after='00',meaning='prepared managed keeper energy byte'))
 prepared_memory=m.m.read(0,0x110000)
 assert [i for i,(x,y) in enumerate(zip(before,prepared_memory)) if x!=y]==[e['linear'] for e in edits]
 assert regs()==initial_regs
 input_hash=hashlib.sha256(prepared_memory).hexdigest();(private/'input.bin').write_bytes(prepared_memory)
 initial={'ticks':m.st['ticks'],'rng':[m.m.rd(0x7B62),m.m.rd(0x8336)],'squad':m._squad(7)}
 prepared=True
m.m.at('0791:8062',prepare_caller)
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
  assert prepared
  assert m.m.stack_word(2)&255==a.side and m.m.stack_word(4)&255==a.keeper
  assert d['keeper_unavailable'] is bool(a.keeper)
  assert d['timeout_polls']==(1000 if a.keeper else 400) and d['poll_ms']==10
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
 'method':'real natural request to actual8062entry, then single declared keeperenergy0 input before localcapture; not natural injury/replacement',
 'injected_bytes':edits,'coordinator_refresh':None,
 'input_sha256':input_hash,'input_registers':initial_regs,'forced_menu':forced,'waits':waits,'keys':keys,
 'after_physical_sha256':hashlib.sha256(memory).hexdigest(),'after_registers':regs(),
 'rng':[m.m.rd(0x7B62),m.m.rd(0x8336)],'private_path':str(private),
 'sources_sha256':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'runtime/original_match/match.py',ROOT/'runtime/original_match/screens.py',Path(__file__)]}}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'engine':a.engine,'keeper':bool(a.keeper),'response':a.response,'forced_menu':forced,'waits':waits}),flush=True)
