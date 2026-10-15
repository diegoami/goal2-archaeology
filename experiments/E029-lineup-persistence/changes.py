#!/usr/bin/env python3
"""E029 step 2: from a timeline TSV (timeline.py), list every state where one country's squad words
or the fixture index changed against the previous state, with the change described as: eleven in
(slots 1..11 as a set), bench (slots 12..20 as a set), order-only changes.
Usage: python3 -I changes.py TIMELINE.tsv COUNTRY_COLUMN_NAME   e.g. sq16"""
import sys

rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
hdr = rows[0]
col = hdr.index(sys.argv[2])
prev = None
prevfix = None
for r in rows[1:]:
    st, ts, fix, stage = r[0], r[1], r[2], r[3]
    sq = r[col]
    if not sq:
        continue
    w = [int(v) for v in sq.split(',')]
    if all(v == 0 for v in w):
        continue
    tag = []
    if prevfix is not None and fix != prevfix:
        tag.append(f'FIXTURE {prevfix}->{fix}')
    if prev is not None and w != prev:
        e0, e1 = set(prev[:11]), set(w[:11])
        b0, b1 = set(prev[11:]), set(w[11:])
        if e0 != e1 or b0 != b1:
            tag.append(f'MEMBERSHIP out={sorted(e0 - e1)} in={sorted(e1 - e0)} bench_out={sorted(b0 - b1)} bench_in={sorted(b1 - b0)}')
        else:
            moved = [i + 1 for i in range(20) if prev[i] != w[i]]
            tag.append(f'ORDER slots {moved}')
    if prev is None:
        tag.append('FIRST')
    if tag:
        print(f'{st}\t{ts}\tfix={fix}\tstage={stage}\t' + ' ; '.join(tag))
    prev = w
    prevfix = fix
