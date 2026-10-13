#!/usr/bin/env python3
"""Check the whole-match harness against the E011 ground truth (T38 Done-when 1 and 2).

    python3 experiments/E021-m0-whole-match/check.py [--hook NAME]

For each E011 record: take its watchstart savestate (the captain screen before the kick-off; the
release E011 asset named by sha256, downloaded into .cache/dl/ when missing), emulate the whole
match with runtime/emul/watched_match.py to the full-time board, and check EVERY mid-play read of the
record (both halves; the record's "ground-truth trajectory" observation, none excluded) against the
emulated trajectory tick-exactly: the read's (DS:831F, DS:831D) names the clock reading, and its
DS:7B62 must be one of the values the seed word takes under that reading (E011 notes.md §6, F013).
Also: the full-time score equals the record's, the 000E skip log is empty, the keys delivered are
exactly the declared ones, and the seed word and the text screen (4000 bytes, sha256) at the board
equal the record's "full time" read. Ends with `match: N/N` (N = the records' reads) and the
hooked-call count; exits non-zero on an empty set, any miss or any failed check.

--hook substitutes 214B:0688 (F004's RNG step) with a Python LCG and PROVES it side by side at
every call (runtime/emul/watched_match.py, `hook(prove=True)`): the original routine runs to its
return with every byte it writes recorded, the state is put back, the model runs on it, and the
two must write the same bytes in the same order and return the same registers; the first
difference stops the run with a ProofError naming the call, the address and the byte. The hooks: `f004` is F004's
`seed = seed * 0x7ABD + 0x1B0F`, returning 1 + (seed * n) >> 16; `f004-mult+1` and `f004-inc+1`
change the multiplier or the increment by +1; `f004+hidden-write` writes 0xDEAD to the seed and
restores it before each F004 step, `f004+raw-write` does the same with raw `mu.mem_write` calls,
`f004+831D-write` writes 0xDEAD to DS:831D and restores it, and `f004+inc+1-off-seed` steps with
increment + 1 only when the seed pointer is not DS:7B62 (the hook's falsifiers). A hooked run is also compared with
an unhooked run of the same state: every write of the seed word (value before and after, clock
reading) must be the original's, in order.
--hook m2-287c (T46, M2b) substitutes 214B:0688, 0791:278A, 1771:377E and 0791:287C (runtime/model/contests.py), each
proved at every call. While 287C's original runs in its proof, the hooks of the routines it calls (278A, 0688) do not
fire: the original's inner calls are the original's own code (watched_match.original_running), so those routines'
counts here are M1's minus what 287C's calls make (545 each of 278A and 0688 per record); they are printed per record.
`m2-287c+inverted` flips 287C's AL, `m2-287c+n+1` adds 32 to the value it divides (n + 1): the falsifiers.
--hook m2-draws (T47, M2c) adds the draw wrappers 214B:06B1 and 214B:06D0 (runtime/model/draws.py) to M2b's four, six
routines each proved at every call. While a proof's original runs, the hooks of the routines it calls do not fire, so
the wrappers' counts are the reach log's (out/t47-reach-helpers.log, unhooked) minus the wrapper entries made inside the
originals of 278A, 377E and 287C (every entry counted by a code hook in the run, minus the hooked ones: 287C's 06D0 call, 545), and
0688's are M2b's minus one per wrapper call; the adjustment is computed and printed per record. Falsifiers:
`m2-draws+06b1-n+1` (draws in 1..n+1), `+06b1-value+1`, `+06d0-inverted`, `+06d0-seed-write` (the seed write dropped).
--hook m2-longs (T48, M2d) adds the long helpers 214B:0D56 (signed 32-bit max, runtime/model/longs.py) and 23E4:0279 (32-bit
multiply, register convention) to M2c's six: eight routines, each proved at every call. M2c's six keep M2c's counts
(out/t47-m2-draws-run2.log: 0D56 and 0279 call none of them); 0D56 and 0279 are the reach log's counts
(out/t48-reach-0d56-0279.log, unhooked) minus the entries made inside the originals of the other routines (counted by a
code hook, minus the hooked calls). Their scratch registers (BX, CX, SI, DI, ES) and arithmetic flags are reproduced, so
`scratch_differences` is printed per routine and is 0 for them. Falsifiers: `m2-longs+0d56-min` (min instead of max),
`+0d56-tie-a` (a on a tie: the two longs are equal, so no register changes: a tally shows the calls it would change),
`+0279-product+1`, `+0279-no-cross-term` (the `mul bx` term left out of DX), `+0279-scratch` (SI not reproduced: counted
in `scratch_differences`, not an error).
Each emulated run's outputs (without the draw list, whose count and sha256 they carry) are written
to a new file under experiments/E021-m0-whole-match/out/ (never overwritten)."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
import driver  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402
from unicorn import UC_HOOK_CODE  # noqa: E402
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import contests  # noqa: E402
import draws  # noqa: E402
import keeping  # noqa: E402
import longs  # noqa: E402
from condition import _Record  # noqa: E402  (a QuickMatch over literal records and the foot tables)
from quick_engine import idiv, s16, s8  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
# Wall-clock limit of one emulated match. M2c's six proofs took 1310-1480 s per record; the eight of M2d (T48) did not
# finish in the former 1800 s (3601 of 4149 ticks, four runs, out/t48-m2-longs*.log: void by timeout), so 5400 s.
RUN_TIMEOUT_S = 5400
DL = ROOT / ".cache/dl"
LCG_STEP = "214B:0688"
MULT, INC = 0x7ABD, 0x1B0F          # F004 (seg_214B_01.asm:881, :883)


def f004_step(mult=MULT, inc=INC):
    """F004's step as a hook fn: stack (far call) n at +4, the seed's far pointer at +6/+8;
    the new seed is stored, AX = DX = 1 + (new * n) >> 16 (seg_214B_01.asm:873-894)."""
    def fn(g):
        n, off, seg = g.arg(0), g.arg(1), g.arg(2)
        new = (g.word(seg, off) * mult + inc) & 0xFFFF
        g.set_word(seg, off, new)
        r = (((new * n) >> 16) + 1) & 0xFFFF
        g.set_reg("ax", r)
        g.set_reg("dx", r)
    return fn


def hidden_write(step):
    """A falsifier (review R1): `step` preceded by a write of 0xDEAD to the seed word and its
    restore, so the step's results are F004's but the word takes a value the original never
    writes."""
    def fn(g):
        off, seg = g.arg(1), g.arg(2)
        seed = g.word(seg, off)
        g.set_word(seg, off, 0xDEAD)
        g.set_word(seg, off, seed)
        step(g)
    return fn


def trace_difference(reference, draws):
    """None when the two seed-write traces are identical, else the first differing index with
    both entries (a missing entry is None)."""
    for i, (a, b) in enumerate(zip(reference, draws)):
        if a != b:
            return i, a, b
    if len(reference) != len(draws):
        i = min(len(reference), len(draws))
        return i, reference[i] if i < len(reference) else None, draws[i] if i < len(draws) else None
    return None


def raw_write(step):
    """A falsifier (review round 2, R1): 0xDEAD written to the seed word and restored with raw
    Unicorn writes (`g.mu.mem_write`), then F004's step."""
    def fn(g):
        lin = g.arg(2) * 16 + g.arg(1)
        saved = g.mem(lin, 2)
        g.mu.mem_write(lin, b"\xad\xde")
        g.mu.mem_write(lin, saved)
        step(g)
    return fn


