"""Measure integrated desktop speed on an immutable committed test bundle.

This is a diagnostic speed sample, not final T73 acceptance. Extraction contains
no Git metadata, branch or worktree; ongoing implementer edits cannot affect it.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'experiments/E036-match-port/out/T73/integrated-desktop-speed-20261023-a'
PIN = '585891d8'
head = subprocess.check_output(['git', 'rev-parse', PIN], cwd=ROOT, text=True).strip()
OUT.mkdir(exist_ok=False)
bundle = Path('/tmp') / ('T73-integrated-speed-' + head)
bundle.mkdir(exist_ok=False)
files = ['runtime', 'tools/heavy.sh', 'experiments/E036-match-port/families']
files += [str(p.relative_to(ROOT)) for p in (ROOT / 'experiments/E036-match-port').glob('*.py')]
archive = subprocess.check_output(['git', 'archive', head, *files], cwd=ROOT)
with tarfile.open(fileobj=io.BytesIO(archive)) as tf:
    tf.extractall(bundle, filter='data')
cmd = [sys.executable, '-B', str(bundle / 'experiments/E036-match-port/family.py'),
       '--family', 'ALL', '--only', 'S/quick-1,S/quick-30', '--ports', 'all', '--workers', '2',
       '--cache', str(ROOT / '.cache/dl'), '--checkpoint', str(ROOT / '.cache/checkpoints/T73-speed-a'),
       '--time-limit', '6000', '--stretch-limit', '1200', '--out', str(OUT / 'sample.jsonl')]
(OUT / 'launch.json').write_text(json.dumps({'purpose': 'Diagnostic speed sample, not final acceptance',
    'head': head, 'archive_sha256': hashlib.sha256(archive).hexdigest(),
    'temporary_test_bundle': str(bundle), 'command': cmd}, indent=2) + '\n')
start = time.monotonic()
with (OUT / 'family.log').open('x') as log:
    result = subprocess.run(cmd, cwd=bundle, env=dict(os.environ, HARNESS_HEAVY_SLOTS='32'),
                            stdout=log, stderr=subprocess.STDOUT)
(OUT / 'result.json').write_text(json.dumps({'runner_exit': result.returncode,
                                           'wall_seconds': time.monotonic() - start}, indent=2) + '\n')
print('Integrated speed sample closed:', result.returncode, flush=True)
sys.exit(result.returncode)
