"""T71: synthetic branch tests of the post-match ports, with reached twins."""
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

    def run(self, address, words=(), answer=None):
        entry = port._module_registry("postmatch").entries[address]
        for i, value in enumerate([0x5678] + ([0x9ABC] if entry.far else []) + list(words)):
            self.mem.memory[0x3000 + i * 2:0x3002 + i * 2] = (value & 0xFFFF).to_bytes(2, "little")
        self.mem._entries.append((0x3000, entry.far))
        try:
            value = entry.fn(self.mem, None)
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


class Postmatch(Case):
    def test_registry_contract(self):
        reg = port._module_registry("postmatch")
        self.assertEqual(set(reg.entries), {"0791:F1F6", "0791:CAB0", "0791:CB7D", "0791:BC5D", "0791:D050",
                                          "0791:D016", "0791:D032", "0791:E929", "1771:8757", "1771:82BD",
                                          "1771:85F7", "1771:59D8"})

    def test_man_of_match_decode_and_strict_ties(self):
        for perf, want in ((10060, 2), (60, 2), (55, 1), (0x7FFF, 1), (10040, 1)):
            r = Rig()
            r.ds16(0x9B34, 1)
            r.ds16(0x9B36, 2)
            r.squad(1, [1, 2])
            r.lin16(PSEG * 16 + POFF + 20 + 0x12, 55)
            r.lin16(PSEG * 16 + POFF + 40 + 0x12, perf)
            r.run("0791:CAB0")
            self.assertEqual(r.mem.ds16(0x7C3A), want, perf)

    def test_man_bench_only_substituted_off(self):
        for off, want in ((False, 1), (True, 2)):
            r = Rig()
            r.ds16(0x9B34, 1)
            r.ds16(0x9B36, 2)
            r.squad(1, [1] + [0] * 10 + [2])
            r.lin16(PSEG * 16 + POFF + 20 + 0x12, 55)
            r.lin16(PSEG * 16 + POFF + 40 + 0x12, 60)
            r.run("0791:CAB0", answer=answers({"214B:0C57": int(off)}))
            self.assertEqual(r.mem.ds16(0x7C3A), want)

    def test_restore_zero_and_signed_energy(self):
        for energy in (0, 1, 100, 128, 255):
            r = Rig()
            r.ds16(0x9B34, 1)
            r.ds16(0x9B36, 2)
            r.squad(1, [1, 0, 2])
            r.ds8(0x9B08, 43)
            r.ds8(0x9B0A, 62)
            for word in (1, 2):
                r.player(word, 0xC, 99)
                r.player(word, 0xD, 80)
                r.player(word, 0xE, energy)
            r.run("0791:CB7D")
            for word, morale in ((1, 43), (2, 62)):
                base = PSEG * 16 + POFF + 20 * word
                self.assertEqual(r.mem.memory[base + 0xC], morale)
                self.assertEqual(r.mem.memory[base + 0xE], 80 if 0 < energy < 128 else energy)
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 0xC], 0)

    def test_reset_tactics_all_twenty_including_zero_then_eleven_positions(self):
        r = Rig()
        r.squad(3, list(range(1, 20)) + [0])
        r.ds8(0x9B7C + 3, 17)
        for word in range(20):
            r.player(word, 0xF, 255)
        for k in range(1, 12):
            r.ds8(0x9F02 + 20 * 3 + k, k + 1)
        r.run("0791:BC5D", [3])
        self.assertEqual(r.args("0791:BBFF"), [(3, 17)])
        self.assertEqual(r.args("1771:52CC"), [(3,)])
        for word in range(20):
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 * word + 0xF], 0)
        for k in range(1, 12):
            self.assertEqual(r.mem.memory[PSEG * 16 + POFF + 20 * k + 6], k + 1)

    def test_streak_place_and_total(self):
        for address, before, after in (("0791:D016", 255, 0), ("0791:D016", 8, 9), ("0791:D032", 8, 0)):
            for place in (0, 1):
                r = Rig()
                base = FXSEG * 16 + FXOFF
                for k in (3, 4, 5):
                    r.lin8(base + k, before)
                r.run(address, [0x2222, place, FXOFF, FXSEG])
                self.assertEqual(r.mem.memory[base + 3 + place], after)
                self.assertEqual(r.mem.memory[base + 5], after)
                self.assertEqual(r.mem.memory[base + 4 - place], before)

    def test_table_display_keeps_mode_and_kind(self):
        r = Rig()
        r.ds8(0x9976, 12)
        r.run("0791:E929", [1, 19])
        self.assertEqual(r.targets(), [("1771:8757", "0791:E931"), ("1771:958D", "0791:E943")])
        self.assertEqual(r.args("1771:958D"), [(1, 12, 19)])

    def test_group_stage_dispatch_dimensions_and_empty_tables(self):
        for stage, continents, groups, finals in ((2, 4, 8, 0), (3, 4, 2, 0), (5, 4, 8, 1), (7, 1, 8, 1),
                                                  (2, 0, 8, 0), (2, 4, 0, 0), (1, 4, 8, 0), (6, 4, 8, 0)):
            r = Rig()
            r.lin8(GSEG * 16 + GOFF + 0x3C, stage)
            r.lin8(GSEG * 16 + GOFF + 0x40, 1)
            r.ds8(0x1110 + int(stage == 7), continents)
            r.ds8(0x1112 + int(stage == 3), groups)
            r.ds16(0xA933, 0x100)
            r.ds16(0xA935, 0x5000)
            def reply(c, mem):
                if c.target == "23E4:08DF":
                    mem.regs['eflags'] = 0 if stage in (2, 3, 5, 7) else 0x40
                return finals if c.target == "1771:59D8" else 0
            r.run("1771:8757", answer=reply)
            calls = r.args("1771:82BD")
            self.assertEqual(len(calls), continents * groups if stage in (2, 3, 5, 7) else 0)
            if calls:
                self.assertEqual(calls[0], (0x5000, 0x100 + 0xE00 + finals * 0x700))
            self.assertEqual(len(r.args("1771:85F7")), int(stage == 6))

    def test_finals_set_true_and_false(self):
        for belongs in (False, True):
            for high in (0, 0xAB):
                r = Rig()
                r.lin8(GSEG * 16 + GOFF + 0x3C, 5)
                def reply(c, mem):
                    mem.regs['eflags'] = 0 if belongs else 0x40
                    return (high << 8) | 0xCD
                result = r.run("1771:59D8", answer=reply)
                self.assertIsInstance(result, int)
                self.assertEqual(result, (high << 8) | int(belongs))
                self.assertEqual(r.mem.memory[BP0 - 1], int(belongs))

    def test_country_totals_streaks_and_best_results(self):
        for outcome in (0, 1, 2):
            for host in (False, True):
                for neutral in (False, True):
                    r = Rig()
                    r.fixture(2, 3, 4)
                    base = FXSEG * 16 + FXOFF
                    r.lin8(base, 4)
                    r.lin8(base + 1, 2)
                    r.lin8(base + 3, outcome)
                    for team in (3, 4):
                        for field in (0xA7, 0xAD, 0xB3, 0xB9):
                            for k in range(3):
                                r.country(team, field + k, 2)
                                r.country(team, field + k + 3, 7)
                    reply = answers({"0791:D44C": int(host), "1771:5A03": int(neutral), "0791:A6E4": 3,
                                     "1771:5C60": [1, 2, 3, 2]})
                    r.run("0791:D050", [FXOFF, FXSEG], reply)
                    for side, team in enumerate((3, 4)):
                        cb = SQSEG * 16 + SQOFF + 0xBF * team
                        self.assertEqual(r.mem.memory[cb + 0x3C:cb + 0x41],
                                         bytes([int(outcome == side), int(outcome == 2),
                                                int(outcome not in (side, 2)), 4 if side == 0 else 2,
                                                2 if side == 0 else 4]))
                        for field in (0xA7, 0xAD, 0xB3, 0xB9):
                            self.assertEqual(list(r.mem.memory[cb + field:cb + field + 3]), [7, 7, 7])
                    inc = r.args("0791:D016")
                    clear = r.args("0791:D032")
                    self.assertEqual(len(inc), 4)
                    self.assertEqual(len(clear), 4 if outcome != 2 else 8)
                    for target_args in inc + clear:
                        self.assertEqual(target_args[2], int(host and target_args[1] >= SQOFF + 4 * 0xBF))
                        self.assertEqual(target_args[3], BP0)
                    self.assertEqual(len(r.args("1771:5C60")), 0 if outcome == 2 else 4)
                    self.assertEqual(len(r.args("23E4:025D")), 0 if outcome == 2 else 1)

    def test_country_streak_maxima_keep_equal_or_larger(self):
        r = Rig()
        r.fixture(2, 3, 4)
        r.lin8(FXSEG * 16 + FXOFF + 3, 2)
        for team in (3, 4):
            for field in (0xA7, 0xAD, 0xB3, 0xB9):
                for k, (a, b) in enumerate(((9, 7), (7, 7), (6, 7))):
                    r.country(team, field + k, a)
                    r.country(team, field + k + 3, b)
        r.run("0791:D050", [FXOFF, FXSEG])
        for team in (3, 4):
            for field in (0xA7, 0xAD, 0xB3, 0xB9):
                cb = SQSEG * 16 + SQOFF + 0xBF * team
                self.assertEqual(list(r.mem.memory[cb + field:cb + field + 3]), [9, 7, 7])

    def test_sort_group_table_all_fixture_filters_and_outcomes(self):
        # Three played fixtures and the three rejection paths, from the list's slots 25..36.
        r = Rig()
        tseg, toff, lseg, loff, fseg, foff = 0x5000, 0x20, 0x5200, 0x10, 0x5400, 0x20
        for ptr, off, seg in ((0xA92F, loff, lseg), (0xA92B, foff, fseg)):
            r.ds16(ptr, off)
            r.ds16(ptr + 2, seg)
        r.lin8(GSEG * 16 + GOFF + 0x3C, 2)
        for slot, country in enumerate((1, 2, 3, 4)):
            r.lin16(tseg * 16 + toff + 8 * slot, country)
        for number, (a, b, kind) in enumerate(((3, 1, 2), (1, 1, 2), (0, 1, 2), (4, 0, 1), (0xFE, 0, 2)), 1):
            fx = fseg * 16 + foff + (number - 1) * 8
            for k, v in enumerate((a, b, kind, 0)):
                r.lin8(fx + k, v)
            r.lin16(fx + 4, 1)
            r.lin16(fx + 6, 2)
            r.lin16(lseg * 16 + loff + 0x48 + 2 * (number + 23), number)
        def reply(c, mem):
            if c.target == "214B:0018":
                seg, off, count, v = c.args
                mem.memory[seg * 16 + off:seg * 16 + off + count] = bytes([v]) * count
            return 0
        r.run("1771:82BD", [toff, tseg], reply)
        self.assertEqual(list(r.mem.memory[tseg * 16 + toff + 2:tseg * 16 + toff + 8]), [1, 1, 1, 4, 3, 3])
        self.assertEqual(len(r.args("214B:0018")), 4)

    def test_sort_group_table_tie_break_order(self):
        for rows, expected_swaps in (([(5, 1, 6), (4, 1, 7), (0, 0, 0), (0, 0, 0)], 1),
                                     ([(2, 1, 6), (4, 1, 6), (0, 0, 0), (0, 0, 0)], 1),
                                     ([(2, 1, 6), (4, 3, 6), (0, 0, 0), (0, 0, 0)], 1),
                                     ([(2, 1, 6), (2, 1, 6), (0, 0, 0), (0, 0, 0)], 0),
                                     ([(5, 1, 6), (4, 1, 6), (0, 0, 0), (0, 0, 0)], 0),
                                     ([(4, 3, 6), (2, 1, 6), (0, 0, 0), (0, 0, 0)], 0)):
            r = Rig()
            tseg, toff = 0x5000, 0x20
            for slot, (gf, ga, pts) in enumerate(rows):
                r.lin16(tseg * 16 + toff + 8 * slot, slot + 1)
                for field, v in ((5, gf), (6, ga), (7, pts)):
                    r.lin8(tseg * 16 + toff + 8 * slot + field, v)
            # Fixtures lists are zero; fake fill preserves the synthetic scores for the exchange sort.
            r.ds16(0xA92F, 0x10)
            r.ds16(0xA931, 0x5200)
            r.run("1771:82BD", [toff, tseg])
            self.assertEqual(len(r.args("214B:007B")), expected_swaps, rows)
            self.assertEqual(r.u16(BP0 - 4), 3)
            self.assertEqual(r.u16(BP0 - 2), 4)

    def test_aggregate_unplayed_and_index_exit(self):
        for index, played in ((0, True), (1, False), (1, True)):
            r = Rig()
            r.ds16(0xA92B, 0x20)
            r.ds16(0xA92D, 0x5400)
            r.lin16(GSEG * 16 + GOFF + 0x26, index)
            r.lin16(GSEG * 16 + GOFF + 0x2C, 0)
            r.lin8(0x54000 + 0x20, 2 if played else 0xFE)
            r.run("1771:85F7")
            self.assertEqual(len(r.written("1771:8728")), int(index == 1 and played))

    def test_aggregate_winners_totals_and_tie(self):
        for a, b, c, d, winner in ((4, 0, 1, 0, 0), (0, 4, 1, 0, 1), (1, 1, 2, 2, 1),
                                           (2, 2, 1, 1, 0), (1, 1, 1, 1, 1)):
            r = Rig()
            r.ds16(0xA92B, 0x20)
            r.ds16(0xA92D, 0x5400)
            r.lin16(GSEG * 16 + GOFF + 0x26, 2)
            r.lin16(GSEG * 16 + GOFF + 0x2C, 1)
            for k, v in ((0, a), (1, b), (8, c), (9, d)):
                r.lin8(0x54000 + 0x20 + k, v)
            r.run("1771:85F7")
            base = 0x54000 + 0x20 + 0x960 * 8
            self.assertEqual(list(r.mem.memory[base:base + 2]), [a + d, b + c])
            self.assertEqual(r.mem.memory[base + 3], winner)

    def test_run_match_tail_quick_save_and_manager_branches(self):
        for quick in (False, True):
            for save in (False, True):
                for kind in (1, 2):
                    for managed in (0, 1):
                        r = Rig()
                        r.fixture(kind, 1, 2)
                        r.ds16(0x9B34, 1)
                        r.ds16(0x9B36, 2)
                        r.ds8(0x9A3E, int(quick))
                        r.squad(1, [1] + [0] * 19)
                        r.player(1, 0xC, 44)
                        r.lin16(PSEG * 16 + POFF + 20 + 0x12, 0x7777)
                        trace = []
                        r.mem.sites[r.mem.lin("0791:F2E3")] = [lambda: trace.append("MATCH_PLAYED")]
                        def reply(c, mem):
                            trace.append(c.target)
                            if c.target == "23E4:08DF":
                                mem.regs['eflags'] = 0 if quick else 0x40
                            return int(save) if c.target == "0791:0B7C" else (managed if c.target == "1771:0B77" else 0)
                        r.run("0791:F1F6", [FXOFF, FXSEG], reply)
                        self.assertIn("MATCH_PLAYED", trace)
                        self.assertEqual(trace.index("MATCH_PLAYED"), trace.index("0791:F098") + 1)
                        self.assertEqual(trace[trace.index("MATCH_PLAYED") + 1], "23E4:025D")
                        self.assertEqual(len(r.args("0791:15B9")), int(not quick))
                        self.assertEqual(len(r.args("0791:0B7C")), int(not quick))
                        self.assertEqual(len(r.args("0791:0A6B")), int(save and not quick))
                        self.assertEqual(len(r.args("0791:ED8A")), 2 if quick else 1)
                        self.assertEqual(len(r.args("0791:E929")), int(kind != 1))
                        self.assertEqual(r.args("0791:BC5D"), [(1,), (2,)] if not managed else [])
                        self.assertEqual(r.args("0791:BA4E"), [(1,), (2,)] if managed else [])
                        self.assertEqual(r.mem.ds8(0x9B08), 44)
                        self.assertEqual(r.u16(PSEG * 16 + POFF + 20 + 0x12), 0x37)
                        self.assertEqual(r.mem.ds8(0x66D), 0)
                        self.assertEqual(r.mem.ds8(0xC20), 0)
                        self.assertEqual(r.mem.memory[GSEG * 16 + GOFF + 1], 1)
                        self.assertEqual(r.args("0791:F098"), [(BP0,)])
                        self.assertEqual(len(r.args("23E4:025D")), 3)

if __name__ == "__main__":
    unittest.main()
