"""T76 fixed pre-task controls against one frozen runtime/test snapshot."""
import hashlib,io,json,shutil,subprocess,sys,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'controls-1'
BASE='411fdefa0287f984e5c0efc1fb1c585263c67690'
P='runtime/original_match/port/takers.py'
CONTROLS=[
 ('poll-bound','wait_or_key','r.ax<=word(mem,r,-4)','r.ax<word(mem,r,-4)'),
 ('delay-argument','wait_or_key','r.ax=10;','r.ax=11;'),
 ('speed-floor','raise_speed',"w8(mem,r,0x3F,2,'0C39')","w8(mem,r,0x3F,1,'0C39')"),
 ('question-yes','ask_do_you_want',"r.al==ord('Y')","r.al==ord('N')"),
 ('fallback-not-called','choose_captain_or_taker',"if bad:r=yield from computer_taker(mem,r,'CD59')","if False:r=yield from computer_taker(mem,r,'CD59')"),
 ('fallback-outside-eleven','choose_captain_or_taker','bad=r.ax>11','bad=r.ax>12'),
 ('captain-wrong-table','choose_captain_or_taker',"mem.wds16((r.di+0x9978)&M16,r.cx,'0791:CD05')","mem.wds16((r.di+0x997A)&M16,r.cx,'0791:CD05')"),
 ('enter-keeps-current','choose_captain_or_taker',"if variant!='enter-keeps-current':r.local16(-7,r.ax)","if False:r.local16(-7,r.ax)"),
 ('role-skill-offset','computer_taker','r.di+0x764','r.di+0x765'),
 ('escape-keeps-last','managed_order',"r._put(off,bytes([(ss8(mem,r,off)-1)&255]))","r._put(off,bytes([ss8(mem,r,off)]))"),
 ('no-down-pushback','managed_order',"if variant!='order-no-pushback':","if False:"),
 ('order-slot-offset','order_char','r.ax=r.ax+index','r.ax=r.ax+index+1'),
]

def mutate(source,function,old,new):
 start=source.index('def '+function+'(');end=source.find('\n\ndef ',start+1);decorator=source.find('\n\n@',start+1)
 if decorator!=-1:end=min(end,decorator) if end!=-1 else decorator
 if end==-1:end=len(source)
 body=source[start:end];assert body.count(old)>=1,(function,old)
 return source[:start]+body.replace(old,new)+source[end:]

OUT.mkdir(exist_ok=False)
with tempfile.TemporaryDirectory(prefix='T76-frozen-') as name:
 frozen=Path(name);shutil.copytree(ROOT/'runtime',frozen/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (frozen/'tests').mkdir()
 for test in ('test_port_takers.py','test_port_selection.py','test_port_menus.py','test_port_update.py','test_original_match.py'):
  shutil.copy(ROOT/'tests'/test,frozen/'tests'/test)
 hashes={str(p.relative_to(frozen)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(frozen.rglob('*')) if p.is_file()}
 (OUT/'source.json').write_text(json.dumps({'baseline':BASE,'frozen_sources':hashes},indent=2)+'\n')
 results=[]
 for label,function,old,new in [('fixed-pre-task-port',None,None,None),('fixed-pre-task-original',None,None,None)]+CONTROLS:
  with tempfile.TemporaryDirectory(prefix='T76-control-') as name:
   tree=Path(name)
   if function is None:
    archive=subprocess.check_output(['git','archive',BASE,'runtime'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(tree,filter='data')
   else:
    shutil.copytree(frozen/'runtime',tree/'runtime');p=tree/P;p.write_text(mutate(p.read_text(),function,old,new))
   shutil.copytree(frozen/'tests',tree/'tests');(tree/'tests/__init__.py').write_text('')
   target='tests.test_original_match.SetPieceTests' if label=='fixed-pre-task-original' else 'tests.test_port_takers'
   if target.endswith('SetPieceTests'):
    (tree/'.cache').mkdir();(tree/'.cache/dl').symlink_to(ROOT/'.cache/dl',target_is_directory=True)
   command=[sys.executable,'-B','-m','unittest',target]
   try:
    r=subprocess.run(command,cwd=tree,capture_output=True,text=True,timeout=30)
    (OUT/(label+'.log')).write_text(r.stdout+r.stderr)
    caught=r.returncode!=0 and ('AssertionError' in r.stderr or (function is None and ('cannot import name' in r.stderr or "unexpected keyword argument 'set_piece'" in r.stderr)))
    code=r.returncode
   except subprocess.TimeoutExpired as e:
    (OUT/(label+'.log')).write_bytes((e.stdout or b'')+(e.stderr or b'')+b'\nTIMEOUT30s\n');caught=True;code='timeout'
   results.append({'name':label,'caught':caught,'returncode':code,'command':command,'function':function,'original':old,'replacement':new})
   print(label,code,caught,flush=True)
 (OUT/'summary.json').write_text(json.dumps({'baseline':BASE,'sources':hashes,'results':results},indent=2)+'\n')
 raise SystemExit(0 if all(r['caught'] for r in results) else 1)
