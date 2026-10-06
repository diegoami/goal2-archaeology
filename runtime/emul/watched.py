#!/usr/bin/env python3
"""Unicorn emulation of a watched match half, generalised from T24's
`experiments/E010-q010-quick-engine/emu_full_loop.py` (E010's notes hold the mechanics this
reuses: the savestate Memory component's 0x78-byte header, 16-bit linear addresses in
`emu_start`, the BIOS key thunk `214B:0723 -> 235C:000B` skipped with AL=0).

`WatchedHalf(savestate_bytes).run()` emulates the ORIGINAL binary's second half from a
half-time team-screen stall savestate (the state at the `0791:9A32` tail's `0791:ED8A` wait,
E011 notes.md §5): it applies the tail's two writes (`DS:830B`, `DS:832A = 0x50`), then runs
`0791:983F` — the whole half: its head (8062, 2A15, the watched-only 2929 and 8CCA), the tick
loop `0791:97D0` with the watched engine `0791:9564`, `8CF5` and `9119` per tick, the clock
`970C`, and the post-loop cleanups — as real guest code, stopping at `0791:98C0` (the `ret`).
Interventions, and nothing else:
- interrupts swallowed (the BIOS/DOS calls the binary makes are display and speaker);
- `214B:0723` (keypressed) returns "no key" — E004's discipline sends no key during play, and
  the half-time wait is before the entry point;
- the `000E` wait family (05F6/0572/04F5/045D, the crowd animation, an RNG consumer) is
  skipped and LOGGED: its callers are 000E menu code only (calls.tsv), unreachable from the
  match, so the log must stay empty — a non-empty log means the skip is wrong and the run is
  void (E010's notes, "the RNG-consumer closure missed").
Every draw of the MAIN seed (`214B:0688` on `DS:7B62`) is recorded with the match clock:
`draws` is the ordered list of `(minute DS:831F, value before, value after)`. The seed word's
value between two draws is the earlier draw's "after", so the set of values the word takes
during a minute is {the value entering it} ∪ {each "after" in it} — the trajectory
`emu_check.py` checks the ground-truth reads against (E011 notes.md §6). The second stream
(`DS:8336`, the speaker) is recorded separately and does not feed the main seed.

Requirements: python3-unicorn; the half-time savestate (E011's release asset, or scratch)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import savestate  # noqa: E402
from unicorn import Uc, UC_ARCH_X86, UC_MODE_16, UC_HOOK_INTR, UC_HOOK_CODE  # noqa: E402
from unicorn.x86_const import *  # noqa: E402

SS, SP0 = 0x7000, 0x6FF4
# 0791 offsets (the tick map, E011 notes.md §1/§2/§5)
HALF_ENTRY, HALF_END = 0x983F, 0x98C0
KEYTHUNK = 0x723                       # 214B:0723, the BIOS keypressed thunk
WAIT_FAMILY = ((0x5F6, 6), (0x572, 2), (0x4F5, 4), (0x45D, 4))  # 000E, (offset, ret nbytes)
LCG = 0x688                            # 214B:0688, the RNG step


class WatchedHalf:
    def __init__(self, data):
        st = savestate.Savestate(data)
        load = st.program().ds_base // 16 - 0x2581
        self.CODE, self.DS = load + 0x791, load + 0x2581
        self.SEG214B, self.SEG000E = load + 0x214B, load + 0x00E
        self.seed_lin = self.DS * 16 + 0x7B62
        self.mu = Uc(UC_ARCH_X86, UC_MODE_16)
        self.mu.mem_map(0, 0x110000)
        self.mu.mem_write(0, bytes(st.mem[0x78:0x78 + 0x110000]))
        self.mu.reg_write(UC_X86_REG_SS, SS)
        self.mu.reg_write(UC_X86_REG_SP, SP0)
        self.mu.reg_write(UC_X86_REG_DS, self.DS)
        self.mu.reg_write(UC_X86_REG_ES, self.DS)
        self.mu.reg_write(UC_X86_REG_CS, self.CODE)
        self.draws = []       # (minute, before, after) per main-seed 0688 call
        self.speaker = []     # the second stream's values, for the record
        self.strays = []      # 000E wait-family skips: must stay empty
        self.ticks = 0
        self._hook()

    def rd(self, off, n=2):
        return int.from_bytes(self.mu.mem_read(self.DS * 16 + off, n), "little")

    def wr(self, off, v):
        self.mu.mem_write(self.DS * 16 + off, v.to_bytes(2, "little"))

    def _hook(self):
        mu = self.mu

        def skip_keychk(uc, addr, size, data):
            sp = uc.reg_read(UC_X86_REG_SP)
            ss = uc.reg_read(UC_X86_REG_SS) * 16
            rip = int.from_bytes(uc.mem_read(ss + sp, 2), "little")
            rcs = int.from_bytes(uc.mem_read(ss + sp + 2, 2), "little")
            uc.reg_write(UC_X86_REG_SP, sp + 4)
            uc.reg_write(UC_X86_REG_AX, uc.reg_read(UC_X86_REG_AX) & 0xFF00)
            uc.reg_write(UC_X86_REG_CS, rcs)
            uc.reg_write(UC_X86_REG_EIP, rip)   # 16-bit mode: EIP is the OFFSET in CS

        def skip_ret(nbytes):
            def hook(uc, addr, size, data):
                sp = uc.reg_read(UC_X86_REG_SP)
                ss = uc.reg_read(UC_X86_REG_SS) * 16
                rip = int.from_bytes(uc.mem_read(ss + sp, 2), "little")
                rcs = int.from_bytes(uc.mem_read(ss + sp + 2, 2), "little")
                self.strays.append("000E:%04X" % (addr - self.SEG000E * 16))
                uc.reg_write(UC_X86_REG_SP, sp + 2 + nbytes)
                uc.reg_write(UC_X86_REG_CS, rcs)
                uc.reg_write(UC_X86_REG_EIP, rip)
            return hook

        def rng(uc, addr, size, data):
            """214B:0688 entry: stack (far-called, retf 6) holds n at +4, seed far ptr at +6/+8.
            Only calls on DS:7B62 (the main seed) are recorded; the step is the LCG itself."""
            sp = uc.reg_read(UC_X86_REG_SP)
            ss = uc.reg_read(UC_X86_REG_SS) * 16
            off = int.from_bytes(uc.mem_read(ss + sp + 6, 2), "little")
            seg = int.from_bytes(uc.mem_read(ss + sp + 8, 2), "little")
            lin = seg * 16 + off
            before = int.from_bytes(uc.mem_read(lin, 2), "little")
            after = (before * 0x7ABD + 0x1B0F) & 0xFFFF
            if lin == self.seed_lin:
                self.draws.append((self.rd(0x831F), before, after))
            else:
                self.speaker.append(after)

        def tick(uc, addr, size, data):
            self.ticks += 1

        mu.hook_add(UC_HOOK_INTR, lambda uc, i, d: None)
        mu.hook_add(UC_HOOK_CODE, skip_keychk, begin=self.SEG214B * 16 + KEYTHUNK, end=self.SEG214B * 16 + KEYTHUNK)
        for off, nb in WAIT_FAMILY:
            mu.hook_add(UC_HOOK_CODE, skip_ret(nb), begin=self.SEG000E * 16 + off, end=self.SEG000E * 16 + off)
        mu.hook_add(UC_HOOK_CODE, rng, begin=self.SEG214B * 16 + LCG, end=self.SEG214B * 16 + LCG)
        mu.hook_add(UC_HOOK_CODE, tick, begin=self.CODE * 16 + 0x970C, end=self.CODE * 16 + 0x970C)

    def run(self, timeout_s=1800):
        """Emulate the half. Returns self (see the class docstring for the fields)."""
        # 0791:9A32's tail after the ED8A wait (seg_0791_16.asm:9AEE-9B05): the kick-off slot
        # and the restart countdown, exactly as the real game sets them before 983F.
        side = 0 if self.rd(0x831A, 1) == 0 else 1
        self.wr(0x830B, (0 if side == 0 else 11) + 10)
        self.wr(0x832A, 0x50)
        self.start_state = {"831F": self.rd(0x831F), "831B": self.rd(0x831B), "8325": self.rd(0x8325, 1),
                            "7B62": self.rd(0x7B62), "830B": self.rd(0x830B, 1), "832A": self.rd(0x832A)}
        self.mu.emu_start(self.CODE * 16 + HALF_ENTRY, self.CODE * 16 + HALF_END, timeout=timeout_s * 1000000)
        self.final = {"831F": self.rd(0x831F), "831B": self.rd(0x831B), "8325": self.rd(0x8325, 1),
                      "7B62": self.rd(0x7B62), "score": [self.rd(0x9B3C, 1), self.rd(0x9B3D, 1)],
                      "ticks": self.ticks, "draws": len(self.draws), "strays": list(self.strays)}
        return self

    def minute_values(self):
        """minute -> the set of values DS:7B62 takes during that minute (notes.md §6)."""
        sets = {}
        value = self.start_state["7B62"]
        for minute, before, after in self.draws:
            assert before == value, f"the seed moved outside 0688: {before:04x} then {value:04x}"
            sets.setdefault(minute, set()).add(value)
            sets[minute].add(after)
            value = after
        return sets