def clock_write(step):
    """A falsifier (review round 2, R2): 0xDEAD written to DS:831D (the sub-tick) and restored,
    then F004's step."""
    def fn(g):
        saved = g.rd(0x831D)
        g.set_word(g.DS, 0x831D, 0xDEAD)
        g.set_word(g.DS, 0x831D, saved)
        step(g)
    return fn


def off_seed_increment(step, wrong):
    """A falsifier (review round 2, R3): F004's step on DS:7B62, the wrong step (increment + 1)
    when the seed pointer is elsewhere (DS:8336, the speaker stream)."""
    def fn(g):
        on_main = g.arg(2) * 16 + g.arg(1) == g.DS * 16 + 0x7B62
        (step if on_main else wrong)(g)
    return fn


SKILL_READER = "0791:278A"
RECORD_SIZE = 20            # 2797 `mov dx, 0x14; mul dx` (the player array's stride)


def skill_trace(g, off, seg, element, gate=None):
    """The model's run of 0791:278A on the guest's state (see skill_reader): (value, dx)."""
    pitch = seg * 16 + off
    index = g.word_at(pitch + 0xD)
    rec = g.far(0xA91B) + RECORD_SIZE * index
    p = lambda i: g.mem(rec + i, 1)[0]
    pb = lambda i: g.mem(pitch + i, 1)[0]
    # the tables are indexed by record bytes (+7, +5): the original reads DS memory past the
    # documented 168 / 192 bytes (E011-r0001 call #77: +5 = 0x10, row 16 of DS:6DCD), so the
    # model gets the following bytes of the data segment too (12 * 255 + 255 < 4096)
    classes = g.mem(g.DS * 16 + 0x6D25, 4096)
    profiles = g.mem(g.DS * 16 + 0x6DCD, 4096)
    saved = keeping.KEEPER_EVENTS
    if gate is not None:
        keeping.KEEPER_EVENTS = gate
    try:
        return keeping.contest_trace(p(4), p(5), p(7), p(0xC), p(0xE), element, classes, profiles,
                                     pb(0x13), pb(0x11), g.rd(0x8327, 1), g.rd(0x80FC, 1), pb(6))
    finally:
        keeping.KEEPER_EVENTS = saved


def skill_reader(gate=None, product_plus=0):
    """0791:278A as a hook fn (M1a): reads the routine's inputs from the guest and decides its result
    with keeping.contest_trace. Far-called with `retf 6` (2879): stack args off (bp+6), seg (bp+8),
    element (bp+0xA) = arg(0), arg(1), arg(2). Reads: the pitch record's word +0xD (2793, the player
    index), +0x13 (27F1), +0x11 (2846), +6 (2852); the player record at the far pointer DS:A91B
    (279C) + 0x14 * index, bytes +0xC (27AB), +0xE (27D4), +4/+5/+7 (3A06, seg_1771_05.asm:3A06-3A7F,
    keeping.skill_value), the tables DS:6D25 and DS:6DCD (4096 bytes each: see below), DS:8327 (2833) and
    DS:80FC (2859). Results: AX = the value (2870-2873); DX is what the last `div` left (281C's
    remainder, or 2865's `value % 0x10` when the manager's share is added), which the proof compares
    (REGS_RETURNED). `gate` replaces keeping.KEEPER_EVENTS and `product_plus` adds to the value
    (the falsifiers)."""
    def fn(g):
        off, seg, element = g.arg(0), g.arg(1), g.arg(2)
        value, dx = skill_trace(g, off, seg, element, gate)
        g.set_reg("ax", (value + product_plus) & 0xFFFF)
        g.set_reg("dx", dx)
    return fn

