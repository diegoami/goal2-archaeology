"""In-place mutation sweep of the model and the checker (T32 rework round 1).

Every module-level int constant of runtime/model/confidence.py and of
check_confidence.py is shifted by +1 and by -1; named behaviour mutants are
applied; every `raise` statement of both files is deleted (replaced by
`pass`). Each mutant runs tests.test_model_confidence with a timeout; a
mutant is KILLED when the tests fail. Sources are restored in finally and on
SIGINT/SIGTERM, and their sha256 is checked afterwards.
Usage: mutation_sweep.py <new log path inside the worktree>
"""
import ast
import hashlib
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'runtime/model/confidence.py'
CHECKER = ROOT / 'experiments/E018-q016-confidence/check_confidence.py'
COMMAND = [sys.executable, '-m', 'unittest', 'tests.test_model_confidence']
TIMEOUT = 60

BEHAVIOUR = {
    MODEL: [
        ('reverse expected margin', 'opponent_rating - own_rating', 'own_rating - opponent_rating'),
        ('ignore continent', '(CONTINENT_BASE - continent)', '(CONTINENT_BASE - 1)'),
        ('ignore continent rank', '(CONTINENT_RANK_BASE - continent_rank)', '(CONTINENT_RANK_BASE - 1)'),
        ('ignore world rank', 'WORLD_RANK_BASE - world_rank', 'WORLD_RANK_BASE - 1'),
        ('wrong doubling predicate', '(winner == side) == (side == 0 or bool(special_kind))', '(winner == side) != (side == 0 or bool(special_kind))'),
        ('draw treated as win', 'if winner != 2:', 'if winner != 0:'),
        ('R3 equal scores take the draw branch', 'if winner != 2:', 'if winner != 2 and scores[0] != scores[1]:'),
        ('doubling ignores special kind', '(side == 0 or bool(special_kind))', '(side == 0)'),
        ('R5 substitute skips the result term', "base = change(before, delta) if role == 'substitute' else before", 'base = before'),
        ('unused gets the result term', "base = change(before, delta) if role == 'substitute' else before", 'base = change(before, delta)'),
        ('drop persistence', 'if persist:', 'if False:'),
    ],
    CHECKER: [
        ('set aside checks only the first case', 'for case in cases:\n        failures = declared_input_failures(case)',
         'for case in cases[:1]:\n        failures = declared_input_failures(case)'),
        ('set aside checks only the first defect', 'for defect in defects:', 'for defect in defects[:1]:'),
        ('set aside by any check failure', 'if defect not in failures:', 'if not failures:'),
        ('kept record skips declared inputs', 'failures = declared_input_failures(case)\n    if failures:',
         'failures = {}\n    if failures:'),
        ('kept mismatch ignored', 'return int(matches != total)', 'return 0'),
        ('empty set accepted', 'if not total:', 'if False:'),
        ('run/trace equality dropped', "if cases != records[trace_name]['cases']:", 'if False:'),
        ('special kind ignored', 'special = bool(table[kind // 8] & (1 << (kind % 8)))', 'special = False'),
    ],
}


def int_constants(path, text):
    lines = text.splitlines(keepends=True)
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and type(node.value.value) is int:
            value = node.value
            for delta in (1, -1):
                changed = lines.copy()
                line = changed[value.lineno - 1]
                changed[value.lineno - 1] = line[:value.col_offset] + str(value.value + delta) + line[value.end_col_offset:]
                yield f'{node.targets[0].id} {value.value}->{value.value + delta}', ''.join(changed)


def raise_deletions(text):
    lines = text.splitlines(keepends=True)
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Raise):
            if node.lineno != node.end_lineno:
                raise ValueError(f'multi-line raise at {node.lineno}')
            changed = lines.copy()
            line = changed[node.lineno - 1]
            changed[node.lineno - 1] = line[:node.col_offset] + 'pass\n'
            yield f'delete raise at line {node.lineno}: {line.strip()[:70]}', ''.join(changed)


def clear_bytecode():
    for path in (MODEL, CHECKER):
        for cache in (path.parent / '__pycache__').glob(path.stem + '.*.pyc'):
            cache.unlink()


def main():
    destination = ROOT / sys.argv[1]
    if not destination.resolve().is_relative_to(ROOT):
        raise ValueError('log must remain inside worktree')
    originals = {path: path.read_text() for path in (MODEL, CHECKER)}
    digests = {path: hashlib.sha256(text.encode()).hexdigest() for path, text in originals.items()}
    mutants = []
    for path, text in originals.items():
        mutants += [(path, label, changed) for label, changed in int_constants(path, text)]
        for label, old, new in BEHAVIOUR[path]:
            if text.count(old) != 1:
                raise ValueError(f'nonunique mutation: {label}')
            mutants.append((path, label, text.replace(old, new)))
        mutants += [(path, label, changed) for label, changed in raise_deletions(text)]

    def restore(*_):
        for path, text in originals.items():
            path.write_text(text)
        clear_bytecode()

    signal.signal(signal.SIGTERM, lambda *a: (restore(), sys.exit(2)))
    with destination.open('x') as log:
        killed = 0
        try:
            clear_bytecode()
            baseline = subprocess.run(COMMAND, cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT)
            log.write(f'BASELINE exit={baseline.returncode} {baseline.stderr.strip().splitlines()[-1]}\n')
            if baseline.returncode:
                return 1
            for path, label, text in mutants:
                path.write_text(text)
                clear_bytecode()
                try:
                    result = subprocess.run(COMMAND, cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT)
                    code, tail = result.returncode, result.stderr.strip().splitlines()[-1]
                except subprocess.TimeoutExpired:
                    code, tail = 'timeout', 'timeout'
                path.write_text(originals[path])
                status = 'KILLED' if code != 0 else 'SURVIVED'
                killed += code != 0
                log.write(f'{path.relative_to(ROOT)}: {label}: {status} exit={code} {tail}\n')
                log.flush()
            log.write(f'killed: {killed}/{len(mutants)}\n')
            print(f'killed: {killed}/{len(mutants)}')
        finally:
            restore()
            for path, digest in digests.items():
                if hashlib.sha256(path.read_text().encode()).hexdigest() != digest:
                    raise RuntimeError(f'{path} not restored')
            log.write('sources restored, sha256 unchanged\n')
        return int(killed != len(mutants))


if __name__ == '__main__':
    raise SystemExit(main())
