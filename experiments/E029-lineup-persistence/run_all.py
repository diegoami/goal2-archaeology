#!/usr/bin/env python3
"""E029: build out/<run>-timeline.tsv and out/<run>-changes.txt for every run record the task names
(plus E015-r0014..r0016, the owner's earlier sittings, as extra evidence), read-only over runs/E015/.
Usage (from the repository root): python3 -I experiments/E029-lineup-persistence/run_all.py"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True)
for r in ['r0007', 'r0008', 'r0009', 'r0010', 'r0013', 'r0014', 'r0015', 'r0016', 'r0017']:
    tl = os.path.join(OUT, f'{r}-timeline.tsv')
    subprocess.check_call([sys.executable, '-I', os.path.join(HERE, 'timeline.py'),
                           os.path.join(ROOT, 'runs', 'E015', f'E015-{r}.json'), tl])
    cols = open(tl).readline().rstrip('\n').split('\t')[4:]
    for c in cols:
        out = subprocess.check_output([sys.executable, '-I', os.path.join(HERE, 'changes.py'), tl, c], text=True)
        with open(os.path.join(OUT, f'{r}-{c}-changes.txt'), 'w') as f:
            f.write(out)
        print(r, c, out.count('\n'), 'change lines')