STRENGTH_READER = "1771:377E"
# What E011-r0001 and r0002 each do at 1771:377E (T43 Evidence: experiments/E021-m0-whole-match/reach.py and
# reach_377e_branches.py, logs out/t43-reach-377e-r2.log and out/t43-reach-377e-branches.log).
EXPECTED_377E = {"calls": 88, "available": 88, "unavailable": 0, "form<0x20": 84, "form>=0x20": 4,
                 "form==0x20": 2, "clamped": 0, "wrong foot": 0}


class ThresholdMutant(_Record):
    """A falsifier: quick_engine's strength_trace with the form threshold moved to 0x21 (the real one
    is 0x20, seg_1771_05.asm:37C8)."""
    threshold = 0x21

    def strength_trace(self, w):
        trace = {"unavailable": self.unavailable_reason(w), "form_high": None, "clamped": False,
                 "wrong_foot": False, "halved_from": None, "value": 0}
        if trace["unavailable"] is not None:
            return trace
        p = self._player(w)
        v = (p[4] + s8(p[0xE]) - 0x3E) & 0xFFFF
        trace["form_high"] = s8(p[0xC]) >= self.threshold
        if trace["form_high"]:
            v = (v - idiv(s16(v), 0x10)) & 0xFFFF
        else:
            v = (v + s8(p[0xC])) & 0xFFFF
        if s16(v) < 0:
            v, trace["clamped"] = 0, True
        elif s16(v) > 0x100:
            v, trace["clamped"] = 0x100, True
        if self.wrong_foot(w):
            trace["wrong_foot"], trace["halved_from"] = True, v
            v = idiv(s16(v), 2) & 0xFFFF
        trace["value"] = v
        return trace


def strength_reader(tally=None, result_plus=0, record_class=_Record):
    """1771:377E as a hook fn (M1b): reads the routine's inputs from the guest and decides AX with
    quick_engine.QuickMatch.player_strength, unchanged. Far-called with `retf 2` (3824): the player word
    is [bp + 6] = arg(0) (3784). Reads: the far pointer DS:A91B (378C `les di, [0xa91b]`) + 0x14 * w
    (3787-3790, the offset wraps at 16 bits as `add di, ax` does) and the record's bytes (+4 37B7, +0xC
    37C8/37E0, +0xE 37AD; +5, +2, +6, +7 and +0x10 in 3216, 3041, 3088, 3179), the foot tables DS:0E60 (30C9)
    and DS:0E7C (30BA; w % 3 indexes it, 30B2-30B5): 14 * 255 + 255 bytes of the first, the three of the second.
    Result: AX = the strength (381E). DX is what the original leaves, which the proof compares:
    - unavailable by energy (+0xE < 1, 3233): 3216's `mul dx` at 3222, DX = (w * 0x14) >> 16;
    - unavailable by +0x10 element 8, 6 or 3 (3248, 325F, 3276): 214B:0C57's `mov dx, ax` at 0C61 after
      `dec ax`, DX = element - 1 of the call that returned nonzero (7, 5 or 2);
    - available: 3179 ends with 3041's `mov dx, ax` at 3064 (DX = +5; 3088's `mul dx` at 30C3 runs before it,
      and 23E4:08DF touches no DX), then the halving `cdq; idiv cx` at 380C-3813 leaves DX = the remainder of
      the value BEFORE halving (v % 2, v in 0..0x100) when the foot is wrong, and nothing else touches DX.
    The branches and the pre-halving value come from the model's own run (quick_engine.strength_trace);
    `tally` (a dict) counts them; `result_plus` adds to AX (a falsifier); `record_class` replaces the
    model's class (a falsifier)."""
    def fn(g):
        w = g.arg(0)
        base = (g.rd(0xA91B) + ((w * RECORD_SIZE) & 0xFFFF)) & 0xFFFF
        rec = g.rd(0xA91D) * 16 + base
        p = g.mem(rec, RECORD_SIZE)
        foot_table = g.mem(g.DS * 16 + 0xE60, 14 * 255 + 256)
        foot_index = g.mem(g.DS * 16 + 0xE7C, 3)
        m = record_class({w: p}, foot_table, foot_index)
        trace = m.strength_trace(w)       # the model's own execution: AX, DX and the tally come from it
        value = trace["value"]
        if trace["unavailable"] == "energy":
            dx = ((w * RECORD_SIZE) >> 16) & 0xFFFF
        elif trace["unavailable"] is not None:
            dx = trace["unavailable"] - 1
        elif trace["wrong_foot"]:
            dx = trace["halved_from"] & 1     # the remainder of the value BEFORE halving (idiv, 3813); 0..0x100
        else:
            dx = p[5]
        if tally is not None:
            keys = ["calls", "available" if trace["unavailable"] is None else "unavailable"]
            if trace["form_high"] is not None:
                keys.append("form>=0x20" if trace["form_high"] else "form<0x20")
                if p[0xC] == 0x20:
                    keys.append("form==0x20")
            if trace["clamped"]:
                keys.append("clamped")
            if trace["wrong_foot"]:
                keys.append("wrong foot")
            for k in keys:
                tally[k] = tally.get(k, 0) + 1
        g.set_reg("ax", (value + result_plus) & 0xFFFF)
        g.set_reg("dx", dx)
    return fn


CONTEST_GATE = "0791:287C"
EXPECTED_287C = {"calls": 545, "non-zero": 296, "zero": 249}   # F022 / T46 Evidence, per record


