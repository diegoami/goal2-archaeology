#!/usr/bin/env python3
"""Regenerate static/goal-exe/ from the released GOAL.EXE, byte for byte.

    python3 tools/static/listing.py <released GOAL.EXE> <output directory>

It unpacks the file (tools/static/unlzexe.py), refuses any input whose sha256 is not the known
one, and disassembles the code segments with capstone (the version pinned in
tools/static/requirements.txt; it refuses another version, because another version may
print differently). The output is deterministic: no time, path or host in any file.
"""
import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import goalexe  # noqa: E402
from goalexe import DOS_FUNCTIONS, printable, track_ah  # noqa: E402
import unlzexe  # noqa: E402

PACKED_SHA256 = "a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664"
LINES_PER_PART = 1100  # about 60 KB a file, so that no file is too big to read

def ascii_col(bs):
    return "".join(chr(b) if printable(b) else "." for b in bs)


def fmt_ins(img, a, i, base):
    """One instruction as text, with relocated segment words named."""
    raw = bytes(i.bytes)
    off = a - base
    b0 = raw[0]
    reloc_at = [k for k in range(a, a + i.size) if k in img.relocs]
    if b0 in (0x9A, 0xEA) and len(raw) == 5:
        o = struct.unpack_from("<H", raw, 1)[0]
        s = struct.unpack_from("<H", raw, 3)[0]
        text = "%s far %04X:%04X" % ("call" if b0 == 0x9A else "jmp", s, o)
    else:
        text = i.mnemonic + (" " + i.op_str if i.op_str else "")
        if reloc_at:
            v = img.reloc_value[reloc_at[0]]
            text += "   ; relocated segment word %04X" % v
    return "%04X  %-15s %s" % (off, raw.hex(" ").upper(), text)


def dos_note(prev_ah, i):
    if i.mnemonic == "int" and i.operands and i.operands[0].imm == 0x21:
        if prev_ah is None:
            return "   ; INT 21h, AH not set by a nearby mov"
        return "   ; INT 21h AH=%02X %s" % (prev_ah, DOS_FUNCTIONS.get(prev_ah, "?"))
    return ""


def gap_rows(img, lo, hi, seg):
    """Rows for bytes that are not code: Pascal strings (length byte, text) and `db` rows."""
    rows = []
    a = lo
    raw = bytearray()
    raw_start = lo

    def flush():
        nonlocal raw
        for k in range(0, len(raw), 16):
            chunk = raw[k:k + 16]
            rows.append("%04X  %-15s db %s   ; %s" % (
                raw_start + k - seg * 16, "", " ".join("%02X" % b for b in chunk), ascii_col(chunk)))
        raw = bytearray()

    while a < hi:
        n = img.data[a]
        if n >= 3 and a + 1 + n <= hi and all(printable(b) for b in img.data[a + 1:a + 1 + n]):
            flush()
            txt = bytes(img.data[a + 1:a + 1 + n]).decode("ascii")
            rows.append("%04X  %-15s pstr %r" % (a - seg * 16, "", txt))
            a += 1 + n
            raw_start = a
            continue
        if not raw:
            raw_start = a
        raw.append(img.data[a])
        a += 1
    flush()
    return rows


def render_segment(img, dis, s, e):
    lo, hi = s * 16, e * 16
    starts = {a: why for a, why in dis.starts.items() if lo <= a < hi}
    routine_starts = {a for a, why in starts.items() if why & {"entry", "call", "far", "prologue"}}
    jump_targets = {a for a, why in starts.items() if "jump" in why}
    lines = []
    a = lo
    prev_ah = None
    while a < hi:
        if a in routine_starts:
            lines.append("")
            lines.append("; ---- routine %04X:%04X  (found by: %s)" % (s, a - lo, ", ".join(sorted(starts[a]))))
            lines.append("sub_%04X:" % (a - lo))
            prev_ah = None
        elif a in jump_targets:
            lines.append("loc_%04X:" % (a - lo))
        if a in dis.ins:
            i = dis.ins[a]
            lines.append(fmt_ins(img, a, i, lo) + dos_note(prev_ah, i))
            prev_ah = track_ah(prev_ah, i)
            a += i.size
        else:
            b = a
            while b < hi and not dis.covered[b]:
                b += 1
            lines.append("; data (not reached as code), %d bytes" % (b - a))
            lines += gap_rows(img, a, b, s)
            a = b
    return lines


