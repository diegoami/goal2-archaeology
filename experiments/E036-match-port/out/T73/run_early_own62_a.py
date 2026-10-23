"""T73 early frozen-source own62, strict display profile, not final acceptance."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[4]
E036=ROOT/'experiments/E036-match-port'
OUT=E036/'out/T73/own-display-early-20261023-a'
OUT.mkdir(exist_ok=False)
MODULE=ROOT/'runtime/original_match/port/display.py'
source=MODULE.read_bytes()
count=subprocess.check_output([sys.executable,str(E036/'out/T73/coverage_addresses.py'),'--entries'],text=True).strip()
plan=json.loads(subprocess.check_output([sys.executable,str(E036/'shards.py'),'plan','--family','ALL','--shards','16'],cwd=ROOT))
(OUT/'launch.json').open('x').write(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'module':'display','module_sha256':hashlib.sha256(source).hexdigest(),'count':count,
 'purpose':'early diagnostic, not final acceptance'},indent=2)+'\n')
(OUT/'display-source.py').open('xb').write(source)
(OUT/'plan.json').open('x').write(json.dumps(plan,indent=2)+'\n')
env=dict(os.environ,HARNESS_HEAVY_SLOTS='32')
def run(s):
 i=s['shard'];start=time.monotonic()
 cmd=[sys.executable,'-B',str(E036/'family.py'),'--family','ALL','--only',s['only'],'--workers','2',
      '--ports','display','--count',count,'--checkpoint',str(ROOT/f'.cache/checkpoints/T73-own-early-a-s{i}'),
      '--time-limit','6000','--stretch-limit','1200','--out',str(OUT/f'shard-{i}.jsonl')]
 with (OUT/f'shard-{i}.log').open('x') as log:
  log.write('COMMAND: '+repr(cmd)+'\n');log.flush()
  result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 return {'shard':i,'exit_code':result.returncode,'seconds':time.monotonic()-start}
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:results=list(pool.map(run,plan['include']))
(OUT/'timing.json').open('x').write(json.dumps(results,indent=2)+'\n')
assert MODULE.read_bytes()==source,'Frozen renderer source changed'
if any(r['exit_code'] for r in results):sys.exit('One or more runs did not complete; inspect logs')
with (OUT/'collect.log').open('x') as log:
 subprocess.run([sys.executable,str(E036/'shards.py'),'collect','--family','ALL','--out',str(OUT/'own.jsonl'),
  *[str(OUT/f'shard-{s["shard"]}.jsonl') for s in plan['include']]],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
with (OUT/'compare.log').open('x') as log:
 result=subprocess.run([sys.executable,str(E036/'compare.py'),'--family','ALL','--no-screen','--candidate',str(OUT/'own.jsonl')],
                       cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
(OUT/'result.json').open('x').write(json.dumps({'compare_exit':result.returncode,'note':'early diagnostic only'},indent=2)+'\n')
print('EARLY OWN62 complete; strict compare exit',result.returncode,flush=True)
sys.exit(result.returncode)
