"""Decode every Pascal set F023 and the annotations cite, over all 32 bytes (element e = bit e&7 of byte e>>3, 23E4:08DF).

python3 -B experiments/E023-competitions-structure/sets.py > experiments/E023-competitions-structure/out/sets.txt
Code-segment sets are read from the `db` rows of the listing (two rows of 16 bytes at the cited address).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dsbytes

CODE = os.path.join(HERE, '..', '..', 'static', 'goal-exe', 'code')


def code_set(fname, addr):
    rows = {}
    for line in open(os.path.join(CODE, fname)):
        m = re.match(r'^([0-9A-F]{4})\s+db ((?:[0-9A-F]{2} ?){16})', line)
        if m:
            rows[int(m.group(1), 16)] = bytes.fromhex(m.group(2).replace(' ', ''))
    return rows[addr] + rows[addr + 16]


def members(raw):
    assert len(raw) == 32
    out = [e for e in range(256) if raw[e >> 3] >> (e & 7) & 1]
    rng = []
    for e in out:
        if rng and rng[-1][1] == e - 1:
            rng[-1][1] = e
        else:
            rng.append([e, e])
    return ', '.join(str(a) if a == b else '%d..%d' % (a, b) for a, b in rng)


mem = dsbytes.load()
sets = [
    ('CS:81E8 ageing gate (seg_1771_12.asm:118)', code_set('seg_1771_12.asm', 0x81E8)),
    ('CS:8737 8757 gate (seg_1771_12.asm:682)', code_set('seg_1771_12.asm', 0x8737)),
    ('CS:59B8 59D8 finals-table stages (seg_1771_08.asm:735)', code_set('seg_1771_08.asm', 0x59B8)),
    ('CS:7099 60CB announce stages (seg_000E_09.asm:471)', code_set('seg_000E_09.asm', 0x7099)),
    ('DS:0F3E result kinds', bytes(dsbytes.get(mem, 0x0F3E, 32))),
    ('DS:693A decider kinds', bytes(dsbytes.get(mem, 0x693A, 32))),
]
for name, raw in sets:
    print('%s\n  bytes %s\n  members {%s}' % (name, raw.hex(' '), members(raw)))
