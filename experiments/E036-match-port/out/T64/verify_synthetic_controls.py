"""Prove T64's pending-local-read and live-push tests with in-memory controls."""
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'runtime'))
from tests import test_port_ball as tests
from original_match import port
from original_match.port import ball


def run(suite):
    return unittest.TextTestRunner(verbosity=2).run(suite)


baseline = run(unittest.defaultTestLoader.loadTestsFromModule(tests))
assert baseline.wasSuccessful(), 'Unmutated baseline must pass'
print('Baseline: all16 synthetic tests pass.', flush=True)


def stale8(mem, r, offset):
    return mem.u8(mem.ss_lin((r.bp + offset) & 0xFFFF))


def stale16(mem, r, offset):
    return mem.u16(mem.ss_lin((r.bp + offset) & 0xFFFF))


with patch.object(ball, 'local8', stale8), patch.object(ball, 'local16', stale16):
    failures = run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.NearestBall))
    assert len(failures.failures) == 3 and not failures.errors
    print('Historical stale-local helpers: all3 nearest tests fail assertions, no setup errors.', flush=True)

source = inspect.getsource(ball.find_nearest_to_ball)
source = source[source.index('def find_nearest_to_ball'):]
assert source.count('r.push(r.ax)') == 1
source = source.replace('r.push(r.ax)', 'None', 1)
namespace = dict(vars(ball))
exec(compile(source, '<T64 omit3099 in-memory>', 'exec'), namespace)
entry = port._module_registry('ball').entries['0791:2FB1']
with patch.object(entry, 'fn', namespace['find_nearest_to_ball']):
    failure = run(unittest.TestSuite([tests.NearestBall('test_direction_product_is_a_live_stack_word_during_second_call')]))
    assert len(failure.failures) == 1 and not failure.errors
    print('Omitting3099: live-word test fails an assertion, no setup errors.', flush=True)

print('T64 synthetic controls PASS: baseline16 and both behavioral controls; source files untouched.', flush=True)
