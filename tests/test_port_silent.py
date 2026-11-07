"""T120: the silent path's ports (runtime/original_match/port/silent.py) on synthetic memory, branch by branch.

The proof against the original is experiments/E040-route-fixture-writes/prove.py (the route harness, E040's states);
these tests visit the listing's branches on PlainMem with the guest calls answered by the test, so each routine's
calls (target, arguments, return address, near or far), its writes and its loops' bounds are pinned:
- D47E: the score from DS:9B3C after B19D(0xC); +3 := 2 level, 1 the second ahead, 0 the first ahead; B15F's 1 adds
  B19D(4) and, still level, the coin 06FA into +3; +0x12 := 0x7FFF for the first 11 of both squads, not the 12th;
- B602: one 06B1(0x1E) per goal of each side, the squad slot DS:0A09[draw], +0xA incremented, B3B7 only when 5A03 is
  nonzero, B364(player, 1); no draw for a side with no goal;
- BB2F: A4A1, then per side 20 x (3558, 06B1(4), 06B1(2), B364(word, the second draw - the first)), then BA4E for a managed side
  (near) or BC5D (push cs: far, returning to BBE4); the first byte and DS:0C1E := 0;
- 6970: the four calls on the fixture at the cursor and BC5D for both countries; a 0xFE fixture's score page (one key
  read, E929(second country, 0)), the parent's [bp - 2] := 0 after the cursor's increment; any other fixture's results
  list, from max(cursor - 15, the parent's [bp - 6]) to the cursor (0D56's longint arguments), rows from 8, the key
  0xAE (up to 5), 0xAF (down to 0), space (04F8 with CS:696A), the +0x3E polls with a 50 ms wait each when no key
  waits, then the parent's [bp - 2] := 1 before the cursor's increment;
- the variants change what their names say (the falsifiers prove.py --variant runs)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from original_match import port  # noqa: E402
from test_port_update import Rig as UpdateRig, Case, answers, PSEG, POFF, SQSEG, SQOFF, GSEG, GOFF, FXSEG, FXOFF  # noqa: E402

FX = FXSEG * 16 + FXOFF
GAME = GSEG * 16 + GOFF
FIXTURES_SEG, FIXTURES_OFF = 0x5000, 0x0008      # the fixture list (DS:A92B): fixture i at +8 (i - 1)
PARENT_BP = 0x3100                               # route_fixture's BP, the word 6970 is given


class Rig(UpdateRig):
    def __init__(self):
        super().__init__()
        self.ds16(0xA92B, FIXTURES_OFF)
        self.ds16(0xA92D, FIXTURES_SEG)

    def run(self, address, words=(), answer=None, variant=None):
        """test_port_update.Rig.run, for this module's ports."""
        entry = port._module_registry("silent").entries[address]
        for i, value in enumerate([0x5678] + ([0x9ABC] if entry.far else []) + list(words)):
            self.mem.memory[0x3000 + i * 2:0x3002 + i * 2] = (value & 0xFFFF).to_bytes(2, "little")
        self.mem._entries.append((0x3000, entry.far))
        try:
            value = entry.fn(self.mem, variant)
            gen, sent = value, None
            while True:
                try:
                    request = gen.send(sent)
                except StopIteration as stop:
                    value = stop.value
                    break
                self.calls.append((request.target, request.args, request.ret_to, request.far))
                if len(self.calls) > 5000:
                    raise AssertionError(f"more than 5000 calls, the last {request.target}")
                sent = answer(request, self.mem) if answer else 0
                self.mem.regs["ax"] = sent & 0xFFFF
        finally:
            self.mem._entries.pop()
        return value

    def fixture_bytes(self, first_byte, goals, kind, a, b):
        self.mem.memory[FX:FX + 8] = bytes([goals[0], goals[1], kind, first_byte]) + a.to_bytes(2, "little") + \
            b.to_bytes(2, "little")

    def squad_range(self, country, first_word):
        self.squad(country, list(range(first_word, first_word + 20)))

    def player_word(self, word, k):
        return self.u16(PSEG * 16 + POFF + 0x14 * word + k)

    def calls_of(self, target):
        return [c for c in self.calls if c[0] == target]


