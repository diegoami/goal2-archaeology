#!/usr/bin/env python3
"""Unit tests for runtime/model/recreate.py and experiments/E016-q014-retirement/check_recreate.py
(T30, Q014; F017).

Fixtures are literal 20-byte records, and every expected value is a literal byte at a literal
offset (1 age, 2 peak, 3 rating, 4 ability, 5 profile, 6 position, 7 club position, 8..0xB caps
and goals, 0xC morale, 0xD fitness, 0xE energy, 0xF tactics, 0x10 status, 0x11 scorer count,
0x12/0x13 performance) — never the model's own offset or range constants — so a changed constant
cannot carry its expectation with it (T28's R9). The exact fixtures are records the game wrote:
the E006 new games (F007) and the E014 year ends (F016), named on each test; the hand-computed
ones show their arithmetic. experiments/E016-q014-retirement/mutation_sweep.py changes every
constant of the model in place and runs this file; its committed output lists the results.

Run: python3 -m unittest -v tests.test_model_recreate
"""
import copy
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
sys.path.insert(0, str(ROOT / "experiments" / "E014-q013-ageing"))
sys.path.insert(0, str(ROOT / "experiments" / "E016-q014-retirement"))
import ageing as A            # noqa: E402 — F016 (retirement_flag, compute_ability)
import recreate as R          # noqa: E402 — the model under test
import check_ageing as C      # noqa: E402 — capture parsing
import check_recreate as K    # noqa: E402 — the checker under test


def h(s):
    return bytes.fromhex(s)


def e006_arrays():
    """The player and country arrays of E006-r0001 at the main screen of a new game (F007)."""
    r = json.loads((ROOT / "runs" / "E006" / "E006-r0001.json").read_text())
    pa = ca = None
    for o in r["observations"]:
        f = o.get("field", "")
        if f.startswith("player array"):
            pa = h(o["value"])
        if f.startswith("country array"):
            ca = h(o["value"])
    return pa, ca


def e014_captures(run):
    return C.captures(json.loads((ROOT / "runs" / "E014" / f"E014-{run}.json").read_text()))


class GeneratorTests(unittest.TestCase):
    """214B:0688 through 214B:06B1 (seg_214B_01.asm:871-911)."""

    def test_162_steps_from_ten_oclock(self):
        # F004/F007: DS:7B62 at the main screen is the word 162 steps from hour*256 + minute;
        # at 10:00 it read 0xee42 (E006, three games)
        w = 0x0A00
        for _ in range(162):
            w = R.lcg_step(w)
        self.assertEqual(w, 0xEE42)

    def test_draw_literals(self):
        # 0 -> 0x1B0F = 6927; 6927 * 6 >> 16 = 0, + 1
        self.assertEqual(R.draw(0x0000, 6), (1, 0x1B0F))
        self.assertEqual(R.draw(0x1234, 21), (7, 0x5373))
        self.assertEqual(R.draw(0xFDF6, 16), (14, 0xD5AD))


class CountryRatingTests(unittest.TestCase):
    """1771:10E7 (seg_1771_02.asm:697-738)."""

    def test_e006_countries(self):
        # country 1: +0x2C 1, +0x2A 0x1c, +0x2B 0x50: (4 * 5 + 49) / 2 = 34, its players' +3 0xa1
        self.assertEqual(R.country_rating(1, 0x1C, 0x50), 34)
        self.assertEqual(R.country_rating(1, 0x1B, 0x14), 66)     # country 2, +3 0xc1
        self.assertEqual(R.country_rating(4, 0x11, 0x53), 31)     # country 128, +3 0x9e
        self.assertEqual(R.rating_of((1, 0x1C, 0x50)), 34)
        rec = bytearray(0xBF)
        rec[0x2C], rec[0x2A], rec[0x2B] = 4, 0x11, 0x53
        self.assertEqual(R.rating_of(bytes(rec)), 31)

    def test_domain_edges(self):
        self.assertEqual(R.country_rating(1, 1, 1), 128)          # (4 * 32 + 128) / 2
        self.assertEqual(R.country_rating(4, 32, 128), 1)         # (1 * 1 + 1) / 2
        self.assertEqual(R.country_rating(4, 32, 127), 1)         # 3 idiv 2 = 1

    def test_signed_divide_truncates_toward_zero(self):
        # (5 - 6) * (33 - 1) + (129 - 128) = -31; idiv 2 = -15 (a floor would give -16)
        self.assertEqual(R.country_rating(6, 1, 128), -15)

    def test_better_rank_raises_the_rating(self):
        self.assertGreater(R.country_rating(2, 3, 10), R.country_rating(2, 4, 10))   # 104 > 102
        self.assertGreater(R.country_rating(2, 3, 10), R.country_rating(2, 3, 12))   # 104 > 103


