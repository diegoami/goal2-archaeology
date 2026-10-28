"""Read-only phase diagnostic for E034-03's unchanged 60-second dispatch guard.

Exact first straight run/capture policy from the accepted checkpoint test.
Not a substitute for full boundary acceptance. Original-byte captures stay private.
"""
import builtins,faulthandler,sys,os,json,hashlib,time,subprocess,importlib.util
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'experiments/E036-match-port/out/T78c'
if '--child' not in sys.argv:
    paths=sorted((ROOT/'runtime/original_match').rglob('*.py'))+[ROOT/'tests/test_port_engine.py',Path(__file__)]
    def hashes():return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    before=hashes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    command=['tools/heavy.sh','T78c-deadline-probe-v1','--',sys.executable,'-B','-X','faulthandler',str(Path(__file__).resolve()),'--child']
    start=time.monotonic();timed_out=False
    with (OUT/'deadline-probe-v1.log').open('x') as log:
        p=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,PYTHONPATH='runtime',PYTHONFAULTHANDLER='1'))
        (ROOT/'.cache/T78c-deadline-probe-v1-pid.json').write_text(json.dumps(dict(pid=p.pid,head=head,command=command)))
        try:code=p.wait(timeout=900)
        except subprocess.TimeoutExpired:
            timed_out=True;p.terminate();code=p.wait(timeout=30)
    report=dict(head=head,command=command,source_sha256=before,source_unchanged=before==hashes(),exit_code=code,timed_out=timed_out,wall_s_including_queue=time.monotonic()-start,finished_utc=datetime.now(timezone.utc).isoformat(),diagnostic_not_acceptance=True)
    with (OUT/'deadline-probe-v1-exit.json').open('x') as f:json.dump(report,f,indent=2)
    print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'}),flush=True)
    raise SystemExit(code if before==hashes() else 2)
faulthandler.enable(all_threads=True)
original_import=builtins.__import__
def deny(name,*args,**kwargs):
    if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
    return original_import(name,*args,**kwargs)
builtins.__import__=deny
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('denial not installed')
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import Image,Match,Fixture
from original_match.assets import reference_image
spec=importlib.util.spec_from_file_location('deadline_policy',ROOT/'experiments/E033-original-match-kit/save_boundaries.py');harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
start=time.monotonic()
def report(stage,**kwargs):print(json.dumps(dict(stage=stage,elapsed_s=round(time.monotonic()-start,4),**kwargs)),flush=True)
advance=Match._advance
last=None
def traced(self):
    global last
    context=(self.st.get('phase'),self.st.get('stage'))
    begin_wall,begin_cpu=time.monotonic(),time.process_time()
    if context!=last:report('phase_start',phase=context,minute=self.st.get('minute'),timeout_s=self.timeout_s);last=context
    try:return advance(self)
    except Exception as error:
        report('advance_error',phase=context,minute=self.st.get('minute'),error_type=type(error).__name__,error=str(error),timeout_s=self.timeout_s)
        raise
    finally:
        wall=time.monotonic()-begin_wall
        if wall>1:report('long_advance',phase=context,minute=self.st.get('minute'),wall_s=wall,cpu_s=time.process_time()-begin_cpu)
Match._advance=traced
m=Match(Image.from_savestate(reference_image(ROOT/'.cache/dl')),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
assert m.timeout_s==60 and not hasattr(m.m,'_uc')
saves=[];kinds=set();private=ROOT/'.cache/T78c-deadline-probe-v1';private.mkdir(exist_ok=False)
def capture(i,event,phase):
    if phase=='answered' or event.kind not in kinds or event.kind in ('decision','end'):
        if event is not None:kinds.add(event.kind)
        blob=m.save();saves.append((i,phase,blob));report('capture',boundary=i,phase=phase,kind=None if event is None else event.kind)
def policy(match,data):match.answer(quick=True) if data['context']=='half_time' else match.answer()
try:
    events=harness.drive(m,policy,(),capture)
    assert 'unicorn' not in sys.modules
    result=m.result();report('straight_pass',events=len(events),boundaries=len(saves),score=result['score'],draws=result['draws'],memory_sha256=hashlib.sha256(m.m.read(0,0x110000)).hexdigest(),diagnostic_not_acceptance=True)
finally:
    for index,phase,blob in saves[-2:]:
        path=private/f'{index}-{phase}.omk';path.write_bytes(blob);report('private_public_boundary_capture',boundary=index,phase=phase,sha256=hashlib.sha256(blob).hexdigest())
