"""T126: trusted local test children run the standalone port on PyPy 3.11.

Pickle protocol 4 preserves Python values (notably tuples and bytes). This is a
private test-process protocol, NOT a production or untrusted-input API. Original
memory travels only through private pipes; protocol errors never dump payloads.
The CPython caller retains the original/Unicorn reference and unittest results.
"""
from __future__ import annotations

from collections import Counter
import importlib
import os
from pathlib import Path
import pickle
import re
import shutil
import subprocess
import sys
import traceback
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 1


class PortRuntimeError(RuntimeError):
    """A required PyPy worker or its complete test inventory was not valid."""


class RemoteTestFailure(AssertionError):
    pass


class RemoteTestError(RuntimeError):
    pass


def _identity():
    return {'implementation': sys.implementation.name, 'major': sys.version_info.major,
            'minor': sys.version_info.minor, 'version': sys.version.splitlines()[0]}


def _check_identity(identity):
    if not isinstance(identity, dict) or (identity.get('implementation'), identity.get('major'),
                                         identity.get('minor')) != ('pypy', 3, 11):
        raise PortRuntimeError('port tests require PyPy 3.11; worker identity was '
                               + repr(identity))


def pypy_executable(executable=None):
    """A configured missing/wrong executable fails; there is no CPython fallback."""
    configured = executable if executable is not None else os.environ.get('GOAL2_PORT_PYTHON')
    if configured is not None:
        configured = os.fspath(configured)
        if not configured:
            raise PortRuntimeError('GOAL2_PORT_PYTHON is empty; PyPy 3.11 is required')
        found = shutil.which(configured)
        if found is None:
            raise PortRuntimeError('configured PyPy 3.11 executable is missing: ' + configured)
        return found
    for candidate in ('pypy3.11', 'pypy3', str(Path.home() / '.local/bin/pypy3.11'),
                      str(ROOT / '.cache/pypy/bin/pypy3.11')):
        found = shutil.which(candidate)
        if found:
            return found
    raise PortRuntimeError('PyPy 3.11 is required: set GOAL2_PORT_PYTHON to its executable')


