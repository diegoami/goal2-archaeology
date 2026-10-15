#!/usr/bin/env python3
"""E029 step 1: per state of a human-playthrough run record, the squad words (slots 1..20) of the
decoded countries, the fixture index word [A923]+0x26, the stage byte and the snapshot's timestamp.
Read-only over runs/E015/*.json (python3 -I, never prints a record).
Usage: python3 -I timeline.py RUN.json OUT.tsv"""
import json
import re
import sys

rec = json.load(open(sys.argv[1]))
states = {}
for x in rec['observations']:
    f = x['field']
    m = re.match(r'state (\d+) \(snapshots/snap-\d+-(\w+)\.sav\)(?:: )?(.*)', f)
    if not m:
        continue
    n = int(m.group(1))
    rest = m.group(3)
    s = states.setdefault(n, {'ts': m.group(2)})
    if rest.startswith('fixture index word'):
        s['fix'] = x['value']
    elif rest.startswith('stage byte'):
        s['stage'] = x['value']
for x in rec['decoded']:
    m = re.match(r'state (\d+)(?: \(snapshots/snap-\d+-(\w+)\.sav\))?: country (\d+) squad \(player numbers\)', x['field'])
    if not m:
        continue
    v = x['value']
    if isinstance(v, str):
        v = json.loads(v)
    s = states.setdefault(int(m.group(1)), {'ts': m.group(2) or ''})
    s.setdefault('sq', {})[int(m.group(3))] = v
cs = sorted({c for s in states.values() for c in s.get('sq', {})})
with open(sys.argv[2], 'w') as o:
    o.write('state\tts\tfix\tstage\t' + '\t'.join(f'sq{c}' for c in cs) + '\n')
    for n in sorted(states):
        s = states[n]
        o.write(f"{n}\t{s['ts']}\t{s.get('fix', '')}\t{s.get('stage', '')}\t" +
                '\t'.join(','.join(map(str, s.get('sq', {}).get(c, []))) for c in cs) + '\n')