def header(kind, tool, unpacked_sha, extra):
    return [
        "; GOAL.EXE (goal (version 2), artifact set goal2-a949da2f), %s" % kind,
        "; packed GOAL.EXE sha256 %s (92,391 bytes, LZEXE 0.91)" % PACKED_SHA256,
        "; unpacked (tools/static/unlzexe.py) sha256 %s" % unpacked_sha,
        "; tool: %s" % tool,
        "; addresses are SEGMENT:OFFSET with SEGMENT the image paragraph before relocation; image offset = SEGMENT*16+OFFSET",
    ] + extra


def write(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def split_parts(lines):
    """Parts of about LINES_PER_PART lines, cut only just before a routine."""
    parts, cur = [], []
    for ln in lines:
        if len(cur) >= LINES_PER_PART and ln.startswith("; ---- routine"):
            parts.append(cur)
            cur = []
        cur.append(ln)
    if cur:
        parts.append(cur)
    return parts


def hexdump(img, lo, hi, seg):
    rows = []
    prev, star = None, False
    for a in range(lo, hi, 32):
        chunk = bytes(img.data[a:min(a + 32, hi)])
        if chunk == prev:
            if not star:
                rows.append("*")
                star = True
            continue
        star = False
        prev = chunk
        rows.append("%04X  %s  |%s|" % (a - seg * 16, chunk.hex(" ").upper().ljust(32 * 3 - 1), ascii_col(chunk)))
    rows.append("%04X" % (hi - seg * 16))
    return rows


def find_strings(img, lo, hi, seg):
    """ASCII runs of >= 4 printable bytes; a run is a Pascal string when the byte before it
    (or its first byte) equals its length."""
    out = []
    a = lo
    while a < hi:
        if printable(img.data[a]):
            b = a
            while b < hi and printable(img.data[b]):
                b += 1
            n = b - a
            if n >= 4:
                kind = "ascii"
                txt = bytes(img.data[a:b])
                if a > lo and img.data[a - 1] == n:
                    kind, a = "pstr", a - 1  # the address of a Pascal string is its length byte
                elif img.data[a] == n - 1:
                    kind, txt = "pstr", txt[1:]
                out.append((a, kind, txt.decode("ascii")))
            a = b
        else:
            a += 1
    return out


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__)
        return 2
    pkg, core = goalexe.capstone_version()
    if pkg != goalexe.CAPSTONE_PIN:
        sys.stderr.write("listing: capstone %s is installed, %s is pinned (tools/static/requirements.txt)\n" % (
            pkg, goalexe.CAPSTONE_PIN))
        return 1
    with open(argv[1], "rb") as f:
        packed = f.read()
    if hashlib.sha256(packed).hexdigest() != PACKED_SHA256:
        sys.stderr.write("listing: not the known GOAL.EXE (sha256 differs)\n")
        return 1
    exe = unlzexe.unpack(packed)
    usha = hashlib.sha256(exe).hexdigest()
    img = goalexe.Image(exe)
    dis = goalexe.Disassembly(img)
    out = argv[2]
    for sub in ("code", "data"):  # regenerate from scratch: no stale part files
        shutil.rmtree(os.path.join(out, sub), ignore_errors=True)
    tool = "capstone %s (pip package; core library %s) (CS_ARCH_X86, CS_MODE_16), recursive descent from the entry point, far calls and near calls/jumps, then routine prologues (55 89 E5 / 55 8B EC) in what remains; tools/static/listing.py" % (pkg, core)
    seg_files = []
    for s, e in img.code_segments:
        lines = render_segment(img, dis, s, e)
        parts = split_parts(lines)
        for k, part in enumerate(parts, 1):
            name = "code/seg_%04X_%02d.asm" % (s, k)
            hdr = header("code segment %04X (image offsets %05X..%05X), part %d of %d" % (s, s * 16, e * 16 - 1, k, len(parts)),
                         tool, usha, [])
            write(os.path.join(out, name), hdr + part)
            seg_files.append((s, e, name))
    # data segment: hexdump
    ds = img.ds
    total = len(img.data)
    dlines = hexdump(img, ds * 16, total, ds)
    k = 0
    chunk = 300
    while k * chunk < len(dlines):
        part = dlines[k * chunk:(k + 1) * chunk]
        hdr = header("data segment %04X as hex (initialised part, image offsets %05X..%05X), part %d" % (ds, ds * 16, total - 1, k + 1),
                     "tools/static/listing.py (no disassembly)", usha,
                     ["; 32 bytes a row; '*' repeats the row above; offsets are DS offsets"])
        write(os.path.join(out, "data/ds_%04X_%02d.hex" % (ds, k + 1)), hdr + part)
        k += 1
    # strings
    rows = ["segment:offset\timage_offset\tkind\ttext"]
    for s, e in img.code_segments:
        for a, kind, txt in find_strings_code_gaps(img, dis, s, e):
            rows.append("%04X:%04X\t%05X\t%s\t%s" % (s, a - s * 16, a, kind, txt))
    for a, kind, txt in find_strings(img, ds * 16, total, ds):
        rows.append("%04X:%04X\t%05X\t%s\t%s" % (ds, a - ds * 16, a, kind, txt))
    hdr = header("strings (ASCII runs of 4 or more printable bytes, in code gaps and the data segment)", "tools/static/listing.py", usha,
                 ["; kind pstr = length-prefixed (Pascal) string, ascii = anything else; heuristic, not a parse"])
    write(os.path.join(out, "strings.tsv"), hdr + rows)
    import xrefs
    xrefs.write_tables(img, dis, out, header, tool, usha, write)
    write(os.path.join(out, "README.md"), readme(img, dis, seg_files, usha, tool))
    return 0


