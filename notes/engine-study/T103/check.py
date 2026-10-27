#!/usr/bin/env python3
"""T103 contract coverage and source integrity; not semantic or behavioural proof."""
import argparse
import copy
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'notes/engine-study'))
from foundations.check import pin, sha, write_new

CONTROLS = [f'team-{k}' for k in range(1,9)] + [f'own-{k}' for k in range(1,5)] + ['played-role','manual-mark','captain','set-piece-takers','selection','pace','quick','controller']
BASE = 'a42c2cbe91300c8ee261b82fa993e665ed3f3325'
ROUTINES = {'T103a': ['0791:26D7', '1771:1981', '1771:4925', '1771:4952', '1771:49B8', '1771:4B61', '1771:33CD', '1771:3431', '1771:34E7', '1771:3E2F', '1771:3EF8', '1771:0E6C'], 'T103b': ['0791:A3DE', '0791:AC67', '0791:AD8F', '0791:AFA3', '0791:B11F', '1771:517A', '1771:52CC', '1771:53E8', '1771:5532'], 'T103c': ['0791:BBFF', '0791:BC5D', '0791:BD03', '0791:BD83', '0791:BF6B', '0791:C173', '0791:BEC7', '0791:C01A', '0791:C0DF', '0791:C24D', '0791:C2A8', '0791:C406', '0791:C48D']}
CHAPTERS = {'T103a': 'tactics', 'T103b': 'lineup-policy', 'T103c': 'computer-policy'}
VERSIONS = {task:(2 if task in ['T103a','T103c'] else 1) for task in ROUTINES}

def frontier():
    deferred = ['0791:BBFF', '0791:BD03', '0791:BD83', '0791:BF6B', '0791:C173', '0791:BEC7', '0791:C01A', '0791:C0DF', '0791:C24D', '0791:C2A8', '0791:C406', '0791:C48D', '1771:53E8', '1771:5532', '0791:BC5D']
    owners={a:t for t,rows in ROUTINES.items() for a in rows}
    assert len(owners)==sum(map(len,ROUTINES.values()))
    assert set(deferred)<=set(owners)
    return [dict(address=a,owner=owners[a]) for a in deferred]



def validate(task, data, text):
    assert data['task'] == task and data['source_commit'] == BASE
    if task == 'T103a':
        assert {r['id'] for r in data['control_matrix']} == set(CONTROLS)
        for r in data['control_matrix']:
            assert all(r.get(k) for k in ['write','readers','effect','refresh','persistence','limits'])
    rows = data['routines']
    assert len(rows) == len(ROUTINES[task])
    assert {r['address'] for r in rows} == set(ROUTINES[task])
    for row in rows:
        assert all(row.get(k) for k in ['mechanism', 'fields', 'visible_effect', 'limits'])
    assert len(data['sections']) >= 3 and len(text.split()) >= 250
    assert all('## ' + s in text for s in data['sections'])
    assert len(data['examples']) >= 2
    for example in data['examples']:
        assert all(example.get(k) for k in ['id', 'inputs', 'steps', 'limits'])
        # Zero/False are substantive predictions (for example an offside line at
        # zero). Missing, null and empty placeholder predictions still fail.
        prediction = example['prediction']
        assert prediction is not None and (isinstance(prediction, (bool, int, float)) or bool(prediction))
    assert set(ROUTINES[task]) <= {r['address'] for r in data['locations']}
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
    for case in ['missing-routine', 'missing-source', 'shifted-source', 'missing-examples', 'missing-prediction']:
        broken = copy.deepcopy(data)
        if case == 'missing-routine':
            broken['routines'].pop()
        elif case == 'missing-source':
            broken['source_sha256'] = {}
        elif case == 'shifted-source':
            broken['locations'][0]['line'] += 1
        elif case == 'missing-examples':
            broken['examples'] = []
        else:
            broken['examples'][0].pop('prediction')
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
    frontier()
    ledger = ROOT / f'notes/engine-study/T103/{args.task}-v{VERSIONS[args.task]}.json'
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
