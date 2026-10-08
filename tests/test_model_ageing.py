#!/usr/bin/env python3
"""Unit tests for runtime/model/ageing.py and the E014 checker (T28, Q013; E014).

Every fixture is a literal 20-byte record and every expected value a literal byte or a literal
offset (1 age, 2 peak, 3 rating, 4 ability, 5 profile, 7 club position, 8/9 caps, 0x11 the
scorer count), never the predictor's own offset constants — so a changed constant in
runtime/model/ageing.py cannot carry its fixtures with it (review R9). The continuing-player
fixtures are real pairs from the committed captures (runs/E014, the record, country and player
word named on each row): the expected aged record is the first capture's bytes with +1, +4 and
+0x11 taken from the second capture. Listing lines: experiments/E014-q013-ageing/notes.md.
The PR lists the in-place mutations run against these tests (Done-when 2).
Run: python3 -m unittest -v tests.test_model_ageing"""
import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
sys.path.insert(0, str(ROOT / "experiments" / "E014-q013-ageing"))
import ageing as A  # noqa: E402
import check_ageing as C  # noqa: E402


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

# (record, country, word, first capture, second capture): continuing players, every branch of
# 1771:32EB at the AGED age a = +1 + 1 against p = +2 — below by 1..6, the copy band 0..3,
# above by 4..5 — for outfield players and goalkeepers (+7 == 0).
CONTINUING = [
    ("r0005", 1, 13, "01161da1820b010100000000072020110000ff7f", "01171da1820b010100000000012020110000ff7f"),  # a-p = -6
    ("r0005", 2, 36, "02171dc19c09050500000000062020000000ff7f", "02181dc1a809050500000000012020000000ff7f"),  # -5
    ("r0005", 3, 60, "03161bceb40f0d0d000000001e2020000000ff7f", "03171bceb40f0d0d040001001c20200000004727"),  # -4
    ("r0005", 2, 27, "02171bc1a808070700000000122020000000ff7f", "02181bc1b408070700000000081a1a000000ff7f"),  # -3
    ("r0005", 1, 3, "011a1da1960c0202000000001e1414320000ff7f", "011b1da1960c020203000000161c1c320000ff7f"),   # -2
    ("r0006", 2, 32, "021c1fc1b4040000000000001c2020910000ff7f", "021d1fc1b4040000050000001b2020910000ff7f"),  # -2 gk
    ("r0005", 1, 6, "011b1da19602060600000000042020800000ff7f", "011c1da1a102060600000000022020800000ff7f"),   # -1
    ("r0006", 2, 32, "021d1fc1b4040000050000001b2020910000ff7f", "021e1fc1c10400000b000000111414910000ff7f"),  # -1 gk
    ("r0005", 2, 33, "021a1bc1c1090202000000001d1e1e320000ff7f", "021b1bc1c10902020c000000192020320000ff7f"),  # 0
    ("r0005", 3, 52, "031e1fcece0e0000000000001b2020110000ff7f", "031f1fcece0e0000030000000c20201100003700"),  # 0 gk
    ("r0005", 1, 8, "011b1ba1a1070808000000001e1414000000ff7f", "011c1ba1a10708080c000000172020000000ff7f"),   # 1
    ("r0005", 1, 5, "011a19a1a106050500000000132020000000ff7f", "011b19a1a10605050c0000000d1919000000ff7f"),   # 2
    ("r0005", 1, 17, "011f1da1a10c070700000000071212000000ff7f", "01201da1a10c070709000000052020000000ff7f"),  # 3
    ("r0005", 1, 1, "01201ea1a10a000000000000082020110000ff7f", "01211ea1a10a00000b000000022020110000ff7f"),   # 3 gk
    ("r0005", 1, 4, "011d1aa1a10b020200000000181717320000ff7f", "011e1aa1960b02020b000000101212320000ff7f"),   # 4
    ("r0006", 1, 12, "01201da1a10d000001000000011212110000ff7f", "01211da1960d000005000000022020110000ff7f"),  # 4 gk
    ("r0005", 1, 2, "011d19a1960f010100000000051212110000ff7f", "011e19a18c0f01010c000000011e1e110000ff7f"),   # 5
]