def score(first, second):
    """An answer for B19D: DS:9B3C, 9B3D := the two goals."""
    def put(request, mem):
        mem.memory[mem.DS * 16 + 0x9B3C] = first
        mem.memory[mem.DS * 16 + 0x9B3D] = second
        return 0
    return put


def responder(table):
    """{target: value, [values] or fn(request, mem)}; an unlisted target answers 0."""
    queues = {k: (list(v) if isinstance(v, list) else v) for k, v in table.items()}

    def answer(request, mem):
        v = queues.get(request.target, 0)
        if isinstance(v, list):
            v = v.pop(0)
        return v(request, mem) if callable(v) else v
    return answer


class Registry(Case):
    def test_the_four_routines_and_their_returns(self):
        reg = port._module_registry("silent")
        self.assertEqual({a: e.ret for a, e in reg.entries.items()},
                         {"000E:6970": "ret 2", "0791:D47E": "retf 4", "0791:B602": "retf 4", "0791:BB2F": "retf 4", "0791:B15F": "ret 4"})
        self.assertEqual(set(reg.variants), {"goal-plus-one", "credit-twice", "scorer-draw-29"})
        self.assertIn("silent", port.available())


class QuickResultSilent(Case):
    def _run(self, scores, needs_winner=0, coin=0, variant=None):
        r = Rig()
        r.fixture_bytes(0xFF, (9, 9), 2, 3, 4)
        r.squad_range(3, 100)
        r.squad_range(4, 200)
        r.ds8(0x80FC, 0x5A)
        r.run("0791:D47E", [FXOFF, FXSEG],
              responder({"0791:B19D": [score(*s) for s in scores], "0791:B15F": needs_winner, "214B:06FA": coin}),
              variant)
        return r

    def test_calls_in_order_with_their_arguments(self):
        r = self._run([(2, 1)])
        self.assertEqual(r.targets(), [("0791:A3DE", "0791:D495"), ("1771:0BC4", "0791:D4A8"),
                                       ("1771:0BC4", "0791:D4BA"), ("0791:B19D", "0791:D4C1"),
                                       ("0791:B15F", "0791:D507")])
        a3de, second, first, b19d, b15f = r.calls
        self.assertEqual((a3de[1], a3de[3]), ((FXSEG, FXOFF), False))
        self.assertEqual([a & 0xFF for a in second[1]], [4, 1, 0x5A])     # the second country, 1, DS:80FC
        self.assertEqual([a & 0xFF for a in first[1]], [3, 0, 0])
        self.assertEqual((b19d[1], b19d[3]), ((0xC,), False))

    def test_the_result_byte(self):
        for goals, plus3 in (((2, 1), 0), ((1, 2), 1), ((1, 1), 2), ((0, 0), 2), ((0, 5), 1)):
            r = self._run([goals])
            self.assertEqual(bytes(r.mem.memory[FX:FX + 4]), bytes([goals[0], goals[1], 2, plus3]), goals)

    def test_a_winner_needed_rolls_again_and_tosses_when_level(self):
        r = self._run([(1, 1), (2, 2)], needs_winner=1, coin=1)
        self.assertEqual([c[1] for c in r.calls_of("0791:B19D")], [(0xC,), (4,)])
        self.assertEqual([c[2] for c in r.calls_of("214B:06FA")], ["0791:D52F"])
        self.assertEqual(r.mem.memory[FX:FX + 4], bytearray([2, 2, 2, 1]))
        r = self._run([(1, 1), (3, 2)], needs_winner=1, coin=1)
        self.assertEqual(r.calls_of("214B:06FA"), [])
        self.assertEqual(r.mem.memory[FX:FX + 4], bytearray([3, 2, 2, 0]))

    def test_no_winner_needed_no_second_roll(self):
        r = self._run([(1, 1)], needs_winner=0)
        self.assertEqual(len(r.calls_of("0791:B19D")), 1)
        self.assertEqual(r.calls_of("214B:06FA"), [])

    def test_the_first_eleven_of_both_squads(self):
        r = self._run([(0, 0)])
        for base in (100, 200):
            self.assertEqual([r.player_word(w, 0x12) for w in range(base, base + 11)], [0x7FFF] * 11)
            self.assertEqual(r.player_word(base + 11, 0x12), 0)
        self.assertEqual(len(r.written("0791:D5A9")), 22)

    def test_goal_plus_one(self):
        r = self._run([(2, 1)], variant="goal-plus-one")
        self.assertEqual(r.mem.memory[FX:FX + 2], bytearray([3, 1]))


