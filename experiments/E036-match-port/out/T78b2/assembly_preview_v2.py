"""Exercise the preserved T78b draft against this helper slice, without a checkout edit.
Diagnostic only; not T78b acceptance. All executed source is this repo's Python.
"""
import builtins
import subprocess
import sys
import types
real_import = builtins.__import__
def deny(name, *args, **kw):
    if name == 'unicorn' or name.startswith('unicorn.'):
        raise ImportError('positive Unicorn denial')
    return real_import(name, *args, **kw)
builtins.__import__ = deny
try: __import__('unicorn')
except ImportError: pass
else: raise AssertionError('denial failed')
from original_match import Image, Fixture
from original_match.assets import reference_image
source = subprocess.check_output(['git', 'show', 'd8f10f9a:runtime/original_match/match.py'], text=True)
module = types.ModuleType('original_match._assembly_preview')
module.__package__ = 'original_match'
sys.modules[module.__name__] = module
exec(compile(source, 'T78b-d8f10f9a-match.py', 'exec'), module.__dict__)
m = module.Match(Image.from_bytes(reference_image('.cache/dl')), Fixture(7, 19, index=21),
    managed=7, seed=0x1234, record_draws=True, delay_byte=0, engine='port')
import signal
last = [None, 0, 0]
original_dispatch = m.m._dispatch
def diagnostic_dispatch(linear):
    last[2] += 1
    last[1] = last[1] + 1 if linear == last[0] else 0
    last[0] = linear
    if last[1] > 10000:
        raise RuntimeError('unchanged dispatch address repeated 10000 times')
    original_dispatch(linear)
m.m._dispatch = diagnostic_dispatch
def stop(signum, frame):
    raise TimeoutError('bounded diagnostic wall time 60s')
signal.signal(signal.SIGALRM, stop)
signal.alarm(60)
try:
    for event in m.events():
        if event.kind in ('minute', 'decision', 'half_time', 'full_time'):
            print(event.kind, event.minute, flush=True)
finally:
    signal.alarm(0)
    print('diagnostic', {k:m.st.get(k) for k in ('phase','minute','ticks')},
          m.m.where(m.m.reg('cs'),m.m.reg('ip')), 'dispatch', last,
          'frames', [f.describe() for f in m.m.frames[-4:]], flush=True)

r = m.result()
assert not hasattr(m.m, '_uc')
print({k: r[k] for k in ('score', 'ticks', 'draws', 'draws_digest')})