class TacticsAndFitnessTests(unittest.TestCase):
    """1771:3431/33CD/2FFB and 1771:3558 (seg_1771_05.asm)."""

    def test_hardness_edge(self):
        # hardness = +5 - (+3 and 1): 4 - 1 = 3 -> 33CD; 5 - 1 = 4 -> not; 4 - 0 = 4 -> not
        self.assertEqual(R.tactics_bits(h("00000081000409090000000000000000000000ff")), (0x80, 0x08))
        self.assertEqual(R.tactics_bits(h("00000081000509090000000000000000000000ff")), (0x00, 0x00))
        self.assertEqual(R.tactics_bits(h("00000080000409090000000000000000000000ff")), (0x00, 0x00))

    def test_positions(self):
        for pos, want in ((0, 0x11), (1, 0x11), (3, 0x11), (4, 0x11), (5, 0x00), (6, 0x00),
                          (13, 0x00)):
            r = bytearray(20)
            r[3], r[5], r[6] = 0x80, 9, pos
            self.assertEqual(R.tactics_bits(bytes(r)), (want, 0x00), pos)

    def test_centre_back_profile_edge(self):
        r = bytearray(20)
        r[3], r[6] = 0x80, 2
        r[5] = 13
        self.assertEqual(R.tactics_bits(bytes(r)), (0x32, 0x00))   # elements 5, 6, 2
        r[5] = 14
        self.assertEqual(R.tactics_bits(bytes(r)), (0x22, 0x00))   # elements 6, 2

    def test_computer_branch(self):
        old = h("01241b0000000000000000000000000000000000")    # 36 > 27 + 4: T = 13
        # draw(0, 26): 6927 * 26 >> 16 = 2 -> 3; 13 + 3 = 16
        self.assertEqual(R.fitness(old, False, 0x0000), (16, 16, 0x1B0F))
        young = h("01141b0000000000000000000000000000000000")  # 20 <= 31: T = 16
        self.assertEqual(R.fitness(young, False, 0x0001), (32, 32, 0x95CC))   # capped at 0x20
        edge = h("011f1b0000000000000000000000000000000000")   # 31 = 27 + 4: still T = 16
        self.assertEqual(R.fitness(edge, False, 0x0000)[0], 20)     # draw(0, 32) = 4: 16 + 4 (T 13: 16)

    def test_managed_branch(self):
        old = h("01241b0000000000000000000000000000000000")
        # a = draw(0, 14) = 2; b = draw(0x1b0f, 39) = 10 (15138 * 39 >> 16 = 9); 13 + 10 - 2
        self.assertEqual(R.fitness(old, True, 0x0000), (21, 21, 0x3B22))

    def test_managed_floor_visits_zero(self):
        young = h("01141b0000000000000000000000000000000000")
        # a = 17, b = 1: 16 + 1 - 17 = 0 -> energy 0, fitness floored to 1 (363C-3646)
        self.assertEqual(R.fitness(young, True, 0x0237), (1, 0, 0x0391))

    def test_initial_letters(self):
        self.assertEqual(R.initial(0x0004)[0], ord("A"))
        self.assertEqual(R.initial(0x0006)[0], ord("W"))
        seen = {R.initial(w)[0] for w in range(0x10000)}
        self.assertEqual(seen, set(b"ABCDEFGHIJKLMNOPRSTVW"))


