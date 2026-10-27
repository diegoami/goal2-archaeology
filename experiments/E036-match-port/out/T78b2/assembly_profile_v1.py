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
import cProfile
import pstats
profiler=cProfile.Profile()
profiler.enable()
for event in m.events():
    if event.kind == 'minute' and event.minute >= 3: break
profiler.disable()
assert not hasattr(m.m,'_uc')
print('Standalone diagnostic prefix', m.st['minute'], m.st['ticks'])
pstats.Stats(profiler).strip_dirs().sort_stats('cumtime').print_stats(25)
