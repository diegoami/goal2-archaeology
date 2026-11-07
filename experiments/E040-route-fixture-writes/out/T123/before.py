"""Load exact old owners in both parent and verified PyPy test workers.
No checkout is changed; all authored test methods must fail, without skips.
"""
import importlib,subprocess,sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools')]
BASE='62289f17e3386560537cb32804799765a437cb59'
OWNERS=['original_match.port.route','original_match.port.silent','original_match.port.display','original_match.port.entrypoints','original_match.match','original_match.route']
sources={name:subprocess.check_output(['git','show',BASE+':runtime/'+name.replace('.','/')+'.py'],text=True,cwd=ROOT) for name in OWNERS}

def install(sources):
    import original_match
    from original_match import port
    for name,source in sources.items():
        parent,_,leaf=name.rpartition('.');module=types.ModuleType(name);module.__package__=parent;module.__file__=str(ROOT/'runtime'/Path(*name.split('.')).with_suffix('.py'))
        sys.modules[name]=module;exec(compile(source,module.__file__,'exec'),module.__dict__)
        setattr(importlib.import_module(parent),leaf,module)
    original_match.Match=sys.modules['original_match.match'].Match

install(sources)
import port_test_runtime
real_call=port_test_runtime.call_in_pypy
port_test_runtime.call_in_pypy=lambda module,function,args=(),kwargs=None,**options:real_call('test_route_sealed','_before_callback',args=(sources,function,args,kwargs or {}),**options)
m=importlib.import_module('tests.test_route_sealed')
# The fixture recipe is reference scaffolding absent at BASE. Its exact pre-CI
# loader version is82a86d9e; new availability tests must fail that unchanged owner.
fixture_source=subprocess.check_output(['git','show','82a86d9e5d2a5148c0924fa4d9ce63a5bb10484e:experiments/E040-route-fixture-writes/out/T123/fixtures.py'],text=True,cwd=ROOT)
def old_fixtures():
    module=types.ModuleType('_t123_pre_ci_fixture');module.__file__=str(ROOT/'experiments/E040-route-fixture-writes/out/T123/fixtures.py')
    exec(compile(fixture_source,module.__file__,'exec'),module.__dict__);return module
m._fixtures=old_fixtures
suite=unittest.defaultTestLoader.loadTestsFromModule(m)
def ids(suite):
    for t in suite:
        if isinstance(t,unittest.TestSuite):yield from ids(t)
        else:yield t.id()
expected=set(ids(suite));result=unittest.TextTestRunner(verbosity=2).run(suite)
failed={getattr(t,'test_case',t).id() for t,_ in result.errors+result.failures}
assert expected==failed and not result.skipped,(expected-failed,result.skipped)
print('ALL authored methods fail on exact unchanged old owners in parent and verified PyPy workers; no skips.')
