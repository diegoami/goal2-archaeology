"""Run the current tests against a committed version of one source file, in place.

Usage: red_against_head.py <rev> <source path> <log path>. The working copy
of the source is restored in finally; the log is opened exclusively.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    rev, source, log = sys.argv[1], ROOT / sys.argv[2], ROOT / sys.argv[3]
    for path in (source, log):
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError('paths must remain inside worktree')
    current = source.read_text()
    old = subprocess.run(['git', 'show', f'{rev}:{sys.argv[2]}'], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout
    with log.open('x') as out:
        try:
            source.write_text(old)
            for cache in (source.parent / '__pycache__').glob(source.stem + '.*.pyc'):
                cache.unlink()
            result = subprocess.run([sys.executable, '-m', 'unittest', 'tests.test_model_confidence'],
                                    cwd=ROOT, capture_output=True, text=True, timeout=60)
            out.write(f'{sys.argv[2]} at {rev}, tests of the working tree: exit={result.returncode}\n')
            out.write(result.stderr)
            print(f'exit={result.returncode}')
        finally:
            source.write_text(current)
            for cache in (source.parent / '__pycache__').glob(source.stem + '.*.pyc'):
                cache.unlink()


if __name__ == '__main__':
    main()
