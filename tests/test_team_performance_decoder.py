"""T115: independent TEAM performance expectations over fake memory; values are hand-computed."""
import unittest
from runtime.decoders.team_performance import player_value, role_sums, team_performance


class Memory:
    def __init__(self):
        self.ds = bytearray(65536)
        self.ds[0xD7C:0xD7C+16] = bytes([0, 1, 1, 4, 4, 2, 2, 2, 2, 5, 5, 5, 3, 3, 29, 31])
        self.players, self.countries = {0: player(0x7FFF, 0)}, {}

    def read_ds(self, off, n):
        return bytes(self.ds[off:off+n])

    def read_player(self, word):
        return self.players[word]

    def read_country(self, n):
        return self.countries[n]

    def decode(self, country, c1e=1, c1f=1, sides=(1, 2)):
        return team_performance(country, c1e, c1f, sides, self.read_country, self.read_player, self.read_ds)


def player(performance, position, energy=20, status=0):
    r = bytearray(20)
    r[6], r[0xE], r[0x10] = position, energy, status
    r[0x12:0x14] = (performance & 0xFFFF).to_bytes(2, 'little')
    return bytes(r)


def country(words):
    r = bytearray(191)
    for i, w in enumerate(words):
        r[2*i:2*i+2] = w.to_bytes(2, 'little')
    return bytes(r)


class TestValue(unittest.TestCase):
    def test_encodings(self):
        self.assertEqual(player_value(0x37), 100)           # a starter's fresh rating
        self.assertEqual(player_value(10000+0x37), 100)     # an incoming substitute's
        self.assertEqual(player_value(0x37+40), 140)        # a goal
        self.assertEqual(player_value(10000+0x37-50), 50)   # a substitute's own goal
        self.assertEqual(player_value(0x37-100), 0)
        self.assertEqual(player_value(0x7FFF), 0x7FFF-0x37-10000+100)  # blank is not skipped

    def test_threshold_follows_the_subtraction(self):
        self.assertEqual(player_value(5000+0x37), 5100)     # not above 5000 after -0x37
        self.assertEqual(player_value(5001+0x37), 5001-10000+100)
        self.assertEqual(player_value(5001), 5001-0x37+100)  # 3827 would decode this one

    def test_wrap(self):
        self.assertEqual(player_value(0x8037), -32768+100)  # signed after -0x37: no -10000
        self.assertEqual(player_value(0), -0x37+100)
        self.assertEqual(player_value(0x7FCB), 0x7FCB-0x37-10000+100)


class TestSums(unittest.TestCase):
    def test_roles_and_signed_halves(self):
        m = Memory()
        m.players.update({1: player(0x37, 0), 2: player(0x37+20, 1), 3: player(0x37+1, 3),
                          4: player(0x37-103, 9), 5: player(0x37, 12, energy=0, status=0xFF)})
        m.countries[1] = country([1, 2, 3, 4, 5])
        # slots 6..11 are word 0: player 0's blank 0x7FFF counts at its keeper role, six times
        blank = 0x7FFF-0x37-10000+100
        keeper = (100+6*blank) & 0xFFFF
        keeper = keeper-0x10000 if keeper >= 0x8000 else keeper
        self.assertEqual(role_sums(m.countries[1], m.read_player, m.read_ds),
                         [keeper, 120+50, 50-1, -1+100])

    def test_role_bound(self):
        m = Memory()
        m.players[1] = player(0x37, 14)
        m.countries[1] = country([1]*11)
        with self.assertRaises(ValueError):
            role_sums(m.countries[1], m.read_player, m.read_ds)


class TestPanel(unittest.TestCase):
    def setUp(self):
        self.m = Memory()
        self.m.players.update({7: player(0x37, 6), 8: player(0x37+60, 0)})
        self.m.countries[1] = country([7]*11)
        self.m.countries[2] = country([8]*11)

    def test_gate(self):
        for c1e, c1f in ((0, 0), (1, 0), (0, 1)):
            self.assertIsNone(self.m.decode(1, c1e, c1f))
        self.assertIsNotNone(self.m.decode(1, 2, 255))

    def test_side_choice(self):
        self.assertEqual(self.m.decode(2)['side'], 1)
        self.assertEqual(self.m.decode(1)['side'], 0)
        out = self.m.decode(99)                              # not in the match: side 0's team
        self.assertEqual((out['side'], out['team']), (0, 1))
        self.assertEqual(self.m.decode(2, sides=(2, 2))['side'], 1)

    def test_rows_and_cells(self):
        out = self.m.decode(1)                               # eleven midfielders at 100
        self.assertEqual(out['role_sums'], [0, 0, 1100, 0])
        self.assertEqual([(b['row'], b['column'], b['value'], b['cells']) for b in out['bars']],
                         [(20, 10, 1, 0), (21, 10, 1, 0), (22, 10, 256, 25), (23, 10, 1, 0)])
        out = self.m.decode(2)                               # eleven keepers at 160: undivided
        self.assertEqual(out['role_sums'], [1760, 0, 0, 0])
        self.assertEqual(out['bars'][0]['cells'], 25)


if __name__ == '__main__':
    unittest.main()