def gate_reader(tally=None, invert=False, value_plus=0):
    """0791:287C as a hook fn (M2b): contests.gate, over the inputs read from the guest. Far-called with
    `retf 6` (28AF), the same arguments as 278A (it pushes them on, 2882-2889): off (bp+6), seg (bp+8),
    element (bp+0xA) = arg(0), arg(1), arg(2). Reads: whatever 278A reads (skill_trace: the model decides
    278A's value; the original's inner call is NOT hooked while the original runs in a proof,
    watched_match.original_running), and the seed word at the far pointer DS:A978 (06D6 `les di, [0xa978]`;
    off at A978, seg at A97A), which 0688 steps and stores (069F `stosw`). Writes: the seed word, as
    `stosw` does. Results (contests.py): AL the result, AH the draw's high byte, DX the draw.
    `tally` (a dict) counts the results of the model's own run; `invert` flips AL and `value_plus` adds to
    the value 278A returns (a falsifier: 32 makes n + 1)."""
    def fn(g):
        off, seg, element = g.arg(0), g.arg(1), g.arg(2)
        value, _ = skill_trace(g, off, seg, element)
        seed_lin = g.far(0xA978)
        r = contests.gate((value + value_plus) & 0xFFFF, g.word_at(seed_lin))
        g.put(seed_lin, r.seed.to_bytes(2, "little"))
        result = r.result ^ 1 if invert else r.result
        if tally is not None:
            tally["calls"] = tally.get("calls", 0) + 1
            key = "non-zero" if r.result else "zero"
            tally[key] = tally.get(key, 0) + 1
        g.set_reg("ax", (r.ax & 0xFF00) | result)
        g.set_reg("dx", r.dx)
    return fn


DRAW_06B1, DRAW_06D0 = "214B:06B1", "214B:06D0"


def wrapper_reader(which, tally=None, falsifier=None):
    """214B:06B1 (`which` = 1) or 214B:06D0 (0) as a hook fn (M2c): draws.draw_06b1 / draw_06d0, far-called with
    `retf 2` (06CD, 06F7): n = [bp + 6] = arg(0) (06BD, 06DC). Reads the far pointer DS:A978 (offset at A978, segment
    at A97A: 06B7, 06D6) and the seed word it points to (0688's `lodsw`, 0694). Writes the new seed word as 0688's
    `stosw` does (069F). Results: AX and DX (draws.py). `tally` counts the calls and, per falsifier, the calls it
    would change (computed from the model's own run); `falsifier` selects one (06B1: n+1, value+1; 06D0: inverted,
    seed-write)."""
    model = draws.draw_06b1 if which else draws.draw_06d0

    def fn(g):
        n = g.arg(0)
        seed_lin = g.far(0xA978)
        seed = g.word_at(seed_lin)
        honest = model(seed, n)
        r = model(seed, n + 1) if falsifier == "n+1" else honest
        if tally is not None:
            def bump(key, cond=True):
                tally[key] = tally.get(key, 0) + bool(cond)
            bump("calls")
            if which:
                bump("n+1 changes the draw", model(seed, n + 1).draw != honest.draw)
                bump("value+1 changes AX")
            else:
                bump("draw is 1", honest.draw == 1)
                bump("inverted changes AL")
            bump("seed-write changes the seed", honest.seed != seed)
        if falsifier != "seed-write":
            g.put(seed_lin, r.seed.to_bytes(2, "little"))
        ax = r.ax
        if falsifier == "value+1":
            ax = (ax + 1) & 0xFFFF
        elif falsifier == "inverted":
            ax ^= 1
        g.set_reg("ax", ax)
        g.set_reg("dx", r.dx)
    return fn


LONG_MAX, LONG_MUL = "214B:0D56", "23E4:0279"


def merge_flags(g, arith):
    """The routine's last flag-setting instruction decides the six arithmetic flags; the other bits stay the guest's."""
    g.set_reg("flags", (g.reg("flags") & ~longs.ARITH) | arith)


def max_variant(honest, a, b, variant=None):
    """(AX, DX) of 214B:0D56 under a falsifier. `a` and `b` are (low, high) words; `honest` is longs.max_0d56's result.
    min: the loser instead of the winner; tie-a: `a` when the two longs are equal (the listing's `jbe` makes it b)."""
    if variant == "min":
        return b if (honest.ax, honest.dx) == a else a
    if variant == "tie-a" and a == b:
        return a
    return honest.ax, honest.dx


def long_max_reader(tally=None, falsifier=None):
    """214B:0D56 as a hook fn (M2d): longs.max_0d56. Far-called with `retf 8` (0D8D): b = [bp + 6] (low, arg(0)) and
    [bp + 8] (high, arg(1)), a = [bp + 0xA] (low, arg(2)) and [bp + 0xC] (high, arg(3)) (0D5C, 0D61, 0D68, 0D7A: the
    frame is push bp, so bp + 6 is the first word past the far return address). Reads only the stack arguments and writes
    only its dead frame. Results: AX, DX, ES (the winner's high word) and the six arithmetic flags of the last `cmp`.
    `tally` counts the calls and the branches of the model's own run; `falsifier` selects one (min, tie-a), whose reach
    (the calls it would change, computed against the honest result) is tallied as well."""
    def fn(g):
        b, a = (g.arg(0), g.arg(1)), (g.arg(2), g.arg(3))
        honest = longs.max_0d56(*a, *b)
        ax, dx = max_variant(honest, a, b, falsifier)
        if tally is not None:
            def bump(key, cond=True):
                tally[key] = tally.get(key, 0) + bool(cond)
            bump("calls")
            bump("high words differ (jg or jl taken)", a[1] != b[1])
            bump("a wins", (honest.ax, honest.dx) == a and a != b)
            bump("b wins", (honest.ax, honest.dx) == b and a != b)
            bump("ties (a == b)", a == b)
            bump("min changes the result", max_variant(honest, a, b, "min") != (honest.ax, honest.dx))
            bump("tie-a changes the result", max_variant(honest, a, b, "tie-a") != (honest.ax, honest.dx))
        g.set_reg("ax", ax)
        g.set_reg("dx", dx)
        g.set_reg("es", honest.dx)
        merge_flags(g, honest.flags)
    return fn


