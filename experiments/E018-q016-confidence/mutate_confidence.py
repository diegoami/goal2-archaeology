"""In-place +/-1 sweep of every declared model constant; restore in finally."""
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / 'runtime/model/confidence.py'
COMMAND = [sys.executable, '-m', 'unittest', '-v', 'tests.test_model_confidence']


def clear_bytecode():
    for path in (MODEL.parent / '__pycache__').glob('confidence.*.pyc'):
        path.unlink()


def main():
    destination = ROOT / sys.argv[1]
    if not destination.resolve().is_relative_to(ROOT):
        raise ValueError('log must remain inside worktree')
    original = MODEL.read_text()
    lines = original.splitlines(keepends=True)
    edits = []
    for node in ast.parse(original).body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and type(node.value.value) is int:
            value = node.value
            for delta in (1, -1):
                changed = lines.copy()
                line = changed[value.lineno - 1]
                changed[value.lineno - 1] = line[:value.col_offset] + str(value.value + delta) + line[value.end_col_offset:]
                edits.append((f'{node.targets[0].id} {value.value}->{value.value + delta}', ''.join(changed)))
    for label, old, new in [
        ('reverse expected margin', 'opponent_rating - own_rating', 'own_rating - opponent_rating'),
        ('ignore continent', '(CONTINENT_BASE - continent)', '(CONTINENT_BASE - 1)'),
        ('ignore continent rank', '(CONTINENT_RANK_BASE - continent_rank)', '(CONTINENT_RANK_BASE - 1)'),
        ('ignore world rank', 'WORLD_RANK_BASE - world_rank', 'WORLD_RANK_BASE - 1'),
        ('wrong doubling predicate', '(winner == side) == (side == 0 or bool(special_kind))', '(winner == side) != (side == 0 or bool(special_kind))'),
        ('draw treated as win', 'if winner != 2:', 'if winner != 0:'),
        ('drop persistence', 'if persist:', 'if False:'),
    ]:
        if original.count(old) != 1:
            raise ValueError(f'nonunique mutation: {label}')
        edits.append((label, original.replace(old, new)))
    with destination.open('x') as log:
        killed = 0
        try:
            clear_bytecode()
            baseline = subprocess.run(COMMAND, cwd=ROOT, capture_output=True, text=True, timeout=30)
            log.write(f'BASELINE exit={baseline.returncode}\n{baseline.stderr}\n')
            if baseline.returncode:
                return 1
            for label, text in edits:
                MODEL.write_text(text)
                clear_bytecode()
                result = subprocess.run(COMMAND, cwd=ROOT, capture_output=True, text=True, timeout=30)
                status = 'KILLED' if result.returncode else 'SURVIVED'
                killed += result.returncode != 0
                log.write(f'{label}: {status} exit={result.returncode}\n{result.stderr}\n')
                log.flush()
            log.write(f'killed: {killed}/{len(edits)}\n')
            print(f'killed: {killed}/{len(edits)}')
            return int(killed != len(edits))
        finally:
            MODEL.write_text(original)
            clear_bytecode()


if __name__ == '__main__':
    raise SystemExit(main())
