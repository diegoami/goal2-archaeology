"""T116: independent TEAM characteristics expectations over fake memory; values are hand-computed."""
import unittest
from runtime.decoders.team_characteristics import aggregates, bar_cells, team_characteristics


class Memory:
    """Fake tables that name each table and index: H3 is hardness table entry 3."""
    def __init__(self):
        self.ds = bytearray(65536)
        label = 0
        for name, table, count in (('M', 0x78A3, 33), ('H', 0x78C4, 17), ('F', 0x78D5, 33), ('E', 0x78F6, 33),
                                   ('X', 0x7917, 40)):
            for i in range(count):
                self.ds[table+i] = label
                text = f'{name}{i}'.encode()
                self.ds[0x6EB4+16*label:0x6EB4+16*label+1+len(text)] = bytes([len(text)])+text
                label = (label+1) % 256
        self.players = {0: bytes(20)}

    def read_ds(self, off, n):
        return bytes(self.ds[off:off+n])

    def read_player(self, word):
        return self.players[word]


def player(morale=16, fitness=20, energy=20, hardness=8, b3=0, age=25, caps=10, status=0):
    r = bytearray(20)
    r[1], r[3], r[5] = age, b3, hardness & 0xFF
    r[8:10] = caps.to_bytes(2, 'little')
    r[0xC], r[0xD], r[0xE], r[0x10] = morale & 0xFF, fitness & 0xFF, energy & 0xFF, status
    return bytes(r)


def country(words):
    r = bytearray(191)
    for i, w in enumerate(words):
        r[2*i:2*i+2] = w.to_bytes(2, 'little')
    return bytes(r)


class TestAggregates(unittest.TestCase):
    def setUp(self):
        self.m = Memory()

    def agg(self, players):
        words = []
        for i, p in enumerate(players, 1):
            self.m.players[i] = p
            words.append(i)
        return aggregates(country(words+[0]*(11-len(words))), self.m.read_player)

    def test_eleven_and_the_seed(self):
        out = self.agg([player()]*11)
        self.assertEqual(out, dict(morale=(6+176)//11, fitness=(6+220)//11, hardness=(6+88)//11,
                                   energy=(6+220)//11, age=(6+275)//11, caps=(6+110)//11))

    def test_unavailable_count_in_the_divisor(self):
        out = self.agg([player(energy=0)]+[player(status=0x80)]+[player()]*9)
        self.assertEqual(out['energy'], (6+180)//11)
        self.assertEqual(out['age'], (6+225)//11)
        # word 0 in a slot reads player 0, unavailable here (energy 0)
        out = self.agg([player()]*5)
        self.assertEqual(out['caps'], (6+50)//11)

    def test_slot_twelve_is_ignored(self):
        self.m.players[1], self.m.players[2] = player(), player(caps=1000)
        self.assertEqual(aggregates(country([1]*11+[2]), self.m.read_player)['caps'], (6+110)//11)

    def test_morale_terms(self):
        self.assertEqual(self.agg([player(morale=40)]*11)['morale'], (6+11*32)//11)
        self.assertEqual(self.agg([player(morale=0)]*11)['morale'], 1)          # floor 1, morale only
        self.assertEqual(self.agg([player(morale=-128)]+[player(morale=0)]*10)['morale'], (6-128) % 65536//11)

    def test_fitness_needs_positive_energy_but_availability_already_does(self):
        self.assertEqual(self.agg([player(fitness=-5)]*11)['fitness'], (6-55) % 65536//11)
        self.assertEqual(self.agg([player(fitness=0)]*11)['fitness'], 0)        # no floor here

    def test_hardness_byte(self):
        self.assertEqual(self.agg([player(hardness=9, b3=1)]*11)['hardness'], (6+88)//11)
        self.assertEqual(self.agg([player(hardness=0, b3=3)]*11)['hardness'], (6+11*255) % 65536//11)

    def test_age_and_caps_wrap(self):
        self.assertEqual(self.agg([player(caps=60000)]*11)['caps'], (6+660000) % 65536//11)
        self.assertEqual(self.agg([player(age=255)]*11)['age'], (6+11*255)//11)


class TestDisplay(unittest.TestCase):
    def setUp(self):
        self.m = Memory()

    def decode(self, p):
        self.m.players[1] = p
        return team_characteristics(country([1]*11), self.m.read_player, self.m.read_ds)

    def test_rows_labels_bars_numbers(self):
        out = self.decode(player(morale=15, fitness=28, energy=28, hardness=8, age=29, caps=0))
        self.assertEqual([(d['field'], d['row'], d['column'], d['value'], d['text'], d['cells'], d['in_table'])
                          for d in out['descriptors']],
                         [('hardness', 20, 46, 8, 'H8', 8, True), ('fitness', 21, 46, 28, 'F28', 14, True),
                          ('energy', 22, 46, 28, 'E28', 14, True), ('morale', 23, 46, 15, 'M15', 7, True)])
        self.assertEqual([(n['field'], n['row'], n['column'], n['text']) for n in out['numbers']],
                         [('caps', 19, 49, '0'), ('age', 19, 59, '29')])

    def test_out_of_table_reads_the_next_table(self):
        out = self.decode(player(hardness=17, fitness=33, energy=33, morale=0))
        d = {x['field']: x for x in out['descriptors']}
        self.assertEqual((d['hardness']['text'], d['hardness']['in_table']), ('F0', False))
        self.assertEqual(d['fitness']['text'], 'E0')
        self.assertEqual(d['energy']['text'], 'X0')
        self.assertEqual((d['morale']['value'], d['morale']['text']), (1, 'M1'))

    def test_bar_shift_drops_high_bits(self):
        self.assertEqual(bar_cells(16, 16), 16)
        self.assertEqual(bar_cells(32, 32), 16)
        self.assertEqual(bar_cells(1, 32), 0)
        self.assertEqual(bar_cells(3, 32), 1)
        self.assertEqual(bar_cells(4096, 16), 0)
        self.assertEqual(bar_cells(5946, 32), ((5946*16) & 0xFFFF)//32)

    def test_label_bounds(self):
        self.m.ds[0x6EB4+16*self.m.ds[0x78C4+8]] = 16
        with self.assertRaises(ValueError):
            self.decode(player())
        with self.assertRaises(ValueError):
            team_characteristics(bytes(190), self.m.read_player, self.m.read_ds)


if __name__ == '__main__':
    unittest.main()
