"""#695 natural original/port request lifecycle proof. Raw guest bytes stay ignored."""
import argparse,builtins,copy,hashlib,json,sys,time
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--engine',choices=('original','port'),required=True)
p.add_argument('--case',choices=('request','cancel','zero','dismiss','timeout'),required=True)
p.add_argument('--out',type=Path,required=True);p.add_argument('--checkpoint',action='store_true');a=p.parse_args()
assert not a.out.exists(),'immutable output exists'
if a.engine=='port':
 assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
 original_import=builtins.__import__
 def deny(name,*args,**kwargs):
  if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
  return original_import(name,*args,**kwargs)
 builtins.__import__=deny
 try:__import__('unicorn')
 except ImportError:pass
 else:raise AssertionError('denial inactive')
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
from original_match import Image,Match,Fixture
from original_match import screens as S
from original_match.match import KEYPRESSED,READKEY,KP_WAIT,SITE_SELECT
from original_match.image import PLAYERS_PTR,PLAYER_SIZE
import family,records
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
input_hash=hashlib.sha256(raw).hexdigest();assert input_hash=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
image=Image.from_savestate(raw)
m=Match(image,Fixture(7,19,index=21),managed=7,seed=0x1234,substitutions=0 if a.case=='zero' else 5,
 ticks=True,record_draws=True,delay_byte=0,engine=a.engine,substitution_control=True,timeout_s=600)
started=time.monotonic();events=[];keys=[];waits=[];boundaries=[];expected=None;operation=0;paused=False;resumed=False
request_ops=[True,False,False] if a.case=='cancel' else [True,True,False] if a.case=='zero' else [True,True]
request_done=False;target_notice=False;made=False;edit_expected=None;pending_response=None;cancel_pending=False;cancel_sent=False;checkpointed=False

class Tap:
 def site_enter(self,linear,replay):
  if replay:return
  if linear==m.m.lin('0791:CC2E') and m.m.stack_word(0)==0x8042:
   waits.append(dict(polls=m.m.stack_word(2),key_polls=0,delays=0,delay_value=10))
  elif linear==m.m.lin(KEYPRESSED) and waits:
   site=m.m.where(m.m.stack_word(2),m.m.stack_word(0))
   if site==KP_WAIT and m.m.frame_word(m.m.reg('bp'),2)==0x8042:waits[-1]['key_polls']+=1
  elif linear==m.m.lin('214B:1E09') and waits:
   site=m.m.where(m.m.stack_word(2),m.m.stack_word(0))
   if site=='0791:CC65':
    assert m.m.stack_word(4)==10;waits[-1]['delays']+=1
 def site_leave(self,linear,stopped):pass

def attach():
 previous=m._key_for
 def key(site):
  value=previous(site)
  if value is not None:keys.append([site,value])
  return value
 m._key_for=key
 m.m.site_tap=Tap()
 # Keep the original wait entry observable even if no kit hook ever mutates it.
 m.m.at('214B:1E09',lambda replay:None)
attach()
def frozen():
 base=m.m.far(PLAYERS_PTR);squad=m._squad(7)
 return dict(ticks=m.st['ticks'],minute=m.st['minute'],score=m.st['score'][:],
  rng=[m.m.rd(0x7B62),m.m.rd(0x8336)],draws=len(m.st['draws']),
  squad=squad,budget=m.m.rd(S.SUBS_LEFT+m.side,1),
  players=digest([m.m.read(base+PLAYER_SIZE*w,PLAYER_SIZE).hex() for w in squad]))
def boundary(event):
 d=event.data
 assert d['request_substitution'] is bool(m.m.rd(S.SUBS_REQUEST,1))
 if d['context'] in ('pause','substitution'):
  assert d['substitutions_now'] is bool(m.m.rd(S.SUBS_ALLOWED,1))
 value=dict(context=d['context'],minute=event.minute,request=d['request_substitution'],
  allowed=bool(m.m.rd(S.SUBS_ALLOWED,1)),squad_sha256=digest(d['eleven']+d['bench']),
  budget=d['substitutions_left'],ticks=m.st['ticks'],rng=[m.m.rd(0x7B62),m.m.rd(0x8336)],
  edited=bool(d.get('edited')),keeper=d.get('keeper_unavailable'),timeout_polls=d.get('timeout_polls'))
 boundaries.append(value);print(json.dumps({'boundary':value}),flush=True)

def answer_request(desired):
 global expected
 expected=(frozen(),desired,len([k for k in keys if k==[SITE_SELECT,S.ENTER]]))
 m.answer(request_substitution=desired,edit_only=True)

