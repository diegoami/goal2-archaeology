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


# E006-r0001 (DOS 10:00), the bytes as read: players 1..40 (countries 1 and 2: every position code a
# squad uses, ages below, at and above the peak, players older than peak + 4) and 2561..2640 (the 80
# players 1771:98C4 made for the managed country 7); country records 1, 2 and 7, bytes +0x28..+0x2F;
# GOAL.DAT block squad_20, records 1, 2 and 7.
COUNTRIES_1_2 = (
    "01201ea1a10a000000000000082020110000ff7f011d19a1960f010100000000051212110000ff7f011a1da1960c0202000000001e1414320000ff7f011d1aa1a10b020200000000181717320000ff7f"
    "011a19a1a106050500000000132020000000ff7f011b1da19602060600000000042020800000ff7f01201ca19603070700000000112020800000ff7f011b1ba1a1070808000000001e1414000000ff7f"
    "01211ba182100c0c00000000102020000000ff7f01191ba1960d0d0d000000001a1b1b000000ff7f011f1ca1a10d0d0d00000000042020000000ff7f011f1da1a10d000000000000081b1b110000ff7f"
    "01161da1820b010100000000072020110000ff7f011f1ca1a110020200000000132020220000ff7f011a1ca19606050500000000042020000000ff7f011a1ca19601060600000000182020800000ff7f"
    "011f1da1a10c070700000000071212000000ff7f01191ba196040c0c00000000061616800000ff7f011d1ca1a10f0d0d00000000042020000000ff7f011f1ba1960b0d0d00000000171c1c000000ff7f"
    "021e1ec1c102000000000000131919910000ff7f021b1bc1c10a010100000000171a1a110000ff7f021e1dc1c10a020200000000182020320000ff7f021d1ac1c105020200000000062020320000ff7f"
    "021d1cc1c106050500000000062020000000ff7f021d1bc1c10b0606000000000e1d1d000000ff7f02171bc1a808070700000000122020000000ff7f02211dc1b409080800000000071515000000ff7f"
    "021e1ac1b403090900000000102020800000ff7f021f1ac1a80f0d0d00000000051616000000ff7f021b1bc1c1010d0d00000000101313800000ff7f02211dc1b40d000000000000022020110000ff7f"
    "021a1bc1c1090202000000001d1e1e320000ff7f021d1ac1c102020200000000091111b20000ff7f021e1cc1c107040400000000142020110000ff7f02171dc19c09050500000000062020000000ff7f"
    "021f1cc1c10e070700000000032020000000ff7f021d1cc1c1050909000000000d2020000000ff7f02181cc1a8020d0d00000000061d1d800000ff7f021d1bc1c1050d0d000000000a1313000000ff7f"
)
EXTRA_7 = (
    "071d20e2d3100000000000000f1d1d110000ff7f071d20e2d30b000000000000102020110000ff7f071f1ee3e3070000000000001d1c1c110000ff7f07241eddb3050000000000000c2020110000ff7f"
    "071e1bdfdf0a010100000000042020110000ff7f071e1bdddd030101000000000c1f1f910000ff7f07221bdea601010100000000171d1d910000ff7f07221ae29b01010100000000032020910000ff7f"
    "071e1be3e301020200000000142020b20000ff7f07191de6c9050202000000001c1313320000ff7f071d1be6e60f020200000000021a1a220000ff7f071a1ce3d40e020200000000092020220000ff7f"
    "071e1ae0d2030303000000001a2020910000ff7f07201be6c90b0303000000001f2020110000ff7f071d1ae3e30a0303000000000b1919110000ff7f071c1ae0e008030300000000032020110000ff7f"
    "07221ae29b05040400000000190f0f110000ff7f071d1ae3e304040400000000202020910000ff7f071b1ce0e00f040400000000092020110000ff7f07191ce1d20f0404000000001d1b1b110000ff7f"
    "071f1ce2e20d0505000000001c2020000000ff7f071a1cddcf010505000000000e0a0a800000ff7f07181ddec20f0505000000001a2020000000ff7f071d1de3e3070505000000000a2020000000ff7f"
    "071b1cdede06060600000000142020000000ff7f071a1cddcf09060600000000011010000000ff7f071a1ce4d510060600000000061414000000ff7f07191adddd08060600000000092020000000ff7f"
    "071f1ae6c9100707000000001d2020000000ff7f071e1de1e1060707000000001a1c1c000000ff7f071b1be2e20b0707000000001a2020000000ff7f071a1be4e4100707000000001d2020000000ff7f"
    "071a19dfdf0e080800000000182020000000ff7f071c19e2e207080800000000021010000000ff7f071c1de6e60d0808000000000d1919000000ff7f071e1be3e30e080800000000131919000000ff7f"
    "071f1bdfd107090900000000112020000000ff7f071b1ae2e20e0909000000000a2020000000ff7f071e1be4e4070909000000001e2020000000ff7f071f1bded006090900000000201919000000ff7f"
    "071d1ce3e3070a0a00000000191a1a000000ff7f071f1ae1c4100a0a00000000082020000000ff7f07201ce5d60f0a0a00000000131d1d000000ff7f07181ce3c6100a0a000000001f1818000000ff7f"
    "071f1ce0e00c0b0b000000000c1d1d000000ff7f071a1ce6d7090b0b000000001f2020000000ff7f071c1ae3e30e0b0b000000001a0b0b000000ff7f07181cdfc30a0b0b00000000161a1a000000ff7f"
    "07191ae1e10b0c0c000000000c0606000000ff7f071f1adfc3060c0c00000000171b1b000000ff7f071a19e1e1010c0c000000000b0e0e800000ff7f071e1ae2d3020c0c00000000112020800000ff7f"
    "071f1adec20a0d0d00000000020303000000ff7f07191ae4e40a0d0d00000000201818000000ff7f07201addb30a0d0d00000000020e0e000000ff7f071a1ddfd10e0d0d00000000041818000000ff7f"
    "07161edfa704000000000000032020910000ff7f07121de19a0f010100000000132020110000ff7f07131ae1b605020200000000010c0c320000ff7f07141ae4b906020200000000122020320000ff7f"
    "07121ae5ab0c0303000000000c2020110000ff7f07121be1a808040400000000082020110000ff7f07131de39c06050500000000081414000000ff7f07141bdeb40c0707000000000c1e1e000000ff7f"
    "07141de3aa02080800000000030e0e800000ff7f07141de5ab0c090900000000202020000000ff7f07131ce0a8050d0d00000000101c1c000000ff7f07161ee4ab070000000000000c2020110000ff7f"
    "07141addb3070101000000000c1b1b110000ff7f07131bdda50e020200000000201313220000ff7f07121de59d040303000000001c2020910000ff7f07141be4b909050500000000141d1d000000ff7f"
    "07121ae1a80d0a0a000000000c0f0f000000ff7f07121ae2a9100c0c000000000a2020000000ff7f07121be1a8060d0d00000000101010000000ff7f07131de49c040d0d000000000a2020000000ff7f"
    "07221bdfa708040400000000052020110000ff7f071b19e5e50a0505000000000f1e1e000000ff7f071a1bdddd0e0707000000001c2020000000ff7f071c1cdfdf07080800000000160808000000ff7f"
)
COUNTRY_28 = {1: bytes.fromhex("1c501c5001f70104"), 2: bytes.fromhex("1b141b1401470204"), 7: bytes.fromhex("011d011d018b8104")}
SQUAD = {1: bytes.fromhex("00010202050607080c0d0d0001020506070c0d0d"), 2: bytes.fromhex("0001020205060708090d0d000202040507090d0d"),
         7: bytes.fromhex("000102020304050708090d00010203050a0c0d0d")}


