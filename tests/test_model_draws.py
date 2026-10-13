#!/usr/bin/env python3
"""Unit tests for runtime/model/draws.py (T47, M2c; F004): the wrappers 214B:06B1 and 214B:06D0. Each constant
cites its listing line (draws.py). Every test fails when the behaviour it pins is removed: the PR lists the
mutations (the range n, the compare to 1, the result values, AH, DX, the seed step).
Run: python3 -m unittest -v tests.test_model_draws"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import draws as D  # noqa: E402
import recreate  # noqa: E402


class Wrapper06B1Tests(unittest.TestCase):
    def test_draw_and_seed_are_recreates(self):
        # seed 0x1234, n = 4: new word 21363, draw 2 (the same values contests.py pins)
        r = D.draw_06b1(0x1234, 4)
        self.assertEqual((r.draw, r.seed), recreate.draw(0x1234, 4))
        self.assertEqual((r.draw, r.seed), (2, 21363))

    def test_range_is_1_to_n(self):
        draws = {D.draw_06b1(s, 6).draw for s in range(0, 65536, 3)}
        self.assertEqual(draws, {1, 2, 3, 4, 5, 6})          # never 0, never n + 1 (06A4 `inc dx` after the mul)

    def test_n_of_1_always_draws_1(self):
        self.assertEqual({D.draw_06b1(s, 1).draw for s in range(0, 65536, 11)}, {1})

    def test_ax_and_dx_are_the_draw(self):
        r = D.draw_06b1(1, 2048)                              # draw 1199 = 0x4AF: both bytes of AX count
        self.assertEqual((r.draw, r.ax, r.dx), (1199, 0x04AF, 0x04AF))

    def test_n_is_16_bit(self):
        self.assertEqual(D.draw_06b1(0x1234, 0x10004), D.draw_06b1(0x1234, 4))


class Wrapper06D0Tests(unittest.TestCase):
    def test_al_is_1_exactly_when_the_draw_is_1(self):
        # n = 4: a quarter of the seeds draw 1 (06E3 `cmp ax, 1`, 06EC)
        ones = [s for s in range(65536) if D.draw_06d0(s, 4).ax & 0xFF == 1]
        self.assertEqual(len(ones), 16384)
        for s in ones[:50]:
            self.assertEqual(D.draw_06d0(s, 4).draw, 1)
        self.assertEqual(D.draw_06d0(0, 4).ax & 0xFF, 1)       # seed 0 draws 1 at n = 4
        self.assertEqual(D.draw_06d0(0x1234, 4).ax & 0xFF, 0)  # draw 2

    def test_al_is_never_the_draws_low_byte(self):
        # draw 2: AL = 0, not 2 (06E8 `mov al, 0`); draw 1199 (low byte 0xAF): AL = 0
        self.assertEqual(D.draw_06d0(0x1234, 4).ax, 0)
        self.assertEqual(D.draw_06d0(1, 2048).ax, 0x0400)

    def test_ah_keeps_the_draws_high_byte_and_dx_the_draw(self):
        r = D.draw_06d0(1, 2048)
        self.assertEqual((r.draw, r.ax >> 8, r.dx), (1199, 0x04, 1199))
        r = D.draw_06d0(0, 4)
        self.assertEqual((r.ax, r.dx), (1, 1))

    def test_seed_is_stepped_as_the_draw_does(self):
        self.assertEqual(D.draw_06d0(0x1234, 4).seed, recreate.draw(0x1234, 4)[1])

    def test_n_of_1_is_always_true(self):
        self.assertEqual({D.draw_06d0(s, 1).ax for s in range(0, 65536, 13)}, {1})


if __name__ == "__main__":
    unittest.main()
