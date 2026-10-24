"""Review mutants pass old menu tests and fail the stronger branch assertions."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
BASE='46a6b13f9c16337b54b2f136c4444e29a9f4b680'
module='runtime/original_match/port/menus.py';source=(ROOT/module).read_text()
mutations=[
 ('wrong-pitch-pointer','match_key_poll',"'214B:1D6F',mem.DS,0x66A,","'214B:1D6F',mem.DS,0x66B,"),
 ('pitch-upper-five','match_key_poll','r.al=4;hi=r.ax','r.al=5;hi=r.ax'),
 ('pitch-directions-swapped','match_key_poll','int(mem.ds8(0xA976)==0xB1)','int(mem.ds8(0xA976)==0xAC)'),
 ('pitch-refresh-far','match_key_poll',"'0691',ret='944B',far=False","'0691',ret='944B',far=True"),
 ('drop-help-save','match_key_poll',"r=yield from guest(mem,r,'23E4:025D',*source,r.es,r.di,r.ax,ret='947D')",'pass'),
 ('drop-help-restore','match_key_poll',"r=yield from guest(mem,r,'23E4:025D',*source,r.es,r.di,r.ax,ret='9497')",'pass'),
 ('help-copy-short','match_key_poll','r.ax=4000','r.ax=3999'),
 ('drop-prompt-copy','ask_yes_no',"r=yield from _g(mem,r,'23E4:0644',*source,r.ss,line,r.ax,ret='0580')",'pass'),
 ('drop-prompt-save','ask_yes_no',"r=yield from _g(mem,r,'0625',ret='0584')",'pass'),
 ('drop-expression-store','ask_yes_no',"r=yield from _g(mem,r,'23E4:062A',r.ss,r.di,ret='0597')",'pass'),
 ('drop-expression-suffix','ask_yes_no',"r=yield from _g(mem,r,'23E4:06B7',mem.seg(0x214B),r.di,ret='05A1')",'pass'),
 ('drop-prompt-draw','ask_yes_no',"r=yield from _g(mem,r,'0350',row,r.ss,expression,mem.DS,r.di,ret='05AA')",'pass'),
 ('drop-menu-guard','in_match_menu',"r=yield from guest(mem,r,'214B:1765',flag,mem.seg(0x0791),r.di,ret='F046')",'pass'),
]
legacy=subprocess.check_output(['git','show',BASE+':tests/test_port_menus.py'],cwd=ROOT,text=True)
current=(ROOT/'tests/test_port_menus.py').read_text();results=[]
for label,fn,old,new in [('correct',None,None,None)]+mutations:
 if fn is None:mutated=source
 else:
  start=source.index('def '+fn+'(');end=source.index('\n\n@PORTS.port',start)
  body=source[start:end];assert old in body,(label,old)
  assert body.count(old)==(2 if label=='help-copy-short' else 1),(label,body.count(old))
  mutated=source[:start]+body.replace(old,new)+source[end:]
 for version,tests in [('legacy',legacy),('new',current)]:
  with tempfile.TemporaryDirectory(prefix='m4-411-') as name:
   tree=Path(name);shutil.copytree(ROOT/'runtime',tree/'runtime',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
   (tree/module).write_text(mutated);(tree/'tests').mkdir();(tree/'tests/__init__.py').write_text('')
   shutil.copy(ROOT/'tests/test_port_update.py',tree/'tests/test_port_update.py')
   (tree/'tests/test_port_menus.py').write_text(tests)
   r=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_port_menus'],cwd=tree,capture_output=True,text=True,timeout=30)
   with (OUT/f'{label}-{version}-1.log').open('x') as f:f.write(r.stdout+r.stderr)
   assertion='AssertionError' in r.stderr
   if fn is None or version=='legacy':assert r.returncode==0,(label,version,r.stderr)
   else:assert r.returncode!=0 and assertion,(label,version,r.stderr)
   results.append({'control':label,'tests':version,'exit':r.returncode,'assertion_failure':assertion})
   print(label,version,r.returncode,flush=True)
with (OUT/'controls-1.json').open('x') as f:json.dump({'baseline':BASE,'runtime_sha256':hashlib.sha256(source.encode()).hexdigest(),'tests_sha256':hashlib.sha256(current.encode()).hexdigest(),'results':results},f,indent=2);f.write('\n')
print('PASS: correct code passes; all13 semantic mutants survive legacy tests and fail new assertions')