def long_mul_reader(tally=None, falsifier=None):
    """23E4:0279 as a hook fn (M2d): longs.mul_0279. Register convention, `retf` (0293): DX:AX times BX:CX (CX the low
    word of the second operand; 027D, 0283, 0289). Reads AX, DX, BX, CX at the entry; writes AX, DX and the scratch
    BX, CX, SI, DI the listing leaves (0285, 028B, 0279, 027B) and the arithmetic flags of the last `add` (0291); no memory
    write (its pushes are its dead frame). `tally` counts the calls and, per falsifier, the calls it would change
    (computed from the model's own run); `falsifier` selects one: product+1 (the 32-bit product plus one), no-cross-term
    (the `mul bx` term, 0283-0285, left out of DX), scratch (SI not set)."""
    def fn(g):
        ax, dx, bx, cx = g.reg("ax"), g.reg("dx"), g.reg("bx"), g.reg("cx")
        r = longs.mul_0279(ax, dx, bx, cx)
        out_ax, out_dx = r.ax, r.dx
        if falsifier == "product+1":
            out_ax, out_dx = (r.ax + 1) & 0xFFFF, (r.dx + (r.ax == 0xFFFF)) & 0xFFFF
        elif falsifier == "no-cross-term":
            out_dx = (r.dx - r.bx) & 0xFFFF
        if tally is not None:
            def bump(key, cond=True):
                tally[key] = tally.get(key, 0) + bool(cond)
            bump("calls")
            bump("DX operand (a high word) non-zero", dx)
            bump("BX operand (b high word) non-zero", bx)
            bump("mul bx term (AX * BX low word) non-zero = no-cross-term changes DX", r.bx)
            bump("mul cx term (DX * CX low word) non-zero", r.cx)
            bump("carry out of AX * CX non-zero", (ax * cx) >> 16)
            bump("product+1 changes the result")
            bump("SI differs at entry = the scratch falsifier shows", g.reg("si") != ax)
        g.set_reg("ax", out_ax)
        g.set_reg("dx", out_dx)
        g.set_reg("bx", r.bx)
        g.set_reg("cx", r.cx)
        if falsifier != "scratch":
            g.set_reg("si", r.si)
        g.set_reg("di", r.di)
        merge_flags(g, r.flags)
    return fn


HOOKS = {"none": None, "f004": f004_step(), "f004+hidden-write": hidden_write(f004_step()),
         "f004+raw-write": raw_write(f004_step()), "f004+831D-write": clock_write(f004_step()),
         "f004+inc+1-off-seed": off_seed_increment(f004_step(), f004_step(inc=INC + 1)),
         "f004-mult+1": f004_step(mult=MULT + 1),
         "f004-inc+1": f004_step(inc=INC + 1)}


M1 = {"m1-278a": {}, "m1-278a+gate-0x18": {"gate": frozenset({0x18})},
      "m1-278a+product+1": {"product_plus": 1}}
# M1b: 214B:0688, 0791:278A and 1771:377E together; the value is strength_reader's arguments
M1B = {"m1-377e": {}, "m1-377e+result+1": {"result_plus": 1},
       "m1-377e+form-0x21": {"record_class": ThresholdMutant}}
# M2b: 214B:0688, 0791:278A, 1771:377E and 0791:287C together
M2 = {"m2-287c": {}, "m2-287c+inverted": {"invert": True}, "m2-287c+n+1": {"value_plus": 32}}

# M2c: M2b's four and the draw wrappers 214B:06B1 and 214B:06D0
M2C = {"m2-draws": (None, None), "m2-draws+06b1-n+1": (DRAW_06B1, "n+1"),
       "m2-draws+06b1-value+1": (DRAW_06B1, "value+1"), "m2-draws+06d0-inverted": (DRAW_06D0, "inverted"),
       "m2-draws+06d0-seed-write": (DRAW_06D0, "seed-write")}


# M2d: M2c's six and the long helpers 214B:0D56 and 23E4:0279
M2D = {"m2-longs": (None, None), "m2-longs+0d56-min": (LONG_MAX, "min"), "m2-longs+0d56-tie-a": (LONG_MAX, "tie-a"),
       "m2-longs+0279-product+1": (LONG_MUL, "product+1"), "m2-longs+0279-no-cross-term": (LONG_MUL, "no-cross-term"),
       "m2-longs+0279-scratch": (LONG_MUL, "scratch")}
M2_ALL = dict(M2C, **M2D)                      # the hooks that substitute M2c's six routines
LONG_REACH_LOG ="t48-reach-0d56-0279.log"
M2C_COUNTS_LOG = "t47-m2-draws-run2.log"       # the six routines' counts of the M2c run (T47)


def reach_counts(rid, log="t47-reach-helpers.log", addrs=(DRAW_06B1, DRAW_06D0)):
    """The unhooked entry counts of `addrs` in record `rid` (a reach log under out/: T47's for the wrappers, T48's
    t48-reach-0d56-0279.log for the long helpers)."""
    text = (OUT / log).read_text()
    block = text.split("E011-r")[1:]
    block = next(b for b in block if b.startswith(rid[-4:]))
    return {a: int(re.search(rf"{a} entered (\d+)", block).group(1)) for a in addrs}


