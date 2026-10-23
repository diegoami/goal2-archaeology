"""Run declared T73 falsifier witnesses concurrently, preserving every outcome.

Manifest: [{"variant": "name", "routine": "SSSS:OOOO", "only": "S/quick-1"}].
Each witness uses the production display profile and the actual family runner.
The original coverage record must show the selected routine's entry was reached.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from run_counted_family import ROOT, E036, sources

sys.path.insert(0, str(E036))
import compare
import families
import family


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--workers', type=int, default=16)
    a = ap.parse_args()
    manifest_path = ROOT / a.manifest
    manifest = json.loads(manifest_path.read_text())
    assert len({r['variant'] for r in manifest}) == len(manifest)
    out = (ROOT / a.out).resolve()
    out.relative_to((E036 / 'out/T73').resolve())
    out.mkdir(exist_ok=False)
    frozen = sources()
    profile = family.read_display_profile()
    reference = compare.load(ROOT / profile['reference'])
    original = compare.load(E036 / 'out/T73/coverage-unported-desktop-20261023/coverage-unported.jsonl')
    specs = {mid: digest for fam in families.select('ALL', families.discover())
             for mid, digest in fam.expected().items()}
    launch = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'manifest': manifest, 'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
              'source_sha256': frozen}
    (out / 'launch.json').write_text(json.dumps(launch, indent=2) + '\n')

    def run(row):
        name = row['variant']
        assert name and all(c.islower() or c.isdigit() or c == '-' for c in name), name
        only = row['only'].split(',')
        assert only and len(set(only)) == len(only)
        for mid in only:
            assert original[mid]['counts'][row['routine']] > 0, (name, mid, 'unreached original entry')
        cmd = [sys.executable, '-B', str(E036 / 'family.py'), '--family', 'ALL', '--only', row['only'],
               '--ports', 'display', '--variant', 'display.' + name, '--count', row['routine'],
               '--workers', '1', '--checkpoint', str(ROOT / '.cache/checkpoints' / out.name / name),
               '--time-limit', '6000', '--stretch-limit', '1200', '--out', str(out / f'{name}.jsonl')]
        with (out / f'{name}.log').open('x') as log:
            log.write('COMMAND: ' + repr(cmd) + '\n')
            log.flush()
            exit_code = subprocess.run(cmd, cwd=ROOT, env=dict(os.environ, HARNESS_HEAVY_SLOTS='32'),
                                       stdout=log, stderr=subprocess.STDOUT).returncode
        result = {'variant': name, 'routine': row['routine'], 'runner_exit': exit_code, 'caught': False}
        path = out / f'{name}.jsonl'
        if not path.exists():
            return result
        try:
            candidate = compare.load(path)
            assert set(candidate) == set(only)
            assert compare.candidate_display_profile(candidate, True) is not None
            for rec in candidate.values():
                assert rec['variant'] == 'display.' + name
                assert rec['port_calls'][row['routine']] == rec['counts'][row['routine']]
            lines, ok = compare.check(reference, candidate, {mid: specs[mid] for mid in only},
                                      expect='differ', no_screen=True, strict_display=True,
                                      image_sha256=families.image_sha256())
            (out / f'{name}-compare.log').write_text('\n'.join(lines) + '\n')
            result['caught'] = ok
            result['completed'] = {mid: not bool(compare.completed(rec)) for mid, rec in candidate.items()}
            result['differences'] = {mid: compare.differences(reference[mid], rec, True, True)
                                     for mid, rec in candidate.items() if not compare.completed(rec)}
        except (compare.Malformed, AssertionError, KeyError) as exc:
            result['audit_error'] = str(exc)
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
        results = list(pool.map(run, manifest))
    current = sources()
    changed = [p for p in sorted(set(frozen) | set(current)) if frozen.get(p) != current.get(p)]
    summary = {'source_changes': changed, 'results': results,
               'all_caught': not changed and all(r['caught'] for r in results)}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'variants': len(results), 'caught': sum(r['caught'] for r in results),
                      'source_changes': changed}), flush=True)
    return 0 if summary['all_caught'] else 1


if __name__ == '__main__':
    sys.exit(main())
