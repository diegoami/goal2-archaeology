#!/usr/bin/env python3
"""Check the proposed structure of GOAL.DAT (finding F002, claims R001..R011) against the file.

    python3 tools/static/goaldat.py <released GOAL.DAT> [<output directory>]

Prints one line per check. With an output directory it writes blocks.tsv (the block table) and
checks.txt (every check, with the offsets and byte values it cites). Exit status 1 if any check
fails. The block sizes are the ones the game's loader reads, in order (GOAL.EXE, routine
1771:018A, sizes in the `mov ax, size` before each call far 214B:1B47); everything else here is
read from the bytes alone.
"""
import hashlib
import os
import sys

SHA256 = "bc5e5c04434d31f350eb7803afc3810333393e049d50dde559797a5b068c60ca"

# (name, size in bytes, record size or None, records) in file order. The sizes are the loader's.
BLOCKS = [
    ("country_names", 0x0810, 16, 129),
    ("player_names", 0x8387, 11, 3061),
    ("player_initials", 0x0BF5, 1, 3061),
    ("manager_names", 0x06DB, 13, 135),
    ("manager_initials", 0x0087, 1, 135),
    ("per_country_3", 0x0183, 3, 129),
    ("per_country_a", 0x0081, 1, 129),
    ("per_country_b", 0x0081, 1, 129),
    ("per_country_c", 0x0081, 1, 129),
    ("squad_20", 0x0A14, 20, 129),
]
LOADER_DEST = ["[9B68] heap", "[9B6C] heap", "[9B70] heap", "[9B74] heap", "[9B78] heap",
               "DS:9D80", "DS:9B7C", "DS:9BFD", "DS:9C7E", "DS:9F03"]


def printable(b):
    return 0x20 <= b < 0x7F


def block_offsets():
    o, out = 0, []
    for name, size, rec, n in BLOCKS:
        assert rec * n == size, name
        out.append((name, o, size, rec, n))
        o += size
    return out


class Checks:
    def __init__(self):
        self.rows = []
        self.failed = 0

    def add(self, cid, ok, text):
        self.rows.append((cid, ok, text))
        if not ok:
            self.failed += 1


def pascal_records(data, off, rec, n, maxlen, last=None):
    """Records 1..last (default n-1) of a table of 'Pascal string' records. A record is well
    formed when its length byte is in 1..maxlen and the bytes after it, up to the first zero byte
    or the end of the record, are 1 or more printable ASCII bytes. Returns (bad, equal, longer,
    shorter, examples): `longer` counts records whose text run is longer than the length byte says,
    `shorter` those whose length byte exceeds the text run."""
    last = n - 1 if last is None else last
    bad, equal, longer, shorter, ex = [], 0, 0, 0, []
    for i in range(1, last + 1):
        r = data[off + rec * i: off + rec * (i + 1)]
        ln = r[0]
        k = 1
        while k < rec and printable(r[k]):
            k += 1
        run = k - 1
        # a run must end at a zero byte or at the record's end (not at some other byte)
        if not (1 <= ln <= maxlen and run >= 1 and (k == rec or r[k] == 0)):
            bad.append(i)
            continue
        if run == ln:
            equal += 1
        elif run > ln:
            longer += 1
            ex.append((i, ln, bytes(r[1:1 + run]).decode()))
        else:
            shorter += 1
            ex.append((i, ln, bytes(r[1:1 + run]).decode()))
    return bad, equal, longer, shorter, ex


def desc(name, st, off, rec):
    bad, equal, longer, shorter, ex = st
    return ("length byte = text run in %d records, text run longer than the length byte in %d, shorter in %d (e.g. %s; the first at 0x%04X)" % (
        equal, longer, shorter, ", ".join("record %d length %d text %r" % e for e in ex[:2]),
        off + rec * ex[0][0] if ex else off))