def logged_counts(log, rid):
    """The 'calls per routine' dict a check log under out/ printed for record `rid`."""
    for line in (OUT / log).read_text().splitlines():
        if line.startswith(f"  {rid}: calls per routine"):
            return eval(line.split("calls per routine ")[1].split(", proved")[0])
    raise SystemExit(f"no counts for {rid} in {log}")


def m2b_counts(rid):
    """M2b's hooked call counts per routine for record `rid` (out/t46-m2-287c.log)."""
    return logged_counts("t46-m2-287c.log", rid)


def common_dl():
    """The main checkout's .cache/dl (the git common dir's parent), or None when git cannot say."""
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return Path(r.stdout.strip()).parent / ".cache/dl"


def asset(entry, release="E011"):
    """A record output's bytes, by its sha256: from this worktree's cache, else the main checkout's (copied in),
    else downloaded from the release. A file enters the cache only whole: it is written under a per-process temp
    directory and renamed into place (os.replace, atomic), so two first runs cannot half-read each other."""
    name = f"{entry['sha256'][:16]}-{entry['name']}"
    path = DL / name
    if not path.is_file():
        DL.mkdir(parents=True, exist_ok=True)
        tmp = DL / f".{name}.{os.getpid()}.part"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir()
        try:
            common = common_dl()
            if common is not None and (common / name).is_file() and common.resolve() != DL.resolve():
                shutil.copyfile(common / name, tmp / name)
            else:
                cmd = ["gh", "release", "download", release, "--repo", "diegoami/goal2-archaeology",
                       "--pattern", name, "--dir", str(DL)]
                try:
                    subprocess.run(cmd[:-1] + [str(tmp)], check=True)
                    if not (tmp / name).is_file():
                        raise OSError("gh wrote no such file")
                except (subprocess.CalledProcessError, OSError) as e:
                    raise SystemExit(f"cannot download {name} ({e}); run: {' '.join(cmd)}")
            os.replace(tmp / name, path)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    data = path.read_bytes()
    if driver.sha256(data) != entry["sha256"]:
        raise SystemExit(f"{path}: sha256 does not match the record's {entry['sha256']}")
    return data


def observation(record, prefix):
    return next(o["value"] for o in record["observations"] if o.get("field", "").startswith(prefix))


def reads(record):
    """Every mid-play read of the record: [(minute, sub-tick, seed)], in read order."""
    return [tuple(p) for p in json.loads(observation(record, "ground-truth trajectory"))]


def full_time(record):
    clock = observation(record, "full time: clock").split()
    return {"seed": int(clock[4]), "score": [int(x) for x in observation(record, "full time: score bytes").split()],
            "screen_sha256": observation(record, "full time: text screen 80x25, chars+attributes")}


def draws_digest(draws):
    return hashlib.sha256("\n".join("%d %d %04x %04x" % d for d in draws).encode()).hexdigest()


def write_out(label, run_id, payload):
    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = OUT / f"{stamp}-{label}-{run_id}.json"
    with open(path, "x") as f:                       # never overwrite
        json.dump(payload, f, indent=1)
    return path


