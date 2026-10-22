"""Continue existing T64 validation only after the frozen focused controls pass."""
import ast
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path('/home/diego/projects/goal2-archaeology')
WORK = ROOT / '.claude/worktrees/task-T64-port-ball'
OUT = WORK / 'experiments/E036-match-port/out/T64'
UNIT = 'goal2-t64-flow-full-r1.service'
CONTROL = OUT / 'flow-controls-0a078570ea-r1.txt'
MANIFEST = OUT / 'unit-input-0a078570ea.json'
STAMP = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
PREFIX = 'smoke-' + STAMP
owned = []
env = os.environ.copy()
env.update(HARNESS_SESSION_FAMILY='openai', HARNESS_CLIENT='codex', HARNESS_HEAVY_SLOTS='4',
           PYTHONPATH=str(WORK / 'runtime'), TMPDIR=str(WORK / '.cache/tmp'))
(WORK / '.cache/tmp').mkdir(parents=True, exist_ok=True)

def save(message):
    paths = [str(p.relative_to(WORK)) for p in owned if p.exists()]
    if not paths:
        return
    subprocess.run(['git', 'add', '--', *paths], cwd=WORK, check=True)
    if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=WORK).returncode:
        subprocess.run(['git', 'commit', '-m', 'T64: ' + message], cwd=WORK, check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'HEAD'], cwd=WORK, check=True)

print('Waiting for frozen 33-test baseline and five controls; no family launched', flush=True)
while True:
    state = subprocess.check_output(['systemctl', '--user', 'show', UNIT, '-p', 'ActiveState', '--value'], text=True).strip()
    data = CONTROL.read_text() if CONTROL.exists() else ''
    passed = ('Baseline: 33 synthetic tests PASS' in data
              and data.count('control caught by assertion, no setup errors') == 5
              and 'T64 flow controls PASS; source files untouched' in data)
    if state not in ('active', 'activating', 'deactivating'):
        if not passed:
            print('ALARM: focused controls ended without complete PASS; no smoke launched', flush=True)
            sys.exit(1)
        break
    print(datetime.datetime.now(datetime.timezone.utc).isoformat(), 'focused controls', state, flush=True)
    time.sleep(60)

inputs = json.loads(MANIFEST.read_text())
hashes = inputs['source_sha256']
assert all(hashlib.sha256((WORK / p).read_bytes()).hexdigest() == h for p, h in hashes.items()), 'Source changed; do not test a different input'
tree = ast.parse((WORK / 'runtime/original_match/port/ball.py').read_text())
addresses = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'port':
        addresses.append(ast.literal_eval(node.args[0]))
assert len(set(addresses)) == 21
candidate = OUT / (PREFIX + '.jsonl')
log = OUT / (PREFIX + '-run.txt')
receipt = OUT / (PREFIX + '-input.json')
args = ['/usr/bin/python3', '-B', 'experiments/E036-match-port/family.py', '--family', 'F40',
        '--only', 'F40/e032-0101', '--ports', 'ball', '--workers', '1', '--time-limit', '3000',
        '--count', ','.join(sorted(addresses)), '--out', str(candidate.relative_to(WORK))]
assert not any(p.exists() for p in (candidate, log, receipt))
receipt.write_text(json.dumps({'scope': 'One-match strict smoke only; not ALL-family acceptance',
    'argv': args, 'source_sha256': hashes, 'focused_log_sha256': hashlib.sha256(CONTROL.read_bytes()).hexdigest(),
    'input_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=WORK, text=True).strip()}, indent=2) + '\n')
owned.extend((receipt, candidate, log))
save('record gated strict smoke inputs after focused controls PASS')
with log.open('x') as stream:
    proc = subprocess.Popen(args, cwd=WORK, env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
    last = time.monotonic()
    while proc.poll() is None:
        if time.monotonic() - last >= 1200:
            save('checkpoint gated strict smoke progress')
            last = time.monotonic()
        time.sleep(30)
save('preserve strict smoke raw outputs')
assert proc.returncode == 0, 'ALARM: smoke worker failed; inspect full retained log'
assert all(hashlib.sha256((WORK / p).read_bytes()).hexdigest() == h for p, h in hashes.items()), 'Source changed during smoke'
sys.path[:0] = [str(WORK / 'runtime'), str(WORK / 'experiments/E036-match-port')]
import compare
import families
import records
rows = compare.load(candidate)
assert set(rows) == {'F40/e032-0101'}
for row in rows.values():
    records.validate(row)
family = next(f for f in families.select('F40', families.discover()))
expected = {k: v for k, v in family.expected().items() if k in rows}
lines, ok = compare.check(compare.load(WORK / family.reference), rows, expected, image_sha256=families.image_sha256())
result = OUT / (PREFIX + '-result.json')
result.write_text(json.dumps({'scope': 'One-match strict smoke only; not ALL-family acceptance',
    'worker_exit': proc.returncode, 'ok': ok, 'comparison': lines,
    'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest()}, indent=2) + '\n')
owned.append(result)
save('preserve strict one-match smoke comparison')
print('\n'.join(lines), flush=True)
assert ok, 'ALARM: strict smoke mismatch; no acceptance families launched'
print('T64 strict one-match smoke PASS; full own/ALL families and review still required', flush=True)