def _request(request, *, executable=None, timeout=None):
    command = [pypy_executable(executable), '-B', str(Path(__file__).resolve()), '--worker']
    try:
        completed = subprocess.run(command, input=pickle.dumps(request, protocol=4),
                                   stdout=subprocess.PIPE, stderr=None,
                                   cwd=ROOT, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PortRuntimeError('PyPy test worker could not complete: ' + str(exc)) from exc
    # Worker stderr is inherited for live progress. Its redirected incidental
    # stdout never interleaves with the private binary return value.
    try:
        response = pickle.loads(completed.stdout)
    except Exception as exc:
        raise PortRuntimeError('PyPy worker returned no valid private result '
                               f'(exit {completed.returncode}); payload omitted') from exc
    if not isinstance(response, dict) or response.get('protocol') != PROTOCOL:
        raise PortRuntimeError('PyPy worker returned an incompatible test protocol')
    _check_identity(response.get('identity'))
    if completed.returncode or response.get('worker_error'):
        raise PortRuntimeError('PyPy test worker failed: ' + str(response.get('worker_error',
                               'exit ' + str(completed.returncode))))
    return response


def call_in_pypy(module, function, args=(), kwargs=None, *, executable=None, timeout=None):
    """Call a trusted test function in verified PyPy, returning its typed value."""
    response = _request({'mode': 'call', 'module': module, 'function': function,
                         'args': tuple(args), 'kwargs': {} if kwargs is None else kwargs},
                        executable=executable, timeout=timeout)
    if response.get('mode') != 'call':
        raise PortRuntimeError('PyPy worker returned the wrong callback result mode')
    if not response.get('ok'):
        raise PortRuntimeError('PyPy callback failed:\n' + str(response.get('traceback', 'no traceback')))
    print('port callback runtime: PyPy 3.11 (' + response['identity']['version'] + ')', file=sys.stderr)
    return response['value']


def _flatten(tests):
    for test in tests:
        if isinstance(test, unittest.TestSuite):
            yield from _flatten(test)
        else:
            yield test


def _static_skip(test):
    for obj in (test.__class__, getattr(test, getattr(test, '_testMethodName', ''), None)):
        if getattr(obj, '__unittest_skip__', False):
            return str(getattr(obj, '__unittest_skip_why__', ''))
    return None


def _fixture(label, tests):
    match = re.fullmatch(r'(setUpClass|tearDownClass|setUpModule|tearDownModule) \((.+)\)', label)
    if not match:
        raise PortRuntimeError('unknown child fixture outcome: ' + label)
    kind, owner = match.groups()
    ids = []
    for test in tests:
        actual = test.__class__.__module__
        if kind.endswith('Class'):
            actual += '.' + test.__class__.__qualname__
        if owner == actual:
            ids.append(test.id())
    if not ids:
        raise PortRuntimeError('child fixture outcome has no requested owner: ' + label)
    return kind, ids


def _validate_suite_response(response, tests, *, allow_skips=(), failfast=False):
    _check_identity(response.get('identity'))
    ids = [test.id() for test in tests]
    if len(set(ids)) != len(ids):
        raise PortRuntimeError('duplicate requested test ID in PyPy suite inventory')
    if response.get('mode') != 'suite' or response.get('requested_ids') != ids or response.get('loaded_ids') != ids:
        raise PortRuntimeError('PyPy requested/loaded test inventory differs from the parent')
    by_id = {test.id(): test for test in tests}
    approved = set(allow_skips)
    if approved - set(ids):
        raise PortRuntimeError('skip approval names a test outside this PyPy suite')
    active = None
    started, stopped, outcomes, blocked = [], [], set(), set()
    failure_seen = False
    counted = Counter()
    single_terminal = set()
    for sequence, event in enumerate(response.get('events', ())):
        if event.get('sequence') != sequence:
            raise PortRuntimeError('missing/duplicate child outcome event sequence')
        kind, name = event.get('kind'), event.get('id')
        if kind in ('fixture_error', 'fixture_skip'):
            fixture_kind, affected = _fixture(name, tests)
            if active is not None:
                raise PortRuntimeError('fixture outcome inside an active child test')
            counted['skips' if kind == 'fixture_skip' else 'errors'] += 1
            if kind == 'fixture_skip':
                reason = str(event.get('reason', ''))
                if any(i not in approved and _static_skip(by_id[i]) != reason for i in affected):
                    raise PortRuntimeError('unexpected child skip in ' + name)
            else:
                failure_seen = True
            if fixture_kind.startswith('setUp'):
                blocked.update(i for i in affected if i not in stopped)
            continue
        if name not in by_id:
            raise PortRuntimeError('wrong child test ID in PyPy outcome inventory: ' + str(name))
        if kind == 'start':
            if active is not None or name in started:
                raise PortRuntimeError('duplicate/overlapping child test start: ' + name)
            active = name; started.append(name)
        elif kind == 'stop':
            if active != name or name in stopped:
                raise PortRuntimeError('duplicate or unmatched child test stop: ' + name)
            if name not in outcomes:
                raise PortRuntimeError('missing child test outcome: ' + name)
            active = None; stopped.append(name)
        elif kind in ('success', 'failure', 'error', 'skip', 'expected_failure', 'unexpected_success', 'subtest', 'subtest_skip'):
            if active != name:
                raise PortRuntimeError('child outcome outside its active test: ' + name)
            outcomes.add(name)
            if kind in ('success', 'skip', 'expected_failure', 'unexpected_success'):
                if (name, kind) in single_terminal:
                    raise PortRuntimeError('duplicate child terminal outcome: ' + name + ' ' + kind)
                single_terminal.add((name, kind))
            counters = {'success': 'successes', 'failure': 'failures', 'error': 'errors',
                        'skip': 'skips', 'expected_failure': 'expected_failures',
                        'unexpected_success': 'unexpected_successes', 'subtest_skip': 'skips'}
            if kind in counters:
                counted[counters[kind]] += 1
            if kind == 'subtest' and event.get('outcome') in ('failure', 'error'):
                counted['failures' if event['outcome'] == 'failure' else 'errors'] += 1
            if kind in ('skip', 'subtest_skip'):
                if name not in approved and _static_skip(by_id[name]) != str(event.get('reason', '')):
                    raise PortRuntimeError('unexpected child skip for ' + name + ': ' + str(event.get('reason', '')))
            if kind in ('subtest', 'subtest_skip') and not str(event.get('subtest_id', '')).startswith(name + ' '):
                raise PortRuntimeError('wrong child subtest ID: ' + str(event.get('subtest_id')))
            failure_seen |= kind in ('failure', 'error', 'unexpected_success') or (
                kind == 'subtest' and event.get('outcome') in ('failure', 'error'))
        else:
            raise PortRuntimeError('unknown child unittest outcome: ' + str(kind))
    if active is not None or started != stopped or response.get('tests_run') != len(started):
        raise PortRuntimeError('missing/duplicate child test completion in PyPy inventory')
    missing = set(ids) - set(started) - blocked
    if missing and not (failfast and response.get('should_stop') and failure_seen):
        raise PortRuntimeError('missing executed child test IDs: ' + ', '.join(sorted(missing)))
    if [i for i in ids if i in started] != started:
        raise PortRuntimeError('child test order differs from the parent inventory')
    fields = ('successes', 'failures', 'errors', 'skips', 'expected_failures', 'unexpected_successes')
    if response.get('outcome_counts') != {name: counted[name] for name in fields}:
        raise PortRuntimeError('missing/duplicate child terminal outcomes in result summary')


class _RemoteHolder(unittest.TestCase):
    def __init__(self, identity):
        super().__init__('runTest'); self.identity = identity
    def id(self): return self.identity
    def __str__(self): return self.identity
    def shortDescription(self): return None
    def countTestCases(self): return 0


def _remote_info(text, failure=False, test=None):
    kind = RemoteTestFailure if failure else RemoteTestError
    if failure and test is not None and not issubclass(kind, test.failureException):
        kind = type('PyPyAssertionFailure', (test.failureException,), {})
    value = BaseException.__new__(kind)
    BaseException.__init__(value, text)
    return kind, value, None


def _replay(response, tests, result):
    by_id = {test.id(): test for test in tests}
    for event in response['events']:
        kind, name = event['kind'], event['id']
        if kind.startswith('fixture_'):
            holder = _RemoteHolder(name)
            if kind == 'fixture_skip': result.addSkip(holder, event['reason'])
            else: result.addError(holder, _remote_info(event['traceback']))
            continue
        test = by_id[name]
        if kind == 'start': result.startTest(test)
        elif kind == 'stop': result.stopTest(test)
        elif kind == 'success': result.addSuccess(test)
        elif kind == 'failure': result.addFailure(test, _remote_info(event['traceback'], True, test))
        elif kind == 'error': result.addError(test, _remote_info(event['traceback']))
        elif kind == 'skip': result.addSkip(test, event['reason'])
        elif kind == 'expected_failure': result.addExpectedFailure(test, _remote_info(event['traceback'], True, test))
        elif kind == 'unexpected_success': result.addUnexpectedSuccess(test)
        elif kind == 'subtest_skip': result.addSkip(_RemoteHolder(event['subtest_id']), event['reason'])
        elif kind == 'subtest':
            subtest = _RemoteHolder(event['subtest_id'])
            outcome = event['outcome']
            info = None if outcome == 'success' else _remote_info(event['traceback'], outcome == 'failure', test)
            result.addSubTest(test, subtest, info)


class PyPySuite(unittest.TestSuite):
    """The same selected test IDs, once each, in one verified PyPy child batch."""
    def __init__(self, tests=(), *, executable=None, timeout=None, allow_skips=()):
        selected = list(_flatten(tests))
        super().__init__(selected)
        self.executable, self.timeout, self.allow_skips = executable, timeout, tuple(allow_skips)

    def run(self, result, debug=False):
        if result.shouldStop or not self._tests:
            return result
        tests = list(self._tests)
        try:
            ids = [test.id() for test in tests]
            if len(set(ids)) != len(ids):
                raise PortRuntimeError('duplicate requested test ID in PyPy suite inventory')
            response = _request({'mode': 'suite', 'selectors': ids, 'failfast': bool(result.failfast)},
                                executable=self.executable, timeout=self.timeout)
            _validate_suite_response(response, tests, allow_skips=self.allow_skips, failfast=bool(result.failfast))
            print(f"port test runtime: PyPy 3.11 ({response['identity']['version']}), {len(ids)} selected tests", file=sys.stderr)
            _replay(response, tests, result)
        except Exception:
            if debug: raise
            result.addError(_RemoteHolder('PyPy worker / test inventory'), sys.exc_info())
        return result


class _RecordingResult(unittest.TestResult):
    def __init__(self, failfast=False):
        super().__init__(); self.events = []; self.failfast = failfast; self.successes = 0
    def _event(self, kind, test, **fields):
        self.events.append(dict(sequence=len(self.events), kind=kind, id=test.id(), **fields))
    def startTest(self, test):
        super().startTest(test); self._event('start', test)
        print('PyPy test start: ' + test.id(), file=sys.stderr, flush=True)
    def stopTest(self, test):
        self._event('stop', test); super().stopTest(test)
        print('PyPy test end: ' + test.id(), file=sys.stderr, flush=True)
    def addSuccess(self, test):
        super().addSuccess(test); self.successes += 1; self._event('success', test)
    def addFailure(self, test, err):
        text = self._exc_info_to_string(err, test)
        super().addFailure(test, err); self._event('failure', test, traceback=text)
    def addError(self, test, err):
        text = self._exc_info_to_string(err, test)
        super().addError(test, err)
        self._event('fixture_error' if isinstance(test, unittest.suite._ErrorHolder) else 'error', test, traceback=text)
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if isinstance(test, unittest.case._SubTest):
            self._event('subtest_skip', test.test_case, subtest_id=test.id(), reason=str(reason))
        else:
            self._event('fixture_skip' if isinstance(test, unittest.suite._ErrorHolder) else 'skip', test, reason=str(reason))
    def addExpectedFailure(self, test, err):
        text = self._exc_info_to_string(err, test)
        super().addExpectedFailure(test, err); self._event('expected_failure', test, traceback=text)
    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test); self._event('unexpected_success', test)
    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        outcome = 'success' if err is None else ('failure' if issubclass(err[0], test.failureException) else 'error')
        fields = {'subtest_id': subtest.id(), 'outcome': outcome}
        if err is not None: fields['traceback'] = self._exc_info_to_string(err, test)
        self._event('subtest', test, **fields)


