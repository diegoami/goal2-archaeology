"""Resume exact saved family selections; fresh logs, immutable prior records."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,time,datetime
root=Path('/home/diego/projects/goal2-archaeology');task=sys.argv[1];assert task in ('T62','T64')
tree={'T62':'agent-a55a365b32cd67a36','T64':'task-T64-port-ball'}[task];work=root/'.claude/worktrees'/tree;out=work/'experiments/E036-match-port/out'/task
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
if task=='T62':
 data=json.loads((out/'integration-input-20261019-resumed.json').read_text());args=json.loads((out/'all-main53-20261019-resumed-b.args.json').read_text())['argv'];expected_count=62
else:
 data=json.loads((out/'smoke-20261019T203630Z-input.json').read_text());args=data['argv'];expected_count=1
hashes=data['source_sha256']
def verify():assert all(hashlib.sha256((work/n).read_bytes()).hexdigest()==h for n,h in hashes.items()),'Frozen source mismatch'
verify();env=os.environ.copy();env.update(HARNESS_SESSION_FAMILY='openai',HARNESS_CLIENT='codex',HARNESS_HEAVY_SLOTS='4',PYTHONPATH=str(work/'runtime'),TMPDIR=str(work/'.cache/tmp'))
candidate=work/args[args.index('--out')+1];log=out/('resume-'+stamp+'-run.txt');receipt=out/('resume-'+stamp+'-input.json')
receipt.write_text(json.dumps({'argv':args,'source_sha256':hashes,'resume_completed_records':len(candidate.read_bytes().splitlines()) if candidate.exists() else 0,'input_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip()},indent=2)+'\n')
method=out/('resume-records-method-'+stamp+'.py');method.write_bytes(Path(__file__).read_bytes());paths=[receipt,method,candidate,log]
def save(message):
 names=[str(p.relative_to(work)) for p in paths if p.exists()];subprocess.run(['git','add','--',*names],cwd=work,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode:
  subprocess.run(['git','commit','-m',task+': '+message],cwd=work,check=True);subprocess.run(['git','push','-u','origin','HEAD'],cwd=work,check=True)
save('record exact reboot-resume inputs')
with log.open('x') as f:
 proc=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);last=time.monotonic()
 while proc.poll() is None:
  if time.monotonic()-last>=1200:save('checkpoint resumed family progress');last=time.monotonic()
  time.sleep(20)
save('retain resumed worker output');assert proc.returncode==0,'Worker failed; inspect full raw log';verify()
if task=='T62':
 candidate=out/'all.jsonl';assert not candidate.exists()
 with candidate.open('xb') as f:
  for h in 'ab':f.write((out/f'all-main53-20261019-resumed-{h}.jsonl').read_bytes())
 paths.append(candidate)
sys.path[:0]=[str(work/'runtime'),str(work/'experiments/E036-match-port')]
import compare,families,records
rows=compare.load(candidate);assert len(rows)==expected_count
for row in rows.values():records.validate(row)
refs={};expected={}
for family in families.select('ALL',families.discover()):
 selected={k:v for k,v in family.expected().items() if k in rows};expected.update(selected)
 if selected:refs.update(compare.load(work/family.reference))
lines,ok=compare.check(refs,rows,expected,image_sha256=families.image_sha256())
result=out/('resume-'+stamp+'-result.json');result.write_text(json.dumps({'worker_exit':proc.returncode,'ok':ok,'records':len(rows),'comparison':lines,'candidate_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()},indent=2)+'\n');paths.append(result)
if task=='T62':
 counts=out/('resume-'+stamp+'-counts.txt');paths.append(counts)
 with counts.open('x') as f:code=subprocess.run(['/usr/bin/python3','-B','experiments/E036-match-port/out/T62/summary.py',str(candidate.relative_to(work))],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
 assert code==0
save('preserve resumed strict comparison');print(lines[-1],flush=True);assert ok,'Strict comparison failed'
