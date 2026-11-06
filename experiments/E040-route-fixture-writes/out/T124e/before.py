"""Run the exact final new tests against the unmodified merged-main stages owner.

Loads old public source in a fresh process, never changes a checkout file and
never rewrites old measurements. Requires every new test to fail/error.
"""
import importlib
import subprocess
import sys
import types
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import port
name='original_match.port.stages'
source=subprocess.check_output(['git','show','4e8c34201473c46e058daf96c0b559c21fb41116:runtime/original_match/port/stages.py'],text=True,cwd=ROOT)
old=types.ModuleType(name);old.__package__='original_match.port';old.__file__=str(ROOT/'runtime/original_match/port/stages.py')
sys.modules[name]=old;exec(compile(source,old.__file__,'exec'),old.__dict__);port.stages=old
module=importlib.import_module('tests.test_port_stage_news');suite=unittest.defaultTestLoader.loadTestsFromModule(module)
def ids(s):
    for t in s:
        if isinstance(t,unittest.TestSuite):yield from ids(t)
        else:yield t.id()
expected=set(ids(suite));result=unittest.TextTestRunner(verbosity=2).run(suite)
failed={getattr(t,'test_case',t).id() for t,_ in result.errors+result.failures}
assert result.testsRun==len(expected)==13 and failed==expected and not result.skipped,(expected-failed,failed-expected,result.testsRun,result.skipped)
print('Before-port control: ALL13 exact final new tests failed/errors on unchanged merged-main owner; no skips.')
