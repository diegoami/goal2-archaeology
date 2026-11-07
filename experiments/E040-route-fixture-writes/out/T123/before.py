"""Load unchanged old port owner in memory; exact authored tests must fail.
No checkout file is rewritten and no production fallback is supplied.
"""
import ast,importlib,subprocess,sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from original_match import port
name='original_match.port.route';old=types.ModuleType(name);old.__package__='original_match.port';old.__file__=str(ROOT/'runtime/original_match/port/route.py')
source=subprocess.check_output(['git','show','62289f17e3386560537cb32804799765a437cb59:runtime/original_match/port/route.py'],text=True,cwd=ROOT)
sys.modules[name]=old;exec(compile(source,old.__file__,'exec'),old.__dict__);port.route=old
m=importlib.import_module('tests.test_route_sealed');suite=unittest.defaultTestLoader.loadTestsFromModule(m)
def ids(s):
 for t in s:
  if isinstance(t,unittest.TestSuite):yield from ids(t)
  else:yield t.id()
expected=set(ids(suite));result=unittest.TextTestRunner(verbosity=2).run(suite)
failed={getattr(t,'test_case',t).id() for t,_ in result.errors+result.failures}
assert expected==failed and not result.skipped,(expected-failed,result.skipped)
print('ALL authored tests fail/error on unchanged before source; no skip/no checkout rewrite.')
