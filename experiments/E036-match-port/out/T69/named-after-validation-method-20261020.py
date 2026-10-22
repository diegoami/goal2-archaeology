"""Finish T69's required named view after its existing validation job ends."""
import datetime,hashlib,json,os,pathlib,subprocess,time
ROOT=pathlib.Path('/home/diego/projects/goal2-archaeology')
WORK=ROOT/'.claude/worktrees/agent-aca0f4fd155445184'
OUT=WORK/'experiments/E036-match-port/out/T69'
STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
UNIT='goal2-t69-validate-20261020.service'
SOURCE_INPUT=OUT/'integration-input-main53-20261020T163512Z.json'
RESULT=OUT/'integration-checks-result-20261020T163512Z.json'
print('Wait for existing focused, real-check and full-suite validation; no slot held.',flush=True)
while True:
 state=subprocess.check_output(['systemctl','--user','show',UNIT,'-p','ActiveState','--value'],text=True).strip()
 if state not in ('active','activating','deactivating'):break
 time.sleep(45)
assert RESULT.exists(),'Existing validation ended without final result; no named job launched'
result=json.loads(RESULT.read_text())
assert set(result['exits'])=={'frame-replay-guest','check','full-suite'} and not any(result['exits'].values()),'Existing validation failed; inspect raw results before continuing'
hashes=json.loads(SOURCE_INPUT.read_text())['source_sha256']
assert all(hashlib.sha256((WORK/p).read_bytes()).hexdigest()==h for p,h in hashes.items()),'Frozen source drift'
exe=ROOT/'.cache/goal2/GOAL.EXE'
assert hashlib.sha256(exe.read_bytes()).hexdigest() in (WORK/'artifacts/known.json').read_text()
env=os.environ.copy()
env.update(HARNESS_SESSION_FAMILY='openai',HARNESS_CLIENT='codex',HARNESS_HEAVY_SLOTS='4',GOAL2_GHIDRA_WORK='/tmp/goal2-T69-ghidra-work',TMPDIR=str(WORK/'.cache/tmp'))
(WORK/'.cache/tmp').mkdir(parents=True,exist_ok=True)
annotation=OUT/('annotations-after-validation-'+STAMP+'.txt')
log=OUT/('named-after-validation-'+STAMP+'.txt')
receipt=OUT/('named-after-validation-input-'+STAMP+'.json')
args=['tools/harness/heavy.sh','--weight','2','T69-named','--','bash','tools/static/decompile.sh','--annotations','static/goal-exe/annotations',str(exe),'static/goal-exe/named']
receipt.write_text(json.dumps({'scope':'Required T69 named-view regeneration only; no family/review/merge dispatch','argv':args,'source_sha256':hashes,'validation_result_sha256':hashlib.sha256(RESULT.read_bytes()).hexdigest()},indent=2)+'\n')
paths=[receipt,annotation,log]
def save(message,finished=False):
 names=[str(p.relative_to(WORK)) for p in paths if p.exists()]
 if finished:names.append('static/goal-exe/named')
 subprocess.run(['git','add','--',*names],cwd=WORK,check=True)
 if subprocess.run(['git','diff','--cached','--quiet'],cwd=WORK).returncode:
  subprocess.run(['git','commit','-m','T69: '+message],cwd=WORK,check=True)
  subprocess.run(['git','push','-u','origin','HEAD'],cwd=WORK,check=True)
with annotation.open('x') as f:
 code=subprocess.run(['/usr/bin/python3','tools/static/check_annotations.py'],cwd=WORK,env=env,stdout=f,stderr=subprocess.STDOUT).returncode
save('record verified named-view regeneration inputs')
assert code==0,'Annotation failure; named generation not launched'
with log.open('x') as f:
 proc=subprocess.Popen(args,cwd=WORK,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT)
 last=time.monotonic()
 while proc.poll() is None:
  if time.monotonic()-last>=1200:save('checkpoint required named-view regeneration');last=time.monotonic()
  time.sleep(30)
save('retain required named-view generation output',finished=True)
assert all(hashlib.sha256((WORK/p).read_bytes()).hexdigest()==h for p,h in hashes.items()),'Runtime drift during named generation'
state=OUT/('named-after-validation-result-'+STAMP+'.json');paths.append(state)
state.write_text(json.dumps({'exit':proc.returncode,'source_unchanged':True,'files':{str(p.relative_to(WORK)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists() and p!=state}},indent=2)+'\n')
save('record named-view regeneration result')
assert proc.returncode==0,'Named generation failed; inspect complete log'
print('T69 named-view generation PASS. Fresh families and independent review remain; no automatic dispatch.',flush=True)
