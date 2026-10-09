"""Literal-input/expected-output tests for the events-morale model.

These cover the edges the listing establishes: each named event's delta,
the persist flag's effect on DS:9B07, the [1, 255] clamp on the live byte,
the team aggregate's `min(32, s8(+0xC))` per starter (no lower clamp; the
16-bit accumulator wraps mod 0x10000; the divide-by-11 is unsigned), the
+6 seed, and the floor of 1. The signed-byte boundaries 1, 128, 255 are
the R1 cases the review required.
"""
import unittest

from runtime.model import morale


class EventClampTests(unittest.TestCase):
    def test_injure_high_morale(self):
        # 0791:7D56: clamp(+0xC + (-2), 1, 255), persist True.
        self.assertEqual(morale.injure(30), (28, 28))

    def test_injure_low_morale(self):
        # 1 + (-2) = -1 → clamp to 1.
        self.assertEqual(morale.injure(2), (1, 1))

    def test_injure_floor_morale(self):
        # 1 + (-2) = -1 → clamp to 1; persist writes min(32, 1) = 1.
        self.assertEqual(morale.injure(1), (1, 1))

    def test_send_off_clamps_and_persists(self):
        # The send_off head call has the same effect as injure: -2 with persist True.
        self.assertEqual(morale.send_off(30), (28, 28))
        self.assertEqual(morale.send_off(1), (1, 1))

    def test_scorer_plus_one_persists(self):
        # 0791:6443 calls 7CC5 with s8(DS:0x7920[side]) = +1 and flag 1.
        self.assertEqual(morale.scorer(16, 1), (17, 17))

    def test_scorer_minus_one_persists(self):
        # When DS:7C39 != 0, the scorer's delta is s8(0x7920[0]) = -1.
        self.assertEqual(morale.scorer(16, -1), (15, 15))

    def test_team_reaction_does_not_persist(self):
        # 0791:65FE: 7CC5 with s8(DS:0x7920[side]) and flag 0; DS:9B07 not written.
        self.assertEqual(morale.team_reaction(16, 1), (17, None))
        self.assertEqual(morale.team_reaction(16, -1), (15, None))

    def test_event_clamp_signed_byte_high(self):
        # 127 + (-2) = 125; clamp to [1, 255]; persist=1 writes min(32, 125) = 32.
        self.assertEqual(morale.event_clamp(127, -2, True), (125, 32))

    def test_event_clamp_signed_byte_wrap(self):
        # 128 (signed -128) + (-2) = -130 → 1; persist=1 writes 1.
        self.assertEqual(morale.event_clamp(128, -2, True), (1, 1))

    def test_event_clamp_no_persist_leaves_saved_alone(self):
        # 0791:65FE writes live only; DS:9B07 untouched.
        self.assertEqual(morale.event_clamp(16, 0, False), (16, None))

    def test_event_clamp_persist_false_signed_byte_still_clamped(self):
        # 254 as a signed byte is -2; +1 = -1 → clamp to 1; no DS:9B07 write.
        self.assertEqual(morale.event_clamp(254, 1, False), (1, None))
        # 30 + 1 = 31, clamp keeps 31.
        self.assertEqual(morale.event_clamp(30, 1, False), (31, None))
        # 32 + 1 = 33, no upper cap here (the clamp is [1, 255] for 7CC5).
        self.assertEqual(morale.event_clamp(32, 1, False), (33, None))

    def test_event_clamp_signed_underflow_helper_rejects_out_of_byte(self):
        # The signed-one-byte delta helper guards against non-byte values.
        for delta in (-129, 128, 200):
            with self.assertRaises(ValueError):
                morale.scorer(16, delta)
            with self.assertRaises(ValueError):
                morale.team_reaction(16, delta)


