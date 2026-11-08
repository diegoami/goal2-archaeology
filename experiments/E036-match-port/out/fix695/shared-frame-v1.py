"""Prepared ABIcontrol: fresh machines at one identical original8062frame; no parent-coroutine restore claim."""
import argparse,builtins,copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--engine',choices=('original','port'),required=True)
p.add_argument('--frame',type=Path,required=True);p.add_argument('--keeper',type=int,choices=(0,1),required=True)
p.add_argument('--response',choices=('dismiss','timeout'),required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists()
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
from original_match import Match
from original_match.machine import Machine,REGS
from original_match.match import KEYPRESSED,KP_WAIT,SITE_NOTICE,PITCH,PITCH_SIZE
from original_match.image import PLAYERS_PTR,PLAYER_SIZE
from original_match import screens as S
frame=json.loads(a.frame.read_text());folder=Path(frame['private_path']);memory=bytearray((folder/'memory.bin').read_bytes())
assert hashlib.sha256(memory).hexdigest()==frame['input_memory_sha256']
meta_raw=(folder/'coordinator.json').read_bytes();assert hashlib.sha256(meta_raw).hexdigest()==frame['coordinator_sha256']
meta=json.loads(meta_raw);side=meta['side'];load=meta['load'];ds=(load+0x2581)*16

def word(address):return int.from_bytes(memory[address:address+2],'little')
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
edits=[]
if a.keeper:
 slot=memory[ds+0x0668+side]+1
 player=word(ds+PITCH+PITCH_SIZE*slot+13)
 base=word(ds+PLAYERS_PTR)+16*word(ds+PLAYERS_PTR+2);address=base+PLAYER_SIZE*player+14
 assert memory[base+PLAYER_SIZE*player+6]==0 and memory[address]>0
 edits=[dict(linear=address,before=f'{memory[address]:02x}',after='00',meaning='single prepared keeper energy byte')]
 memory[address]=0
assert memory[ds+S.SUBS_REQUEST]==1
m=object.__new__(Match)
for key in ['opts','st','inputs','side','image_sha256','fixture_ptr','end_lin','timeout_s']:setattr(m,key,copy.deepcopy(meta[key]))
m.engine=a.engine;m.image_header=(folder/'header.bin').read_bytes();m.image_tail=(folder/'tail.bin').read_bytes();m.tables=None
m._queue=[];m._menu=None;m._result=None;m._names=None
if a.engine=='port':
 from original_match.port.engine import PortMachine
 m.m=PortMachine(memory,load)
else:m.m=Machine(memory,load)
for key,value in meta['registers'].items():m.m.set_reg(key,value)
m._hooks();m._install_ports(['all'] if a.engine=='port' else None);m._install_proof(None)
assert {r:m.m.reg(r) for r in REGS}==meta['registers'] and m.m.read(0,0x110000)==bytes(memory)
ret=m.m.where(m.m.reg('cs'),m.m.stack_word(0));until=m.m.lin(ret)
keys=[];waits=[];events=[]
class Tap:
 def site_enter(self,linear,replay,**kw):
  if replay or kw.get('fired'):return
  if linear==m.m.lin('0791:CC2E') and m.m.stack_word(0)==0x8042:
   row=m._screen_raw()[3840:4000];text=bytes(row[::2]);phrase=b'HAS NO GOALKEEPER' if a.keeper else b'SUBSTITUTION OPPORTUNITY';start=text.find(phrase);assert start>=0
   waits.append(dict(polls=m.m.stack_word(2),key_polls=0,delays=0,row_sha256=hashlib.sha256(row).hexdigest(),phrase=phrase.decode(),phrase_column=start+1,phrase_attributes=list(row[2*start+1:2*(start+len(phrase)):2]),hint_attributes=list(row[131:160:2])))
  elif linear==m.m.lin(KEYPRESSED) and waits:
   site=m.m.where(m.m.stack_word(2),m.m.stack_word(0))
   if site==KP_WAIT and m.m.frame_word(m.m.reg('bp'),2)==0x8042:waits[-1]['key_polls']+=1
  elif linear==m.m.lin('214B:1E09') and waits:
   site=m.m.where(m.m.stack_word(2),m.m.stack_word(0))
   if site=='0791:CC65' and m.m.frame_word(m.m.reg('bp'),2)==0x8042:assert m.m.stack_word(4)==10;waits[-1]['delays']+=1
 def site_leave(self,*args,**kw):pass
m.m.site_tap=Tap();m.m.at('214B:1E09',lambda replay:None)
key=m._key_for

def observe(site):
 result=key(site)
 if result is not None:keys.append([site,result])
 return result
m._key_for=observe
initial_squad=m._squad(7);initial_ticks=m.st['ticks'];initial_budget=m.m.rd(S.SUBS_LEFT+side,1)
forced=False;answered=False;fresh=True
while True:
 if m._queue:
  event=m._queue.pop(0)
  if event.kind!='decision':continue
  m.st['waiting']=dict(event.data);d=event.data;events.append(dict(d))
  if d['context']=='substitution_opportunity':
   assert not answered and d['keeper_unavailable'] is bool(a.keeper)
   assert d['timeout_polls']==(1000 if a.keeper else 400) and d['poll_ms']==10
   assert m.m.stack_word(2)&255==side and m.m.stack_word(4)&255==a.keeper
   m.answer(opportunity=a.response);answered=True
  elif d['context']=='substitution':assert a.keeper and answered;forced=True;break
  else:raise AssertionError('unexpected bounded context')
 else:
  stopped=m.m.run(until,600,fresh=fresh);fresh=False
  if stopped is None:assert not a.keeper and answered;break
assert forced is bool(a.keeper) and len(waits)==1 and answered
assert waits[0]['key_polls']==(waits[0]['polls'] if a.response=='timeout' else 1)
assert waits[0]['delays']==(waits[0]['polls'] if a.response=='timeout' else 0)
assert m.st['ticks']==initial_ticks
assert sorted(m._squad(7))==sorted(initial_squad) and m.m.rd(S.SUBS_LEFT+side,1)==initial_budget
assert not m.st['log']['substitutions'] and not m.st['pending_subs']
if a.response=='dismiss':assert [SITE_NOTICE,S.ESC] in keys
else:assert not [k for k in keys if k[0]==SITE_NOTICE]
private=ROOT/'.cache/fix695'/a.out.stem;private.mkdir(parents=True,exist_ok=False)
(private/'input.bin').write_bytes(bytes(memory));after=m.m.read(0,0x110000);(private/'after.bin').write_bytes(after)
value={'engine':a.engine,'side':side,'keeper':bool(a.keeper),'response':a.response,'completed':True,
 'method':'bounded fresh-machine ABIcontrol at identical ORIGINAL8062entry; no active parent coroutine/save-resume or naturalinjury/replacement claim',
 'frame_receipt_sha256':hashlib.sha256(a.frame.read_bytes()).hexdigest(),'injected_bytes':edits,
 'input_sha256':hashlib.sha256(memory).hexdigest(),'input_registers':meta['registers'],'forced_menu':forced,
 'waits':waits,'keys':keys,'decisions_sha256':digest(events),'rng':[m.m.rd(0x7B62),m.m.rd(0x8336)],
 'after_physical_sha256':hashlib.sha256(after).hexdigest(),'after_registers':{r:m.m.reg(r) for r in REGS},
 'squad_before_sha256':digest(initial_squad),'squad_after_sha256':digest(m._squad(7)),
 'private_path':str(private),'sources_sha256':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'runtime/original_match/match.py',ROOT/'runtime/original_match/screens.py',Path(__file__)]}}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'completed':True,'engine':a.engine,'side':side,'keeper':bool(a.keeper),'response':a.response,'forced_menu':forced}),flush=True)
