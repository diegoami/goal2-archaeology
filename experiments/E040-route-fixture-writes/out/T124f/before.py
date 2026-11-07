"""Exact final tests without the new owner; no checkout file is changed.

The base has no ageing module. An EMPTY registry only permits per-test loading;
it supplies no routine or stand-in behavior. Every test must fail/error.
"""
import importlib,subprocess,sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import port
base='0cf79c2a81e9f606d869a0ef26f53a9da8654765'
assert subprocess.run(['git','cat-file','-e',base+':runtime/original_match/port/ageing.py'],cwd=ROOT,capture_output=True).returncode!=0
old=types.ModuleType('original_match.port.ageing');old.PORTS=port.Registry('ageing','absent on base: EMPTY negative-control registry')
sys.modules[old.__name__]=old;port.ageing=old
module=importlib.import_module('tests.test_port_in_season_ageing');suite=unittest.defaultTestLoader.loadTestsFromModule(module)
def ids(s):
    for t in s:
        if isinstance(t,unittest.TestSuite):yield from ids(t)
        else:yield t.id()
expected=set(ids(suite));result=unittest.TextTestRunner(verbosity=2).run(suite)
failed={getattr(t,'test_case',t).id() for t,_ in result.errors+result.failures}
assert len(expected)==result.testsRun==18 and expected==failed and not result.skipped,(expected-failed,result.testsRun,result.skipped)
print('Before-owner control: ALL18 exact final new tests fail/error with the owner absent; no skips; no checkout file changed.')