def rows(chunks):
    b = bytes.fromhex("".join(chunks))
    return [b[i:i + 20] for i in range(0, len(b), 20)]


def country_array():
    c = bytearray(COUNTRY_ALLOC)
    for n, raw in COUNTRY_28.items():
        c[n * COUNTRY_REC + 0x28:n * COUNTRY_REC + 0x30] = raw
    return bytes(c)


class Model(unittest.TestCase):
    def assert_fields(self, got, want, what):
        for f in summarise.MODELLED:
            self.assertEqual(got[f], want[f], f"{what} field +0x{f:X}")

    def test_lcg_matches_f004(self):
        # F004: DS:7B62 at the main screen is 162 steps past hour*256+minute; 0xee42 at 10:00 (E003-r0007)
        self.assertEqual(summarise.lcg_steps(10 * 256, 0xEE42), 162)
        self.assertEqual(summarise.LCG(0).draw(16), ((0x1B0F * 16) >> 16) + 1)

    def test_ratings(self):
        c = country_array()
        self.assertEqual(summarise.rating(c, 1), 34)    # ((5-1)*(33-28) + (129-80)) // 2
        self.assertEqual([summarise.rating(c, n) for n in (2, 7)], [66, 114])

    def test_squads_of_countries_1_and_2(self):
        sq = bytes(20) + SQUAD[1] + SQUAD[2] + bytes(20 * 126)
        model, _ = summarise.model_squads(country_array(), sq, last=2)
        for n, want in enumerate(rows(COUNTRIES_1_2), start=1):
            self.assert_fields(model[n], want, f"player {n}")

    def test_the_80_players_of_the_managed_country(self):
        # 1771:98C4 for country 7 (rating 114), from the LCG word 0xf5db E006's summary found
        model = summarise.model_extra(0xF5DB, 7, SQUAD[7], 114)
        observed = rows(EXTRA_7)
        self.assertEqual(len(model), 80)
        for i, (m, o) in enumerate(zip(model, observed)):
            self.assert_fields(m, o, f"player {2561 + i}")

    def test_seed_search_finds_0xf5db(self):
        self.assertEqual(summarise.find_extra_seed(rows(EXTRA_7), 7, SQUAD[7], 114), [0xF5DB])


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
