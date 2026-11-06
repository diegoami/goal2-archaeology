"""T126: real PyPy workers preserve typed callbacks and unittest outcomes.

The authored failing fixtures are lazy attributes, absent from dir(module), so
ordinary discovery never collects them. No original game image is needed.
"""
import copy
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import port_test_runtime as R


def _typed(value):
    print('authored incidental stdout')
    return (value, b'\x00\xff', {'tuple': (True, None, (1, 2))}, sys.implementation.name)


def _touch(path):
    Path(path).write_text('incorrect runtime executed callback')


def _explode():
    raise ValueError('authored callback failure')


def _fixture_type(name='WorkerFixture'):
    class Fixture(unittest.TestCase):
        def test_ok(self):
            self.assertEqual(sys.implementation.name, 'pypy')
            self.assertEqual(sys.version_info[:2], (3, 11))
            print('authored test stdout')

        def test_failure(self):
            self.fail('authored assertion failure')

        def test_error(self):
            raise ValueError('authored test error')

        def test_subtest(self):
            for number in (0, 1):
                with self.subTest(number=number):
                    self.assertEqual(number, 0)

        def test_subtest_skip(self):
            with self.subTest(number=3):
                self.skipTest('authored subtest skip')

        def test_cleanup_errors(self):
            def cleanup():
                raise ValueError('authored repeated cleanup error')
            self.addCleanup(cleanup); self.addCleanup(cleanup)
            raise RuntimeError('authored body error')

        @unittest.skip('authored static skip')
        def test_static_skip(self):
            self.fail('static skip executed')

        def test_dynamic_skip(self):
            raise unittest.SkipTest('authored unexpected child skip')

        @unittest.expectedFailure
        def test_expected_failure(self):
            self.fail('authored expected failure')

        @unittest.expectedFailure
        def test_unexpected_success(self):
            pass

    if name == 'WorkerSetupError':
        @classmethod
        def setUpClass(cls):
            raise RuntimeError('authored class setup failure')
        Fixture.setUpClass = setUpClass
    elif name != 'WorkerFixture':
        raise AttributeError(name)
    Fixture.__name__ = Fixture.__qualname__ = name
    Fixture.__module__ = __name__
    return Fixture


def __getattr__(name):
    if name in ('WorkerFixture', 'WorkerSetupError'):
        return _fixture_type(name)
    raise AttributeError(name)


def _case(method='test_ok', fixture='WorkerFixture'):
    return _fixture_type(fixture)(method)


