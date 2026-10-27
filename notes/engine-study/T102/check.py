#!/usr/bin/env python3
"""T102 contract coverage and source integrity; not semantic or behavioural proof."""
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
    'T102a': '2FB1 30EA 3111 3323 333F 384C 3B9E 3BEE 3D38 3DF6 4E28 500C 5049 533B 57AC 58E1'.split(),
    'T102b': '34C1 3B15 3C20 3C3F 3EC5 3EDF 3EF8 3FAD 408E 40BC 4151 835F 83A2 869F 593B 59B3'.split(),
    'T102c': '4DA9 539F 5474 5513 5565 56D9 5729 5A33 5A8E 5B36 5E41 5EAB 5F06 5F8A 6188 61EC 6240 6337 6443 65A4 65FE 6755 67B6'.split(),
}
CHAPTERS = {'T102a': 'possession', 'T102b': 'ball-play', 'T102c': 'scoring'}
VERSIONS = {'T102a': 2, 'T102b': 1, 'T102c': 1}


def frontier():
    census = json.loads((ROOT / 'notes/engine-study/T95/census-08beac2e-v1.json').read_text())
    rows = [r for r in census['routines'] if r['module'] in {'ball','contests','duels'} or
            (r['module']=='motion' and r['address'] in {'0791:835F','0791:83A2','0791:869F'})]
    owners = {'0791:'+a: task for task,addresses in ROUTINES.items() for a in addresses}
    assert len(rows)==len(owners)==sum(map(len,ROUTINES.values()))==55
    assert {r['address'] for r in rows}==set(owners)
    return [dict(address=r['address'],module=r['module'],owner=owners[r['address']]) for r in rows]



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
        assert all(example.get(k) for k in ['id', 'inputs', 'steps', 'limits'])
        # Zero/False are substantive predictions (for example an offside line at
        # zero). Missing, null and empty placeholder predictions still fail.
        prediction = example['prediction']
        assert prediction is not None and (isinstance(prediction, (bool, int, float)) or bool(prediction))
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
    ledger = ROOT / f'notes/engine-study/T102/{args.task}-v{VERSIONS[args.task]}.json'
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