def emulate(data, hook_name, inputs=()):
    m = WatchedMatch(data)
    m.tally377e = dict.fromkeys(EXPECTED_377E, 0)
    m.tally287c = {}
    m.tally_draws = {}
    m.entries = {}      # every entry of a wrapper (or long helper), hooked or inside a proof's original
    m.tally_longs = {}
    if hook_name in M1 or hook_name in M1B or hook_name in M2 or hook_name in M2C or hook_name in M2D:     # M0's substitution, 278A's (and 377E's), each proved at every call
        m.hook(LCG_STEP, HOOKS["f004"], prove=True)
        m.hook(SKILL_READER, skill_reader(**M1.get(hook_name, {})), prove=True)
        if hook_name in M1B or hook_name in M2 or hook_name in M2C or hook_name in M2D:
            m.hook(STRENGTH_READER, strength_reader(m.tally377e, **M1B.get(hook_name, {})), prove=True)
        if hook_name in M2:
            m.hook(CONTEST_GATE, gate_reader(m.tally287c, **M2[hook_name]), prove=True)
        if hook_name in M2C or hook_name in M2D:
            m.hook(CONTEST_GATE, gate_reader(m.tally287c), prove=True)
            fal = M2C.get(hook_name, (None, None))
            for addr, which in ((DRAW_06B1, 1), (DRAW_06D0, 0)):
                m.tally_draws[addr] = {}
                m.hook(addr, wrapper_reader(which, m.tally_draws[addr], fal[1] if fal[0] == addr else None), prove=True)
            entry_counted = [DRAW_06B1, DRAW_06D0]
            if hook_name in M2D:
                lf = M2D[hook_name]
                for addr, reader in ((LONG_MAX, long_max_reader), (LONG_MUL, long_mul_reader)):
                    m.tally_longs[addr] = {}
                    m.hook(addr, reader(m.tally_longs[addr], lf[1] if lf[0] == addr else None), prove=True)
                entry_counted += [LONG_MAX, LONG_MUL]
            for addr in entry_counted:    # entries made inside an original that runs in a proof
                m.entries[addr] = 0
                m.mu.hook_add(UC_HOOK_CODE, lambda uc, a, sz, d, addr=addr: m.entries.__setitem__(addr, m.entries[addr] + 1),
                              begin=m.lin(addr), end=m.lin(addr))
    elif HOOKS[hook_name] is not None:
        m.hook(LCG_STEP, HOOKS[hook_name], prove=True)
    for fn in inputs:
        fn(m)
    error = None
    t = time.time()
    try:
        m.run(timeout_s=RUN_TIMEOUT_S)
    except Exception as e:  # a void run: everything after it counts as missed
        error = f"{type(e).__name__}: {e}"
        m.final = m.state()
    return m, error, round(time.time() - t, 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs/E011"))
    ap.add_argument("--hook", choices=sorted(HOOKS) + sorted(M1) + sorted(M1B) + sorted(M2) + sorted(M2C) + sorted(M2D), default="none")
    a = ap.parse_args(argv)
    records = sorted(Path(a.runs).glob("E011-r*.json"))
    for p in records:       # every asset first: a failed download stops here, before any measured output
        asset(next(o for o in json.loads(p.read_text())["outputs"] if o["name"].endswith("-watchstart.sav")))
    n = ok = 0
    failed = []
    hooked = proved = reader_hooked = reader_proved = 0
    strength_hooked = strength_proved = contest_hooked = contest_proved = 0
    scratch = {}
    long_calls = {}         # M2d: address -> [hooked, proved], summed over the records
    long_scratch = {}       # M2d: address -> {register: proved calls where it differed}, summed over the records
    differences = []
    for p in records:
        record = json.loads(p.read_text())
        rid = record["run_id"]
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        data = asset(entry)
        m, error, secs = emulate(data, a.hook)
        trace = None
        if a.hook != "none":   # a substitution is right only if every seed write is the original's
            ref, ref_error, _ = emulate(data, "none")
            trace = "unhooked run void: " + ref_error if ref_error else trace_difference(ref.draws, m.draws)
        sets = m.tick_values()
        cps = reads(record)
        hit = sum(1 for mi, d, s in cps if s in sets.get((mi, d), ()))
        n += len(cps)
        ok += hit
        hooked += m.hook_counts.get(LCG_STEP, 0)
        proved += m.proved_calls.get(LCG_STEP, 0)
        per_record = m.hook_counts.get(SKILL_READER, 0)
        reader_hooked += per_record
        reader_proved += m.proved_calls.get(SKILL_READER, 0)
        if a.hook in M1B or a.hook in M2 or a.hook in M2_ALL:
            per377 = m.hook_counts.get(STRENGTH_READER, 0)
            strength_hooked += per377
            strength_proved += m.proved_calls.get(STRENGTH_READER, 0)
            print(f"  {rid}: {STRENGTH_READER} calls {per377}, proved {m.proved_calls.get(STRENGTH_READER, 0)};"
                  f" branches {m.tally377e}")
        if a.hook in M2 or a.hook in M2_ALL:
            print(f"  {rid}: calls per routine {m.hook_counts}, proved {m.proved_calls};"
                  f" {CONTEST_GATE} results {m.tally287c}")
        if a.hook in M1 or a.hook in M1B or a.hook in M2 or a.hook in M2_ALL:
            print(f"  {rid}: {SKILL_READER} calls {per_record}, proved {m.proved_calls.get(SKILL_READER, 0)}")
        for r, c in m.scratch_differences.get(LCG_STEP, {}).items():
            scratch[r] = scratch.get(r, 0) + c
        ft = full_time(record)
        out = m.outputs() if m.stopped_at_board else {"final": m.final, "key_log": m.key_log, "strays": m.strays,
                                                      "hook_counts": m.hook_counts, "inputs": m.inputs}
        screen_sha = out.get("board_screen_sha256")
        checks = {
            "full-time score equals the record's": m.final["score"] == ft["score"],
            "the 000E skip log is empty": not m.strays,
            "keys: the three declared screens, Enter each": [k[0].split(" (")[0] for k in m.key_log]
            == ["captain screen", "half-time board", "team screen"],
            "stopped at the full-time board's key wait": m.stopped_at_board,
            "seed at the board equals the record's full-time read": m.final["7B62"] == ft["seed"],
            "board screen sha256 equals the record's full-time screen": screen_sha == ft["screen_sha256"],
            "every seed write equals the unhooked original's (hooked runs)": trace is None,
        }
        contest_hooked += m.hook_counts.get(CONTEST_GATE, 0)
        contest_proved += m.proved_calls.get(CONTEST_GATE, 0)
        if a.hook == "m2-287c":
            checks["287C's calls and results equal the Evidence's (545: 296 non-zero / 249 zero)"] = (
                m.tally287c == EXPECTED_287C and m.hook_counts.get(CONTEST_GATE) == 545
                and m.proved_calls.get(CONTEST_GATE) == 545)
        if a.hook in M2D:
            reach = reach_counts(rid, LONG_REACH_LOG, (LONG_MAX, LONG_MUL))
            base = logged_counts(M2C_COUNTS_LOG, rid)
            nested = {x: m.entries[x] - m.hook_counts[x] for x in (LONG_MAX, LONG_MUL)}   # entries no hook took
            print(f"  {rid}: long-helper tallies {m.tally_longs}")
            print(f"  {rid}: scratch_differences (proved calls where an uncompared register differed, per routine):"
                  f" {m.scratch_differences}")
            for x in (LONG_MAX, LONG_MUL):
                long_calls[x] = [long_calls.get(x, [0, 0])[0] + m.hook_counts[x], long_calls.get(x, [0, 0])[1] + m.proved_calls[x]]
                long_scratch[x] ={r: long_scratch.get(x, {}).get(r, 0) + c for r, c in m.scratch_differences[x].items()}
            if not error:
                expected = {**base, LONG_MAX: reach[LONG_MAX] - nested[LONG_MAX], LONG_MUL: reach[LONG_MUL] - nested[LONG_MUL]}
                print(f"  {rid}: entries of 0D56/0279 inside the originals of the other routines (not hooked, counted by a"
                      f" code hook minus the hooked calls): {nested}; reach (unhooked, {LONG_REACH_LOG}) {reach};"
                      f" M2c counts ({M2C_COUNTS_LOG}) {base}")
                print(f"  {rid}: expected counts = M2c's six unchanged, 0D56/0279 = reach - nested: {expected}; got {m.hook_counts}")
                checks["the eight counts equal M2c's six and the adjusted reach for 0D56/0279, all proved"] = (
                    m.hook_counts == expected and m.proved_calls == m.hook_counts)
        if a.hook in M2C and not error:
            reach, base = reach_counts(rid), m2b_counts(rid)
            nested = {a: m.entries[a] - m.hook_counts[a] for a in (DRAW_06B1, DRAW_06D0)}   # entries no hook took
            wrappers = m.hook_counts[DRAW_06B1] + m.hook_counts[DRAW_06D0]
            expected = {DRAW_06B1: reach[DRAW_06B1] - nested[DRAW_06B1], DRAW_06D0: reach[DRAW_06D0] - nested[DRAW_06D0],
                        LCG_STEP: base[LCG_STEP] - wrappers, SKILL_READER: base[SKILL_READER],
                        STRENGTH_READER: base[STRENGTH_READER], CONTEST_GATE: base[CONTEST_GATE]}
            print(f"  {rid}: wrapper entries inside the originals of 278A/377E/287C (not hooked, computed):"
                  f" {nested}; reach (unhooked) {reach}; M2b counts {base}")
            print(f"  {rid}: expected counts = reach - nested for the wrappers, M2b - wrapper calls for 0688:"
                  f" {expected}; got {m.hook_counts}")
            print(f"  {rid}: wrapper tallies {m.tally_draws}")
            checks["the six counts equal the adjusted reach / M2b counts, all proved"] = (
                m.hook_counts == expected and m.proved_calls == m.hook_counts)
        if a.hook == "m1-377e":
            checks["377E's calls and branch tally equal the measured original's (T43 Evidence)"] = (
                m.tally377e == EXPECTED_377E and m.hook_counts.get(STRENGTH_READER) == 88)
        print(f"{rid}: start {entry['name']} (captain screen, seed 0x{m.start_state['7B62']:04x});"
              f" emulated {m.final['ticks']} clock ticks, {len(m.draws)} seed writes, {secs} s;"
              f" full time: minute {m.final['831F']} sub-tick {m.final['831D']}, seed 0x{m.final['7B62']:04x},"
              f" score {m.final['score']} (record {ft['score']}, seed 0x{ft['seed']:04x});"
              f" 000E strays: {m.strays or 'none'}; hook {a.hook}: {m.hook_counts or 'none'}", flush=True)
        if error:
            print(f"  VOID: {error}")
            failed.append(f"{rid}: {error}")
            if error.startswith("ProofError"):
                differences.append(f"{rid}: {error}")
        for name, good in checks.items():
            if not good:
                print(f"  FAIL: {name}" + (f": first difference {trace}" if name.startswith("every seed write") else ""))
                failed.append(f"{rid}: {name}")
        for mi, d, s in cps:
            if s not in sets.get((mi, d), ()):
                print(f"  MISS: read at minute {mi} sub-tick {d} seed 0x{s:04x} is not on the emulated"
                      f" trajectory ({len(sets.get((mi, d), ()))} values under that clock reading)")
        print(f"  {rid}: reads {hit}/{len(cps)}")
        out.update({"run_id": rid, "hook": a.hook, "start_state": {"name": entry["name"], "sha256": entry["sha256"]},
                    "reads_matched": hit, "reads": len(cps), "checks": checks, "error": error, "seconds": secs,
                    "draws_count": len(m.draws), "draws_sha256": draws_digest(m.draws)})
        out.pop("draws", None)
        print(f"  outputs: {write_out(a.hook, rid, out).relative_to(ROOT)}")
    if a.hook != "none":
        print(f"hooked calls of {LCG_STEP}: {hooked}; proved side by side with no difference: {proved};"
              f" differences: {len(differences)}" + (f" (first: {differences[0]})" if differences else ""))
        if a.hook in M2 or a.hook in M2_ALL:
            print(f"hooked calls of {CONTEST_GATE}: {contest_hooked}; proved side by side with no difference:"
                  f" {contest_proved}")
        if a.hook in M1 or a.hook in M1B or a.hook in M2 or a.hook in M2_ALL:
            print(f"hooked calls of {SKILL_READER}: {reader_hooked}; proved side by side with no difference:"
                  f" {reader_proved}")
        if a.hook in M1B or a.hook in M2 or a.hook in M2_ALL:
            print(f"hooked calls of {STRENGTH_READER}: {strength_hooked}; proved side by side with no difference:"
                  f" {strength_proved}")
        print("uncompared-register differences (warnings, proved calls): "
              + ", ".join(f"{r} {c}" for r, c in scratch.items()))
        if a.hook in M2D:
            for x in (LONG_MAX, LONG_MUL):
                print(f"hooked calls of {x}: {long_calls[x][0]}; proved side by side with no difference: {long_calls[x][1]};"
                      f" scratch_differences (BX, CX, SI, DI, ES, FLAGS; summed over the records): {long_scratch.get(x)}")
    else:
        print("hooked calls: none (no hook)")
    print(f"match: {ok}/{n}")
    if n == 0:
        print("no reads: an empty set fails")
        return 1
    return 0 if ok == n and not failed else 1


if __name__ == "__main__":
    sys.exit(main())
