"""#695 exact legacy queued-pair compatibility, default vs false and pre-change runtime."""
import argparse,builtins,copy,hashlib,json,sys,time
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('--engine',choices=('original','port'),required=True)
p.add_argument('--out',type=Path,required=True);p.add_argument('--runtime',type=Path)
a=p.parse_args();assert not a.out.exists()
if a.engine=='port':
 assert sys.implementation.name=='pypy'
 original_import=builtins.__import__
 def deny(name,*args,**kw):
  if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
  return original_import(name,*args,**kw)
 builtins.__import__=deny
 try:__import__('unicorn')
 except ImportError:pass
 else:raise AssertionError('denial failed')
runtime=a.runtime or ROOT/'runtime';sys.path.insert(0,str(runtime))
from original_match import Image,Match,Fixture
raw=(ROOT/'.cache/dl/e0afff6751747233-e006-1000-r0001.sav').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def run(explicit):
 opts={'substitution_control':False} if explicit else {}
 m=Match(Image.from_savestate(raw),Fixture(7,19,index=21),managed=7,seed=0x1234,substitutions=5,
  ticks=True,record_draws=True,delay_byte=0,engine=a.engine,timeout_s=600,**opts)
 assert 'substitution_control' not in m.opts
 paused=asked=seen=False;events=[];pair=None
 for event in m.events():
  events.append(asdict(event))
  if event.kind=='tick' and event.minute>=2 and not paused:m.pause();paused=True
  if event.kind!='decision':continue
  d=event.data;context=d['context']
  assert 'request_substitution' not in d and context!='substitution_opportunity'
  if context=='pause' and not asked:
   positions=dict(d['positions']);off=next(w for w in d['eleven'] if positions[w]>=2)
   on=next(w for w in d['bench'] if positions[w]>=2)
   pair=[off,on];m.answer(substitutions=[pair]);asked=True
  else:
   if context=='substitution' and d.get('requested')==[pair]:seen=True
   m.answer()
 assert asked and seen and pair is not None
 result=copy.deepcopy(m.result());memory=m.m.read(0,0x110000)
 assert any(s['off']==pair[0] and s['on']==pair[1] for s in result['substitutions'])
 return dict(result=result,events=events,memory=memory)
started=time.monotonic();first=run(False)
if a.runtime is None:
 second=run(True)
 assert first==second,'default vs explicitfalse changed full result/events/RNG/physical memory'
else:second=None
private=ROOT/'.cache/fix695'/a.out.stem;private.mkdir(parents=True,exist_ok=False)
(private/'memory.bin').write_bytes(first['memory'])
(private/'run.json').write_text(json.dumps({'result':first['result'],'events':first['events']},sort_keys=True))
value={'engine':a.engine,'runtime':str(runtime),'seconds':time.monotonic()-started,'completed':True,
 'current_source_default_false_equal':second is not None,'legacy_queued_pair_made':True,
 'raw_result_sha256':digest(first['result']),'events_raw_sha256':digest(first['events']),
 'full_physical_memory_sha256':hashlib.sha256(first['memory']).hexdigest(),
 'private_path':str(private),'private_run_sha256':hashlib.sha256((private/'run.json').read_bytes()).hexdigest(),
 'sources_sha256':{str(q):hashlib.sha256(q.read_bytes()).hexdigest() for q in [runtime/'original_match/match.py',runtime/'original_match/screens.py',Path(__file__)]}}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps({'engine':a.engine,'completed':True,'seconds':value['seconds']}),flush=True)
