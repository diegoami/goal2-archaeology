#!/usr/bin/env python3
"""Unit tests for runtime/model/longs.py (T48, M2d): the long helpers 214B:0D56 (signed 32-bit max) and 23E4:0279
(32-bit multiply). Every case asserts the FULL result tuple (0D56: AX, DX, ES, flags; 0279: AX, DX, BX, CX, SI, DI,
flags), not one register. The tuples are checked three ways: by hand (the docstrings), by the differential test against
the ORIGINAL machine code run on a bare Unicorn machine (tests/longs_original.py: the listing's bytes), and through
tests/mutations_t48.py, which kills each branch condition, register and term of the models in memory.
Run: python3 -m unittest -v tests.test_model_longs"""
import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
sys.path.insert(0, str(ROOT / "tests"))
import longs as L  # noqa: E402

CF, PF, AF, ZF, SF, OF = L.CF, L.PF, L.AF, L.ZF, L.SF, L.OF


def mx(a, b):
    return tuple(L.max_0d56(a & 0xFFFF, a >> 16, b & 0xFFFF, b >> 16))


class FlagTests(unittest.TestCase):
    def test_sub_flags(self):
        self.assertEqual(L.sub16_flags(5, 3), 0)                        # 2: one bit set -> odd parity, PF clear
        self.assertEqual(L.sub16_flags(3, 5), CF | AF | SF)             # 0xFFFE: borrow, borrow out of bit 3, sign; 7 bits -> PF clear
        self.assertEqual(L.sub16_flags(7, 7), ZF | PF)                  # 0: zero, even parity
        self.assertEqual(L.sub16_flags(0x8000, 0x7FFF), OF | AF)        # 0x0001: signed overflow, borrow out of bit 3
        self.assertEqual(L.sub16_flags(0x7FFF, 0x8000), OF | CF | SF | PF)   # 0xFFFF: no borrow out of bit 3 (F - 0), 8 bits -> PF
        self.assertEqual(L.sub16_flags(0xFFFF, 0xFFFE), 0)

    def test_add_flags(self):
        self.assertEqual(L.add16_flags(0xFFFF, 1), CF | AF | ZF | PF)    # 0: carry, carry out of bit 3, zero, even
        self.assertEqual(L.add16_flags(0x7FFF, 1), OF | AF | SF | PF)    # 0x8000: signed overflow, sign; low byte 0: even
        self.assertEqual(L.add16_flags(1, 2), PF)                        # 3: two bits -> even
        self.assertEqual(L.add16_flags(1, 1), 0)                         # 2: one bit -> odd
        self.assertEqual(L.add16_flags(0x8000, 0x8000), CF | OF | ZF | PF)


class Max0D56Tests(unittest.TestCase):
    """CASES: ((a, b), (AX, DX, ES, flags)). Flags are those of the last `cmp` (0D61 high words when they differ,
    else 0D68 low words)."""
    CASES = [
        ((0x00000005, 0x00000003), (0x5, 0x0, 0x0, 0x0)),                  # a > b: a (0D6D)
        ((0x00000003, 0x00000005), (0x5, 0x0, 0x0, 0x91)),                 # a < b: b (0D7A)
        ((0x00000007, 0x00000007), (0x7, 0x0, 0x0, 0x44)),                 # a == b: b (a tie returns b: identical)
        ((0x00020000, 0x00010005), (0x0, 0x2, 0x2, 0x0)),                  # a hi > b hi (jg): a although a lo < b lo
        ((0x00010005, 0x00020000), (0x0, 0x2, 0x2, 0x95)),                 # a hi < b hi (jl): b although a lo > b lo
        ((0xFFFF0000, 0x00000001), (0x1, 0x0, 0x0, 0x84)),                 # negative a < positive b: b
        ((0x00000001, 0xFFFF0000), (0x1, 0x0, 0x0, 0x11)),                 # positive a > negative b: a
        ((0xFFFFFFFF, 0xFFFFFFFE), (0xFFFF, 0xFFFF, 0xFFFF, 0x0)),         # -1 > -2: a (high words equal, low unsigned 0xFFFF > 0xFFFE)
        ((0xFFFFFFFE, 0xFFFFFFFF), (0xFFFF, 0xFFFF, 0xFFFF, 0x95)),        # -2 < -1: b
        ((0xFFFFFFFF, 0x00000000), (0x0, 0x0, 0x0, 0x84)),                 # -1 < 0: b
        ((0x00000000, 0xFFFFFFFF), (0x0, 0x0, 0x0, 0x11)),                 # 0 > -1: a
        ((0x00018000, 0x00017FFF), (0x8000, 0x1, 0x1, 0x810)),             # equal high words, lo 0x8000 > 0x7FFF UNSIGNED: a
        ((0x00017FFF, 0x00018000), (0x8000, 0x1, 0x1, 0x885)),             # lo 0x7FFF < 0x8000 unsigned: b
        ((0x80000000, 0x7FFFFFFF), (0xFFFF, 0x7FFF, 0x7FFF, 0x810)),       # most negative < most positive: b (high words signed)
        ((0x7FFFFFFF, 0x80000000), (0xFFFF, 0x7FFF, 0x7FFF, 0x885)),       # most positive > most negative: a
        ((0x80000000, 0x80000000), (0x0, 0x8000, 0x8000, 0x44)),           # equal negatives
        ((0x12345678, 0x12345679), (0x5679, 0x1234, 0x1234, 0x95)),        # carry across the low byte: b
    ]

    def test_exact_tuples(self):
        for (a, b), want in self.CASES:
            with self.subTest(a=hex(a), b=hex(b)):
                self.assertEqual(mx(a, b), want)

    def test_branches_are_distinguished(self):
        """The three decisions separately: jg (high words signed greater), jl (signed less), jbe (low words, unsigned)."""
        self.assertEqual(mx(0x00000000, 0xFFFF0005)[:2], (0, 0))          # jg: 0 > negative; the low words would say b
        self.assertEqual(mx(0xFFFF0005, 0x00000000)[:2], (0, 0))          # jl: a negative loses; the low words would say a
        self.assertEqual(mx(0x00010001, 0x00010000)[:2], (1, 1))          # equal high: a lo > b lo -> a
        self.assertEqual(mx(0x00010000, 0x00010001)[:2], (1, 1))          # equal high: a lo < b lo -> b
        self.assertEqual(mx(0x00010000, 0x0000FFFF)[:2], (0, 1))          # a hi > b hi although a lo < b lo

    def test_es_is_the_winners_high_word(self):
        for (a, b), (ax, dx, es, _) in self.CASES:
            self.assertEqual(es, dx)

    def test_max_matches_the_signed_value(self):
        rng = random.Random(48)
        for _ in range(2000):
            a, b = rng.getrandbits(32), rng.getrandbits(32)
            if rng.random() < 0.3:
                b = (a & 0xFFFF0000) | rng.getrandbits(16)               # equal high words
            sa, sb = a - (1 << 32) * (a >> 31), b - (1 << 32) * (b >> 31)
            ax, dx, es, _ = mx(a, b)
            self.assertEqual((dx << 16) | ax, a if sa > sb else b)


