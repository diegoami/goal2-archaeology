"""runtime/original_match/port/attributes.py (T61): the player attributes of segment 1771, ported.

- SimTests (no emulator, no image): each port run on plain memory by a small simulator (the Sim below pushes the
  arguments as the listing does, runs the port, resolves its guest calls: a routine of the module runs as its port, a
  helper of 214B or 23E4 is a model written from the listing). Every expected value is written in the test from the
  listing or taken from the literal values tests/test_model_condition.py holds (the original's own answers for 377E);
  none comes from the port. They cover the branches ALL does not reach: the foot test's rows, an unavailable player
  by each of its reasons, each element of a player's own tactics, the clamps of the strength, and the marking.
- VariantTests: each variant (a falsifier of the task's Done-when) changes an answer the unvaried port gives.
- DifferentialTests (unicorn and the reference image in .cache/dl, else skipped): every routine run against the
  original's, on random states, the registers and the whole of guest memory compared (the dead stack frames included),
  by experiments/E036-match-port/out/T61/diffcheck.py; and a mutation the harness must see."""
import importlib.util
import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT))
from original_match import port  # noqa: E402
from original_match.port import attributes  # noqa: E402
from original_match.port.mem import PlainMem, s8  # noqa: E402
from tests import test_model_condition as literal  # noqa: E402

REG = attributes.PORTS
DIFFCHECK = ROOT / "experiments/E036-match-port/out/T61/diffcheck.py"


