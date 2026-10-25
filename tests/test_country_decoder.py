"""T94: independent TEAM label expectations; fake tables deliberately distinguish the fields."""
import unittest
from runtime.decoders.country import country_rating, country_status, manager_skill, team_labels


class Tables:
    def __init__(self):
        self.memory=bytearray(65536)
        self.calls=[]
        for i in range(32):
            self.memory[0x7894+i]=i
            self.put(0x6EB4+16*i,f'M{i}'.encode())
        for i in range(16):
            self.memory[0x7884+i]=32+i
            self.put(0x6EB4+16*(32+i),f'C{i}'.encode())

    def put(self,off,payload):
        self.memory[off:off+1+len(payload)]=bytes([len(payload)])+payload

    def read(self,off,n):
        self.calls.append((off,n))
        return bytes(self.memory[off:off+n])

    def code(self,segment,off,n):
        assert (segment,off,n)==(0x1771,0xAF0,8)
        return b'\x07unknown'


def country(continent=1,crank=2,world=1,manager=12):
    r=bytearray(191)
    r[42:47]=bytes([crank,world,continent,0,manager])
    return bytes(r)


class CountryDecoder(unittest.TestCase):
    def test_germany_original_labels_and_meaning(self):
        t=Tables()
        t.put(0x6EB4+16*47,b'giant')
        t.put(0x6EB4+16*15,b'eclectic')
        self.assertEqual(team_labels(country(),b'\x0c\x7e\x00',t.read,t.code),
                         dict(status='giant',skill='eclectic',country_rating=126))

    def test_rating_formula_independent_contrasting_countries(self):
        self.assertEqual(country_rating(1,28,80),34)
        self.assertEqual(country_rating(1,4,19),113)
        self.assertEqual(country_rating(4,17,83),31)
        self.assertEqual(country_rating(4,32,128),1)  # odd numerator truncates
        self.assertEqual(country_rating(1,1,1),128)

    def test_every_country_band_boundary(self):
        t=Tables()
        for value,band in [(1,0),(8,0),(9,1),(16,1),(17,2),(120,14),(121,15),(128,15)]:
            c,r,w=(4,32,129-2*value) if value<=64 else (1,1,257-2*value)
            with self.subTest(value=value):
                self.assertEqual(country_status(c,r,w,t.read),f'C{band}')

    def test_manager_zero_unknown_and_all_byte_boundaries(self):
        t=Tables()
        def forbidden(*args): raise AssertionError('manager zero must not read a label')
        self.assertIsNone(manager_skill(0,0,forbidden,forbidden))
        self.assertEqual(manager_skill(129,0,t.read,t.code),'unknown')
        for value,band in [(1,0),(8,0),(9,1),(120,14),(121,15),(128,15),(129,16),(255,31)]:
            self.assertEqual(manager_skill(134,value,t.read,t.code),f'M{band}')

    def test_manager_context_changes_skill_without_changing_status(self):
        t=Tables()
        a=team_labels(country(manager=129),b'\x01\x01\x7f',t.read,t.code)
        b=team_labels(country(manager=129),b'\x7f\x80\x01',t.read,t.code)
        self.assertEqual((a['status'],a['skill']),('C15','M0'))
        self.assertEqual((b['status'],b['skill']),('C15','M15'))
        self.assertEqual(team_labels(country(manager=0),None,t.read,t.code)['skill'],None)

    def test_pascal_label_and_glyph_projection_are_bounded(self):
        t=Tables()
        t.put(0x6EB4+16*47,b'A\0B\x01\x82')
        self.assertEqual(country_status(1,2,1,t.read),'A B☺é')
        t.memory[0x6EB4+16*47]=16
        with self.assertRaises(ValueError): country_status(1,2,1,t.read)
        with self.assertRaises(ValueError): country_status(1,2,1,lambda off,n:b'')

    def test_host_input_bounds_are_explicit(self):
        t=Tables()
        for c,r,w in [(0,1,1),(5,1,1),(1,0,1),(1,33,1),(1,1,0),(1,1,129),(True,1,1)]:
            with self.assertRaises(ValueError): country_rating(c,r,w)
        for m,v in [(-1,1),(135,1),(12,-1),(12,256),(True,1)]:
            with self.assertRaises(ValueError): manager_skill(m,v,t.read,t.code)
        with self.assertRaises(ValueError): team_labels(b'',None,t.read,t.code)
        with self.assertRaises(ValueError): team_labels(country(),b'\x0c',t.read,t.code)
