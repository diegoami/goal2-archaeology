#!/usr/bin/env python3
"""Unit tests for runtime/model/ageing.py (T28, Q013; E014). Every constant the tests pin cites
the listing line it comes from (experiments/E014-q013-ageing/notes.md). The mutation checks of
Done-when 2 — the peak-band rule, a branch direction, a divisor, the variance seed — are pinned
by test_band_edges, test_below_band_halves, test_above_band_and_divisor,
test_retirement_predicate_edges and test_seed_is_not_consumed (each fails when its constant is
changed; the PR lists the mutations run). These tests fail before the change (runtime/model/
ageing.py does not exist on main) and pass after it.
Run: python3 -m unittest -v tests.test_model_ageing"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import ageing as A  # noqa: E402


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
CLASS_TABLE = bytes(DATA[0x6D25 + i] for i in range(14 * 12))    # DS:6D25 (F008/F015)
PROFILE_TABLE = bytes(DATA[0x6DCD + i] for i in range(16 * 12))  # DS:6DCD (F008/F015)
DATA1 = hex_bytes(ROOT / "static" / "goal-exe" / "data" / "ds_2581_01.hex")


def record(age=27, peak=27, rating=0xF0, profile=5, club=3, caps=0, **kw):
    r = bytearray(20)
    r[0] = 7                      # country (any nonzero)
    r[A.AGE] = age
    r[A.PEAK] = peak
    r[A.RATING] = rating
    r[A.ABILITY] = A.compute_ability(age, peak, rating)
    r[0x05] = profile
    r[0x06] = club
    r[A.CLUB_POSITION] = club
    r[A.CAPS] = caps & 0xFF       # caps, a word (F008: +8/+9)
    r[A.CAPS + 1] = caps >> 8
    r[0x0C] = 0x10
    r[0x0D] = 0x10
    r[0x0E] = 0x10
    r[0x12] = 0xFF                # performance 0x7FFF low byte (F014)
    r[0x13] = 0x7F
    for k, v in kw.items():
        r[int(k, 0) if isinstance(k, str) else k] = v
    return bytes(r)


class BandRuleTests(unittest.TestCase):
    """compute_ability 1771:32EB, seg_1771_05.asm:283-370 (notes.md section 3)."""

    def test_band_edges(self):
        # 3308-332E: inside p..p+3 -> +4 = +3 (333A). Mutating PEAK_BAND (3 -> 2 or 4) moves
        # an edge and fails this test; so does swapping either branch direction (jb/jg).
        r = 0xF0
        for age in (27, 28, 29, 30):                 # p = 27: the band 27..30
            self.assertEqual(A.compute_ability(age, 27, r), r, f"age {age} inside the band")
        self.assertEqual(A.compute_ability(31, 27, r), (r * 15) // 16, "p+4: k = 1 (337F)")
        self.assertEqual(A.compute_ability(26, 27, r), r, "p-1: k = 0 (33A1-33A7)")

    def test_below_band_halves(self):
        # 338D-33A7: k = (p - a) idiv 2 (signed, cdq at 33A3) — floor for p > a.
        # Mutating BELOW_DIVISOR (2 -> 1) fails this test.
        r = 0xF0
        self.assertEqual(A.compute_ability(25, 27, r), (r * 15) // 16)   # k = 2//2 = 1
        self.assertEqual(A.compute_ability(24, 27, r), (r * 15) // 16)   # k = 3//2 = 1 (floor)
        self.assertEqual(A.compute_ability(23, 27, r), (r * 14) // 16)   # k = 4//2 = 2
        self.assertEqual(A.compute_ability(21, 27, r), (r * 13) // 16)   # k = 6//2 = 3

    def test_above_band_and_divisor(self):
        # 3368-3388: k = a - (p + 3), one step per year; 33B3-33C3: +4 = ((r * (16 - k)) mod
        # 65536) div 16, low byte. Mutating ABILITY_DIVISOR (16 -> 15) or FACTOR_BASE fails.
        r = 0xF0
        self.assertEqual(A.compute_ability(32, 27, r), (r * 14) // 16)   # k = 2
        self.assertEqual(A.compute_ability(37, 27, r), (r * 9) // 16)    # k = 7
        self.assertEqual(A.compute_ability(31, 27, 240), 225)            # 240 * 15 // 16
        # the whole curve is monotone in the three branches: rises below the band, flat inside,
        # falls above (the backlog's hypothesis, from the listing's branches)
        curve = [A.compute_ability(a, 27, r) for a in range(20, 38)]
        below = curve[:7]
        self.assertEqual(below, sorted(below), "rises to the band")
        self.assertEqual(curve[7:11], [r] * 4, "flat inside the band 27..30")
        above = curve[11:]
        self.assertEqual(above, sorted(above, reverse=True), "falls after the band")

    def test_factor_wrap_edge(self):
        # 3386/33AE: factor = 0x10 - k is a 16-bit WORD — k > 16 wraps negative; 33B6 mul is
        # unsigned 16x16, 33B9 `xor dx, dx` keeps only the low product, 33BE div 16 unsigned.
        # a = p + 20 -> k = 17 -> factor 0xFFFF: (240 * 0xFFFF) mod 65536 = 65296, // 16 = 4081,
        # low byte 0xF1. The listing's arithmetic, not a Python negative floor.
        self.assertEqual(A.compute_ability(47, 27, 240), ((240 * 0xFFFF) & 0xFFFF) // 16 & 0xFF)
        self.assertEqual(A.compute_ability(47, 27, 240), 0xF1)

    def test_age_byte_wrap(self):
        # 7E6F: inc byte ptr es:[di + 1] — a byte increment, wraps 255 -> 0.
        out = A.year_end_bytes(1, record(age=255, peak=30, rating=100))
        self.assertEqual(out[A.AGE], 0)


class YearEndBytesTests(unittest.TestCase):
    """The loop's per-player writes: 7FB1/7E4A (notes.md section 2)."""

    def test_writes_exactly_three_bytes(self):
        # The yearly loop's complete write set on a continuing player is {+1, +4, +0x11}
        # (7E6F, 333A/33C3, 7FD4) — +2, +3, +5, +6, +7 are never written.
        out = A.year_end_bytes(1, record())
        self.assertEqual(sorted(k for k in out if isinstance(k, int)), [0x01, 0x04, 0x11])
        self.assertEqual(out[0x11], 0)                       # 7FD4
        self.assertIn("retires", out)

    def test_player_zero_skips_the_age(self):
        # 7E64-7E6A: 7E4A returns without the increment for player 0; 7FB1's +0x11 write (7FD4)
        # is unconditional, so player 0's record still gets +0x11 = 0 and nothing else.
        out = A.year_end_bytes(0, record(age=25, peak=27, rating=0xF0))
        self.assertEqual(sorted(k for k in out if isinstance(k, int)), [0x11])

    def test_retirement_flag_is_reported(self):
        self.assertEqual(A.year_end_bytes(1, record(age=28, peak=27))["retires"], 0)
        self.assertEqual(A.year_end_bytes(1, record(age=34, peak=28))["retires"], 1)