class RuntimeTests(unittest.TestCase):
    def test_real_pypy_callback_preserves_tuple_bytes_and_mapping(self):
        value = (b'authored input', {'pairs': ((1, 2), (3, 4))})
        actual = R.call_in_pypy(__name__, '_typed', (value,))
        self.assertEqual(actual, (value, b'\x00\xff', {'tuple': (True, None, (1, 2))}, 'pypy'))

    def test_callback_failure_reaches_parent(self):
        with self.assertRaisesRegex(R.PortRuntimeError, 'authored callback failure'):
            R.call_in_pypy(__name__, '_explode')

    def test_configured_cpython_is_rejected_before_callback(self):
        self.assertEqual(sys.implementation.name, 'cpython', 'routing helper tests belong to CPython tooling')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'must-not-exist'
            with self.assertRaisesRegex(R.PortRuntimeError, 'PyPy 3.11'):
                R.call_in_pypy(__name__, '_touch', (str(path),), executable=sys.executable)
            self.assertFalse(path.exists())

    def test_configured_missing_executable_fails_without_fallback(self):
        with patch.dict(os.environ, {'GOAL2_PORT_PYTHON': '/authored/missing/pypy3.11'}):
            with self.assertRaises(R.PortRuntimeError):
                R.call_in_pypy(__name__, '_typed')

    def test_suite_preserves_ids_counts_and_success(self):
        tests = [_case(), _case('test_expected_failure')]
        suite = R.PyPySuite(tests)
        self.assertEqual(suite.countTestCases(), 2)
        self.assertEqual([test.id() for test in suite], [test.id() for test in tests])
        result = unittest.TestResult(); suite.run(result)
        self.assertEqual(result.testsRun, 2)
        self.assertTrue(result.wasSuccessful(), result.errors)
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertEqual(suite.countTestCases(), 2)

    def test_actual_child_failures_errors_and_subtests_propagate(self):
        tests = [_case('test_failure'), _case('test_error'), _case('test_subtest')]
        result = unittest.TestResult(); R.PyPySuite(tests).run(result)
        self.assertEqual(result.testsRun, 3)
        self.assertEqual(len(result.failures), 2)
        self.assertEqual(len(result.errors), 1)
        self.assertIs(result.failures[0][0], tests[0])
        self.assertIn('authored assertion failure', result.failures[0][1])
        self.assertIn('authored test error', result.errors[0][1])
        self.assertIn('number=1', result.failures[1][0].id())
        self.assertIn('AssertionError', result.failures[1][1])
        result = unittest.TestResult(); R.PyPySuite([_case('test_cleanup_errors')]).run(result)
        self.assertEqual((result.testsRun, len(result.errors)), (1, 3))

    def test_expected_failure_and_unexpected_success_keep_semantics(self):
        result = unittest.TestResult()
        R.PyPySuite([_case('test_expected_failure'), _case('test_unexpected_success')]).run(result)
        self.assertEqual((result.testsRun, len(result.expectedFailures), len(result.unexpectedSuccesses)), (2, 1, 1))
        self.assertFalse(result.wasSuccessful())

    def test_only_parent_known_static_skips_are_allowed_by_default(self):
        result = unittest.TestResult(); R.PyPySuite([_case('test_static_skip')]).run(result)
        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.skipped), 1)
        self.assertTrue(result.wasSuccessful())
        result = unittest.TestResult(); R.PyPySuite([_case('test_dynamic_skip')]).run(result)
        self.assertFalse(result.wasSuccessful())
        self.assertEqual(result.skipped, [])
        self.assertIn('unexpected child skip', result.errors[0][1])

    def test_explicit_approved_skip_remains_visible(self):
        test = _case('test_dynamic_skip'); result = unittest.TestResult()
        R.PyPySuite([test], allow_skips=(test.id(),)).run(result)
        self.assertEqual((result.testsRun, len(result.skipped)), (1, 1))
        self.assertTrue(result.wasSuccessful())

    def test_subtest_skips_keep_identity_and_require_approval(self):
        test = _case('test_subtest_skip')
        result = unittest.TestResult(); R.PyPySuite([test]).run(result)
        self.assertFalse(result.wasSuccessful()); self.assertEqual(result.skipped, [])
        result = unittest.TestResult(); R.PyPySuite([test], allow_skips=(test.id(),)).run(result)
        self.assertEqual((result.testsRun, len(result.skipped)), (1, 1))
        self.assertIn('number=3', result.skipped[0][0].id())
        self.assertTrue(result.wasSuccessful())

    def test_class_fixture_error_is_preserved_and_cannot_look_green(self):
        result = unittest.TestResult()
        R.PyPySuite([_case(fixture='WorkerSetupError')]).run(result)
        self.assertEqual(result.testsRun, 0)
        self.assertEqual(len(result.errors), 1)
        self.assertIn('setUpClass', result.errors[0][0].id())
        self.assertIn('authored class setup failure', result.errors[0][1])

    def test_missing_or_duplicate_requested_selectors_fail_parent(self):
        result = unittest.TestResult(); R.PyPySuite([_case(), _case()]).run(result)
        self.assertFalse(result.wasSuccessful())
        self.assertIn('duplicate', result.errors[0][1])
        wrong = _case(); wrong.id = lambda: __name__ + '.WorkerFixture.absent_method'
        result = unittest.TestResult(); R.PyPySuite([wrong]).run(result)
        self.assertFalse(result.wasSuccessful())
        self.assertIn('inventory', result.errors[0][1])

    def test_wrong_runtime_suite_is_error_not_skip(self):
        result = unittest.TestResult(); R.PyPySuite([_case()], executable=sys.executable).run(result)
        self.assertFalse(result.wasSuccessful()); self.assertEqual(result.skipped, [])
        self.assertIn('PyPy 3.11', result.errors[0][1])

    def test_tampered_loaded_and_executed_inventory_is_rejected(self):
        tests = [_case()]
        response = R._request({'mode': 'suite', 'selectors': [tests[0].id()], 'failfast': False})
        for loaded in ([], [tests[0].id(), tests[0].id()], ['wrong.id']):
            with self.subTest(loaded=loaded):
                changed = copy.deepcopy(response); changed['loaded_ids'] = loaded
                with self.assertRaises(R.PortRuntimeError):
                    R._validate_suite_response(changed, tests)
        changed = copy.deepcopy(response); changed['events'] = []; changed['tests_run'] = 0
        with self.assertRaisesRegex(R.PortRuntimeError, 'missing'):
            R._validate_suite_response(changed, tests)
        changed = copy.deepcopy(response)
        success = next(i for i, event in enumerate(changed['events']) if event['kind'] == 'success')
        changed['events'].insert(success, copy.deepcopy(changed['events'][success]))
        with self.assertRaisesRegex(R.PortRuntimeError, 'duplicate'):
            R._validate_suite_response(changed, tests)
        changed = copy.deepcopy(response); changed['identity']['implementation'] = 'cpython'
        with self.assertRaisesRegex(R.PortRuntimeError, 'PyPy 3.11'):
            R._validate_suite_response(changed, tests)
