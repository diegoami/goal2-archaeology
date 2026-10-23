"""T72 desktop falsifiers: strict comparisons over the declared selected ids."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = ROOT / 'experiments/E036-match-port'
sys.path.insert(0, str(HERE))
import compare
import families

OUT = HERE / 'out/T72/falsifiers-acceptance-20261023'
OUT.mkdir(exist_ok=False)
PYTHON = sys.executable
env = dict(os.environ, HARNESS_HEAVY_SLOTS='32')
count = (HERE/'out/T72/coverage-addresses.txt').read_text().strip()
o8 = [m.id for f in families.select('O8', families.discover()) for m in f.matches]
reference = compare.load(HERE / 'out/T57/reference.jsonl')
jobs = [('confidence-plus-one', o8), ('rolled-energy-plus-one', o8), ('recovered-energy-plus-one', ['O8/c30-c44-friendly', 'O8/c64-c90-friendly'])]

def run(job):
    variant, ids = job
    target = OUT / (variant + '.jsonl')
    cmd = [PYTHON, '-B', str(HERE/'family.py'), '--family', 'ALL', '--only', ','.join(ids),
           '--ports', 'update', '--variant', 'update.'+variant, '--workers', '2',
           '--count', count, '--checkpoint', str(ROOT/'.cache/checkpoints'/('T72-acceptance-'+variant)),
           '--time-limit', '6000', '--stretch-limit', '1200', '--out', str(target)]
    with (OUT/(variant+'.log')).open('x') as log:
        log.write('COMMAND: '+repr(cmd)+'\n'); log.flush()
        result = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        return variant, result.returncode
    refs, expected = {}, {}
    for fam in families.select('ALL', families.discover()):
        log = compare.load(ROOT/fam.reference)
        for mid, digest in fam.expected().items():
            if mid in ids:
                refs[mid], expected[mid] = log[mid], digest
    lines, ok = compare.check(refs, compare.load(target), expected, 'differ', image_sha256=families.image_sha256())
    post = [mid for mid, rec in compare.load(target).items() if refs[mid]['after']['seed'] != rec['after']['seed'] or refs[mid]['after']['ranges']['records'] != rec['after']['ranges']['records']]
    ok = ok and set(post) == set(ids)
    lines.append('Post-update records or seed differ: '+repr(post))
    (OUT/(variant+'-compare.txt')).write_text('\n'.join(lines)+'\n')
    return variant, 0 if ok else 1

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    results = list(pool.map(run, jobs))
(OUT/'results.json').write_text(json.dumps(results, indent=2)+'\n')
print(results, flush=True)
sys.exit(0 if all(code == 0 for _, code in results) else 1)