def run_checks(data):
    c = Checks()
    blocks = block_offsets()
    total = sum(b[2] for b in blocks)
    c.add("R001", len(data) == total == 44040 and hashlib.sha256(data).hexdigest() == SHA256,
          "ten blocks, in this order and of these sizes, cover offsets 0x0000..0xAC07 = %d bytes = the file size; block offsets: %s" % (
              total, ", ".join("%s 0x%04X+0x%04X" % (n, o, s) for n, o, s, _, _ in blocks)))
    off = {b[0]: b for b in blocks}

    def zero_first(name):
        _, o, s, rec, n = off[name]
        return not any(data[o:o + rec])

    # R002 country names
    _, o, sz, rec, n = off["country_names"]
    st = pascal_records(data, o, rec, n, 15)
    c.add("R002", not st[0] and zero_first("country_names"),
          "0x%04X..0x%04X: %d records of %d bytes; record 0 (0x%04X) is all zero; in records 1..128 byte 0 is a length 1..15 and the bytes after it up to the first zero byte are printable ASCII (malformed records: %s); %s; first name %r at 0x%04X, last %r at 0x%04X" % (
              o, o + sz - 1, n, rec, o, st[0][:5], desc("", st, o, rec),
              bytes(data[o + 17:o + 17 + data[o + 16]]).decode(), o + 16,
              bytes(data[o + 16 * 128 + 1:o + 16 * 128 + 1 + data[o + 16 * 128]]).decode(), o + 16 * 128))
    # R003 player names
    _, o, sz, rec, n = off["player_names"]
    st = pascal_records(data, o, rec, n, 10)
    c.add("R003", not st[0] and zero_first("player_names"),
          "0x%04X..0x%04X: %d records of %d bytes; record 0 is all zero; in records 1..3060 byte 0 is a length 1..10 and the bytes after it up to the first zero byte or the record's end are printable ASCII (malformed: %s); %s; record 1 %r at 0x%04X, record 3060 %r at 0x%04X" % (
              o, o + sz - 1, n, rec, st[0][:5], desc("", st, o, rec),
              bytes(data[o + 12:o + 12 + data[o + 11]]).decode(), o + 11,
              bytes(data[o + 11 * 3060 + 1:o + 11 * 3060 + 1 + data[o + 11 * 3060]]).decode(), o + 11 * 3060))
    # R004 initials
    _, o, s, rec, n = off["player_initials"]
    letters = data[o + 1:o + n]
    c.add("R004", data[o] == 0 and all(65 <= b <= 90 for b in letters),
          "0x%04X..0x%04X: %d bytes; byte 0 is 0; bytes 1..3060 are all upper-case ASCII letters (%d distinct letters)" % (
              o, o + s - 1, n, len(set(letters))))
    # R005 manager names
    _, o, sz, rec, n = off["manager_names"]
    st = pascal_records(data, o, rec, n, 12, last=128)
    tail_zero = not any(data[o + rec * 129:o + sz])
    c.add("R005", not st[0] and zero_first("manager_names") and tail_zero,
          "0x%04X..0x%04X: %d records of %d bytes; record 0 is all zero; in records 1..128 byte 0 is a length 1..12 and the bytes after it up to the first zero byte are printable ASCII (malformed: %s); records 129..134 are all zero; %s; record 1 %r at 0x%04X, record 128 %r at 0x%04X" % (
              o, o + sz - 1, n, rec, st[0][:5], desc("", st, o, rec),
              bytes(data[o + 14:o + 14 + data[o + 13]]).decode(), o + 13,
              bytes(data[o + 13 * 128 + 1:o + 13 * 128 + 1 + data[o + 13 * 128]]).decode(), o + 13 * 128))
    # R006 manager initials
    _, o, s, rec, n = off["manager_initials"]
    letters = data[o + 1:o + 129]
    c.add("R006", data[o] == 0 and all(65 <= b <= 90 for b in letters) and not any(data[o + 129:o + n]),
          "0x%04X..0x%04X: %d bytes; byte 0 is 0; bytes 1..128 are upper-case ASCII letters; bytes 129..134 are 0" % (o, o + s - 1, n))
    # R007 per-country triples
    _, o, s, rec, n = off["per_country_3"]
    vals = list(data[o + 3:o + s])
    counts = {v: vals.count(v) for v in sorted(set(vals))}
    c.add("R007", not any(data[o:o + 3]) and all(9 <= v <= 15 for v in vals),
          "0x%04X..0x%04X: %d records of 3 bytes; record 0 is zero; every byte of records 1..128 is in 9..15 (counts by value: %s); "
          "the code (0791:1073) reads byte 0 and byte 2 of a team's record and byte 1 when they would be equal; the meaning of the three bytes is not decoded here" % (
              o, o + s - 1, n, counts))
    # R008 per-country bytes a
    _, o, s, rec, n = off["per_country_a"]
    v = list(data[o:o + s])
    c.add("R008", v[0] == 0 and len(set(v[1:])) > 1,
          "0x%04X..0x%04X: %d bytes, one per country 0..128; byte 0 is 0; bytes 1..128 hold %d distinct values in %d..%d; the loader code 1771:9A40 copies byte i into field +0x2D of country record i; not decoded" % (
              o, o + s - 1, n, len(set(v[1:])), min(v[1:]), max(v[1:])))
    # R009, R010 permutations
    for cid, name in (("R009", "per_country_b"), ("R010", "per_country_c")):
        _, o, s, rec, n = off[name]
        v = list(data[o:o + s])
        c.add(cid, v[0] == 0 and sorted(v) == list(range(129)),
              "0x%04X..0x%04X: %d bytes; byte 0 is 0; the values are each of 0..128 exactly once (a permutation); identity: %s" % (
                  o, o + s - 1, n, v == list(range(129))))
    # R011 squad_20
    _, o, sz, rec, n = off["squad_20"]
    allv = list(data[o + 20:o + sz])
    sorted_both, exceptions, zeros_ok = 0, [], True
    for i in range(1, n):
        r = list(data[o + 20 * i:o + 20 * (i + 1)])
        a, b = r[:11], r[11:]
        if a == sorted(a) and b == sorted(b):
            sorted_both += 1
        else:
            exceptions.append(i)
        if r[0] != 0 or r[11] != 0:
            zeros_ok = False
    c.add("R011", not any(data[o:o + 20]) and zeros_ok and min(allv) == 0 and max(allv) == 13 and len(set(allv)) == 14,
          "0x%04X..0x%04X: %d records of 20 bytes; record 0 is all zero; in every record 1..128 byte 0 and byte 11 are 0; all values lie in 0..13 and all 14 values occur; "
          "bytes 0..10 and bytes 11..19 are each non-decreasing in %d of 128 records (exceptions: records %s, at offsets %s)" % (
              o, o + sz - 1, n, sorted_both, exceptions, ", ".join("0x%04X" % (o + 20 * i) for i in exceptions)))
    return c


