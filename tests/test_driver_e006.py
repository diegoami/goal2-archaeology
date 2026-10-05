"""E006 (T15, Q004): the player and country arrays read from a savestate (runtime/driver/players.py),
and the analysis of experiments/E006-q004-skills/summarise.py.

The synthetic savestate plants the far pointers and the arrays with literal offsets and sizes taken from
F002 / static/goal-exe-map.md (2139:0000: [A917] 0x603F bytes, [A91B] 0xEF24 bytes; records 0xBF and
0x14 bytes), not from the module. Neighbouring bytes of each pointer differ and the bytes just past each
array are non-zero, so a pointer offset, a record size or an array size off by one fails a test here.
The fixtures of the model tests are bytes of E006-r0001 (players 1, 2, 12 and 2561; country 1's
record bytes +0x28..+0x2F) and GOAL.DAT block squad_20 record 1."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "experiments" / "E006-q004-skills"))

import players  # noqa: E402
import summarise  # noqa: E402
from test_driver_dataseg import DS_BASE, memory_image, savestate_of  # noqa: E402

PLAYERS_AT = (0x4E5B, 0x000D)    # segment, offset as E006-r0001 read them
COUNTRIES_AT = (0x4857, 0x000E)
PLAYER_REC, PLAYER_ALLOC = 0x14, 0xEF24
COUNTRY_REC, COUNTRY_ALLOC = 0xBF, 0x603F


def lin(at):
    return at[0] * 16 + at[1]


def arrays():
    """A country array whose record c names players (c-1)*20+1 .. c*20 and a player array whose
    records hold their country in byte 0; other bytes distinct."""
    c = bytearray((i * 7 + 1) % 253 for i in range(COUNTRY_ALLOC))
    p = bytearray((i * 5 + 2) % 251 for i in range(PLAYER_ALLOC))
    for country in range(1, 129):
        for slot in range(20):
            n = (country - 1) * 20 + slot + 1
            a = country * COUNTRY_REC + 2 * slot
            c[a:a + 2] = n.to_bytes(2, "little")
            p[n * PLAYER_REC] = country
    return bytes(p), bytes(c)


def state_with(p, c, players_at=PLAYERS_AT, countries_at=COUNTRIES_AT):
    mem = bytearray(memory_image())
    mem[DS_BASE + 0xA916] = 0xEE    # the bytes around the two adjacent pointers (A917..A91E) differ
    mem[DS_BASE + 0xA91F] = 0xDD
    for ptr, at in ((0xA91B, players_at), (0xA917, countries_at)):
        mem[DS_BASE + ptr:DS_BASE + ptr + 4] = at[1].to_bytes(2, "little") + at[0].to_bytes(2, "little")
    # the country array ends where the player array starts (0x4857E + 0x603F = 0x4E5BD, as in E006-r0001):
    # written first, so its byte past the end is the player array's first byte, not zero either
    for at, data in ((countries_at, c), (players_at, p)):
        mem[lin(at) + len(data)] = 0x77                        # a byte past the array that is not zero
        mem[lin(at):lin(at) + len(data)] = data
    return savestate_of(bytes(mem))


class Arrays(unittest.TestCase):
    def setUp(self):
        self.p, self.c = arrays()
        self.s = state_with(self.p, self.c)

    def test_pointers(self):
        self.assertEqual(players.far_pointer(self.s, 0xA91B), (0x4E5B, 0x000D, 0x4E5BD))
        self.assertEqual(players.far_pointer(self.s, 0xA917), (0x4857, 0x000E, 0x4857E))

    def test_arrays_are_the_allocations(self):
        self.assertEqual(players.players(self.s), self.p)
        self.assertEqual(players.countries(self.s), self.c)
        self.assertEqual((players.N_PLAYERS, players.N_COUNTRIES), (3061, 129))

    def test_check_places_the_arrays(self):
        self.assertEqual(players.check(players.players(self.s), players.countries(self.s)), [])

    def test_squad_words(self):
        self.assertEqual(players.squad(self.c, 1), list(range(1, 21)))
        self.assertEqual(players.squad(self.c, 128), list(range(2541, 2561)))

    def test_check_refuses_a_shifted_player_array(self):
        s = state_with(b"\x00" + self.p[:-1], self.c)
        self.assertTrue(players.check(players.players(s), players.countries(s)))

    def test_check_refuses_a_shifted_country_array(self):
        s = state_with(self.p, b"\x00" + self.c[:-1])
        self.assertTrue(players.check(players.players(s), players.countries(s)))

    def test_check_refuses_a_short_array(self):
        self.assertTrue(players.check(self.p[:-1], self.c))
        self.assertTrue(players.check(self.p, self.c[:-1]))

    def test_last_country_last_player(self):
        # the edge: country 128's last word and player 2560's byte 0
        p = bytearray(self.p)
        p[2560 * PLAYER_REC] = 127
        self.assertTrue(players.check(bytes(p), self.c))


# E006-r0001 (DOS 10:00), players 1, 2, 12 and 2561, the bytes as read.
PLAYER_1 = bytes.fromhex("01201ea1a10a000000000000082020110000ff7f")
PLAYER_2 = bytes.fromhex("011d19a1960f010100000000051212110000ff7f")
PLAYER_12 = bytes.fromhex("011f1da1a10d000000000000081b1b110000ff7f")
PLAYER_2561 = bytes.fromhex("071d20e2d3100000000000000f1d1d110000ff7f")
COUNTRY_1_28 = bytes.fromhex("1c501c5001f70104")   # country 1, bytes +0x28..+0x2F
SQUAD_1 = bytes.fromhex("00010202050607080c0d0d0001020506070c0d0d")  # GOAL.DAT squad_20 record 1


class Model(unittest.TestCase):
    def test_lcg_matches_f004(self):
        # F004: DS:7B62 at the main screen is 162 steps past hour*256+minute; 0xee42 at 10:00 (E003-r0007)
        self.assertEqual(summarise.lcg_steps(10 * 256, 0xEE42), 162)
        self.assertEqual(summarise.LCG(0).draw(16), ((0x1B0F * 16) >> 16) + 1)

    def test_rating_of_country_1(self):
        c = bytearray(COUNTRY_ALLOC)
        c[COUNTRY_REC + 0x28:COUNTRY_REC + 0x30] = COUNTRY_1_28
        self.assertEqual(summarise.rating(bytes(c), 1), 34)   # ((5-1)*(33-28) + (129-80)) // 2

    def test_country_1_slots_1_2_12(self):
        c = bytearray(COUNTRY_ALLOC)
        c[COUNTRY_REC + 0x28:COUNTRY_REC + 0x30] = COUNTRY_1_28
        sq = bytes(20) + SQUAD_1 + bytes(20 * 127)
        model, _ = summarise.model_squads(bytes(c), sq, last=1)
        for n, want in ((1, PLAYER_1), (2, PLAYER_2), (12, PLAYER_12)):
            for f in summarise.MODELLED:
                self.assertEqual(model[n][f], want[f], f"player {n} field +0x{f:X}")

    def test_extra_player_from_its_seed(self):
        # the managed country 7 (rating 114): the first of 1771:98C4's players from LCG word 0xf5db
        first = summarise.model_extra(0xF5DB, 7, bytes(20), 114)[0]
        for f in summarise.MODELLED:
            self.assertEqual(first[f], PLAYER_2561[f], f"field +0x{f:X}")


class GoalDat(unittest.TestCase):
    def test_r007_r008_offsets(self):
        dat = bytearray((i * 3 + 1) % 256 for i in range(44040))
        r = summarise.per_country(bytes(dat))
        self.assertEqual(r["R007[0]"][1], dat[0x9EEE + 3])
        self.assertEqual(r["R007[2]"][128], dat[0x9EEE + 3 * 128 + 2])
        self.assertEqual(r["R008"][1], dat[0xA071 + 1])
        self.assertEqual(r["R008"][128], dat[0xA071 + 128])


if __name__ == "__main__":
    unittest.main()
