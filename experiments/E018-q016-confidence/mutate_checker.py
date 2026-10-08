"""Remove each checker guard in place; retain results and restore source."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'experiments/E018-q016-confidence/check_confidence.py'


def main():
    original = SOURCE.read_text()
    edits = [
        ('defective consistency', 'if not failures:', 'if False:'),
        ('empty comparison', 'if not total:', 'if False:'),
        ('kept mismatch', 'return int(matches != total)', 'return 0'),
    ]
    killed = 0
    try:
        with (ROOT / sys.argv[1]).open('x') as log:
            for label, old, new in edits:
                assert original.count(old) == 1
                SOURCE.write_text(original.replace(old, new))
                for cache in (SOURCE.parent / '__pycache__').glob('check_confidence.*.pyc'):
                    cache.unlink()
                result = subprocess.run([sys.executable, '-m', 'unittest', '-v',
                                         'tests.test_model_confidence.CheckerTests'],
                                        cwd=ROOT, capture_output=True, text=True, timeout=30)
                log.write(f'{label}: exit={result.returncode}\n{result.stderr}\n')
                killed += result.returncode != 0
            log.write(f'killed: {killed}/3\n')
        print(f'killed: {killed}/3')
        return int(killed != 3)
    finally:
        SOURCE.write_text(original)
        for cache in (SOURCE.parent / '__pycache__').glob('check_confidence.*.pyc'):
            cache.unlink()


if __name__ == '__main__':
    raise SystemExit(main())
