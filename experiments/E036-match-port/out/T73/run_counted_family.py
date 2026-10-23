"""Run a counted T73 family in desktop shards, retaining a source manifest.

Each invocation requires a new output directory. Family workers take heavy slots
themselves. The final comparison always uses the strict declared display profile.
"""
import argparse
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    paths = sorted((ROOT / 'runtime/original_match').rglob('*.py'))
    paths += [E036 / name for name in ('family.py', 'families.py', 'records.py', 'compare.py')]
    paths += sorted((E036 / 'families/display').glob('*'))
    return {str(p.relative_to(ROOT)): digest(p) for p in paths if p.is_file()}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', required=True, help='new directory under out/T73')
    ap.add_argument('--ports', choices=('display', 'all'), default='display')
    ap.add_argument('--purpose', required=True)
    ap.add_argument('--shards', type=int, default=16)
    a = ap.parse_args()
    out = (ROOT / a.out).resolve()
    out.relative_to((E036 / 'out/T73').resolve())
    out.mkdir(exist_ok=False)
    frozen = sources()
    count = subprocess.check_output([sys.executable, str(E036 / 'out/T73/coverage_addresses.py'),
                                     '--entries'], cwd=ROOT, text=True).strip()
    plan = json.loads(subprocess.check_output([sys.executable, str(E036 / 'shards.py'), 'plan',
                                              '--family', 'ALL', '--shards', str(a.shards)], cwd=ROOT))
    launch = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'ports': a.ports, 'count': count, 'purpose': a.purpose, 'source_sha256': frozen}
    (out / 'launch.json').write_text(json.dumps(launch, indent=2) + '\n')
    (out / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
    env = dict(os.environ, HARNESS_HEAVY_SLOTS='32')

    def run(shard):
        i = shard['shard']
        cmd = [sys.executable, '-B', str(E036 / 'family.py'), '--family', 'ALL',
               '--only', shard['only'], '--workers', '2', '--ports', a.ports, '--count', count,
               '--checkpoint', str(ROOT / '.cache/checkpoints' / out.name / f'shard-{i}'),
               '--time-limit', '6000', '--stretch-limit', '1200',
               '--out', str(out / f'shard-{i}.jsonl')]
        start = time.monotonic()
        with (out / f'shard-{i}.log').open('x') as log:
            log.write('COMMAND: ' + repr(cmd) + '\n')
            log.flush()
            result = subprocess.run(cmd, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        return {'shard': i, 'exit_code': result.returncode, 'seconds': time.monotonic() - start}

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.shards) as pool:
        results = list(pool.map(run, plan['include']))
    (out / 'timing.json').write_text(json.dumps(results, indent=2) + '\n')
    current = sources()
    changed = [p for p in sorted(set(frozen) | set(current)) if frozen.get(p) != current.get(p)]
    result = {'purpose': a.purpose, 'source_changes': changed, 'shard_failures':
              [r for r in results if r['exit_code']], 'compare_exit': None, 'calls_audit_exit': None}
    if not changed and not result['shard_failures']:
        with (out / 'collect.log').open('x') as log:
            subprocess.run([sys.executable, str(E036 / 'shards.py'), 'collect', '--family', 'ALL',
                            '--out', str(out / 'family.jsonl'),
                            *[str(out / f'shard-{s["shard"]}.jsonl') for s in plan['include']]],
                           cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=True)
        for name, command in (
            ('compare', [str(E036 / 'compare.py'), '--family', 'ALL', '--no-screen',
                         '--candidate', str(out / 'family.jsonl')]),
            ('calls_audit', [str(E036 / 'out/T73/audit_counted_calls.py'), str(out / 'family.jsonl')]),
        ):
            with (out / f'{name}.log').open('x') as log:
                result[f'{name}_exit'] = subprocess.run([sys.executable, '-B', *command], cwd=ROOT,
                                                       stdout=log, stderr=subprocess.STDOUT).returncode
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return 0 if not changed and not result['shard_failures'] and result['compare_exit'] == 0 and result['calls_audit_exit'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
