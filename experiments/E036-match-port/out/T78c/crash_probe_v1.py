"""Bounded T78c E034-02 diagnostic: last five boundaries, not full acceptance.

Original-game checkpoints stay in ignored .cache; only hashes/phase messages
are public. Positive Unicorn denial and faulthandler are enabled before imports.
"""
import builtins
import faulthandler
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time
faulthandler.enable(all_threads=True)
faulthandler.register(signal.SIGUSR1, all_threads=True)
original_import=builtins.__import__
def deny(name,*args,**kwargs):
    if name=='unicorn' or name.startswith('unicorn.'):
        raise ImportError('T78c diagnostic positive Unicorn denial')
    return original_import(name,*args,**kwargs)
builtins.__import__=deny
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('import denial missing')
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
from original_match.assets import reference_image
from tests.test_port_engine import memory_digest,Checkpoints
spec=importlib.util.spec_from_file_location('probe_e033',ROOT/'experiments/E033-original-match-kit/save_boundaries.py')
harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
cache=ROOT/'.cache/T78c-crash-probe-v1'
cache.mkdir(exist_ok=False)
start=time.monotonic()
def report(stage,**kwargs):
    print(json.dumps(dict(stage=stage,elapsed_s=round(time.monotonic()-start,3),pid=os.getpid(),**kwargs)),flush=True)
report('start',positive_unicorn_denial=True,diagnostic_only=True)
m=Match(Image.from_savestate(reference_image(ROOT/'.cache/dl')),
        Fixture(7,19,index=42,kind=200),managed=7,engine='port',record_draws=True)
saves=[]
def capture(i,event,phase):
    if i>=1564 and (phase=='answered' or event.kind in ('decision','shootout_kick','full_time','end')):
        # First shoot-out kick only, matching the original first-kind policy.
        if event.kind=='shootout_kick' and any(kind=='shootout_kick' for _,_,kind,_ in saves):return
        blob=m.save();path=cache/f'{i}-{phase}.omk'
        path.write_bytes(blob);saves.append((i,phase,event.kind,path))
        report('captured',boundary=i,phase=phase,kind=event.kind,sha256=hashlib.sha256(blob).hexdigest())
straight=harness.drive(m,harness.play_on,(),capture)
wanted=m.result();memory=memory_digest(m)
report('straight_finished',events=len(straight),captured=len(saves),memory_sha256=memory)
case=Checkpoints('runTest')
for i,phase,kind,path in saves:
    report('load_start',boundary=i,phase=phase)
    blob=path.read_bytes();r=Match.load(blob)
    report('load_finished',boundary=i,phase=phase,frames=len(r.m.frames))
    actual_state,actual_memory=case.unpack(r.save());saved_state,saved_memory=case.unpack(blob)
    for actual,saved in ((json.dumps(actual_state,sort_keys=True).encode(),json.dumps(saved_state,sort_keys=True).encode()),
                         (actual_memory,saved_memory)):
        assert hashlib.sha256(actual).digest()==hashlib.sha256(saved).digest(),(i,phase,'loaded state')
    rest=harness.drive(r,harness.play_on,(),start=i+1)
    assert rest==straight[i+1:],(i,phase,'events')
    assert r.result()==wanted,(i,phase,'result')
    assert memory_digest(r)==memory,(i,phase,'memory')
    report('boundary_pass',boundary=i,phase=phase)
assert 'unicorn' not in sys.modules
assert len(saves)==5,len(saves)
report('diagnostic_pass',boundaries=5,full_acceptance=False)
