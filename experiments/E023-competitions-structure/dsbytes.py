"""Read bytes of the data segment 2581 from the committed hex dumps static/goal-exe/data/ds_2581_0*.hex.

usage: python3 -B experiments/E023-competitions-structure/dsbytes.py HEXOFF LEN
prints LEN bytes from DS:HEXOFF. A row '*' repeats the row above until the next row's offset.
Bytes outside the initialised part print as '??'.
"""
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'static', 'goal-exe', 'data')


def load():
    mem = {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'ds_2581_0*.hex'))):
        last = None      # (offset, bytes) of the last real row
        repeat = False
        for line in open(path):
            if line.startswith(';') or not line.strip():
                continue
            if line.startswith('*'):
                repeat = True
                continue
            m = re.match(r'^([0-9A-F]{4,5})  ((?:[0-9A-F]{2} ){1,32})', line)
            if not m:
                continue
            off = int(m.group(1), 16)
            data = bytes.fromhex(m.group(2).replace(' ', ''))
            if repeat and last is not None:
                o = last[0] + len(last[1])
                while o < off:
                    for i, b in enumerate(last[1]):
                        mem[o + i] = b
                    o += len(last[1])
            repeat = False
            for i, b in enumerate(data):
                mem[off + i] = b
            last = (off, data)
    return mem


def get(mem, a, n):
    return [mem.get(a + i) for i in range(n)]


if __name__ == '__main__':
    mem = load()
    args = sys.argv[1:]
    for k in range(0, len(args), 2):      # several HEXOFF LEN pairs may follow each other
        a = int(args[k], 16)
        n = int(args[k + 1])
        print('%04X: ' % a + ' '.join('??' if b is None else '%02X' % b for b in get(mem, a, n)))