class CreditSilentMatchScorers(Case):
    def _run(self, goals, tables, draws, variant=None):
        r = Rig()
        r.fixture_bytes(0xFF, goals, 2, 3, 4)
        r.squad_range(3, 100)
        r.squad_range(4, 200)
        r.country(3, 0x2C, 1)
        r.country(4, 0x2C, 5)
        for draw in range(1, 31):
            r.ds8(0xA09 + draw, (draw % 20) + 1)          # the slot table DS:0A0A..: draw -> squad slot 1..20
        r.run("0791:B602", [FXOFF, FXSEG], answers({"1771:5A03": tables, "214B:06B1": list(draws)}), variant)
        return r

    def test_one_draw_per_goal_and_the_credits(self):
        r = self._run((2, 1), 1, [4, 19, 7])
        self.assertEqual([c[1] for c in r.calls_of("214B:06B1")], [(0x1E,)] * 3)
        slot = lambda d: (d % 20) + 1
        credited = [100 + slot(4) - 1, 100 + slot(19) - 1, 200 + slot(7) - 1]
        for w in credited:
            self.assertEqual(r.player_word(w, 0xA), 1, w)
        self.assertEqual([c[1] for c in r.calls_of("0791:B3B7")],
                         [(credited[0], 1), (credited[1], 1), (credited[2], 5)])
        self.assertEqual([c[1] for c in r.calls_of("0791:B364")], [(w, 1) for w in credited])
        self.assertEqual({c[3] for c in r.calls if c[0] in ("0791:B3B7", "0791:B364")}, {False})

    def test_no_tables_no_b3b7_and_no_goal_no_draw(self):
        r = self._run((0, 2), 0, [1, 1])
        self.assertEqual(r.calls_of("0791:B3B7"), [])
        self.assertEqual(len(r.calls_of("214B:06B1")), 2)
        self.assertEqual(r.player_word(200 + 2 - 1, 0xA), 2)       # the same scorer twice
        r = self._run((0, 0), 1, [])
        self.assertEqual([c[0] for c in r.calls], ["1771:5A03"])

    def test_variants(self):
        r = self._run((1, 0), 0, [4], variant="credit-twice")
        self.assertEqual(r.player_word(100 + 5 - 1, 0xA), 2)
        r = self._run((1, 0), 0, [4], variant="scorer-draw-29")
        self.assertEqual(r.calls_of("214B:06B1")[0][1], (0x1D,))


