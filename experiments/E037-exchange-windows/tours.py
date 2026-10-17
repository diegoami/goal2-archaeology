"""Decode the stage 7 friendlies of 1771:71B2 (asm seg_1771_10.asm, 7336-7421) from the committed data-segment dumps,
and evaluate F031's predicate at every gap of a country's stage 7 friendlies.

usage (from the repository root): python3 -B experiments/E037-exchange-windows/tours.py > experiments/E037-exchange-windows/out/tours.txt

The loops, as read in the listing (5D94 is near: [bp+4] group, [bp+6] kind, [bp+8] -> side A (+4), [bp+0xA] -> side B
(+6); the first push is side B):
  for r = 1..4, c = 1..4, i = 1..16:            (7349-73D8)
      A = order[32(c-1) + 2i - 1]                (73AE-73C3: the second push)
      P = DS:10C6[4c + (i mod 4)]                (7383-7397)
      B = order[32(P-1) + DS:10D5[4*((i+1) div 2) + r]]   (7363-73A7: the first push)
      5D94(0, 1, A, B)
  for i = 1..64:                                 (73EC-7421)
      A = order[2i], B = order[2i-1]             (the first push is order[2i-1])
      5D94(0, 1, A, B)
order[k] is the byte DS:9CFF + k (the 128-byte order table, continent c at 32(c-1)+1..32c, filled by 1771:56FF at
the stage 5 build: the world order kept per continent).
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predicate  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    'e023_dsbytes', os.path.join(HERE, '..', 'E023-competitions-structure', 'dsbytes.py'))
_ds = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ds)
MEM = _ds.load()


def b(off):
    return MEM[off]


def continent_of(pos):
    return (pos - 1) // 32 + 1


def stage7_friendlies():
    """The 320 friendlies in fixture-number order: (number in the stage, loop, round r, side A pos, side B pos)."""
    out = []
    n = 0
    for r in range(1, 5):
        for c in range(1, 5):
            for i in range(1, 17):
                a = 32 * (c - 1) + 2 * i - 1
                p = b(0x10C6 + 4 * c + (i % 4))
                idx = b(0x10D5 + 4 * ((i + 1) // 2) + r)
                bpos = 32 * (p - 1) + idx
                n += 1
                out.append((n, 1, r, a, bpos))
    for i in range(1, 65):
        n += 1
        out.append((n, 2, 0, 2 * i, 2 * i - 1))
    return out


def main():
    fx = stage7_friendlies()
    print('# E037 tours.py: stage 7 friendlies of 1771:71B2 decoded from static/goal-exe/data/ds_2581_0*.hex')
    print('DS:10C6+4c+(i mod 4), c = 1..4:', [[b(0x10C6 + 4 * c + k) for k in range(4)] for c in range(1, 5)])
    print('DS:10D5+4k+r, k = 1..8, r = 1..4:', [[b(0x10D5 + 4 * k + r) for r in range(1, 5)] for k in range(1, 9)])
    print('fixtures:', len(fx))
    first = [f for f in fx if f[1] == 1]
    second = [f for f in fx if f[1] == 2]
    cross1 = sum(1 for f in first if continent_of(f[3]) != continent_of(f[4]))
    cross2 = sum(1 for f in second if continent_of(f[3]) != continent_of(f[4]))
    print('loop 1: %d fixtures, %d with side B of another continent' % (len(first), cross1))
    print('loop 2: %d fixtures, %d with side B of another continent' % (len(second), cross2))
    # per position: its fixtures in order
    per = {p: [] for p in range(1, 129)}
    for n, loop, r, a, bp in fx:
        per[a].append((n, loop, r, 'A', continent_of(bp)))
        per[bp].append((n, loop, r, 'B', continent_of(a)))
    counts = sorted(set(len(v) for v in per.values()))
    print('friendlies per position:', counts)
    shapes = {}
    for p, seq in per.items():
        own = continent_of(p)
        shape = tuple((side, 'X' if oc != own else 'S') for _, _, _, side, oc in seq)
        shapes.setdefault(shape, []).append(p)
    print('shapes (side, X = other continent / S = same), and the positions within a continent block that have them:')
    for shape, ps in sorted(shapes.items()):
        within = sorted(set((q - 1) % 32 + 1 for q in ps))
        print('  %s : %d positions, block positions %s' % (' '.join(s + x for s, x in shape), len(ps), within))
    print()
    print('gap verdicts (finals flag 0, not in a match, not sacked); last played before the first gap: a stage 5 or 6 fixture')
    for p in (1, 2):
        own = continent_of(p)
        seq = per[p]
        # (kind, continent of the record's side B): the opponent's when the country is side A, its own when it is B
        fixtures = [(1, oc if side == 'A' else own) for _, _, _, side, oc in seq]
        last = (5, own)
        print('position %d (continent %d):' % (p, own))
        for k, nxt in enumerate(fixtures):
            v = predicate.exchange(0, 0, 0, own, nxt, last)
            print('  before friendly %d (%s side %s, opponent continent %d): %s' % (
                k + 1, 'record (kind 1, B continent %d)' % nxt[1], seq[k][3], seq[k][4], v))
            last = nxt
        v = predicate.exchange(0, 0, 0, own, None, last)
        print('  after the last friendly, no fixture pending: %s' % v)
        v = predicate.exchange(0, 0, 0, own, (7, own), last)
        print('  after the last friendly, next a kind 7 fixture (flag not yet set): %s' % v)


if __name__ == '__main__':
    main()