def find_strings_code_gaps(img, dis, s, e):
    res = []
    lo, hi = s * 16, e * 16
    a = lo
    while a < hi:
        if dis.covered[a]:
            a += 1
            continue
        b = a
        while b < hi and not dis.covered[b]:
            b += 1
        res += find_strings(img, a, b, s)
        a = b
    return res


def readme(img, dis, seg_files, usha, tool):
    n_ins = len(dis.ins)
    lines = [
        "# static/goal-exe/",
        "",
        "Generated, never edited by hand: `python3 tools/static/listing.py <released GOAL.EXE> static/goal-exe` (or",
        "`tools/static/regenerate.sh`) rewrites every file here byte for byte.",
        "",
        "- Artifact: `GOAL.EXE` of artifact set `goal2-a949da2f`, packed sha256 `%s` (LZEXE 0.91)." % PACKED_SHA256,
        "- Unpacked by `tools/static/unlzexe.py`: sha256 `%s`, %d bytes (the unpacked file is never committed)." % (usha, len(img.data) + img.header[4] * 16),
        "- Tool: %s." % tool,
        "- Image: %d bytes of load module (%d relocations). Entry point %04X:%04X, stack %04X:%04X.  Data segment %04X." % (
            len(img.data), len(img.relocs), img.cs, img.ip, img.ss, img.sp, img.ds),
        "- Addresses are `SEGMENT:OFFSET` where SEGMENT is the paragraph in the image before relocation (what the file holds);",
        "  the image offset is `SEGMENT*16 + OFFSET`; the unpacked file's offset is that plus its header size (%d bytes)." % (img.header[4] * 16),
        "  A relocated segment word in an instruction is shown by its unrelocated value.",
        "- %d instructions decoded; %d of %d code-segment bytes are code. The rest is reported as `data`." % (
            n_ins, sum(dis.covered[s * 16:e * 16].count(1) for s, e in img.code_segments),
            sum((e - s) * 16 for s, e in img.code_segments)),
        "",
        "| File | What |",
        "| --- | --- |",
    ]
    for s, e, name in seg_files:
        lines.append("| `%s` | code segment %04X (image %05X..%05X) |" % (name, s, s * 16, e * 16 - 1))
    lines += [
        "| `data/ds_%04X_NN.hex` | the initialised data segment as hex with ASCII |" % img.ds,
        "| `strings.tsv` | ASCII runs and Pascal strings, with addresses |",
        "| `routines.tsv` | every routine found: address, size, callers, INT 21h functions, string and data references |",
        "| `calls.tsv` | call edges: caller routine, callee |",
        "| `datarefs.tsv` | data-segment offsets and the routines that reference them |",
        "",
        "Method limits: recursive descent misses code reached only through computed jumps or procedure",
        "variables unless a routine prologue shows it; bytes after the last decoded instruction of a gap are",
        "reported as data. A listing line is capstone's decoding of the bytes, not a claim about the program.",
        "",
        "Decompiled view: `decompiled/` holds Ghidra's pseudo-C of every routine here, headed by the same",
        "`SEGMENT:OFFSET`, with `decompiled/index.tsv` giving each routine's file and line",
        "(`tools/static/decompile.sh`, not run by this script). What it can be trusted for, checked against",
        "hand-traced claims, is in `findings/F009-*.md`; where it and this listing differ, the listing decides.",
        "",
        "Named view: `named/` is the same pseudo-C with the names of `annotations/` applied (routines, the player",
        "and country records, globals), each with its confidence and basis (`tools/static/decompile.sh --annotations`,",
        "T20; `tools/static/check_annotations.py` checks the rows). Read it first; `decompiled/` stays the raw view.",
    ]
    return lines


if __name__ == "__main__":
    sys.exit(main(sys.argv))
