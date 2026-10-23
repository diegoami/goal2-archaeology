import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time

root = Path('/home/diego/projects/goal2-archaeology')
out = root / 'experiments/E036-match-port/out/T71/own-desktop-r2-20261023'
python = '/home/diego/.local/bin/python3.12'
script = 'experiments/E036-match-port/'
plan = json.loads(subprocess.check_output([python, script+'shards.py', 'plan', '--family', 'ALL', '--shards', '16'], cwd=root))
(out/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
count = (root/'experiments/E036-match-port/out/T71/coverage-addresses.txt').read_text().strip()
env = dict(os.environ, HARNESS_HEAVY_SLOTS='32')
def run(shard):
    n = shard['shard']
    cmd = [python, '-B', script+'family.py', '--family', 'ALL', '--only', shard['only'], '--workers', '2', '--checkpoint', f'.cache/checkpoints/T71-own-r2-s{n}', '--out', str(out/f'shard-{n}.jsonl'), '--count', count, '--ports', 'postmatch', '--time-limit', '6000', '--stretch-limit', '1200']
    start = time.time()
    with (out/f'shard-{n}.log').open('x') as log:
        result = subprocess.run(cmd, cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
    return dict(shard=n, exit_code=result.returncode, seconds=time.time()-start)
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    results = list(pool.map(run, plan['include']))
(out/'timing.json').write_text(json.dumps(results, indent=2)+'\n')
if any(r['exit_code'] for r in results):
    sys.exit('one or more shards failed; see timing.json')
with (out/'collect.log').open('x') as log:
    subprocess.run([python, script+'shards.py', 'collect', '--family', 'ALL', '--out', str(out/'own.jsonl'), *[str(out/f'shard-{s["shard"]}.jsonl') for s in plan['include']]], cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
with (out/'compare.log').open('x') as log:
    subprocess.run([python, script+'compare.py', '--family', 'ALL', '--candidate', str(out/'own.jsonl')], cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
print('COMPLETE: postmatch ALL collected and compared', flush=True)
