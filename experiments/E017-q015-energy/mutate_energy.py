"""DW2: mutate each declared model constant in place, by +1 AND -1 (review round 1 R2: a +1-only
sweep missed REST_THRESHOLD 16->15), and the reviewer's named operator mutants, with clean bytecode.

No copied module and no runtime monkeypatch: each subprocess imports the real
energy.py. The source is restored even on a failed test/timeout. The supplied
log path is exclusive-create so a measurement is never overwritten.
"""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'runtime/model/energy.py'
COMMAND = [sys.executable, '-m', 'unittest', '-v', 'tests.test_model_energy']


# the reviewer's operator mutants (review round 1 R3, R4), each pattern unique in energy.py
OPERATOR_MUTANTS = [
    ('watched floor unsigned', '        if signed(out[ENERGY]) > FLOOR:', '        if out[ENERGY] > FLOOR:'),
    ('watched floor >=', '        if signed(out[ENERGY]) > FLOOR:', '        if signed(out[ENERGY]) >= FLOOR:'),
    ('quick floor unsigned', 'QUICK_PERIOD == 0 and signed(out[ENERGY]) > FLOOR', 'QUICK_PERIOD == 0 and out[ENERGY] > FLOOR'),
    ('quick floor >=', 'QUICK_PERIOD == 0 and signed(out[ENERGY]) > FLOOR', 'QUICK_PERIOD == 0 and signed(out[ENERGY]) >= FLOOR'),
    ('draw lower bound 0', 'if not 1 <= value <= bound:', 'if not 0 <= value <= bound:'),
]


def clear_bytecode():
    for path in (MODEL.parent / '__pycache__').glob('energy.*.pyc'):
        path.unlink()


def main():
    destination = ROOT / sys.argv[1]
    if not destination.resolve().is_relative_to(ROOT):
        raise ValueError('log must stay inside the worktree')
    original = MODEL.read_text()
    lines = original.splitlines(keepends=True)
    mutants = []
    for node in ast.parse(original).body:
        if not isinstance(node, ast.Assign):
            continue
        names = node.targets[0]
        values = node.value
        if isinstance(names, ast.Tuple):
            pairs = zip(names.elts, values.elts)
        else:
            pairs = [(names, values)]
        for name, value in pairs:
            if isinstance(name, ast.Name) and isinstance(value, ast.Constant):
                for delta in (+1, -1):
                    mutants.append((name.id, value, delta))
    with destination.open('x') as log:
        log.write('In-place +1 and -1 sweep of every top-level numeric model constant, then the named operator mutants\n')
        log.write('Command: python3 -m unittest -v tests.test_model_energy\n')
        log.write('Per subprocess timeout: 30 seconds; source restored in finally\n')
        killed = 0
        try:
            clear_bytecode()
            baseline = subprocess.run(COMMAND, cwd=ROOT, capture_output=True,
                                      text=True, timeout=30)
            log.write(f'BASELINE exit={baseline.returncode}\n{baseline.stderr}\n')
            if baseline.returncode:
                return 1
            edits = []
            for name, value, delta in mutants:
                changed = lines.copy()
                line = changed[value.lineno - 1]
                changed[value.lineno - 1] = (line[:value.col_offset] +
                    str(value.value + delta) + line[value.end_col_offset:])
                edits.append((f'{name} {value.value}->{value.value + delta}', ''.join(changed)))
            for label, old, new in OPERATOR_MUTANTS:
                if original.count(old) != 1:
                    raise ValueError(f'operator mutant {label}: pattern not unique')
                edits.append((label, original.replace(old, new)))
            for label, text in edits:
                MODEL.write_text(text)
                clear_bytecode()
                try:
                    result = subprocess.run(COMMAND, cwd=ROOT, capture_output=True,
                                            text=True, timeout=30)
                except subprocess.TimeoutExpired:
                    log.write(f'{label}: TIMEOUT (not a kill)\n')
                    continue
                status = 'KILLED' if result.returncode else 'SURVIVED'
                killed += result.returncode != 0
                log.write(f'{label}: {status} exit={result.returncode}\n')
                if result.returncode:
                    log.write(result.stderr + '\n')
                log.flush()
            log.write(f'killed: {killed}/{len(edits)}\n')
            print(f'killed: {killed}/{len(edits)}; log: {sys.argv[1]}')
            return int(killed != len(edits))
        finally:
            MODEL.write_text(original)
            clear_bytecode()


if __name__ == '__main__':
    raise SystemExit(main())
