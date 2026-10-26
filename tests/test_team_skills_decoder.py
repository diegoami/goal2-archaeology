"""T114: independent TEAM skills expectations over fake memory; values are hand-computed."""
import unittest
from runtime.decoders.team_bars import line_bars
from runtime.decoders.team_skills import line_sums, strength, team_skills


class Memory:
    """Fake original memory: tables at their DS/CS offsets, records by number."""
    def __init__(self):
        self.ds = bytearray(65536)
        self.cs = bytearray(65536)
        self.ds[0xD4E:0xD4E+16] = bytes([0, 1, 1, 4, 4, 2, 2, 2, 2, 5, 5, 5, 3, 3, 0, 1])
        self.ds[0xE7C:0xE7F] = bytes([0, 1, 2])
        for row in range(3):
            for side in range(14):
                self.ds[0xE60+14*row+side] = 1  # a nonzero foot: 3139's set applies
        self.cs[0x0BA4] = 0x62                   # elements 1, 5, 6
        self.cs[0x3139:0x313B] = bytes([0x88, 0x04])  # {3, 7, 10}
        self.cs[0x3159:0x315B] = bytes([0x10, 0x09])  # {4, 8, 11}
        self.players, self.countries, self.managers = {}, {}, {0: bytes(3)}

    def read_ds(self, off, n):
        return bytes(self.ds[off:off+n])

    def read_code(self, segment, off, n):
        assert segment == 0x1771
        return bytes(self.cs[off:off+n])

    def read_player(self, word):
        return self.players[word]

    def read_country(self, n):
        return self.countries[n]

    def read_manager(self, m):
        return self.managers[m]

    def decode(self, country=1):
        return team_skills(self.countries[country], self.read_player, self.read_country,
                           self.read_manager, self.read_ds, self.read_code)


def player(country=1, skill=0x3E+40, energy=20, form=10, position=6, side=1,
           tactics=0, status=0, b2=0, b5=0, b3=0):
    r = bytearray(20)
    r[0], r[2], r[3], r[4], r[5] = country, b2, b3, skill, b5
    r[6], r[7], r[0xC], r[0xE], r[0xF], r[0x10] = position, side, form & 0xFF, energy & 0xFF, tactics, status
    return bytes(r)


def country(words, tactics=0, manager=1):
    r = bytearray(191)
    for i, w in enumerate(words):
        r[2*i:2*i+2] = w.to_bytes(2, 'little')
    r[0x2D], r[0x2E] = tactics, manager
    return bytes(r)


class TestStrength(unittest.TestCase):
    def setUp(self):
        self.m = Memory()

    def value(self, **kw):
        return strength(7, player(**kw), self.m.read_ds, self.m.read_code)

    def test_form_below_32_is_added(self):
        self.assertEqual(self.value(skill=0x3E+40, energy=20, form=10), 70)

    def test_form_32_takes_a_sixteenth(self):
        self.assertEqual(self.value(skill=0x3E+44, energy=20, form=32), 64-4)

    def test_negative_form_and_clamps(self):
        self.assertEqual(self.value(skill=0x3E, energy=1, form=-5), 0)
        self.assertEqual(self.value(skill=255, energy=127, form=31), 0x100)

    def test_unavailable_is_zero(self):
        self.assertEqual(self.value(energy=0), 0)
        self.assertEqual(self.value(energy=-3), 0)
        for bit in (7, 5, 2):
            self.assertEqual(self.value(status=1 << bit), 0)
        self.assertEqual(self.value(status=0x5B), 70)  # bits 0,1,3,4,6 do not exclude

    def test_halving_cases(self):
        self.assertEqual(self.value(position=3), 35)        # foot nonzero, set {3,7,10}
        self.assertEqual(self.value(position=3, b2=10, b5=20), 70)  # 3041: +2 + +5 == 30
        self.m.ds[0xE60+14*(7 % 3)+1] = 0                   # zero foot: set {4,8,11}
        self.assertEqual(self.value(position=4), 35)
        self.assertEqual(self.value(position=3), 70)
        self.assertEqual(self.value(position=0, side=1), 35)  # keeper with a side
        self.assertEqual(self.value(position=6, side=0), 35)  # outfield without one
        self.assertEqual(self.value(position=0, side=0), 70)


