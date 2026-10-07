#!/usr/bin/env python3
"""Unit tests for runtime/model/keeping.py (T27, Q012; E013). Every constant the tests pin cites
the listing line it comes from. The class/profile tables are the initialised data image's bytes
at DS:6D25/DS:6DCD (static/goal-exe/data/ds_2581_03.hex; F008's `summarise.py --tables` prints
the same two tables from the records). The mutation checks of Done-when 2 — the divisor, the
keeper gate, the contest order — are pinned by test_skill_divisor_is_32, test_keeper_extra_gate
and test_save_predictions (each fails when its constant is changed; the PR lists them).
Run: python3 -m unittest -v tests.test_model_keeping"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import keeping as K  # noqa: E402


def hex_bytes(path):
    """The initialised data segment as {offset: byte} ('*' rows repeat the previous 0x20)."""
    import re
    mem, last_off = {}, None
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith(";") or line == "*":
            if line == "*":
                for i in range(0x20):
                    mem[last_off + 0x20 + i] = mem[last_off + i]
                last_off += 0x20
            continue
        m = re.match(r"^([0-9A-F]{4})\s+((?:[0-9A-F]{2} )+)", line)
        if not m:
            continue
        off = int(m.group(1), 16)
        for i, b in enumerate(bytes.fromhex(m.group(2).replace(" ", ""))):
            mem[off + i] = b
        last_off = off
    return mem


DATA = hex_bytes(ROOT / "static" / "goal-exe" / "data" / "ds_2581_03.hex")
CLASS_TABLE = [DATA[0x6D25 + i] for i in range(14 * 12)]    # DS:6D25 (F008)
PROFILE_TABLE = [DATA[0x6DCD + i] for i in range(16 * 12)]  # DS:6DCD (F008)
SV = lambda b4, b5, b7, e: K.skill_value(b4, b5, b7, e, CLASS_TABLE, PROFILE_TABLE)  # noqa: E731
CV = lambda **kw: K.contest_value(class_table=CLASS_TABLE, profile_table=PROFILE_TABLE, **kw)  # noqa: E731


class TestTables(unittest.TestCase):
    def test_class_columns(self):
        # seg_1771_05.asm:3A46: c = DS:6D25[12*+7 + element]; a goalkeeper's keeping class is 1
        # (row 0), every outfield position's is 12 (rows 1..13, element 1) — "only the keeper
        # keeps" is the derivation, not a gate (F015).
        self.assertEqual(CLASS_TABLE[12 * 0 + 1], 1)
        self.assertTrue(all(CLASS_TABLE[12 * p + 1] in (7, 11, 12) for p in range(1, 14)))
        # element 12 reads the byte at 12*+7 + 12 — the NEXT row's column 0 (the formula F008
        # verified on 960 bars): a goalkeeper's penalties class is row 1 column 0 = 12 (weak),
        # a position-2 defender's is 9 (row 3 column 0)
        self.assertEqual(CLASS_TABLE[12 * 0 + 12], CLASS_TABLE[12 * 1 + 0])
        self.assertEqual(CLASS_TABLE[12 * 0 + 12], 12)
        self.assertEqual(CLASS_TABLE[12 * 2 + 12], CLASS_TABLE[12 * 3 + 0])

    def test_keeper_keeping_value(self):
        # profile row [+5] class 1 is 23..26 (F008's curve table): 3A06 = row*((+4)+1) div 32
        for b5 in range(1, 16):
            row = PROFILE_TABLE[12 * b5 + CLASS_TABLE[12 * 0 + 1]]
            self.assertIn(row, (23, 25, 26), f"profile {b5}")
        self.assertEqual(SV(180, 1, 0, 1), 26 * 181 // 32)     # 147: the new game's keeper
        self.assertEqual(SV(0x00, 1, 0, 1), 0)                 # +4 = 0 floors keeping at 0
        self.assertEqual(SV(0xFF, 1, 0, 1), 26 * 256 // 32)    # 208: the high edit

    def test_skill_divisor_is_32(self):
        # 3A71-3A74: mov cx, 0x20 / div cx — the screen's 3947 divides by 0x100 instead (F008);
        # a mutated divisor (0x100) fails this equality on the keeper's own numbers
        self.assertEqual(K.SKILL_DIVISOR, 32)
        self.assertEqual(SV(180, 1, 0, 1), (26 * 181) // 32)
        self.assertNotEqual(SV(180, 1, 0, 1), (26 * 181) // 256)


class TestContest(unittest.TestCase):
    # 0791:278A, seg_0791_04.asm:846-2879
    def test_form_and_energy_base(self):
        # 27AB-27D9: form +1 below 0x20 else 0; energy +0xE joins only for element < 0xC
        skill = SV(180, 1, 0, 1)
        # element 1 joins the energy: base = 30 + 1 + 4 = 35
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1),
                         (35 * skill) // 256 + skill // 4)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1),
                         (35 * 147) // 256 + 147 // 4)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=0x20, plus_e=4, element=1),
                         (0 + 4) * 147 // 256 + 147 // 4)

    def test_penalty_bonus(self):
        # 27C5-27CF: element >= 0xC adds 0x20 to the base and skips the energy add
        e12 = CV(plus4=180, plus5=1, plus7=12, plus_c=30, plus_e=4, element=12)
        skill = SV(180, 1, 12, 12)
        self.assertEqual(e12, ((31 + 0x20) * skill) // 256 + skill // 4)  # form 30 -> base 31, then the 0x20 bonus

    def test_pitch_halving(self):
        # 27F1-2802: pitch record +0x13 set halves the derived skill before the product
        plain = CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1)
        halved = CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1, pitch_13=1)
        skill = SV(180, 1, 0, 1) // 2      # 147 -> 73
        self.assertEqual(halved, (35 * skill) // 256 + skill // 4)
        self.assertNotEqual(halved, plain)

    def test_keeper_extra_gate(self):
        # 2823-284C: only element 1 under event code 0x18 (the set CS:276A) adds pitch +0x11;
        # any other element or event adds nothing — the mutated gate (element 2, or event 0x17)
        # fails these two
        base = CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1,
                            pitch_11=7, event_code=K.KEEPING_EVENT), base + 7)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1,
                            pitch_11=7, event_code=0x17), base)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=2,
                            pitch_11=7, event_code=K.KEEPING_EVENT),
                         CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=2))

    def test_manager_share(self):
        # 284F-286A: an outfield slot (pitch +6 < 0xC) with 80FC set adds value/16
        v = CV(plus4=180, plus5=1, plus7=1, plus_c=30, plus_e=4, element=3, pitch_6=1, flag_80fc=1)
        plain = CV(plus4=180, plus5=1, plus7=1, plus_c=30, plus_e=4, element=3, pitch_6=1)
        self.assertEqual(v, plain + plain // 16)

    def test_outfield_keeping_is_not_gated_away(self):
        # an outfield challenger's derived keeping is NOT negligible: his class column is 7, 11
        # or 12, and class 7 with profile 1 gives 19*181 div 32 = 107 against a keeper's 147 —
        # the save duel reads keeping of whoever challenges, goalkeeper or not (F015)
        self.assertLess(SV(180, 1, 12, 1), SV(180, 1, 0, 1))
        self.assertEqual(SV(180, 1, 2, 1), 19 * 181 // 32)      # position 2: class 7 -> 107
        self.assertGreater(SV(180, 1, 12, 1), 30)


class TestPredictions(unittest.TestCase):
    def test_save_predictions(self):
        # the E013 arms: +4 -> 0x00 predicts strictly fewer saves than the baseline's second
        # half (the keeper's contest value collapses, seg_0791_10.asm:5BD8); +4 -> 0xFF
        # predicts a changed line log. A mutated order (the low edit predicting no change)
        # fails this test
        low = K.keeper_save_predictions(3, 0x00)
        self.assertTrue(low["saves_below_baseline"])
        self.assertEqual(low["saves_at_most"], 2)
        high = K.keeper_save_predictions(3, 0xFF)
        self.assertFalse(high["saves_below_baseline"])
        self.assertTrue(high["line_log_differs_from_baseline"])

    def test_edited_values_are_linear(self):
        # 3A2C: inc — the value is linear in (+4)+1, so the edit ratio is exact
        old, new = K.predict_edited_values(180, 1, 0, 1, CLASS_TABLE, PROFILE_TABLE, 0x00)
        self.assertEqual((old, new), (147, 0))
        old, new = K.predict_edited_values(180, 1, 0, 1, CLASS_TABLE, PROFILE_TABLE, 0xFF)
        self.assertEqual((old, new), (147, 26 * 256 // 32))
        self.assertAlmostEqual(new / old, 256 / 181, places=2)

    def test_outfield_predictions(self):
        # 3A06 is element-parametric and reads +4 for every element, so the edited outfield
        # player's values shift; but 214B:0688 advances once per rand(n) call whatever n is
        # (F012), so only a flipped comparison changes the trajectory — the prediction the
        # E013-r0003 record checks: no event count changes. A mutated "always differs" fails.
        p = K.outfield_edit_predictions()
        self.assertTrue(p["line_log_unchanged"])
        self.assertTrue(p["values_change"])


if __name__ == "__main__":
    unittest.main()