for event in m.events():
 events.append(asdict(event))
 if event.kind=='tick':
  if pending_response is not None:
   assert pending_response[0] in ('dismiss','timeout') and not pending_response[1]
   pending_response=None
  if not paused and event.minute>=2:
   m.pause();paused=True
  elif cancel_pending and not cancel_sent:
   m.pause();cancel_sent=True
  continue
 if event.kind!='decision':continue
 d=event.data;context=d['context'];boundary(event)
 if context=='pause':
  if expected is not None:
   before,desired,enters=expected;expected=None
   assert frozen()==before,'request/cancel advanced clock/RNG/players/budget'
   actual=desired if before['budget'] or not desired else False
   assert d['request_substitution'] is actual
   assert m.st['pending_subs']==[],'standalone request fabricated a pair'
   actual_enters=len([k for k in keys if k==[SITE_SELECT,S.ENTER]])-enters
   if operation and request_ops[operation-1]==desired and operation>1 and request_ops[operation-2]==desired and before['budget']:
    assert actual_enters==0,'repeated desired state toggled the original request'
   if a.checkpoint and not checkpointed:
    before_memory=m.m.read(0,0x110000);saved=m.save();loaded=Match.load(saved)
    assert loaded.opts.get('substitution_control') is True
    assert loaded.st['waiting']==m.st['waiting'];assert loaded.m.read(0,0x110000)==before_memory
    m=loaded;attach();checkpointed=True
  if cancel_sent:
   if d['request_substitution']:
    answer_request(False)
   else:
    cancel_pending=False;m.answer()
   continue
  if operation<len(request_ops):
   desired=request_ops[operation];operation+=1;answer_request(desired)
  else:
   request_done=True;resumed=True;m.answer()
  continue
 if context=='substitution_opportunity':
  keeper=d['keeper_unavailable'];assert d['timeout_polls']==(1000 if keeper else 400);assert d['poll_ms']==10
  if request_done and resumed and not target_notice and a.case in ('request','dismiss','timeout'):
   assert d['request_substitution'];assert not keeper,'target must be the natural independent request, not keeper injury'
   assert event.minute<45
   target_notice=True
   response='accept' if a.case=='request' else a.case
   pending_response=(response,keeper)
   if response!='accept':cancel_pending=True
   m.answer(opportunity=response)
  else:
   # Actual unrelated injury opportunities: timeout is a declared literal no-key.
   pending_response=('timeout',keeper);m.answer(opportunity='timeout')
  continue
 if context=='substitution':
  if pending_response is not None:
   response,keeper=pending_response;pending_response=None
   assert response=='accept' or keeper,'ordinary Esc/timeout incorrectly entered the menu'
  if edit_expected is not None:
   off,on,old=edit_expected;edit_expected=None
   assert d['edited'];assert on in d['eleven'] and off in d['bench']
   assert d['substitutions_left']==old['budget']-1
   assert m.st['ticks']==old['ticks'] and m.st['minute']==old['minute']
   assert not d['request_substitution'];made=True;m.answer();continue
  if a.case=='request' and target_notice and not made:
   positions=dict(d['positions']);off=next(w for w in d['eleven'] if positions[w]>=2 and w not in d['injured'])
   on=next(w for w in d['bench'] if positions[w]>=2 and m._player(w,14)>0)
   edit_expected=(off,on,frozen());m.answer(substitutions=[(off,on)],edit_only=True)
  else:m.answer()
  continue
 m.answer()

assert paused and request_done
if a.case=='request':assert target_notice and made
if a.case in ('dismiss','timeout'):assert target_notice and cancel_sent and not cancel_pending
if a.checkpoint:assert checkpointed
if a.engine=='port':assert not hasattr(m.m,'_uc') and 'unicorn' not in sys.modules
result=copy.deepcopy(m.result());memory=m.m.read(0,0x110000)
private=ROOT/'.cache/fix695'/a.out.stem;private.mkdir(parents=True,exist_ok=False)
(private/'memory.bin').write_bytes(memory)
(private/'run.json').write_text(json.dumps({'events':events,'result':result,'keys':keys,'boundaries':boundaries,'waits':waits},sort_keys=True))
receipt={'engine':a.engine,'case':a.case,'checkpoint':a.checkpoint,'completed':True,'seconds':time.monotonic()-started,
 'python':sys.version,'implementation':sys.implementation.name,'input_sha256':input_hash,
 'sources_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'runtime/original_match/match.py',ROOT/'runtime/original_match/screens.py',Path(__file__)]},
 'result_sha256':records.result_digest(result),'raw_result_sha256':digest(result),'events_raw_sha256':digest(events),
 'events_display_profile':family.display_events_digest([(e['kind'],e['minute'],e['score'],e['data']) for e in events]),
 'full_physical_memory_sha256':hashlib.sha256(memory).hexdigest(),'accepted_state_ranges':family.digest_memory(m,[],input_hash),
 'draws_digest':result['draws_digest'],'keys_sha256':digest(keys),'keys':keys,'boundaries':boundaries,'waits':waits,
 'private_path':str(private),'private_run_sha256':hashlib.sha256((private/'run.json').read_bytes()).hexdigest(),
 'mask':[],'cross_backend_boundary':'existing strict display-profile events + records.result_digest + all unmasked DS/records.RANGES; raw whole-memory hashes retained',
 'raw_original_bytes_published':False}
with a.out.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'completed':True,'engine':a.engine,'case':a.case,'seconds':receipt['seconds']}),flush=True)
