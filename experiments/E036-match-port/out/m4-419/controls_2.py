"""In-memory omission and semantic mutants; no source files are changed."""
import io,json,sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import port
from original_match.port import _display_finals
from tests.test_port_display_finals import Finals
reg=port._module_registry('display');saved={a:reg.entries[a] for a in _display_finals.PORTS.entries}
source=(ROOT/'runtime/original_match/port/_display_finals.py').read_text()
def run():
 result=unittest.TextTestRunner(stream=io.StringIO()).run(unittest.defaultTestLoader.loadTestsFromTestCase(Finals))
 return {'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful()}
results=[]
try:
 baseline=run();assert baseline['passed'],baseline
 for address,entry in saved.items():
  reg.entries[address]=port.Entry(address,entry.ret,lambda m,v:None,'old-stub',stub='control: old removal')
  result=run();result.update(name='omit-'+address,caught=not result['passed']);results.append(result)
  reg.entries[address]=entry
 mutations=[
 ('leaderboard-attribute',"mem.DS,0xaab2,8,7,'1771:8881'","mem.DS,0xaab2,8,3,'1771:8881'"),
 ('restore-country',"_write(mem,r,r.ss,r.di - 8,16,r.ax,'1771:91C4')","pass"),
 ('odd-shift-carry','unsigned=-1 if _old & 1 else 0','unsigned=0 if _old & 1 else -1'),
 ('copy-short','r.ax=4000','r.ax=3900'),
 ('wrong-bracket',"_call(mem,r,'1771:937C'","_call(mem,r,'1771:91CE'"),
 ('skip-group-key',"r=yield from _call(mem,r,'214B:1560',3,'1771:91BE',True)","r=r"),
 ('skip-bracket-key',"r=yield from _call(mem,r,'214B:08DD',0,'1771:9567',True)","r=r"),
 ]
 for name,old,new in mutations:
  assert source.count(old)==1,(name,source.count(old))
  module=types.ModuleType('original_match.port._control_finals');module.__package__='original_match.port'
  exec(compile(source.replace(old,new),'<control:'+name+'>','exec'),module.__dict__)
  reg.entries.update(module.PORTS.entries)
  result=run();result.update(name=name,caught=not result['passed']);results.append(result)
  reg.entries.update(saved)
finally:reg.entries.update(saved)
receipt={'baseline':baseline,'controls':results,'all_caught':all(x['caught'] for x in results)}
with (OUT/'controls-2.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt),flush=True)
assert receipt['all_caught'],receipt