class PrepareUnplayedMatch(Case):
    def _run(self, managed):
        r = Rig()
        r.fixture_bytes(0xFE, (0, 0), 0, 3, 4)
        r.ds16(0x9B34, 3)
        r.ds16(0x9B36, 4)
        r.squad_range(3, 100)
        r.squad_range(4, 200)
        r.ds8(0x0C1E, 7)
        r.run("0791:BB2F", [FXOFF, FXSEG], answers({"1771:0B77": list(managed), "214B:06B1": [3, 1] * 40}))
        return r

    def test_the_calls_and_the_writes(self):
        r = self._run([1, 0])
        t = [c[0] for c in r.calls]
        self.assertEqual(t[0], "0791:A4A1")
        side = ["1771:3558", "214B:06B1", "214B:06B1", "0791:B364"] * 20
        self.assertEqual(t[1:81], side)
        self.assertEqual(t[81:83], ["1771:0B77", "0791:BA4E"])
        self.assertEqual(t[83:163], side)
        self.assertEqual(t[163:], ["1771:0B77", "0791:BC5D"])
        self.assertEqual([c[1] for c in r.calls_of("214B:06B1")[:2]], [(4,), (2,)])
        minus2 = (1 - 3) & 0xFFFF                                    # 06B1(2) = 1 minus 06B1(4) = 3 (BBA1-BBA2)
        self.assertEqual([c[1] for c in r.calls_of("0791:B364")][:2], [(100, minus2), (101, minus2)])
        self.assertEqual([c[1] for c in r.calls_of("0791:B364")][20], (200, minus2))
        self.assertEqual([c[1] for c in r.calls_of("1771:3558")][19:21], [(119,), (200,)])
        bc5d = r.calls_of("0791:BC5D")[0]
        self.assertEqual((bc5d[1], bc5d[2], bc5d[3]), ((4,), "0791:BBE4", True))
        ba4e = r.calls_of("0791:BA4E")[0]
        self.assertEqual((ba4e[1], ba4e[2], ba4e[3]), ((3,), "0791:BBD2", False))
        self.assertEqual(r.mem.memory[FX + 3], 0xFE)                 # +3 kept: BBF0 writes byte 0
        self.assertEqual(r.mem.memory[FX], 0)
        self.assertEqual(r.mem.memory[r.mem.DS * 16 + 0x0C1E], 0)

    def test_unmanaged_both_reset(self):
        r = self._run([0, 0])
        self.assertEqual([c[1] for c in r.calls_of("0791:BC5D")], [(3,), (4,)])
        self.assertEqual(r.calls_of("0791:BA4E"), [])


