#!/usr/bin/env python3
"""E029 step 3: place the managed side's squad-word changes of the run records against the match windows
and ask, for each in-match substitution, whether (a) it is still in the eleven at full time, (b) it is
still in the eleven at the last state of the record, (c) it is in the eleven at the first state of the
NEXT match (only where a record holds one). Read-only over out/*-timeline.tsv (run_all.py).

A "substitution" is a membership change of the managed country's squad words (slots 1..11 against
slots 12..20) between two states inside a match window; a change before kick-off is a "pre-match edit".
The match windows are read off the recorded screens (out/*-screens.tsv, screens.py) and the fixture
index word of the timeline; each is cited in WINDOWS.
Usage (repository root): python3 -I experiments/E029-lineup-persistence/substitutions.py"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')

# names: the player numbers 301..320 are Italy's squad as listed on the in-match team screen of
# E015-r0007 state 85 (the screen's order is the squad order: eleven, then bench); 2593 is a pool player
# the owner named Causio in E015-r0013's notes (state 725 to 731).
NAMES = {301: 'Pagliuca', 302: 'Baresi', 303: 'Maldini', 304: 'Costacurta', 305: 'Di Chiara',
         306: 'Tassotti', 307: 'Albertini', 308: 'Eranio', 309: 'Donadoni', 310: 'Vialli',
         311: 'Signori', 312: 'Zenga', 313: 'D Agostini', 314: 'Vierchowod', 315: 'Stroppa',
         316: 'Berti', 317: 'Giannini', 318: 'Baggio', 319: 'Lentini', 320: 'Schillaci', 2593: 'Causio'}

# (run, country column, match label, kick-off state, full-time state, evidence for the window)
WINDOWS = [
    ('r0007', 'sq16', 'Italy-Turkey friendly (fixture 18)', 53, 207,
     'out/r0007-screens.tsv: the match board VERSUS from state 53, HALF TIME 72, bench screen 76-131, FULL TIME 207; fixture word 18 -> 19 at state 213'),
    ('r0013', 'sq16', 'Italy-Portugal (fixture 116)', 279, 798,
     'out/r0013-screens.tsv: SELECT 259-278, VERSUS 279, bench screens from 292, FULL TIME 798; fixture word 116 -> 117 at state 801'),
    ('r0017', 'sq16', 'Italy match (fixture 22)', 196, 280,
     'out/r0017-screens.tsv: SELECT 86-195, VERSUS 196, FULL TIME 280; fixture word 22 -> 23 at state 288'),
]
# the next match's first state, for a substitution of the window above (a record that loads the save)
NEXT = {
    'r0007': [('r0009', 'sq16', 10, 'Belgium qualifier: first match board (E015-r0009 state 10: BELGIUM versus ITALY)'),
              ('r0010', 'sq16', 12, 'Belgium qualifier: first match board (E015-r0010 state 12: BELGIUM versus ITALY)')],
}


def load(run, col):
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(OUT, f'{run}-timeline.tsv'))]
    c = rows[0].index(col)
    d = {}
    for r in rows[1:]:
        if r[c]:
            w = [int(v) for v in r[c].split(',')]
            if any(w):
                d[int(r[0])] = (r[1], w)
    return d


def name(p):
    return NAMES.get(p, str(p))


lines = []
tsv = ['run\tstate\tutc\tphase\tout\tin\tin_xi_at_fulltime\tin_xi_at_record_end\tnext_match_first_state']
tot = {'subs': 0, 'ft': 0, 'end': 0, 'next_placed': 0, 'next_held': 0, 'next_unplaced': 0}
for run, col, label, ko, ft, why in WINDOWS:
    d = load(run, col)
    states = sorted(d)
    last = states[-1]
    lines.append(f'== {run} {col} {label}: kick-off state {ko}, full time state {ft}, record ends at state {last}')
    lines.append(f'   window: {why}')
    prev = None
    events = []
    for s in states:
        w = d[s][1]
        if prev is not None and (set(prev[:11]) != set(w[:11]) or set(prev[11:]) != set(w[11:])):
            outs = sorted(set(prev[:11]) - set(w[:11]))
            ins = sorted(set(w[:11]) - set(prev[:11]))
            phase = 'in-match' if ko < s <= ft else ('pre-match' if s <= ko else 'after full time')
            events.append((s, d[s][0], phase, outs, ins))
        prev = w
    xi_ft = set(d[ft][1][:11])
    xi_end = set(d[last][1][:11])
    for s, utc, phase, outs, ins in events:
        pairs = ', '.join(f'{name(o)} -> {name(i)}' for o, i in zip(outs, ins))
        lines.append(f'   state {s} {utc} {phase}: out {outs} in {ins}  ({pairs})')
        row = [run, str(s), utc, phase, ','.join(map(str, outs)), ','.join(map(str, ins)), '', '', '']
        if phase == 'in-match':
            tot['subs'] += 1
            a = all(i in xi_ft for i in ins) and all(o not in xi_ft for o in outs)
            b = all(i in xi_end for i in ins) and all(o not in xi_end for o in outs)
            tot['ft'] += a
            tot['end'] += b
            row[6] = 'yes' if a else 'NO'
            row[7] = 'yes' if b else 'NO'
            if run in NEXT:
                res = []
                for nrun, ncol, nstate, nwhy in NEXT[run]:
                    nd = load(nrun, ncol)
                    xi = set(nd[nstate][1][:11])
                    ok = all(i in xi for i in ins) and all(o not in xi for o in outs)
                    res.append(f'{nrun}:{nstate}:{"yes" if ok else "NO"}')
                    tot['next_placed'] += 1
                    tot['next_held'] += ok
                row[8] = ' '.join(res)
            else:
                tot['next_unplaced'] += 1
                row[8] = 'not placeable: no later match in the record'
        tsv.append('\t'.join(row))
    # the eleven at kick-off, at full time and at the record's end, as numbers
    lines.append(f'   XI at kick-off  (state {ko}): {d[ko][1][:11]}')
    lines.append(f'   XI at full time (state {ft}): {d[ft][1][:11]}')
    lines.append(f'   XI at record end (state {last}): {d[last][1][:11]}')
    lines.append(f'   in-match substitutions here: {sum(1 for e in events if e[2] == "in-match")}; '
                 f'pre-match edits before kick-off: {sum(1 for e in events if e[2] == "pre-match")}')
    if run in NEXT:
        for nrun, ncol, nstate, nwhy in NEXT[run]:
            nd = load(nrun, ncol)
            lines.append(f'   next match, {nrun} state {nstate} ({nwhy}): XI {nd[nstate][1][:11]}; '
                         f'identical to the XI at full time, in order: {nd[nstate][1][:11] == d[ft][1][:11]}')
lines.append('')
lines.append(f"TOTAL in-match substitutions placed: {tot['subs']}")
lines.append(f"  in the eleven at full time: {tot['ft']} of {tot['subs']}")
lines.append(f"  in the eleven at the last state of the record: {tot['end']} of {tot['subs']}")
lines.append(f"  first state of the next match placed for: {tot['next_placed'] // 2 if tot['next_placed'] else 0} substitutions, each read in "
             f"2 independent reloads of the same saved game = {tot['next_placed']} readings, "
             f"holding the swapped eleven in {tot['next_held']} of {tot['next_placed']}")
lines.append(f"  not placeable (no later match in the record): {tot['next_unplaced']}")
open(os.path.join(OUT, 'substitutions.txt'), 'w').write('\n'.join(lines) + '\n')
open(os.path.join(OUT, 'substitutions.tsv'), 'w').write('\n'.join(tsv) + '\n')
print('\n'.join(lines))
