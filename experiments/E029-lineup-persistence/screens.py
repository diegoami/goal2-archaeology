#!/usr/bin/env python3
"""E029: tag each state of a run record with a coarse screen class read from the recorded text page
(observation 'text screen rows'): VERSUS (match board: a line with 'versus'), SUBS (the in-match team
screen: 'substitutions left'), SELECT (the pre-match select screen: ' select '), OTHER; one TSV line per
state where the tag changes. The extractor lists a screen only when it changed, so a state without one
keeps the previous text. Read-only. Usage: python3 -I screens.py RUN.json OUT.tsv"""
import json
import re
import sys

rec = json.load(open(sys.argv[1]))
scr = {}
nums = set()
for x in rec['observations']:
    m = re.match(r'state (\d+) ', x['field'])
    if m:
        nums.add(int(m.group(1)))
    m = re.match(r'state (\d+) \(.*\): text screen rows', x['field'])
    if m:
        scr[int(m.group(1))] = x['value']
last_text = ''
prev = None
with open(sys.argv[2], 'w') as o:
    o.write('state\ttag\tdetail\n')
    for n in sorted(nums):
        t = scr.get(n, last_text)
        last_text = t
        tag = 'OTHER'
        if 'substitutions left' in t:
            tag = 'SUBS'
        elif 'versus' in t:
            tag = 'VERSUS'
        elif re.search(r'\bselect\b', t):
            tag = 'SELECT'
        detail = ''
        if tag == 'SUBS':
            m = re.search(r'substitutions left\s*│\s*(\d+)', t)
            detail = 'left=' + (m.group(1) if m else '?')
        if tag == 'VERSUS':
            m = re.search(r'(HALF TIME|FULL TIME|FINAL WHISTLE)', t)
            detail = m.group(1) if m else ''
        if (tag, detail) != prev:
            o.write(f'{n}\t{tag}\t{detail}\n')
        prev = (tag, detail)
