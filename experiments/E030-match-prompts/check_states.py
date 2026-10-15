#!/usr/bin/env python3
"""E030: check every state number F030 cites against out/<run>-prompts.tsv (made by prompts.py from the committed
records). Each claim is (run, first state, last state, class, class of the next snapshot, seconds from the last state
to the next snapshot, seconds from the first state to the last); a claim that does not match the log fails the run.
Writes out/state-check.txt. Read-only. Usage (repository root): python3 -I experiments/E030-match-prompts/check_states.py"""
import os
import sys
from datetime import datetime, timezone

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')

# (run, first, last, class, next_state, next_class, seconds last->next, seconds first->last)
CLAIMS = [
    ('r0013', 339, 339, 'REPLAY_ASK', 340, 'OTHER', 20, 0),
    ('r0013', 736, 736, 'REPLAY_ASK', 737, 'SAVEGOAL_ASK', 1, 0),
    ('r0013', 742, 742, 'REPLAY_ASK', 743, 'OTHER', 1, 0),
    ('r0013', 87, 87, 'SAVEGOAL_ASK', 88, 'REPLAY_RUNNING', 3, 0),
    ('r0013', 332, 332, 'SAVEGOAL_ASK', 333, 'HIL_NAME', 1, 0),
    ('r0013', 737, 737, 'SAVEGOAL_ASK', 738, 'REPLAY_RUNNING', 5, 0),
    ('r0013', 99, 99, 'SUMMARY_ASK', 100, 'OTHER', 15, 0),
    ('r0013', 799, 800, 'SUMMARY_ASK', 801, 'OTHER', 7, 5),
    ('r0013', 28, 28, 'WATCH_ASK', 29, 'OTHER', 4, 0),
    ('r0013', 101, 106, 'WATCH_ASK', 107, 'OTHER', 2, 56),
    ('r0013', 111, 111, 'WATCH_ASK', 112, 'OTHER', 5, 0),
    ('r0013', 280, 280, 'CAPTAIN', 281, 'OTHER', 5, 0),
    ('r0013', 333, 333, 'HIL_NAME', 334, 'REPLAY_RUNNING', 2, 0),
    ('r0013', 2, 2, 'GL_NAME', 3, 'OTHER', 2, 0),
    ('r0013', 802, 806, 'GL_NAME', 807, 'OTHER', 20, 29),
    ('r0013', 865, 865, 'GL_NAME', None, None, None, 0),
    ('r0017', 202, 202, 'CAPTAIN', 203, 'OTHER', 4, 0),
    ('r0017', 286, 286, 'SUMMARY_ASK', 287, 'OTHER', 2, 0),
    ('r0017', 3, 3, 'GL_NAME', 4, 'OTHER', 2, 0),
    ('r0017', 290, 295, 'GL_NAME', 296, 'QUIT_ASK', 4, 17),
]
# (run, state, seconds from the previous snapshot to it, class of the previous snapshot)
BEFORE = [
    ('r0013', 99, 5, 'OTHER', 98),
    ('r0013', 799, 15, 'OTHER', 798),
    ('r0013', 339, 20, 'OTHER', 338),
]
# (run, state, byte [A923]+0x41)
INS = [('r0013', 2, 0), ('r0017', 2, 0), ('r0017', 3, 0)]


def load(run):
    rows = {}
    order = []
    for line in list(open(os.path.join(OUT, f'{run}-prompts.tsv')))[1:]:
        f = line.rstrip('\n').split('\t')
        rows[int(f[0])] = f
        order.append(int(f[0]))
    return rows, order


def utc(s):
    return datetime.strptime(s, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)


def main():
    lines, bad = [], 0
    logs = {r: load(r) for r in ('r0013', 'r0017')}
    for run, a, z, cls, ns, ncls, secs, span in CLAIMS:
        rows, order = logs[run]
        ok = all(rows[s][2] == cls for s in range(a, z + 1)) and order.count(a) == 1
        ok = ok and all(s in rows for s in range(a, z + 1))
        got_span = int((utc(rows[z][1]) - utc(rows[a][1])).total_seconds())
        ok = ok and got_span == span
        if ns is None:
            ok = ok and order[-1] == z
            got = 'no snapshot follows'
        else:
            nxt = order[order.index(z) + 1]
            got = f'next {nxt} {rows[nxt][2]} +{int((utc(rows[nxt][1]) - utc(rows[z][1])).total_seconds())} s'
            ok = ok and nxt == ns and rows[nxt][2] == ncls and int((utc(rows[nxt][1]) - utc(rows[z][1])).total_seconds()) == secs
        bad += not ok
        lines.append(f'{"ok" if ok else "FAIL"} {run} states {a}..{z} {cls}, span {got_span} s, {got}')
    for run, st, secs, cls, prev in BEFORE:
        rows, order = logs[run]
        p = order[order.index(st) - 1]
        d = int((utc(rows[st][1]) - utc(rows[p][1])).total_seconds())
        ok = p == prev and rows[p][2] == cls and d == secs
        bad += not ok
        lines.append(f'{"ok" if ok else "FAIL"} {run} state {st}: previous snapshot {p} {rows[p][2]} {d} s earlier')
    for run, st, b in INS:
        rows, _ = logs[run]
        ok = rows[st][3] == str(b)
        bad += not ok
        lines.append(f'{"ok" if ok else "FAIL"} {run} state {st}: [A923]+0x41 = {rows[st][3]}')
    open(os.path.join(OUT, 'state-check.txt'), 'w').write('\n'.join(lines) + f'\n{len(lines) - bad} of {len(lines)} claims match\n')
    print('\n'.join(lines))
    return 1 if bad else 0


sys.exit(main())
