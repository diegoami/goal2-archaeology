"""Read-only accepted696 overlay: no configure call or replacement return flags."""
import sys,json,hashlib,pickle,subprocess,time,types,importlib
from pathlib import Path
ROOT=Path('/home/diego/projects/m3-trackb/goal2-archaeology-3')
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools')]
ACCEPTED='70f38677edc351579ce59fb8bb2de2fdc9be9624'

def overlay(sources):
 import original_match
 for leaf,text in sources.items():
  name='original_match.'+leaf;mod=types.ModuleType(name);mod.__package__='original_match';mod.__file__=str(ROOT/'runtime/original_match'/f'{leaf}.py')
  sys.modules[name]=mod;exec(compile(text,mod.__file__,'exec'),mod.__dict__);setattr(original_match,leaf,mod)
 original_match.Match=sys.modules['original_match.match'].Match
 return original_match

def candidate(state,tables,sources):
 pkg=overlay(sources)
 from tests.test_route_sealed import _denials
 from tests.test_route_entry_config import _drive_entry
 from original_match.port.tables import from_record
 from original_match.machine import REGS,MEM_SIZE
 assert sys.implementation.name=='pypy';_denials()
 R=pkg.route;step=R.play_round(state,from_record(tables),R.DEFAULT_KEYS);m=step.match
 assert not hasattr(m,'configure_route_entry'),'baseline accidentally used new API'
 result=_drive_entry(m,False);seen=[];continuation=step.continuation
 continuation.m.at('000E:6F1D',lambda replay:None if replay else seen.append({k:continuation.m.reg(k) for k in REGS}))
 after=R.resume_round(continuation,m)
 assert seen==[result['returned']]
 result.update(final_state=after.state,all16_actual_transfer=True,entry_context=step.continuation.record)
 return result

def main():
 sources={leaf:subprocess.check_output(['git','show',f'{ACCEPTED}:runtime/original_match/{leaf}.py'],cwd=ROOT,text=True) for leaf in ('match','route')}
 pkg=overlay(sources)
 from tests.test_route_sealed import _fixtures
 from tests.test_route_entry_config import _drive_entry
 from original_match.machine import REGS,MEM_SIZE
 from original_match.image import Image
 from original_match.port.tables import to_record
 from port_test_runtime import call_in_pypy
 image=_fixtures().image();state=image.state(image.tables);collected=[]
 class Oracle(pkg.route.Route):
  def _match(self):
   context={k:self.m.reg(k) for k in REGS};g=self.m.far(0xA923);idx=self.m.word_at(g+0x26);fx=self.m.read(self.m.far(0xA92B)+8*(idx-1),8)
   fixture=pkg.Fixture(int.from_bytes(fx[4:6],'little'),int.from_bytes(fx[6:8],'little'),idx,fx[2])
   entry=Image(self.header+self.m.read(0,MEM_SIZE)+self.tail);entry.tables=self.tables
   m=pkg.Match(entry,fixture,engine='original',tail=False,timeout_s=600)
   assert not hasattr(m,'configure_route_entry') and not m.inputs and m.m.read(0,MEM_SIZE)==self.m.read(0,MEM_SIZE)
   for k,v in context.items():m.m.set_reg(k,v)
   result=_drive_entry(m,False);collected.append(result)
   self.m.write(0,result['memory'])
   for k,v in result['returned'].items():self.m.set_reg(k,v)
   assert {k:self.m.reg(k) for k in REGS}==result['returned']
 oracle=Oracle(image,entry='play_round',record_writes=False,match_entry=True);oracle.call()
 actual=call_in_pypy('t127_entry_baseline_v2','candidate',args=(state,to_record(image.tables),sources));expected=collected[0]
 old_expected,old_actual=pickle.loads((ROOT/'.cache/t127/20261108T130829Z-0/pair.pickle').read_bytes())
 for key in ('events','result','draws','returned','keys','memory'):
  assert expected[key]==old_expected[key],f'accepted-original default differs from T127 original reference: {key}'
 for key in ('events','result','draws','returned','keys','memory'):
  assert actual[key]==old_actual[key],f'accepted-default port differs from new default configured port: {key}'
 final=Image(oracle.header+oracle.m.read(0,MEM_SIZE)+oracle.tail);final.tables=image.tables
 assert actual['final_state']==final.state(image.tables)
 private=ROOT/'.cache/t127'/('baseline-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));private.mkdir(exist_ok=False)
 (private/'pair.pickle').write_bytes(pickle.dumps((expected,actual),protocol=4))
 row=dict(schema='t127-accepted-default-baseline/1',accepted_source=ACCEPTED,
  accepted_match_sha256=hashlib.sha256(sources['match'].encode()).hexdigest(),accepted_route_sha256=hashlib.sha256(sources['route'].encode()).hexdigest(),
  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),original_returned=expected['returned'],port_returned=actual['returned'],
  differences={k:[expected['returned'][k],actual['returned'][k]] for k in expected['returned'] if expected['returned'][k]!=actual['returned'][k]},
  accepted_original_identical_to_new_original=True,accepted_port_identical_to_new_configured_default=True,full_sealed_round_state_equal=True,
  actual_all16_transfer_equal=actual['all16_actual_transfer'],no_configure_api_or_call=True,
  raw_private_sha256=hashlib.sha256((private/'pair.pickle').read_bytes()).hexdigest())
 out=ROOT/'experiments/E040-route-fixture-writes/out/T127/accepted-default-baseline-70f38677-v2.json'
 with out.open('x')as f:json.dump(row,f,indent=2);f.write('\n')
 print(json.dumps(row,sort_keys=True),flush=True)
if __name__=='__main__':main()
