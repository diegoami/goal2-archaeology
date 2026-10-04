#!/usr/bin/env python3
"""Unpack an LZEXE 0.91 executable into a plain MZ executable.

Written from the public description of the LZEXE 0.91 format (the same one every
LZEXE unpacker follows); it uses no code from any of them.

The packed file is:

  0x00..0x1b  the MZ header (14 words). e_cs:e_ip point into the decompressor stub.
  0x1c..0x1f  the signature "LZ91"
  e_cparhdr*16  start of the load module: the compressed bit-stream (the first
              bytes after the header), then, at paragraph e_cs of the load module,
              the decompressor stub.
  stub + 0       eight words: ip0, cs0, sp0, ss0 (the original entry point and
              stack), the compressed size in paragraphs, the growth in
              paragraphs from compressed to unpacked image, two words that
              this tool does not use.
  stub + 0x158   the packed relocation table.

The bit-stream: a 16-bit word of flag bits, read least-significant bit first,
the next word being fetched as soon as the 16th bit of the current one is used.
  1                      one literal byte follows
  0 0 b1 b0, byte      a short match: length 2 + (b1 b0); the offset is the 16-bit
                         negative number 0xff00 | byte (1..256 bytes back)
  0 1, byte, byte2     a long match: the offset is the negative 16-bit number
                         0xe000 | ((byte2 & 0xf8) << 5) | byte (up to 8192 bytes back),
                         the length (byte2 & 7) + 2; when that is 2, one more byte
                         follows: 0 ends the stream, 1 changes segment (a no-op for a
                         flat output buffer), n >= 2 gives the length n + 1.
The relocation table is a list of spans between relocation addresses: a byte
(1..255); or a 0 byte and a word (2..65535); or 0, 0, 0 (advance the segment
by 0x0fff, offset unchanged); or 0, 1, 0 to end.

The output has the relocation table in the MZ header, the entry point and stack
restored from the stub, and a header padded to a multiple of 512 bytes. The
minimum and maximum allocation are derived (packed minalloc less the growth), they
are not the original packer's input, and they do not affect the code or data.

Usage: unlzexe.py <packed.exe> <unpacked.exe>   (prints the unpacked sha256 and size)
"""
import hashlib
import struct
import sys

STUB_RELOC_OFFSET = 0x158  # the packed relocation table, from the stub start, in 0.91 (0.90 used 0x19d)


class LzexeError(Exception):
    pass


def parse_header(data):
    if len(data) < 0x20 or data[:2] not in (b"MZ", b"ZM"):
        raise LzexeError("not an MZ executable")
    hdr = struct.unpack("<14H", data[:0x1C])
    if data[0x1C:0x20] != b"LZ91":
        raise LzexeError("no LZEXE 0.91 signature at 0x1c (found %r)" % data[0x1C:0x20])
    return hdr


class _Stream:
    def __init__(self, data, pos):
        self.d = data
        self.pos = pos

    def byte(self):
        if self.pos >= len(self.d):
            raise LzexeError("compressed stream ends early")
        v = self.d[self.pos]
        self.pos += 1
        return v

    def word(self):
        lo = self.byte()
        return lo | self.byte() << 8


def decompress(data, start):
    """Return (image, end_position) of the bit-stream that begins at `start`."""
    s = _Stream(data, start)
    bits = s.word()
    count = 16

    def getbit():
        nonlocal bits, count
        b = bits & 1
        count -= 1
        if count == 0:
            bits = s.word()
            count = 16
        else:
            bits >>= 1
        return b

    out = bytearray()
    while True:
        if getbit():
            out.append(s.byte())
            continue
        if not getbit():
            length = getbit() << 1
            length |= getbit()
            length += 2
            span = s.byte() | 0xFF00
        else:
            span = s.byte()
            length = s.byte()
            span |= ((length & ~7) << 5) | 0xE000
            length = (length & 7) + 2
            if length == 2:
                length = s.byte()
                if length == 0:
                    break
                if length == 1:
                    continue
                length += 1
        span -= 0x10000
        if len(out) + span < 0:
            raise LzexeError("match reaches before the start of the output")
        for _ in range(length):
            out.append(out[len(out) + span])
    return bytes(out), s.pos


def read_relocations(data, pos):
    """Decode the packed relocation table at `pos`: a list of (segment, offset)."""
    rel_off = 0
    rel_seg = 0
    relocs = []
    while True:
        if pos >= len(data):
            raise LzexeError("relocation table ends early")
        span = data[pos]
        pos += 1
        if span == 0:
            if pos + 2 > len(data):
                raise LzexeError("relocation table ends early")
            span = data[pos] | data[pos + 1] << 8
            pos += 2
            if span == 0:
                rel_seg += 0x0FFF
                continue
            if span == 1:
                break
        rel_off += span
        rel_seg += (rel_off & ~0x0F) >> 4
        rel_off &= 0x0F
        relocs.append((rel_seg & 0xFFFF, rel_off))
    return relocs


def build_mz(image, relocs, ip, cs, sp, ss, minalloc, maxalloc):
    hdr_len = (0x1C + 4 * len(relocs) + 0x1FF) & ~0x1FF
    total = hdr_len + len(image)
    words = [
        0x5A4D, total % 512, (total + 511) // 512, len(relocs), hdr_len // 16,
        minalloc & 0xFFFF, maxalloc & 0xFFFF, ss, sp, 0, ip, cs, 0x1C, 0,
    ]
    head = struct.pack("<14H", *words)
    for seg, off in relocs:
        head += struct.pack("<HH", off, seg)
    head += b"\0" * (hdr_len - len(head))
    return head + image


def unpack(data):
    """Unpack the bytes of an LZEXE 0.91 file; return the bytes of a plain MZ file."""
    hdr = parse_header(data)
    cparhdr, minalloc, maxalloc, cs = hdr[4], hdr[5], hdr[6], hdr[11]
    stub = (cs + cparhdr) << 4
    if stub + 16 > len(data):
        raise LzexeError("the stub lies beyond the end of the file")
    ip0, cs0, sp0, ss0, packed_paras, growth, _a, _b = struct.unpack("<8H", data[stub:stub + 16])
    start = (cs - packed_paras + cparhdr) << 4
    if not 0 < start < stub:
        raise LzexeError("inconsistent compressed size in the stub")
    image, end = decompress(data, start)
    if end > stub:
        raise LzexeError("the bit-stream runs into the stub")
    relocs = read_relocations(data, stub + STUB_RELOC_OFFSET)
    out_min = max(0, minalloc - growth)
    out_max = maxalloc if maxalloc == 0xFFFF else max(out_min, maxalloc - (minalloc - out_min))
    return build_mz(image, relocs, ip0, cs0, sp0, ss0, out_min, out_max)


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__.split("Usage:")[1])
        return 2
    try:
        with open(argv[1], "rb") as f:
            data = f.read()
        out = unpack(data)
    except (LzexeError, OSError) as e:
        sys.stderr.write("unlzexe: %s\n" % e)
        return 1
    with open(argv[2], "wb") as f:
        f.write(out)
    print("%s  %d  %s" % (hashlib.sha256(out).hexdigest(), len(out), argv[2]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
