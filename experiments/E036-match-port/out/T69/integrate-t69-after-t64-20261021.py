"""Complete an existing port's ALL check after its own/falsifier pipeline ends."""
from pathlib import Path
import ast, datetime, hashlib, json, os, shlex, subprocess, sys, time

root = Path('/home/diego/projects/goal2-archaeology')
task = sys.argv[1]
tree, own_unit, own_log, success, frozen_file, module = {
    'T64': ('task-T64-port-ball', 'goal2-t64-validation-resume-20261021',
            't64-validation-resume-20261021.log', 'T64 own62 and3 F40 falsifiers passed.',
            'own-falsifier-input-20261020T163810Z.json', 'ball'),
    'T69': ('agent-aca0f4fd155445184', 'goal2-t69-after-t64-20261021',
            't69-after-t64-20261021.log', 'T69 recovered own62 and three O8 falsifiers PASS;',
            'own-falsifier-input-20261020T164316Z.json', 'frame'),
}[task]
work = root / '.claude/worktrees' / tree
out = work / 'experiments/E036-match-port/out' / task
print('Waiting for existing own/falsifier pipeline; no slot held', flush=True)
while subprocess.run(['systemctl', '--user', 'is-active', '--quiet', own_unit]).returncode == 0:
    time.sleep(20)
assert success in (root / '.cache' / own_log).read_text(), 'Own/falsifier pipeline failed; inspect complete logs'
frozen = json.loads((out / frozen_file).read_text())
hashes = frozen['source_sha256']
def verify():
    assert all(hashlib.sha256((work / name).read_bytes()).hexdigest() == digest
               for name, digest in hashes.items()), 'Frozen runtime changed'
verify()
main = '53d7ef5ec445aebc5f20d053f05d1db008db771e'
subprocess.run(['git', 'merge-base', '--is-ancestor', main, 'HEAD'], cwd=work, check=True)
live_main = subprocess.check_output(['gh', 'api', 'repos/diegoami/goal2-archaeology/commits/main', '--jq', '.sha'], cwd=root, text=True).strip()
assert live_main == main, 'Approved main advanced; main must integrate it explicitly before this run'
stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
env = os.environ.copy()
env.update(HARNESS_SESSION_FAMILY='openai', HARNESS_CLIENT='codex', HARNESS_HEAVY_SLOTS='4',
           PYTHONPATH=str(work / 'runtime'), TMPDIR=str(work / '.cache/tmp'))
sys.path[:0] = [str(work / 'runtime'), str(work / 'experiments/E036-match-port')]
import compare, families, records
addresses = sorted(ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse((work / f'runtime/original_match/port/{module}.py').read_text()))
                   if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'port')
paths = []
def save(message):
    names = [str(p.relative_to(work)) for p in paths if p.exists()]
    subprocess.run(['git', 'add', '--', *names], cwd=work, check=True)
    if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=work).returncode:
        subprocess.run(['git', 'commit', '-m', task + ': ' + message], cwd=work, check=True)
        subprocess.run(['git', 'push', 'origin', 'HEAD'], cwd=work, check=True)
receipt = out / f'integration-input-{stamp}.json'
receipt.write_text(json.dumps({'source_sha256': hashes, 'approved_main': main,
    'input_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=work, text=True).strip(),
    'review_policy': 'Owner 2026-10-21: checks plus green CI; one milestone review for port stage',
    'scope': 'Integrated ALL on approved main; final combination replay follows any other port merges'}, indent=2) + '\n')
method = out / f'integration-method-{stamp}.py'
method.write_bytes(Path(__file__).read_bytes())
paths.extend((receipt, method))
jobs = []
sets = []
for half in 'ab':
    previous = root / '.claude/worktrees/task-T63-port-positioning/experiments/E036-match-port/out/T63' / f'all-main53-{half}.args'
    words = shlex.split(previous.read_text().splitlines()[1])
    only = words[words.index('--only') + 1]
    sets.append(set(only.split(',')))
    candidate = out / f'all-main53-{stamp}-{half}.jsonl'
    log = out / f'all-main53-{stamp}-{half}-run.txt'
    argfile = out / f'all-main53-{stamp}-{half}-args.json'
    args = ['/usr/bin/python3', '-B', 'experiments/E036-match-port/family.py', '--family', 'ALL',
            '--only', only, '--ports', 'all', '--workers', '2', '--time-limit', '3000',
            '--count', ','.join(addresses), '--out', str(candidate.relative_to(work))]
    argfile.write_text(json.dumps({'argv': args}, indent=2) + '\n')
    paths.extend((candidate, log, argfile))
    jobs.append((args, candidate, log))
assert len(sets[0]) == len(sets[1]) == 31 and not sets[0] & sets[1]
save('record frozen integrated ALL inputs')
procs = []
for args, candidate, log in jobs:
    stream = log.open('x')
    proc = subprocess.Popen(args, cwd=work, env=env, stdin=subprocess.DEVNULL, stdout=stream, stderr=subprocess.STDOUT)
    procs.append((proc, stream))
last = time.monotonic()
while any(proc.poll() is None for proc, stream in procs):
    if time.monotonic() - last >= 1200:
        save('checkpoint integrated ALL progress')
        last = time.monotonic()
    time.sleep(20)
for proc, stream in procs:
    stream.close()
save('preserve integrated ALL worker output')
verify()
assert all(proc.returncode == 0 for proc, stream in procs), 'Integrated worker failed; retain raw evidence and inspect'
candidate = out / ('all.jsonl' if task == 'T64' else 'all-final-20261020.jsonl')
assert not candidate.exists(), 'Do not overwrite prior evidence'
with candidate.open('xb') as stream:
    for args, part, log in jobs:
        stream.write(part.read_bytes())
paths.append(candidate)
rows = compare.load(candidate)
assert set(rows) == sets[0] | sets[1] and len(rows) == 62
for row in rows.values():
    records.validate(row)
refs = {}; expected = {}
for family in families.select('ALL', families.discover()):
    refs.update(compare.load(work / family.reference)); expected.update(family.expected())
lines, ok = compare.check(refs, rows, expected, image_sha256=families.image_sha256())
matrix = {ident: {a: {'entry': row['counts'].get(a, 0), 'port_calls': row['port_calls'].get(a, 0)} for a in addresses}
          for ident, row in rows.items()}
counts_equal = all(cell['entry'] == cell['port_calls'] for row in matrix.values() for cell in row.values())
result = out / f'integration-result-{stamp}.json'
result.write_text(json.dumps({'ok': ok, 'records': len(rows), 'counts_equal': counts_equal,
    'comparison': lines, 'matrix': matrix, 'candidate_sha256': hashlib.sha256(candidate.read_bytes()).hexdigest()}, indent=2) + '\n')
paths.append(result)
save('preserve strict integrated ALL comparison and calls')
print(lines[-1], 'counts_equal', counts_equal, flush=True)
assert ok and counts_equal
print(task, 'integrated ALL62 PASS; port-stage milestone review replaces per-PR review', flush=True)