class NewGameTests(unittest.TestCase):
    """1771:97CC and 1771:98C4 against the E006-r0001 new game (F007)."""

    @classmethod
    def setUpClass(cls):
        cls.pa, cls.ca = e006_arrays()

    def country(self, c):
        cr = self.ca[0xBF * c: 0xBF * (c + 1)]
        squad = [cr[2 * i] | cr[2 * i + 1] << 8 for i in range(20)]
        return cr, squad, [self.pa[20 * p: 20 * p + 20] for p in squad]

    def test_country_one_literal(self):
        cr, squad, recs = self.country(1)
        self.assertEqual(squad[:3], [1, 2, 3])
        made, _ = R.new_game_squad(1, 34, [0, 1, 2] + [r[7] for r in recs[3:]])
        self.assertEqual(made[0], h("01201ea1a10a000000000000082020110000ff7f"))
        self.assertEqual(made[1], h("011d19a1960f010100000000051212110000ff7f"))
        self.assertEqual(made[2], h("011a1da1960c0202000000001e1414320000ff7f"))

    def test_every_squad_player(self):
        n = 0
        for c in range(1, 129):
            cr, squad, recs = self.country(c)
            made, _ = R.new_game_squad(c, R.rating_of(cr), [r[7] for r in recs])
            for slot in range(20):
                self.assertEqual(made[slot], recs[slot], (c, slot + 1))
                n += 1
        self.assertEqual(n, 2560)

    def test_managed_pool(self):
        # country 7 is managed (+0x2E 0x81); 98C4 starts one draw after 97CC(128) ends (the
        # manager's initial, 1771:09A0 -> 1771:0000); its 80 records are players 0xA01..0xA50
        _, w = R.new_game_squad(128, 0, [0] * 20)
        cr, squad, recs = self.country(7)
        self.assertEqual(cr[0x2E], 0x81)
        pool, _ = R.managed_pool(R.lcg_step(w), 7, R.rating_of(cr), [r[7] for r in recs])
        self.assertEqual(len(pool), 80)
        self.assertEqual(pool[0], h("071d20e2d3100000000000000f1d1d110000ff7f"))
        for i, made in enumerate(pool):
            self.assertEqual(made, self.pa[20 * (0xA01 + i): 20 * (0xA02 + i)], i)

    def test_pool_rating_draw(self):
        # flag 0: +3 = 40 + 0x7F - 10 - rand(10); position 5, managed fitness
        made, w = R.make_player(bytes(20), 0, 5, 7, 40, True, 0x18BD)
        self.assertEqual(made, h("071e1b9b9b080505000000001c1919000000ff7f"))
        self.assertEqual(w, 0x3A80)


# E014-r0006, captures 0 -> 1, country 1: the three re-creates in slot order (words 2, 7, 20)
# from the RNG word 0xfdf6 at 80DA's entry (check_recreate recovers it; 1 of 65536 words)
R0006_C1 = (
    # (retiree as the second pass saw it: the first capture's record aged, +1 + 1, new record, initial)
    (h("011f19a18c0f01010c000000011e1e110000ff7f"), h("01191ca1960e010100000000171b1b110000ff7f"), 0x4E),
    (h("01221ca18c03070703000000092020800000ff7f"), h("011b1aa1a105070700000000162020800000ff7f"), 0x56),
    (h("01211ba18c0b0d0d08000000142020000000ff7f"), h("01181ca18c060d0d000000001b1212000000ff7f"), 0x4D),
)


