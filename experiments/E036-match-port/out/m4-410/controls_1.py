"""Prove the old C24D test misses both review mutants and the new test catches them."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
BASE='ba67abd14521e9d0d5af6d635150bf0df830af89'
module='runtime/original_match/port/rare.py';source=(ROOT/module).read_text()
start=source.index('def listing_0791_C24D(');end=source.index('\n\n@PORTS.port',start)
body=source[start:end]
mutations=[('all-available','# C29A jmp 0xc2a2\n            pc=0xC2A2','# C29A jmp 0xc2a2\n            pc=0xC29C'),
           ('stops-before-slot11','; _b=11','; _b=10'),
           ('starts-at-slot3',"16,2,'0791:C253'","16,3,'0791:C253'"),
           ('includes-slot1',"16,2,'0791:C253'","16,1,'0791:C253'")]
legacy=subprocess.check_output(['git','show',BASE+':tests/test_port_rare.py'],cwd=ROOT,text=True)
current=(ROOT/'tests/test_port_rare.py').read_text();results=[]
for name,old,new in [('correct',None,None)]+mutations:
 if old is not None:assert body.count(old)==1,(name,old)
 mutated=source if old is None else source[:start]+body.replace(old,new)+source[end:]
 for version,test in [('legacy',legacy),('new',current)]:
  with tempfile.TemporaryDirectory(prefix='m4-410-') as d:
   tree=Path(d);shutil.copytree(ROOT/'runtime',tree/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
   (tree/module).write_text(mutated);(tree/'tests').mkdir();(tree/'tests/__init__.py').write_text('')
   for f in ('test_port_quick.py','test_port_selection.py','test_port_menus.py','test_port_update.py'):shutil.copy(ROOT/'tests'/f,tree/'tests'/f)
   (tree/'tests/test_port_rare.py').write_text(test)
   command=[sys.executable,'-B','-m','unittest','tests.test_port_rare']
   r=subprocess.run(command,cwd=tree,capture_output=True,text=True,timeout=30)
   with (OUT/f'{name}-{version}-1.log').open('x') as f:f.write(r.stdout+r.stderr)
   assertion='AssertionError' in r.stderr
   if old is None:assert r.returncode==0,r.stderr
   elif version=='new':assert r.returncode!=0 and assertion,r.stderr
   elif name in ('all-available','stops-before-slot11'):assert r.returncode==0,r.stderr
   results.append({'control':name,'tests':version,'exit':r.returncode,'assertion_failure':assertion})
   print(name,version,r.returncode,flush=True)
with (OUT/'controls-1.json').open('x') as f:json.dump({'baseline':BASE,'runtime_sha256':hashlib.sha256(source.encode()).hexdigest(),'new_test_sha256':hashlib.sha256(current.encode()).hexdigest(),'results':results},f,indent=2);f.write('\n')
print('PASS: both review mutants survive legacy tests; all four scan/order mutants fail new assertions; correct code passes')
