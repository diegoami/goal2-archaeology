#!/usr/bin/env python3
"""T104 contract coverage and source integrity; not semantic or behavioural proof."""
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
 'T104a': '0791:690C 0791:698E 0791:69BD 0791:6AAD 0791:6AF7 0791:6B65 0791:6BF1 0791:6D4E 0791:6DEA 0791:6E11 0791:6E6E 0791:6F01 0791:6F3E 0791:6FB6 0791:6FEE 0791:7069 0791:70F6 0791:715A 0791:717F 0791:71E8 0791:7287 0791:74C2 0791:7621 0791:6ECF 0791:72F2 0791:73BA'.split(),
 'T104b': '0791:7881 0791:798D 0791:7A43 0791:7B24 0791:7B77 0791:7CC5 0791:7D56 0791:7E60 0791:7EEF 0791:8206 0791:82EB'.split(),
 'T104c': '0791:8062 0791:A260 0791:A2E6 0791:A920 0791:A9B8 0791:AAE8 0791:C5DC 0791:C7EB 0791:C88D 0791:DE27 0791:DE51 0791:E022 0791:E2A0 0791:E44F 0791:E949 0791:EA09'.split(),
 'T104d': '0791:0B7C 0791:0C0B 0791:9B0C 0791:9B5B 0791:9B93 0791:9ED3 0791:A006 0791:A10A 0791:CC2E 0791:CC7B'.split(),
 'T104e': '0791:CAB0 0791:CB7D 0791:D016 0791:D032 0791:D050 0791:E929 0791:F1F6 1771:59D8 1771:82BD 1771:85F7 1771:8757 0791:B27F 0791:B364 0791:B6CC 0791:B71C 0791:B7FA 0791:BA4E 1771:10E7 1771:3558 1771:3651 1771:5A38 1771:5A8F 1771:5C60 0791:B3B7'.split(),
}
CHAPTERS = {'T104a':'restarts','T104b':'discipline','T104c':'substitutions','T104d':'shootouts','T104e':'lifecycle'}
VERSIONS = {task:1 for task in ROUTINES}
VERSIONS['T104c'] = 2
DEFERRED = '0791:BBFF 0791:BD03 0791:BD83 0791:BF6B 0791:C173 0791:BEC7 0791:C01A 0791:C0DF 0791:C24D 0791:C2A8 0791:C406 0791:C48D 1771:53E8 1771:5532 0791:BC5D'.split()


def frontier():
    census=json.loads((ROOT/'notes/engine-study/T95/census-08beac2e-v1.json').read_text())
    modules={'restarts','takers','discipline','update','postmatch','selection','rare'}
    rows=[r for r in census['routines'] if r['module'] in modules]
    owners={a:task for task,addresses in ROUTINES.items() for a in addresses}
    assert len(owners)==sum(map(len,ROUTINES.values()))==87
    assert not set(owners)&set(DEFERRED) and len(DEFERRED)==15
    owners.update({a:'T103 policy' for a in DEFERRED})
    assert len(rows)==len(owners)==102 and {r['address'] for r in rows}==set(owners)
    return [dict(address=r['address'],module=r['module'],owner=owners[r['address']]) for r in rows]



def validate(task, data, text):
    assert data['task'] == task and data['source_commit'] == BASE
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
    ledger = ROOT / f'notes/engine-study/T104/{args.task}-v{VERSIONS[args.task]}.json'
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
