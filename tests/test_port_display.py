"""T73: preserved state and narrowly projected display-event behavior."""
import signal
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port
from original_match.port.mem import PlainMem

PSEG, POFF = 0x4800, 0x0010          # the players' table (DS:A91B)
SQSEG, SQOFF = 0x4A00, 0x0020        # the countries (DS:A917)
GSEG, GOFF = 0x4C00, 0x0040          # the game record (DS:A923): +0x26 the index, +0x2C the hosts, +0x40, +0x38
FXSEG, FXOFF = 0x4E00, 0x0010        # a fixture: +1, +2 its kind, +4 and +6 its countries
PARENT = 0x2800                      # the BP of a synthetic parent frame (B11F's, 52CC's)
BP0 = 0x3000 - 2                     # the BP a routine's `push bp; mov bp, sp` gives (SP 0x3000 at the entry)


class Rig:
    def __init__(self):
        self.mem = PlainMem(bytearray(0x60000))
        self.mem.regs.update(ss=0, sp=0x3000, bp=0x1234, ds=self.mem.DS, eflags=0x202)
        self.calls = []
        self.writes = []             # (DS offset or linear, size, value, writer linear)
        self.ds16(0xA91B, POFF)
        self.ds16(0xA91D, PSEG)
        self.ds16(0xA917, SQOFF)
        self.ds16(0xA919, SQSEG)
        self.ds16(0xA923, GOFF)
        self.ds16(0xA925, GSEG)
        ds = self.mem.DS * 16

        def watch(address, size, value, at):
            self.writes.append((address - ds if ds <= address <= ds + 0xFFFF else address, size, value, at))
        self.mem.listeners.append((0, len(self.mem.memory), watch))

    def ds8(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off] = value & 0xFF

    def ds16(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off:self.mem.DS * 16 + off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def lin8(self, lin, value):
        self.mem.memory[lin] = value & 0xFF

    def lin16(self, lin, value):
        self.mem.memory[lin:lin + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def u16(self, lin):
        return int.from_bytes(self.mem.memory[lin:lin + 2], "little")

    def player(self, word, k, value):
        """Byte k of the player record of `word`."""
        self.lin8(PSEG * 16 + POFF + 0x14 * word + k, value)

    def country(self, country, k, value):
        """Byte k of the country record."""
        self.lin8(SQSEG * 16 + SQOFF + 0xBF * country + k, value)

    def squad(self, country, words):
        """The country's squad words 1.. (its record at DS:A917 + 0xBF country)."""
        base = SQSEG * 16 + SQOFF + 0xBF * country
        for k, w in enumerate(words, 1):
            self.lin16(base + 2 * k - 2, w)

    def fixture(self, kind, first, second):
        base = FXSEG * 16 + FXOFF
        self.mem.memory[base:base + 8] = bytes([0xFE, 0, kind, 0]) + first.to_bytes(2, "little") + \
            second.to_bytes(2, "little")

    def run(self, address, words=(), answer=None, variant=None):
        entry = port._module_registry("display").entries[address]
        for i, value in enumerate([0x5678] + ([0x9ABC] if entry.far else []) + list(words)):
            self.mem.memory[0x3000 + i * 2:0x3002 + i * 2] = (value & 0xFFFF).to_bytes(2, "little")
        self.mem._entries.append((0x3000, entry.far))
        try:
            value = entry.fn(self.mem, variant)
            if hasattr(value, "send"):
                gen, sent = value, None
                while True:
                    try:
                        request = gen.send(sent)
                    except StopIteration as stop:
                        value = stop.value
                        break
                    self.calls.append((request.target, request.args, request.ret_to, request.far))
                    if len(self.calls) > 5000:           # a loop that does not end (a test of a loop's bound)
                        raise AssertionError(f"more than 5000 calls, the last {request.target}")
                    sent = answer(request, self.mem) if answer else 0
                    self.mem.regs["ax"] = sent & 0xFFFF
        finally:
            self.mem._entries.pop()
        return value

    def targets(self):
        return [(t, ret) for t, _, ret, _ in self.calls]

    def args(self, target):
        return [a for t, a, _, _ in self.calls if t == target]

    def written(self, writer):
        lin = self.mem.lin(writer)
        return [(off, size, value) for off, size, value, at in self.writes if at == lin]


class Case(unittest.TestCase):
    """A test that cannot hang: a loop that does not end (a test of a loop's bound) fails after 20 s."""

    def setUp(self):
        if hasattr(signal, "SIGALRM"):
            def timed_out(signum, frame):
                raise AssertionError("the routine did not return within 20 s")
            signal.signal(signal.SIGALRM, timed_out)
            signal.alarm(20)

    def tearDown(self):
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)


def answers(table):
    """A responder from {target: value or [values in order]} (an unlisted target answers 0)."""
    queues = {k: (list(v) if isinstance(v, list) else v) for k, v in table.items()}

    def answer(request, mem):
        v = queues.get(request.target, 0)
        return v.pop(0) if isinstance(v, list) else v
    return answer


class Display(Case):
    def test_registry_has_the_eighty_eight_listing_returns(self):
        import json
        rows = json.loads((Path(__file__).resolve().parents[1] / 'experiments/E036-match-port/out/T73/static-inventory.json').read_text())
        reg = port._module_registry('display')
        self.assertEqual(set(reg.entries), {r['address'] for r in rows})
        self.assertEqual(len(reg.entries), 88)
        for row in rows:
            entry = reg.entries[row['address']]
            self.assertEqual(entry.ret, row['returns'][0] if row['returns'] else 'ret')

    def test_glyph_modes_keep_the_nested_slot_and_signed_clock(self):
        for mode, slot, clock, threshold, want in ((0, 1, 0, 0, 1), (1, 14, 0, 0, 65),
                (2, 11, 0, 0, 12), (2, 11, 1, 0, 11), (2, 12, 0, 0, 11),
                (2, 12, 0, 255, 12), (3, 11, 0, 0, 22), (3, 12, 0, 0, 21),
                (4, 1, 0, 0, 0x2F), (4, 11, 0, 0, 0x39), (4, 12, 0, 0, 0x2F),
                (255, 12, 0, 0, 0xA9)):
            r = Rig()
            r.ds8(0x66A, mode)
            r.lin16(PARENT - 2, slot)
            r.lin8(BP0 - 1, 0xA9)
            r.ds16(0x80F5 + slot * 0x16, 1)
            r.player(1, 6, 4)
            r.ds8(0x69A8 + 4, 65)
            r.ds8(0x8319, threshold)
            r.ds16(0x831B, clock)
            for off, value in ((0x6D4, 11), (0x6D5, 12), (0x6D2, 21), (0x6D3, 22)):
                r.ds8(off, value)
            got = r.run('0791:05C6', [PARENT])
            self.assertEqual(got & 255, want, (mode, slot, clock, threshold))

    def test_refresh_keeps_all_twenty_two_pitch_words(self):
        r = Rig()
        for off, value in ((0x832E, 4), (0x832F, 1), (0x8330, 12), (0x8331, 9)):
            r.ds8(off, value)
        def answer(c, mem):
            if c.target == '0791:045D':return int(c.args[0] in (1, 12))
            if c.target == '0791:05C6':return 42
            if c.target == '0791:2974':return int((c.args[1] - 0x80E8) // 0x16 >= 12)
            return 0
        r.run('0791:0691', answer=answer)
        for slot in range(1, 23):
            side = int(slot >= 12)
            want = ((9 if side else 12) << 8 | 1) if slot in (1, 12) else ((1 if side else 4) << 8 | 42)
            self.assertEqual(r.mem.ds16(0x80E8 + slot * 0x16 + 4), want)

    def grid(self, r):
        r.ds16(0x7C16, 0x100)
        r.ds16(0x7C18, 0x5000)
        r.ds16(0x7C1E, 0x100)
        r.ds16(0x7C20, 0x5200)
        r.ds16(0x640, 0x7FFF)
        r.ds8(0x880, 42)
        r.ds8(0x881, 43)

    def test_ball_preserves_old_cell_previous_point_and_new_occupancy(self):
        for member in (False, True):
            for occupied in (False, True):
                for high in (False, True):
                    r = Rig()
                    self.grid(r)
                    base = FXSEG * 16 + FXOFF
                    r.lin16(base, 0x0302)
                    r.lin16(base + 2, 0x0201)
                    r.lin8(base + 5, 7)
                    r.lin8(base + 0xD, int(high))
                    old = 0x100 + 0x90E + 160 + 4
                    new = 0x100 + 0x90E + 320 + 6
                    r.lin16(0x50000 + old, 0x076F)
                    r.lin16(0x52000 + old, 0x0720)
                    r.lin16(0x52000 + new, 0x0720)
                    r.lin16(0x50000 + new, 0x0601 if occupied else 0x0720)
                    def answer(c, mem):
                        if c.target == '23E4:08DF':mem.regs['eflags'] = 0 if member else 0x40
                        return 3 if c.target == '0791:835F' else 0
                    r.run('0791:8F10', [FXOFF, FXSEG], answer)
                    self.assertEqual(r.u16(0x50000 + old), 0x0720 if member else 0x076F)
                    self.assertEqual(r.u16(base + 2), 0x0302)
                    self.assertEqual(r.mem.memory[base + 4], 43 if high else 42)
                    self.assertEqual(r.u16(0x50000 + new), 0x0601 if occupied else 0x072B if high else 0x072A)

    def test_ball_offscreen_or_unchanged_skips_old_erase_and_travel_boundary(self):
        for point, previous, travel, want in ((0x7FFF, 0x7FFF, 2, 42), (0x0302, 0x0302, 2, 42),
                                             (0x0302, 0x7FFF, 3, 43)):
            r = Rig()
            self.grid(r)
            base = FXSEG * 16 + FXOFF
            r.lin16(base, point)
            r.lin16(base + 2, previous)
            r.lin8(base + 0xD, 1)
            r.run('0791:8F10', [FXOFF, FXSEG], answers({'0791:835F':travel}))
            self.assertEqual(r.args('23E4:08DF'), [])
            self.assertEqual(r.mem.memory[base + 4], want)

    def test_reset_sprite_keeps_quick_and_watched_state_writes(self):
        for quick in (False, True):
            r = Rig()
            self.grid(r)
            r.ds16(0x644, 0x0D01)
            r.ds8(0x9A3E, int(quick))
            at = 0x100 + 0x90E + 160
            r.lin16(0x52000 + at, 0x0742)
            r.lin16(0x50000 + at, 0x0641)
            r.run('0791:9079', [FXOFF, FXSEG])
            self.assertEqual(r.u16(FXSEG * 16 + FXOFF), 0x0D01)
            self.assertEqual(len(r.args('0791:8E24')), int(not quick))
            self.assertEqual(r.u16(0x50000 + at), 0x0641 if quick else 0x0742)

    def test_menu_copy_selects_and_preserves_the_whole_four_thousand_bytes(self):
        for used in (False, True):
            r = Rig()
            r.ds8(0xC1F, int(used))
            for off, seg in ((0x7C1E, 0x5000), (0x7C22, 0x5200), (0x7C1A, 0x5400)):
                r.ds16(off, 0x100)
                r.ds16(off + 2, seg)
            r.run('0791:A699', [FXOFF, FXSEG])
            self.assertEqual(r.args('23E4:025D'), [(0x5200 if used else 0x5000, 0x100, 0x5400, 0x100, 4000)])
            self.assertEqual(r.args('214B:0329'), [(FXSEG, FXOFF, r.mem.DS, 0xA96E)])

    def test_speaker_seed_helper_and_noise_keep_ordered_rng_calls(self):
        r = Rig()
        got = r.run('0791:94C9', [123], answers({'214B:0688':0xAB34}))
        self.assertEqual(got, 0xAB34)
        self.assertEqual(r.args('214B:0688'), [(r.mem.DS, 0x8336, 123)])
        for bound, first, speed, tone in ((0, 1, 1, False), (20, 20, 1, False),
                                        (20, 10, 0, False), (20, 10, 1, True), (20, 65534, 1, True)):
            r = Rig()
            r.ds16(0x832A, bound)
            r.lin8(GSEG * 16 + GOFF + 0x3F, speed)
            r.run('0791:94E8', answer=answers({'0791:94C9':[first, 300]}))
            self.assertEqual(r.args('0791:94C9'), [] if not bound else [(50,), (320,)] if tone else [(50,)])
            self.assertEqual(r.args('214B:1EBC'), [(400,)] if tone else [])
            self.assertEqual(len(r.args('214B:1E8D')), int(not tone))
            self.assertEqual(r.args('0791:0425'), [(speed,)])

    def test_text_cell_loops_keep_direction_attributes_and_zero_count(self):
        for backwards in (False, True):
            for count in (0, 1, 3):
                r = Rig()
                sbase = FXSEG * 16 + FXOFF
                dbase = GSEG * 16 + GOFF
                r.mem.memory[sbase:sbase + 3] = b'ABC'
                source = FXOFF + (count - 1 if backwards and count else 0)
                destination = GOFF + (2 * (count - 1) if backwards and count else 0)
                r.run('214B:0123' if backwards else '214B:00FF',
                      [count, 0x0570, source, FXSEG, destination, GSEG])
                self.assertEqual(bytes(r.mem.memory[dbase:dbase + count * 2]), b''.join(bytes([x, 0x70]) for x in b'ABC'[:count]))
                self.assertEqual(bool(r.mem.reg('eflags') & 0x400), backwards)

    def test_string_wrappers_preserve_coordinates_temporary_and_attribute(self):
        for address, backwards, set_attr in (('214B:01A3', True, False), ('214B:0205', True, True),
                                             ('214B:026D', False, False), ('214B:02C8', False, True)):
            r = Rig()
            r.ds16(0xA96E, GOFF)
            r.ds16(0xA970, GSEG)
            r.ds8(0xAAB2, 9)
            r.mem.memory[FXSEG * 16 + FXOFF:FXSEG * 16 + FXOFF + 4] = b'\x03ABC'
            def answer(c, mem):
                if c.target == '23E4:0644':
                    a, b, d, e, n = c.args
                    mem.memory[d * 16 + e:d * 16 + e + 4] = mem.memory[a * 16 + b:a * 16 + b + 4]
                return 0
            words = [0xA96E, r.mem.DS, 10, 4, FXOFF, FXSEG] + ([7] if set_attr else [])
            r.run(address, words, answer)
            target = '214B:0123' if backwards else '214B:00FF'
            self.assertEqual(r.args(target), [(GSEG, GOFF + 4 * 160 + 10 * 2 - 0xA2,
                                               0, BP0 - 0x100 + (3 if backwards else 1), 7 if set_attr else 9, 3)])
            self.assertEqual(r.mem.ds8(0xAAB2), 7 if set_attr else 9)

    def test_score_writer_preserves_both_pascal_results_and_rows(self):
        r = Rig()
        r.ds8(0x9B3C, 2)
        r.ds8(0x9B3D, 5)
        r.run('0791:0712', [FXOFF, FXSEG], answers({'214B:09DA':0, '214B:0205':0}))
        self.assertEqual(r.args('214B:09DA'), [(0, 5), (0, 2)])
        self.assertEqual(r.args('214B:0205'), [(0x70, 0, BP0 - 0x104, 2, 31, FXSEG, FXOFF),
                                               (0x70, 0, BP0 - 0x104, 4, 31, FXSEG, FXOFF)])

    def test_no_replay_boundary_clears_the_pending_change_flag(self):
        r = Rig()
        r.ds8(0x9B55, 1)
        r.run('0791:0C65')
        self.assertEqual(r.mem.ds8(0x9B55), 0)
        self.assertEqual(r.written('0791:0C6B'), [(0x9B55, 1, 0)])


    def test_snapshot_preserves_all_record_copies_flags_and_seed(self):
        r = Rig()
        r.ds16(0x9B34, 3)
        r.ds16(0x9B36, 4)
        r.squad(3, list(range(1, 21)))
        r.squad(4, [0] * 20)
        r.country(3, 0x2E, 130)
        r.country(4, 0x2E, 131)
        for ptr, seg in ((0xA91F,0x4C00),(0x9B74,0x5400),(0x9B78,0x5600),
                         (0x9B6C,0x5000),(0x9B70,0x5200),(0xA978,0x5800)):
            r.ds16(ptr, 0x100)
            r.ds16(ptr+2, seg)
        for word in range(21):r.lin8(0x52000 + 0x100 + word, word+1)
        r.lin8(0x56000 + 0x100 + 130, 65)
        r.lin8(0x56000 + 0x100 + 131, 66)
        r.lin16(0x58000 + 0x100, 4321)
        r.ds16(0x9B3A, 0x0205)
        r.ds16(0x9B3C, 0x0304)
        r.run('0791:15B9')
        moves = r.args('23E4:025D')
        self.assertEqual(len(moves), 51)
        self.assertEqual(len(r.args('23E4:0644')), 42)
        self.assertEqual(moves[0], (r.mem.DS,0x7C3E,r.mem.DS,0x8439,0x7FB))
        self.assertIn((r.mem.DS,0x9B08,r.mem.DS,0x9AE0,40), moves)
        self.assertEqual(r.mem.ds8(0x9970),65)
        self.assertEqual(r.mem.ds8(0x9971),66)
        self.assertEqual(r.mem.ds8(0x98E0),2)
        self.assertEqual(r.mem.ds8(0x98E0+20),1)
        self.assertEqual(r.mem.ds16(0x9B30),3)
        self.assertEqual(r.mem.ds16(0x9B32),4)
        self.assertEqual(r.mem.ds16(0x9B38),0x0205)
        self.assertEqual(r.mem.ds16(0x9B3E),0x0304)
        self.assertEqual(r.mem.ds16(0x9974),4321)
        self.assertEqual(r.args('214B:0329'),[(r.mem.DS,0x6120,r.mem.DS,0xA96A)])

    def test_summary_keeps_the_board_key_site_and_key_clear(self):
        for flag in (0,1):
            r = Rig()
            r.ds8(0xA976,65)
            sites=[]
            r.mem._key=lambda site: sites.append(site) or 13
            r.run('0791:0106',[flag],answer=lambda c, mem: mem._key(c.ret_to) if c.target=='214B:08DD' else 0)
            self.assertEqual(r.args('214B:08DD'),[()] if flag else [])
            self.assertEqual(sites,['0791:041A'] if flag else [])
            self.assertEqual(r.mem.ds8(0xA976),0)
            self.assertEqual(r.written('0791:041A'),[(0xA976,1,0)])


    def test_lineup_body_keeps_template_all_eleven_rows_and_formation_abi(self):
        r=Rig();r.ds16(0x9B34,3);r.ds16(0x9B36,4)
        r.squad(3,list(range(1,12)));r.squad(4,list(range(21,32)))
        for off,value in ((0x8C6,2),(0x8C7,40),(0x8C8,4),(0x8C9,42),(0x8CA,3),(0x8CB,41)):
            r.ds8(off,value)
        r.run('0791:A75D',answer=answers({'1771:0F58':0xABCD,'1771:0E6C':0x1200,'0791:A6E4':9}))
        self.assertEqual(r.args('0791:A699'),[(r.mem.DS,0x534A)])
        self.assertEqual(r.args('1771:0E6C'),[(3,),(4,)])
        self.assertEqual(r.args('1771:0F58'),[(3,8,2),(4,8,40),(9,7,38)])
        self.assertEqual(r.args('1771:2F37'),[(i,i+12,4) for i in range(1,12)]+
                         [(20+i,i+12,42) for i in range(1,12)])
        self.assertEqual(r.args('214B:0205'),[(0xAB07,0,BP0-0x107,0x120B,3,r.mem.DS,0xA96E),
                                            (0xAB07,0,BP0-0x107,0x120B,41,r.mem.DS,0xA96E)])

    def test_replay_no_path_preserves_the_original_question_call(self):
        from original_match.port.mem import PortError
        for enabled in (False,True):
            r=Rig();r.ds8(0x9B55,1);r.ds8(0xC1E,1)
            r.lin8(GSEG*16+GOFF+0x41,int(enabled))
            r.run('0791:0C65',answer=answers({'0791:0B7C':0}))
            self.assertEqual(r.mem.ds8(0x9B55),0)
            self.assertEqual(r.args('0791:0B7C'),[(r.mem.seg(0x0791),0xC42)] if enabled else [])
        r=Rig();r.ds8(0xC1E,1);r.lin8(GSEG*16+GOFF+0x41,1)
        with self.assertRaises(PortError):r.run('0791:0C65',answer=answers({'0791:0B7C':1}))
        r=Rig();r.ds8(0xC1E,0);r.lin8(GSEG*16+GOFF+0x41,1)
        with self.assertRaises(PortError):r.run('0791:0C65')


    def test_attribute_and_highlight_cells_keep_zero_negative_and_direction_behavior(self):
        for count in (0,1,3,65535):
            r=Rig();r.mem.regs.update(ax=0xABCD,cx=0x1234,eflags=0x602)
            base=GSEG*16+GOFF;r.mem.memory[base:base+6]=bytes([65,7,66,7,67,7])
            r.run('214B:00DB',[count,0x0570,GOFF,GSEG])
            expected=bytes([65,0x70,66,0x70,67,0x70]) if count==3 else bytes([65,0x70,66,7,67,7]) if count==1 else bytes([65,7,66,7,67,7])
            self.assertEqual(bytes(r.mem.memory[base:base+6]),expected)
            self.assertEqual(r.mem.reg('ax'),0x0570 if 0<count<32768 else 0xABCD)
            self.assertEqual(bool(r.mem.reg('eflags')&0x400),not(0<count<32768))
        r=Rig();r.ds16(0xA96E,GOFF);r.ds16(0xA970,GSEG)
        r.run('214B:13C5',[12,10,4])
        self.assertEqual(r.args('214B:00DB'),[(GSEG,GOFF+4*160+20-0xA2,0x70,12)])

    def test_player_card_zero_guard_and_status_routes_keep_performance_tail(self):
        r=Rig();r.run('1771:42BC',[0])
        self.assertEqual(r.args('214B:0329'),[(r.mem.DS,0x486E,r.mem.DS,0xA96E)])
        self.assertEqual(r.args('1771:3827'),[])
        for status,energy,text in ((0,20,0x42A6),(0x80,20,0x426A),(0,0,0x4274),
                                   (0x10,20,0x427C),(0x20,20,0x4283),(0x04,20,0x428C)):
            r=Rig();r.ds8(0xC1E,1)
            for field,v in ((0,3),(1,25),(6,4),(7,4),(12,20),(13,20),(14,energy),(16,status)):
                r.player(1,field,v)
            def answer(c,mem):
                if c.target=='214B:0C57':return int(bool(c.args[1]&(1<<(c.args[0]-1))))
                return {'1771:2FAD':75,'1771:3041':0,'1771:3088':0,'1771:2FFB':16,'1771:30D9':4,'1771:3A82':5}.get(c.target,0)
            r.run('1771:42BC',[1],answer)
            self.assertEqual(r.args('1771:3827'),[(1,8,60)])
            self.assertEqual(r.args('1771:3947'),[(1,11,11)])
            self.assertEqual(r.args('1771:3BD3'),[(1,)])
            displayed=[args[2] if target=='214B:0205' else args[1] for target,args,ret,far in r.calls if target in ('214B:01A3','214B:0205') and len(args)>=6]
            self.assertIn(text,displayed,(status,energy,displayed))

    def test_tactics_panel_keeps_keeper_swaps_and_override_string_frames(self):
        for keeper,own in ((False,0),(True,255)):
            r=Rig();r.ds8(0xC1E,1)
            for field,v in ((0,3),(6,0 if keeper else 4),(15,own)):r.player(1,field,v)
            r.country(3,0x2D,0xAA)
            def answer(c,mem):
                if c.target=='214B:0C57':return int(bool(c.args[1]&(1<<(c.args[0]-1))))
                return 0
            r.run('1771:3BD3',[1],answer)
            self.assertEqual(len(r.args('214B:01A3')),4)
            self.assertEqual(len(r.args('23E4:06B7')),4 if own else 0)
            moves=r.args('214B:003C')
            self.assertEqual(len(moves),4 if keeper else 0)
            if keeper:
                self.assertEqual(moves[0],(r.mem.DS,0x6AC0,0,BP0-0x108,256))
                self.assertEqual(moves[-1],(0,BP0-0x108,r.mem.DS,0x6AC0,256))
            self.assertEqual(r.args('1771:3B3F'),[(BP0,)])

    def test_tactics_mark_target_uses_both_names_and_zone_marker(self):
        r=Rig();r.ds8(0xC1E,1);r.ds16(0x9B36,3);r.ds8(0xAAB2,7)
        for field,v in ((0,3),(6,4),(15,0),(16,0x40)):r.player(1,field,v)
        r.player(2,6,5);r.ds16(0x9A3E+40+2*5,2)
        def answer(c,mem):
            if c.target=='214B:0C57':return int(bool(c.args[1]&(1<<(c.args[0]-1))))
            return 5 if c.target=='1771:3A82' else 0
        r.run('1771:3BD3',[1],answer)
        self.assertEqual(r.args('1771:2EE5'),[(2,16,43)])
        self.assertEqual(len(r.args('214B:02C8')),1)
        self.assertEqual(r.args('214B:02C8')[0][2],0x3BD1)

    def test_performance_buckets_keep_encoded_scores_and_sentinel(self):
        for performance,want in ((0x7FFF,99),(4,1),(5,2),(54,2),(55,3),(104,3),(105,4),
                                  (155,5),(205,6),(255,7),(355,8),(455,9),(10055,3)):
            r=Rig();r.ds8(0xE86,99);r.lin16(PSEG*16+POFF+20+18,performance)
            r.run('1771:3827',[60,8,1],answers({'1771:2E20':7}))
            self.assertEqual(r.mem.ds8(0xE86),want,performance)
            self.assertEqual(len(r.args('214B:01A3')),int(performance!=0x7FFF))

    def test_skill_bars_keep_all_twelve_unclamped_unsigned_products(self):
        r=Rig();r.player(1,4,255);r.player(1,5,0);r.player(1,7,0)
        for k in range(1,13):r.ds8(0x6D25+k,k-1);r.ds8(0x6DCD+k-1,k+1)
        r.ds16(0xA96E,GOFF);r.ds16(0xA970,GSEG)
        r.run('1771:3947',[10,4,1])
        self.assertEqual(len(r.args('214B:00DB')),12)
        self.assertEqual([a[-1] for a in r.args('214B:00DB')],list(range(2,14)))


class EventProjection(unittest.TestCase):
    def modules(self):
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments/E036-match-port'))
        import family, records
        return family, records

    def test_only_the_full_time_screen_field_is_projected_without_mutation(self):
        import copy
        family, records = self.modules()
        events = [('minute', 90, (2, 1), {'seed':123}),
                  ('full_time', 90, (2, 1), {'seed':123, 'screen_sha256':'a', 'statistics':{'shots':[2, 1]}})]
        changed = copy.deepcopy(events)
        changed[1][3]['screen_sha256'] = 'b'
        saved = copy.deepcopy(events)
        self.assertNotEqual(records.events_digest(events), records.events_digest(changed))
        self.assertEqual(family.display_events_digest(events), family.display_events_digest(changed))
        self.assertEqual(events, saved)
        self.assertEqual(family.display_events_digest(events)[0], 2)

    def test_other_event_fields_and_metadata_still_change_the_digest(self):
        import copy
        family, records = self.modules()
        event = ('full_time', 90, (2, 1), {'seed':123, 'screen_sha256':'a', 'statistics':{'shots':[2, 1]},
                                          'decision':{'context':'half_time'}, 'nested':{'screen_sha256':'x'}})
        baseline = family.display_events_digest([event])
        changed = [('goal', event[1], event[2], event[3]), (event[0], 91, event[2], event[3]),
                   (event[0], event[1], (3, 1), event[3])]
        for key, value in [('seed',124), ('statistics',{'shots':[3, 1]}),
                           ('decision',{'context':'pause'}), ('nested',{'screen_sha256':'y'})]:
            data = copy.deepcopy(event[3]);data[key] = value
            changed.append((event[0], event[1], event[2], data))
        for other in changed:
            self.assertNotEqual(family.display_events_digest([other]), baseline)
        self.assertNotEqual(family.display_events_digest([event, event]), baseline)
        a = [('minute', 90, (2, 1), {'screen_sha256':'a'})]
        b = [('minute', 90, (2, 1), {'screen_sha256':'b'})]
        self.assertNotEqual(family.display_events_digest(a), family.display_events_digest(b))

class StrictDisplayProfile(unittest.TestCase):
    def setup_profile(self, directory):
        import json
        from tests.test_e036_compare import family, compare_module
        path = Path(directory) / 'profile.json'
        value = {'schema':1, 'mask':[['DS', 0x9974, 2]],
                 'reference':str(Path(directory) / 'reference.jsonl'), 'proof':'synthetic test proof'}
        path.write_text(json.dumps(value))
        return family, compare_module, path, value

    def patched(self, family, compare, path):
        import contextlib
        from unittest import mock
        stack = contextlib.ExitStack()
        for module in {family, compare.family_runner}:
            stack.enter_context(mock.patch.object(module, 'DISPLAY_PROFILE', path))
        return stack

    def test_profile_is_ds_only_and_missing_is_refused(self):
        import tempfile, json
        with tempfile.TemporaryDirectory() as d:
            family, compare, path, value = self.setup_profile(d)
            with self.patched(family, compare, path):
                self.assertEqual(family.read_display_profile(), value)
                for mask in ([['P', 10, 2]], [['DS', 65535, 2]], [['DS', 12, 2], ['DS', 11, 2]]):
                    path.write_text(json.dumps({**value, 'mask':mask}))
                    with self.assertRaises(family.Refused):family.read_display_profile()
                path.unlink()
                with self.assertRaises(family.Refused):family.read_display_profile()
                with self.assertRaises(compare.Malformed):
                    compare.candidate_display_profile({'id':{'ports':['display'],'mask':value['mask']}}, True)

    def test_display_cli_gets_only_the_declared_mask_and_legacy_default_stays_empty(self):
        import tempfile, json
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            family, compare, path, value = self.setup_profile(d)
            with self.patched(family, compare, path), mock.patch('original_match.assets.check_cache'):
                args = family.parser().parse_args(['--family','F40','--out',str(Path(d)/'out.jsonl')])
                self.assertEqual(family.prepare(args)[1], [])
                with mock.patch.object(family, 'ports_of', return_value=['display.any-variant']):
                    self.assertEqual(family.prepare(args)[1], value['mask'])
                    wrong = Path(d)/'wrong.json';wrong.write_text(json.dumps([['DS',12,2]]))
                    args.mask = str(wrong)
                    with self.assertRaises(family.Refused):family.prepare(args)
                    correct = Path(d)/'correct.json';correct.write_text(json.dumps(value['mask']))
                    args.mask = str(correct)
                    self.assertEqual(family.prepare(args)[1], value['mask'])

    def test_strict_profile_compares_legacy_skipped_ds_blocks(self):
        import tempfile, copy
        from tests.test_e036_compare import record, F40, dg
        with tempfile.TemporaryDirectory() as d:
            family, compare, path, value = self.setup_profile(d)
            with self.patched(family, compare, path):
                original = record(F40[0], mask=value['mask'])
                changed = copy.deepcopy(original)
                changed['board']['screen_sha256'] = dg('other screen')
                self.assertEqual(compare.differences(original,changed,True,strict_display=True), [])
                changed['after']['ds'][59] = dg('changed bytes not in the proved mask')
                self.assertEqual(compare.differences(original,changed,True), [])
                self.assertTrue(compare.differences(original,changed,True,strict_display=True))
                changed['ports']=['display']
                self.assertEqual(compare.candidate_display_profile({'x':changed},True), value)
                changed['mask']=[]
                with self.assertRaises(compare.Malformed):compare.candidate_display_profile({'x':changed},True)

    def test_profile_reference_missing_or_mask_mismatched_is_malformed(self):
        import tempfile, json, contextlib, io
        from tests.test_e036_compare import record, F40
        with tempfile.TemporaryDirectory() as d:
            family, compare, path, value = self.setup_profile(d)
            candidate = Path(d)/'candidate.jsonl'
            rows=[record(mid, mask=value['mask']) for mid in F40]
            for row in rows:row.update(ports=['display'],variant=None,port_calls={'0791:0106':1})
            candidate.write_text(''.join(json.dumps(row)+'\n' for row in rows))
            reference=Path(value['reference'])
            args=['--family','F40','--no-screen','--candidate',str(candidate)]
            with self.patched(family,compare,path), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(compare.main(args),2)
                reference.write_text(''.join(json.dumps(record(mid))+'\n' for mid in F40))
                self.assertEqual(compare.main(args),2)
                reference.write_text(''.join(json.dumps(record(mid,mask=value['mask']))+'\n' for mid in F40))
                self.assertEqual(compare.main(args),0)
                other = Path(d)/'other-reference.jsonl'
                other.write_text(reference.read_text())
                self.assertEqual(compare.main(args+['--reference',str(other)]),2)
                self.assertEqual(compare.main(args+['--reference',str(reference)]),0)
                path.unlink()
                self.assertEqual(compare.main(args),2)

    def test_empty_declared_profile_is_selected_separately_from_raw_empty_mask(self):
        import tempfile,json
        from unittest import mock
        from tests.test_e036_compare import record,F40,FAMILIES
        with tempfile.TemporaryDirectory() as d:
            family,compare,path,value=self.setup_profile(d)
            value['mask']=[];path.write_text(json.dumps(value))
            declared=path.with_name('mask.json');declared.write_text('[]')
            other=Path(d)/'other-empty.json';other.write_text('[]')
            with self.patched(family,compare,path),mock.patch('original_match.assets.check_cache'):
                self.assertEqual(family.read_display_profile()['mask'],[])
                self.assertTrue(family.uses_display_projection([],selected=True))
                self.assertFalse(family.uses_display_projection([],selected=False))
                args=family.parser().parse_args(['--family','F40','--out',str(Path(d)/'out.jsonl')])
                self.assertFalse(family.display_profile_selected(args))
                self.assertEqual(family.prepare(args)[1],[])
                args.mask=str(other)
                self.assertFalse(family.display_profile_selected(args))
                args.mask=str(declared)
                self.assertTrue(family.display_profile_selected(args))
                self.assertEqual(family.prepare(args)[1],[])
                with mock.patch.object(family,'ports_of',return_value=['display']):
                    args.mask=None
                    self.assertTrue(family.display_profile_selected(args))
                    self.assertEqual(family.prepare(args)[1],[])
                self.assertEqual(compare.candidate_display_profile({'x':{'ports':['display'],'mask':[]}},True),value)
                self.assertIsNone(compare.candidate_display_profile({'x':{'mask':[]}},True))
                spec=FAMILIES['F40'].matches[0]
                raw=family.checkpoint_key(spec,[],[],[])
                projected=family.checkpoint_key(spec,[],[],[],display_profile=True)
                self.assertNotIn('display_profile',raw)
                self.assertEqual(projected,{**raw,'display_profile':1})

    def test_selected_profile_mode_reaches_single_and_pool_workers(self):
        import tempfile
        from unittest import mock
        from tests.test_e036_compare import family,FAMILIES,record
        spec=FAMILIES['F40'].matches[0]
        with tempfile.TemporaryDirectory() as d, mock.patch('original_match.assets.reference_image',return_value=b'input'), \
             mock.patch('original_match.Image.from_bytes',return_value=object()), \
             mock.patch.object(family,'run_match',return_value=record(spec.id)) as run:
            family.run_family([spec],str(Path(d)/'out.jsonl'),mask=[],display_profile=True,say=lambda s:None)
            self.assertIs(run.call_args.kwargs['display_profile'],True)
            with mock.patch.dict(family._worker,{},clear=True):
                family._init_worker('.cache',[],[],300,display_profile=True)
                family._run_in_worker(spec.id)
                self.assertIs(run.call_args.kwargs['display_profile'],True)

class CommentaryMemoryTests(unittest.TestCase):
    def test_disabled_record_retains_only_pointer_frame(self):
        r=Rig();r.ds8(0x7C38+12,255)
        r.run('0791:1829',(33,4,2))
        self.assertEqual(r.calls,[])
        self.assertEqual(r.u16(BP0-0x28),0x7C38+12)
        self.assertEqual(r.u16(BP0-0x26),r.mem.DS)

    def test_leading_and_two_trailing_name_markers_follow_listing_calls(self):
        r=Rig();r.ds8(0x7C38,3);r.ds16(0x7C39,2);r.ds16(0x7C3B,4)
        r.ds16(0x9B6C,0x600);r.ds16(0x9B6E,0x400)
        lines=iter((b'\x03\x01a\x01',b'\x02b\x01',b'\x02c\x02',b'\x02ok'))
        def answer(q,m):
            if q.target=='23E4:0644':
                data=next(lines);seg,off=q.args[2:4]
                m.memory[seg*16+off:seg*16+off+len(data)]=data
            return 0
        r.run('0791:1829',(33,4,0),answer=answer)
        stores=[q for q in r.calls if q[0]=='23E4:0644']
        self.assertEqual([q[1][-1] for q in stores],[35]*4)
        self.assertEqual([q[2] for q in stores],['0791:1873','0791:18BD','0791:190E','0791:195F'])
        names=[q for q in r.calls if q[0] in ('23E4:062A','23E4:06B7') and q[1][0]==0x400]
        self.assertEqual([q[1] for q in names],[(0x400,0x616),(0x400,0x616),(0x400,0x62C)])
        self.assertEqual(len(r.args('23E4:06B7')),5)

    def test_padding_and_top_rows_update_both_buffers(self):
        for row,expected in ((4,[0xA96A,0xA972]),(5,[0xA96A])):
            for length in (0,3,30,35):
                with self.subTest(row=row,length=length):
                    r=Rig();r.ds8(0x7C38,3);r.ds8(0x7C3D,1);r.ds8(0x832F,0xA5)
                    def answer(q,m):
                        if q.target=='23E4:0644':
                            seg,off=q.args[2:4];data=bytes([length])+b'x'*length
                            m.memory[seg*16+off:seg*16+off+len(data)]=data
                        return 0
                    r.run('0791:1829',(33,row,0),answer=answer)
                    output=[q for q in r.calls if q[0]=='214B:02C8']
                    self.assertEqual([q[1][-1] for q in output],expected)
                    self.assertEqual([q[1][0] for q in output],[0xA5]*len(expected))
                    self.assertEqual([q[1][3:5] for q in output],[(row,33)]*len(expected))
                    fills=[q[1][2:] for q in r.calls if q[0]=='214B:0018']
                    self.assertEqual(fills,[(30-length,32)] if length<30 else [])
                    self.assertEqual(r.mem.u8(BP0-0x24),30)

class ClockDigitMemoryTests(unittest.TestCase):
    def test_vertical_segment_uses_parent_colour_and_adjacent_rows(self):
        r=Rig();r.lin16(PARENT+4,0x1200);r.lin16(PARENT-10,0x100);r.lin16(PARENT-8,0x400)
        r.run('0791:0481',(PARENT,75))
        self.assertEqual(r.u16(0x4000+0x100+148),0x12DC)
        self.assertEqual(r.u16(0x4000+0x100+308),0x12DB)

    def test_seven_segment_table_drives_three_fills_and_four_verticals(self):
        r=Rig();r.lin16(PARENT+4,0x1200);r.lin16(PARENT-10,0x100);r.lin16(PARENT-8,0x400)
        for i in range(1,8):r.ds8(0x644+i*10+ord('8'),1);r.ds16(0x6C2+i*2,i*80)
        r.run('0791:04C9',(PARENT,75,ord('8')))
        self.assertEqual(len(r.args('214B:0000')),3)
        self.assertEqual([a[2:] for a in r.args('214B:0000')],[(4,0x12DF)]*3)
        self.assertEqual(r.args('0791:0481'),[(75+i*80,PARENT) for i in range(4,8)])
        self.assertEqual(r.u16(BP0-2),7)

    def test_formatter_retains_colour_shift_and_one_or_two_digit_calls(self):
        for text,columns in ((b'7',[75]),(b'90',[69,75])):
            with self.subTest(text=text):
                r=Rig();r.ds16(0xA96A,0x100);r.ds16(0xA96C,0x400)
                def answer(q,m):
                    if q.target=='23E4:0644':
                        seg,off=q.args[2:4];data=bytes([len(text)])+text
                        m.memory[seg*16+off:seg*16+off+len(data)]=data
                    return 0
                r.run('0791:054C',(0x12,90),answer=answer)
                self.assertEqual(r.u16(BP0+4),0x1200)
                self.assertEqual([a[1] for a in r.args('0791:04C9')],columns)
                self.assertEqual([a[0]&255 for a in r.args('0791:04C9')],list(text))

class DelayMemoryTests(unittest.TestCase):
    def test_busy_wait_removed_but_final_unsigned_count_frame_preserved(self):
        for count in (0,1,5,65535):
            with self.subTest(count=count):
                r=Rig();r.ds16(0xA9FF,3);r.ds16(0xAA01,1)
                for off in (-8,-6,-4,-2):r.lin16(BP0+off,0xCAFE)
                r.run('214B:1E09',(count,))
                expected=[count,3,1,count] if count else [0xCAFE]*4
                self.assertEqual([r.u16(BP0+off) for off in (-8,-6,-4,-2)],expected)
                self.assertEqual(r.calls,[])

class NoticeMemoryTests(unittest.TestCase):
    def test_notice_uses_both_players_and_preserves_wait_key_restore_chain(self):
        for key in (0,1):
            with self.subTest(key=key):
                r=Rig();r.player(7,6,2);r.player(9,6,4)
                r.ds16(0x9B6C,0x100);r.ds16(0x9B6E,0x400)
                r.ds16(0xA96E,0x200);r.ds16(0xA970,0x500)
                r.ds16(0xA96A,0x300);r.ds16(0xA96C,0x600)
                r.run('0791:C50C',(7,9),answer=answers({'1771:2E20':[0x12,0x34],'214B:0723':key}))
                self.assertEqual(r.args('1771:2E20'),[(9,4),(7,2)])
                self.assertEqual(r.args('214B:0205'),[(0x12,0x400,0x163,25,29,r.mem.DS,0xA96E)])
                self.assertEqual(r.args('214B:02C8'),[(0x34,0x400,0x14D,25,38,r.mem.DS,0xA96E)])
                self.assertEqual(r.args('214B:003C'),[(0x500,0x1100,0x600,0x1200,160)])
                self.assertEqual(r.args('0791:CC2E'),[(300,)])
                self.assertEqual(len(r.args('214B:08DD')),key)
                self.assertEqual(r.targets()[-1],('214B:0643','0791:C5D6'))

class RemovedBodyDispositionTests(unittest.TestCase):
    def test_declared_removals_preserve_memory_registers_and_void_return(self):
        # This visits Python removals, not the original UI branch PCs. ALL
        # comparison separately proves their combined removal in declared states.
        registry=port._module_registry('display')
        for address,entry in registry.entries.items():
            if not entry.stub:continue
            for words in ((),(0,)*12,(65535,)*12):
                with self.subTest(address=address,words=words):
                    r=Rig();r.mem.regs.update(ax=0xA55A,dx=0x5AA5,eflags=0x602)
                    r.run(address,words)
                    before=bytes(r.mem.memory);registers=dict(r.mem.regs)
                    self.assertIsNone(r.run(address,words))
                    self.assertEqual(bytes(r.mem.memory),before)
                    self.assertEqual(r.mem.regs,registers)
                    self.assertEqual(r.writes,[])
                    self.assertEqual(r.calls,[])

class UnreachedStateBranchTests(unittest.TestCase):
    def test_empty_statistics_bar_and_nonempty_reached_twin(self):
        for first,second,want in ((0,0,[]),(1,65535,[]),(1,3,[18,6])):
            with self.subTest(first=first,second=second):
                r=Rig();r.lin16(0x40100,first);r.lin16(0x40102,second)
                r.ds16(0xA96E,0x200);r.ds16(0xA970,0x500)
                try:r.run('0791:006C',(0,4,0x100,0x4000))
                except ZeroDivisionError:self.fail('an empty bar must bypass division')
                self.assertEqual([a[-1] for a in r.args('214B:00DB')],want)

    def test_empty_squad_row_and_nonempty_reached_twin(self):
        for word,want in ((0,[]),(1,[(1,4,2)])):
            r=Rig();r.run('1771:2F37',(2,4,word))
            self.assertEqual(r.args('1771:2EE5'),want)
            self.assertEqual(r.u16(BP0-4),POFF+20*word)

    def test_performance_brightness_uses_live_slot_then_status_bit(self):
        for slot,status,want in ((11,0,15),(12,0,7),(12,4,15)):
            with self.subTest(slot=slot,status=status):
                r=Rig();r.ds8(0xC1F,1);r.player(1,16,status);r.lin16(PSEG*16+POFF+20+18,500)
                def answer(q,m):
                    if q.target=='1771:3A82':return slot
                    if q.target=='214B:0C57':return int(bool(q.args[1]&(1<<(q.args[0]-1))))
                    return 7 if q.target=='1771:2E20' else 0
                r.run('1771:3827',(60,8,1),answer=answer)
                self.assertEqual(r.mem.ds8(0xAAB2),want)

    def test_mark_text_match_flag_and_side_flag_branches(self):
        for live,flag,source in ((0,0,0xE90),(0,1,0xE9B),(1,0,0xE90),(1,1,0x3AD5)):
            r=Rig();r.ds8(0xC1E,live);r.run('1771:3AE2',(PARENT,flag))
            a=r.args('214B:01A3')[0]
            self.assertEqual(a[1],source)
            self.assertEqual(a[0],r.mem.seg(0x1771) if live and flag else r.mem.DS)

    def test_mark_row_position_zone_and_country_default_branches(self):
        for position,status,want_zone in ((1,64,None),(2,64,True),(2,0,False)):
            r=Rig();r.lin16(PARENT+4,1);r.player(1,6,position);r.player(1,16,status)
            r.player(1,0,3);r.country(3,0x2D,128)
            def answer(q,m):return int(bool(q.args[1]&(1<<(q.args[0]-1))))
            r.run('1771:3B3F',(PARENT,),answer=answer)
            if want_zone is None:self.assertEqual(r.calls,[])
            elif want_zone:self.assertEqual([a[1] for a in r.args('214B:01A3')],[0x3B30])
            else:self.assertEqual(r.args('1771:3AE2'),[(1,BP0)])

    def test_tactics_nonmatch_default_mark_row_skips_live_slot_lookup(self):
        r=Rig();r.ds8(0xC1E,0);r.player(1,6,4)
        r.run('1771:3BD3',(1,))
        self.assertEqual(r.args('1771:3A82'),[])
        self.assertEqual(r.args('1771:3B3F'),[(BP0,)])

    def test_card_two_feet_yellow_card_and_nonmatch_selection_label(self):
        r=Rig();r.player(1,16,8);r.player(1,14,1)
        def answer(q,m):
            if q.target=='214B:0C57':return int(bool(q.args[1]&(1<<(q.args[0]-1))))
            return {'1771:3041':1,'1771:3A82':5}.get(q.target,0)
        r.run('1771:42BC',(1,),answer=answer)
        self.assertEqual(r.args('1771:3088'),[])
        self.assertIn(0x425D,[a[1] for a in r.args('214B:026D')])
        self.assertIn((14,r.mem.seg(0x1771),0x4268,10,40,r.mem.DS,0xA96E),r.args('214B:02C8'))
        self.assertIn(0x4298,[a[1] for a in r.args('214B:01A3')])

    def test_message_special_colour_and_yes_no_highlight_twins(self):
        for special,want in ((0,0x27),(1,0x82)):
            r=Rig();r.ds8(0x7922,0x27);r.ds8(0x7923,0x70)
            positions=iter((special,5))
            def answer(q,m):
                if q.target=='23E4:0644':
                    seg,off=q.args[2:4];m.memory[seg*16+off:seg*16+off+4]=b'\x03yes'
                if q.target=='23E4:06E3':return next(positions)
                return 0
            r.run('214B:0350',(0xA96E,r.mem.DS,0x100,0x400,25),answer=answer)
            self.assertEqual(r.args('214B:02C8')[0][0],want)
            self.assertEqual([a[-2:] for a in r.args('214B:00DB')],[(0x70,1),(0x70,1)])

class ToneMemoryTests(unittest.TestCase):
    def test_tone_divisor_argument_and_return_high_byte_are_preserved(self):
        for frequency in (1,440,32768,65535):
            r=Rig();r.ds8(0xA9FC,0)
            def answer(q,m):
                if q.target=='23E4:0294':
                    dividend=(m.reg('dx')<<16)|m.reg('ax')
                    divisor=(m.reg('bx')<<16)|m.reg('cx')
                    quotient=dividend//divisor;m.regs['dx']=quotient>>16
                    return quotient&65535
                return 0
            r.run('214B:1EBC',(frequency,),answer=answer)
            quotient=0x1234DD//frequency;low=quotient&65535
            self.assertEqual(r.u16(BP0+6),low)
            self.assertEqual(r.mem.reg('ax'),(low&0xFF00)|(low>>8))
            self.assertEqual(r.mem.reg('dx'),quotient>>16)
            self.assertEqual(r.targets(),[('214B:1E75','214B:1ECA'),('23E4:0294','214B:1EDE')])

    def test_disabled_sound_skips_division_even_for_zero_frequency(self):
        r=Rig();r.ds8(0xA9FC,1);r.mem.regs.update(ax=0xBEEF,dx=0x1234)
        r.run('214B:1EBC',(0,))
        self.assertEqual(r.calls,[])
        self.assertEqual(r.u16(BP0+6),0)
        self.assertEqual(r.u16(BP0),0x1234)
        self.assertEqual((r.mem.reg('ax'),r.mem.reg('dx')),(0xBEEF,0x1234))

if __name__ == '__main__':
    unittest.main()
