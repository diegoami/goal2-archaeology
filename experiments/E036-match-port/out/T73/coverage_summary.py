"""T73 original-only ALL block counts and static owners; no candidate-mask inference.

--out names a new report. Every unvisited block remains explicit; tests and
static impossibility arguments are separate claims, never manufactured hits.
"""
import argparse,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
p=argparse.ArgumentParser();p.add_argument('log');p.add_argument('--out',required=True);a=p.parse_args()
log=Path(a.log);raw=log.read_bytes();recs=[json.loads(s) for s in raw.splitlines() if s.strip()]
assert len(recs)==62 and len({r['id'] for r in recs})==62 and all(not r['error'] for r in recs)
assert all(not r.get('ports') and not r.get('mask') and not r.get('variant') for r in recs)
addrs=sorted(recs[0]['counts']);assert len(addrs)==685 and all(sorted(r['counts'])==addrs for r in recs)
placements={};instructions={};current=None
for path in sorted((ROOT/'static/goal-exe/code').glob('seg_*.asm')):
 for number,line in enumerate(path.read_text().splitlines(),1):
  m=re.match(r'; ---- routine ([0-9A-F]{4}:[0-9A-F]{4})',line)
  if m:current=m[1]
  if line.startswith('; ----') and not m:current=None
  if current:
   seg=current[:4];m=re.match(r'([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s*\S+',line)
   if m:
    addr=seg+':'+m[1];placements[addr]=(current,str(path.relative_to(ROOT)),number)
    instructions.setdefault(current,[]).append(addr)
rows=[]
for addr in addrs:
 owner,path,line=placements[addr];block=[];active=False
 for instruction in instructions[owner]:
  if instruction==addr:active=True
  elif active and instruction in addrs:break
  if active:block.append(instruction)
 per={}
 for r in recs:
  family=r['id'].split('/')[0];per[family]=per.get(family,0)+bool(r['counts'][addr])
 rows.append({'address':addr,'routine':owner,'listing':path,'line':line,'instructions':len(block),
              'calls':sum(r['counts'][addr] for r in recs),'matches':sum(bool(r['counts'][addr]) for r in recs),'families_reached':per})
report={'input':str(log),'input_sha256':hashlib.sha256(raw).hexdigest(),'matches':62,'blocks':len(rows),
        'reached':sum(bool(r['calls']) for r in rows),'unreached':sum(not r['calls'] for r in rows),'rows':rows}
Path(a.out).open('x').write(json.dumps(report,indent=2)+'\n')
print('address\troutine\tcalls\tmatches\tstatic instructions\tlisting')
for r in rows:print(f"{r['address']}\t{r['routine']}\t{r['calls']}\t{r['matches']}/62\t{r['instructions']}\t{r['listing']}:{r['line']}")
