#!/usr/bin/env python3
"""Unit tests for runtime/model/contests.py (T46, M2b; F022): the gate 0791:287C. Each constant cites
its listing line (contests.py). Every test fails when the behaviour it pins is removed: the PR lists
the mutations (divisor, + 1, inversion, the seed step, AH, DX).
Run: python3 -m unittest -v tests.test_model_contests"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import contests as C  # noqa: E402
import recreate  # noqa: E402


class GateTests(unittest.TestCase):
    def test_n_is_the_value_div_32_plus_1(self):
        # 288E-2895: unsigned div by 0x20, then inc; the edges of the divisor
        for value, n in ((0, 1), (31, 1), (32, 2), (63, 2), (64, 3), (100, 4), (0xFFFF, 2048)):
            self.assertEqual(C.gate(value, 0x1234).n, n, value)

    def test_the_value_is_the_16_bit_ax(self):
        self.assertEqual(C.gate(0x10020, 0x1234).n, 2)       # only AX reaches the div (2893)

    def test_n_of_1_never_succeeds(self):
        # a draw of 1..1 is 1, 06D0 is true, 287C returns 0 for every seed
        self.assertEqual({C.gate(31, s).result for s in range(0, 65536, 7)}, {0})

    def test_the_result_is_one_unless_the_draw_is_one(self):
        # n = 4 (value 100): 06D0 is true for exactly a quarter of the seeds; 287C is 0 there
        zero = [s for s in range(65536) if C.gate(100, s).result == 0]
        self.assertEqual(len(zero), 16384)
        for s in zero[:50]:
            self.assertEqual(C.gate(100, s).draw, 1)
        self.assertEqual(C.gate(100, 0).result, 0)           # seed 0 draws 1 at n = 4
        self.assertEqual(C.gate(100, 0x1234).result, 1)      # draw 2

    def test_the_draw_is_recreates_with_the_new_seed(self):
        draw, new = recreate.draw(0x1234, 4)
        g = C.gate(100, 0x1234)
        self.assertEqual((g.draw, g.seed), (draw, new))
        self.assertEqual((g.draw, g.seed), (2, 21363))

    def test_registers_ax_and_dx(self):
        # AL = result, AH = the draw's high byte (06D0 and 287C change AL only), DX = the draw (06A4)
        g = C.gate(0xFFFF, 1)
        self.assertEqual((g.draw, g.result), (1199, 1))
        self.assertEqual(g.ax, 0x0400 | 1)
        self.assertEqual(g.dx, 1199)
        g = C.gate(100, 0)
        self.assertEqual((g.ax, g.dx), (0, 1))


if __name__ == "__main__":
    unittest.main()