class SimulateFixture(Case):
    CURSOR = 20

    def _rig(self, first_byte, start, speed):
        r = Rig()
        r.ds16(0xA923, GOFF)
        r.ds16(0xA925, GSEG)
        r.lin16(GAME + 0x26, self.CURSOR)
        r.lin8(GAME + 0x3E, speed)
        base = FIXTURES_SEG * 16 + FIXTURES_OFF + 8 * (self.CURSOR - 1)
        r.mem.memory[base:base + 8] = bytes([first_byte, 0, 1, 0]) + (3).to_bytes(2, "little") + \
            (4).to_bytes(2, "little")
        r.lin16(PARENT_BP - 6, start)                 # route_fixture's [bp - 6]: the cursor its call started at
        r.lin8(PARENT_BP - 2, 0x55)
        r.ds8(0xA976, 0)
        return r, base

    def _run(self, first_byte, start=1, speed=2, key=None, polls=None):
        r, base = self._rig(first_byte, start, speed)
        table = {"214B:0D56": max(self.CURSOR - 15, start), "214B:0723": polls if polls is not None else [int(key is not None)] + [0] * 8}

        def read_key(request, mem):
            mem.memory[mem.DS * 16 + 0xA976] = key
            return key
        table["214B:08DD"] = read_key
        r.run("000E:6970", [PARENT_BP], responder(table))
        return r, base

    def test_the_four_calls_and_the_tactics(self):
        r, base = self._run(0xFF)
        seg, off = FIXTURES_SEG, FIXTURES_OFF + 8 * (self.CURSOR - 1)
        self.assertEqual(r.calls[:6], [("0791:D47E", (seg, off), "000E:69CA", True),
                                       ("0791:B7FA", (seg, off), "000E:69E6", True),
                                       ("0791:B602", (seg, off), "000E:6A02", True),
                                       ("0791:D050", (seg, off), "000E:6A1E", True),
                                       ("0791:BC5D", (3,), "000E:6A3B", True),
                                       ("0791:BC5D", (4,), "000E:6A3B", True)])

    def test_a_0xFE_fixture_shows_its_score_page(self):
        r, base = self._run(0xFE, key=0x0D)
        ds = r.mem.DS
        self.assertEqual([(c[0], c[1], c[2]) for c in r.calls[6:]], [
            ("0791:0712", (ds, 0xA96E), "000E:6A51"),
            ("214B:0329", (ds, 0x25CC, ds, 0xA96E), "000E:6A60"),
            ("214B:0329", (ds, 0x14A6, ds, 0xA96E), "000E:6A6F"),
            ("23E4:025D", (0, 0, 0, 0, 0xFA0), "000E:6A84"),
            ("214B:08DD", (), "000E:6A89"),
            ("0791:E929", (4, 0), "000E:6A98")])
        self.assertEqual(r.u16(GAME + 0x26), self.CURSOR + 1)
        self.assertEqual(r.mem.memory[PARENT_BP - 2], 0)
        self.assertEqual([w[0] for w in r.writes if w[0] in (GAME + 0x26, PARENT_BP - 2)],
                         [GAME + 0x26, PARENT_BP - 2])                 # 6A9B, then 6AA2

    def test_the_results_list_from_the_later_of_its_start_and_cursor_minus_15(self):
        for start, first in ((1, self.CURSOR - 15), (10, 10)):
            r, base = self._run(0xFF, start=start, speed=0)
            d56 = r.calls_of("214B:0D56")[0]
            self.assertEqual(d56[1], (0, start, 0, self.CURSOR - 15))      # longint(start), longint(cursor - 15)
            rows = r.calls_of("1771:7812")
            self.assertEqual([c[1][2] for c in rows], list(range(8, 8 + self.CURSOR - first + 1)))
            self.assertEqual([c[1][1] for c in rows],
                             [FIXTURES_OFF + 8 * (i - 1) for i in range(first, self.CURSOR + 1)])
            self.assertEqual({c[1][3] & 0xFF for c in rows}, {0x21})
            self.assertEqual(r.mem.memory[PARENT_BP - 2], 1)
            self.assertEqual(r.u16(GAME + 0x26), self.CURSOR + 1)
            self.assertEqual([w[0] for w in r.writes if w[0] in (GAME + 0x26, PARENT_BP - 2)],
                             [PARENT_BP - 2, GAME + 0x26])             # 6C0F, then 6C17

    def test_cursor_below_15_the_high_word_borrows(self):
        self.CURSOR = 3
        r, base = self._run(0xFF, start=1, speed=0)
        self.assertEqual(r.calls_of("214B:0D56")[0][1], (0, 1, 0xFFFF, (3 - 15) & 0xFFFF))

    def test_the_speed_shown_and_the_keys(self):
        for speed, key, after in ((2, 0xAE, 3), (5, 0xAE, 5), (2, 0xAF, 1), (0, 0xAF, 0), (2, 0x20, 2),
                                  (2, 0x41, 2), (2, None, 2)):
            r, base = self._run(0xFF, speed=speed, key=key, polls=[int(key is not None)] + [1] * 6)
            self.assertEqual(r.mem.memory[r.mem.DS * 16 + 0xAA], (5 - speed) & 0xFF)
            text = r.calls_of("214B:02C8")[0]
            self.assertEqual([a & 0xFF for a in text[1]], [0xE, r.mem.DS & 0xFF, 0xAA, 0x19, 0x34,
                                                           r.mem.DS & 0xFF, 0x6E])
            self.assertEqual(r.mem.memory[GAME + 0x3E], after, (speed, key))
            self.assertEqual(len(r.calls_of("214B:08DD")), int(key is not None))
            pause = r.calls_of("214B:04F8")
            self.assertEqual(pause, [("214B:04F8", (r.mem.seg(0x000E), 0x696A), "000E:6BD5", True)]
                             if key == 0x20 else [])

    def test_the_waits(self):
        for speed, loop, waits in ((0, [], 0), (3, [0, 0, 0], 3), (3, [1, 0, 1], 1), (5, [1] * 5, 0)):
            r, base = self._run(0xFF, speed=speed, polls=[0] + loop)     # no key at 6B84, then the loop's polls
            self.assertEqual([c[2] for c in r.calls_of("214B:0723")],
                             ["000E:6B89"] + ["000E:6BF7"] * speed)
            self.assertEqual([c[1] for c in r.calls_of("214B:1E09")], [(0x32,)] * waits)


if __name__ == "__main__":
    unittest.main()
