"""Diagnostic of unchanged S/quick-1 using the preserved T78b facade.

The oracle is unhooked original code. Candidate imports are positively denied
before any kit loading. This is not final T78b CLI/checkpoint/corpus acceptance.
"""
import builtins
import json
from pathlib import Path
import subprocess
import sys
import types
mode=sys.argv[1]
if mode=='port':
    original_import=builtins.__import__
    def deny(name,*args,**kwargs):
        if name=='unicorn' or name.startswith('unicorn.'):
            raise ImportError('positive Unicorn denial')
        return original_import(name,*args,**kwargs)
    builtins.__import__=deny
    try:__import__('unicorn')
    except ImportError:pass
    else:raise AssertionError('guard failed')
root=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(root/'runtime'),str(root/'experiments/E036-match-port')]
import original_match
if mode=='port':
    source=subprocess.check_output(['git','show','0ac4c840:runtime/original_match/match.py'],text=True)
    module=types.ModuleType('original_match._quick_preview')
    module.__package__='original_match';sys.modules[module.__name__]=module
    exec(compile(source,'T78b-0ac4c840-match.py','exec'),module.__dict__)
    class Candidate(module.Match):
        def __init__(self,*args,**kwargs):
            kwargs['engine']='port'
            super().__init__(*args,**kwargs)
            assert not hasattr(self.m,'_uc')
    original_match.Match=Candidate
import family
import families
from original_match import port
from original_match.assets import reference_image
image=original_match.Image.from_bytes(reference_image(root/'.cache/dl'))
spec=next(s for s in families.discover()['S'].matches if s.id=='S/quick-1')
profile=family.read_display_profile()
record=family.run_match(image,spec,mask=profile['mask'],
    ports=port.spec_names(port.load(['all'])) if mode=='port' else (),display_profile=True)
Path(sys.argv[2]).write_text(json.dumps(record,sort_keys=True)+'\n')
print(json.dumps({'diagnostic_engine':mode,'id':record['id'],'error':record['error'],
    'score':record['score'],'ticks':record['ticks'],'cpu_s':record['cpu_s']}),flush=True)
assert record['error'] is None and record['stopped_at_board'] and not record['strays']
if mode=='port':assert not any(n=='unicorn' or n.startswith('unicorn.') for n in sys.modules)
