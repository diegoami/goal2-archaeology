"""Tables derived from the disassembly: routines.tsv, calls.tsv, datarefs.tsv (called by listing.py)."""
import bisect
import os
import struct
from collections import Counter, defaultdict

import capstone

from goalexe import printable, track_ah

X86 = capstone.x86


def string_runs(img, lo, hi, covered=None):
    """ASCII runs (>= 4 printable bytes, none of them decoded as code) as (start, end) image offsets."""
    runs = []
    a = lo
    while a < hi:
        if printable(img.data[a]) and not (covered and covered[a]):
            b = a
            while b < hi and printable(img.data[b]) and not (covered and covered[b]):
                b += 1
            if b - a >= 4:
                runs.append((a, b))
            a = b
        else:
            a += 1
    return runs


class Strings:
    def __init__(self, runs):
        self.runs = runs
        self.starts = [r[0] for r in runs]

    def at(self, linear):
        """Text of the run that `linear` points into, or at the length byte just before it."""
        k = bisect.bisect_right(self.starts, linear + 1) - 1
        if k >= 0 and self.runs[k][0] - 1 <= linear < self.runs[k][1]:
            return self.runs[k]
        return None


def routine_table(img, dis):
    starts = sorted(a for a, why in dis.starts.items() if why & {"entry", "call", "far", "prologue"})
    return starts


def write_tables(img, dis, out, header, tool, usha, write):
    starts = routine_table(img, dis)
    start_set = set(starts)
    ds_lo = img.ds * 16
    ds_strs = Strings(string_runs(img, ds_lo, len(img.data)))
    code_strs = {s: Strings(string_runs(img, s * 16, e * 16, dis.covered)) for s, e in img.code_segments}

    def routine_of(a):
        k = bisect.bisect_right(starts, a) - 1
        if k < 0 or img.segment_of(starts[k]) != img.segment_of(a):
            return None
        return starts[k]

    callers = Counter()
    edges = Counter()
    datarefs = defaultdict(set)
    rinfo = defaultdict(lambda: {"ins": 0, "bytes": 0, "int21": Counter(), "ints": Counter(),
                                 "strs": [], "ds_direct": 0})
    prev_ah, prev_r = None, None
    for a in sorted(dis.ins):
        i = dis.ins[a]
        r = routine_of(a)
        if r is None:
            continue
        if r != prev_r:
            prev_ah, prev_r = None, r
        ri = rinfo[r]
        ri["ins"] += 1
        ri["bytes"] += i.size
        raw = bytes(i.bytes)
        s = img.segment_of(a)
        base = s * 16
        if i.mnemonic == "int" and i.operands:
            n = i.operands[0].imm
            if n == 0x21:
                ri["int21"]["%02X" % prev_ah if prev_ah is not None else "??"] += 1
            else:
                ri["ints"]["%02X" % n] += 1
        prev_ah = track_ah(prev_ah, i)
        target = None
        if raw[0] == 0x9A and (a + 3) in img.relocs:
            target = struct.unpack_from("<H", raw, 3)[0] * 16 + struct.unpack_from("<H", raw, 1)[0]
        elif i.mnemonic == "call" and i.operands and i.operands[0].type == X86.X86_OP_IMM:
            target = base + (i.operands[0].imm & 0xFFFF)
        if target is not None and target in start_set:
            callers[target] += 1
            edges[(r, target)] += 1
        # pointer idiom: mov di, imm16 ; push ds|cs ; push di (a constant or variable passed by reference)
        if raw[0] == 0xBF and len(raw) == 3 and (a + 1) not in img.relocs:
            v = struct.unpack_from("<H", raw, 1)[0]
            tail = bytes(img.data[a + 3:a + 5])
            if tail == b"\x1e\x57":
                datarefs[v].add(r)
                run = ds_strs.at(ds_lo + v)
                if run:
                    ri["strs"].append(("DS:%04X" % v, run))
            elif tail == b"\x0e\x57":
                run = code_strs[s].at(base + v)
                if run:
                    ri["strs"].append(("CS:%04X" % v, run))
        # direct or indexed DS memory operands, not bp/sp frames
        for op in i.operands:
            if op.type == X86.X86_OP_MEM and op.mem.segment in (0, X86.X86_REG_DS) \
                    and op.mem.base not in (X86.X86_REG_BP, X86.X86_REG_SP) \
                    and op.mem.index not in (X86.X86_REG_BP, X86.X86_REG_SP):
                if op.mem.base == 0 and op.mem.index == 0:
                    ri["ds_direct"] += 1
                    datarefs[op.mem.disp & 0xFFFF].add(r)
                elif op.mem.disp:
                    datarefs[op.mem.disp & 0xFFFF].add(r)

    def addr(a):
        s = img.segment_of(a)
        return "%04X:%04X" % (s, a - s * 16)

    def text(run):
        return bytes(img.data[run[0]:run[1]]).decode("ascii")[:36].replace("\t", " ")

    rows = ["segment:offset\tsize\tinstructions\tfound_by\tcallers\tint21_ah\tother_int\tds_direct_operands\tstring_refs (first 4)"]
    for a in starts:
        r = rinfo[a]
        i21 = ",".join("%s:%d" % kv for kv in sorted(r["int21"].items()))
        oi = ",".join("%s:%d" % kv for kv in sorted(r["ints"].items()))
        strs, seen = [], set()
        for loc, run in r["strs"]:
            if (loc, run) in seen:
                continue
            seen.add((loc, run))
            strs.append("%s=%s" % (loc, text(run)))
        rows.append("%s\t%d\t%d\t%s\t%d\t%s\t%s\t%d\t%s" % (
            addr(a), r["bytes"], r["ins"], ",".join(sorted(dis.starts[a])), callers[a], i21, oi,
            r["ds_direct"], " | ".join(strs[:4])))
    hdr = header("routines found (a routine runs to the next routine start in its segment)", tool, usha,
                 ["; int21_ah is AH from the nearest preceding mov in the same routine (?? = not seen);",
                  "; string_refs: `mov di, imm16 / push ds|cs / push di` whose imm16 points into an ASCII run (>= 4 printable bytes)"])
    write(os.path.join(out, "routines.tsv"), hdr + rows)
    erows = ["caller\tcallee\tcount"]
    for (c, t), n in sorted(edges.items()):
        erows.append("%s\t%s\t%d" % (addr(c), addr(t), n))
    write(os.path.join(out, "calls.tsv"), header("call edges between routines (direct near and far calls)", tool, usha, []) + erows)
    drows = ["ds_offset\troutines\troutine_list (first 8)"]
    for v in sorted(datarefs):
        rs = sorted(datarefs[v])
        drows.append("DS:%04X\t%d\t%s" % (v, len(rs), " ".join(addr(x) for x in rs[:8])))
    hdr = header("data-segment offsets referenced by routines", tool, usha,
                 ["; an offset is listed when an instruction has a DS-relative memory operand with that displacement (direct or indexed, not bp/sp frames)",
                  "; or `mov di, imm16 / push ds / push di` with that value; a base address of an array is listed once, its elements are not"])
    write(os.path.join(out, "datarefs.tsv"), hdr + drows)
