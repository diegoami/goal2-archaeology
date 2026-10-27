#!/usr/bin/env python3
"""T101 contract coverage and source integrity; not semantic or behavioural proof."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'notes/engine-study'))
from foundations.check import pin, sha, write_new

BASE = 'a42c2cbe91300c8ee261b82fa993e665ed3f3325'
ROUTINES = {
    'T101a': '419C 42CB 4354 4532 4649 474D 4B64'.split(),
    'T101b': '1F3C 1FDD 20E3 2218 4438 44C1 47C5 4A28'.split(),
    'T101c': '4D3F 8537 8889 8AE9 8C67 8CCA 8CF5 8E24 90C5 9119'.split(),
}
CHAPTERS = {'T101a': 'positioning', 'T101b': 'marking', 'T101c': 'movement'}


def validate(task, data, text):
    assert data['task'] == task and data['source_commit'] == BASE
    rows = data['routines']
    assert len(rows) == len(ROUTINES[task])
    assert {r['address'] for r in rows} == {'0791:' + a for a in ROUTINES[task]}
    for row in rows:
        assert all(row.get(k) for k in ['mechanism', 'fields', 'visible_effect', 'limits'])
    assert len(data['sections']) >= 3 and len(text.split()) >= 250
    assert all('## ' + s in text for s in data['sections'])
    assert len(data['examples']) >= 2
    for example in data['examples']:
        assert all(example.get(k) for k in ['id', 'inputs', 'steps', 'prediction', 'limits'])
    assert {'0791:' + a for a in ROUTINES[task]} <= {r['address'] for r in data['locations']}
    assert data['source_sha256']
    for name, digest in data['source_sha256'].items():
        raw = (ROOT / name).read_bytes()
        assert sha(raw) == digest, f'source hash differs: {name}'
        assert raw == subprocess.check_output(['git', 'show', f'{BASE}:{name}'], cwd=ROOT), name
    for loc in data['locations']:
        line = (ROOT / loc['file']).read_text().splitlines()[loc['line'] - 1]
        assert loc['address'] in line and sha(line.encode()) == loc['heading_sha256']


def controls(task, data, text):
    results = {}
    for case in ['missing-routine', 'missing-source', 'shifted-source', 'missing-examples']:
        broken = copy.deepcopy(data)
        if case == 'missing-routine':
            broken['routines'].pop()
        elif case == 'missing-source':
            broken['source_sha256'] = {}
        elif case == 'shifted-source':
            broken['locations'][0]['line'] += 1
        else:
            broken['examples'] = []
        try:
            validate(task, broken, text)
        except (AssertionError, KeyError):
            results[case] = 'rejected'
        else:
            raise AssertionError(f'control escaped: {case}')
    return results


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--task', choices=ROUTINES, required=True)
    ap.add_argument('--controls', action='store_true')
    ap.add_argument('--receipt', type=Path)
    args = ap.parse_args()
    ledger = ROOT / f'notes/engine-study/T101/{args.task}-v1.json'
    data = json.loads(ledger.read_text())
    text = (ROOT / f'docs/engine-study/{CHAPTERS[args.task]}.md').read_text()
    validate(args.task, data, text)
    result = {'task': args.task, 'scope': __doc__, 'routines': len(data['routines']),
              'manifest_sha256': sha(ledger.read_bytes()), 'positive': 'accepted'}
    if args.controls:
        result['controls'] = controls(args.task, data, text)
    if args.receipt:
        write_new(args.receipt, result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