class RecreateExactTests(unittest.TestCase):
    """1771:7E80 (seg_1771_11.asm:872-947) exactly, against E014-r0006's year end."""

    def test_three_recreates_of_one_country(self):
        w = 0xFDF6
        for old, new, ini in R0006_C1:
            got, gi, w = R.recreate(old, 34, w)
            self.assertEqual(got, new)
            self.assertEqual(gi, ini)

    def test_ten_draws_each(self):
        w = 0xFDF6
        for _ in range(10):
            w = R.lcg_step(w)
        self.assertEqual(R.recreate(R0006_C1[0][0], 34, 0xFDF6)[2], w)

    def test_carries_position_tactics_and_scorer_count(self):
        old = h("01221ca18c03030703000500092020c50407ff7f")   # +6 3 (moved), goals 5, +0xF c5, +0x10 4, +0x11 7
        got, _, _ = R.recreate(old, 34, 0xFDF6)
        self.assertEqual(got[6], 0x03)       # 7F36 restores the old +6
        self.assertEqual(got[7], 0x07)
        self.assertEqual(got[0x0F], 0xC5)    # position 7, hardness >= 4: no bit set or cleared
        self.assertEqual((got[8], got[9], got[0x0A], got[0x0B]), (0, 0, 0, 0))   # 7F09, 7F12
        self.assertEqual(got[0x10], 0x00)    # 7F19
        self.assertEqual(got[0x11], 0x07)    # nothing in 7E80's callee set writes +0x11

    def test_goalkeeper_bases(self):
        # +7 = 0: +1 base 28 (DS:110D), +2 base 30 (DS:0E81), make_player age base 31 (DS:118B)
        old = h("01231ea18c0a000014000000012020110000ff7f")
        got, gi, w = R.recreate(old, 34, 0x0000)
        # +5: draw(0, 16) = 2; +2: 30 + 2 - 1 = 31 (a = draw(0x1e54, 3) = 1, b = 2); +4: 27 is
        # below 31: k = 2, 0xa1 * 14 / 16 = 0x8c; +0xF: keeper (0x11) and hardness 2 - 1 < 4
        self.assertEqual(got, h("011b1fa18c020000000000001d2020910000ff7f"))
        self.assertEqual((gi, w), (0x4E, 0xA14A))