class Mul0279Tests(unittest.TestCase):
    """CASES: ((AX, DX, BX, CX), (AX, DX, BX, CX, SI, DI, flags)). The second operand is BX:CX with CX the LOW word and BX
    the HIGH word: `mul cx` at 027D pairs with AX, `mul bx` (0283) is the low-word-times-high-word cross term, and
    the second `mul cx` (0289) is DX times CX. The flags are those of the last `add dx, cx` (0291)."""
    CASES = [
        ((3, 0, 0, 5), (0xF, 0, 0, 0, 3, 0, 0x44)),                          # 3 * 5
        ((0xFFFF, 0, 0, 0xFFFF), (0x1, 0xFFFE, 0, 0, 0xFFFF, 0, 0x80)),      # 0xFFFF * 0xFFFF = 0xFFFE0001: carry into the high word
        ((0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF), (0x1, 0, 0x1, 0x1, 0xFFFF, 0xFFFF, 0x55)),   # 0xFFFFFFFF ** 2 mod 2**32 = 1
        ((0, 1, 0, 1), (0, 1, 0, 1, 0, 1, 0)),                              # (1 << 16) * 1: DX * CX term only
        ((2, 0, 1, 0), (0, 2, 2, 0, 2, 0, 0)),                               # 2 * (1 << 16): AX * BX term only
        ((2, 3, 5, 7), (0xE, 0x1F, 0xA, 0x15, 2, 3, 0)),                     # 2*7 + (2*5 + 3*7) << 16
        ((0, 0, 0xFFFF, 0xFFFF), (0, 0, 0, 0, 0, 0, 0x44)),                  # 0 times anything
        ((0x8000, 0, 0, 2), (0, 1, 0, 0, 0x8000, 0, 0)),                     # 0x8000 * 2 = 0x10000
        ((0x1234, 0x5678, 0x9ABC, 0xDEF0), (0x28C0, 0xD68A, 0xA630, 0x2080, 0x1234, 0x5678, 0x80)),
        ((0xFFFF, 0, 0xFFFF, 0), (0, 1, 1, 0, 0xFFFF, 0, 0)),                # the AX * BX term wraps: 0xFFFF * 0xFFFF low word 1
        ((0, 0xFFFF, 0, 0xFFFF), (0, 1, 0, 1, 0, 0xFFFF, 0)),                # the DX * CX term wraps: low word 1
        ((1, 0, 0xFFFF, 0), (0, 0xFFFF, 0xFFFF, 0, 1, 0, 0x84)),             # 1 * (0xFFFF << 16)
        ((0x100, 0x100, 0x100, 0x100), (0, 1, 0, 0, 0x100, 0x100, 0)),       # both low terms vanish; high-word carry of AX * CX
        ((0xFFFF, 0xFFFF, 0, 1), (0xFFFF, 0xFFFF, 0, 0xFFFF, 0xFFFF, 0xFFFF, 0x84)),   # -1 * 1
    ]

    def test_exact_tuples(self):
        for regs, want in self.CASES:
            with self.subTest(regs=regs):
                self.assertEqual(tuple(L.mul_0279(*regs)), want)

    def test_product_is_the_low_32_bits(self):
        rng = random.Random(49)
        for _ in range(2000):
            a, b = rng.getrandbits(32), rng.getrandbits(32)
            r = L.mul_0279(a & 0xFFFF, a >> 16, b >> 16, b & 0xFFFF)
            self.assertEqual((r.dx << 16) | r.ax, (a * b) & 0xFFFFFFFF)

    def test_each_term_alone(self):
        """AX*CX (027D) alone, AX*BX (0283) alone, DX*CX (0289) alone, and the carry from the first into DX."""
        self.assertEqual(tuple(L.mul_0279(0xFFFF, 0, 0, 2))[:2], (0xFFFE, 1))      # carry out of the low product
        self.assertEqual(tuple(L.mul_0279(3, 0, 5, 0))[:2], (0, 15))               # AX * BX
        self.assertEqual(tuple(L.mul_0279(0, 3, 0, 5))[:2], (0, 15))               # DX * CX
        self.assertEqual(tuple(L.mul_0279(0, 0, 5, 7))[:2], (0, 0))                # DX = AX = 0: no term
        self.assertEqual(tuple(L.mul_0279(1, 1, 1, 1))[:2], (1, 2))                # all three: 1 + (1 + 1) << 16

    def test_si_di_are_the_inputs_and_bx_cx_the_low_words_of_the_terms(self):
        r = L.mul_0279(0x1234, 0x5678, 0x9ABC, 0xDEF0)
        self.assertEqual((r.si, r.di), (0x1234, 0x5678))                            # 0279, 027B
        self.assertEqual(r.bx, (0x1234 * 0x9ABC) & 0xFFFF)                          # 0285
        self.assertEqual(r.cx, (0x5678 * 0xDEF0) & 0xFFFF)                          # 028B


