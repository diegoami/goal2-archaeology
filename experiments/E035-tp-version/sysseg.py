#!/usr/bin/env python3
"""Cut the System-unit code segment out of a Turbo Pascal EXE (the target of the first far call of the
entry routine) and print/compare it. Reads files only.
usage: sysseg.py EXE            -> info line + first bytes
       sysseg.py cmp A.EXE B.EXE -> instruction-skeleton comparison of the two System segments
Skeleton = capstone mnemonic + operand kinds with immediates/displacements/addresses masked."""
import struct, sys, re, hashlib


def load(path):
    d = open(path, 'rb').read()
    hdr = struct.unpack_from('<HHHHHHHHHHHHHHH', d, 2)
    hdrsz = hdr[3] * 16
    ip, cs = hdr[9], hdr[10]
    img = d[hdrsz:]
    ent = cs * 16 + ip
    assert img[ent] == 0x9A, 'entry is not a far call'
    off, seg = struct.unpack_from('<HH', img, ent + 1)
    return img, seg, off, d


def sysseg(path):
    img, seg, off, d = load(path)
    # segment runs to the next code segment start we know of; take until the end of the image
    return img, seg * 16, d


def system_code(path):
    """The System segment's bytes (from its start to the data segment, whose paragraph the
    segment's first instruction `mov dx, imm` names) and the whole file."""
    img, seg, off, d = load(path)
    base = seg * 16
    code = img[base:base + 0x2400]
    dsg = struct.unpack_from('<H', code, 1)[0]
    return img[base:dsg * 16], d


def skel(code, base):
    from capstone import Cs, CS_ARCH_X86, CS_MODE_16
    md = Cs(CS_ARCH_X86, CS_MODE_16)
    md.detail = False
    out = []
    pos = 0
    while pos < len(code):
        got = False
        for i in md.disasm(code[pos:pos + 16], 0):
            op = re.sub(r'0x[0-9a-f]+|\b\d+\b', 'N', i.op_str)
            out.append((pos, i.size, i.mnemonic + ' ' + op, code[pos:pos + i.size]))
            pos += i.size
            got = True
            break
        if not got:
            out.append((pos, 1, 'db', code[pos:pos + 1]))
            pos += 1
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'cmp':
        a = sysseg(sys.argv[2]); b = sysseg(sys.argv[3])
    else:
        img, base, d = sysseg(sys.argv[1])
        print(sys.argv[1], 'size', len(d), 'system segment image offset 0x%X' % base)
        import hashlib
        print('sha256 of the first 48 bytes:', hashlib.sha256(img[base:base + 48]).hexdigest())
