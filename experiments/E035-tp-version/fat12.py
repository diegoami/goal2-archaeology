#!/usr/bin/env python3
"""Minimal read-only FAT12 floppy-image reader: list / extract files (recursive).
usage: fat12.py ls IMG | fat12.py x IMG OUTDIR
Reads the image only; runs nothing of Borland's."""
import struct, sys, os


class Fat12:
    def __init__(s, path):
        s.d = open(path, 'rb').read()
        d = s.d
        (s.bps, s.spc, s.res, s.nfat, s.nroot, s.tot, _m, s.spf) = struct.unpack_from('<HBHBHHBH', d, 11)
        s.fat = d[s.res * s.bps:(s.res + s.spf) * s.bps]
        s.rootoff = (s.res + s.nfat * s.spf) * s.bps
        s.dataoff = s.rootoff + s.nroot * 32

    def nxt(s, c):
        o = c * 3 // 2
        v = s.fat[o] | (s.fat[o + 1] << 8)
        return (v >> 4) if c & 1 else (v & 0xFFF)

    def chain(s, c):
        out = b''
        while 2 <= c < 0xFF8:
            o = s.dataoff + (c - 2) * s.spc * s.bps
            out += s.d[o:o + s.spc * s.bps]
            c = s.nxt(c)
        return out

    def entries(s, raw):
        for i in range(0, len(raw), 32):
            e = raw[i:i + 32]
            if e[0] == 0:
                break
            if e[0] == 0xE5 or e[11] & 0x08:
                continue
            name = e[:8].decode('latin1').rstrip()
            ext = e[8:11].decode('latin1').rstrip()
            yield (name + ('.' + ext if ext else '')), e[11], struct.unpack_from('<H', e, 26)[0], struct.unpack_from('<I', e, 28)[0]

    def walk(s, raw=None, prefix=''):
        if raw is None:
            raw = s.d[s.rootoff:s.dataoff]
        for n, a, c, sz in s.entries(raw):
            if n in ('.', '..'):
                continue
            if a & 0x10:
                yield from s.walk(s.chain(c), prefix + n + '/')
            else:
                yield prefix + n, c, sz


if __name__ == '__main__':
    f = Fat12(sys.argv[2])
    for n, c, sz in f.walk():
        if sys.argv[1] == 'ls':
            print(f'{sz:9d} {n}')
        else:
            p = os.path.join(sys.argv[3], n)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'wb').write(f.chain(c)[:sz])
