#!/usr/bin/env python3
"""E025 round 3: the ORIGINAL instruction bytes of the routines F025 reasons about, run in Unicorn
over the edge values of the inputs each derived claim depends on.

    python3 -B experiments/E025-sacking-and-end/edge_probes.py <unpacked GOAL.EXE> <out log>

<unpacked GOAL.EXE> is `python3 tools/static/unlzexe.py <released GOAL.EXE> <file>` (sha256
6fd8c5ef...13188, checked). The image is loaded at segment 0x1000 with its MZ relocations applied;
only the data the routine reads is written (a state block, two country records, a manager table),
and the DS image itself is the original initialised data (so the set DS:0F3E, the table DS:118E and
the code-segment sets are the original's). No instruction of the routines is replaced. Two stubs, both
declared per probe: the call of 1771:80DA inside 1771:8208 is returned from immediately (its country
loop is not under test), and the "build constant" probes change ONE immediate byte in emulator
memory (the hypothesis F025 states), never in the file. Output is written with open(..., 'x').
"""
import hashlib
import struct
import sys
from pathlib import Path

from unicorn import (Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_CODE, UcError)
from unicorn.x86_const import (UC_X86_REG_AX, UC_X86_REG_BP, UC_X86_REG_CS, UC_X86_REG_DS, UC_X86_REG_ES,
                               UC_X86_REG_IP, UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_DI, UC_X86_REG_BX,
                               UC_X86_REG_CX, UC_X86_REG_DX, UC_X86_REG_SI)

L = 0x1000                       # load segment
DS = 0x2581 + L
SS = 0x3052 + L
RET_SEG = 0xE000                 # sentinel return address (never executed)
STATE_SEG, CTRY_SEG, MGR_SEG, FIX_SEG, FRAME_SEG = 0x6000, 0x6100, 0x6200, 0x6300, 0x6400
EXPECT_SHA = "6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188"
out = []


def say(s=""):
    print(s)
    out.append(s)


class Machine:
    def __init__(self, image):
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x100000)
        sig, last, pages, nrel, hdr, mina, maxa, ss, sp, cs_, ip, cs, relo, ovl = struct.unpack('<2sHHHHHHHHHHHHH', image[:28])
        body = image[hdr * 16:]
        self.mu.mem_write(L * 16, body)
        for k in range(nrel):
            off, seg = struct.unpack('<HH', image[relo + 4 * k:relo + 4 * k + 4])
            a = (L + seg) * 16 + off
            w = struct.unpack('<H', bytes(self.mu.mem_read(a, 2)))[0]
            self.mu.mem_write(a, struct.pack('<H', (w + L) & 0xFFFF))
        self.mu.reg_write(UC_X86_REG_DS, DS)
        self.mu.reg_write(UC_X86_REG_ES, DS)
        self.mu.reg_write(UC_X86_REG_SS, SS)
        self.snap = {}

    def wr(self, seg, off, data):
        self.mu.mem_write(seg * 16 + off, bytes(data))

    def rd(self, seg, off, n):
        return bytes(self.mu.mem_read(seg * 16 + off, n))

    def w16(self, seg, off, v):
        self.wr(seg, off, struct.pack('<H', v & 0xFFFF))

    def r16(self, seg, off):
        return struct.unpack('<H', self.rd(seg, off, 2))[0]

    def dsw(self, off, v):
        self.w16(DS, off, v)

    def far_ptr(self, off, seg_, ptr_seg, ptr_off=0):
        self.dsw(off, ptr_off)
        self.dsw(off + 2, ptr_seg)

    def code(self, seg):
        return seg + L

    def run(self, cs, ip, stack_words=(), near=False, until=None, stops=(), maxn=200000, sp=0x3F00, bp=0):
        """Run from cs:ip. stack_words are written upward from SP after the return address.
        Returns the address (cs, ip) where it stopped: `until` (default the sentinel return) or a stop hook."""
        mu = self.mu
        ret = [0x0000] if near else [0x0000, RET_SEG]
        ret_cs = cs if near else RET_SEG
        words = ret + list(stack_words)
        mu.reg_write(UC_X86_REG_SS, SS)
        mu.reg_write(UC_X86_REG_SP, sp)
        mu.reg_write(UC_X86_REG_BP, bp)
        for k, w in enumerate(words):
            self.w16(SS, sp + 2 * k, w)
        if near:
            self.w16(SS, sp, 0xFFF0)
        mu.reg_write(UC_X86_REG_CS, cs)
        hit = []
        hooks = []
        targets = list(stops)
        if until is None:
            until = (ret_cs * 16 + (0xFFF0 if near else 0))

        def h(uc, addr, size, user):
            hit.append(addr)
            uc.emu_stop()
        for t in targets:
            hooks.append(mu.hook_add(UC_HOOK_CODE, h, begin=t, end=t))
        try:
            mu.emu_start(cs * 16 + ip, until, count=maxn)
        finally:
            for k in hooks:
                mu.hook_del(k)
        return hit[0] if hit else None


