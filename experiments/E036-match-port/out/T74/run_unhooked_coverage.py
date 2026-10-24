"""Record original-only ALL63 branch/entry counts; immutable attempt1 outputs."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PYTHON = '/home/diego/.local/bin/python3.12'
counts = subprocess.check_output([PYTHON, str(OUT/'coverage_addresses.py')], text=True).strip()
command = [PYTHON, '-B', 'experiments/E036-match-port/family.py', '--family', 'ALL',
           '--workers', '2', '--time-limit', '900', '--count', counts,
           '--out', str(OUT/'coverage-unhooked-1.jsonl')]
sources = ['runtime/original_match/match.py', 'experiments/E036-match-port/family.py',
           'experiments/E036-match-port/families.py', 'experiments/E036-match-port/records.py',
           'experiments/E036-match-port/families/S.json']
receipt = {'head': subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
           'command': command, 'sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}}
(OUT/'coverage-unhooked-source-1.json').write_text(json.dumps(receipt,indent=2)+'\n')
with (OUT/'coverage-unhooked-1.log').open('x') as log:
    result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
(OUT/'coverage-unhooked-1.exit').write_text(str(result.returncode)+'\n')
