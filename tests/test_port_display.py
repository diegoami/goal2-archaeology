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

if __name__ == '__main__':
    unittest.main()
