"""T73: independent original-run access evidence, sharded across the desktop.

The observer must leave every match identical to T57. No candidate or mask is
installed. The watcher explicitly leaves unobserved stack bytes unmaskable.
"""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
E036 = ROOT / 'experiments/E036-match-port'
OUT = E036 / 'out/T73/watch-all-desktop-20261023'
OUT.mkdir(exist_ok=False)
WATCH = E036 / 'out/T73/watch_accesses.py'
watch_source = WATCH.read_bytes()
(OUT / 'watch-source.py').write_bytes(watch_source)
plan = json.loads(subprocess.check_output([
    sys.executable, str(E036/'shards.py'), 'plan', '--family', 'ALL', '--shards', '32',
], cwd=ROOT))
(OUT / 'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
receipt = {'observer_sha256': hashlib.sha256(watch_source).hexdigest(),
           'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
           'shards': 32, 'slots': 32, 'weight_per_shard': 1, 'ports': [], 'mask': []}
(OUT / 'launch.json').write_text(json.dumps(receipt, indent=2)+'\n')
env = dict(os.environ, HARNESS_HEAVY_SLOTS='32')

def run(shard):
    i = shard['shard']
    cmd = [str(ROOT/'tools/heavy.sh'), f'T73-watch-s{i}', '--', sys.executable, '-B', str(WATCH),
           '--only', shard['only'], '--fast-pc', '--gzip', '--time-limit', '6000',
           '--out-dir', str(OUT/f'shard-{i}')]
    start = time.monotonic()
    with (OUT / f'shard-{i}.log').open('x') as log:
        log.write('COMMAND: '+repr(cmd)+'\n'); log.flush()
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        (OUT/f'shard-{i}-process.json').write_text(json.dumps({'pid': proc.pid, 'command': cmd})+'\n')
        code = proc.wait()
    return {'shard': i, 'exit_code': code, 'seconds': time.monotonic()-start}

with concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
    results = list(pool.map(run, plan['include']))
(OUT/'timing.json').write_text(json.dumps(results, indent=2)+'\n')
if any(r['exit_code'] for r in results):
    sys.exit('One or more watches failed; preserve and inspect each shard.')
assert WATCH.read_bytes() == watch_source, 'Observer source changed during the evidence run'
paths = [str(p) for s in plan['include'] for p in sorted((OUT/f'shard-{s["shard"]}').glob('*-record.jsonl'))]
with (OUT/'collect.log').open('x') as log:
    subprocess.run([sys.executable, str(E036/'shards.py'), 'collect', '--family', 'ALL',
                    '--out', str(OUT/'unhooked-records.jsonl'), *paths], cwd=ROOT,
                   stdout=log, stderr=subprocess.STDOUT, check=True)
with (OUT/'compare.log').open('x') as log:
    subprocess.run([sys.executable, str(E036/'compare.py'), '--family', 'ALL',
                    '--candidate', str(OUT/'unhooked-records.jsonl')], cwd=ROOT,
                   stdout=log, stderr=subprocess.STDOUT, check=True)
print('COMPLETE: 62 original watched matches collected and strictly identical', flush=True)
