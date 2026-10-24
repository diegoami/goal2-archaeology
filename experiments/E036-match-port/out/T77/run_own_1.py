"""Freeze source after acquiring six shared slots; run three two-worker shards."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'runtime'))
import heavy_slot
os.environ['HARNESS_HEAVY_SLOTS']='8'
heavy_slot.take('T77-own-1',weight=6)
OUT=HERE/'own-1';OUT.mkdir(exist_ok=False)
def fingerprint():
 paths=list((ROOT/'runtime').rglob('*.py'))+list((ROOT/'tests').glob('test*.py'))
 paths+=list((ROOT/'experiments/E036-match-port').glob('*.py'))+list((ROOT/'experiments/E036-match-port/families').rglob('*'))
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.is_file() and '__pycache__' not in str(p)}
before=fingerprint();(OUT/'source-before.json').write_text(json.dumps(before,indent=2)+'\n')
sys.path.insert(0,str(ROOT/'experiments/E036-match-port'))
import shards
entries=','.join(json.loads((HERE/'listing-inventory-1.json').read_text())[i]['entry'] for i in range(17))
ids=shards.selected_ids('ALL');jobs=[]
for shard in shards.plan(ids,3):
 label='shard-'+str(shard['shard']);dest=OUT/(label+'.jsonl')
 cmd=[sys.executable,'-B','experiments/E036-match-port/family.py','--family','ALL','--only',shard['only'],'--ports','quick,rare','--count',entries,'--workers','2','--time-limit','1800','--stretch-limit','300','--out',str(dest)]
 (OUT/(label+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 log=(OUT/(label+'.log')).open('x');p=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);jobs.append((label,p,log,dest))
(OUT/'pids.json').write_text(json.dumps({l:p.pid for l,p,*_ in jobs},indent=2)+'\n')
exits={}
for label,p,log,dest in jobs:exits[label]=p.wait();log.close()
(OUT/'exits.json').write_text(json.dumps(exits,indent=2)+'\n')
after=fingerprint();(OUT/'source-after.json').write_text(json.dumps(after,indent=2)+'\n')
assert before==after,'source changed during match run'
assert not any(exits.values()),exits
shards.collect(ids,[d for *_,d in jobs],OUT/'own.jsonl')
with (OUT/'compare.log').open('x') as log:
 r=subprocess.run([sys.executable,'-B','experiments/E036-match-port/compare.py','--family','ALL','--candidate',str(OUT/'own.jsonl')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
(OUT/'compare.exit').write_text(str(r.returncode)+'\n')
raise SystemExit(r.returncode)
