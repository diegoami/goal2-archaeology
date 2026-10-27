#!/usr/bin/env python3
"""Exercise the structural T101 contracts on absent deliverables and labelled mocks."""
import json
import subprocess
import sys
from check import ROOT, BASE, ROUTINES, pin, validate, controls, write_new


def main():
    results = []
    for task, routines in ROUTINES.items():
        cmd = [sys.executable, '-B', str(ROOT / 'notes/engine-study/T101/check.py'),
               '--task', task, '--controls']
        baseline = subprocess.run(cmd, capture_output=True, text=True)
        assert baseline.returncode != 0 and 'FileNotFoundError' in baseline.stderr
        mock = pin({'task': task, 'sections': ['Mock one', 'Mock two', 'Mock three'],
                    'routines': [{'address': '0791:' + a, 'mechanism': 'MOCK',
                                  'fields': ['MOCK'], 'visible_effect': 'MOCK', 'limits': 'MOCK'}
                                 for a in routines],
                    'examples': [{'id': str(i), 'inputs': 'MOCK', 'steps': ['MOCK'],
                                  'prediction': 'MOCK', 'limits': 'MOCK'} for i in range(2)]},
                   ['0791:' + a for a in routines], source_commit=BASE)
        text = '\n'.join('## ' + s + '\n' + 'mock ' * 100 for s in mock['sections'])
        validate(task, mock, text)
        results.append({'task': task, 'baseline_argv': cmd, 'baseline_exit': baseline.returncode,
                        'baseline_stderr': baseline.stderr, 'mock': 'accepted; structural only',
                        'controls': controls(task, mock, text)})
    write_new(ROOT / 'notes/engine-study/T101/readiness-v1.json',
              {'scope': __doc__, 'source_commit': BASE, 'results': results})
    print('PASS: three absent deliverables rejected, three structural mocks accepted, 12 controls rejected')


if __name__ == '__main__':
    main()
