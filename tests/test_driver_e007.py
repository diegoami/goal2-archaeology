"""E007 (T16, Q009): the names read from a savestate (runtime/driver/players.py), the player screen's
transcription (runtime/driver/playerscreen.py), the runner's choices (experiments/E007-*/run.py) and the
model of experiments/E007-*/summarise.py.

The real screens and records are E007's own (runs/E007, committed, never rewritten): player 121 is
P Schmeichel (a goalkeeper), 221 B Illgner (a goalkeeper at the full bar of 25), 236 M Sammer (a two
footed player); the expected values are the screen's own text and bars as transcribed in the records.
The synthetic savestates plant the name arrays with literal offsets and sizes taken from the listing
(2139:0000: [9B6C] 0x8387 bytes, [9B70] 0xBF5 bytes; 1771:2E93: 11-byte Pascal strings and one byte per
initial), not from the module."""
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "tests"))

import playerscreen  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402
from test_driver_dataseg import DS_BASE, memory_image, savestate_of  # noqa: E402


def load_by_path(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Loaded by path under their own names: other experiments' scripts share the names `run` and `summarise`.
summarise = load_by_path("e007_summarise", "experiments/E007-q009-player-screen/summarise.py")
run = load_by_path("e007_run", "experiments/E007-q009-player-screen/run.py")

SURNAMES_AT = (0x5000, 0x0010)   # segment, offset
INITIALS_AT = (0x5900, 0x0003)
COUNTRIES_AT = (0x7400, 0x0030)


def lin(at):
    return at[0] * 16 + at[1]


def name_arrays(names):
    """{n: (initial, surname)} -> (surname array, initial array) of the allocation sizes."""
    s = bytearray(b"\xaa" * players.NAMES_BYTES)
    i = bytearray(b"\xbb" * players.INITIALS_BYTES)
    for n, (ini, sur) in names.items():
        s[n * 11:(n + 1) * 11] = bytes([len(sur)]) + sur.encode("cp437") + b"\xcc" * (10 - len(sur))
        i[n] = ord(ini)
    return bytes(s), bytes(i)


def state_with_names(s, i):
    mem = bytearray(memory_image())
    mem[DS_BASE + 0x9B6B] = 0xEE    # the bytes around the two pointers differ
    for ptr, at in ((0x9B6C, SURNAMES_AT), (0x9B70, INITIALS_AT)):
        mem[DS_BASE + ptr:DS_BASE + ptr + 4] = at[1].to_bytes(2, "little") + at[0].to_bytes(2, "little")
    for at, data in ((SURNAMES_AT, s), (INITIALS_AT, i)):
        mem[lin(at) + len(data)] = 0x77            # a byte past the array that is not zero
        mem[lin(at):lin(at) + len(data)] = data
    return savestate_of(bytes(mem))


class Names(unittest.TestCase):
    def setUp(self):
        self.names = {0: ("Z", "Nobody"), 1: ("P", "Schmeichel"), 2: ("L", "Olsen"), 3060: ("T", "Frank")}
        self.s, self.i = name_arrays(self.names)
        self.state = state_with_names(self.s, self.i)

    def test_arrays_are_the_allocations(self):
        self.assertEqual((players.NAMES_BYTES, players.INITIALS_BYTES), (3061 * 11, 3061))
        self.assertEqual(players.surnames(self.state), self.s)
        self.assertEqual(players.initials(self.state), self.i)

    def test_full_name(self):
        s, i = players.surnames(self.state), players.initials(self.state)
        self.assertEqual(players.full_name(s, i, 1), "P Schmeichel")   # ten characters: the record's longest
        self.assertEqual(players.full_name(s, i, 2), "L Olsen")        # the bytes after the string are not read
        self.assertEqual(players.full_name(s, i, 3060), "T Frank")     # the last record

    def test_a_length_byte_beyond_the_record_stays_in_the_record(self):
        # a Pascal string of 11 bytes holds 10 characters; a length byte of 0xFF reads no further than the record
        s = bytearray(self.s)
        s[1 * 11] = 0xFF
        self.assertEqual(len(players.full_name(bytes(s), self.i, 1)), 2 + 10)
        self.assertEqual(players.full_name(bytes(s), self.i, 2), "L Olsen")   # the next record is not read


class Screens(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all = {p["n"]: p for p in summarise.load()}

    def raw(self, n):
        return self.all[n]["raw"]

    def screen(self, n):
        return playerscreen.screen_of_raw(self.raw(n))

    def edited(self, n, edits):
        raw = bytearray(self.raw(n))
        for (row, col), (ch, attr) in edits.items():
            if ch is not None:
                raw[(row * 80 + col) * 2] = ch
            if attr is not None:
                raw[(row * 80 + col) * 2 + 1] = attr
        return playerscreen.screen_of_raw(bytes(raw))

    def test_goalkeeper_left_footed(self):
        got = playerscreen.parse(self.screen(121))
        self.assertEqual(got["name"], "P Schmeichel")
        self.assertEqual((got["age"], got["caps"], got["goals"], got["height_in"], got["bias"]), (30, 0, 0, 71, "left  foot"))
        self.assertEqual((got["position"], got["club_position"], got["status"], got["cards"], got["performance"]),
                         ("goalkeeper", "goalkeeper", "ready to play", "", ""))
        self.assertEqual(list(got["skills"].values()), [22, 21, 13, 13, 5, 5, 5, 5, 5, 5, 5, 5])
        self.assertEqual(list(got["skills"])[:3], ["keeping", "kicking", "tackling"])
        self.assertEqual(got["panel"]["hardness"], {"word": "mild", "bar": 6})
        self.assertEqual(got["panel"]["morale"], {"word": "concerned", "bar": 4})
        self.assertEqual(got["panel"]["leadership"], {"word": "negligible", "bar": 2})

    def test_the_longest_position_name_and_two_footed(self):
        got = playerscreen.parse(self.screen(236))
        self.assertEqual((got["bias"], got["position"], got["panel"]["hardness"]), ("two footed", "central midfield", {"word": "none", "bar": 0}))
        # 'defensive midfield' is 18 characters, the whole field of the cell (cols 1..18)
        self.assertEqual(playerscreen.parse(self.screen(385))["position"], "defensive midfield")

    def test_full_bar(self):
        got = playerscreen.parse(self.screen(221))
        self.assertEqual(max(got["skills"].values()), 25)
        self.assertEqual(got["panel"]["leadership"], {"word": "captain", "bar": 14})

    def test_the_bar_field_is_cols_10_to_35(self):
        # the edge: a field filled with 0x70 reads 26; the cells just outside it are not counted
        full = {(11, c): (None, 0x70) for c in range(10, 36)}
        self.assertEqual(playerscreen.parse(self.edited(121, full))["skills"]["keeping"], 26)
        outside = {(11, c): (None, 0x05) for c in range(10, 36)}
        outside.update({(11, 9): (None, 0x70), (11, 36): (None, 0x70)})
        self.assertEqual(playerscreen.parse(self.edited(121, outside))["skills"]["keeping"], 0)

    def test_the_right_bar_field_is_cols_47_to_60(self):
        full = {(22, c): (None, 0x70) for c in range(47, 61)}
        self.assertEqual(playerscreen.parse(self.edited(121, full))["panel"]["leadership"]["bar"], 14)
        outside = {(22, c): (None, 0x0C) for c in range(47, 61)}
        outside.update({(22, 46): (None, 0x70), (22, 61): (None, 0x70)})
        self.assertEqual(playerscreen.parse(self.edited(121, outside))["panel"]["leadership"]["bar"], 0)

    def test_a_word_as_wide_as_the_field_has_no_filler(self):
        word = "very confident"     # 14 characters
        edits = {(21, 47 + i): (ord(c), None) for i, c in enumerate(word)}
        self.assertEqual(playerscreen.parse(self.edited(121, edits))["panel"]["morale"]["word"], word)

    def test_only_a_player_screen_is_parsed(self):
        with self.assertRaises(ValueError):
            playerscreen.parse(self.edited(121, {(10, 1): (ord("x"), None)}))   # the 's' of the skills header
        with self.assertRaises(ValueError):
            playerscreen.parse(self.edited(121, {(7, 33): (ord("x"), None)}))   # inside the height cell
        with self.assertRaises(ValueError):
            playerscreen.screen_of_raw(b"\0" * 3999)


class Formulas(unittest.TestCase):
    def tables(self, **kv):
        t = summarise.Tables()
        for off, data in kv.items():
            t.add(int(off[1:], 16), bytes(data))
        return t

    def rec(self, **f):
        r = bytearray(20)
        for k, v in f.items():
            r[int(k[1:], 16)] = v
        return bytes(r)

    def test_two_footed_is_a_sum_of_30(self):
        self.assertTrue(summarise.two_footed(self.rec(f5=5, f2=25)))
        self.assertFalse(summarise.two_footed(self.rec(f5=5, f2=24)))
        self.assertFalse(summarise.two_footed(self.rec(f5=6, f2=25)))

    def test_hardness_takes_one_off_when_plus_3_is_odd(self):
        self.assertEqual(summarise.hardness_value(self.rec(f5=8, f3=0xA1)), 7)
        self.assertEqual(summarise.hardness_value(self.rec(f5=8, f3=0xA0)), 8)
        self.assertEqual(summarise.hardness_value(self.rec(f5=1, f3=0xA1)), 0)   # the lowest +5 is 1

    def test_leadership_is_the_remainder_by_8_halved_under_21(self):
        self.assertEqual(summarise.leadership_value(self.rec(f3=0xA1, f5=8, f1=0x15)), 1)   # 153 mod 8, age 21: not halved
        self.assertEqual(summarise.leadership_value(self.rec(f3=0xA7, f5=8, f1=0x15)), 7)   # 159 mod 8
        self.assertEqual(summarise.leadership_value(self.rec(f3=0xA7, f5=8, f1=0x14)), 3)   # age 20: halved
        with self.assertRaises(ValueError):
            summarise.leadership_value(self.rec(f3=5, f5=8))

    def test_skill_bars_are_the_class_value_times_plus_4_plus_1_over_256(self):
        pos, prof = 2, 3
        t = summarise.Tables()
        for i in range(1, 13):
            t.mem[0x6D25 + 12 * pos + i] = i                 # row i of position 2 is class i
            t.mem[0x6D25 + 12 * (pos + 1) + i] = 13 - i      # another position's row differs
            t.mem[0x6DCD + 12 * prof + i] = 2 * i + 1        # profile 3: class c has base 2c + 1 (3..25)
            t.mem[0x6DCD + 12 * (prof + 1) + i] = 26         # another profile differs
        base = [2 * i + 1 for i in range(1, 13)]
        self.assertEqual(summarise.skill_bars(self.rec(f7=pos, f5=prof, f4=255), t), base)        # *256 div 256
        self.assertEqual(summarise.skill_bars(self.rec(f7=pos, f5=prof, f4=127), t), [b * 128 // 256 for b in base])
        self.assertEqual(summarise.skill_bars(self.rec(f7=pos, f5=prof, f4=0), t), [b // 256 for b in base])
        self.assertEqual(summarise.skill_bars(self.rec(f7=pos + 1, f5=prof, f4=255), t), [2 * (13 - i) + 1 for i in range(1, 13)])

    def test_status_takes_the_first_test_that_holds(self):
        self.assertEqual(summarise.status_class(self.rec(f10=0x80, fE=0)), "suspended")   # bit 8 before injured
        self.assertEqual(summarise.status_class(self.rec(f10=0x00, fE=0)), "injured")
        self.assertEqual(summarise.status_class(self.rec(f10=0x10, fE=5)), "booked")       # bit 5
        self.assertEqual(summarise.status_class(self.rec(f10=0x20, fE=5)), "sent off")     # bit 6
        self.assertEqual(summarise.status_class(self.rec(f10=0x04, fE=5)), "substituted")  # bit 3
        self.assertEqual(summarise.status_class(self.rec(f10=0x00, fE=5)), "ready")

    def model_tables(self):
        t = summarise.Tables()
        for lo, hi in ((0x0E40, 0x0E90), (0x0F20, 0x0F80), (0x6990, 0x6AC0), (0x6D20, 0x7940)):
            t.add(lo, bytes(hi - lo))
        return t

    def plant_pstr(self, t, off, text):
        for k, b in enumerate(bytes([len(text)]) + text.encode("cp437")):
            t.mem[off + k] = b

    def test_position_is_plus_6_and_club_position_plus_7_and_the_height_and_skills_follow_plus_7(self):
        # the edge the 80 players cannot visit: +6 = +7 in all of them (F007)
        t = self.model_tables()
        self.plant_pstr(t, 0x69B6 + 0x13 * 3, "AAA")
        self.plant_pstr(t, 0x69B6 + 0x13 * 5, "BBBBB")
        t.mem[0x0E46 + 5], t.mem[0x0E46 + 3], t.mem[0x0E54 + 4] = 70, 60, 2     # n = 4 mod 12
        m = summarise.model(self.rec(f6=3, f7=5), 4, t)
        self.assertEqual((m["position"], m["club_position"], m["height_in"]), ("AAA", "BBBBB", 72))

    def test_fitness_follows_plus_0xD_and_energy_plus_0xE(self):
        t = self.model_tables()
        t.mem[0x78D5 + 7], t.mem[0x78F6 + 9] = 3, 4
        self.plant_pstr(t, 0x6EB4 + 16 * 3, "three")
        self.plant_pstr(t, 0x6EB4 + 16 * 4, "four")
        m = summarise.model(self.rec(fD=7, fE=9), 1, t)
        self.assertEqual((m["fitness"], m["energy"]), (("three", 7 * 14 // 32), ("four", 9 * 14 // 32)))
        injured = summarise.model(self.rec(fD=7, fE=0), 1, t)      # +0xE = 0: the word of index DS:78D5[0], no bar
        self.assertEqual(injured["fitness"][1], 0)

    def test_morale_index_stops_at_0x20_and_the_bar_is_drawn_below_it(self):
        t = self.model_tables()
        t.mem[0x78A3 + 0x1F], t.mem[0x78A3 + 0x20], t.mem[0x78A3 + 0x21] = 5, 6, 7
        self.plant_pstr(t, 0x6EB4 + 16 * 5, "five")
        self.plant_pstr(t, 0x6EB4 + 16 * 6, "six")
        self.assertEqual(summarise.model(self.rec(fC=0x1F), 1, t)["morale"], ("five", 0x1F * 14 // 32))
        self.assertEqual(summarise.model(self.rec(fC=0x20), 1, t)["morale"], ("six", 0))
        self.assertEqual(summarise.model(self.rec(fC=0x21), 1, t)["morale"], ("six", 0))   # min(+0xC, 0x20): not reachable in a new game

    def test_tables_refuse_a_byte_two_records_give_differently(self):
        t = summarise.Tables()
        t.add(0x10, b"\x01\x02")
        t.add(0x11, b"\x02\x03")
        with self.assertRaises(ValueError):
            t.add(0x12, b"\x09")
        with self.assertRaises(KeyError):
            t.byte(0x13)


class Records(unittest.TestCase):
    """The model against every transcribed player of every committed record."""

    @classmethod
    def setUpClass(cls):
        cls.ps = [p for p in summarise.load() if p["n"] is not None]

    def test_80_players_from_4_countries_every_value_as_the_model_says(self):
        self.assertEqual((len(self.ps), len({p["rec"][0] for p in self.ps})), (80, 4))
        bad = [(p["n"], k) for p in self.ps for k, (a, b) in summarise.compare(p).items() if a != b]
        self.assertEqual(bad, [])

    def test_the_comparison_visits_every_shown_value(self):
        names = list(summarise.compare(self.ps[0]))
        # the ten of the card (age, caps, goals, height, bias, position, club position, status, performance, cards),
        # the 12 skill bars, and the word and the bar of each of the 5 panel rows
        self.assertEqual(len(names), 10 + 12 + 5 * 2)
        self.assertEqual(sum(n.startswith("skill") for n in names), 12)

    def test_a_wrong_formula_is_seen(self):
        # the model with +3 where the listing has +4 differs on some of the 960 bars (summarise.py prints the count)
        alt = summarise.alternative_counts(self.ps)
        self.assertEqual((alt["+4"], alt["total"]), (960, 960))
        self.assertLess(alt["+3"], 960)

    def test_every_goalkeeper_shows_goalkeeper_twice(self):
        gks = [p for p in self.ps if p["rec"][6] == 0]
        self.assertEqual(len(gks), 8)
        self.assertTrue(all(p["shown"]["position"] == p["shown"]["club_position"] == "goalkeeper" for p in gks))


class Runner(unittest.TestCase):
    def test_tables_cover_every_byte_the_model_reads(self):
        # the edge E007-r0001..r0003 missed: DS:6DCD + 12 * 16 + 12 = DS:6E99 is past DS:6E90
        pooled = {p["n"]: p for p in summarise.load()}[121]["tables"]
        t = summarise.Tables()
        for lo, hi, _ in run.TABLES:
            t.add(lo, bytes(pooled.byte(o) for o in range(lo, hi)) if lo != 0x0C10 else bytes(hi - lo))
        top = self.extreme(pooled)
        for rec in top:
            summarise.model(rec, 3060, t)       # a KeyError is a byte no kept range holds

    def extreme(self, pooled):
        out = []
        for f5, f7, f4, f3, f12, f13, f14 in ((16, 13, 255, 255, 31, 32, 32), (1, 0, 0, 128, 0, 1, 1), (16, 13, 255, 255, 32, 32, 32)):
            r = bytearray(20)
            r[1], r[3], r[4], r[5], r[6], r[7], r[0xC], r[0xD], r[0xE] = 0x14, f3, f4, f5, f7, f7, f12, f13, f14
            out.append(bytes(r))
        return out

    def test_every_word_a_player_shows_is_in_the_kept_range(self):
        end = [hi for lo, hi, what in run.TABLES if "the words" in what][0]
        top = 0
        for p in summarise.load():
            t, r = p["tables"], p["rec"]
            h, lead = summarise.hardness_value(r), summarise.leadership_value(r)
            top = max(top, t.byte(0x78C4 + h), t.byte(0x78D5 + r[0xD]), t.byte(0x78F6 + r[0xE]), t.byte(0x78A3 + min(r[0xC], 0x20)), t.byte(0x7917 + lead))
        self.assertGreater(top, 0x40)           # indexes reach the upper words, so a range cut short fails here
        self.assertLessEqual(0x6EB4 + 16 * top + 16, end)

    def test_candidates_are_the_players_with_the_shown_name(self):
        s, i = name_arrays({1: ("P", "Nielsen"), 2: ("K", "Nielsen"), 3: ("P", "Nielsen"), 4: ("P", "Nielsen ")})
        self.assertEqual(run.candidates(s, i, "P Nielsen"), [1, 3])
        self.assertEqual(run.candidates(s, i, "K Nielsen"), [2])
        self.assertEqual(run.candidates(s, i, "P Olsen"), [])
        # player 0 is no player (1771:42BC returns at once for 0, `42D2`): never a candidate
        s0, i0 = name_arrays({0: ("P", "Nielsen"), 1: ("P", "Nielsen")})
        self.assertEqual(run.candidates(s0, i0, "P Nielsen"), [1])

    def test_the_player_is_found_by_name_and_age(self):
        s, i = name_arrays({1: ("P", "Nielsen"), 2: ("P", "Nielsen"), 3: ("L", "Olsen")})
        recs = bytearray(players.PLAYERS_BYTES)
        recs[1 * 20 + 1], recs[2 * 20 + 1], recs[3 * 20 + 1] = 28, 31, 25
        recs[2 * 20 + 5] = 0x5A
        recs[2 * 20] = 5                                     # player 2 is of country 5
        cs = bytearray((k * 3 + 1) % 247 for k in range(players.COUNTRIES_BYTES))
        state = self.with_players(bytes(recs), s, i, bytes(cs))
        got = run.player_observations(1, "x", state, {"name": "P Nielsen", "age": 31}, s, i)
        self.assertIn("n=2 named=[1, 2] named_and_aged=[2]", got[0]["value"])
        self.assertEqual(got[1]["value"], bytes(recs[40:60]).hex())
        self.assertEqual(got[1]["value"][10:12], "5a")
        self.assertEqual(len(got), 3)
        self.assertEqual(got[2]["value"], bytes(cs[5 * 0xBF:6 * 0xBF]).hex())              # country 5's record, not 4's or 6's
        self.assertEqual(got[2]["addr"], hex(lin(COUNTRIES_AT) + 5 * 0xBF))
        both = run.player_observations(1, "x", state, {"name": "P Nielsen", "age": 99}, s, i)
        self.assertIn("n=unresolved", both[0]["value"])
        self.assertEqual(len(both), 1)                       # no record for an unresolved player

    def with_players(self, p, s, i, c):
        mem = bytearray(memory_image())
        for ptr, at in ((0x9B6C, SURNAMES_AT), (0x9B70, INITIALS_AT), (0xA91B, (0x6200, 0x0020)), (0xA917, COUNTRIES_AT)):
            mem[DS_BASE + ptr:DS_BASE + ptr + 4] = at[1].to_bytes(2, "little") + at[0].to_bytes(2, "little")
        mem[lin((0x6200, 0x0020)):lin((0x6200, 0x0020)) + len(p)] = p
        mem[lin(COUNTRIES_AT):lin(COUNTRIES_AT) + len(c)] = c
        for at, data in ((SURNAMES_AT, s), (INITIALS_AT, i)):
            mem[lin(at):lin(at) + len(data)] = data
        return savestate_of(bytes(mem))

    def test_table_observations_are_the_planted_bytes(self):
        mem = bytearray(memory_image())
        for lo, hi, _ in run.TABLES:
            mem[DS_BASE + lo:DS_BASE + hi] = bytes((lo + k) % 251 for k in range(hi - lo))
        obs = run.table_observations(4, savestate_of(bytes(mem)))
        self.assertEqual(len(obs), len(run.TABLES))
        for o, (lo, hi, _) in zip(obs, run.TABLES):
            self.assertEqual(bytes.fromhex(o["value"]), bytes((lo + k) % 251 for k in range(hi - lo)))
            self.assertIn(f"DS:{lo:04X}..{hi - 1:04X}, {hi - lo} bytes", o["field"])


if __name__ == "__main__":
    unittest.main()
