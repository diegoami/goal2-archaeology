"""Source-bound own ALL63 and three reached per-scenario falsifiers (desktop8slots)."""
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
from original_match.port import menus
name=sys.argv[1]
folder=OUT/name
folder.mkdir(exist_ok=False)
sources=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+[ROOT/'experiments/E036-match-port'/p for p in ('family.py','families.py','compare.py','records.py')])
receipt={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
(folder/'source.json').write_text(json.dumps(receipt,indent=2)+'\n')
entries=','.join(sorted(menus.PORTS.entries))
env={**os.environ,'HARNESS_HEAVY_SLOTS':'8'}
jobs=[]
if name.startswith('own'):
    definitions=[(f'shard-{s["shard"]}',s['only'],None) for s in shards.plan(shards.selected_ids('ALL'),4)]
else:
    definitions=[('speed-right-increments','S/quick-1','speed-right-increments')]
for label,only,variant in definitions:
    output=folder/(label+'.jsonl')
    command=[PYTHON,'-B','experiments/E036-match-port/family.py','--family','ALL','--only',only,
             '--ports','menus','--count',entries,'--workers','2' if variant is None else '1',
             '--time-limit','1800','--stretch-limit','300','--checkpoint',f'.cache/checkpoints/T74-{name}-{label}',
             '--out',str(output)]
    if variant:command+=['--variant','menus.'+variant]
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
if name.startswith('own'):
    merged=folder/'own.jsonl'
    shards.collect(shards.selected_ids('ALL'),[o for _,_,_,o,_ in jobs],merged)
    with (folder/'compare.log').open('x') as log:
        result=subprocess.run([PYTHON,'-B','experiments/E036-match-port/compare.py','--family','ALL',
                               '--candidate',str(merged)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    (folder/'compare.exit').write_text(str(result.returncode)+'\n')
    raise SystemExit(result.returncode)
reference=compare.load(ROOT/'experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl')
specs={m.id:m for f in families.discover().values() for m in f.matches}
original=compare.load(OUT/'coverage-unhooked-1.jsonl')
branches={'tactics-adjacent-bit':'1771:1A33','speed-right-increments':'0791:940F','tactics-change-unflagged':'0791:F004'}
owners={'tactics-adjacent-bit':'1771:1981','speed-right-increments':'0791:9372','tactics-change-unflagged':'0791:ED8A'}
proof=[]
for label,_,_,output,variant in jobs:
    candidate=compare.load(output)
    declared=next(row[1] for row in definitions if row[0]==label).split(',')
    assert set(candidate)==set(declared),(label,'unexpected/missing IDs')
    expected={mid:specs[mid].sha256 for mid in declared}
    lines,ok=compare.check(reference,candidate,expected,expect='differ',image_sha256=families.image_sha256())
    (folder/(label+'-compare.log')).write_text('\n'.join(lines)+'\n')
    assert ok,label
    for mid,row in candidate.items():
        assert row.get('variant')=='menus.'+variant
        assert original[mid]['counts'][branches[variant]]>0,(variant,'original branch unvisited')
        assert row['port_calls'][owners[variant]]>0,(variant,'mutant not invoked')
        proof.append({'variant':variant,'match':mid,'branch':branches[variant],
                      'original_branch_calls':original[mid]['counts'][branches[variant]],
                      'mutant_routine_calls':row['port_calls'][owners[variant]],
                      'mutant_entry_count':row['counts'][owners[variant]]})
(folder/'caught-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
(folder/'compare.exit').write_text('0\n')
