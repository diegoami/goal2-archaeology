#!/usr/bin/env python3
"""E029 step 5: the owner's note 13 of E015-r0013 (between states 297 and 298, UTC 05:23:49) says the game
asked for the captain and for the goal-kick taker and that the owner typed C (computer selects).
Does that choice change the managed country's squad words (order or membership)? Compare Italy's squad
words (country 16) at every state from the kick-off screen (279) to the first substitution (321).
Read-only over out/r0013-timeline.tsv. Usage (repository root): python3 -I experiments/E029-lineup-persistence/cprompt.py"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(OUT, 'r0013-timeline.tsv'))]
c = rows[0].index('sq16')
seen = {}
for r in rows[1:]:
    s = int(r[0])
    if 279 <= s <= 320:
        seen.setdefault(r[c], []).append(s)
lines = [f'E015-r0013 states 279..320 (kick-off board to the state before the first substitution at 321): '
         f'{sum(len(v) for v in seen.values())} states, {len(seen)} distinct squad-word lists for country 16']
for k, v in seen.items():
    lines.append(f'  states {v[0]}..{v[-1]} ({len(v)}): {k}')
lines.append('note 13 (C typed at the captain / goal-kick prompts) lies between states 297 and 298')
open(os.path.join(OUT, 'cprompt.txt'), 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
