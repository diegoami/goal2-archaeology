"""T124b1: qualifying ranking helpers, original-call differential oracles.

Synthetic direct inputs are deliberately labelled; the natural construction proof
is in out/T124b1. Every direct call retains a real caller return address.
[confirmed: seg_1771_02.asm 114B and seg_1771_09.asm 5EE1..6616; F017/F023].
"""
import unittest
from tests.test_port_stages import _Calls, RET
from original_match.port import stages as ST

RET.update({"1771:114B": "1771:64C3", "1771:5EE1": "1771:6406",
            "1771:5FD1": "1771:606D", "1771:602D": "1771:63C8",
            "1771:6103": "1771:63C2", "1771:61F8": "1771:63CC",
            "1771:63A4": "1771:6765"})
ENTRIES = {"1771:114B": "retf 2", "1771:5EE1": "ret 6", "1771:5FD1": "ret 0xa",
           "1771:602D": "ret 2", "1771:6103": "ret 2", "1771:61F8": "ret 2", "1771:63A4": "ret"}


def word(m, addr, value):
    m.write(addr, (value & 65535).to_bytes(2, "little"))


class Rankings(_Calls):
    def test_entries_returns_and_no_duplicate_display_ownership(self):
        self.assertEqual({a: ST.PORTS.entries[a].ret for a in ENTRIES}, ENTRIES)
        self.assertNotIn("1771:5C94", ST.PORTS.entries)
        self.assertNotIn("1771:5CCB", ST.PORTS.entries)

    def test_continent_rank_includes_ties_self_and_only_same_continent(self):
        def before(m):
            for c in range(1, 129):
                m.write(m.far(ST.COUNTRIES) + 191*c + 43, bytes([2 if c < 5 else 3, 1 if c < 4 else 2]))
        m, p = self.call("1771:114B", (1,), before=before)
        self.proved(p, "1771:114B")
        self.assertEqual(m.reg("ax"), 3)

    def test_quicksort_unsigned_points_ties_and_self_swap(self):
        def before(m):
            word(m, m.DS*16 + 0x9B56, 0x9BFD)
            word(m, m.DS*16 + 0x9B58, m.DS)
            m.write(m.DS*16 + 0x9BFE, bytes(range(1, 9)))
            for c, points in enumerate((0, 65535, 32768, 32767, 7, 7, 7, 0), 1):
                word(m, m.far(ST.COUNTRIES) + 191*c + 47, points)
        m,p = self.call("1771:5EE1", (1, 8, 0x3E80), before=before)
        self.proved(p, "1771:5EE1")
        order=list(m.read(m.DS*16+0x9BFE,8))
        self.assertEqual(order, [2,3,4,6,7,5,8,1])

    def test_bonus_wraps_points_and_counter_and_signed_flag(self):
        for flag in (0, 1, 255):
            with self.subTest(flag=flag):
                def before(m):
                    cp=m.far(ST.COUNTRIES)+191
                    word(m,cp+47,65500)
                    m.write(cp+50+4*(flag if flag<128 else flag-256)+2,bytes([255]))
                m,p=self.call("1771:5FD1", (1,600,2,flag,0x3E80),before=before)
                self.proved(p,"1771:5FD1")
                cp=m.far(ST.COUNTRIES)+191
                self.assertEqual(m.word_at(cp+47),820 if flag == 255 else 564)  # signed -1 counter aliases high points byte
                self.assertEqual(m.read(cp+50+4*(flag if flag<128 else flag-256)+2,1),bytes([3 if flag == 255 else 0]))

    def test_world_and_continent_placement_bonuses_real_winner_loser_calls(self):
        for target in ("1771:602D","1771:6103"):
            with self.subTest(target=target):
                m,p=self.call(target,(0x3E80,))
                self.proved(p,target)

    def test_group_points_both_modes_and_stage2_table_selector(self):
        for mode,stage in ((0,2),(0,5),(1,5)):
            with self.subTest(mode=mode,stage=stage):
                m,p=self.call("1771:61F8",(0x3E80,),game={0x40:mode,0x3C:stage})
                self.proved(p,"1771:61F8")

    def test_rank_recompute_both_modes_full_order_and_manager_records(self):
        for mode in (0,1):
            with self.subTest(mode=mode):
                m,p=self.call("1771:63A4",game={0x40:mode,0x3C:2 if mode==0 else 5},
                              before=self.manager_edges)
                self.proved(p,"1771:63A4")
                for c in range(1,129):
                    cp=m.far(ST.COUNTRIES)+191*c
                    self.assertEqual(m.word_at(cp+47),5-m.read(cp+44,1)[0])
                    tag=m.read(cp+46,1)[0]
                    self.assertEqual(m.read(m.far(ST.MANAGERS)+3*tag+2,1),bytes([0]))

    @staticmethod
    def manager_edges(m):
        for tag,value in ((0,128),(128,127),(129,255),(130,1)):
            m.write(m.far(ST.MANAGERS)+3*tag+2,bytes([value]))
        for c in range(1,129):
            cp=m.far(ST.COUNTRIES)+191*c
            m.write(cp+40,bytes([255,255]))

    def test_ranking_bonus_and_manager_reset_falsifiers_are_caught(self):
        from original_match.port.prove import ProofError
        for variant in ("ranking-bonus-dropped","manager-score-reset-dropped"):
            with self.subTest(variant=variant),self.assertRaises(ProofError):
                self.call("1771:63A4",specs=((ST.PORTS,variant),),before=self.manager_edges)


