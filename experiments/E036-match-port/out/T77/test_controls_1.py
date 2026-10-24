"""One immutable snapshot, fixed dispatch baseline and behavioral mutations."""
import hashlib,io,json,shutil,subprocess,sys,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent/'controls-1'
BASE='186f08cfc9f4ff5f30089b7662ff911a59e16032'
CONTROLS=[
 ('trial-strict','quick','B19D','# B1F4 jle','# B1F4 jle'),
]
# Replace exactly the selected listing block's effect, never the test.
MUTATIONS=[
 ('penalty-state','rare','6ECF','_write(mem,r,mem.DS,0x8324,8,1,','_write(mem,r,mem.DS,0x8324,8,0,'),
 ('keeper-role','rare','C24D','_write(mem,r,r.es,r.di + 6,8,0,','_write(mem,r,r.es,r.di + 6,8,1,'),
 ('wing-role','rare','C406','_write(mem,r,r.es,r.di + 6,8,2,','_write(mem,r,r.es,r.di + 6,8,3,'),
 ('height-boundary','rare','BEC7','if unsigned>=0 else','if unsigned>0 else'),
 ('back-surplus-tie','rare','C2A8','if unsigned<=0 else','if unsigned<0 else'),
 ('remove-no-sort','rare','C48D',"r=yield from _call(mem,r,'0791:230C',0,'0791:C506',False)",'pass'),
 ('ready-not-set','rare','72F2',"_write(mem,r,mem.DS,0x8323,8,1,","_write(mem,r,mem.DS,0x8323,8,0,"),
 ('arrival-state','rare','73BA',"_write(mem,r,r.es,r.di + 0x12,8,0,","_write(mem,r,r.es,r.di + 0x12,8,1,"),
 ('trial-equal-wins','quick','B19D','if signed<=0 else','if signed<0 else'),
 ('line-home-never','quick','0BC4','if z else 0x0DE0','if True else 0x0DE0'),
 ('energy-equal-decays','quick','D733','if signed<=0 else','if signed<0 else'),
]

def mutate(source,entry,old,new):
 import re
 m=re.search(r'def listing_[0-9A-F]+_'+entry+r'\(',source);assert m
 end=source.find('\n\n@PORTS.port',m.start()+1);end=len(source) if end<0 else end
 body=source[m.start():end];assert old in body,(entry,old)
 return source[:m.start()]+body.replace(old,new)+source[end:]

OUT.mkdir(exist_ok=False)
with tempfile.TemporaryDirectory(prefix='T77-frozen-') as name:
 frozen=Path(name);shutil.copytree(ROOT/'runtime',frozen/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (frozen/'tests').mkdir()
 for test in ('test_port_quick.py','test_port_rare.py','test_port_selection.py','test_port_menus.py','test_port_update.py'):
  shutil.copy(ROOT/'tests'/test,frozen/'tests'/test)
 hashes={str(p.relative_to(frozen)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(frozen.rglob('*')) if p.is_file()}
 (OUT/'source.json').write_text(json.dumps({'baseline':BASE,'frozen_sources':hashes},indent=2)+'\n')
 results=[]
 for label,module,entry,old,new in [('fixed-pre-task','quick',None,None,None)]+MUTATIONS:
  with tempfile.TemporaryDirectory(prefix='T77-control-') as name:
   tree=Path(name)
   if entry is None:
    archive=subprocess.check_output(['git','archive',BASE,'runtime'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(tree,filter='data')
   else:
    shutil.copytree(frozen/'runtime',tree/'runtime');p=tree/f'runtime/original_match/port/{module}.py';p.write_text(mutate(p.read_text(),entry,old,new))
   shutil.copytree(frozen/'tests',tree/'tests');(tree/'tests/__init__.py').write_text('')
   cmd=[sys.executable,'-B','-m','unittest','tests.test_port_quick','tests.test_port_rare']
   r=subprocess.run(cmd,cwd=tree,capture_output=True,text=True,timeout=30)
   (OUT/(label+'.log')).write_text(r.stdout+r.stderr)
   caught=r.returncode!=0 and ('AssertionError' in r.stderr or (entry is None and 'cannot import name' in r.stderr))
   results.append({'name':label,'caught':caught,'returncode':r.returncode,'command':cmd,'entry':entry,'original':old,'replacement':new})
   print(label,r.returncode,caught,flush=True)
 (OUT/'summary.json').write_text(json.dumps({'baseline':BASE,'sources':hashes,'results':results},indent=2)+'\n')
 raise SystemExit(0 if all(r['caught'] for r in results) else 1)