class TestLineSums(unittest.TestCase):
    def setUp(self):
        self.m = Memory()
        self.m.managers[1] = bytes([0, 100, 0])   # bonus 100 div 8 + 16 = 28, eighth 3

    def test_lines_bonus_tactics_and_hybrids(self):
        m = self.m
        m.players[1] = player(position=0, side=0)          # keeper 70: no tactic bonus
        m.players[2] = player(position=1)                  # defence
        m.players[3] = player(position=3, side=1, b2=10, b5=20)  # hybrid 4: 98 halves 49+49
        m.players[4] = player(position=9, skill=0x3E+41)   # hybrid 5: 99 -> unsigned 49 twice
        m.players[5] = player(position=12, energy=0)       # unavailable attacker: 0, no bonus
        m.countries[1] = country([1, 2, 3, 4, 5], tactics=0b00010001)  # elements 1 and 5 set
        # outfield players 2,3,4,5 each add 3 per element: 1 and 5 set -> attack, 6 clear -> defence
        self.assertEqual(line_sums(m.countries[1], m.read_player, m.read_country, m.read_manager,
                                   m.read_ds, m.read_code),
                         [98, 98+49+4*3, 49+49, 49+0+2*4*3])

    def test_player_override_only_below_five(self):
        m = self.m
        # element 1 from the player (+0xF element 5 set, element 1 clear); 5 and 6 from country 2
        m.players[1] = player(country=2, tactics=0b00010000)
        m.countries[2] = country([], tactics=0b00110001)
        m.countries[1] = country([1])
        self.assertEqual(line_sums(m.countries[1], m.read_player, m.read_country, m.read_manager,
                                   m.read_ds, m.read_code), [0, 3, 98, 6])

    def test_zero_words_are_skipped_and_slot_12_ignored(self):
        m = self.m
        m.players[9] = player(position=12)
        m.countries[1] = country([0]*11+[9])
        self.assertEqual(line_sums(m.countries[1], m.read_player, m.read_country, m.read_manager,
                                   m.read_ds, m.read_code), [0, 0, 0, 0])

    def test_manager_zero_reads_record_zero(self):
        m = self.m
        m.managers[0] = bytes([0, 255, 0])                 # bonus 31+16 = 47, eighth 5
        m.players[1] = player(position=0, side=0)
        m.countries[1] = country([1], manager=0)
        self.assertEqual(line_sums(m.countries[1], m.read_player, m.read_country, m.read_manager,
                                   m.read_ds, m.read_code), [117, 0, 0, 0])

    def test_positions_beyond_the_line_table_are_refused(self):
        m = self.m
        m.ds[0xD4E+16] = 6
        m.players[1] = player(position=16)
        m.countries[1] = country([1])
        with self.assertRaises(ValueError):
            line_sums(m.countries[1], m.read_player, m.read_country, m.read_manager, m.read_ds, m.read_code)


class TestBars(unittest.TestCase):
    def test_scaling_clamps_and_cells(self):
        bars = line_bars([10, 44, 1027, -8], 15)
        self.assertEqual([(b['line'], b['row'], b['column'], b['value'], b['cells']) for b in bars],
                         [('keeper', 15, 10, 10, 0), ('defence', 16, 10, 11, 1),
                          ('midfield', 17, 10, 256, 25), ('attack', 18, 10, 1, 0)])

    def test_keeper_is_not_divided_and_division_truncates(self):
        bars = line_bars([257, 1023, 1027, -7], 15)
        self.assertEqual([b['value'] for b in bars], [256, 255, 256, 1])
        self.assertEqual([b['cells'] for b in bars], [25, 24, 25, 0])

    def test_panel_rows(self):
        m = Memory()
        m.managers[1] = bytes(3)
        m.players[1] = player(position=0, side=0, skill=255, energy=127, form=31)
        m.countries[1] = country([1])
        out = m.decode()
        self.assertEqual(out['line_sums'], [0x100+16, 0, 0, 0])
        self.assertEqual([(b['row'], b['cells']) for b in out['bars']], [(15, 25), (16, 0), (17, 0), (18, 0)])

    def test_host_bounds(self):
        with self.assertRaises(ValueError):
            line_bars([0, 0, 0], 15)
        with self.assertRaises(ValueError):
            line_bars([0, 0, 0, 0x8000], 15)
        m = Memory()
        with self.assertRaises(ValueError):
            team_skills(bytes(190), m.read_player, m.read_country, m.read_manager, m.read_ds, m.read_code)


if __name__ == '__main__':
    unittest.main()
