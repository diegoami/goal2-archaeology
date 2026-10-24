"""Isolated behavior controls; never mutate the live implementation or fixtures."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'controls-2'
OUT.mkdir(exist_ok=False)
module='runtime/original_match/port/display.py';source=(ROOT/module).read_text()
mutations=[
 ('wrong-byte','toggle_sound_memory',"mem.wds8(0xA9FC,r.al,","mem.wds8(0xA9FD,r.al,"),
 ('inverted-toggle','toggle_sound_memory','r.al=int(disabled==0)','r.al=int(disabled!=0)'),
 ('missing-speaker-call','toggle_sound_memory',"r=yield from guest(mem,r,'214B:1E8D',ret='214B:1E61')",'pass'),
 ('wrong-compare-flags','toggle_sound_memory','r.arith(sub_flags(disabled,0,8))','r.arith(sub_flags(0,1,8))'),
 ('wrong-saved-frame','speaker_off_memory','r=Regs(mem);r.enter()','r=Regs(mem);r.enter();r.local16(0,0)'),
 ('wrong-input-result','speaker_off_memory','if not disabled:r.al=0','if not disabled:r.al=1'),
]
def mutate(fn,old,new):
 start=source.index('def '+fn+'(');end=source.index('\n\n@PORTS.port',start)
 body=source[start:end];assert body.count(old)==1,(fn,old)
 return source[:start]+body.replace(old,new)+source[end:]
results=[]
for label,fn,old,new in [('old-stubs',None,None,None)]+mutations:
 with tempfile.TemporaryDirectory(prefix='m4-408-control-') as name:
  tree=Path(name);shutil.copytree(ROOT/'runtime',tree/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  path=tree/module
  path.write_text(subprocess.check_output(['git','show','922fd8d8:'+module],cwd=ROOT,text=True) if fn is None else mutate(fn,old,new))
  (tree/'tests').mkdir();(tree/'tests/__init__.py').write_text('')
  shutil.copy(ROOT/'tests/test_port_display.py',tree/'tests/test_port_display.py')
  for rel in ('experiments/E036-match-port/out/T60/fuzz.py','experiments/E036-match-port/out/m4-408/differential_1.py'):
   dest=tree/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(ROOT/rel,dest)
  cache=tree/'.cache/dl';cache.mkdir(parents=True)
  image='e0afff6751747233-e006-1000-r0001.sav';(cache/image).symlink_to(ROOT/'.cache/dl'/image)
  cmd=[sys.executable,'-B','experiments/E036-match-port/out/m4-408/differential_1.py']
  r=subprocess.run(cmd,cwd=tree,capture_output=True,text=True,timeout=30)
  (OUT/(label+'.log')).write_text(r.stdout+r.stderr)
  measurement=tree/'experiments/E036-match-port/out/m4-408/differential-1.json'
  assert measurement.is_file(),r.stderr
  shutil.copy(measurement,OUT/(label+'.json'))
  caught=r.returncode!=0 and 'AssertionError' in r.stderr
  results.append({'control':label,'caught':caught,'exit':r.returncode,'function':fn,'old':old,'new':new})
  print(label,caught,flush=True)
receipt={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'baseline':'922fd8d8','results':results}
(OUT/'summary.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert all(r['caught'] for r in results)
