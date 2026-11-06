"""T124c continental builders: listing-derived synthetic ABI edges.

[confirmed:F023; named1771_05/raw1771_10 6B55..6FEA]. Natural input lineage
and exact play_round constructor/tail comparisons are under out/T124c.
Synthetic knockout inputs use distinct native countries of each continent,
valid B1/B2 membership, saved semifinal indices and completed1-0/0-2 scores.
"""
import unittest
from tests.test_port_stages import _Calls,RET
from tests.test_port_stage_qualifying import qualifying_rng_port,word
from original_match.port import stages as ST

RET.update({'1771:6B55':'1771:76D0','1771:6E59':'1771:76D9'})
ENTRIES={'1771:6B55':'ret','1771:6E59':'ret'}


def native_continent_teams(m,c):
    return [n for n in range(1,129) if m.read(m.far(ST.COUNTRIES)+191*n+44,1)[0]==c][:8]


def knockout_input(m):
    """Declared synthetic completed semis, all group countries/native pointers valid; host eliminated in groups."""
    g=m.far(ST.GAME);table=m.far(ST.TABLES);fx=m.far(ST.FIXTURES)
    first=769
    for c in range(1,5):
        teams=native_continent_teams(m,c)
        assert len(teams)==8 and len(set(teams))==8
        for bgroup in (1,2):
            for place in range(1,5):
                word(m,table+c*0x1C0+bgroup*0x38+place*8+0x500,teams[(bgroup-1)*4+place-1])
        word(m,g+0x2C+2*c,teams[7])
        n=first+(c-1)*2
        word(m,table+c*0x1C0+0x56C,n);word(m,table+c*0x1C0+0x56E,n+1)
        for idx,a,b,scores,flag in ((n,teams[0],teams[5],(1,0),0),(n+1,teams[4],teams[1],(0,2),1)):
            m.write(fx+8*(idx-1),bytes([*scores,0x65,flag])+a.to_bytes(2,'little')+b.to_bytes(2,'little'))
    word(m,g+0x26,777);word(m,g+0x28,777)


def manager_in_runnerup_group(m):
    """Consistent synthetic manager-country transfer to an A runner-up (hence Bgroup3/4, no finals group)."""
    table=m.far(ST.TABLES);g=m.far(ST.GAME);countries=m.far(ST.COUNTRIES)
    country=m.word_at(table+0x1C0+0x38+16-0x200)
    old=m.read(m.far(ST.MANAGERS)+3*129,1)[0]
    m.write(countries+191*old+46,bytes([old]))
    m.write(countries+191*country+46,bytes([129]))
    m.write(m.far(ST.MANAGERS)+3*129,bytes([country]))
    m.write(g,b'\x01')


def host_seed_six(m):
    """Controlled valid RNG word: (6*0x7ABD+0x1B0F)&FFFF=64381, so first draw8 != draw7 [derived:F004]."""
    word(m,m.far(0xA978),6)


def continental_falsifier_input(m,variant):
    if variant=='continental-host-bound-seven':host_seed_six(m)
    elif variant=='continental-third-place-opponent':knockout_input(m)
    else:raise AssertionError(variant)


class Continental(_Calls):
    def specs(self,variant=None):
        return ((ST.PORTS,variant),'runtime',qualifying_rng_port(),(ST.display_helpers(),None))

    def test_entries_and_single_display_ownership(self):
        self.assertEqual({a:ST.PORTS.entries[a].ret for a in ENTRIES},ENTRIES)
        for a in ('1771:5C94','1771:5CCB'):self.assertNotIn(a,ST.PORTS.entries)

    def test_stage3_full_calendar_hosts_and_finals_group_count(self):
        m,p=self.call('1771:6B55',specs=self.specs(),game={0x3C:3,0x3D:1,0x40:0})
        self.proved(p,'1771:6B55')
        g=m.far(ST.GAME)
        self.assertEqual(m.word_at(g+0x28),1345)
        fx=m.far(ST.FIXTURES)
        kinds=[m.read(fx+8*(n-1)+2,1)[0] for n in range(769,1345)]
        self.assertEqual((kinds.count(3),kinds.count(1)),(48,528))
        for c in range(1,5):
            host=m.word_at(g+0x2C+2*c)
            self.assertEqual(m.read(m.far(ST.COUNTRIES)+191*host+44,1)[0],c)

    def test_managed_bgroups3_to8_do_not_receive_a_finals_group(self):
        m,p=self.call('1771:6B55',specs=self.specs(),game={0x3C:3,0x3D:1,0x40:0},before=manager_in_runnerup_group)
        self.proved(p,'1771:6B55')
        self.assertEqual(m.read(m.far(ST.GAME)+2,1),b'\x00')

    def test_semifinal_builder_uses_b1_winner_b2_runnerup_and_reverse(self):
        m,p=self.call('1771:6E59',specs=self.specs(),game={0x3C:4,0x3D:2,0x40:0},before=knockout_input)
        self.proved(p,'1771:6E59')
        self.assertEqual(m.word_at(m.far(ST.GAME)+0x28),785)
        for c in range(1,5):
            t=native_continent_teams(m,c);fx=m.far(ST.FIXTURES)
            n=777+(c-1)*2
            self.assertEqual({m.word_at(fx+8*(n-1)+4),m.word_at(fx+8*(n-1)+6)},{t[0],t[5]})
            self.assertEqual({m.word_at(fx+8*n+4),m.word_at(fx+8*n+6)},{t[4],t[1]})
            self.assertEqual(m.read(fx+8*(n-1)+2,1),b'\x65')

    def test_third_place_losers_precede_final_winners_and_indices(self):
        m,p=self.call('1771:6E59',specs=self.specs(),game={0x3C:4,0x3D:1,0x40:0},before=knockout_input)
        self.proved(p,'1771:6E59')
        self.assertEqual(m.word_at(m.far(ST.GAME)+0x28),785)
        fx=m.far(ST.FIXTURES);table=m.far(ST.TABLES)
        for c in range(1,5):
            t=native_continent_teams(m,c);n=777+(c-1)*2
            self.assertEqual({m.word_at(fx+8*(n-1)+4),m.word_at(fx+8*(n-1)+6)},{t[5],t[4]})
            self.assertEqual({m.word_at(fx+8*n+4),m.word_at(fx+8*n+6)},{t[0],t[1]})
            self.assertEqual(m.read(fx+8*(n-1)+2,1),b'\x66')
            self.assertEqual(m.read(fx+8*n+2,1),b'\x67')
            self.assertEqual(m.word_at(table+c*0x1C0+0x570),n)
            self.assertEqual(m.word_at(table+c*0x1C0+0x572),n+1)

    def test_host_and_knockout_assignment_falsifiers_are_caught(self):
        from original_match.port.prove import ProofError
        for variant,target,rounds,before in (
            ('continental-host-bound-seven','1771:6B55',1,host_seed_six),
            ('continental-third-place-opponent','1771:6E59',1,knockout_input)):
            with self.subTest(variant=variant),self.assertRaises(ProofError):
                self.call(target,specs=self.specs(variant),game={0x3C:3 if target.endswith('6B55') else 4,0x3D:rounds,0x40:0},before=before)
