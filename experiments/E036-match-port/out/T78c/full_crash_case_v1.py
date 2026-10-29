"""Complete original E034-02 policy under positive denial and crash tracing.

This is a diagnostic rerun of the full unchanged unittest, not a replacement
for hosted acceptance. Never overwrite a log/receipt or expose a checkpoint.
"""
import os,sys,json,hashlib,time,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
if '--child' in sys.argv:
    import builtins,faulthandler
    faulthandler.enable(all_threads=True)
    original=builtins.__import__
    def deny(name,*args,**kwargs):
        if name=='unicorn' or name.startswith('unicorn.'):
            raise ImportError('T78c full scenario positive Unicorn denial')
        return original(name,*args,**kwargs)
    builtins.__import__=deny
    try:__import__('unicorn')
    except ImportError:pass
    else:raise AssertionError('positive denial not installed')
    sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
    import unittest
    print('Full original E034-02 scenario: positive Unicorn denial, faulthandler enabled',flush=True)
    program=unittest.main(module=None,argv=[sys.argv[0],'tests.test_port_engine.Checkpoints.test_e034_02','-v'],exit=False)
    assert 'unicorn' not in sys.modules
    raise SystemExit(not program.result.wasSuccessful())
paths=sorted((ROOT/'runtime/original_match').rglob('*.py'))+[ROOT/'tests/test_port_engine.py',Path(__file__)]
def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
before=hashes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
command=['tools/heavy.sh','T78c-full-crash-v1','--',sys.executable,'-B','-X','faulthandler',str(Path(__file__).resolve()),'--child']
start=time.monotonic();timed_out=False
out=ROOT/'experiments/E036-match-port/out/T78c'
with (out/'full-crash-v1.log').open('x') as log:
 p=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONPATH='runtime',PYTHONFAULTHANDLER='1'))
 (ROOT/'.cache/T78c-full-crash-v1-pid.json').write_text(json.dumps(dict(pid=p.pid,head=head,command=command)))
 try:code=p.wait(timeout=10800)
 except subprocess.TimeoutExpired:
  timed_out=True;p.terminate();code=p.wait(timeout=30)
report=dict(head=head,command=command,exit_code=code,timed_out=timed_out,source_unchanged=before==hashes(),source_sha256=before,wall_s_including_queue=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat())
with (out/'full-crash-v1-exit.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'}),flush=True)