class RetirementTests(unittest.TestCase):
    """1771:7F40 (seg_1771_11.asm:950-1000; notes.md section 4)."""

    def test_retirement_predicate_edges(self):
        # (DS:110E[gk] < a AND caps == 0) OR a > p + 5. DS:110E = 1E 21 (ds_2581_01.hex:143);
        # the data image itself, so the constants are not hand-copied:
        self.assertEqual((DATA1[0x110E], DATA1[0x110F]), tuple(A.RETIRE_LIMIT))
        f = A.retirement_flag
        self.assertEqual(f(record(age=30, peak=27, club=3, caps=0)), 0)   # 30 < 30 false
        self.assertEqual(f(record(age=31, peak=27, club=3, caps=0)), 1)   # 30 < 31, caps 0
        self.assertEqual(f(record(age=31, peak=27, club=3, caps=4)), 0)   # caps nonzero, 31<=32
        self.assertEqual(f(record(age=33, peak=27, club=3, caps=40)), 1)  # 33 > 27+5
        self.assertEqual(f(record(age=33, peak=28, club=3, caps=40)), 0)  # 33 <= 28+5
        # goalkeeper: DS:110E[1] = 0x21 = 33 (club_position 0, 7F5D-7F6A)
        self.assertEqual(f(record(age=33, peak=30, club=0, caps=0)), 0)   # 33 < 33 false
        self.assertEqual(f(record(age=34, peak=30, club=0, caps=0)), 1)
        self.assertEqual(f(record(age=35, peak=30, club=0, caps=9)), 0)   # 35 <= 30+5
        self.assertEqual(f(record(age=36, peak=30, club=0, caps=9)), 1)   # 36 > 30+5
        # mutating RETIRE_PEAK_MARGIN (5 -> 4) flips age=33/peak=28 and fails this test
        self.assertEqual(f(record(age=33, peak=28, club=3, caps=9)), 0)   # 33 <= 28+5
        self.assertEqual(f(record(age=34, peak=28, club=3, caps=9)), 1)   # 34 > 28+5