# ---- the simulator ------------------------------------------------------------------------------------------------
class Sim:
    """The ports on plain memory. The arrays: players at 4000:0, countries at 5000:0, managers at 5800:0; SS 6000."""
    PLAYERS_SEG, COUNTRIES_SEG, MANAGERS_SEG, SS = 0x4000, 0x5000, 0x5800, 0x6000

    def __init__(self, variant=None):
        self.mem = mem = PlainMem(bytearray(0x110000), load=0)
        self.ds, self.variant, self.guest_calls = mem.DS * 16, variant, []
        for off, seg in ((0xA91B, self.PLAYERS_SEG), (0xA917, self.COUNTRIES_SEG), (0xA91F, self.MANAGERS_SEG)):
            mem.memory[self.ds + off:self.ds + off + 4] = (0).to_bytes(2, "little") + seg.to_bytes(2, "little")
        mem.regs.update(ss=self.SS, sp=0x3F00, bp=0x1234, ax=0, dx=0, cs=mem.seg(0x1771), ds=mem.DS)
        cs = mem.seg(0x1771) * 16     # the sets 23E4:08DF reads in the code segment, and the two strings (listing data rows)
        for off, row in ((0x3139, b"\x88\x04"), (0x3159, b"\x10\x09"), (0x3411, b"\x1b\x00"), (0x0E6A, b"\x01-"),
                         (0x2E91, b"\x01 ")):
            mem.memory[cs + off:cs + off + len(row)] = row
        self.ds_bytes(0xE60, literal.FOOT_TABLE[:0xE0])      # the original's DS:0E60 and DS:0E7C (T36's literals)
        self.ds_bytes(0xE7C, literal.FOOT_INDEX)
        self.ds_bytes(0x6D25, literal.CLASS_TABLE)
        self.ds_bytes(0x6DCD, literal.PROFILE_TABLE)
        self.ds_bytes(0xE46, bytes(60 + k for k in range(16)))      # synthetic tables
        self.ds_bytes(0xE54, bytes(range(2, 14)))
        self.ds_bytes(0x699A, bytes(0x40 + k for k in range(16)))
        self.ds_bytes(0x6905, bytes(0x20 + k for k in range(16)))
        self.ds_bytes(0xD5C, bytes([0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3]))     # 0E6C's line of a position
        self.ds_bytes(0xF3E, bytes([0x0A, 0x00]))                                    # kinds {1, 3} for 5A03 (bit e)

    # -- memory -----------------------------------------------------------------------------------------------------
    def ds_bytes(self, off, data):
        self.mem.memory[self.ds + off:self.ds + off + len(data)] = data

    def ds_word(self, off, value):
        self.ds_bytes(off, value.to_bytes(2, "little"))

    def lin(self, seg, off):
        return seg * 16 + off

    def player(self, n, **fields):
        """Player n's record (20 bytes) with fields given by offset name: f0..f13 (hex digits of the offset)."""
        base = self.lin(self.PLAYERS_SEG, 0x14 * n)
        for k, v in fields.items():
            self.mem.memory[base + int(k[1:], 16)] = v
        return self.mem.memory[base:base + 0x14]

    def squad(self, c, words, tactics=0, manager=None):
        base = self.lin(self.COUNTRIES_SEG, 0xBF * c)
        for i, w in enumerate(words):
            self.mem.memory[base + 2 * i:base + 2 * i + 2] = w.to_bytes(2, "little")
        self.mem.memory[base + 0x2D] = tactics
        if manager is not None:
            self.mem.memory[base + 0x2E] = manager

    def country_byte(self, c, off, value):
        self.mem.memory[self.lin(self.COUNTRIES_SEG, 0xBF * c) + off] = value

    def byte(self, seg, off):
        return self.mem.memory[self.lin(seg, off)]

    # -- calls ------------------------------------------------------------------------------------------------------
    def run(self, address, *args, ax=0, dx=0):
        """The routine at `address` called with the arguments pushed in the order given (the last nearest the return
        address), AX and DX as given; (AX, DX) at its return."""
        entry = REG.entries[address]
        self.mem.set_reg("ax", ax)
        self.mem.set_reg("dx", dx)
        self._execute(address, args, entry.far, "1771:FFFF" if not entry.far else "1771:FFFE")
        return self.mem.reg("ax"), self.mem.reg("dx")

    def _execute(self, address, args, far, ret_to):
        mem = self.mem
        sp0, bp0 = mem.reg("sp"), mem.reg("bp")
        rseg, roff = (int(x, 16) for x in ret_to.split(":"))
        words = list(args) + ([mem.seg(rseg)] if far else []) + [roff]
        sp = sp0
        for w in words:
            sp -= 2
            mem.w16(mem.ss_lin(sp), w & 0xFFFF, "1771:0000")
        mem.set_reg("sp", sp)
        if address in REG.entries:
            entry = REG.entries[address]
            assert entry.far == far, (address, far)
            mem._entries.append((sp, entry.far))
            try:
                value = entry.fn(mem, self.variant)
                if inspect.isgenerator(value):
                    value = self._drive(value)
            finally:
                mem._entries.pop()
            mem.set_reg("sp", sp + (4 if far else 2) + entry.pop)
            mem.set_reg("bp", bp0)
            if value is not None:
                mem.set_reg("ax", value & 0xFFFF)
            return
        model = getattr(self, "m_" + address.replace(":", "_"))
        base = mem.ss_lin(sp)
        ax, pop = model(base + (4 if far else 2))
        mem.set_reg("sp", sp + (4 if far else 2) + pop)
        if ax is not None:
            mem.set_reg("ax", ax & 0xFFFF)

    def _drive(self, gen):
        sent = None
        while True:
            try:
                request = gen.send(sent)
            except StopIteration as stop:
                return stop.value
            self.guest_calls.append((request.target, request.args))
            self._execute(request.target, request.args, request.far, request.ret_to)
            sent = self.mem.reg("ax")

    # -- the helpers of 214B and 23E4 the ports call: models of the listing (the stack as the callee sees it) --------
    def w(self, linear):
        return self.mem.u16(linear)

    def m_214B_0C57(self, a):                     # 0C57: ((word set) >> (elem - 1)) & 1, DX = elem - 1; retf 4
        elem, setw = self.w(a + 2), self.w(a)
        self.mem.set_reg("dx", (elem - 1) & 0xFFFF)
        return (setw >> ((elem - 1) & 0x1F)) & 1, 4

    def _bit_op(self, a, clear):
        elem, seg, off = self.w(a + 4), self.w(a + 2), self.w(a)
        mask = (1 << (elem - 1)) & 0xFFFF
        lin = self.lin(seg, off)
        old = self.mem.memory[lin]
        if clear:
            mask = ~mask & 0xFFFF
            self.mem.memory[lin] = old & mask & 0xFF
            result = old & mask
        else:
            self.mem.memory[lin] = (old | mask) & 0xFF
            result = old | mask
        self.mem.set_reg("dx", mask)
        return result & 0xFFFF, 6

    def m_214B_0C79(self, a):
        return self._bit_op(a, False)

    def m_214B_0CA1(self, a):
        return self._bit_op(a, True)

    def m_23E4_08DF(self, a):                     # 08DF: bit e of byte e >> 3 of the set; ZF set when it is clear; retf 6
        word, seg, off = self.w(a + 4), self.w(a + 2), self.w(a)
        e = word & 0xFF
        zf = not (self.mem.memory[self.lin(seg, off + (e >> 3))] & (1 << (e & 7)))
        self.mem.set_reg("eflags", 0x40 if zf else 0)
        return (self.mem.reg("ax") & 0xFF00) | (1 << (e & 7)), 6

    def _pstr(self, seg, off):
        lin = self.lin(seg, off)
        return self.mem.memory[lin + 1:lin + 1 + self.mem.memory[lin]]

    def pstr(self, seg, off, text):
        lin = self.lin(seg, off)
        self.mem.memory[lin] = len(text)
        self.mem.memory[lin + 1:lin + 1 + len(text)] = bytes(text)

    def m_23E4_075A(self, a):                     # 075A: the character as a string of one at the pointer left on the stack
        ch, off, seg = self.w(a), self.w(a + 2), self.w(a + 4)
        self.pstr(seg, off, bytes([ch & 0xFF]))
        return (self.mem.reg("ax") & 0xFF00) | (ch & 0xFF), 2

    def m_23E4_06B7(self, a):                     # 06B7: the second string appended to the first (at most 255); retf 4
        soff, sseg, doff, dseg = self.w(a), self.w(a + 2), self.w(a + 4), self.w(a + 6)
        self.pstr(dseg, doff, (bytes(self._pstr(dseg, doff)) + bytes(self._pstr(sseg, soff)))[:255])
        return None, 4

    def m_23E4_0644(self, a):                     # 0644: the string at [a + 6] assigned to [a + 2], at most [a] long; retf 0xA
        maxlen, doff, dseg, soff, sseg = self.w(a), self.w(a + 2), self.w(a + 4), self.w(a + 6), self.w(a + 8)
        self.pstr(dseg, doff, bytes(self._pstr(sseg, soff))[:maxlen])
        self.mem.set_reg("dx", self.mem.reg("ds"))
        return None, 10

    def m_23E4_06E3(self, a):                     # 06E3: the 1-based place of the first string in the second, 0 when absent; retf 8
        toff, tseg, poff, pseg = self.w(a), self.w(a + 2), self.w(a + 4), self.w(a + 6)
        pattern, text = bytes(self._pstr(pseg, poff)), bytes(self._pstr(tseg, toff))
        return text.find(pattern) + 1, 8

    def m_214B_09DA(self, a):                     # 09DA: the long (hi, lo) as decimal at the pointer left on the stack; retf 4
        lo, hi, off, seg = self.w(a), self.w(a + 2), self.w(a + 4), self.w(a + 6)
        self.pstr(seg, off, str((hi << 16) | lo).encode())
        return None, 4

    def m_214B_0018(self, a):                     # 0018: FillChar(pointer, count, value); retf 8
        value, count, off, seg = self.w(a), self.w(a + 2), self.w(a + 4), self.w(a + 6)
        lin = self.lin(seg, off)
        self.mem.memory[lin:lin + count] = bytes([value & 0xFF]) * count
        return value & 0xFF, 8