def main(argv):
    if len(argv) not in (2, 3):
        sys.stderr.write(__doc__)
        return 2
    with open(argv[1], "rb") as f:
        data = f.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        sys.stderr.write("goaldat: not the known GOAL.DAT (sha256 differs)\n")
        return 1
    c = run_checks(data)
    lines = ["%s %s %s" % (cid, "OK  " if ok else "FAIL", text) for cid, ok, text in c.rows]
    for ln in lines:
        print(ln[:200] + ("..." if len(ln) > 200 else ""))
    if len(argv) == 3:
        os.makedirs(argv[2], exist_ok=True)
        with open(os.path.join(argv[2], "blocks.tsv"), "w", newline="\n") as f:
            f.write("; GOAL.DAT sha256 %s (44,040 bytes); sizes are the loader's, GOAL.EXE 1771:018A\n" % SHA256)
            f.write("block\tfile_offset\tsize\trecord_size\trecords\tloader_destination\n")
            for (name, o, s, rec, n), dest in zip(block_offsets(), LOADER_DEST):
                f.write("%s\t0x%04X\t%d\t%d\t%d\t%s\n" % (name, o, s, rec, n, dest))
        with open(os.path.join(argv[2], "checks.txt"), "w", newline="\n") as f:
            f.write("; tools/static/goaldat.py on GOAL.DAT sha256 %s\n" % SHA256)
            f.write("\n".join(lines) + "\n")
    return 1 if c.failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
