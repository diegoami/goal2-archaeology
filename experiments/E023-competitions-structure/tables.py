"""Decode the stage-builder tables of the data image (offsets from the listing, F023).

python3 -B experiments/E023-competitions-structure/tables.py > experiments/E023-competitions-structure/tables.txt
Every offset below is the one written in the builder's listing (cited in F023); this script only reads bytes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dsbytes

mem = dsbytes.load()


def b(a, n=1):
    v = dsbytes.get(mem, a, n)
    return v if n > 1 else v[0]


print('== DS:0F3E decider shape; DS:693A decider set (Pascal set of 32 bytes: element e = bit e%8 of byte e//8)')
for name, base in (('DS:0F3E', 0x0F3E), ('DS:693A', 0x693A)):
    raw = b(base, 32)
    members = [e for e in range(256) if raw[e // 8] >> (e % 8) & 1]
    # compress to ranges
    rng = []
    for e in members:
        if rng and rng[-1][1] == e - 1:
            rng[-1][1] = e
        else:
            rng.append([e, e])
    print(name, ' '.join('%02X' % x for x in raw), '->', ', '.join('%d' % lo if lo == hi else '%d..%d' % (lo, hi) for lo, hi in rng))
for name, base in (('CS:81E8 / 8737 (stage gate)', None),):
    pass
for s in (0xAC, 0x98):
    print('code-set byte %02X -> stages' % s, [e for e in range(8) if s >> e & 1])

print('\n== DS:118E start stage by flag', b(0x118E, 2))
print('== DS:6936 first fixture number per class (word)', [b(0x6936 + 2 * k) + 256 * b(0x6937 + 2 * k) for k in range(2)])

print('\n== slot permutations at DS:0F76 (builder: [DS:0F71 + 4*r + a], r,a = 1..4)')
for r in range(1, 5):
    print(r, [b(0xF71 + 4 * r + a) for a in range(1, 5)])

print('\n== 12-round schedule rows: row k at DS:0F54 + 0x18*k, pair of round r = bytes [+2r],[+2r+1], k = group + continent (2..12)')
ok = True
for k in range(2, 13):
    pairs = [(b(0xF54 + 0x18 * k + 2 * r), b(0xF54 + 0x18 * k + 2 * r + 1)) for r in range(1, 13)]
    full = sorted(pairs) == sorted((x, y) for x in range(1, 5) for y in range(1, 5) if x != y)
    ok &= full
    print(k, '%04X' % (0xF54 + 0x18 * k + 2), pairs, 'double round robin' if full else 'NOT a double round robin')
print('all rows double round robins of 4:', ok)

print('\n== friendlies partner table DS:1087 + 6*g + e (g 1..8, e 1..6): group of the same table the group plays friendlies against')
for g in range(1, 9):
    print(g, [b(0x1087 + 6 * g + e) for e in range(1, 7)], 'at %04X' % (0x1087 + 6 * g + 1))
print('friendly rounds limit DS:1106[class==0]:', 'class0 (stage2):', b(0x1107), 'class1 (stage5):', b(0x1106))

print('\n== single round robin pair list DS:10BC + 2*m (m 1..6) pairs', [(b(0x10BC + 2 * m), b(0x10BC + 2 * m + 1)) for m in range(1, 7)])
print('== DS:10C6 (WC friendlies 71B2: [8*... ]) bytes', b(0x10C6, 16))
print('== DS:10D5 bytes', b(0x10D5, 17))
print('== DS:10F9 (continent offsets 5EE1/6103: 0x1F+x) bytes', b(0x10F9, 8))
print('== DS:1104 (rounds friendlies list?)', b(0x1104, 4), 'DS:1106', b(0x1106, 2), 'DS:1108', b(0x1108, 2))
print('== DS:1110 continents per stage {x:4,7:1}', b(0x1110, 2), 'groups per continent DS:1112 {x:8, 3:2}', b(0x1112, 2))
print('== DS:0F72 + 4*r (71B2 finals slot order, r 1..4): ')
for r in range(1, 5):
    print(r, [b(0xF72 + 4 * r + k) for k in range(0, 4)])