RET.update({"1771:56E4": "1771:6944", "1771:56FF": "1771:6758",
            "1771:6730": "1771:76C7", "23E4:11D7": "1771:67A8"})
DRAW_ENTRIES={"1771:56E4":"ret 2","1771:56FF":"ret","1771:6730":"ret","23E4:11D7":"retf"}


def qualifying_rng_port():
    """Real06B1 includes its0688 body inline; select the caller entry, without double-registering its inline callee.

    [confirmed: port/entrypoints.py random_core/rng_core] This is the same real
    implementation used by the aggregate proof, never a stub or replacement RNG.
    """
    from original_match.port import Registry,entrypoints
    reg=Registry('entrypoints','real06B1 with its original inlined0688 body')
    reg._add(entrypoints.PORTS.entries['214B:06B1'])
    return (reg,None)


class Draw(_Calls):
    """[confirmed: F023/F004] Direct synthetic ABI edges; full natural/world construction under out/T124b2."""
    def test_four_entries_and_return_abis(self):
        self.assertEqual({a:ST.PORTS.entries[a].ret for a in DRAW_ENTRIES},DRAW_ENTRIES)

    def test_continent_offset_wraps_word_and_returns_real_cx(self):
        for c in (0,1,2,3,4,5,65535):
            with self.subTest(c=c):
                m,p=self.call('1771:56E4',(c,))
                self.proved(p,'1771:56E4')
                self.assertEqual(m.reg('ax'),((c-1)*32)&65535)
                self.assertEqual(m.reg('cx'),5)

    def test_mode0_copies_all129_bytes_including_sentinel(self):
        def before(m):
            m.write(m.DS*16+0x9C7E,bytes(range(129)))
            m.write(m.DS*16+0x9D80,b'\xA5')
        m,p=self.call('1771:56FF',game={0x40:0},before=before,specs=('stages','runtime'))
        self.proved(p,'1771:56FF')
        self.assertEqual(m.read(m.DS*16+0x9CFF,129),bytes(range(129)))
        self.assertEqual(m.read(m.DS*16+0x9D80,1),b'\xA5')
        self.assertEqual(m.reg('cx'),0)

    def test_mode1_stably_filters_original_world_order_per_continent(self):
        expected=[]
        def before(m):
            order=list(reversed(range(1,129)))
            m.write(m.DS*16+0x9BFE,bytes(order))
            m.write(m.DS*16+0x9CFF,b'\xA5')
            m.set_reg('cx',0xBEEF)
            for c in range(1,5):
                expected.extend(n for n in order if m.read(m.far(ST.COUNTRIES)+191*n+44,1)[0]==c)
        m,p=self.call('1771:56FF',game={0x40:1},before=before,specs=('stages','runtime'))
        self.proved(p,'1771:56FF')
        self.assertEqual(m.read(m.DS*16+0x9D00,128),bytes(expected))
        self.assertEqual(m.read(m.DS*16+0x9CFF,1),b'\xA5')
        self.assertEqual(m.reg('cx'),0xBEEF)  # caller-observable on the initial-year seed path

    def test_reference_seed_service_preserves_cx_dx_and_sets_only_ah(self):
        for cx,dx,ax in ((0,0,0),(0xBEEF,0xFACE,0x53A7),(65535,1,0x8001)):
            with self.subTest(cx=cx,dx=dx,ax=ax):
                def before(m):
                    m.set_reg('cx',cx);m.set_reg('dx',dx);m.set_reg('ax',ax)
                m,p=self.call('23E4:11D7',before=before)
                self.proved(p,'23E4:11D7')
                self.assertEqual(m.rd(0x7B62),cx)
                self.assertEqual(m.rd(0x7B64),dx)
                self.assertEqual(m.reg('ax'),0x2C00|(ax&255))
                self.assertEqual((m.reg('cx'),m.reg('dx')),(cx,dx))

    def test_initial_year_whole_builder_both_modes_with_real_library_helpers(self):
        for mode in (0,1):
            with self.subTest(mode=mode):
                m,p=self.call('1771:6730',game={0x38:0,0x39:0,0x3C:2 if mode==0 else 5,0x40:mode},
                              specs=('stages','runtime',qualifying_rng_port()))
                self.proved(p,'1771:6730')
                summary=p.summary()
                self.assertEqual(summary['23E4:11D7']['nested'],1)
                self.assertEqual(m.word_at(m.far(ST.GAME)+0x26),1 if mode==0 else 1361)
                self.assertEqual(m.word_at(m.far(ST.GAME)+0x28),769 if mode==0 else 2001)

    def test_draw_order_and_group_assignment_falsifiers_caught(self):
        from original_match.port.prove import ProofError
        for variant in ('qualifying-draw-order-reversed','qualifying-group-plus-one'):
            with self.subTest(variant=variant),self.assertRaises(ProofError):
                self.call('1771:6730',game={0x38:0,0x39:0,0x3C:2,0x40:0},
                          specs=((ST.PORTS,variant),'runtime',qualifying_rng_port()))
