"""Classify unresolved T73 body omissions over ALL using interleaved shards.

An omission is removable only if all 62 completed records remain strict exact.
Any difference is retained as a falsifier witness. All runs use the frozen code.
"""
import argparse
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from run_counted_family import ROOT, E036, sources
sys.path.insert(0, str(E036))
import compare
import families
import family


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    rows = json.loads((ROOT / a.manifest).read_text())
    assert len({r['variant'] for r in rows}) == len(rows)
    out = (ROOT / a.out).resolve()
    out.relative_to((E036 / 'out/T73').resolve())
    out.mkdir(exist_ok=False)
    frozen = sources()
    plan = json.loads(subprocess.check_output([sys.executable, str(E036 / 'shards.py'), 'plan',
                                             '--family', 'ALL', '--shards', '31'], cwd=ROOT))
    (out / 'launch.json').write_text(json.dumps({'head': subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'manifest': rows,
        'source_sha256': frozen, 'plan': plan}, indent=2) + '\n')
    for row in rows:
        assert row['variant'].startswith('omit-')
        (out / row['variant']).mkdir()

    def run(task):
        row, shard = task
        name, i = row['variant'], shard['shard']
        folder = out / name
        cmd = [sys.executable, '-B', str(E036 / 'family.py'), '--family', 'ALL', '--only', shard['only'],
               '--ports', 'display', '--variant', 'display.' + name, '--count', row['routine'],
               '--workers', '2', '--checkpoint', str(ROOT / '.cache/checkpoints' / out.name / name / str(i)),
               '--time-limit', '600', '--stretch-limit', '120', '--out', str(folder / f'shard-{i}.jsonl')]
        start = time.monotonic()
        with (folder / f'shard-{i}.log').open('x') as log:
            log.write('COMMAND: ' + repr(cmd) + '\n'); log.flush()
            result = subprocess.run(cmd, cwd=ROOT, env=dict(os.environ, HARNESS_HEAVY_SLOTS='32'),
                                    stdout=log, stderr=subprocess.STDOUT)
        return {'variant': name, 'shard': i, 'runner_exit': result.returncode,
                'seconds': time.monotonic() - start}

    # Spread each wave across variants, so one long family does not monopolize the queue.
    tasks = [(row, shard) for shard in plan['include'] for row in rows]
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
        timing = list(pool.map(run, tasks))
    (out / 'timing.json').write_text(json.dumps(timing, indent=2) + '\n')
    current = sources()
    changed = [p for p in sorted(set(frozen) | set(current)) if frozen.get(p) != current.get(p)]
    reference = compare.load(ROOT / family.read_display_profile()['reference'])
    expected = {mid: digest for fam in families.select('ALL', families.discover())
                for mid, digest in fam.expected().items()}
    results = []
    for row in rows:
        folder = out / row['variant']
        with (folder / 'collect.log').open('x') as log:
            collected = subprocess.run([sys.executable, str(E036 / 'shards.py'), 'collect', '--family', 'ALL',
                '--out', str(folder / 'family.jsonl'), *[str(folder / f'shard-{s["shard"]}.jsonl')
                for s in plan['include']]], cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        if collected.returncode:
            results.append({'variant': row['variant'], 'collection_failed': True}); continue
        candidate = compare.load(folder / 'family.jsonl')
        assert compare.candidate_display_profile(candidate, True) is not None
        for rec in candidate.values():
            assert rec['port_calls'][row['routine']] == rec['counts'][row['routine']]
        lines, exact = compare.check(reference, candidate, expected, no_screen=True,
                                    strict_display=True, image_sha256=families.image_sha256())
        (folder / 'compare.log').write_text('\n'.join(lines) + '\n')
        witnesses = {mid: compare.completed(rec) or compare.differences(reference[mid], rec, True, True)
                     for mid, rec in candidate.items()}
        results.append({'variant': row['variant'], 'routine': row['routine'], 'matches': len(candidate),
                        'strict_exact_all': exact, 'falsifier_witnesses': {m: d for m, d in witnesses.items() if d}})
    (out / 'summary.json').write_text(json.dumps({'source_changes': changed, 'results': results}, indent=2) + '\n')
    print(json.dumps({'source_changes': changed, 'results': results}), flush=True)
    return int(bool(changed) or any(r.get('collection_failed') for r in results))


if __name__ == '__main__':
    sys.exit(main())