class SeedTests(unittest.TestCase):
    """The variance question (notes.md section 3): the yearly path consumes no RNG."""

    def test_seed_is_not_consumed(self):
        # calls.tsv: 8208/80DA/7FDF/7FB1/7E4A/32EB/7F40 have no RNG callee — the prediction of
        # a continuing player is seed-independent. Mutating the predictor to consume `seed`
        # (a variance term) fails this test; the observed year-to-year variance of the records
        # (check_ageing.py's `observed variance` report) is the creation draw (+2, +3), which
        # the record itself carries.
        rec = record(age=29, peak=27, rating=0xC8)
        a = A.ageing_value(rec, 1, CLASS_TABLE, PROFILE_TABLE, 0)
        b = A.ageing_value(rec, 1, CLASS_TABLE, PROFILE_TABLE, 12345)
        self.assertEqual(a, b)

    def test_observed_variance_matches_the_records_curve(self):
        # The help file's "differ by year" (GOAL.HLP 327-332): two players of the same rating
        # and age differ per year ONLY through their creation draws (+2 peak, +3 rating) — the
        # actual variance the E014 records show. Same age, different peaks -> different deltas.
        r = record(age=29, peak=26, rating=0xC8)   # past his band: falls
        s = record(age=29, peak=29, rating=0xC8)   # inside his band: at the ceiling
        dr = A.ageing_value(r, 1, CLASS_TABLE, PROFILE_TABLE, 1)[A.ABILITY] - r[A.ABILITY]
        ds = A.ageing_value(s, 1, CLASS_TABLE, PROFILE_TABLE, 1)[A.ABILITY] - s[A.ABILITY]
        self.assertLess(dr, 0)
        self.assertEqual(ds, 0xC8 - A.compute_ability(29, 29, 0xC8))


class DerivedSkillTests(unittest.TestCase):
    """1771:3A06 through the year end (notes.md section 5; F015)."""

    def test_skills_scale_with_ability_only(self):
        # The loop writes +4 only, so all twelve engine skills move by the same integer formula
        # t * (ability + 1) div 32 with the SAME table values (3A51-3A74).
        rec = record(age=30, peak=27, rating=0xF0, profile=5, club=3)
        out = A.ageing_value(rec, 1, CLASS_TABLE, PROFILE_TABLE, 7)
        before, after = out["skills"]
        self.assertEqual(len(before), 12)
        expect_after = tuple(
            PROFILE_TABLE[12 * rec[0x05] + CLASS_TABLE[12 * rec[A.CLUB_POSITION] + e]]
            * (out[A.ABILITY] + 1) // A.SKILL_DIVISOR for e in range(12))
        self.assertEqual(after, expect_after)
        # a goalkeeper's keeping (element 0) is class 1 (F008): the profile row's first value
        gk = record(age=30, peak=30, rating=0xF0, club=0)
        self.assertEqual(CLASS_TABLE[0], 1)
        out_gk = A.ageing_value(gk, 1, CLASS_TABLE, PROFILE_TABLE, 7)
        gb, ga = out_gk["skills"]
        self.assertEqual(ga[0], PROFILE_TABLE[12 * gk[0x05] + 1]
                         * (out_gk[A.ABILITY] + 1) // 32)
        # 30 -> 31 stays inside the band 30..33: the ability holds at the ceiling and the
        # twelve skills do not move ...
        self.assertEqual(out_gk[A.ABILITY], gk[A.ABILITY])
        self.assertEqual(gb, ga)
        # ... while one year past the band (34 -> 35, k = 2) drops all twelve
        old = record(age=34, peak=30, rating=0xF0, club=0)
        b2, a2 = A.ageing_value(old, 1, CLASS_TABLE, PROFILE_TABLE, 7)["skills"]
        self.assertTrue(all(x >= y for x, y in zip(b2, a2)))
        self.assertTrue(any(x > y for x, y in zip(b2, a2)))


class TableConstantTests(unittest.TestCase):
    def test_tables_come_from_the_data_image(self):
        # DS:0E80 = 1B 1E and DS:110C = 19 1C (ds_2581_01.hex:123,143) — the creation bases the
        # notes cite; pinned so a hand-copied constant cannot drift from the image.
        self.assertEqual((DATA1[0x0E80], DATA1[0x0E81]), (0x1B, 0x1E))
        self.assertEqual((DATA1[0x110C], DATA1[0x110D]), (0x19, 0x1C))
        self.assertEqual((DATA1[0x118E], DATA1[0x118F]), (0x02, 0x05))


if __name__ == "__main__":
    unittest.main()
