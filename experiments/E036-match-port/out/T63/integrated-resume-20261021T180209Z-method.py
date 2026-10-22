"""Resume only the interrupted integrated T63 selection; checkpoint raw evidence."""
from pathlib import Path
import datetime,hashlib,json,os,shlex,subprocess,time
root=Path('/home/diego/projects/goal2-archaeology');work=root/'.claude/worktrees/task-T63-port-positioning';out=work/'experiments/E036-match-port/out/T63'
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
hashes=json.loads((out/'close-checkpoint-input-20261020T220409Z.json').read_text())['source_sha256']
def verify():
 for n,h in hashes.items():assert hashlib.sha256((work/n).read_bytes()).hexdigest()==h,n
verify();assert not (out/'all-rework-main53-cbbfb28.jsonl').exists()
assert subprocess.check_output(['gh','api','repos/diegoami/goal2-archaeology/commits/main','--jq','.sha'],text=True).strip()=='53d7ef5ec445aebc5f20d053f05d1db008db771e'
env=os.environ.copy();env.update(HARNESS_SESSION_FAMILY='openai',HARNESS_CLIENT='codex',HARNESS_HEAVY_SLOTS='4',PYTHONPATH=str(work/'runtime'),TMPDIR=str(work/'.cache/tmp'))
labels=','.join('0791:'+a for a in ('1F3C','1FDD','20E3','2218','419C','42CB','4354','4438','44C1','4532','4649','474D','47C5','4A28','4B64','4D3F'))
paths=[];jobs=[]
for h in 'ab':
 words=shlex.split((out/f'all-main53-{h}.args').read_text().splitlines()[1]);only=words[words.index('--only')+1]
 candidate=out/f'all-rework-main53-cbbfb28-{h}.jsonl';log=out/f'all-rework-main53-cbbfb28-{h}-resume-{stamp}.txt'
 args=['/usr/bin/python3','-B','experiments/E036-match-port/family.py','--family','ALL','--only',only,'--ports','all','--workers','2','--time-limit','3000','--count',labels,'--out',str(candidate.relative_to(work))]
 paths.extend((candidate,log,out/f'all-rework-main53-cbbfb28-{h}-run.txt'));jobs.append((args,log))
receipt=out/f'integrated-resume-{stamp}-input.json';receipt.write_text(json.dumps({'source_sha256':hashes,'argv':[a for a,l in jobs],'scope':'Resume interrupted ALL62 only; no new engine tasks, no review/merge'},indent=2)+'\n');method=out/f'integrated-resume-{stamp}-method.py';method.write_bytes(Path(__file__).read_bytes());paths.extend((receipt,method))
def save(message):
 verify();assert subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode==0
 subprocess.run(['git','add','--',*[str(p.relative_to(work)) for p in paths if p.exists()]],cwd=work,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=work).returncode:
  subprocess.run(['git','commit','-m','T63: '+message],cwd=work,check=True);subprocess.run(['git','push','origin','HEAD'],cwd=work,check=True)
save('preserve interrupted integrated logs and exact continuation')
procs=[]
for args,log in jobs:
 f=log.open('x');p=subprocess.Popen(args,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT);procs.append((p,f))
last=time.monotonic()
while any(p.poll() is None for p,f in procs):
 if time.monotonic()-last>=1200:save('checkpoint resumed integrated raw progress');last=time.monotonic()
 time.sleep(20)
for p,f in procs:f.close()
save('retain completed integrated worker evidence');verify();assert all(p.returncode==0 for p,f in procs),[(p.returncode) for p,f in procs]
final=out/f'integrated-resume-{stamp}-finalize.txt';paths.append(final)
with final.open('x') as f:code=subprocess.run(['/usr/bin/python3','-B','experiments/E036-match-port/out/T63/rework-finalize-all.py'],cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
paths.extend(out.glob('all-rework-main53-cbbfb28*'))
result=out/f'integrated-resume-{stamp}-result.json';result.write_text(json.dumps({'workers':[p.returncode for p,f in procs],'finalizer':code,'source_sha256':hashes},indent=2)+'\n');paths.append(result)
save('preserve strict integrated comparison and manifest');assert code==0
print('T63 integrated ALL62 passed. Main must read final report, finalize notes, and dispatch authorized R2 review. No automatic review/merge.',flush=True)
