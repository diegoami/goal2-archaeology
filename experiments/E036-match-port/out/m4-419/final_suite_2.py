"""Final frozen full-suite proof after the finals milestone correction."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
import heavy_slot
os.environ['HARNESS_HEAVY_SLOTS']='8'
heavy_slot.take('m4-419-full-suite',weight=1)
OUT=HERE/'full-suite-2';OUT.mkdir(exist_ok=False)
paths=sorted(set(list((ROOT/'runtime').rglob('*.py'))+list((ROOT/'tests').rglob('*.py'))+
 list((ROOT/'experiments/E036-match-port').glob('*.py'))+
 [p for p in (ROOT/'experiments/E036-match-port/families').rglob('*') if p.is_file() and '__pycache__' not in str(p)]+
 list((ROOT/'static/goal-exe/annotations').glob('*'))+list((ROOT/'static/goal-exe/named').glob('*'))))
paths=[p for p in paths if p.is_file()]
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();(OUT/'source-before.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'sources':before},indent=2)+'\n')
fixtures={}
for name in ('e0afff6751747233-e006-1000-r0001.sav','3ea57029282b849f-g1-03874-shootout-start.sav'):
 p=ROOT/'.cache/dl'/name;assert p.is_file(),name;fixtures[name]=hashlib.sha256(p.read_bytes()).hexdigest()
assert fixtures['3ea57029282b849f-g1-03874-shootout-start.sav']=='3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc'
(OUT/'fixtures.json').write_text(json.dumps(fixtures,indent=2)+'\n')
command=[sys.executable,'-B','-m','unittest','discover','-s','tests','-v']
(OUT/'command.json').write_text(json.dumps(command,indent=2)+'\n')
with (OUT/'suite.log').open('x') as f:r=subprocess.run(command,cwd=ROOT,env={**os.environ,'PYTHONPATH':'runtime'},stdout=f,stderr=subprocess.STDOUT)
(OUT/'exit').write_text(str(r.returncode)+'\n')
after=hashes();(OUT/'source-after.json').write_text(json.dumps(after,indent=2)+'\n');assert before==after
text=(OUT/'suite.log').read_text();m=re.search(r'Ran (\d+) tests in ([\d.]+)s',text)
skips=[line for line in text.splitlines() if ' ... skipped ' in line]
checkpoints=[line for line in text.splitlines() if 'test_build_guard_mutable.OriginalCheckpoint.' in line]
receipt={'exit':r.returncode,'tests':int(m[1]) if m else None,'seconds':float(m[2]) if m else None,'skip_lines':skips,'real_checkpoint_tests':checkpoints,'sources_frozen':True}
(OUT/'results.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert r.returncode==0 and m and int(m[1])==2089,receipt
assert len(checkpoints)==3 and all(line.endswith(' ... ok') for line in checkpoints),checkpoints
print('PASS: full2089 tests; sources frozen; all three original checkpoint controls actually run')
