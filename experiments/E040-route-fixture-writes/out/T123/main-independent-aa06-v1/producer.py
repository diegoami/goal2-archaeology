import hashlib,json,pathlib,subprocess
root=pathlib.Path('/home/diego/projects/m3-trackb/goal2-archaeology-3')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()=='aa06d8e94cdbbc6166e17cb34fb3be2b1cc48dd3'
prefix=root/'experiments/E040-route-fixture-writes/out/T123'
index=prefix/'acceptance-v1/index.json'
assert hashlib.sha256(index.read_bytes()).hexdigest()=='89409fa3cf6cbb0dd252ffd462d22bf75709be7ecb291f58618d5680346d50e8'
def call(name,args):
 print('MAIN INDEPENDENT '+name,flush=True)
 subprocess.run(['python3','-B',*map(str,args)],cwd=root,check=True)
call('index',[prefix/'verify.py',index])
call('cached all14 strict comparison',['experiments/E040-route-fixture-writes/runner.py','--sealed','--check'])
call('pending/completed history',[prefix/'history.py','--bundle',prefix/'paired-final-v3','--out','/tmp/main-t123-aa06-history-v1.json'])
for name in ('continental','world','ageing-continental','ageing-world'):
 call(name,[prefix/'terminal_v2.py','--case',name,'--out',f'/tmp/main-t123-aa06-{name}-v1.jsonl'])
call('actual returned ALL16',[prefix/'return_effects.py','--out','/tmp/main-t123-aa06-return-v1.jsonl'])
call('missing-cache actual original/PyPy entry',[prefix/'ci_fixture_proof.py','--out','/tmp/main-t123-aa06-ci-v1.json'])
print('MAIN INDEPENDENT COMPLETE',flush=True)