def lin(seg, off):
    return (seg + L) * 16 + off


def set_state(m, stage=2, rounds=1, word=0, year=1994, groups=(0, 0, 0, 0, 0, 0, 0)):
    """the state block [DS:A923] at STATE_SEG:0 (0x110 bytes, zeroed)"""
    m.wr(STATE_SEG, 0, bytes(0x110))
    m.w16(STATE_SEG, 0x38, word)
    m.w16(STATE_SEG, 0x3A, year)
    m.wr(STATE_SEG, 0x3C, bytes([stage, rounds]))
    for i, g in enumerate(groups):
        m.wr(STATE_SEG, 2 + i, bytes([g]))   # [A923] + m + 1 for m = 1..
    m.far_ptr(0xA923, None, STATE_SEG)


def set_countries(m, ranks):
    """country records at CTRY_SEG:0xBF*i, i = 1..len(ranks): (continent, crank, wrank, manager_byte, be)"""
    m.wr(CTRY_SEG, 0, bytes(0xBF * (len(ranks) + 2)))
    for i, (cont, crank, wrank, mgr, be) in enumerate(ranks, 1):
        base = 0xBF * i
        m.wr(CTRY_SEG, base + 0x2A, bytes([crank, wrank, cont]))
        m.wr(CTRY_SEG, base + 0x2E, bytes([mgr]))
        m.wr(CTRY_SEG, base + 0xBE, bytes([be]))
    m.far_ptr(0xA917, None, CTRY_SEG)


