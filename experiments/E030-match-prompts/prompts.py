#!/usr/bin/env python3
"""E030: the prompt screens around a match, per snapshot, from the committed run records E015-r0013 and E015-r0017.
Read-only: no game run. For each state of a record it takes the recorded text screen (the extractor lists a screen
only when it changed, so a state without one keeps the previous text, as E029's screens.py does), the snapshot's UTC
time from its file name, and the byte [A923]+0x41 of the game state block (the INS toggle). It tags the screen with a
prompt class and writes, per run, one TSV line per state plus a summary of each prompt: the snapshots that hold it,
the runs of consecutive snapshots, the screen class of the snapshot that follows and the seconds to it.
Usage (repository root): python3 -I experiments/E030-match-prompts/prompts.py"""
import json
import os
import re
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
RUNS = ('r0013', 'r0017')

# (class, text that must be on the screen); the first match wins
CLASSES = (
    ('REPLAY_ASK', 'Do you want an action replay'),
    ('SAVEGOAL_ASK', 'Do you want to save this goal'),
    ('SUMMARY_ASK', 'Do you want to save the match summary'),
    ('WATCH_ASK', 'Do you want to watch this match'),
    ('CAPTAIN_TAKER', 'computer select'),
    ('HIL_NAME', 'Please enter name of file'),
    ('GL_NAME', 'Please enter name of saved game'),
    ('SAVEGAME_ASK', 'Do you want to save this game'),
    ('LOAD_ASK', 'Do you want to load a saved game'),
    ('QUIT_ASK', 'Are you sure you want to quit'),
    ('REPLAY_RUNNING', 'REPLAY'),
)


def utc(stamp):
    return datetime.strptime(stamp, '%Y%m%dT%H%M%SZ').replace(tzinfo=timezone.utc)


def load(run):
    rec = json.load(open(os.path.join(ROOT, 'runs', 'E015', f'E015-{run}.json'), encoding='utf-8'))
    text, when, block = {}, {}, {}
    for x in rec['observations']:
        f = x['field']
        m = re.match(r'state (\d+) \(snapshots/snap-\d+-(\w+)\.sav\): text screen rows', f)
        if m:
            text[int(m.group(1))] = x['value']
            when[int(m.group(1))] = m.group(2)
        m = re.match(r'read snapshot snapshots/snap-(\d+)-(\w+)\.sav', f)
        if m:
            when[int(m.group(1))] = m.group(2)
        m = re.match(r'state (\d+) \(.*\): the game state, 0x10e bytes', f)
        if m:
            block[int(m.group(1))] = x['value']
    return text, when, block


def tag(screen):
    for name, key in CLASSES:
        if key in screen:
            if name == 'CAPTAIN_TAKER':
                return 'CAPTAIN' if 'CAPTAIN' in screen else 'TAKER'
            return name
    return 'OTHER'


def ins_byte(hexstr):
    h = ''.join(c for c in hexstr if c in '0123456789abcdefABCDEF')
    return int(h[0x41 * 2:0x41 * 2 + 2], 16) if len(h) >= 0x42 * 2 else None


def secs(a, b):
    return int((utc(b) - utc(a)).total_seconds())


def main():
    summary = []
    for run in RUNS:
        text, when, block = load(run)
        rows = []
        last = ''
        for s in sorted(when):
            if s in text:
                last = text[s]
            rows.append((s, when[s], tag(last), ins_byte(block[s]) if s in block else None))
        with open(os.path.join(OUT, f'{run}-prompts.tsv'), 'w') as o:
            o.write('state\tutc\tclass\tins_byte_0x41\tseconds_to_next\tnext_class\n')
            for i, (s, w, c, b) in enumerate(rows):
                if i + 1 < len(rows):
                    dt, nc = secs(w, rows[i + 1][1]), rows[i + 1][2]
                else:
                    dt, nc = '', ''
                o.write(f'{s}\t{w}\t{c}\t{"" if b is None else b}\t{dt}\t{nc}\n')
        ins = {}
        for r in rows:
            ins[r[3]] = ins.get(r[3], 0) + 1
        summary.append(f'== {run}: {len(rows)} snapshots; [A923]+0x41 over the snapshots: ' +
                       ', '.join(f'{k}: {v}' for k, v in sorted(ins.items(), key=lambda kv: str(kv[0]))))
        for c in sorted({r[2] for r in rows} - {'OTHER'}):
            held = [i for i, r in enumerate(rows) if r[2] == c]
            groups, cur = [], []
            for i in held:
                if cur and i == cur[-1] + 1:
                    cur.append(i)
                else:
                    if cur:
                        groups.append(cur)
                    cur = [i]
            if cur:
                groups.append(cur)
            summary.append(f'  {c}: {len(held)} of {len(rows)} snapshots hold it, in {len(groups)} run(s) of consecutive snapshots')
            for g in groups:
                a, z = rows[g[0]], rows[g[-1]]
                line = f'    states {a[0]}..{z[0]} ({len(g)} snapshots, {secs(a[1], z[1])} s from first to last, {a[1]}..{z[1]})'
                if g[-1] + 1 < len(rows):
                    n = rows[g[-1] + 1]
                    line += f'; next snapshot {n[0]} is {n[2]}, {secs(z[1], n[1])} s after the last'
                else:
                    line += '; no snapshot follows'
                if g[0]:
                    p = rows[g[0] - 1]
                    line += f'; the one before is {p[0]} ({p[2]}), {secs(p[1], a[1])} s earlier'
                summary.append(line)
    open(os.path.join(OUT, 'prompts-summary.txt'), 'w').write('\n'.join(summary) + '\n')
    print('\n'.join(summary))


main()
