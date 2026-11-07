"""#682: actual read-only snapshot/current record and legacy compatibility proof; no raw records published."""
import argparse,builtins,copy,gc,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--engine',choices=('original','port'),required=True)
p.add_argument('--knockout',action='store_true');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
assert not a.out.exists()
if a.engine=='port':
 assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
 original_import=builtins.__import__
 def deny(name,*args,**kwargs):
  if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
  return original_import(name,*args,**kwargs)
 builtins.__import__=deny
 try:__import__('unicorn')
 except ImportError:pass
 else:raise AssertionError('Unicorn denial not active')
else:assert sys.implementation.name=='cpython'
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
from original_match import Image,Fixture,Match
from original_match.image import PLAYERS_PTR,PLAYER_SIZE
import records,family
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
input_hash=hashlib.sha256(raw).hexdigest();assert input_hash=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def event_tuples(events):return [(e['kind'],e['minute'],e['score'],e['data']) for e in events]
def record_snapshot(match):
 base=match.m.far(PLAYERS_PTR)
 return [[word,match.m.read(base+PLAYER_SIZE*word,PLAYER_SIZE).hex()] for word in match._squad(7) if word]
def frozen(match):return [match.st['ticks'],match.m.rd(0x7B62),match.m.rd(0x8336),match.st['minute'],match.st['score'][:]]

def arm(enabled):
 image=Image.from_savestate(raw);base=image.far(PLAYERS_PTR)
 initial={w:bytes(image.memory[base+PLAYER_SIZE*w:base+PLAYER_SIZE*(w+1)]) for w in range(1,3061)}
 options={'live_players':True} if enabled else {}
 m=Match(image,Fixture(7,19,index=39 if a.knockout else 21,kind=200 if a.knockout else 1),managed=7,
         seed=None if a.knockout else 0x1234,substitutions=5,delay_byte=0,record_draws=True,engine=a.engine,
         ports=['all'] if a.engine=='port' else [],timeout_s=60,**options)
 assert m.opts.get('live_players',False)==enabled
 assert enabled or 'live_players' not in m.opts
 events=[];snapshots=[];private=[];paused=False;checkpointed=False;swapped=False;expect_edit=None
 started=time.monotonic()
 for e in m.events():
  events.append({'kind':e.kind,'minute':e.minute,'score':list(e.score),'data':copy.deepcopy(e.data)})
  if not a.knockout and e.kind=='minute' and e.minute>=2 and not paused:
   m.pause();paused=True
  if e.kind!='decision':continue
  d=e.data;context=d['context']
  guest_before=m.m.read(0,0x110000);before=frozen(m)
  actual=record_snapshot(m);private.append(actual)
  assert [w for w,_ in actual]==d['eleven']+d['bench']
  assert len(actual)==20 and len(set(w for w,_ in actual))==20
  if enabled:assert d.get('player_records')==actual
  else:assert 'player_records' not in d
  active={w:bytes.fromhex(r) for w,r in actual if w in d['eleven']}
  energy=sum(v[14]!=initial[w][14] for w,v in active.items())
  performance=sum(v[18:20]!=initial[w][18:20] for w,v in active.items())
  assert record_snapshot(m)==actual
  assert frozen(m)==before and m.m.read(0,0x110000)==guest_before
  check=False
  if not checkpointed and context in ('pause','extra_time'):
   saved=m.dump();loaded=Match.load(saved,timeout_s=60)
   assert loaded.opts.get('live_players',False)==enabled
   assert enabled or 'live_players' not in loaded.opts
   assert loaded.st['waiting']==m.st['waiting']
   assert loaded.m.read(0,0x110000)==guest_before
   assert frozen(loaded)==before
   if a.engine=='port':assert not hasattr(loaded.m,'_uc') and 'unicorn' not in sys.modules
   assert m.m.read(0,0x110000)==guest_before and frozen(m)==before
   del loaded;gc.collect();checkpointed=True;check=True
  if expect_edit is not None:
   off,on,previous=expect_edit
   assert d.get('edited') and frozen(m)==previous
   assert on in d['eleven'] and off in d['bench']
   assert off in dict(actual) and on in dict(actual)
   expect_edit=None
  row={'context':context,'half':d.get('half'),'edited':bool(d.get('edited')),'minute':e.minute,
       'records':len(actual),'record_sha256':digest(actual),'energy_changed_players':energy,
       'performance_changed_players':performance,'checkpoint_checked':check,'frozen':True}
  snapshots.append(row)
  print(json.dumps({'live':enabled,**row}),flush=True)
  if not a.knockout and not swapped and context in ('half_time','substitution') and d.get('substitutions_now',True):
   positions=dict(d['positions'])
   off=(d.get('injured') or d['eleven'][1:2])[0]
   on=next(w for w in d['bench'] if (positions[w]==0)==(positions[off]==0) and m._player(w,14)>0)
   expect_edit=(off,on,frozen(m));swapped=True
   m.answer(substitutions=[(off,on)],edit_only=True)
  else:m.answer()
 assert checkpointed
 contexts={row['context'] for row in snapshots}
 if a.knockout:assert {row['half'] for row in snapshots if row['context']=='extra_time'}=={1,2}
 else:assert {'pause','half_time'}<=contexts and swapped
 assert any(s['energy_changed_players'] for s in snapshots)
 assert any(s['performance_changed_players'] for s in snapshots)
 assert not [e for e in events if e['kind']=='substitution_requested']
 if a.engine=='port':assert not hasattr(m.m,'_uc') and 'unicorn' not in sys.modules
 result=copy.deepcopy(m.result());memory=m.m.read(0,0x110000)
 receipt={'live_players':enabled,'completed':True,'seconds':time.monotonic()-started,'snapshots':snapshots,
  'result_sha256':records.result_digest(result),'full_result_sha256':digest(result),'events_sha256':digest(events),
  'display_profile_events':family.display_events_digest(event_tuples(events)),
  'full_physical_memory_sha256':hashlib.sha256(memory).hexdigest(),
  'accepted_state_ranges':family.digest_memory(m,[],input_hash),'score':result['score'],
  'draws':result['draws'],'draws_digest':result['draws_digest']}
 return receipt,result,memory,events,private

legacy,old_result,old_memory,old_events,old_snapshots=arm(False)
live,new_result,new_memory,new_events,new_snapshots=arm(True)
assert old_result==new_result
assert old_memory==new_memory
assert old_snapshots==new_snapshots
expected=copy.deepcopy(old_events);index=0
for event in expected:
 if event['kind']=='decision':event['data']['player_records']=old_snapshots[index];index+=1
assert index==len(old_snapshots)
assert expected==new_events
receipt={'engine':a.engine,'knockout':a.knockout,'implementation':sys.implementation.name,'python':sys.version,
 'input_sha256':input_hash,'source_sha256':hashlib.sha256((ROOT/'runtime/original_match/match.py').read_bytes()).hexdigest(),
 'proof_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'legacy':legacy,'live':live,
 'same_full_result':True,'same_full_physical_memory':True,'same_live_records_at_all_stops':True,
 'events_equal_with_only_exact_independent_record_additions':True,'memory_mask':[],
 'existing_cross_backend_profile':'only full_time.data.screen_sha256 excluded; raw digests retained',
 'original_record_bytes_published':False}
with a.out.open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps({'engine':a.engine,'knockout':a.knockout,'completed':True,'seconds':legacy['seconds']+live['seconds']}),flush=True)