def main():
    exe = Path(sys.argv[1]).read_bytes()
    sha = hashlib.sha256(exe).hexdigest()
    if sha != EXPECT_SHA:
        raise SystemExit(f"unpacked image sha256 {sha} != {EXPECT_SHA}")
    say(f"image sha256 {sha}; load segment {L:#x}; DS {DS:#x}")

    def fresh():
        m = Machine(exe)
        m.wr(MGR_SEG, 0, bytes(0x195))
        m.far_ptr(0xA91F, None, MGR_SEG)
        return m

    # ---------------------------------------------------------------- P1: 0791:B71C
    say("\n== P1 0791:B71C(fixture, side): the result term of one match, original bytes")
    say("columns: rating of side 0's country, rating of side 1's country | fixture kind | the side asked about | score side0:side1, winner byte (0 = side 0, 1 = side 1, 2 = draw) | delta for that side (signed word)")
    ratings = {"1": (4, 32, 128), "64": (3, 16, 64), "128": (1, 1, 1)}      # (continent, crank, wrank)

    def rating(c, cr, wr):
        return ((5 - c) * (0x21 - cr) + (0x81 - wr)) // 2
    rows = []
    for kind in (2, 3):           # 2 = outside DS:0F3E, 3 = inside (checked below from the image)
        for side in (0, 1):
            for (rn_a, rn_b) in (("1", "128"), ("128", "1"), ("64", "64")):
                for (sa, sb, win) in ((0, 1, 1), (1, 0, 0), (1, 1, 2), (0, 0, 2), (3, 0, 0), (0, 3, 1)):
                    m = fresh()
                    set_countries(m, [ratings[rn_a] + (0, 0), ratings[rn_b] + (0, 0)])
                    m.wr(FIX_SEG, 0, bytes([sa, sb, kind, win, 1, 0, 2, 0]))   # sides = country words 1 and 2
                    # fixture +4 = side 0's country, +6 = side 1's
                    m.w16(FIX_SEG, 4, 1)
                    m.w16(FIX_SEG, 6, 2)
                    m.run(L + 0x791, 0xB71C, stack_words=(side, 0, FIX_SEG))
                    # stack order: side is the arg nearest the return, then offset, then segment
                    ax = m.mu.reg_read(UC_X86_REG_AX)
                    delta = ax - 0x10000 if ax & 0x8000 else ax
                    rows.append((rn_a, rn_b, kind, side, sa, sb, win, delta,
                                 rating(*ratings[rn_a]), rating(*ratings[rn_b])))
    m = fresh()
    # membership of the kind in DS:0F3E, read from the image directly (Pascal set: bit k of byte k//8)
    sbytes = m.rd(DS, 0x0F3E, 32)
    members = [k for k in range(256) if sbytes[k // 8] >> (k % 8) & 1]
    say(f"DS:0F3E members (original bytes): {members}")
    for r in rows:
        say(f"ratings {r[8]:>3},{r[9]:>3} | kind {r[2]} | side {r[3]} | score {r[4]}:{r[5]} winner {r[6]} | delta {r[7]:+d}")

    # ---------------------------------------------------------------- P2: 1771:8208
    say("\n== P2 1771:8208 (stage_end): stage and rounds byte over many calls; stub: the near call of 1771:80DA returns at once")
    for label, const in (("registered build (constant 0)", 0), ("hypothesised shareware build (constant 1 written at 1771:822D in emulator memory)", 1)):
        for start_stage, start_rounds in ((8, 1), (2, 1), (5, 1), (8, 4)):
            m = fresh()
            set_state(m, stage=start_stage, rounds=start_rounds, word=1)
            m.mu.mem_write((L + 0x1771) * 16 + 0x822D, bytes([const]))
            trace = []
            stub_calls = []
            mu = m.mu

            def stub(uc, addr, size, user):
                stub_calls.append(m.rd(STATE_SEG, 0x3C, 1)[0])
                sp = uc.reg_read(UC_X86_REG_SP)
                ip = m.r16(SS, sp)
                uc.reg_write(UC_X86_REG_SP, sp + 2)
                uc.reg_write(UC_X86_REG_IP, ip)
            hk = mu.hook_add(UC_HOOK_CODE, stub, begin=lin(0x1771, 0x80DA), end=lin(0x1771, 0x80DA))
            for call in range(1, 300):
                m.run(L + 0x1771, 0x8208)
                st, rd_ = m.rd(STATE_SEG, 0x3C, 2)
                trace.append((call, st, rd_))
            mu.hook_del(hk)
            first = trace[:8]
            say(f"{label}; start (stage {start_stage}, rounds {start_rounds}): first calls (call, stage, rounds) {first}")
            changes = [t for t in trace if t[0] in (120, 252, 253, 254, 255, 256, 257, 258, 299)]
            say(f"    later: {changes}; 1771:80DA reached {len(stub_calls)} times, at new stages {sorted(set(stub_calls))}")

    # ---------------------------------------------------------------- P3: 000E:7072
    say("\n== P3 000E:7072 (shareware_limit_reached): AL for the build constant (written at 000E:7079 in emulator memory) and the year word")
    for const in (0, 1):
        res = []
        for word in (0, 1, 2, 3, 0x7FFF, 0x8000, 0xFFFF):
            m = fresh()
            set_state(m, word=word)
            m.mu.mem_write((L + 0xE) * 16 + 0x7079, bytes([const]))
            m.run(L + 0xE, 0x7072, near=True)
            res.append((word, m.mu.reg_read(UC_X86_REG_AX) & 0xFF))
        say(f"constant {const}: (word, AL) {res}")

    # ---------------------------------------------------------------- P4: the year word rise and the fold gate
    say("\n== P4 year word: 1771:811B (inc word [+0x38]) then the gate at 1771:675B (cmp word [+0x38], 0; jbe skip)")
    for word in (0, 1, 2, 0xFFFE, 0xFFFF):
        m = fresh()
        set_state(m, word=word)
        m.mu.reg_write(UC_X86_REG_ES, STATE_SEG)
        m.mu.reg_write(UC_X86_REG_DI, 0)
        m.run(L + 0x1771, 0x811B, until=lin(0x1771, 0x811B) + 4)       # the 4-byte inc instruction only
        new = m.r16(STATE_SEG, 0x38)
        m.mu.reg_write(UC_X86_REG_ES, STATE_SEG)
        m.mu.reg_write(UC_X86_REG_DI, 0)
        h = m.run(L + 0x1771, 0x675B, stops=(lin(0x1771, 0x6762), lin(0x1771, 0x6767)))
        say(f"word {word:#06x} -> after inc {new:#06x}; at 675B the fold 63A4 is {'called' if h == lin(0x1771, 0x6762) else 'skipped (goes to 6767)'}")

    # ---------------------------------------------------------------- P5: 000E:0B77 predicate
    say("\n== P5 000E:0B77: the four gates and the score, over the product of their inputs (original bytes)")
    frame_bp = 0x100
    n_ok = n_bad = 0
    shown = []
    for word in (0, 1, 2, 0xFFFF):
        for kind in (1, 2, 3):
            for stage in range(2, 9):
                for group in (0, 1, 7):
                    for be in (0, 1):
                        for score in (-128, -127, -12, -11, -10, -8, -7, -6, -5, 0, 5, 127):
                            m = fresh()
                            set_state(m, stage=stage, word=word, groups=(0, group, 0))     # manager m = 2 -> [A923]+3 = group
                            set_countries(m, [(1, 1, 1, 0x82, be), (2, 2, 2, 0x02, 0)])  # country 1 managed by manager 2 (+0x2E = 0x82)
                            m.wr(MGR_SEG, 3 * 0x82 + 2, bytes([score & 0xFF]))
                            m.wr(FIX_SEG, 0, bytes([1, 0, kind, 0, 1, 0, 2, 0]))
                            # the caller's frame: [bp+4] far fixture pointer (off, seg), [bp+8] the country word
                            m.w16(SS, frame_bp + 4, 0)
                            m.w16(SS, frame_bp + 6, FIX_SEG)
                            m.w16(SS, frame_bp + 8, 1)
                            m.run(L + 0xE, 0xB77, stack_words=(frame_bp,), near=True)
                            got = m.mu.reg_read(UC_X86_REG_AX)
                            got = got - 0x10000 if got & 0x8000 else got
                            zero = word < 2 or kind == 1 or (stage in (3, 4, 7, 8) and group != 0) or be != 0
                            want = 0 if zero else score
                            if got == want:
                                n_ok += 1
                            else:
                                n_bad += 1
                                shown.append((word, kind, stage, group, be, score, got, want))
    say(f"cases {n_ok + n_bad}; equal to the predicate 'returns 0 if word<2 (unsigned) or kind=1 or (stage in {{3,4,7,8}} and group<>0) or +0xBE<>0, else the signed score': {n_ok}; different: {n_bad}")
    for s in shown[:20]:
        say(f"  DIFFERENT (word, kind, stage, group, be, score) -> got, predicted: {s}")

    # ---------------------------------------------------------------- P6: 000E:319B thresholds
    say("\n== P6 000E:319B from 3712: which branch the score s = AX reaches (stop hooks on the first instruction of each branch)")
    branches = {0x371C: "GRIM", 0x375C: "JOB ON THE LINE", 0x3787: "SACKED text", 0x37B4: "ordinary loss"}
    seen = {}
    for s in range(-300, 301):
        m = fresh()
        m.mu.reg_write(UC_X86_REG_AX, s & 0xFFFF)
        m.mu.reg_write(UC_X86_REG_BP, 0x200)
        # frames: bp -> [bp+4] = 0x300 -> [0x300+4] = 0x400 (4E0E's frame)
        m.w16(SS, 0x204, 0x300)
        m.w16(SS, 0x304, 0x400)
        h = m.run(L + 0xE, 0x3712, stops=[lin(0xE, a) for a in branches], bp=0x200)
        seen[s] = branches.get(h - (L + 0xE) * 16) if h is not None else "no branch reached"
    ranges, start = [], -300
    for s in range(-299, 302):
        if s == 301 or seen[s] != seen[s - 1]:
            ranges.append((start, s - 1, seen[s - 1]))
            start = s
    for a, b, name in ranges:
        say(f"  s from {a} to {b}: {name}")
    # the store at 37AC sets 4E0E's flag [bp-2]: run 37A5..37B1 on the frames
    m = fresh()
    m.w16(SS, 0x204, 0x300)
    m.w16(SS, 0x304, 0x400)
    m.wr(SS, 0x400 - 2, b"\x00")
    m.run(L + 0xE, 0x37A5, stops=[lin(0xE, 0x37B1)], bp=0x200)
    say(f"  the flag byte at 4E0E's [bp-2] after 37A5..37B1: before 0, after {m.rd(SS, 0x3FE, 1)[0]}")

    # ---------------------------------------------------------------- P7: displayed year, 16-bit
    say("\n== P7 displayed year: 000E:59BC..59CD computes AX = 2*word + [+0x3A] (the value pushed for the number-to-string call)")
    for word in (0, 1, 2, 0x7FFF, 0x8000, 0xFFFF):
        m = fresh()
        set_state(m, word=word, year=1994)
        m.mu.reg_write(UC_X86_REG_ES, STATE_SEG)
        m.mu.reg_write(UC_X86_REG_DI, 0)
        m.w16(SS, 0x500 - 4, 0)             # [bp-4] = the state block's far pointer (59C2 reloads ES:DI from it)
        m.w16(SS, 0x500 - 2, STATE_SEG)
        m.run(L + 0xE, 0x59BC, stops=[lin(0xE, 0x59CC)], bp=0x500)
        say(f"word {word:#06x}, +0x3A = 1994 -> AX {m.mu.reg_read(UC_X86_REG_AX):#06x} ({m.mu.reg_read(UC_X86_REG_AX)})")


    # ---------------------------------------------------------------- P8: the starting stage
    say("\n== P8 1771:9B85 from 9BB5 to 9BF7: +0x40 and the starting stage from the (even) base year +0x3A (DS:118E = 02 05 in the image)")
    say(f"DS:118E bytes (original): {m.rd(DS, 0x118E, 2).hex()}")
    for base in (1990, 1992, 1994, 1996, 1998, 2000, 2002, 65534):
        m = fresh()
        set_state(m, year=base)
        m.w16(SS, 0x500 - 4, 0)
        m.w16(SS, 0x500 - 2, STATE_SEG)
        m.run(L + 0x1771, 0x9BB5, stops=[lin(0x1771, 0x9BF7)], bp=0x500)
        say(f"base year {base}: +0x40 = {m.rd(STATE_SEG, 0x40, 1)[0]}, starting stage {m.rd(STATE_SEG, 0x3C, 1)[0]}, year word {m.r16(STATE_SEG, 0x38)}")

    with open(sys.argv[2], 'x') as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
