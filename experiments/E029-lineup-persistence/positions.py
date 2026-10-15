#!/usr/bin/env python3
"""E029 step 6: does the managed side's own substitution (the in-match select screen, 0791:E022) copy the
outgoing player's position byte +6 to the incoming one, as the computer's substitution (0791:C88D,
seg_0791_20.asm:777-791) does? For each in-match substitution of out/substitutions.tsv: +6 of the
incoming and of the outgoing player one state before the change, at the change, at full time and at the
last state of the record. Reads runs/E015/*.json (python3 -I; never prints a record).
Usage (repository root): python3 -I experiments/E029-lineup-persistence/positions.py"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'out')
FULL_TIME = {'r0007': 207, 'r0013': 798}
lines = []
same = 0
total = 0
distinct = 0
distinct_same = 0
subs = [l.rstrip('\n').split('\t') for l in open(os.path.join(OUT, 'substitutions.tsv'))][1:]
for run in ('r0007', 'r0013'):
    pos = {}
    nstates = set()
    for x in json.load(open(os.path.join(ROOT, 'runs', 'E015', f'E015-{run}.json')))['observations']:
        m = re.match(r'state (\d+) \(.*\): country 16 squad player (\d+) record', x['field'])
        if m:
            pos[(int(m.group(1)), int(m.group(2)))] = int(x['value'].split()[6], 16)
            nstates.add(int(m.group(1)))
    last = max(nstates)
    lines.append(f'== {run}: +6 (position byte) of the incoming / outgoing player at the state before the substitution, at it, at full time ({FULL_TIME[run]}), at the last state ({last})')
    for r in subs:
        if r[0] != run or r[3] != 'in-match':
            continue
        s = int(r[1])
        o, i = int(r[4]), int(r[5])
        def g(st, p):
            return pos.get((st, p))
        row_in = [g(s - 1, i), g(s, i), g(FULL_TIME[run], i), g(last, i)]
        row_out = [g(s - 1, o), g(s, o), g(FULL_TIME[run], o), g(last, o)]
        total += 1
        if len(set(v for v in row_in if v is not None)) == 1:
            same += 1
        if row_in[0] != row_out[0]:
            distinct += 1
            distinct_same += len(set(row_in)) == 1
        lines.append(f'   state {s}: incoming {i}: {row_in}; outgoing {o}: {row_out}')
lines.append('')
lines.append(f'incoming player whose +6 never changed from before the substitution to the last readable state: {same} of {total}')
lines.append(f'of those, substitutions whose incoming and outgoing +6 differed (where a copy would show): {distinct}; incoming +6 unchanged in {distinct_same} of {distinct}')
open(os.path.join(OUT, 'positions.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
