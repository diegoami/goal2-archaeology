from pathlib import Path
import io, sys, unittest
from unittest.mock import patch
sys.path.insert(0,str(Path.cwd()))
from tests import test_port_motion as tests
from original_match.port import motion
runner=unittest.TextTestRunner(verbosity=1)
result=runner.run(unittest.defaultTestLoader.loadTestsFromModule(tests))
if not result.wasSuccessful(): raise SystemExit(1)
print('Control: all motion tests pass.',flush=True)
without_0a={k:v for k,v in motion.HANDLERS.items() if k!=0x0A}
with patch.dict(motion.HANDLERS,without_0a,clear=True):
 stream=io.StringIO()
 mutant=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([tests.UpdatePlayer('test_state_0a_calls_73ba_before_the_run_step_and_sprite')]))
 print(stream.getvalue(),flush=True)
 if len(mutant.failures)!=1 or mutant.errors or mutant.wasSuccessful():
  raise SystemExit('The missing state-0x0A handler was not caught cleanly.')
print('Mutation caught: removing state 0x0A fails the independent handler test; source files were never mutated.',flush=True)
