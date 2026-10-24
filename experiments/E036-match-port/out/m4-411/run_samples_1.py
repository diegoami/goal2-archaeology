"""The process section 5 rework sample: five F40, two O8, two S cases."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
import heavy_slot
os.environ['HARNESS_HEAVY_SLOTS']='8'
heavy_slot.take('m4-411-samples',weight=6)
sys.path.insert(0,str(ROOT/'experiments/E036-match-port'))
import compare,families,shards
OUT=HERE/'samples-1';OUT.mkdir(exist_ok=False)
definitions=families.discover()
ids=[m.id for m in definitions['F40'].matches[:5]]+[m.id for m in definitions['O8'].matches[:2]]+['S/reference','S/set-piece-taker']
paths=sorted(list((ROOT/'runtime').rglob('*.py'))+list((ROOT/'tests').rglob('*.py'))+list((ROOT/'experiments/E036-match-port').glob('*.py'))+[p for p in (ROOT/'experiments/E036-match-port/families').rglob('*') if p.is_file() and '__pycache__' not in str(p)])
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();(OUT/'source-before.json').write_text(json.dumps(before,indent=2)+'\n')
(OUT/'selection.json').write_text(json.dumps({'ids':ids,'reason':'process section 5 rework sample; five declared F40 cases, two O8 and two S, including taker regression','slots':6},indent=2)+'\n')
jobs=[]
for s in shards.plan(ids,3):
 label=f'shard-{s["shard"]}';dest=OUT/(label+'.jsonl')
 cmd=[sys.executable,'-B','experiments/E036-match-port/family.py','--family','ALL','--only',s['only'],'--ports','all','--count','214B:1E5A,214B:1E8D','--workers','2','--time-limit','1800','--stretch-limit','300','--out',str(dest)]
 (OUT/(label+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 log=(OUT/(label+'.log')).open('x');p=subprocess.Popen(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT);jobs.append((label,p,log,dest))
(OUT/'pids.json').write_text(json.dumps({l:p.pid for l,p,*_ in jobs},indent=2)+'\n')
exits={}
for label,p,log,dest in jobs:exits[label]=p.wait();log.close()
(OUT/'exits.json').write_text(json.dumps(exits,indent=2)+'\n')
after=hashes();(OUT/'source-after.json').write_text(json.dumps(after,indent=2)+'\n');assert before==after
assert not any(exits.values()),exits
shards.collect(ids,[d for *_,d in jobs],OUT/'sample.jsonl')
candidate=compare.load(OUT/'sample.jsonl');profile=compare.candidate_display_profile(candidate,True);assert profile and profile['mask']==[]
expected={mid:d for f in definitions.values() for mid,d in f.expected().items() if mid in ids}
lines,ok=compare.check(compare.load(ROOT/profile['reference']),candidate,expected,no_screen=True,strict_display=True,image_sha256=families.image_sha256())
(OUT/'compare.log').write_text('\n'.join(lines)+'\n');assert ok,lines
for c in candidate.values():
 for address in ('214B:1E5A','214B:1E8D'):assert c['counts'][address]==c['port_calls'][address]
assert sum(c['port_calls']['214B:1E8D'] for c in candidate.values())>0
(OUT/'PASS.json').write_text(json.dumps({'strict_exact':9,'mask':[],'no_skipped_DS_blocks':True,'source_frozen':True,'entry_call_checks':18},indent=2)+'\n')
print('PASS:9/9 strict integrated rework cases; empty mask, all protected fields and18 entry/call checks')