class ManagedReplacementTests(unittest.TestCase):
    """000E:54F0 (seg_000E_07.asm:84-283)."""

    RETIREE = h("07211ce2d3060909000000000f1d1d110000ff7f")   # outfield, +7 = 9
    OLD = h("071e1be2d3060909000000000f1d1d110000ff7f")       # 30: not young (30 >= 17 + 4)
    YOUNG = h("07111be2d3060909000000000f1d1d110000ff7f")     # 17: young

    def run_with(self, others, w=0x0000):
        return R.managed_replacement(bytes(20), self.RETIREE, 7, 40, others, w)

    def test_quota_edge(self):
        # seed 0: the new record is 28, not young; 19 young others -> override to 17 + rand(3)
        got, ini, w = self.run_with([self.YOUNG] * 19 + [self.OLD] * 80)
        self.assertEqual(got, h("07121ca772020909000000001d1414800000ff7f"))
        self.assertEqual((ini, w), (ord("J"), 0x21BC))
        got, ini, w = self.run_with([self.YOUNG] * 20 + [self.OLD] * 79)
        self.assertEqual(got, h("071c1ca7a7020909000000001d1414800000ff7f"))
        self.assertEqual((ini, w), (ord("J"), 0x72B1))

    def test_young_margin_edge(self):
        at20 = h("07141be2d3060909000000000f1d1d110000ff7f")      # 20 < 21: young
        at21 = h("07151be2d3060909000000000f1d1d110000ff7f")      # 21: not
        self.assertEqual(self.run_with([self.YOUNG] * 19 + [at20] + [self.OLD] * 79)[0][1], 0x1C)
        self.assertEqual(self.run_with([self.YOUNG] * 19 + [at21] + [self.OLD] * 79)[0][1], 0x12)

    def test_goalkeeper_young_base(self):
        gk_old = h("07211ce2d3060000000000000f1d1d110000ff7f")
        gk20 = h("07171be2d3060000000000000f1d1d110000ff7f")       # 23 < 20 + 4: young
        gk24 = h("07181be2d3060000000000000f1d1d110000ff7f")       # 24: not
        got = R.managed_replacement(bytes(20), gk_old, 7, 40, [gk20] * 19 + [gk24] * 80, 0x0000)[0]
        self.assertEqual(got[1], 0x15)                              # 20 + rand(3), rand 1 here
        self.assertEqual(got[0x0F], 0x91)                           # keeper: elements 5, 1; 33CD
        got = R.managed_replacement(bytes(20), gk_old, 7, 40, [gk20] * 20 + [gk24] * 79, 0x0000)[0]
        self.assertEqual(got[1], 0x1F)                              # no override: 28 + b - a

    def test_the_new_record_counts_itself(self):
        # seed 0x29: the new record is 20 (25 + b - a, b - a = -5), young; with 19 young others it
        # makes the count 20, so no override (55B5-5628 read its slot after 56F3 stored it)
        got = self.run_with([self.YOUNG] * 19 + [self.OLD] * 80, 0x0029)[0]
        self.assertEqual(got, h("07141ba7870d090900000000070505000000ff7f"))

    def test_override_values(self):
        # +1 = 17 + rand(3): 18, 19, 20 and nothing else over 4096 seeds
        ages = {self.run_with([self.OLD] * 99, w)[0][1] for w in range(4096)}
        self.assertEqual(ages, {0x12, 0x13, 0x14})

    def test_age_base_without_override(self):
        got = self.run_with([self.YOUNG] * 20 + [self.OLD] * 79, 0x4321)[0]
        self.assertEqual(got, h("07171aa79c07090900000000170b0b000000ff7f"))
        got = self.run_with([self.YOUNG] * 20 + [self.OLD] * 79, 0xBEEF)[0]
        self.assertEqual(got, h("07161aa792100909000000000c1a1a000000ff7f"))


class ContractTests(unittest.TestCase):
    """recreate_contract, recreate_constraints and NOT_IN_CAPTURES."""

    OLD = h("011f19a18c0f01010c000000011e1e110000ff7f")

    def test_contract_literal(self):
        c = R.recreate_contract(self.OLD)
        self.assertEqual(c["exact"], {0: 1, 6: 1, 7: 1, 8: 0, 9: 0, 10: 0, 11: 0, 16: 0, 17: 0,
                                      18: 0xFF, 19: 0x7F})
        self.assertEqual(c["range"], {1: (20, 30), 2: (25, 29), 5: (1, 16), 12: (1, 32),
                                      13: (14, 32), 3: (0x80, 0xFF)})
        self.assertEqual(c["same_as"], {14: 13})
        self.assertEqual(c["tactics"][0], 0x11)
        self.assertEqual(c["initial"], b"ABCDEFGHIJKLMNOPRSTVW")
        with_rating = R.recreate_contract(self.OLD, 34)
        self.assertEqual(with_rating["exact"][3], 0xA1)
        self.assertNotIn(3, with_rating["range"])

    def test_contract_carries_scorer_count(self):
        c = R.recreate_contract(h("011f19a18c0f01010c000000011e1e110007ff7f"))
        self.assertEqual(c["exact"][17], 0x07)

    def test_contract_goalkeeper(self):
        c = R.recreate_contract(h("01231ea18c0a000014000000012020110000ff7f"))
        self.assertEqual((c["range"][1], c["range"][2]), ((23, 33), (28, 32)))

    def test_contract_holds_for_the_exact_recreates(self):
        w = 0xFDF6
        for old, new, _ in R0006_C1:
            got, _, w = R.recreate(old, 34, w)
            c = R.recreate_contract(old, 34)
            for off, want in c["exact"].items():
                self.assertEqual(got[off], want, off)
            for off, (lo, hi) in c["range"].items():
                self.assertTrue(lo <= got[off] <= hi, off)

    def test_constraints_f016_form(self):
        c = R.recreate_constraints(self.OLD)
        self.assertEqual(c["exact"], {0: 1, 7: 1, 8: 0, 9: 0, 10: 0, 11: 0, 16: 0, 17: 0,
                                      18: 0xFF, 19: 0x7F})
        self.assertEqual(c["range"], {1: (20, 30), 2: (25, 29), 5: (1, 16)})
        self.assertEqual(R.recreate_constraints(self.OLD, (1, 0x1C, 0x50))["exact"][3], 0xA1)

    def test_not_in_captures(self):
        self.assertEqual(sorted(R.NOT_IN_CAPTURES), [3, 6, 15])


