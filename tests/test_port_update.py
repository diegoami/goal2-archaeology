"""T72: synthetic listing-value branches and reached boundary twins."""
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
        entry = port._module_registry("update").entries[address]
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


class Update(Case):
    def test_registry_contract(self):
        self.assertEqual(set(port._module_registry("update").entries), {
            "0791:B7FA", "0791:B6CC", "0791:B71C", "0791:BA4E", "0791:B27F", "0791:B364",
            "1771:10E7", "1771:3558", "1771:3651", "1771:5A38", "1771:5A8F", "1771:5C60"})

    def test_confidence_signed_clips_and_word_wrap(self):
        from model.confidence import change
        for before in (0, 1, 20, 32, 128, 255):
            for delta in (-32768, -40, -1, 0, 1, 40, 32767):
                r = Rig()
                r.player(1, 0xC, before)
                r.run("0791:B364", [delta, 1])
                self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0xC], change(before, delta))

    def test_manager_signed_clips_and_word_wrap(self):
        for before in (0, 1, 127, 128, 129, 255):
            for delta in (-32768, -200, -1, 0, 1, 200, 32767):
                r = Rig()
                r.ds16(0xA91F, 0x20)
                r.ds16(0xA921, 0x5000)
                base = 0x50000 + 0x20 + 3 * 130 + 2
                r.lin8(base, before)
                r.run("0791:B6CC", [delta, 130])
                v = ((before - 256 if before >= 128 else before) + delta) & 0xFFFF
                v = v - 65536 if v >= 32768 else v
                self.assertEqual(r.mem.memory[base], min(127, max(-127, v)) & 255)

    def test_status_ban_served_red_and_two_bookings(self):
        for initial in (0, 0x80, 0x20, 0x10, 0x18, 0x38, 0xFF):
            r = Rig()
            r.player(1, 0x10, initial)
            def reply(c, mem):
                if c.target == "214B:0C57":
                    bit, value = c.args
                    return int(bool(value & (1 << (bit - 1))))
                if c.target in ("214B:0C79", "214B:0CA1"):
                    bit, seg, off = c.args
                    at = seg * 16 + off
                    mask = 1 << (bit - 1)
                    v = mem.memory[at]
                    mem.memory[at] = (v | mask) if c.target.endswith('0C79') else (v & ~mask)
                return 0
            r.run("0791:B27F", [1], reply)
            expected = initial & ~0x80
            if initial & 0x20:
                expected |= 0x80
            expected &= ~0x20
            if initial & 0x10:
                expected ^= 0x08
                if initial & 0x08:
                    expected |= 0x80
            expected &= ~0x10
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0x10], expected)
            self.assertEqual(r.args("214B:0CA1")[0][0], 8)
            self.assertEqual(r.args("214B:0CA1")[-1][0], 5)

    def test_country_rating_matches_model_wrapping_and_signed_division(self):
        from model.confidence import country_rating
        for continent, rank, world in ((1, 1, 1), (4, 32, 128), (5, 34, 130), (255, 255, 255)):
            r = Rig()
            for field, val in ((0x2C, continent), (0x2A, rank), (0x2B, world)):
                r.country(3, field, val)
            got = r.run("1771:10E7", [3])
            self.assertEqual(got, country_rating(continent, rank, world) & 65535)

    def test_absolute_margin_signed_bytes_and_both_signs(self):
        for a, b in ((0, 0), (4, 2), (2, 4), (0, 255), (128, 127)):
            r = Rig()
            r.lin8(FXSEG * 16 + FXOFF, a)
            r.lin8(FXSEG * 16 + FXOFF + 1, b)
            got = r.run("1771:5C60", [FXOFF, FXSEG])
            self.assertEqual(got, abs((a - 256 if a >= 128 else a) - (b - 256 if b >= 128 else b)))

    def test_result_delta_draw_win_loss_doubling_and_signed_rank(self):
        from model.confidence import result_delta
        for side in (0, 1):
            for winner in (0, 1, 2):
                for special in (False, True):
                    for own, other in ((19, 64), (64, 19)):
                        r = Rig()
                        r.fixture(2, 3, 4)
                        r.lin8(FXSEG * 16 + FXOFF, 4)
                        r.lin8(FXSEG * 16 + FXOFF + 1, 1)
                        r.lin8(FXSEG * 16 + FXOFF + 3, winner)
                        reply = answers({"1771:10E7": [own, other], "1771:5C60": 3,
                                         "1771:5A03": int(special)})
                        got = r.run("0791:B71C", [side, FXOFF, FXSEG], reply)
                        self.assertEqual(got, result_delta(own, other, [4, 1], winner, side, special) & 65535)

    def test_friendly_cross_continent_is_asymmetric(self):
        for kind in (0, 1, 2, 3, 0xC8):
            for same in (False, True):
                for country in (3, 4):
                    r = Rig()
                    r.fixture(kind, 3, 4)
                    r.country(3, 0x2C, 1)
                    r.country(4, 0x2C, 1 if same else 2)
                    got = r.run("1771:5A38", [FXOFF, FXSEG, country])
                    self.assertEqual(got & 255, int(kind == 1 and not same and country == 3))

    def test_gradual_route_short_circuit_and_kind(self):
        for friendly in (False, True):
            for special in (False, True):
                r = Rig()
                got = r.run("1771:5A8F", [FXOFF, FXSEG, 3],
                            answers({"1771:5A38": int(friendly), "1771:5A03": int(special)}))
                self.assertEqual(got & 255, int(friendly or special))
                self.assertEqual(len(r.args("1771:5A03")), int(not friendly))

    def test_roll_fitness_managed_order_age_threshold_and_clamps(self):
        cases = [(False, 27, 24, 10, [20], 30, 30), (True, 28, 24, 10, [11, 30], 29, 29),
                 (True, 29, 24, 7, [8, 21], 20, 20), (False, 20, 24, 100, [60], 1, 160),
                 (False, 20, 24, 100, [200], 32, 32)]
        for managed, age, peak, base, draws, fitness, energy in cases:
            r = Rig()
            r.player(1, 0, 3)
            r.player(1, 1, age)
            r.player(1, 2, peak)
            r.ds8(0xE82, base if age <= peak + 4 else 99)
            r.ds8(0xE83, base if age > peak + 4 else 99)
            r.run("1771:3558", [1], answers({"1771:0B77": int(managed), "214B:06B1": draws}))
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0xD:PSEG * 16 + POFF + 20 + 0xF], bytes([fitness, energy]))
            bounds = [a[0] for a in r.args("214B:06B1")]
            self.assertEqual(bounds, [base + 1, base * 3] if managed else [base * 2])

    def test_recovery_model_draw_order_injury_flag_rest_and_cap(self):
        from model.energy import recover
        cases = [(20, 0, 0, [1, 8], False, 26, 24), (20, 0, 1, [2, 1], True, 28, 24),
                 (20, 10, 1, [2, 8], False, 27, 24), (10, 10, 0, [3, 2], False, 28, 24),
                 (30, 10, 1, [1, 8], False, 28, 24), (30, 10, 1, [1, 8], False, 27, 24),
                 (0, 0, 0, [1, 8], False, 28, 24), (20, 128, 1, [1, 8], False, 28, 24)]
        for fit, energy, flag, draws, heals, age, peak in cases:
            r = Rig()
            rec = bytearray(20)
            rec[1], rec[2], rec[0xD], rec[0xE] = age, peak, fit, energy
            base = PSEG * 16 + POFF + 20
            r.mem.memory[base:base + 20] = rec
            r.ds8(0xE84, 32)
            r.ds8(0xE85, 24)
            r.run("1771:3651", [flag, 1], answers({"214B:06B1": draws, "214B:06D0": int(heals)}))
            transcript = draws + ([1 if heals else 2] if not 0 < energy < 128 else [])
            self.assertEqual(bytes(r.mem.memory[base:base + 20]), recover(rec, flag, transcript, [32, 24]))
            self.assertEqual([a[0] for a in r.args("214B:06B1")], [2, 8] if energy == 0 or flag else [3, 2])

    def test_recovery_lower_floor_bypasses_zero_upper_cap(self):
        r = Rig()
        r.player(1, 0xD, 0)
        r.player(1, 0xE, 0)
        r.ds8(0xE84, 0)
        r.ds8(0xE85, 0)
        r.run("1771:3651", [0, 1], answers({"214B:06B1": [1, 8], "214B:06D0": 0}))
        self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0xD], 1)

    def test_fixture_update_managed_short_circuit_and_bench_roles(self):
        for managed in ((0, 0), (1,), (0, 1)):
            for gradual in (False, True):
                for kind in (1, 2):
                    r = Rig()
                    r.fixture(kind, 3, 4)
                    # Big player words ensure a pushed squad word does not leak its AH into the recovery flag.
                    r.squad(3, [1025] + [0] * 10 + [1026, 1027])
                    r.squad(4, [0] * 20)
                    r.country(3, 0x2E, 130)
                    for word in (1025, 1026, 1027):
                        r.player(word, 6, 11)
                        r.player(word, 7, 4)
                    r.lin16(PSEG * 16 + POFF + 20 * 1025 + 8, 65535)
                    answer = answers({"1771:0B77": list(managed), "0791:B71C": [3, -2],
                                      "1771:5A8F": int(gradual), "214B:0C57": [1, 0],
                                      "214B:06B1": [2, 1, 4, 2]})
                    r.run("0791:B7FA", [FXOFF, FXSEG], answer)
                    any_managed = any(managed)
                    self.assertEqual(len(r.args("1771:0B77")), len(managed))
                    self.assertEqual(len(r.args("0791:B6CC")), 2 if not any_managed and kind != 1 else 0)
                    self.assertEqual(r.args("0791:B27F"), [(1025,), (1026,), (1027,)])
                    self.assertEqual(r.args("0791:B364"), [(1025, 3), (1026, 3), (1026, 65535), (1027, 65534)])
                    if gradual:
                        self.assertEqual(r.args("1771:3651"), [(1025, 1), (1026, 1), (1027, 0)])
                    else:
                        self.assertEqual(r.args("1771:3558"), [(1025,), (1026,), (1027,)])
                    self.assertEqual(r.u16(PSEG * 16 + POFF + 20 * 1025 + 8), 0)
                    self.assertEqual(r.u16(PSEG * 16 + POFF + 20 * 1026 + 8), 1)
                    self.assertEqual(r.u16(PSEG * 16 + POFF + 20 * 1027 + 8), 0)
                    for word in (1026, 1027):
                        self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 * word + 6], 11 if any_managed else 4)

    def test_pool_eighty_entries_status_kind_and_wrapped_bound(self):
        for gradual in (False, True):
            for kind in (0, 1, 2, 3, 0xC8):
                for first in (2, 65520):
                    r = Rig()
                    r.country(3, 0x2E, 130)
                    r.ds16(0x6D18 + 4, first)
                    r.ds16(0x7C2A, FXOFF)
                    r.ds16(0x7C2C, FXSEG)
                    r.fixture(kind, 3, 4)
                    r.ds16(0xA927, 0x20)
                    r.ds16(0xA929, 0x5200)
                    for k in range(2, 82):
                        r.lin16(0x52000 + 0x20 + 2 * k, 1000 + k)
                    r.run("0791:BA4E", [3], answers({"1771:5A8F": int(gradual), "214B:06B1": 2}))
                    count = 80 if first == 2 else 0
                    self.assertEqual(len(r.args("1771:3651")), count if gradual else 0)
                    self.assertEqual(len(r.args("1771:3558")), 0 if gradual else count)
                    self.assertEqual(len(r.args("0791:B364")), count)
                    self.assertEqual(len(r.args("0791:B27F")), count if kind != 0 else 0)
                    if count:
                        self.assertEqual(r.args("0791:B364"), [(1000 + k, 0) for k in range(2, 82)])

    def test_diagnostic_stores_change_the_records(self):
        for variant, expected in ((None, 16), ("confidence-plus-one", 17)):
            r = Rig()
            r.player(1, 0xC, 16)
            r.run("0791:B364", [0, 1], variant=variant)
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0xC], expected)
        for variant, expected in ((None, 20), ("rolled-energy-plus-one", 21)):
            r = Rig()
            r.ds8(0xE82, 10)
            r.run("1771:3558", [1], answers({"1771:0B77": 0, "214B:06B1": 10}), variant=variant)
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0xE], expected)
        for variant, expected in ((None, 20), ("recovered-energy-plus-one", 21)):
            r = Rig()
            r.player(1, 0xD, 20)
            r.player(1, 0xE, 20)
            r.ds8(0xE84, 32)
            r.run("1771:3651", [1, 1], answers({"214B:06B1": [1, 1]}), variant=variant)
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 + 0xE], expected)

if __name__ == "__main__":
    unittest.main()
