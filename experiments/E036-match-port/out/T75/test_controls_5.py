"""Fixed pre-task baseline and branch controls from one immutable source snapshot."""
import hashlib,io,json,shutil,subprocess,sys,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'controls-5'
BASE='bf650a337794ffd82e8e1471d45bfb6c5b753fd4'
P='runtime/original_match/port/selection.py'
CONTROLS=[
 ('squad-slot-off-by-one','selected_pointer','r.ax=r.di-2','r.ax=r.di'),
 ('pool-slot-off-by-one','selected_pointer','r.ax=r.di;r.dx=r.es','r.ax=r.di+2;r.dx=r.es'),
 ('selected-index-off-by-one','selected_index','r.ax=mem.ds16(0xC1B)','r.ax=mem.ds16(0xC1B)+1'),
 ('managed-country-byte-wrong','open_selection','r.ax=r.ax-0x80','r.ax=r.ax-0x81'),
 ('bench-template-wrong','substitution_instructions','0x4740','0x4720'),
 ('request-not-set','select_team',"mem.wds8(0x9B40,1,'0791:E6A9')","mem.wds8(0x9B40,0,'0791:E6A9')"),
 ('budget-zero-swap','select_team','if mem.ds8(0x9B41) and mem.ds8((r.di+0x9B3A)&M16)>0:','if mem.ds8(0x9B41) and mem.ds8((r.di+0x9B3A)&M16)>=0:'),
 ('escape-does-not-cancel','select_team','r.local8(-1,0);r.ax=0;r.local16(-11,0)','r.local8(-1,1);r.ax=0;r.local16(-11,0)'),
 ('empty-slot-is-allowed','swap_in_match','r.al=int(rw(mem,r,0)==0)','r.al=0'),
 ('same-block-is-allowed','swap_in_match','r.al=int(r.al==(r.dx&255))','r.al=0'),
 ('unavailable-flag-ignored','swap_in_match','flag=r.ax;r.push(flag)','flag=0;r.push(flag)'),
 ('sentoff-flag-ignored','swap_in_match','flag=r.ax;r.di=0xE019','flag=0;r.di=0xE019'),
 ('form-not-swapped','swap_in_match',"if variant!='form-not-swapped':","if False:"),
 ('marking-not-cleared','swap_in_match',"mem.wds16((r.di+0x9A3E)&M16,0,'0791:E22A')","mem.wds16((r.di+0x9A3E)&M16,1,'0791:E22A')"),
 ('request-not-cleared','swap_in_match',"mem.wds8(0x9B40,0,'0791:E295')","mem.wds8(0x9B40,1,'0791:E295')"),
 ('keeper-two-allowed','first_team_valid','int(ss8(mem,r,r.bp-16)>1)','int(ss8(mem,r,r.bp-16)>2)'),
 ('keeper-none-allowed','first_team_valid','int(ss8(mem,r,r.bp-16)==0)','0'),
 ('vacancy-allowed','first_team_valid','int(ss8(mem,r,r.bp-2)!=0)','0'),
 ('four-position-allowed','first_team_valid','int(ss8(mem,r,r.bp+r.di-16)>3)','int(ss8(mem,r,r.bp+r.di-16)>4)'),
 ('unavailable-prematch-allowed','first_team_valid','if not mem.ds8(0xC1F):','if False:'),
 ('parent-country-not-restored','first_team_valid','putp(r,parent(mem,r)-5,r.ax);r.al=ss8(mem,r,r.bp-1)','putp(r,parent(mem,r)-5,0);r.al=ss8(mem,r,r.bp-1)'),
 ('sentinel-empty-zero','sort_pool',"w8(mem,r,6,14,'1771:559F')","w8(mem,r,6,0,'1771:559F')"),
 ('sort-parallel-byte-not-swapped','pool_quicksort',"r=yield from guest(mem,r,'214B:007B',*left,*right,r.ax,ret='1771:54F3')","r.ax=0"),
]
def mutate(source,function,old,new):
 start=source.index('def '+function+'(');end=source.find('\n\ndef ',start+1);decorator=source.find('\n\n@',start+1)
 if decorator!=-1:end=min(end,decorator) if end!=-1 else decorator
 if end==-1:end=len(source)
 body=source[start:end];assert body.count(old)==1,(function,old,body.count(old))
 return source[:start]+body.replace(old,new)+source[end:]
OUT.mkdir(exist_ok=False)
with tempfile.TemporaryDirectory(prefix='T75-frozen-') as frozen:
 frozen=Path(frozen);shutil.copytree(ROOT/'runtime',frozen/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 (frozen/'tests').mkdir()
 for test in ('test_port_selection.py','test_port_menus.py','test_port_update.py'):shutil.copy(ROOT/'tests'/test,frozen/'tests'/test)
 hashes={str(p.relative_to(frozen)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(frozen.rglob('*')) if p.is_file()}
 (OUT/'source.json').write_text(json.dumps({'baseline':BASE,'frozen_sources':hashes},indent=2)+'\n')
 results=[]
 for name,function,old,new in [('fixed-pre-task-baseline',None,None,None)]+CONTROLS:
  with tempfile.TemporaryDirectory(prefix='T75-control-') as raw:
   tree=Path(raw)
   if function is None:
    archive=subprocess.check_output(['git','archive',BASE,'runtime'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(tree,filter='data')
   else:
    shutil.copytree(frozen/'runtime',tree/'runtime');path=tree/P;path.write_text(mutate(path.read_text(),function,old,new))
   shutil.copytree(frozen/'tests',tree/'tests');(tree/'tests/__init__.py').write_text('')
   try:
    r=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_port_selection'],cwd=tree,capture_output=True,text=True,timeout=20)
    (OUT/(name+'.log')).write_text(r.stdout+r.stderr)
    caught=r.returncode!=0 and ('AssertionError' in r.stderr or (function is None and 'cannot import name' in r.stderr));code=r.returncode
   except subprocess.TimeoutExpired as e:
    (OUT/(name+'.log')).write_bytes((e.stdout or b'')+(e.stderr or b'')+b'\nTIMEOUT20s\n');caught=True;code='timeout'
   results.append({'name':name,'caught':caught,'returncode':code,'function':function,'original':old,'replacement':new})
   print(name,code,caught,flush=True)
 (OUT/'summary.json').write_text(json.dumps({'baseline':BASE,'sources':hashes,'results':results},indent=2)+'\n')
 raise SystemExit(0 if all(r['caught'] for r in results) else 1)
