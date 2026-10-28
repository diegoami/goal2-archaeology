from pathlib import Path
import subprocess,sys,os,json,hashlib,time,signal
from datetime import datetime,timezone
root=Path('/home/diego/projects/goal2-archaeology-engine')
out=root/'experiments/E036-match-port/out/T78c'
script=out/'crash_probe_v1.py'
paths=sorted((root/'runtime/original_match').rglob('*.py'))+[root/'tests/test_port_engine.py',script]
def hashes():return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
command=['tools/heavy.sh','T78c-crash-diagnostic','--','/home/diego/.local/bin/python3.12','-B','-X','faulthandler',str(script)]
start=time.monotonic();timedout=False
with (out/'crash-diagnostic-v1.log').open('x') as log:
 p=subprocess.Popen(command,cwd=root,env=dict(os.environ,PYTHONPATH='runtime',PYTHONFAULTHANDLER='1'),stdout=log,stderr=subprocess.STDOUT,start_new_session=True,stdin=subprocess.DEVNULL)
 (root/'.cache/T78c-crash-diagnostic-v1-pid.json').write_text(json.dumps(dict(pid=p.pid,head=head,command=command)))
 try:code=p.wait(timeout=1200)
 except subprocess.TimeoutExpired:
  timedout=True;os.killpg(p.pid,signal.SIGUSR1)
  time.sleep(2);os.killpg(p.pid,signal.SIGTERM);code=p.wait(timeout=15)
report=dict(command=command,head=head,source_sha256=before,source_unchanged=before==hashes(),exit_code=code,timed_out=timedout,wall_s_including_queue=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat())
with (out/'crash-diagnostic-v1-exit.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'}),flush=True)