class TeamPanelTests(unittest.TestCase):
    """The 1771:13D0 team-aggregate arithmetic (R1).

    The 214B:0D1C helper returns min(32, s8(+0xC)) with no lower clamp:
    a -128 player byte contributes -128 to the 16-bit accumulator. The
    `add word ptr [0x9B5A], ax` at seg_1771_02.asm:1067 wraps mod 0x10000;
    the `div cx` at line 1093 is the 16-bit unsigned divide by 11; the
    `cmp word ptr [0x9B5A], 1; jae` at 1120-1122 sets a floor of 1.
    """

    def test_all_zero_floors_to_one(self):
        # All starters at 0: sum (no lower clamp) = 0, +6 = 6, //11 = 0, floor = 1.
        self.assertEqual(morale.team_panel_morale([0] * 11), 1)

    def test_all_32_returns_32(self):
        # All starters at 32: sum = 11*32 = 352, +6 = 358, //11 = 32.
        self.assertEqual(morale.team_panel_morale([32] * 11), 32)

    def test_all_16(self):
        # (6 + 11*16) // 11 = 182 // 11 = 16.
        self.assertEqual(morale.team_panel_morale([16] * 11), 16)

    def test_mixed(self):
        starters = [1, 32, 16, 8, 0, 24, 28, 4, 12, 20, 5]
        self.assertEqual(morale.team_panel_morale(starters), 14)

    def test_signed_negative_byte_contributes_negative(self):
        # 128 as signed byte is -128. The aggregate does NOT clamp to 0:
        # min(32, -128) = -128, total = 6 + (-128) = -122, & 0xFFFF = 65414,
        # 65414 // 11 = 5946 (R1).
        self.assertEqual(morale.team_panel_morale([128] + [0] * 10), 5946)

    def test_all_signed_negative(self):
        # 11 × -128: total = 6 + 11 * (-128) = -1402, & 0xFFFF = 64134,
        # 64134 // 11 = 5830. The hand-traced original returns 5830.
        self.assertEqual(morale.team_panel_morale([128] * 11), 5830)

    def test_one_signed_neg_one(self):
        # 255 as signed byte is -1. min(32, -1) = -1, total = 6 + (-1) = 5,
        # 5 // 11 = 0, floor 1.
        self.assertEqual(morale.team_panel_morale([255] + [0] * 10), 1)

    def test_one_signed_above_32(self):
        # 200 as signed byte is -56. min(32, -56) = -56, total = 6 + (-56) = -50,
        # & 0xFFFF = 65486, 65486 // 11 = 5953.
        self.assertEqual(morale.team_panel_morale([200] + [0] * 10), 5953)

    def test_one_just_above_32_clamped(self):
        # 33 (signed) is positive, min(32, 33) = 32, total = 6 + 32 = 38,
        # // 11 = 3.
        self.assertEqual(morale.team_panel_morale([33] + [0] * 10), 3)

    def test_one_signed_pos_127_clamped(self):
        # 127 (signed) is positive, min(32, 127) = 32, total = 6 + 32 = 38,
        # // 11 = 3.
        self.assertEqual(morale.team_panel_morale([127] + [0] * 10), 3)

    def test_above_32_clamped_to_32(self):
        # A starter at byte value 32 contributes 32; a value just above (33 as
        # signed = 33) contributes 32 (clamped to PANEL_MAX).
        self.assertEqual(morale.team_panel_morale([32] * 11), 32)
        self.assertEqual(morale.team_panel_morale([33] * 11), 32)
        # 11 contributions of 32 give the same total as 11 of 33.
        self.assertEqual(
            morale.team_panel_morale([32] * 11),
            morale.team_panel_morale([33] * 11),
        )

    def test_exactly_below_one(self):
        # 0+0+...+1: total = 6+1 = 7, // 11 = 0, → 1.
        self.assertEqual(morale.team_panel_morale([0] * 10 + [1]), 1)

    def test_just_at_floor(self):
        # sum + 6 = 11, // 11 = 1, → 1.
        self.assertEqual(morale.team_panel_morale([0] * 10 + [5]), 1)

    def test_above_floor(self):
        # sum + 6 = 12, // 11 = 1, → 1.
        self.assertEqual(morale.team_panel_morale([0] * 10 + [6]), 1)

    def test_panel_seed_is_6(self):
        # The seed is added BEFORE the divide.
        # 11 starters at 32 → (6 + 352) // 11 = 32.
        self.assertEqual(morale.team_panel_morale([32] * 11), 32)
        # 11 starters at 16 → (6 + 176) // 11 = 16.
        self.assertEqual(morale.team_panel_morale([16] * 11), 16)
        # The seed is observable when the sum crosses the //11 boundary:
        # 10 starters at 0 + 1 at 1 → 7 // 11 = 0, → 1 (the floor catches it).
        # The literal contract: a 32 starter in a zero lineup yields 38 // 11 = 3.
        self.assertEqual(morale.team_panel_morale([32] + [0] * 10), 3)

    def test_panel_divisor_is_11(self):
        # 11 starters at 32 → 32.
        self.assertEqual(morale.team_panel_morale([32] * 11), 32)
        # 10 starters at 32 + 1 at 16 → 358-16=342 // 11 = 31.
        self.assertEqual(morale.team_panel_morale([16] + [32] * 10), 31)
        # 11 at 33 (clamped to 32) → 32; a divisor of 10 gives 35, of 12 gives 29.
        self.assertEqual(morale.team_panel_morale([33] * 11), 32)

    def test_panel_floor_is_1(self):
        # sum + 6 = 6, // 11 = 0 → floor 1.
        self.assertEqual(morale.team_panel_morale([0] * 11), 1)
        # All -128 contributions: 5830 (still >= 1).
        self.assertEqual(morale.team_panel_morale([128] * 11), 5830)
        # All -1 contributions: 6 + 11*(-1) = -5, & 0xFFFF = 65531,
        # 65531 // 11 = 5957 → 5957.
        self.assertEqual(morale.team_panel_morale([255] * 11), 5957)

    def test_non_list_rejected(self):
        # Must be a list or tuple.
        for bad in (None, 5, b'\x00' * 11, 32):
            with self.assertRaises(ValueError):
                morale.team_panel_morale(bad)

    def test_does_not_accept_stringly_typed(self):
        # String iterables should be rejected (the helper requires
        # byte-or-int elements).
        with self.assertRaises(ValueError):
            morale.team_panel_morale('01234567890')


class ClampBoundaries(unittest.TestCase):
    def test_literal_edges(self):
        # The clamp [1, 255] on the live byte.
        for before, delta in [(0, 0), (1, 0), (32, 0), (33, 0), (255, 0),
                              (1, 1), (32, -31), (16, 16), (16, -15), (16, 17)]:
            live, _ = morale.event_clamp(before, delta, True)
            self.assertTrue(1 <= live <= 255)


class MutationConstants(unittest.TestCase):
    """The constants in the model are locked here; a refactor must update
    this test before merging. The full per-constant sweep lives in
    `mutations_morale.py` so the unit suite stays fast."""

    CONSTANTS = (
        ('BYTE_BITS', 8),
        ('WORD_BITS', 16),
        ('LIVE_LOWER', 1),
        ('LIVE_UPPER', 255),
        ('SAVED_UPPER', 32),
        ('PANEL_MAX', 32),
        ('PANEL_SEED', 6),
        ('PANEL_DIVISOR', 11),
        ('PANEL_FLOOR', 1),
    )

    def test_all_constants_have_expected_values(self):
        for name, value in self.CONSTANTS:
            self.assertEqual(getattr(morale, name), value, name)


if __name__ == '__main__':
    unittest.main()