# ---- the tests ----------------------------------------------------------------------------------------------------
class SimTests(unittest.TestCase):
    def test_the_module_ports_the_22_routines_of_the_row(self):
        (reg, variant), = port.load(["attributes"])
        self.assertIsNone(variant)
        listing = {"0AA7": "retf 2", "0B77": "retf 2", "0E24": "ret 2", "0E6C": "retf 2", "2E20": "retf 4",
                   "2E93": "retf 2", "2FAD": "retf 2", "2FFB": "retf 2", "3041": "retf 2", "3088": "retf 2",
                   "30D9": "retf 2", "3179": "retf 2", "3216": "retf 2", "33CD": "retf 2", "3431": "retf 2",
                   "34E7": "retf 2", "377E": "retf 2", "3A06": "retf 4", "3A82": "retf 4", "3E2F": "ret 6",
                   "3EF8": "retf", "5A03": "retf 4"}
        self.assertEqual(sorted(reg.entries), sorted("1771:" + a for a in listing))
        for a, ret in listing.items():
            e = reg.entries["1771:" + a]
            self.assertEqual((e.far, e.pop), (ret.startswith("retf"), int(ret.split()[1]) if " " in ret else 0), a)
        self.assertEqual(sorted(reg.variants),
                         ["foot-sets-swapped", "mark-hi-excl", "skill-divisor-31", "unavailable-bit-6"])

    # -- the readers of a record ---------------------------------------------------------------------------------
    def test_manager_bonus_is_the_manager_byte_over_8_plus_16(self):
        s = Sim()
        s.country_byte(7, 0x2E, 0x83)                        # manager 3 of the manager array at +3 * 0x83 + 1
        s.mem.memory[s.lin(s.MANAGERS_SEG, 3 * 0x83 + 1)] = 0xFF
        self.assertEqual(s.run("1771:0AA7", 7), (255 // 8 + 0x10, 255 % 8))      # zero-extended: no negative dividend
        s.mem.memory[s.lin(s.MANAGERS_SEG, 3 * 0x83 + 1)] = 5
        self.assertEqual(s.run("1771:0AA7", 7), (0x10, 5))

    def test_is_managed_is_the_country_byte_above_0x80(self):
        s = Sim()
        for byte, managed in ((0x80, 0), (0x81, 1), (0x7F, 0), (0xFF, 1), (0, 0)):
            s.country_byte(9, 0x2E, byte)
            ax, dx = s.run("1771:0B77", 9)
            self.assertEqual(ax & 0xFF, managed, hex(byte))
            self.assertEqual(ax >> 8, ((9 * 0xBF) & 0xFFFF) >> 8)                # AH is the multiplication's
            self.assertEqual(dx, (9 * 0xBF) >> 16)

    def test_country_colour_is_15_when_managed_else_the_table_byte(self):
        s = Sim()
        s.country_byte(3, 0x2E, 0x81)
        s.country_byte(3, 0x2C, 5)
        self.assertEqual(s.run("1771:0E24", 3)[0] & 0xFF, 0x0F)
        s.country_byte(3, 0x2E, 3)
        self.assertEqual(s.run("1771:0E24", 3)[0], 0x20 + 5)

    def test_player_name_colour(self):
        s = Sim()
        s.player(5, fE=0)                                    # energy 0: 6
        self.assertEqual(s.run("1771:2E20", 5, 3)[0] & 0xFF, 6)
        s.player(5, fE=9, f10=0x80)                          # element 8 (bit 7): 5
        self.assertEqual(s.run("1771:2E20", 5, 3)[0] & 0xFF, 5)
        s.player(5, fE=9, f10=0x20)                          # element 6 (bit 5): 5
        self.assertEqual(s.run("1771:2E20", 5, 3)[0] & 0xFF, 5)
        s.player(5, fE=9, f10=0x40)                          # element 7 does not count: the position's colour
        self.assertEqual(s.run("1771:2E20", 5, 3)[0] & 0xFF, 0x40 + 3)

    def test_height_hardness_two_footed_and_foot_index(self):
        s = Sim()
        s.player(30, f7=4)
        self.assertEqual(s.run("1771:2FAD", 30)[0], (60 + 4) + (2 + 30 % 12))        # DS:0E46[+7] + DS:0E54[n mod 12]
        s.player(31, f3=0x03, f5=9)
        self.assertEqual(s.run("1771:2FFB", 31), (8, 1))                             # +5 - (+3 and 1)
        s.player(31, f3=0x02, f5=0)
        self.assertEqual(s.run("1771:2FFB", 31), (0, 0))
        s.player(31, f3=0x01, f5=0)
        self.assertEqual(s.run("1771:2FFB", 31)[0], 0xFFFF)                          # 16 bits: 0 - 1
        s.player(32, f5=20, f2=10)
        self.assertEqual(s.run("1771:3041", 32), (1, 20))                            # +5 + +2 == 30
        s.player(32, f5=20, f2=11)
        self.assertEqual(s.run("1771:3041", 32)[0], 0)
        s.player(32, f5=200, f2=100)                                                 # the sum 300: AH 1, not 30
        self.assertEqual(s.run("1771:3041", 32), (0x0100, 200))
        for n, pos7 in ((3, 4), (4, 9), (5, 13)):                                    # DS:0E60[14 * DS:0E7C[n mod 3] + +7]
            s.player(n, f7=pos7)
            want = literal.FOOT_TABLE[14 * literal.FOOT_INDEX[n % 3] + pos7]
            self.assertEqual(s.run("1771:3088", n)[0] & 0xFF, want)

    def test_leadership(self):
        s = Sim()
        for p3, p5, p1, want in ((20, 4, 0x20, (20 - 4) % 8), (4, 20, 0x20, None), (20, 4, 0x10, (20 - 4) % 8 // 2)):
            s.player(40, f3=p3, f5=p5, f1=p1)
            ax, dx = s.run("1771:30D9", 40)
            if want is None:                                  # idiv keeps the sign of the dividend: -16 mod 8 = 0, -15 = -7
                self.assertEqual(ax, 0)
            else:
                self.assertEqual(ax, want)
        s.player(40, f3=4, f5=19, f1=0x20)                    # (4 - 19) = -15: remainder -7 (16 bits), quotient -1
        self.assertEqual(s.run("1771:30D9", 40), ((-7) & 0xFFFF, 0xFFFF))
        s.player(40, f3=4, f5=19, f1=0x10)                    # halved unsigned: 0xFFF9 div 2
        self.assertEqual(s.run("1771:30D9", 40), (0xFFF9 // 2, 1))

    def test_leadership_is_halved_only_below_age_0x15(self):
        s = Sim()
        for age, halved in ((0x14, True), (0x15, False), (0x16, False)):
            s.player(41, f3=21, f5=4, f1=age)                    # 21 - 4 = 17 mod 8 = 1 (16 would give a remainder of 0)
            self.assertEqual(s.run("1771:30D9", 41)[0], (1 // 2) if halved else 1, age)
        s.player(41, f3=26, f5=4, f1=0x14)                         # 22 mod 8 = 6, halved to 3
        self.assertEqual(s.run("1771:30D9", 41)[0], 3)
        s.player(41, f3=26, f5=4, f1=0x15)
        self.assertEqual(s.run("1771:30D9", 41)[0], 6)

    def test_fixture_kind_in_result_set(self):
        s = Sim()
        fixture = s.lin(0x7000, 0x10)
        s.mem.memory[fixture + 2] = 3
        self.assertEqual(s.run("1771:5A03", 0x7000, 0x10, ax=0x1200, dx=0x77), (0x1201, 0x77))    # AH and DX kept
        s.mem.memory[fixture + 2] = 2
        self.assertEqual(s.run("1771:5A03", 0x7000, 0x10, ax=0x1200)[0], 0x1200)

    # -- availability -----------------------------------------------------------------------------------------------
    def test_player_unavailable_by_each_reason(self):
        s = Sim()
        cases = [("available", dict(fE=1, f10=0), 0), ("energy 0", dict(fE=0, f10=0), 1),
                 ("energy negative", dict(fE=0x80, f10=0), 1), ("energy 0xFF", dict(fE=0xFF, f10=0), 1),
                 ("element 8", dict(fE=9, f10=0x80), 1), ("element 6", dict(fE=9, f10=0x20), 1),
                 ("element 3", dict(fE=9, f10=0x04), 1), ("element 7", dict(fE=9, f10=0x40), 0),
                 ("element 5", dict(fE=9, f10=0x10), 0), ("element 4", dict(fE=9, f10=0x08), 0)]
        for name, fields, want in cases:
            s.player(77, **fields)
            self.assertEqual(s.run("1771:3216", 77)[0] & 0xFF, want, name)

    def test_player_unavailable_leaves_ax_and_dx_as_the_listing_does(self):
        s = Sim()
        s.player(77, fE=1, f10=0)
        self.assertEqual(s.run("1771:3216", 77), (0, 2))                            # 0C57's DX of the third test
        s.player(77, fE=1, f10=0x80)
        self.assertEqual(s.run("1771:3216", 77), (1, 7))
        s.player(77, fE=0, f10=0)
        ax, dx = s.run("1771:3216", 77)
        self.assertEqual((ax, dx), ((((77 * 20) & 0xFFFF) & 0xFF00) | 1, (77 * 20) >> 16))   # the multiplication's AH and DX

    def test_squad_slot_of_player(self):
        s = Sim()
        s.squad(5, list(range(100, 120)))
        self.assertEqual(s.run("1771:3A82", 105, 5)[0], 6)
        self.assertEqual(s.run("1771:3A82", 119, 5)[0], 20)
        self.assertEqual(s.run("1771:3A82", 120, 5)[0], 0)
        self.assertEqual(s.run("1771:3A82", 100, 5)[0], 1)

    def test_derived_skill_reads_the_two_literal_tables(self):
        s = Sim()
        s.player(50, f4=100, f5=3, f7=2)
        for element in (1, 5, 12):
            inner = literal.CLASS_TABLE[12 * 2 + element]
            want = literal.PROFILE_TABLE[12 * 3 + inner] * 101 // 32
            self.assertEqual(s.run("1771:3A06", 50, element)[0], want, element)

    # -- the out-of-position flag: the foot test's rows --------------------------------------------------------------
    def foot_rows(self):
        """(foot index, two footed, position, +7, expected) for every row the listing's tests give: 3088's table is the
        original's literal, so the foot of a player is read from it, not assumed."""
        return None

    def test_out_of_place_flag_rows(self):
        s = Sim()
        n = 6                                                  # foot index of player 6: DS:0E60[14 * DS:0E7C[0] + +7]
        feet = {p7: literal.FOOT_TABLE[14 * literal.FOOT_INDEX[n % 3] + p7] for p7 in range(14)}
        right = [p7 for p7, f in feet.items() if f != 0]
        left = [p7 for p7, f in feet.items() if f == 0]
        self.assertTrue(right and left, feet)
        rows = []
        for p7 in right:                                       # a foot, not two footed: the set CS:3139 = {3, 7, 10}
            for pos in (3, 7, 10, 4, 8, 11, 2):
                rows.append((p7, pos, False, 1 if pos in (3, 7, 10) else None))
            rows.append((p7, 5, True, None))                   # two footed skips the set
            rows.append((p7, 3, True, None))
        for p7 in left:                                        # no foot: the set CS:3159 = {4, 8, 11}, two footed or not
            for pos in (4, 8, 11, 3, 7, 10):
                rows.append((p7, pos, False, 1 if pos in (4, 8, 11) else None))
                rows.append((p7, pos, True, 1 if pos in (4, 8, 11) else None))
        for p7, pos, two, want in rows:
            fields = dict(f6=pos, f7=p7, f5=20, f2=10 if two else 11)
            s.player(n, **fields)
            if want is None:                                   # the last test: exactly one of +6 and +7 is 0
                want = 1 if (pos == 0) != (p7 == 0) else 0
            self.assertEqual(s.run("1771:3179", n)[0] & 0xFF, want, (p7, pos, two))
        s.player(n, f6=0, f7=0, f5=20, f2=11)                 # both zero: not out of place
        self.assertEqual(s.run("1771:3179", n)[0] & 0xFF, 0)

    def test_out_of_place_flag_leaves_3041s_ah_and_dx(self):
        s = Sim()
        s.player(6, f6=3, f7=13, f5=200, f2=100)               # sum 300: AH 1, DX = +5
        ax, dx = s.run("1771:3179", 6)
        self.assertEqual((ax >> 8, dx), (1, 200))

    # -- the player's strength ------------------------------------------------------------------------------------
    def test_strength_equals_the_originals_literal_answers(self):
        s = Sim()
        for skill, energy, form, want in literal.GRID:
            s.player(8, f4=skill, fE=energy, fC=form, f5=8, f6=0, f7=0, f10=0)
            self.assertEqual(s.run("1771:377E", 8)[0], want, (skill, energy, form))

    def test_strength_is_zero_when_unavailable_and_halved_when_out_of_place(self):
        s = Sim()
        s.player(8, f4=100, fE=0, f5=8, f6=0, f7=0)            # energy 0: unavailable
        self.assertEqual(s.run("1771:377E", 8)[0], 0)
        s.player(8, f4=100, fE=20, fC=0, f5=8, f6=0, f7=0, f10=0)
        plain = s.run("1771:377E", 8)[0]
        self.assertEqual(plain, 100 - 0x3E + 20)
        s.player(8, f4=100, fE=20, fC=0, f5=8, f6=0, f7=1, f10=0)        # +6 zero, +7 not: out of place
        self.assertEqual(s.run("1771:377E", 8), (plain // 2, 0))
        s.player(8, f4=101, fE=20, fC=0, f5=8, f6=0, f7=1, f10=0)        # 59 is odd: 29, the remainder 1 stays in DX
        self.assertEqual(s.run("1771:377E", 8), (29, 1))
        s.player(8, f4=255, fE=127, fC=31, f5=8, f6=0, f7=0, f10=0)      # 255 - 62 + 127 + 31 = 351: clamped to 0x100
        self.assertEqual(s.run("1771:377E", 8)[0], 0x100)

    def test_strength_below_zero_is_clamped_to_zero(self):
        s = Sim()
        s.player(8, f4=10, fE=1, fC=0, f5=8, f6=0, f7=0, f10=0)         # 10 - 62 + 1 = -51
        self.assertEqual(s.run("1771:377E", 8)[0], 0)

    def test_strength_wrong_foot_is_a_sixteenth_up_to_idiv(self):
        s = Sim()
        s.player(8, f4=74, fE=31, fC=0x7F, f5=8, f6=0, f7=0, f10=0)     # form 0x7F is high: v - v idiv 16
        v = 74 - 0x3E + 31
        self.assertEqual(s.run("1771:377E", 8)[0], v - v // 16)

    # -- a player's own tactics --------------------------------------------------------------------------------------
    def tactics(self, pos, hardness_low, f5=9):
        s = Sim()
        s.player(60, f6=pos, f5=f5 if not hardness_low else 3, f3=0, f0f=0)
        s.run("1771:3431", 60)
        return s.byte(s.PLAYERS_SEG, 0x14 * 60 + 0xF)

    def test_set_player_tactics_by_position(self):
        e = lambda *elements: sum(1 << (k - 1) for k in elements)      # noqa: E731
        for pos in (0, 1, 3, 4):                                       # CS:3411 = {0, 1, 3, 4}: elements 5 and 1
            self.assertEqual(self.tactics(pos, False), e(5, 1), pos)
            self.assertEqual(self.tactics(pos, True), e(8, 5, 1), pos)                 # hardness below 4: 8 on, 4 off
        self.assertEqual(self.tactics(2, False, f5=9), e(5, 6, 2))     # position 2: element 5 only while +5 < 0xE
        self.assertEqual(self.tactics(2, False, f5=0x0E), e(6, 2))
        for pos in (5, 6, 7, 8, 9, 10, 11, 12, 13):
            self.assertEqual(self.tactics(pos, False), 0, pos)
            self.assertEqual(self.tactics(pos, True), e(8), pos)

    def test_set_player_tactics_position_2_with_a_low_skill_sets_element_5_too(self):
        s = Sim()
        s.player(60, f6=2, f5=0x0D, f3=2)                              # hardness 0x0D: 5 - (3 and 1)... +3 is 2: 13
        s.run("1771:3431", 60)
        self.assertEqual(s.byte(s.PLAYERS_SEG, 0x14 * 60 + 0xF), (1 << 4) | (1 << 5) | (1 << 1))

    def test_force_tactic4_off_sets_8_and_clears_4(self):
        s = Sim()
        s.player(61, f0f=0b0000_1111)
        s.run("1771:33CD", 61)
        self.assertEqual(s.byte(s.PLAYERS_SEG, 0x14 * 61 + 0xF), 0b1000_0111)

    def test_reset_own_tactics_clears_and_derives_each_player(self):
        s = Sim()
        s.squad(4, [61, 0, 62] + [0] * 17)
        s.player(61, f6=0, f5=9, f0f=0xFF)
        s.player(62, f6=9, f5=9, f0f=0xFF)
        s.player(63, f0f=0xAA)                                          # not in the squad: untouched
        s.player(0, f0f=0xAA, f6=0)                                     # word 0 is an empty slot: player 0 is never touched
        s.run("1771:34E7", 4)
        self.assertEqual(s.byte(s.PLAYERS_SEG, 0xF), 0xAA)
        self.assertEqual(s.byte(s.PLAYERS_SEG, 0x14 * 61 + 0xF), (1 << 4) | 1)       # position 0: elements 5 and 1
        self.assertEqual(s.byte(s.PLAYERS_SEG, 0x14 * 62 + 0xF), 0)                  # position 9: none
        self.assertEqual(s.byte(s.PLAYERS_SEG, 0x14 * 63 + 0xF), 0xAA)

    # -- the strings ----------------------------------------------------------------------------------------------
    def test_player_name_is_the_initial_a_space_and_the_surname(self):
        s = Sim()
        s.mem.memory[s.ds + 0x9B70:s.ds + 0x9B74] = (0x100).to_bytes(2, "little") + (0x7100).to_bytes(2, "little")
        s.mem.memory[s.ds + 0x9B6C:s.ds + 0x9B70] = (0).to_bytes(2, "little") + (0x7200).to_bytes(2, "little")
        s.mem.memory[0x71000 + 0x100 + 7] = ord("J")
        s.pstr(0x7200, 11 * 7, b"Smith")
        s.run("1771:2E93", 0x7300, 0x20, 7, ax=0, dx=0)               # args: the destination (seg, off), then n
        self.assertEqual(bytes(s._pstr(0x7300, 0x20)), b"J Smith")

    def test_formation_label_counts_the_available_players_by_line(self):
        s = Sim()
        words = list(range(1, 12))                                      # players 1..11, positions: 0, 1, 2, 5, 6, 12, 3, 4, 8, 9, 13
        for w, pos in zip(words, (0, 1, 2, 5, 6, 12, 3, 4, 8, 9, 13)):
            s.player(w, f6=pos, fE=9, f10=0)
        s.player(9, f6=8, fE=0)                                         # unavailable: not counted (a midfielder)
        s.squad(3, words)
        s.run("1771:0E6C", 0x7300, 0x20, 3)
        # lines: 0 -> keeper, 1 -> defence (positions 1..4: 1, 2, 3, 4), 2 -> midfield (5..11: 5, 6, 8 gone, 9), 3 -> attack
        self.assertEqual(bytes(s._pstr(0x7300, 0x20)), b"4-3-2")

    # -- the marking ----------------------------------------------------------------------------------------------
    def test_pick_mark_target_takes_the_first_own_man_that_marks_a_position(self):
        s = Sim()
        mem = s.mem
        bp = 0x4100                                                   # a parent frame above the callee's: BP - 0x10 the own string
        base = mem.ss_lin(bp)
        mem.memory[base - 0x10] = 10
        mem.memory[base - 0x1B] = 10
        for slot, code in zip(range(2, 12), (5, 5, 6, 7, 8, 9, 10, 11, 4, 3)):    # the own positions (slots 2..11)
            mem.memory[base + slot - 0x11] = code
        for slot, code in zip(range(2, 12), (12, 0, 0, 0, 0, 0, 0, 0, 0, 13)):    # the opponents' (12 and 13 are attackers)
            mem.memory[base + slot - 0x1C] = code
        s.ds_bytes(0xEE6 + 14 * 1, bytes([0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]))   # row 1: every opposing position -> own 5
        for r in (2, 3, 4):
            s.ds_bytes(0xEE6 + 14 * r, bytes([99] * 14))
        s.mem.regs.update(ax=0x2222, dx=0x3333)
        s.run("1771:3E2F", 0x0C, 0x0D, bp)                             # lo 0xC, hi 0xD, the parent BP (a near call)
        # opponent slot 11 (position 13), then 2 (position 12), found in the order slot 11 down to 2: each takes the first '5'
        own = [mem.memory[base + slot - 0x11] for slot in range(2, 12)]
        opp = [mem.memory[base + slot - 0x1C] for slot in range(2, 12)]
        marks = [mem.memory[base + slot - 0x27] for slot in range(2, 12)]
        self.assertEqual(opp[0], 0)                                    # slot 2's opponent taken
        self.assertEqual(opp[9], 0)                                    # slot 11's opponent taken
        self.assertEqual(own[0:2], [0, 0])                             # own slots 2 and 3 (position 5) are the markers
        self.assertEqual((marks[0], marks[1]), (11, 2))                # own slot 2 marks opponent 11, slot 3 opponent 2

    def test_pick_mark_target_tries_the_four_rows_in_turn(self):
        s = Sim()
        mem = s.mem
        bp = 0x4100
        base = mem.ss_lin(bp)
        mem.memory[base - 0x10] = 10
        mem.memory[base - 0x1B] = 10
        for slot in range(2, 12):
            mem.memory[base + slot - 0x11] = 3 if slot == 6 else 4                 # own positions: only slot 6 holds code 3
            mem.memory[base + slot - 0x1C] = 13 if slot == 9 else 0                # one opponent, in [12, 13]
        for r, value in ((1, 99), (2, 99), (3, 99), (4, 3)):                       # only row 4 maps position 13 to own 3
            s.ds_bytes(0xEE6 + 14 * r, bytes([value] * 14))
        s.run("1771:3E2F", 0x0C, 0x0D, bp)
        self.assertEqual(mem.memory[base + 6 - 0x11], 0)                           # own slot 6 is the marker
        self.assertEqual(mem.memory[base + 9 - 0x1C], 0)
        self.assertEqual(mem.memory[base + 6 - 0x27], 9)

    def marking_scene(self, tactics0=0x80, opp_unavailable=False):
        s = Sim()
        s.ds_word(0x9B34, 1)
        s.ds_word(0x9B36, 2)
        s.ds_bytes(0xEE6 + 14 * 1, bytes([5] * 14))                  # row 1: every opposing position -> own 5
        for r in (2, 3, 4):
            s.ds_bytes(0xEE6 + 14 * r, bytes([99] * 14))
        team0 = [1 + k for k in range(11)]
        team1 = [201 + k for k in range(11)]
        s.squad(1, team0, tactics=tactics0)
        s.squad(2, team1, tactics=0x80)
        for k, w in enumerate(team0):                                # slot 1 the keeper; slots 2, 3 hold 5, the others 6
            s.player(w, f6=(0 if k == 0 else 5 if k < 3 else 6), fE=9, f10=0)
        for k, w in enumerate(team1):                                # the opposing slots 10 and 11 are attackers 12 and 13
            s.player(w, f6=(0 if k < 9 else 12 if k == 9 else 13), fE=9, f10=0)
        if opp_unavailable:
            s.player(team1[10], fE=0)
        for word in range(0x9A3E, 0x9A3E + 0x50, 2):
            s.ds_word(word, 0xBEEF)
        return s, team0, team1

    def words(self, s, team):
        return [s.mem.u16(s.ds + 0x9A3E + 0x28 * team + 2 * slot) for slot in range(1, 12)]

    def test_set_marking_words_marks_the_opponents_attackers_by_the_first_own_men(self):
        s, team0, team1 = self.marking_scene()
        s.run("1771:3EF8")
        # team 0: own slots 2 and 3 (position 5) mark the opposing slots 11 (position 13) and 10 (12); the rest hold 0
        self.assertEqual(self.words(s, 0), [0, team1[10], team1[9], 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(self.words(s, 1), [0] * 11)               # team 1 has no one in position 5 to mark team 0's 5s

    def test_set_marking_words_a_protect_zone_man_keeps_his_word_and_takes_his_man_out(self):
        s, team0, team1 = self.marking_scene()
        s.player(team0[3], f6=6, fE=9, f10=0x40)                 # slot 4: element 7 (Protect zone)
        s.ds_word(0x9A3E + 2 * 4, team1[6])                      # his marking word names the opposing slot 7
        s.run("1771:3EF8")
        words = self.words(s, 0)
        self.assertEqual(words[3], team1[6])                     # kept
        self.assertEqual(words[1:3], [team1[10], team1[9]])      # the others as without him
        s2, _, _ = self.marking_scene()
        s2.player(team0[3], f6=6, fE=9, f10=0x40)
        s2.player(team1[10], f6=6)                               # the opposing slot 11 no longer an attacker
        s2.ds_word(0x9A3E + 2 * 4, team1[10])                    # ... but named by the protect-zone man: also out of the choice
        s2.player(team1[10], f6=13)
        s2.run("1771:3EF8")
        self.assertEqual(self.words(s2, 0)[1:3], [team1[9], 0])  # slot 11 taken out: slot 2 marks slot 10, slot 3 has none

    def test_set_marking_words_does_not_pick_an_unavailable_opponent(self):
        s, team0, team1 = self.marking_scene(opp_unavailable=True)
        s.run("1771:3EF8")
        self.assertEqual(self.words(s, 0), [0, team1[9], 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def test_set_marking_words_needs_element_8_of_the_team_tactics(self):
        s, team0, team1 = self.marking_scene(tactics0=0x40)      # element 7 only
        s.run("1771:3EF8")
        self.assertEqual(self.words(s, 0), [0] * 11)

    def test_set_marking_words_clears_slot_1_and_marks_the_opponents(self):
        s = Sim()
        mem = s.mem
        s.ds_word(0x9B34, 1)
        s.ds_word(0x9B36, 2)
        s.ds_bytes(0xEE6 + 14 * 1, bytes([0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]))
        for team, country in ((0, 1), (1, 2)):
            words = [200 * team + k for k in range(1, 12)]
            s.squad(country, words, tactics=0x80)                      # team tactics element 8: marking kept
            for k, w in enumerate(words):
                s.player(w, f6=(0 if k == 0 else 5), fE=9, f10=0)
        for word in range(0x9A3E, 0x9A3E + 0x50, 2):
            s.ds_word(word, 0xBEEF)
        s.run("1771:3EF8")
        for team in (0, 1):
            base = s.ds + 0x9A3E + 0x28 * team
            self.assertEqual(mem.u16(base + 2), 0, "slot 1's marking word is cleared")
        # slots with element 8 of the team tactics on and a marker found hold an opponent's player word, or 0
        for team in (0, 1):
            other = [200 * (1 - team) + k for k in range(1, 12)]
            for slot in range(2, 12):
                word = mem.u16(s.ds + 0x9A3E + 0x28 * team + 2 * slot)
                self.assertIn(word, [0] + other, (team, slot))

    def test_set_marking_words_with_the_team_tactic_off_clears_every_word(self):
        s = Sim()
        mem = s.mem
        s.ds_word(0x9B34, 1)
        s.ds_word(0x9B36, 2)
        s.ds_bytes(0xEE6 + 14 * 1, bytes([0, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]))
        for team, country in ((0, 1), (1, 2)):
            words = [200 * team + k for k in range(1, 12)]
            s.squad(country, words, tactics=0x00)
            for k, w in enumerate(words):
                s.player(w, f6=5, fE=9, f10=0)
        for word in range(0x9A3E, 0x9A3E + 0x50, 2):
            s.ds_word(word, 0xBEEF)
        s.run("1771:3EF8")
        for team in (0, 1):
            for slot in range(2, 12):
                self.assertEqual(mem.u16(s.ds + 0x9A3E + 0x28 * team + 2 * slot), 0)


class VariantTests(unittest.TestCase):
    """Each variant is a falsifier: an answer the unvaried port gives, changed."""

    def pair(self, variant, setup, address, *args, **kw):
        out = []
        for v in (None, variant):
            s = Sim(v)
            setup(s)
            out.append(s.run(address, *args, **kw))
        return out

    def test_unavailable_bit_6(self):
        base, mutated = self.pair("unavailable-bit-6", lambda s: s.player(77, fE=9, f10=0x20), "1771:3216", 77)
        self.assertEqual((base[0], mutated[0]), (1, 0))               # element 6 (bit 5) set: unavailable; the variant tests bit 4

    def test_skill_divisor_31(self):
        base, mutated = self.pair("skill-divisor-31", lambda s: s.player(50, f4=200, f5=3, f7=2), "1771:3A06", 50, 5)
        self.assertNotEqual(base, mutated)

    def test_foot_sets_swapped(self):
        # a right foot (foot index 1), position 3, not two footed: out of place; with the sets swapped it is not
        def setup(s):
            s.player(6, f6=3, f7=13, f5=20, f2=11)
        base, mutated = self.pair("foot-sets-swapped", setup, "1771:3179", 6)
        feet = literal.FOOT_TABLE[14 * literal.FOOT_INDEX[6 % 3] + 13]
        self.assertNotEqual(feet, 0)
        self.assertEqual((base[0] & 0xFF, mutated[0] & 0xFF), (1, 0))

    def test_mark_hi_excl(self):
        def setup(s):
            bp = 0x4100
            base = s.mem.ss_lin(bp)
            s.mem.memory[base - 0x10] = 10
            s.mem.memory[base - 0x1B] = 10
            s.mem.memory[base + 2 - 0x11] = 5
            s.mem.memory[base + 2 - 0x1C] = 13                     # an opponent of position 13 == hi
            s.ds_bytes(0xEE6 + 14 + 13, bytes([5]))
            s.base = base
        out = []
        for v in (None, "mark-hi-excl"):
            s = Sim(v)
            setup(s)
            s.run("1771:3E2F", 0x0C, 0x0D, 0x4100)
            out.append(s.byte(s.SS, 0x4100 + 2 - 0x1C))
        self.assertEqual(out, [0, 13])                              # taken by the port, left by the variant


# ---- against the original (unicorn and the image) -------------------------------------------------------------
try:
    import unicorn  # noqa: F401
except ImportError:
    unicorn = None


def load_diffcheck():
    sys.path.insert(0, str(ROOT / "experiments/E036-match-port"))
    spec = importlib.util.spec_from_file_location("e036t61_diffcheck", DIFFCHECK)
    module = importlib.util.module_from_spec(spec)
    sys.modules["e036t61_diffcheck"] = module
    spec.loader.exec_module(module)
    return module


def reference_image_bytes():
    from original_match.assets import REFERENCE
    path = ROOT / ".cache/dl" / REFERENCE["asset"]
    return path.read_bytes() if path.is_file() else None


@unittest.skipIf(unicorn is None or reference_image_bytes() is None, "needs unicorn and the reference image in .cache/dl")
class DifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from original_match import Image
        cls.diff = load_diffcheck()
        cls.image = Image.from_bytes(reference_image_bytes())
        cls.routines = cls.diff.routines()
        cls.specs = port.load(["attributes"])

    def test_every_routine_equals_the_originals_on_random_states(self):
        for address, rt in sorted(self.routines.items()):
            for k in range(15):
                args, regs, problems, _ = self.diff.case(self.image, rt, "T61-unit", k, self.specs)
                self.assertEqual(problems, [], (address, k, args))

    def test_the_harness_sees_a_mutated_port(self):
        mutated = port.load(["attributes.skill-divisor-31"])
        rt = self.routines["1771:3A06"]
        seen = [self.diff.case(self.image, rt, "T61-unit", k, mutated)[2] for k in range(3)]
        self.assertTrue(any("AX" in text for problems in seen for text in problems), seen)


if __name__ == "__main__":
    unittest.main()