def _dispatch(request):
    mode = request.get('mode')
    if mode == 'call':
        try:
            target = importlib.import_module(request['module'])
            for name in request['function'].split('.'): target = getattr(target, name)
            value = target(*request['args'], **request['kwargs'])
            return {'mode': 'call', 'ok': True, 'value': value}
        except BaseException:
            return {'mode': 'call', 'ok': False, 'traceback': traceback.format_exc()}
    if mode != 'suite':
        raise PortRuntimeError('unknown trusted test worker mode')
    selectors = request['selectors']
    if not selectors or len(set(selectors)) != len(selectors):
        raise PortRuntimeError('empty or duplicate requested suite inventory')
    suite = unittest.defaultTestLoader.loadTestsFromNames(selectors)
    loaded = [test.id() for test in _flatten(suite)]
    if loaded != selectors:
        raise PortRuntimeError('loaded test inventory differs from requested selectors')
    result = _RecordingResult(bool(request.get('failfast')))
    suite.run(result)
    return {'mode': 'suite', 'requested_ids': selectors, 'loaded_ids': loaded,
            'events': result.events, 'tests_run': result.testsRun, 'should_stop': result.shouldStop,
            'outcome_counts': {'successes': result.successes, 'failures': len(result.failures),
                'errors': len(result.errors), 'skips': len(result.skipped),
                'expected_failures': len(result.expectedFailures), 'unexpected_successes': len(result.unexpectedSuccesses)}}


def _worker():
    binary_output = sys.stdout.buffer
    sys.stdout = sys.stderr
    for path in reversed((ROOT, ROOT / 'tests', ROOT / 'runtime', ROOT / 'tools')):
        sys.path.insert(0, str(path))
    identity = _identity()
    try:
        _check_identity(identity)  # Before reading request/importing requested code.
        print('Verified port worker: PyPy 3.11 (' + identity['version'] + ')', file=sys.stderr, flush=True)
        response = _dispatch(pickle.load(sys.stdin.buffer))
        code = 0
    except BaseException as exc:
        response = {'worker_error': str(exc)}
        code = 2
    response.update(protocol=PROTOCOL, identity=identity)
    pickle.dump(response, binary_output, protocol=4)
    binary_output.flush()
    return code


if __name__ == '__main__':
    if sys.argv[1:] != ['--worker']:
        raise SystemExit('port_test_runtime is a trusted test worker; use --worker')
    raise SystemExit(_worker())