class RetirementTests(unittest.TestCase):
    """1771:7F40 (F016) on literal aged records: the thresholds the re-create follows."""

    def test_age_limits(self):
        f = A.retirement_flag
        self.assertEqual(f(h("011e1ba1a1000909000000000000000000000000")), 0)   # 30, caps 0, peak 27
        self.assertEqual(f(h("011f1ba1a1000909000000000000000000000000")), 1)   # 31, caps 0
        self.assertEqual(f(h("011f1ba1a1000909010000000000000000000000")), 0)   # 31, caps 1
        self.assertEqual(f(h("01211ea1a1000000000000000000000000000000")), 0)   # keeper 33, peak 30
        self.assertEqual(f(h("01221ea1a1000000000000000000000000000000")), 1)   # keeper 34

    def test_peak_margin(self):
        f = A.retirement_flag
        self.assertEqual(f(h("01201ba1a1000909050000000000000000000000")), 0)   # 32 = 27 + 5
        self.assertEqual(f(h("01211ba1a1000909050000000000000000000000")), 1)   # 33 > 27 + 5


class ImportStyleTests(unittest.TestCase):
    """R9: the re-export works for both import styles."""

    def test_package_import(self):
        import runtime.model.ageing as PA
        import runtime.model.recreate as PR
        old = h("011f19a18c0f01010c000000011e1e110000ff7f")
        self.assertEqual(PA.recreate_constraints(old)["range"], {1: (20, 30), 2: (25, 29), 5: (1, 16)})
        self.assertEqual(PR.recreate(old, 34, 0xFDF6)[0], h("01191ca1960e010100000000171b1b110000ff7f"))

    def test_top_level_import(self):
        old = h("011f19a18c0f01010c000000011e1e110000ff7f")
        self.assertEqual(A.recreate_constraints(old)["exact"][19], 0x7F)

    def test_e014_checker_standalone(self):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        r = subprocess.run([sys.executable, "experiments/E014-q013-ageing/check_ageing.py"],
                           cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertIn("match: 300/300", r.stdout)

    def test_e016_checker_standalone(self):
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        r = subprocess.run([sys.executable, "experiments/E016-q014-retirement/check_recreate.py"],
                           cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertTrue(r.stdout.rstrip().endswith("match: 38/38"), r.stdout[-500:])


class CheckerTests(unittest.TestCase):
    """check_recreate on the E014 records and on probes that must fail (review R1-R3)."""

    @classmethod
    def setUpClass(cls):
        cls.r5 = e014_captures("r0005")
        cls.r6 = e014_captures("r0006")

    def pair(self, caps, k, edit=None):
        b, a = copy.deepcopy(caps[k]), copy.deepcopy(caps[k + 1])
        if edit:
            edit(a)
        mm, notes = [], []
        out = K.check_pair(b, a, mm, notes)
        return out, mm

    @staticmethod
    def player(cap, n, w):
        country = next(c for c in cap["countries"] if c["n"] == n)
        return next(p for p in country["players"] if p["w"] == w)

    def set_byte(self, n, w, off, value):
        def edit(cap):
            p = self.player(cap, n, w)
            r = bytearray(h(p["rec"]))
            r[off] = value
            p["rec"] = r.hex()
        return edit

    def test_all_records(self):
        runs = {"runs/E014": sorted((ROOT / "runs" / "E014").glob("E014-r*.json"))}
        total, mm, pairs, made, exact, _ = K.check_runs(runs)
        self.assertEqual((total, mm, pairs, made, exact), (300, [], 5, 38, 38))

    def test_baseline_pair(self):
        self.assertEqual(self.pair(self.r6, 0), ((60, 8, 8), []))

    def test_undecided_recreate_matching_neither(self):
        # r0006 0->1, country 2, word 24: caps 0 at aged 31 (undecided), re-created
        _, mm = self.pair(self.r6, 0, self.set_byte(2, 24, 0x00, 0xFF))
        self.assertTrue(any("player 24" in m and "neither" in m for m in mm), mm)

    def test_undecided_continuing_matching_neither(self):
        # r0005 0->1, country 1, word 14: caps 0 at aged 32 (undecided), continued with a cap
        _, mm = self.pair(self.r5, 0, self.set_byte(1, 14, 0x02, 0x40))
        self.assertTrue(any("player 14" in m and "neither" in m for m in mm), mm)

    def test_undecided_recreate_joins_the_rating_check(self):
        # word 24's +3 0xc1 -> 0xc2 (+4 0xb4 -> 0xb5 = 194 * 15 / 16): the other re-creates of
        # country 2 carry 0xc1
        def edit(cap):
            p = self.player(cap, 2, 24)
            p["rec"] = "02171ac2b508020200000000012020320000ff7f"
        _, mm = self.pair(self.r6, 0, edit)
        self.assertTrue(any("different +3" in m for m in mm), mm)

    def test_surname(self):
        def edit(cap):
            self.player(cap, 1, 2)["surname"] = "07494e56414c4944000000"
        _, mm = self.pair(self.r6, 0, edit)
        self.assertTrue(any("player 2 " in m and "surname" in m for m in mm), mm)

    def test_initial_outside_the_table(self):
        def edit(cap):
            self.player(cap, 1, 2)["initial"] = "51"     # 'Q' is not in DS:0C38
        _, mm = self.pair(self.r6, 0, edit)
        self.assertTrue(any("player 2 " in m and "initial" in m for m in mm), mm)

    def test_morale_fitness_energy_tactics(self):
        for off, value in ((0x0C, 0xFF), (0x0D, 0xFF), (0x0E, 0xFF), (0x0F, 0x00)):
            _, mm = self.pair(self.r6, 0, self.set_byte(1, 2, off, value))
            self.assertTrue(any("player 2 " in m for m in mm), (off, mm))

    def test_drawn_byte_inside_its_range(self):
        # word 2's re-create 01191ca1960e010100000000171b1b11...: each edit keeps every range,
        # +4 (25 and 26 below peak 28 or 27: k = 1, 0xa1 * 15 / 16 = 0x96) and +0xE = +0xD, so
        # only the exact check sees it
        edits = {"+1": "011a1ca1960e010100000000171b1b110000ff7f",
                 "+2": "01191ba1960e010100000000171b1b110000ff7f",
                 "+5": "01191ca1960d010100000000171b1b110000ff7f",
                 "+0xC": "01191ca1960e010100000000161b1b110000ff7f",
                 "+0xD/+0xE": "01191ca1960e010100000000171c1c110000ff7f"}
        for what, rec in edits.items():
            def edit(cap, rec=rec):
                self.player(cap, 1, 2)["rec"] = rec
            _, mm = self.pair(self.r6, 0, edit)
            self.assertTrue(mm and all("no RNG word" in m for m in mm), (what, mm))

    def test_initial_inside_the_table(self):
        def edit(cap):
            self.player(cap, 1, 2)["initial"] = "4d"     # 'M' for the drawn 'N'
        _, mm = self.pair(self.r6, 0, edit)
        self.assertTrue(mm and all("no RNG word" in m for m in mm), mm)

    def test_empty_set_fails(self):
        self.assertEqual(K.main(["--runs", "tests/no-such-directory"]), 1)

    def test_replacement_errors_direct(self):
        # word 2's re-create (r0006 0->1, country 1): +4 wrong alone -> the ability error; +6 moved
        # (5, not +7) is not checked and 3431's bits are taken with +6 = +7
        old = h("011e19a18c0f01010c000000011e1e110000ff7f")
        good = h("01191ca1960e010100000000171b1b110000ff7f")
        names = ("0443697069000000000000", "52"), ("0443697069000000000000", "4e")
        self.assertEqual(K.replacement_errors(old, good, *names), [])
        bad4 = h("01191ca1970e010100000000171b1b110000ff7f")
        self.assertTrue(any(e.startswith("+0x04") for e in K.replacement_errors(old, bad4, *names)))
        moved = h("01191ca1960e050100000000171b1b110000ff7f")
        self.assertEqual(K.replacement_errors(old, moved, *names), [])

    def test_continued_with_caps_zero(self):
        # r0005 0->1, country 1, word 14: undecided, continued with a cap; caps 0 -> retirement fires
        def edit(cap):
            r = bytearray(h(self.player(cap, 1, 14)["rec"]))
            r[8] = r[9] = 0
            self.player(cap, 1, 14)["rec"] = r.hex()
        _, mm = self.pair(self.r5, 0, edit)
        self.assertTrue(any("player 14" in m and "caps 0" in m for m in mm), mm)

    def write_record(self, d, name, caps, status="completed"):
        obs = [{"source": "memory", "field": f"capture {i} (x): the state bytes", "value": json.dumps(c)}
               for i, c in enumerate(caps)]
        (Path(d) / name).write_text(json.dumps({"observations": obs, "status": status}))

    def test_no_comparison_and_no_recreate_fail(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            self.write_record(d, "E014-r0001.json", self.r6[:1], "aborted: one capture")
            total, mm, *_ = K.check_runs({"x": sorted(Path(d).glob("E0*-r*.json"))})
            self.assertEqual(total, 0)
            self.assertIn("no comparison was made: nothing corroborated", mm)
        with tempfile.TemporaryDirectory() as d:
            # the second capture: every record aged and given a cap (all continuing), so nothing
            # can be a re-create
            after = copy.deepcopy(self.r6[1])
            first = {(c["n"], p["w"]): p for c in self.r6[0]["countries"] for p in c["players"]}
            for c in after["countries"]:
                for p in c["players"]:
                    q = first[(c["n"], p["w"])]
                    r = bytearray(A.aged_record(h(q["rec"])))
                    r[8] = max(r[8], 1)
                    p["rec"], p["surname"], p["initial"] = r.hex(), q["surname"], q["initial"]
            self.write_record(d, "E014-r0002.json", [self.r6[0], after])
            total, mm, _, made, *_ = K.check_runs({"x": sorted(Path(d).glob("E0*-r*.json"))})
            self.assertEqual((total, made), (60, 0))
            self.assertIn("no re-create was compared", mm)

    def test_exit_on_a_mismatch(self):
        import tempfile
        b, a = copy.deepcopy(self.r6[0]), copy.deepcopy(self.r6[1])
        self.set_byte(1, 2, 0x0C, 0xFF)(a)
        with tempfile.TemporaryDirectory() as d:
            self.write_record(d, "E014-r0003.json", [b, a])
            self.assertEqual(K.main(["--runs", d]), 1)
            self.write_record(d, "E014-r0003.json", self.r6[:2])
            self.assertEqual(K.main(["--runs", d]), 0)


if __name__ == "__main__":
    unittest.main()
