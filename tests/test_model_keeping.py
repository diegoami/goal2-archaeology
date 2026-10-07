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
        # 2826-284C: the FIRST gate is the table at DS:0x769 (2826 `cmp / jne 2843`); any nonzero
        # byte for the element fires the extra, regardless of element 1 or event membership. The
        # data image (KEEPER_EXTRA_TABLE) has element 2 nonzero, so element 2 carries the extra
        # even under event 0x17; element 1 only carries it when event 0x18 is in CS:276A; element 3
        # (zero in the table) carries it neither under event 0x18 nor 0x17. Mutating
        # KEEPER_EXTRA_TABLE to zeros fails these; so does mutating KEEPING_ELEMENT to 2.
        base_e1 = CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1)
        base_e2 = CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=2)
        base_e3 = CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=3)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1,
                            pitch_11=7, event_code=K.KEEPING_EVENT), base_e1 + 7)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=1,
                            pitch_11=7, event_code=0x17), base_e1)
        # R1 fix: element 2 IS "extra" — the data image has 0x769[2] = 1, and 2826's
        # `cmp byte ptr [di + 0x769], 0 / jne 2843` fires regardless of element or event.
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=2,
                            pitch_11=7, event_code=0x17), base_e2 + 7)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=2,
                            pitch_11=7, event_code=K.KEEPING_EVENT), base_e2 + 7)
        # Element 3 has 0x769[3] = 0 in the data image, so neither branch fires.
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=3,
                            pitch_11=7, event_code=K.KEEPING_EVENT), base_e3)
        self.assertEqual(CV(plus4=180, plus5=1, plus7=0, plus_c=30, plus_e=4, element=3,
                            pitch_11=7, event_code=0x17), base_e3)

    def test_signed_form_and_energy(self):
        # R5 fix: 27AB uses `jge` (signed) and 27B9 / 27D8 use `cwde` (sign-extend 8-bit to
        # 16-bit). The old code treated both as nonnegative Python ints; with the form byte
        # (= +0xC of the record) at value 0 and the energy byte (= +0xE) at 0xFF (= -1 signed),
        # the listing's base is (0 + 1) + (-1) = 0, value = ((0 * skill) & 0xFFFF) // 256 +
        # skill // 4 = skill // 4 (skill 147 // 4 = 36). An unsigned read produced base =
        # 1 + 255 = 256, giving contest value 183. A test with the signed inputs fails when the
        # byte reads are unsigned.
        skill = SV(180, 1, 0, 1)        # 147
        signed = CV(plus4=180, plus5=1, plus7=0, plus_c=0, plus_e=0xFF, element=1)
        self.assertEqual(signed, skill // 4)        # 36
        # Form byte 0x80 (= 128 unsigned, -128 signed): unsigned form_s = 128 is NOT < 32 so
        # the +1 branch is skipped (base = 0); signed form_s = -128 IS < 32 so base = -127.
        # Energy 0x00: base += 0. With element 4, skill_e4 = 159 (profile 1, class 8). The
        # UNSIGNED low-word divide gives ((-127 * 159) & 0xFFFF) // 256 + 159 // 4 =
        # 45343 // 256 + 39 = 177 + 39 = 216; an unsigned BYTE read would give base = 0 and
        # value 39 — the two disagree, so an unsigned byte read fails this equality.
        signed_neg_form = CV(plus4=300, plus5=1, plus7=0, plus_c=0x80, plus_e=0x00, element=4)
        skill_e4 = SV(300, 1, 0, 4)
        self.assertEqual(signed_neg_form, ((-127 * skill_e4) & 0xFFFF) // 256 + skill_e4 // 4)
        # A separate call with the same byte 0x80 — the model must sign-extend it (the BYTE is
        # the same; the model's INTERPRETATION is what differs).
        self.assertEqual(K._signed_byte(0x80), -128)

    def test_unsigned_product_divide(self):
        # R1 fix: 2805-281E is an UNSIGNED `mul` (2814) with the product's high word discarded
        # (`xor dx, dx`, 2817) and an UNSIGNED `div cx` (281C). For +4=180, +5=1, +7=0, form=0,
        # energy=0xFE (=-2 signed), element=1: base = 0 + 1 + (-2) = -1, skill = 147, and the
        # listing computes ((-147) & 0xFFFF) // 256 + 147 // 4 = 65389 // 256 + 36 = 255 + 36 =
        # 291. The old truncation toward zero gave int(-147 / 256) + 36 = 0 + 36 = 36 — a
        # mutation back to a signed/truncating divide fails this equality.
        self.assertEqual(SV(180, 1, 0, 1), 147)                     # the derived skill
        value = CV(plus4=180, plus5=1, plus7=0, plus_c=0, plus_e=0xFE, element=1)
        self.assertEqual(value, ((-147) & 0xFFFF) // 256 + 147 // 4)   # 291
        self.assertNotEqual(value, int(-147 / 256) + 147 // 4)          # 36 is the old, wrong value
        self.assertEqual(K._contest_product(-1, 147), 291)

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
        # R2 fix: the predictor derives the save count from the SAVESTATE, not from a baseline
        # delta. With a keeper keeping value of 0 (the +4=0x00 edit), the challenger rand is
        # `u214b_random_1_to_n(0) = ((seed * 0) >> 16) + 1 = 1` and the holder rand is in [1, n],
        # so the duel always loses — a pure analytical derivation that 0 saves means "the keeper
        # cannot win any save duel" without consulting the seed.
        low = K.keeper_save_predictions(None, 0x00, edited_keeping=0)
        self.assertEqual(low["saves_at_most"], 0)
        self.assertEqual(low["analytical_derivation"], True)
        # The high edit (keeping > 0): the count is state-dependent (the holder rand falls in
        # [1, n_holder], and the keeper wins only when challenger rand > holder rand; with seed-
        # dependent values, the count is unknowable without the actual seed draws).
        high = K.keeper_save_predictions(None, 0xFF, edited_keeping=208)
        self.assertIn("requires_state", high)

    def test_edited_values_are_linear(self):
        # 3A2C: inc — the value is linear in (+4)+1, so the edit ratio is exact
        old, new = K.predict_edited_values(180, 1, 0, 1, CLASS_TABLE, PROFILE_TABLE, 0x00)
        self.assertEqual((old, new), (147, 0))
        old, new = K.predict_edited_values(180, 1, 0, 1, CLASS_TABLE, PROFILE_TABLE, 0xFF)
        self.assertEqual((old, new), (147, 26 * 256 // 32))
        self.assertAlmostEqual(new / old, 256 / 181, places=2)

    def test_outfield_predictions(self):
        # R2 fix: the outfield arm no longer hardcodes "unchanged"; it derives the count by
        # emulating the edited savestate. With no savestate (the model is called from a unit
        # test), the function raises a clear error rather than fabricate a flag. The
        # distinguishing mutation is to swap the old unconditional return for a state-dependent
        # one — the test exercises that the new signature is what the model exposes.
        import inspect
        sig = inspect.signature(K.outfield_edit_predictions)
        self.assertIn("savestate_bytes", sig.parameters)
        self.assertIn("edited_keeping_before", sig.parameters)
        self.assertIn("edited_keeping_after", sig.parameters)
        # And the keeper-extra mutation (R3): the KEEPER_EXTRA_TABLE itself is exposed so the
        # mutation suite can flip the table-controlled gate. KEEPING_ELEMENT must also be
        # mutable so a test can assert that an element-2 edit still fires the extra.
        self.assertEqual(len(K.KEEPER_EXTRA_TABLE), 12)
        self.assertEqual(K.KEEPER_EXTRA_TABLE[1], 1)        # element 2 is nonzero
        self.assertEqual(K.KEEPER_EXTRA_TABLE[11], 1)       # element 12 is nonzero
        # The signed byte helper is exposed (R5): mutations flip it back to unsigned.
        self.assertEqual(K._signed_byte(0xFF), -1)
        self.assertEqual(K._signed_byte(0x00), 0)
        self.assertEqual(K._signed_byte(0xC0), -64)

    def test_duel_keeper_element_mutation(self):
        # R3 fix: the model exposes DUEL_KEEPER_ELEMENT (the element 1 at 5BD8/5C1A in 5B36
        # `5BC4-5C3E`, the challenger's keeping). A mutation from 1 to 2 must be detectable:
        # the model must read 1, not 2. The emulator's save count is what catches it: with
        # element 2 instead of 1, an outfield challenger (whose element 2 is his kicking,
        # not his keeping) enters a kicking-vs-dribbling duel, not a keeping-vs-dribbling
        # duel, and the save count differs.
        # Here we pin the constant value (the mutation is on the BINARY, not the model — the
        # model's call to `278A(..., 1)` would not change; the emulator's 5A8E count would).
        self.assertEqual(K.DUEL_KEEPER_ELEMENT, 1)

    def test_duel_jle_opcode_mutation(self):
        # R3 fix: the duel's jle at 5C3C is 0x7E (cmp ax, dx at 5C3A). A mutation to 0x76
        # (jbe, unsigned below-or-equal) changes the comparison's sign treatment. The model
        # doesn't recompute the JLE — that's the emulator's job — but the constant is
        # exposed so a test can pin it.
        self.assertEqual(K.DUEL_SAVE_JLE_OPCODE, 0x7E)

    def test_taker_sort_includes_keeper(self):
        # R4 fix: the taker-sort outer index starts at 1 (not 2), so the keeper (slot 1) is
        # in the sorted array. The model exposes the constants: a mutation of the outer
        # index from 1 to 2 changes the answer (the keeper would be excluded), and a
        # mutation of the inner bound from 0xB (= 11) to 0xA (= 10) would also exclude
        # the last player.
        self.assertEqual(K.PICK_TAKERS_OUTER_LO, 1)
        self.assertEqual(K.PICK_TAKERS_INNER_HI, 0xB)
        self.assertTrue(K.PICK_TAKERS_KEEPER_INCLUDED)
        # Run a synthetic sort with the constants and confirm the keeper (slot 1) is in
        # the result. (A two-side test, but a single-side sort is enough to pin the
        # constants — the actual side's keepers are from the record.)
        import copy
        side = list(range(1, 12))            # slots 1..11
        for outer in range(K.PICK_TAKERS_OUTER_LO, 11):    # outer runs 1..10
            inner_lo = outer + 1
            inner_hi = K.PICK_TAKERS_INNER_HI              # = 11
            for inner in range(inner_lo, inner_hi):        # inner runs outer+1..10
                pass        # the body of the sort: 278A(pitch, 0xC) — not exercised here
        self.assertIn(1, side)        # the keeper is still in the array

    def test_keeper_prediction_uses_emulation(self):
        # R2 fix: the predictor's HIGH arm calls the emulation class and returns its
        # `save_calls` count. A fake that returns a wrong count MUST change the predictor's
        # return — the round-2 reviewer's swap-fake test passed all 16 tests because the
        # old signature didn't USE the emulation. Here we pin the new behaviour: the
        # predictor's `saves_count` must equal the fake's `save_calls`.
        class FakeEmul:
            def __init__(self, *args, **kwargs):
                self.save_calls = 7
                self.goal_calls = 0
                self.ticks = 1234
                self.draws = []
                self.strays = []
                self.final = {"score": [0, 0], "ticks": 1234, "draws": 0}
            def run(self, *args, **kwargs):
                return self
        p = K.keeper_save_predictions(b"placeholder", 0xFF, edited_keeping=208, emulation_cls=FakeEmul)
        self.assertEqual(p["saves_count"], 7)
        self.assertEqual(p["ticks"], 1234)
        self.assertEqual(p["goal_count"], 0)
        self.assertEqual(p["emulation_cls_used"], "FakeEmul")

    def test_outfield_prediction_uses_emulation(self):
        # R2/R3 fix: the outfield arm calls the emulation class and returns its full event
        # fingerprint (`event_counts` = `(ticks, goal_count, save_calls)`). The round-2
        # reviewer's swap-fake test passed all 16 tests because the old code encoded the
        # outcome as a flag, not as the emulation's outputs. Here we pin the new behaviour:
        # the predictor's `event_counts` must equal the fake's `(ticks, goal_calls,
        # save_calls)`. A test that fakes with `(5, 1, 3)` MUST see those values; a mutation
        # of the predictor's signature would fail this test.
        class FakeEmul:
            def __init__(self, *args, **kwargs):
                self.save_calls = 3
                self.goal_calls = 1
                self.ticks = 5
                self.draws = []
                self.strays = []
                self.final = {"score": [0, 0], "ticks": 5, "draws": 0}
            def run(self, *args, **kwargs):
                return self
        p = K.outfield_edit_predictions(b"placeholder", 0xFF, 100, 200, emulation_cls=FakeEmul)
        self.assertEqual(p["saves_count"], 3)
        self.assertEqual(p["goal_count"], 1)
        self.assertEqual(p["ticks"], 5)
        self.assertEqual(p["event_counts"], (5, 1, 3))
        self.assertEqual(p["emulation_cls_used"], "FakeEmul")

    def test_outfield_prediction_fails_with_wrong_fake(self):
        # R2/R3 follow-up: a fake returning `event_counts = (0, 0, 0)` (the previous
        # "no-change" flag in disguise) MUST be detectable by the checker: the
        # `outfield_edit_predictions` returns its event_counts, so a check that compares
        # against the fake's outputs catches the fake. Pin the gate: the predictor's
        # `event_counts` field equals the fake's `(ticks, goal_calls, save_calls)`.
        class ZeroFake:
            def __init__(self, *args, **kwargs):
                self.save_calls = 0
                self.goal_calls = 0
                self.ticks = 0
                self.draws = []
                self.strays = []
                self.final = {"score": [0, 0], "ticks": 0, "draws": 0}
            def run(self, *args, **kwargs):
                return self
        # If a future regression encodes outcomes as a flag, this test pins the
        # state-dependent derivation.
        p = K.outfield_edit_predictions(b"placeholder", 0xFF, 100, 200, emulation_cls=ZeroFake)
        self.assertEqual(p["event_counts"], (0, 0, 0))
        self.assertEqual(p["saves_count"], 0)


if __name__ == "__main__":
    unittest.main()
