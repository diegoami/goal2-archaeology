"""Exactly the corrected legacy method fails on the unchanged old006C stub."""
import subprocess,sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
from original_match import port
name='original_match.port.display';module=types.ModuleType(name);module.__package__='original_match.port';module.__file__=str(ROOT/'runtime/original_match/port/display.py')
source=subprocess.check_output(['git','show','62289f17e3386560537cb32804799765a437cb59:runtime/original_match/port/display.py'],text=True,cwd=ROOT)
sys.modules[name]=module;exec(compile(source,module.__file__,'exec'),module.__dict__);port.display=module
suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_port_display.UnreachedStateBranchTests.test_removed_statistics_bar_preserves_zero_and_nonzero_inputs')
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert result.testsRun==1 and len(result.failures)+len(result.errors)==1 and not result.skipped
print('Corrected original-derived statistic-bar test fails unchanged old stub in actual PyPy3.11; no skip.')
