"""#695 exact paired measurements, including private full outputs (not republished)."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];FOLDER=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists()
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def load(name):
 value=json.loads((FOLDER/name).read_text());assert value['completed']
 for name,expected in value.get('sources_sha256',{}).items():
  path=Path(name);path=path if path.is_absolute() else ROOT/path
  assert hashlib.sha256(path.read_bytes()).hexdigest()==expected, str(path)
 return value

def private(value):
 folder=Path(value['private_path']);raw=(folder/'run.json').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==value['private_run_sha256']
 result=json.loads(raw);memory=(folder/'memory.bin').read_bytes()
 assert hashlib.sha256(memory).hexdigest()==value['full_physical_memory_sha256']
 return result,memory

pairs=[]
for case in ('request','cancel','zero','dismiss','timeout','composite'):
 version=1 if case=='composite' else 2
 x=load('original-'+case+'-v'+str(version)+'.json');y=load('port-'+case+'-v'+str(version)+'.json')
 for field in ('result_sha256','events_raw_sha256','events_display_profile','accepted_state_ranges','keys','boundaries','waits','draws_digest','full_physical_memory_sha256'):
  assert x[field]==y[field],(case,field)
 rx,mx=private(x);ry,my=private(y)
 assert mx==my and rx['events']==ry['events'] and rx['keys']==ry['keys'] and rx['waits']==ry['waits']
 differences=sorted(k for k in set(rx['result'])|set(ry['result']) if rx['result'].get(k)!=ry['result'].get(k))
 assert differences==['ports'],(case,differences)
 assert {k:v for k,v in rx['result'].items() if k!='ports'}=={k:v for k,v in ry['result'].items() if k!='ports'}
 if case in ('cancel','zero'):
  assert not x['waits'] and not any(b['context']=='substitution_opportunity' for b in x['boundaries'])
  assert all(b['budget']==(0 if case=='zero' else 5) for b in x['boundaries'])
 if case in ('dismiss','timeout'):
  opportunity=next(i for i,b in enumerate(x['boundaries']) if b['context']=='substitution_opportunity')
  assert x['boundaries'][opportunity+1]['context']=='pause'
  assert x['boundaries'][opportunity+1]['request'] is True
  assert x['boundaries'][opportunity+2]['request'] is False
  assert x['waits'][0]['key_polls']==(400 if case=='timeout' else 1)
  assert x['waits'][0]['delays']==(400 if case=='timeout' else 0)
 if case=='composite':
  assert x['live_players'] is y['live_players'] is True
  assert x['live_records_per_decision']==y['live_records_per_decision']==20
  assert x['live_record_decisions']==y['live_record_decisions']
 pairs.append(dict(case=case,full_physical_memory_equal=True,whole_events_equal=True,
   full_result_equal_except_execution_metadata=differences,keys_boundaries_wait_counters_equal=True,
   actual_record_decisions=x.get('live_record_decisions'),record_count=20*x.get('live_record_decisions',0)))
replays=[]
for engine in ('original','port'):
 x=load(engine+'-request-v2.json');y=load(engine+'-request-resume-v2.json')
 for field in ('raw_result_sha256','events_raw_sha256','full_physical_memory_sha256','keys','boundaries','waits'):
  assert x[field]==y[field],(engine,field)
 rx,mx=private(x);ry,my=private(y);assert rx==ry and mx==my
 replays.append(dict(engine=engine,full_result_events_memory_keys_boundaries_waits_equal=True))
legacy=[]
for engine in ('original','port'):
 x=load(engine+'-legacy-v1.json');y=load(engine+'-baseline-v1.json')
 assert x['current_source_default_false_equal']
 for field in ('raw_result_sha256','events_raw_sha256','full_physical_memory_sha256'):
  assert x[field]==y[field],(engine,field)
 rx,mx=private(x);ry,my=private(y);assert rx==ry and mx==my
 legacy.append(dict(engine=engine,legacy_queued_pair_made=True,default_false_prechange_full_result_events_memory_equal=True))
controls=[]
for stem,version in [('keeper-timeout',3),('side1-timeout',1)]:
 x=load('original-'+stem+'-v'+str(version)+'.json');y=load('port-'+stem+'-v'+str(version)+'.json')
 for field in ('input_sha256','input_registers','injected_bytes','forced_menu','waits','keys','rng','after_physical_sha256','after_registers'):
  assert x[field]==y[field],(stem,field)
 assert x['forced_menu'] is (stem=='keeper-timeout')
 assert x['waits'][0]['key_polls']==(1000 if stem=='keeper-timeout' else 400)
 assert x['waits'][0]['delays']==x['waits'][0]['key_polls']
 for value in (x,y):
  assert hashlib.sha256((Path(value['private_path'])/'input.bin').read_bytes()).hexdigest()==value['input_sha256']
  assert hashlib.sha256((Path(value['private_path'])/'after.bin').read_bytes()).hexdigest()==value['after_physical_sha256']
 controls.append(dict(control=stem,full_input_memory_regs_keys_rng_output_memory_regs_equal=True,
  forced_menu=x['forced_menu'],polls=x['waits'][0]['polls'],injected_bytes=x['injected_bytes']))
value={'natural_pairs':pairs,'within_backend_checkpoint_replays':replays,'legacy_prechange_pairs':legacy,
 'prepared_controls':controls,'events_exclusions':[],'memory_mask':[],
 'cross_backend_result_execution_metadata_only':['ports'],'raw_original_bytes_republished':False,
 'comparator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
with a.out.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print('PASS:6 fullnaturalpairs,2 exactcheckpointreplays,2 exactprechangelegacypairs,2 boundedcontrols; noevent/memory exclusions')
