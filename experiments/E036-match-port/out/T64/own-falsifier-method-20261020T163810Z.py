"""Required T64 own ALL and reached falsifiers; source frozen, four shared slots."""
from pathlib import Path
import os,sys,json,hashlib,subprocess,shlex,time,datetime,ast
root=Path('/home/diego/projects/goal2-archaeology');work=root/'.claude/worktrees/task-T64-port-ball';out=work/'experiments/E036-match-port/out/T64';stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
env=os.environ.copy();env.update(HARNESS_SESSION_FAMILY='openai',HARNESS_CLIENT='codex',HARNESS_HEAVY_SLOTS='4',PYTHONPATH=str(work/'runtime'),TMPDIR=str(work/'.cache/tmp'))
hashes={str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (work/'runtime/original_match').rglob('*.py')}
addresses=sorted(ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse((work/'runtime/original_match/port/ball.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='port');assert len(addresses)==21
sys.path[:0]=[str(work/'runtime'),str(work/'experiments/E036-match-port')]
import compare,families,records
owned=[]
def save(message):
 paths=[str(p.relative_to(work)) for p in owned if p.exists()];subprocess.run(['git','add','--',*paths],cwd=work,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode:
  subprocess.run(['git','commit','-m','T64: '+message],cwd=work,check=True);subprocess.run(['git','push','-u','origin','HEAD'],cwd=work,check=True)
def verify():assert all(hashlib.sha256((work/n).read_bytes()).hexdigest()==h for n,h in hashes.items()),'Source drift'
method=out/('own-falsifier-method-'+stamp+'.py');method.write_bytes(Path(__file__).read_bytes());owned.append(method)
receipt=out/('own-falsifier-input-'+stamp+'.json');receipt.write_text(json.dumps({'source_sha256':hashes,'addresses':addresses,'input_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip(),'scope':'Own ALL62 and three F40 falsifiers; integrated ALL after main merge is separate'},indent=2)+'\n');owned.append(receipt);save('record full own/falsifier validation inputs')
def batch(label,family,halves,variant=None):
 verify();jobs=[]
 for k,ids in enumerate(halves):
  candidate=out/f'{label}-{stamp}-{k}.jsonl';log=out/f'{label}-{stamp}-{k}-run.txt';argfile=out/f'{label}-{stamp}-{k}-args.json';assert not candidate.exists()
  args=['/usr/bin/python3','-B','experiments/E036-match-port/family.py','--family',family,'--only',','.join(ids),'--ports','ball','--workers','2','--time-limit','3000','--count',','.join(addresses),'--out',str(candidate.relative_to(work))]
  if variant:args+=['--variant','ball.'+variant]
  argfile.write_text(json.dumps({'argv':args},indent=2)+'\n');owned.extend((candidate,log,argfile));jobs.append((args,candidate,log))
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
 combined=out/(('own' if label=='own' else 'falsifier-'+variant)+'.jsonl');assert not combined.exists()
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
halves=[]
for half in 'ab':
 p=root/'.claude/worktrees/task-T63-port-positioning/experiments/E036-match-port/out/T63'/f'all-main53-{half}.args';words=shlex.split(p.read_text().splitlines()[1]);halves.append(words[words.index('--only')+1].split(','))
assert len(set(halves[0])|set(halves[1]))==62 and not set(halves[0])&set(halves[1])
batch('own','ALL',halves)
ids=list(next(iter(families.select('F40',families.discover()))).expected());assert len(ids)==40
for variant in ('launch-reverse-x','pass-always-replace','shot-skip-jitter'):batch('fz-'+variant,'F40',[ids[::2],ids[1::2]],variant)
print('T64 own62 and3 F40 falsifiers passed. Integrated ALL and independent review remain.',flush=True)