# (record, country, word, the retiree, its re-create): 7F40 fired on the aged record and 7E80
# replaced the player (the captures' bytes, as above).
REPLACED = [
    # caps clause: age 30 -> 31 > DS:110E[0] = 30, caps 0; peak 26: 31 > 31 is false
    ("r0005", 2, 29, "021e1ac1b403090900000000102020800000ff7f", "02181dc1a8050909000000000d2020800000ff7f"),
    # peak clause: age 30 -> 31 > 25 + 5, caps 12 (the caps clause closed)
    ("r0006", 1, 2, "011e19a18c0f01010c000000011e1e110000ff7f", "01191ca1960e010100000000171b1b110000ff7f"),
    # a goalkeeper (+7 = 0) by the peak clause: age 35 -> 36 > 30 + 5, caps 20
    ("r0006", 1, 1, "01231ea18c0a000014000000012020110000ff7f", "011c1e9b910e000000000000062020110000ff7f"),
]


def rec(hexstr, **edits):
    r = bytearray(bytes.fromhex(hexstr))
    for k, v in edits.items():
        r[int(k[1:], 16)] = v                 # edits like o01=30 (offset 0x01)
    return bytes(r)


# a literal outfield record: country 1, age 29, peak 27, rating 0xF0, ability 0xF0, profile 5,
# positions 3/3, caps 0, morale/fitness/energy 0x10, performance 0x7FFF
BASE = "011d1bf0f005030300000000101010000000ff7f"


class LiteralRecordTests(unittest.TestCase):
    def test_base_fixture_layout(self):
        r = bytes.fromhex(BASE)
        self.assertEqual(len(r), 20)
        self.assertEqual((r[1], r[2], r[3], r[4], r[7]), (29, 27, 0xF0, 0xF0, 3))