class DifferentialTests(unittest.TestCase):
    """The models against the original machine code (the listing's bytes) on a bare Unicorn machine: every register the
    routine touches, the untouched ones (a sentinel in each), SP after the return, and the arithmetic flags."""

    @classmethod
    def setUpClass(cls):
        try:
            import longs_original
        except ModuleNotFoundError:
            raise unittest.SkipTest("unicorn not installed")
        cls.O = longs_original

    LONGS = [0, 1, 0x7FFF, 0x8000, 0xFFFF, 0x10000, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0x12345678, 0xFFFF0000, 0x0000FFFF]

    def test_max_on_every_pair_of_edge_values(self):
        for a in self.LONGS:
            for b in self.LONGS:
                r = self.O.original_max(a, b)
                with self.subTest(a=hex(a), b=hex(b)):
                    self.assertEqual((r["AX"], r["DX"], r["ES"], r["EFLAGS"] & self.O.ARITH_FLAGS), mx(a, b))
                    self.assertEqual((r["BX"], r["CX"], r["SI"], r["DI"], r["SP"]), (0x1111, 0x2222, 0x3333, 0x4444, self.O.SP0))

    def test_mul_on_random_and_edge_registers(self):
        rng = random.Random(50)
        words = [0, 1, 2, 0x7FFF, 0x8000, 0xFFFF, 0x100, 0x1234]
        for _ in range(300):
            regs = [rng.choice(words + [rng.getrandbits(16)]) for _ in range(4)]
            r = self.O.original_mul(*regs)
            with self.subTest(regs=regs):
                got = (r["AX"], r["DX"], r["BX"], r["CX"], r["SI"], r["DI"], r["EFLAGS"] & self.O.ARITH_FLAGS)
                self.assertEqual(got, tuple(L.mul_0279(*regs)))
                self.assertEqual((r["ES"], r["SP"]), (0x5555, self.O.SP0))

    def test_the_cases_above_are_the_originals(self):
        for (a, b), want in Max0D56Tests.CASES:
            r = self.O.original_max(a, b)
            self.assertEqual((r["AX"], r["DX"], r["ES"], r["EFLAGS"] & self.O.ARITH_FLAGS), want)
        for regs, want in Mul0279Tests.CASES:
            r = self.O.original_mul(*regs)
            self.assertEqual((r["AX"], r["DX"], r["BX"], r["CX"], r["SI"], r["DI"], r["EFLAGS"] & self.O.ARITH_FLAGS), want)

    def test_other_flag_bits_are_not_the_routines(self):
        """Neither routine writes a non-arithmetic flag (IF, DF): started with both set they are still set."""
        r = self.O.original_max(5, 3, flags=0x0602)
        self.assertEqual(r["EFLAGS"] & ~self.O.ARITH_FLAGS, 0x0602)
        r = self.O.original_mul(3, 0, 0, 5, flags=0x0602)
        self.assertEqual(r["EFLAGS"] & ~self.O.ARITH_FLAGS, 0x0602)


if __name__ == "__main__":
    unittest.main()
