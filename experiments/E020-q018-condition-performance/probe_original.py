#!/usr/bin/env python3
"""Run the ORIGINAL 1771:377E and 0791:278A on literal player records (Unicorn, E010's half-time
image as the code and data), and write what the original returned as immutable records.

    python3 experiments/E020-q018-condition-performance/probe_original.py strength records/strength-001.json
    python3 experiments/E020-q018-condition-performance/probe_original.py contest  records/contest-001.json

No guest code is changed; the only interventions are the literal player (and, for 278A, pitch)
records written into the guest's own arrays before the call, and a sentinel return address.
`strength` records 1771:377E(player word) -> AX for every combination of the listed +0xC, +0xE
(and +0x10 availability, position and foot) values; `contest` records 0791:278A(pitch, element)
-> AX, with the tables 3A06 reads (DS:6D25, DS:6DCD), the 2826 gate (DS:0769), the foot tables of
377E (DS:0E60, DS:0E7C) and the flags it reads (DS:80FC, DS:8327) copied into the record.
Output files are exclusive-create: a measurement is never overwritten (L40)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import ROOT, STATE_SHA256  # noqa: E402
sys.path.insert(0, str(ROOT / "runtime/emul"))
from watched import WatchedHalf  # noqa: E402
from unicorn.x86_const import UC_X86_REG_SP, UC_X86_REG_SS, UC_X86_REG_CS  # noqa: E402

SENTINEL = 0x98C0       # 0791:98C0, the half's ret: never executed, only the stop address


class Harness:
    def __init__(self):
        self.data = common.load_state()
        self.half = WatchedHalf(self.data)
        self.mu = self.half.mu
        self.load = self.half.CODE - 0x791
        self.pbase = common.player_base(__import__("savestate").Savestate(self.data))

    def ds_read(self, off, n):
        return bytes(self.mu.mem_read(self.half.DS * 16 + off, n))

    def ds_write(self, off, b):
        self.mu.mem_write(self.half.DS * 16 + off, bytes(b))

    def call(self, seg_rel, off, args):
        """Far-call routine seg_rel:off with the word `args` (lowest address first), return AX."""
        mu = self.mu
        sp = mu.reg_read(UC_X86_REG_SP)
        stack = mu.reg_read(UC_X86_REG_SS) * 16 + sp
        words = [SENTINEL, self.half.CODE] + list(args)
        mu.mem_write(stack, b"".join(w.to_bytes(2, "little") for w in words))
        mu.reg_write(UC_X86_REG_CS, self.load + seg_rel)
        mu.emu_start((self.load + seg_rel) * 16 + off, self.half.CODE * 16 + SENTINEL, timeout=10000000)
        from unicorn.x86_const import UC_X86_REG_AX, UC_X86_REG_IP
        if (mu.reg_read(UC_X86_REG_CS), mu.reg_read(UC_X86_REG_IP)) != (self.half.CODE, SENTINEL):
            raise RuntimeError("the routine did not return to the sentinel")
        return mu.reg_read(UC_X86_REG_AX)

    def put_player(self, word, record):
        self.mu.mem_write(self.pbase + 20 * word, bytes(record))


def strength_cases():
    """(+4, +5, +6, +7, +2, +10 status, +C, +E): a record per combination, all other bytes zero."""
    cases = []
    energies = [0, 1, 2, 0x1F, 0x20, 0x3E, 0x7F, 0x80, 0xFF]
    forms = [0, 1, 0x1F, 0x20, 0x21, 0x3F, 0x7F, 0x80, 0xFF]
    for skill in (0x4A, 0xE1):
        for e in energies:
            for c in forms:
                cases.append((skill, 8, 0, 0, 0, 0, c, e))      # a keeper-position record
    # wrong-foot arms of 3179 (record +6 position, +7 foot, +5, +2) at one condition
    for pos, foot7, b5, b2 in ((3, 0, 8, 0), (3, 1, 8, 0), (7, 1, 0x0F, 0x0F), (4, 0, 8, 0),
                               (10, 1, 8, 0), (0, 1, 8, 0), (2, 0, 8, 0)):
        cases.append((0xB4, b5, pos, foot7, b2, 0, 0x10, 0x18))
    # unavailable: +0x10 elements 8, 6, 3 (3216)
    for status in (0x08, 0x40, 0x04):
        cases.append((0xB4, 8, 2, 0, 0, status, 0x10, 0x18))
    return cases


def probe_strength(h):
    words = []
    out_cases = []
    foot_table = h.ds_read(0xE60, 0xE0)
    foot_index = h.ds_read(0xE7C, 3)
    base_word = 3000
    for i, (skill, b5, pos, b7, b2, status, c, e) in enumerate(strength_cases()):
        word = base_word + i
        rec = bytearray(20)
        rec[2], rec[4], rec[5], rec[6], rec[7] = b2, skill, b5, pos, b7
        rec[0x10], rec[0xC], rec[0xE] = status, c, e
        h.put_player(word, rec)
        ax = h.call(0x1771, 0x377E, [word])
        out_cases.append({"player_word": word, "record": bytes(rec).hex(), "strength": ax})
    return {"schema": "E020-strength/1", "method": "Unicorn original 1771:377E on literal records",
            "source_sha256": STATE_SHA256, "source_release": "E010",
            "foot_table_DS_0E60": foot_table.hex(), "foot_index_DS_0E7C": foot_index.hex(),
            "comparisons": out_cases}


def event_cases():
    """The keeper-extra gate: element 1 under DS:8327 in {0, 2, 3, 4, 5, 0x18} (members 3 and 4:
    probe_event_gate.py), at two conditions."""
    return [dict(element=1, c=c, e=e, halve=0, extra=5, slot=1, flag_80fc=0, event=ev)
            for ev in (0, 2, 3, 4, 5, 0x18) for c, e in ((0x10, 0x18), (0, 1))]


def probe_fitness_strength(h):
    """377E with fitness +0xD varied at fixed skills, form and energy: nothing may change."""
    out = []
    word = 2900
    for d in (0, 1, 0x10, 0x20, 0x7F, 0x80, 0xFF):
        for c, e in ((0x10, 0x18), (0, 1), (0x20, 0x7F)):
            word += 1
            rec = bytearray(20)
            rec[4], rec[5], rec[6], rec[7] = 0xB4, 8, 3, 0
            rec[0xC], rec[0xD], rec[0xE] = c, d, e
            h.put_player(word, rec)
            out.append({"player_word": word, "record": bytes(rec).hex(), "strength": h.call(0x1771, 0x377E, [word])})
    return {"schema": "E020-strength/1", "method": "Unicorn original 1771:377E, fitness +0xD varied",
            "source_sha256": STATE_SHA256, "source_release": "E010",
            "foot_table_DS_0E60": h.ds_read(0xE60, 0xE0).hex(), "foot_index_DS_0E7C": h.ds_read(0xE7C, 3).hex(),
            "comparisons": out}


def probe_fitness_contest(h):
    """278A with fitness +0xD varied (elements 3, 10, 12): nothing may change."""
    cases = []
    for element in (3, 10, 12):
        for d in (0, 1, 0x10, 0x20, 0x7F, 0x80, 0xFF):
            for c, e in ((0x10, 0x18), (0, 1)):
                cases.append(dict(element=element, c=c, e=e, halve=0, extra=0, slot=1, flag_80fc=0,
                                  event=0, d=d))
    return probe_contest(h, cases, base_word=2950)


def probe_structure(h):
    """377E over what the strength grid leaves out: every position 0..13 x foot byte +7 in {0, 1} x
    two-footed or not x the three residues of word mod 3 (3179/3088 read them), every single bit of
    +0x10 (3216), other bytes (+0xF, +0x11) set with +0x10 clear, and the clamp boundaries
    (strength exactly 0xFF/0x100/0x101 before the clamp, exactly 0/-1/+1 below it)."""
    out = []
    word = 2200

    def add(rec):
        nonlocal word
        word += 1
        h.put_player(word, rec)
        out.append({"player_word": word, "record": bytes(rec).hex(),
                    "strength": h.call(0x1771, 0x377E, [word])})

    def rec(skill=0xB4, b5=8, pos=3, b7=0, b2=0, status=0, c=0x10, e=0x18, b0f=0, b11=0):
        r = bytearray(20)
        r[2], r[4], r[5], r[6], r[7] = b2, skill, b5, pos, b7
        r[0xC], r[0xE], r[0x10], r[0xF], r[0x11] = c, e, status, b0f, b11
        return r

    for pos in range(14):
        for b7 in (0, 1):
            for two in (False, True):
                for residue in range(3):
                    while word % 3 != (residue - 1) % 3:
                        word += 1
                    add(rec(pos=pos, b7=b7, b5=0x0F if two else 8, b2=0x0F if two else 0))
    for bit in range(8):
        add(rec(status=1 << bit))
    add(rec(b0f=0xFF, b11=0xFF))
    # clamp boundaries: skill 0xE1 (225), form 0: v = 225 + E - 62 -> E = 92, 93, 94 give 255, 256, 257
    for e in (92, 93, 94):
        add(rec(skill=0xE1, pos=0, e=e, c=0))
    # below: skill 74, E = 1 (v = 13), form -13, -14, -12 (0xF3, 0xF2, 0xF4) give 0, -1, 1
    for c in (0xF3, 0xF2, 0xF4):
        add(rec(skill=74, pos=0, e=1, c=c))
    return {"schema": "E020-strength/1", "method": "Unicorn original 1771:377E, structure of 3179/3216/clamp",
            "source_sha256": STATE_SHA256, "source_release": "E010",
            "foot_table_DS_0E60": h.ds_read(0xE60, 0xE0).hex(), "foot_index_DS_0E7C": h.ds_read(0xE7C, 3).hex(),
            "comparisons": out}


def probe_contest(h, cases=None, base_word=None):
    """0791:278A(pitch, element) for edge conditions; pitch record at slot 1 of DS:80E8."""
    class_table = h.ds_read(0x6D25, 14 * 12)
    profile_table = h.ds_read(0x6DCD, 16 * 12)
    keeper_gate = h.ds_read(0x769, 13)
    word = base_word if base_word else (2800 if cases else 3100)
    cases = [] if cases is None else cases
    energies = [0, 1, 0x10, 0x20, 0x7F, 0x80, 0xFE] if not cases else []
    forms = [0, 1, 0x1F, 0x20, 0x3F, 0x80, 0xFF]
    n = 0
    for element in ((3, 10, 12) if not cases else ()):
        for e in energies:
            for c in forms:
                cases.append(dict(element=element, c=c, e=e, halve=0, extra=0, slot=1, flag_80fc=0,
                                  event=0))
    for element, halve, extra, slot, f80, event in (() if cases else (
            (1, 1, 5, 1, 0, 0x18), (1, 0, 5, 1, 0, 0x18),
            (1, 0, 5, 1, 0, 0), (2, 0, 7, 1, 0, 0),
            (4, 0, 7, 1, 0, 0), (10, 0, 7, 1, 1, 0),
            (10, 0, 7, 12, 1, 0), (10, 1, 7, 5, 1, 0))):
        cases.append(dict(element=element, c=0x10, e=0x18, halve=halve, extra=extra, slot=slot,
                          flag_80fc=f80, event=event))
    results = []
    pitch_off = 0x80E8 + 0x16 * 1
    for case in cases:
        word += 1
        rec = bytearray(20)
        rec[4], rec[5], rec[7] = 0xB4, 8, 2
        rec[0xC], rec[0xE] = case["c"], case["e"]
        rec[0xD] = case.get("d", 0)
        h.put_player(word, rec)
        pitch = bytearray(h.ds_read(pitch_off, 0x16))
        pitch[6] = case["slot"]
        pitch[0xD:0xF] = word.to_bytes(2, "little")
        pitch[0x11], pitch[0x13] = case["extra"], case["halve"]
        h.ds_write(pitch_off, pitch)
        h.ds_write(0x80FC, bytes([case["flag_80fc"]]))
        h.ds_write(0x8327, bytes([case["event"]]))
        ax = h.call(0x791, 0x278A, [pitch_off, h.half.DS, case["element"]])
        results.append({"player_word": word, "record": bytes(rec).hex(), "element": case["element"],
                        "pitch_6": case["slot"], "pitch_11": case["extra"], "pitch_13": case["halve"],
                        "flag_80fc": case["flag_80fc"], "event_code_8327": case["event"],
                        "contest": ax})
    return {"schema": "E020-contest/1", "method": "Unicorn original 0791:278A on literal records",
            "source_sha256": STATE_SHA256, "source_release": "E010",
            "class_table_DS_6D25": class_table.hex(), "profile_table_DS_6DCD": profile_table.hex(),
            "keeper_gate_DS_0769": keeper_gate.hex(), "comparisons": results}


def main():
    kind, out = sys.argv[1], HERE / sys.argv[2]
    h = Harness()
    record = {"strength": probe_strength, "contest": probe_contest,
              "events": lambda hh: probe_contest(hh, event_cases()),
              "fitness-strength": probe_fitness_strength, "structure": probe_structure,
              "fitness-contest": probe_fitness_contest}[kind](h)
    out.parent.mkdir(exist_ok=True)
    with out.open("x") as f:
        json.dump(record, f, indent=1)
        f.write("\n")
    print(f"{kind}: {len(record['comparisons'])} comparisons -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