class CapturedPairTests(unittest.TestCase):
    """The yearly first pass 7FB1 -> 7E4A -> 32EB on real records (notes.md sections 2-3)."""

    def test_aged_record_matches_the_next_capture(self):
        for run, n, w, before, after in CONTINUING:
            b, a = bytes.fromhex(before), bytes.fromhex(after)
            want = bytearray(b)
            want[1], want[4], want[0x11] = a[1], a[4], 0       # 7E6F, 32EB, 7FD4 — literal offsets
            with self.subTest(run=run, country=n, word=w):
                self.assertEqual(A.aged_record(b).hex(), bytes(want).hex())
                out = A.ageing_value(b, 0, None, None, 0)
                self.assertEqual((out[1], out[4], out[0x11]), (a[1], a[4], 0))
                # the year end's caps word is the second capture's (r0005 1/17 won 9 caps
                # in the year, closing the caps clause at aged age 32)
                yc = bytearray(b)
                yc[8], yc[9] = a[8], a[9]
                self.assertEqual(A.ageing_value(bytes(yc), 0, None, None, 0)["retires"], 0)

    def test_literal_ability_bytes_of_the_captures(self):
        # The same pairs as literal (aged age, peak, rating) -> ability: 0xa1 = 161 at p - 1 is
        # the five-age plateau's lower end (k = 0 from the idiv 2 at 33A7, notes.md section 3).
        rows = [(0x17, 0x1D, 0x82, 0x82 * 13 // 16), (0x18, 0x1D, 0x9C, 0x9C * 14 // 16),
                (0x1C, 0x1D, 0xA1, 0xA1), (0x1B, 0x1B, 0xC1, 0xC1), (0x20, 0x1D, 0xA1, 0xA1),
                (0x1E, 0x1A, 0xA1, 0x96), (0x1E, 0x19, 0xA1, 0x8C)]
        for age, peak, rating, ability in rows:
            self.assertEqual(A.compute_ability(age, peak, rating), ability, (age, peak, rating))


class BandRuleTests(unittest.TestCase):
    """compute_ability 1771:32EB, seg_1771_05.asm:283-370 (notes.md section 3)."""

    def test_the_whole_curve_literal(self):
        # p = 27, r = 240, ages 20..47; below: k = (p - a) idiv 2; the copy band 27..30; above:
        # k = a - 30; factor 16 - k; 46 gives k = 16 -> 0; 47 wraps (k = 17, factor 0xFFFF).
        want = [195, 195, 210, 210, 225, 225, 240, 240, 240, 240, 240, 225, 210, 195, 180, 165,
                150, 135, 120, 105, 90, 75, 60, 45, 30, 15, 0, 241]
        self.assertEqual([A.compute_ability(a, 27, 240) for a in range(20, 48)], want)

    def test_five_age_maximum_four_age_copy(self):
        # The maximum r holds at p-1..p+3 (five ages); the copy branch (333A) is p..p+3 and
        # p-1 reaches r through k = 0. A rating with a remainder shows the below branch's
        # arithmetic at p-2: 0xA1 * 15 // 16 = 150.
        self.assertEqual([A.compute_ability(a, 29, 0xA1) for a in range(26, 34)],
                         [150, 150, 161, 161, 161, 161, 161, 150])

    def test_factor_wrap_edge(self):
        # 3386/33AE: factor = 0x10 - k is a 16-bit WORD — k = 17 gives 0xFFFF; 33B6 mul keeps
        # the low product (33B9 xor dx, dx): (240 * 0xFFFF) mod 65536 = 65296, div 16 = 4081 =
        # 0x0FF1; 33C3 stores al = 0xF1.
        self.assertEqual(A.compute_ability(47, 27, 240), 0xF1)
        self.assertEqual(A.compute_ability(48, 27, 240), 0xE2)   # 65536-480 = 65056 // 16 = 0x0FE2

    def test_rating_byte_operand(self):
        # 3344: the rating is one byte, zero-extended (xor ah, ah at 3348)
        self.assertEqual(A.compute_ability(31, 27, 0x1F0), 225)
        self.assertEqual(A.compute_ability(28, 27, 0x1F0), 0xF0)   # the copy branch (3333)

    def test_age_byte_wrap(self):
        # 7E6F: inc byte ptr es:[di + 1] — a byte increment, wraps 255 -> 0.
        out = A.year_end_bytes(1, rec(BASE, o01=255))
        self.assertEqual(out[1], 0)


class YearEndBytesTests(unittest.TestCase):
    """The loop's per-player writes: 7FB1/7E4A (notes.md section 2)."""

    def test_writes_exactly_three_bytes(self):
        out = A.year_end_bytes(1, rec(BASE, o11=9))
        self.assertEqual(sorted(k for k in out if isinstance(k, int)), [0x01, 0x04, 0x11])
        self.assertEqual((out[1], out[4], out[0x11]), (30, 0xF0, 0))
        self.assertEqual(A.aged_record(rec(BASE, o11=9)).hex(),
                         "011e1bf0f005030300000000101010000000ff7f")

    def test_player_zero_skips_the_age(self):
        # 7E64-7E6A: 7E4A returns without the increment for player 0; 7FB1's +0x11 write (7FD4)
        # is unconditional.
        self.assertEqual(A.year_end_bytes(0, rec(BASE)), {0x11: 0})


class RetirementTests(unittest.TestCase):
    """1771:7F40 on the AGED record (seg_1771_11.asm:950-1000, 7FDF's second pass :1098)."""

    def test_data_image_constants(self):
        # DS:110E = 1E 21, DS:110C = 19 1C, DS:0E80 = 1B 1E (ds_2581_01.hex:123,143)
        self.assertEqual((DATA1[0x110E], DATA1[0x110F]), (30, 33))
        self.assertEqual((DATA1[0x110C], DATA1[0x110D]), (25, 28))
        self.assertEqual((DATA1[0x0E80], DATA1[0x0E81]), (27, 30))
        self.assertEqual((DATA1[0x118E], DATA1[0x118F]), (0x02, 0x05))

    def test_flag_is_on_the_aged_record(self):
        # R5: age 32, peak 27, caps 10 ages to 33 > 27 + 5 -> retires; the record as it stood
        # (32 > 32 false) would not.
        r = rec(BASE, o01=32, o08=10)
        self.assertEqual(A.retirement_flag(r), 0)
        self.assertEqual(A.ageing_value(r, 0, None, None, 0)["retires"], 1)
        self.assertEqual(A.year_end_bytes(1, r)["retires"], 1)

    def test_peak_clause_boundary(self):
        f = lambda r: A.ageing_value(r, 0, None, None, 0)["retires"]
        self.assertEqual(f(rec(BASE, o01=31, o08=10)), 0)   # aged 32 = 27 + 5: jg not taken
        self.assertEqual(f(rec(BASE, o01=32, o08=10)), 1)   # aged 33 > 32
        self.assertEqual(f(rec(BASE, o01=32, o02=28, o08=10)), 0)   # 33 = 28 + 5
        self.assertEqual(f(rec(BASE, o01=33, o02=28, o08=10)), 1)

    def test_caps_clause_boundary(self):
        f = lambda r: A.ageing_value(r, 0, None, None, 0)["retires"]
        # outfield (+7 = 3): DS:110E[0] = 30 < aged age, caps 0; peak 27 keeps the peak clause off
        self.assertEqual(f(rec(BASE, o01=29)), 0)            # aged 30: 30 < 30 false (jae)
        self.assertEqual(f(rec(BASE, o01=30)), 1)            # aged 31
        self.assertEqual(f(rec(BASE, o01=30, o08=1)), 0)     # caps 1
        self.assertEqual(f(rec(BASE, o01=30, o09=1)), 0)     # caps 0x0100: the WORD at +8
        # goalkeeper (+7 = 0): DS:110E[1] = 33; peak 30 keeps the peak clause off to 35
        gk = rec(BASE, o02=30, o07=0)
        self.assertEqual(f(rec(gk.hex(), o01=32)), 0)        # aged 33: 33 < 33 false
        self.assertEqual(f(rec(gk.hex(), o01=33)), 1)        # aged 34
        # the club position byte decides, not +6 (7F5D: es:[di + 7])
        self.assertEqual(f(rec(BASE, o01=31, o06=0, o02=30)), 1)   # +6 = 0, +7 = 3: limit 30

    def test_captured_retirements_fire(self):
        for run, n, w, old, new in REPLACED:
            with self.subTest(run=run, country=n, word=w):
                self.assertEqual(A.ageing_value(bytes.fromhex(old), 0, None, None, 0)["retires"], 1)


class RecreateTests(unittest.TestCase):
    """1771:7E80's deterministic part (seg_1771_11.asm:871-948)."""

    def test_outfield_constraints_literal(self):
        c = A.recreate_constraints(bytes.fromhex(REPLACED[1][3]))       # +0 = 1, +7 = 1
        self.assertEqual(c["exact"], {0: 1, 7: 1, 8: 0, 9: 0, 10: 0, 11: 0, 16: 0, 17: 0,
                                      18: 0xFF, 19: 0x7F})
        self.assertEqual(c["range"], {1: (20, 30), 2: (25, 29), 5: (1, 16)})

    def test_goalkeeper_constraints_literal(self):
        c = A.recreate_constraints(bytes.fromhex(REPLACED[2][3]))       # +7 = 0
        self.assertEqual(c["exact"][7], 0)
        self.assertEqual(c["range"], {1: (23, 33), 2: (28, 32), 5: (1, 16)})

    def test_captured_recreates_satisfy_them(self):
        for run, n, w, old, new in REPLACED:
            o, r = bytes.fromhex(old), bytes.fromhex(new)
            c = A.recreate_constraints(o)
            with self.subTest(run=run, country=n, word=w):
                self.assertTrue(all(r[k] == v for k, v in c["exact"].items()))
                self.assertTrue(all(lo <= r[k] <= hi for k, (lo, hi) in c["range"].items()))
                self.assertEqual(A.compute_ability(r[1], r[2], r[3]), r[4])


class SeedTests(unittest.TestCase):
    """The continuing-player update consumes no RNG (notes.md section 3)."""

    def test_seed_is_not_consumed(self):
        r = rec(BASE, o01=31)
        outs = [A.ageing_value(r, 1, CLASS_TABLE, PROFILE_TABLE, s) for s in (0, 1, 12345, 2**31)]
        self.assertTrue(all(o == outs[0] for o in outs))

    def test_observed_variance_is_the_records_own(self):
        # Two captured players of one year differ in their +4 deltas only through +1/+2/+3:
        # r0005 1/4 (above the band) fell 0xa1 -> 0x96, r0005 1/8 (inside) held 0xa1.
        d = []
        for row in (CONTINUING[14], CONTINUING[10]):
            b, a = bytes.fromhex(row[3]), bytes.fromhex(row[4])
            d.append(A.ageing_value(b, 0, None, None, 99)[4] - b[4])
            self.assertEqual(d[-1], a[4] - b[4])
        self.assertEqual(d, [-11, 0])


class DerivedSkillTests(unittest.TestCase):
    """1771:3A06 through the year end (notes.md section 5; F015)."""

    def test_skills_literal_formula(self):
        r = rec(BASE, o01=31)                       # aged 32: k = 2, 0xF0 -> 0xD2
        before, after = A.ageing_value(r, 1, CLASS_TABLE, PROFILE_TABLE, 7)["skills"]
        want = lambda ab: tuple(PROFILE_TABLE[12 * 5 + CLASS_TABLE[12 * 3 + e]] * (ab + 1) // 32
                                for e in range(12))
        self.assertEqual(before, want(0xF0))
        self.assertEqual(after, want(0xD2))
        self.assertNotEqual(before, after)

    def test_goalkeeper_keeping(self):
        g = rec(BASE, o07=0, o02=30)
        self.assertEqual(CLASS_TABLE[0], 1)        # a goalkeeper's element 0 is class 1 (F008)
        b, a = A.ageing_value(g, 1, CLASS_TABLE, PROFILE_TABLE, 7)["skills"]
        self.assertEqual(a[0], PROFILE_TABLE[12 * 5 + 1] * (0xF0 + 1) // 32)


def load_pair(run="r0005"):
    record = json.loads((ROOT / "runs" / "E014" / f"E014-{run}.json").read_text())
    caps = C.captures(record)
    return copy.deepcopy(caps[0]), copy.deepcopy(caps[1])


def player(cap, n, w):
    for c in cap["countries"]:
        if c["n"] == n:
            for p in c["players"]:
                if p["w"] == w:
                    return c, p
    raise KeyError((n, w))


class CheckerTests(unittest.TestCase):
    """experiments/E014-q013-ageing/check_ageing.py (review R1-R4)."""

    def check(self, before, after):
        mism = []
        n = C.check_pair(before, after, mism)
        return n, mism

    def test_committed_pair_matches(self):
        b, a = load_pair()
        n, mism = self.check(b, a)
        self.assertEqual((n, mism), (60, []))

    def test_identity_not_name(self):
        # R1: two players with one name; the second is aged right, the first left unaged.
        b, a = load_pair()
        for cap in (b, a):
            _, p1 = player(cap, 1, 13)
            _, p2 = player(cap, 1, 6)
            p1["surname"], p1["initial"] = p2["surname"], p2["initial"]
        _, q = player(a, 1, 13)
        q["rec"] = player(b, 1, 13)[1]["rec"]          # player 13 not aged
        n, mism = self.check(b, a)
        self.assertEqual(n, 60)
        self.assertTrue(any("player 13" in m for m in mism), mism)

    def test_duplicate_country_cannot_hide_a_player(self):
        # review round 2 R1: country 2 replaced by a copy of country 1 in both captures; the
        # first copy's player 13 is left unaged, the second copy aged right. A map keyed by
        # country would keep only the last copy and see nothing wrong.
        import copy
        b, a = load_pair()
        for cap in (b, a):
            cap["countries"][1] = copy.deepcopy(cap["countries"][0])
        _, q = player({"countries": [a["countries"][0]]}, 1, 13)
        q["rec"] = player(b, 1, 13)[1]["rec"]          # the first copy's player 13 not aged
        n, mism = self.check(b, a)
        self.assertEqual(n, 0)
        self.assertTrue(any("not 3 distinct" in m for m in mism), mism)

    def test_a_missing_country_is_a_mismatch(self):
        # review round 2 R1: one country captured instead of three
        b, a = load_pair()
        for cap in (b, a):
            cap["countries"] = cap["countries"][:1]
        n, mism = self.check(b, a)
        self.assertTrue(any("not 3 distinct" in m for m in mism), mism)

    def test_disappearance_needs_a_replacement(self):
        # R2: the retiree r0005 2/29 vanishes from the second capture (record and squad word).
        b, a = load_pair()
        c, p = player(a, 2, 29)
        c["players"].remove(p)
        c["squad"].remove(29)
        n, mism = self.check(b, a)
        self.assertTrue(mism)
        # and an empty second capture of a country
        b, a = load_pair()
        a["countries"][1]["players"] = []
        n, mism = self.check(b, a)
        self.assertTrue(any("player 29" in m for m in mism), mism)

    def test_replacement_keeps_club_position(self):
        # R3: the re-create of r0005 2/29 with +7 changed (old +7 = 9 -> 0)
        b, a = load_pair()
        _, p = player(a, 2, 29)
        r = bytearray(bytes.fromhex(p["rec"]))
        r[7] = 0
        p["rec"] = r.hex()
        n, mism = self.check(b, a)
        self.assertTrue(any("player 29" in m and "+0x07" in m for m in mism), mism)

    def test_replacement_invariants(self):
        for off, val in ((0, 3), (8, 1), (10, 1), (0x10, 1), (0x11, 1), (1, 40), (2, 20), (5, 0),
                         (4, 0)):
            b, a = load_pair()
            _, p = player(a, 2, 29)
            r = bytearray(bytes.fromhex(p["rec"]))
            r[off] = val
            p["rec"] = r.hex()
            with self.subTest(offset=off):
                self.assertTrue(self.check(b, a)[1])

    def test_continuing_byte_changes_fail(self):
        for off in (0, 1, 2, 3, 4, 5, 7, 0x11):
            b, a = load_pair()
            _, p = player(a, 1, 13)
            r = bytearray(bytes.fromhex(p["rec"]))
            r[off] ^= 0x01
            p["rec"] = r.hex()
            with self.subTest(offset=off):
                self.assertTrue(self.check(b, a)[1])

    def test_unflagged_player_replaced_fails(self):
        # r0005 1/13 (age 22, caps 0 but far from every clause) re-created in the second capture
        b, a = load_pair()
        _, p = player(a, 1, 13)
        p["rec"] = "01191ca1960e010100000000171b1b000000ff7f"
        self.assertTrue(self.check(b, a)[1])

    def test_flagged_player_continuing_fails(self):
        # r0005 2/29 retires (caps clause, caps 0): continuing with caps 0 is a mismatch
        b, a = load_pair()
        _, p = player(a, 2, 29)
        _, q = player(b, 2, 29)
        p["rec"], p["initial"] = A.aged_record(bytes.fromhex(q["rec"])).hex(), q["initial"]
        mism = self.check(b, a)[1]
        self.assertTrue(any("continued with caps 0" in m for m in mism), mism)

    def test_managed_country_and_two_ageings_fail(self):
        b, a = load_pair()
        a["countries"][0]["manager_byte"] = 0x81
        self.assertTrue(self.check(b, a)[1])
        b, a = load_pair()
        b["countries"][0]["manager_byte"] = 0x80        # 0B77: > 0x80 is managed, 0x80 is not
        self.assertEqual(self.check(b, a)[1], [])
        b, a = load_pair()
        a["state"]["stage"] = 5                          # 2 -> 5 enters 3 and 5
        self.assertTrue(self.check(b, a)[1])

    def test_ageings_between(self):
        self.assertEqual([C.ageings_between(s, t) for s, t in
                          ((2, 3), (3, 5), (5, 7), (7, 2), (8, 2), (3, 4), (2, 5), (4, 5))],
                         [1, 1, 1, 1, 1, 0, 2, 1])
        self.assertIsNone(C.ageings_between(1, 2))
        self.assertIsNone(C.ageings_between(2, 9))

    def test_tables_must_not_change(self):
        b, a = load_pair()
        a["tables"] = {"changed": True}
        self.assertTrue(self.check(b, a)[1])

    def test_captured_records_are_the_squad(self):
        # a record for a word outside the squad, or two records for one word: coverage
        b, a = load_pair()
        extra = dict(a["countries"][0]["players"][0], w=999)
        a["countries"][0]["players"].append(extra)
        self.assertTrue(any("are not the squad" in m for m in self.check(b, a)[1]))
        b, a = load_pair()
        dup = dict(b["countries"][0]["players"][0])
        b["countries"][0]["players"].append(dup)
        self.assertTrue(any("are not the squad" in m for m in self.check(b, a)[1]))

    def test_squad_is_twenty_distinct_words(self):
        # a squad of 19 (the word and its record gone from both captures), or a 0 word
        b, a = load_pair()
        for cap in (b, a):
            c, p = player(cap, 1, 13)
            c["players"].remove(p)
            c["squad"].remove(13)
        self.assertTrue(any("not 20 distinct" in m for m in self.check(b, a)[1]))
        b, a = load_pair()
        for cap in (b, a):
            c = cap["countries"][0]
            c["squad"][c["squad"].index(13)] = 0
            player(cap, 1, 13)[1]["w"] = 0
        self.assertTrue(any("not 20 distinct" in m for m in self.check(b, a)[1]))

    def test_check_runs_guards(self):
        # each guard of R4 on its own: no record; records with no pair
        total, mism, *_ = C.check_runs([])
        self.assertEqual(total, 0)
        self.assertTrue(any("no E014 record" in m for m in mism), mism)
        total, mism, *_ = C.check_runs([ROOT / "runs" / "E014" / "E014-r0001.json"])
        self.assertEqual(mism, ["no comparison was made: nothing corroborated"])
        # and main's exit, even if check_runs reported nothing for zero comparisons
        saved = C.check_runs
        try:
            C.check_runs = lambda paths: (0, [], 0, [], [])
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(C.main(["--runs", str(ROOT / "runs" / "E014")]), 1)
        finally:
            C.check_runs = saved

    def test_no_evidence_is_a_failure(self):
        # R4: no records, a completed record with one capture, and only aborted single captures
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(C.main(["--runs", d]), 1)
            single = json.loads((ROOT / "runs" / "E014" / "E014-r0001.json").read_text())
            Path(d, "E014-r0001.json").write_text(json.dumps(single))
            self.assertEqual(C.main(["--runs", d]), 1)          # aborted only: 0 comparisons
            single["status"] = "completed"
            Path(d, "E014-r0001.json").write_text(json.dumps(single))
            total, mism, pairs, _, _ = C.check_runs([Path(d, "E014-r0001.json")])
            self.assertTrue(any("completed" in m for m in mism), mism)

    def test_one_rating_per_country(self):
        # r0005 country 2 re-creates 29, 30, 32, 35 in one 7FDF call: one +3 (country_rating +
        # 0x7F). Give 30 another rating (and the +4 its own bytes give) -> a mismatch.
        b, a = load_pair()
        _, p = player(a, 2, 30)
        r = bytearray(bytes.fromhex(p["rec"]))
        self.assertEqual(r[3], 0xC1)
        r[3] = 0xC2
        r[4] = A.compute_ability(r[1], r[2], r[3])
        p["rec"] = r.hex()
        self.assertTrue(any("different +3" in m for m in self.check(b, a)[1]))

    def test_caps_cannot_fall_and_names_hold(self):
        b, a = load_pair("r0006")
        _, p = player(a, 1, 12)                    # caps 1 -> 5 in the first r0006 pair
        r = bytearray(bytes.fromhex(p["rec"]))
        self.assertEqual((r[8], player(b, 1, 12)[1]["rec"][16:18]), (5, "01"))
        r[8] = 0
        p["rec"] = r.hex()
        self.assertTrue(any("caps fell" in m for m in self.check(b, a)[1]))
        for field in ("surname", "initial"):        # a continuing player keeps both
            b, a = load_pair()
            _, p = player(a, 1, 13)
            p[field] = "00" + p[field][2:]
            with self.subTest(field=field):
                self.assertTrue(self.check(b, a)[1])
        b, a = load_pair()                          # a re-create keeps the surname (7F2D: initial)
        _, p = player(a, 2, 29)
        p["surname"] = "00" + p["surname"][2:]
        self.assertTrue(self.check(b, a)[1])
        b, a = load_pair()
        _, p = player(a, 2, 29)
        p["initial"] = "41"
        self.assertEqual(self.check(b, a)[1], [])

    def test_retiree_never_passes_as_recreate(self):
        # check_ageing.replacement_errors' comment: when 7F40 fires (caps 0 or 1, every age,
        # both position classes, every peak roll_peak_age can draw), the continuing prediction
        # is not a valid re-create — its aged age lies above DS:110C[gk] + 5.
        names = ("0a", "41")
        for club, peaks in ((3, range(25, 30)), (0, range(28, 33))):
            for peak in peaks:
                for age in range(0, 255):
                    for caps in (0, 1):
                        r = rec("011d1bf0f005030300000000000000000000ff7f", o01=age, o02=peak,
                                o07=club, o08=caps)
                        if not A.ageing_value(r, 0, None, None, 0)["retires"]:
                            continue
                        aged = A.aged_record(r)
                        errs = C.replacement_errors(r, aged, names, names)
                        self.assertTrue(any("+0x01" in e for e in errs), (club, peak, age, caps))
        # and the edge itself: an outfield retiree's aged age is 31 at the least, one above 30
        self.assertEqual(min(a + 1 for a in range(0, 255) for pk in range(25, 30)
                             if A.ageing_value(rec(BASE, o01=a, o02=pk, o08=0), 0, None, None, 0)
                             ["retires"]), 31)

    def test_committed_records(self):
        total, mism, pairs, deltas, notes = C.check_runs(sorted((ROOT / "runs" / "E014").glob("E014-r*.json")))
        self.assertEqual((total, mism, pairs, len(notes)), (300, [], 5, 4))


if __name__ == "__main__":
    unittest.main()
