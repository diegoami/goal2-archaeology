#!/usr/bin/env python3
"""E029 step 4: the order of the managed country's squad words (Italy, country 16) against the
players' position byte +6 (the key 1771:52CC sorts by), and the screen at every order-only change.
For each run record: per state, are slots 1..11 and slots 12..20 each non-decreasing in +6 (a sorted
block)? And for every state where the squad words changed in order only (same eleven, same bench),
the screen tag of out/<run>-screens.tsv and whether the blocks are sorted after the change.
Reads runs/E015/*.json (python3 -I; never prints a record) and out/*-timeline.tsv, out/*-screens.tsv.
Usage (repository root): python3 -I experiments/E029-lineup-persistence/order_check.py"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(HERE, 'out')
RUNS = ['r0007', 'r0009', 'r0010', 'r0013', 'r0017']


def tags(run):
    t = []
    for l in list(open(os.path.join(OUT, f'{run}-screens.tsv')))[1:]:
        p = l.rstrip('\n').split('\t')
        t.append((int(p[0]), p[1]))
    return t


def tag_at(t, s):
    cur = 'OTHER'
    for n, g in t:
        if n <= s:
            cur = g
    return cur


def sorted_block(keys):
    return all(a <= b for a, b in zip(keys, keys[1:]))


out = []
sumn = {'states': 0, 'xi_sorted': 0, 'bench_sorted': 0, 'ord_events': 0, 'ord_sorted_after': 0}
for run in RUNS:
    path = os.path.join(ROOT, 'runs', 'E015', 'E015-' + run + '.json')
    pos = {}
    for x in json.load(open(path))['observations']:
        m = re.match(r'state (\d+) \(.*\): country 16 squad player (\d+) record', x['field'])
        if m:
            pos[(int(m.group(1)), int(m.group(2)))] = int(x['value'].split()[6], 16)
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(OUT, f'{run}-timeline.tsv'))]
    c = rows[0].index('sq16')
    tg = tags(run)
    prev = None
    out.append(f'== {run}')
    for r in rows[1:]:
        if not r[c]:
            continue
        w = [int(v) for v in r[c].split(',')]
        if not any(w):
            continue
        s = int(r[0])
        keys = [pos.get((s, p)) for p in w]
        if None in keys:
            prev = w
            continue
        xi_ok = sorted_block(keys[:11])
        b_ok = sorted_block(keys[11:])
        sumn['states'] += 1
        sumn['xi_sorted'] += xi_ok
        sumn['bench_sorted'] += b_ok
        if prev is not None and w != prev and set(prev[:11]) == set(w[:11]) and set(prev[11:]) == set(w[11:]):
            sumn['ord_events'] += 1
            sumn['ord_sorted_after'] += (xi_ok and b_ok)
            moved = [i + 1 for i in range(20) if prev[i] != w[i]]
            out.append(f'   state {s} {r[1]} order-only change, slots {moved}; screen {tag_at(tg, s)}; '
                       f'+6 non-decreasing after: XI {xi_ok} bench {b_ok}')
        prev = w
out.append('')
out.append(f"states with the managed squad and all +6 readable: {sumn['states']}")
out.append(f"  slots 1..11 non-decreasing in +6: {sumn['xi_sorted']} of {sumn['states']}")
out.append(f"  slots 12..20 non-decreasing in +6: {sumn['bench_sorted']} of {sumn['states']}")
out.append(f"order-only changes: {sumn['ord_events']}; both blocks sorted after the change: {sumn['ord_sorted_after']} of {sumn['ord_events']}")
open(os.path.join(OUT, 'order-check.txt'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
