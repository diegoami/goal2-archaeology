"""A small LZEXE 0.91 packer, for the tests only: it builds packed fixtures so that no
original file is needed. It follows the public format described in tools/static/unlzexe.py
and is written independently of the unpacker's code (it encodes; the unpacker decodes)."""
import struct

STUB_RELOC_OFFSET = 0x158


class _BitWriter:
    """Flag bits, 16 to a word, least-significant bit first. The reader fetches the next
    word the moment it uses the 16th bit, so the next word's 2 bytes are reserved at that
    moment, before the data bytes of the item that used it."""

    def __init__(self):
        self.out = bytearray()
        self.slot = None
        self.word = 0
        self.n = 0
        self._reserve()

    def _reserve(self):
        self.slot = len(self.out)
        self.out += b"\0\0"
        self.word = 0
        self.n = 0

    def bit(self, b):
        self.word |= (b & 1) << self.n
        self.n += 1
        if self.n == 16:
            self.out[self.slot:self.slot + 2] = struct.pack("<H", self.word)
            self._reserve()

    def byte(self, v):
        self.out.append(v & 0xFF)

    def finish(self):
        self.out[self.slot:self.slot + 2] = struct.pack("<H", self.word)
        return bytes(self.out)


def compress(image, segment_changes=(), stats=None):
    """Greedy LZ77 in LZEXE's token forms. `segment_changes` are output offsets at which a
    segment-change marker (long form, length byte 1) is emitted before the next token."""
    w = _BitWriter()
    stats = {} if stats is None else stats
    seg_at = set(segment_changes)
    i = 0
    n = len(image)
    while i < n:
        if i in seg_at:
            seg_at.discard(i)
            w.bit(0), w.bit(1)
            w.byte(0), w.byte(0)  # offset 0xe000 | 0, length field 0 -> extended
            w.byte(1)
            stats["segment_change"] = stats.get("segment_change", 0) + 1
            continue
        best_len, best_dist = 0, 0
        for dist in range(1, min(i, 8192) + 1):
            k = 0
            while i + k < n and k < 255 and image[i + k] == image[i + k - dist]:
                k += 1
            if k > best_len:
                best_len, best_dist = k, dist
        if best_len >= 2 and best_dist <= 256 and best_len <= 5:
            w.bit(0), w.bit(0)
            ln = best_len - 2
            w.bit(ln >> 1), w.bit(ln & 1)
            w.byte(0x100 - best_dist)
            stats["short"] = stats.get("short", 0) + 1
            i += best_len
        elif best_len >= 3:
            ln = min(best_len, 255)
            off = 0x2000 - best_dist  # 13-bit value: 0xe000 | off is the negative offset
            w.bit(0), w.bit(1)
            w.byte(off & 0xFF)
            if ln <= 9:
                w.byte(((off >> 5) & 0xF8) | (ln - 2))
                stats["long"] = stats.get("long", 0) + 1
            else:
                w.byte((off >> 5) & 0xF8)
                w.byte(ln - 1)
                stats["extended"] = stats.get("extended", 0) + 1
            if best_dist > 256:
                stats["far"] = stats.get("far", 0) + 1
            i += ln
        else:
            w.bit(1)
            w.byte(image[i])
            stats["literal"] = stats.get("literal", 0) + 1
            i += 1
    w.bit(0), w.bit(1)  # end marker: long form, length byte 0
    w.byte(0), w.byte(0)
    w.byte(0)
    return w.finish()


def pack_relocations(relocs):
    """relocs: (segment, offset) pairs. Spans between linear addresses, as LZEXE 0.91."""
    out = bytearray()
    prev = 0
    for seg, off in sorted(relocs, key=lambda r: r[0] * 16 + r[1]):
        span = seg * 16 + off - prev
        prev += span
        while span > 0xFFFF:
            out += b"\0\0\0"
            span -= 0xFFF0
        if span < 256 and span != 0:
            out.append(span)
        else:
            assert span >= 2, "two relocations cannot be 0 or 1 byte apart in this fixture"
            out += b"\0" + struct.pack("<H", span)
    out += b"\0\x01\0"
    return bytes(out)


def build_lzexe(image, relocs=(), ip0=0x0010, cs0=0x0003, sp0=0x0400, ss0=0x0020,
                minalloc=0x0100, growth=0x0007, segment_changes=(), signature=b"LZ91"):
    """A packed file: header, signature, bit-stream, stub (with the 8 info words) and the
    relocation table at stub + 0x158."""
    stream = compress(image, segment_changes)
    start = 0x20
    padded = (len(stream) + 15) & ~15
    paras = padded // 16
    stub = bytearray(struct.pack("<8H", ip0, cs0, sp0, ss0, paras, growth, 0x1234, 0x5678))
    stub += b"\x90" * (STUB_RELOC_OFFSET - len(stub))
    stub += pack_relocations(relocs)
    body = stream + b"\0" * (padded - len(stream)) + bytes(stub)
    total = start + len(body)
    words = [0x5A4D, total % 512, (total + 511) // 512, 0, 2, minalloc, 0xFFFF,
             0x2000, 0x80, 0, 0x000E, paras, 0x1C, 0]
    head = struct.pack("<14H", *words) + signature
    head += b"\0" * (start - len(head))
    return head + body
