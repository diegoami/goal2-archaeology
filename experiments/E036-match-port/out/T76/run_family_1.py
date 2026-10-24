"""Source-bound own ALL64 and three reached per-scenario falsifiers (desktop8slots)."""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PYTHON='/home/diego/.local/bin/python3.12'
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,shards
from original_match.port import takers
name=sys.argv[1]
folder=OUT/name
folder.mkdir(exist_ok=False)
sources=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+[ROOT/'experiments/E036-match-port'/p for p in ('family.py','families.py','compare.py','records.py')])
receipt={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
(folder/'source.json').write_text(json.dumps(receipt,indent=2)+'\n')
entries=','.join(sorted(takers.PORTS.entries)+['0791:CFAF','0791:9B0F','0791:9E5B'])
env={**os.environ,'HARNESS_HEAVY_SLOTS':'8'}
jobs=[]
if name.startswith(('own','native')):
    definitions=[(f'shard-{s["shard"]}',s['only'],None) for s in shards.plan(shards.selected_ids('ALL'),4)]
for label,only,variant in definitions:
    output=folder/(label+'.jsonl')
    command=[PYTHON,'-B','experiments/E036-match-port/family.py','--family','ALL','--only',only,
             '--ports','takers','--count',entries,'--workers','2' if variant is None else '1',
             '--time-limit','1800','--stretch-limit','300','--checkpoint',f'.cache/checkpoints/T76-{name}-{label}',
             '--out',str(output)]
    if name.startswith('native'):
        pos=command.index('--ports');del command[pos:pos+2]
    if variant:command+=['--variant','takers.'+variant]
    (folder/(label+'-command.json')).write_text(json.dumps(command,indent=2)+'\n')
    log=(folder/(label+'.log')).open('x')
    p=subprocess.Popen(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=env)
    jobs.append((label,p,log,output,variant))
(folder/'pids.json').write_text(json.dumps({label:p.pid for label,p,*_ in jobs},indent=2)+'\n')
exits={}
for label,p,log,output,variant in jobs:
    exits[label]=p.wait();log.close()
(folder/'exits.json').write_text(json.dumps(exits,indent=2)+'\n')
if any(exits.values()):raise SystemExit(1)
if name.startswith(('own','native')):
    merged=folder/'own.jsonl'
    shards.collect(shards.selected_ids('ALL'),[o for _,_,_,o,_ in jobs],merged)
    with (folder/'compare.log').open('x') as log:
        result=subprocess.run([PYTHON,'-B','experiments/E036-match-port/compare.py','--family','ALL',
                               '--candidate',str(merged)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    (folder/'compare.exit').write_text(str(result.returncode)+'\n')
    raise SystemExit(result.returncode)
