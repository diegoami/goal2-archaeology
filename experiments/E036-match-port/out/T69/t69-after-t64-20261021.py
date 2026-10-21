from pathlib import Path
import subprocess,time,json,hashlib
checkpoint_root=Path('/home/diego/projects/goal2-archaeology')
print('Owner ordering: waiting for complete T64 falsifier AND integrated ALL pipeline; no heavy slot held.',flush=True)
while subprocess.run(['systemctl','--user','is-active','--quiet','goal2-t64-integrated-resume-20261021'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
 time.sleep(20)
assert 'T64 integrated ALL62 PASS;' in (checkpoint_root/'.cache/t64-integrated-resume-20261021.log').read_text(), 'T64 integration did not pass; retain evidence and stop'
t64out=checkpoint_root/'.claude/worktrees/task-T64-port-ball/experiments/E036-match-port/out/T64'
checks=sorted(t64out.glob('integration-result-*.json'));assert checks
result=json.loads(checks[-1].read_text());assert result['ok'] and result['counts_equal'] and result['records']==62
print('T64 entire pipeline passed; starting only pending T69 Done-when validation.',flush=True)
"""Required T69 own ALL and reached falsifiers; source frozen, four shared slots."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,shlex,time,datetime,ast
root=Path('/home/diego/projects/goal2-archaeology');work=root/'.claude/worktrees/agent-aca0f4fd155445184';out=work/'experiments/E036-match-port/out/T69';stamp='20261020T192724Z'
env=os.environ.copy();env.update(HARNESS_SESSION_FAMILY='openai',HARNESS_CLIENT='codex',HARNESS_HEAVY_SLOTS='4',PYTHONPATH=str(work/'runtime'),TMPDIR=str(work/'.cache/tmp'))
hashes={str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (work/'runtime/original_match').rglob('*.py')}
addresses=sorted(ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse((work/'runtime/original_match/port/frame.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='port');assert len(addresses)==14
sys.path[:0]=[str(work/'runtime'),str(work/'experiments/E036-match-port')]
import compare,families,records
owned=[]
def save(message):
 paths=[str(p.relative_to(work)) for p in owned if p.exists()];subprocess.run(['git','add','--',*paths],cwd=work,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode:
  subprocess.run(['git','commit','-m','T69: '+message],cwd=work,check=True);subprocess.run(['git','push','-u','origin','HEAD'],cwd=work,check=True)
def verify():assert all(hashlib.sha256((work/n).read_bytes()).hexdigest()==h for n,h in hashes.items()),'Source drift'
method=out/('winddown-20261021-own-recovery-method-'+stamp+'.py');method.write_bytes(Path(__file__).read_bytes());owned.append(method)
previous=json.loads((out/'own-falsifier-input-20261020T164316Z.json').read_text());assert hashes==previous['source_sha256'],'Original frozen runtime changed'
receipt=out/('winddown-20261021-own-recovery-input-'+stamp+'.json');receipt.write_text(json.dumps({'source_sha256':hashes,'addresses':addresses,'input_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip(),'scope':'Own ALL62 and three O8 falsifiers; integrated ALL after main merge is separate'},indent=2)+'\n');owned.append(receipt);save('record full own/falsifier validation inputs')
def batch(label,family,halves,variant=None):
 verify();jobs=[]
 for k,ids in enumerate(halves):
  candidate=out/f'{label}-{stamp}-{k}.jsonl';log=out/f'{label}-{stamp}-{k}-winddown-20261021-run.txt';argfile=out/f'{label}-{stamp}-{k}-args.json';assert not log.exists()
  args=['/usr/bin/python3','-B','experiments/E036-match-port/family.py','--family',family,'--only',','.join(ids),'--ports','frame','--workers','2','--time-limit','3000','--count',','.join(addresses),'--out',str(candidate.relative_to(work))]
  if variant:args+=['--variant','frame.'+variant]
  assert not argfile.exists() or json.loads(argfile.read_text())['argv']==args
  if not argfile.exists():argfile.write_text(json.dumps({'argv':args},indent=2)+'\n')
  owned.extend((candidate,log,argfile));jobs.append((args,candidate,log))
 save('record '+label+' exact disjoint selections')
 procs=[]
 for args,candidate,log in jobs:
  f=log.open('x');p=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);procs.append((p,f))
 last=time.monotonic()
 while any(p.poll() is None for p,f in procs):
  if time.monotonic()-last>=1200:save('checkpoint '+label+' progress');last=time.monotonic()
  time.sleep(20)
 for p,f in procs:f.close()
 save('retain '+label+' raw outputs');verify();assert all(p.returncode==0 for p,f in procs),'Worker failure in '+label
 combined=out/(('retry-three-'+stamp if label=='own-retry' else 'falsifier-'+variant+'-final-20261020')+'.jsonl');assert not combined.exists()
 with combined.open('xb') as f:
  for args,candidate,log in jobs:f.write(candidate.read_bytes())
 owned.append(combined);rows=compare.load(combined);expected_ids={x for half in halves for x in half};assert set(rows)==expected_ids
 refs={};expected={}
 for fam in families.select(family,families.discover()):
  selected={k:v for k,v in fam.expected().items() if k in rows};expected.update(selected)
  if selected:refs.update(compare.load(work/fam.reference))
 lines,ok=compare.check(refs,rows,expected,image_sha256=families.image_sha256(),expect='differ' if variant else 'identical')
 matrix={i:{a:{'entry':r['counts'].get(a,0),'port_calls':r['port_calls'].get(a,0)} for a in addresses} for i,r in rows.items()}
 counts_equal=all(x['entry']==x['port_calls'] for row in matrix.values() for x in row.values())
 result=out/(label+'-'+stamp+'-result.json');result.write_text(json.dumps({'ok':ok,'records':len(rows),'counts_equal':counts_equal,'comparison':lines,'matrix':matrix,'candidate_sha256':hashlib.sha256(combined.read_bytes()).hexdigest()},indent=2)+'\n');owned.append(result);save('preserve '+label+' strict comparison and calls');print(label,lines[-1],flush=True);assert ok and counts_equal,label+' failed'

prior=json.loads((out/'own-recovery-20261020T192724Z-result.json').read_text())
assert prior['ok'] and prior['counts_equal'] and prior['records']==62
assert hashlib.sha256((out/'own-final-20261020.jsonl').read_bytes()).hexdigest()==prior['candidate_sha256']
ids=list(next(iter(families.select('O8',families.discover()))).expected());assert len(ids)==8
for variant in ('clock-reload','rating-sign','possession-swapped'):
 result=out/('fz-'+variant+'-'+stamp+'-result.json')
 if result.exists():
  data=json.loads(result.read_text());candidate=out/('falsifier-'+variant+'-final-20261020.jsonl')
  assert data['ok'] and data['counts_equal'] and data['records']==8
  assert hashlib.sha256(candidate.read_bytes()).hexdigest()==data['candidate_sha256']
  print('Preserving completed falsifier',variant,flush=True)
 else:batch('fz-'+variant,'O8',[ids[::2],ids[1::2]],variant)
print('T69 recovered own62 and three O8 falsifiers PASS; integrated ALL remains. Port-stage milestone review replaces per-PR review.',flush=True)
