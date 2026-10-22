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
method=out/('resume-20261021-own-recovery-method-'+stamp+'.py');method.write_bytes(Path(__file__).read_bytes());owned.append(method)
previous=json.loads((out/'own-falsifier-input-20261020T164316Z.json').read_text());assert hashes==previous['source_sha256'],'Original frozen runtime changed'
receipt=out/('resume-20261021-own-recovery-input-'+stamp+'.json');receipt.write_text(json.dumps({'source_sha256':hashes,'addresses':addresses,'input_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip(),'scope':'Own ALL62 and three O8 falsifiers; integrated ALL after main merge is separate'},indent=2)+'\n');owned.append(receipt);save('record full own/falsifier validation inputs')
def batch(label,family,halves,variant=None):
 verify();jobs=[]
 for k,ids in enumerate(halves):
  candidate=out/f'{label}-{stamp}-{k}.jsonl';log=out/f'{label}-{stamp}-{k}-resume-20261021-run.txt';argfile=out/f'{label}-{stamp}-{k}-args.json';assert not log.exists()
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

# Preserve the failed original records and retry only those three cases.
prior_paths=[out/f'own-20261020T164316Z-{k}.jsonl' for k in (0,1)]
prior={}
for path in prior_paths:
 for ident,row in compare.load(path).items():
  assert ident not in prior
  prior[ident]=row
assert len(prior)==62
bad=sorted(ident for ident,row in prior.items() if not records.is_completed(row))
assert bad==['F40/e032-1234','F40/e032-2b7e','F40/edit-c3c3'],bad
assert all(prior[ident]['error']=='TimeLimit: the match is over its time limit' for ident in bad)
refs={};expected={}
for fam in families.select('ALL',families.discover()):
 refs.update(compare.load(work/fam.reference));expected.update(fam.expected())
good={ident:row for ident,row in prior.items() if ident not in bad}
lines,ok=compare.check(refs,good,{k:v for k,v in expected.items() if k in good},image_sha256=families.image_sha256())
prefix=out/f'own-recovery-prefix-resume-20261021-{stamp}.json'
prefix.write_text(json.dumps({'comparison':lines,'ok':ok,'passed_records':len(good),'retry_ids':bad,'prior_sha256':{str(p.relative_to(work)):hashlib.sha256(p.read_bytes()).hexdigest() for p in prior_paths},'reason':'Three TimeLimit records: 26-59 CPU seconds vs 4126-4155 elapsed seconds. Cause unconfirmed; unchanged runtime and unchanged 3000-second time limit. Failed raw records retained.'},indent=2)+'\n')
owned.append(prefix);save('preserve failed own batch and verified completed prefix');assert ok and len(good)==59
batch('own-retry','ALL',[bad[::2],bad[1::2]])
retry_path=out/f'retry-three-{stamp}.jsonl';retry=compare.load(retry_path)
assert set(retry)==set(bad)
combined=out/'own-final-20261020.jsonl';assert not combined.exists()
rows={**good,**retry};assert set(rows)==set(expected)
with combined.open('x') as f:
 for ident in prior:f.write(json.dumps(rows[ident],separators=(',',':'))+'\n')
owned.append(combined)
lines,ok=compare.check(refs,rows,expected,image_sha256=families.image_sha256())
matrix={ident:{a:{'entry':row['counts'].get(a,0),'port_calls':row['port_calls'].get(a,0)} for a in addresses} for ident,row in rows.items()}
counts_equal=all(cell['entry']==cell['port_calls'] for row in matrix.values() for cell in row.values())
result=out/f'own-recovery-{stamp}-result.json'
result.write_text(json.dumps({'ok':ok,'records':len(rows),'counts_equal':counts_equal,'comparison':lines,'matrix':matrix,'candidate_sha256':hashlib.sha256(combined.read_bytes()).hexdigest(),'retry_source':str(retry_path.relative_to(work)),'prior_sources':[str(p.relative_to(work)) for p in prior_paths]},indent=2)+'\n')
owned.append(result);verify();save('preserve complete recovered own comparison and calls');print('own',lines[-1],flush=True);assert ok and counts_equal
ids=list(next(iter(families.select('O8',families.discover()))).expected());assert len(ids)==8
for variant in ('clock-reload','rating-sign','possession-swapped'):batch('fz-'+variant,'O8',[ids[::2],ids[1::2]],variant)
print('T69 recovered own62 and three O8 falsifiers PASS; integrated ALL and independent review remain.',flush=True)
