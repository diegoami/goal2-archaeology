"""T68: the branches of the discipline port that no match of ALL reaches (out/T68/coverage-summary.tsv: 7D7A, AA07, AA71,
AA88, AAA3, AAA7, AAA9, AAAD, AB6E, C1DA, C215, C76E and C7BF are executed 0 times in the 62 matches; BDE9 cannot be
reached, notes/T68.md), run on synthetic memory with the listing's values, each with a reached twin; the branches the
task names, which ALL turned out to reach in a few matches (the substitution budget at 0: C8A0 in 2 matches, 8118 in 37;
a second yellow card: 7F39 in 2; the computer's tactic shift in each direction: C1F1 in 7, C1FE in 14, BFA5 in 14, BFBF
in 7); and the kit's two event writes of the row, the injury (7DD9) and the substitution (C7DC), which the kit reads as
events only from those writers (match.py WRITERS). No byte of the original."""
import signal
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port
from original_match.port.mem import PlainMem

PSEG, POFF = 0x4800, 0x0010          # the players' table (DS:A91B)
SQSEG, SQOFF = 0x4A00, 0x0020        # the squads (DS:A917)
FSEG, FOFF = 0x4C00, 0x0040          # the fixture (DS:A923): +0x3F the speed setting
BP0 = 0x3000 - 2                     # the BP a routine's `push bp; mov bp, sp` gives (SP 0x3000 at the entry)


class Rig:
    def __init__(self):
        self.mem = PlainMem(bytearray(0x60000))
        self.mem.regs.update(ss=0, sp=0x3000, bp=0x1234, ds=self.mem.DS, eflags=0x202)
        self.calls = []
        self.writes = []             # (DS offset, size, value, writer 'SSSS:OOOO')
        self.ds16(0xA91B, POFF)
        self.ds16(0xA91D, PSEG)
        self.ds16(0xA917, SQOFF)
        self.ds16(0xA919, SQSEG)
        self.ds16(0xA923, FOFF)
        self.ds16(0xA925, FSEG)
        ds = self.mem.DS * 16
        lin = {self.mem.lin(f"0791:{a:04X}"): f"0791:{a:04X}" for a in range(0x7C00, 0xCB00)}

        def watch(address, size, value, at):
            if ds <= address <= ds + 0xFFFF:
                self.writes.append((address - ds, size, value, lin.get(at, at)))
        self.mem.listeners.append((0, len(self.mem.memory), watch))

    def ds8(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off] = value & 0xFF

    def ds16(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off:self.mem.DS * 16 + off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def lin8(self, lin, value):
        self.mem.memory[lin] = value & 0xFF

    def lin16(self, lin, value):
        self.mem.memory[lin:lin + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def player(self, word, k, value):
        """Byte k of the player record of `word`."""
        self.lin8(PSEG * 16 + POFF + 0x14 * word + k, value)

    def squad(self, country, words):
        """The country's squad words 1.. (its record at DS:A917 + 0xBF country)."""
        base = SQSEG * 16 + SQOFF + 0xBF * country
        for k, w in enumerate(words, 1):
            self.lin16(base + 2 * k - 2, w)

    def pitch(self, slot, word):
        """The pitch record of `slot`: its slot byte +6 and player word +0xD."""
        rec = 0x80E8 + 0x16 * slot
        self.ds8(rec + 6, slot)
        self.ds16(rec + 0xD, word)
        return rec

    def run(self, address, words=(), answer=None):
        entry = port._module_registry("discipline").entries[address]
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
        return [(off, size, value) for off, size, value, at in self.writes if at == writer]


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


# -- 7EEF: the cards of a foul -------------------------------------------------------------------------------------
def foul_rig(status):
    r = Rig()
    r.ds8(0x830C, 3)                                   # the fouler's slot
    r.ds8(0x830B, 15)                                  # the fouled
    rec = r.pitch(3, 5)
    r.pitch(15, 6)
    r.player(5, 0x10, status)                          # the fouler's status: element k is bit k - 1
    return r, rec


class FoulDispatch(Case):
    def test_second_yellow_sends_off(self):
        """7F0E-7F42: a table byte below 4 (261A) with the fouler's status +0x10 holding element 5 (a booking already,
        214B:0C57(5, status) true) sends him off: 7B77(his record), never 798D."""
        r, rec = foul_rig(status=0x10)
        r.run("0791:7EEF", answer=answers({"0791:261A": [2, 0], "214B:0C57": 1}))
        self.assertEqual(r.targets(), [("0791:261A", "0791:7F0E"), ("214B:0C57", "0791:7F35"),
                                       ("0791:7B77", "0791:7F42"), ("0791:261A", "0791:7F68")])
        self.assertEqual(r.args("214B:0C57"), [(5, 0x10)])
        self.assertEqual(r.args("0791:7B77"), [(r.mem.DS, rec)])

    def test_first_yellow_books(self):
        """The reached twin (7F44): no booking yet (0C57 false): 798D(his record)."""
        r, rec = foul_rig(status=0)
        r.run("0791:7EEF", answer=answers({"0791:261A": [3, 0], "214B:0C57": 0}))
        self.assertEqual(r.targets()[2], ("0791:798D", "0791:7F4D"))
        self.assertEqual(r.args("0791:798D"), [(r.mem.DS, rec)])
        self.assertEqual(r.args("0791:7B77"), [])

    def test_the_softer_player_is_injured(self):
        """7F65-7FC8: a second table byte of 1 injures (7D56) the one of DS:830C and DS:830B of lower hardness
        (1771:2FFB): the fouler when his is lower (7FB0), the fouled on a tie (7F99 jbe; 7FC8)."""
        for fouler, fouled, slot, ret in ((3, 7, 3, "0791:7FB3"), (7, 7, 15, "0791:7FCB"), (8, 2, 15, "0791:7FCB")):
            r, rec = foul_rig(status=0)
            r.run("0791:7EEF", answer=answers({"0791:261A": [9, 1], "214B:06D0": 0, "1771:2FFB": [fouler, fouled]}))
            self.assertEqual(r.targets()[-1], ("0791:7D56", ret))
            self.assertEqual(r.args("0791:7D56"), [(r.mem.DS, 0x80E8 + 0x16 * slot)])


# -- C88D and 8062: the substitution budget ------------------------------------------------------------------------
def substitute_rig(budget, fitness):
    r = Rig()
    side, slot, country = 1, 15, 4
    r.ds8(0x9B3A + side, budget)
    r.ds8(0x668 + side, 11)                            # the side's slot before its first
    r.ds16(0x9B34 + 2 * side, country)
    r.squad(country, [0x40 + k for k in range(1, 21)])
    r.player(0x44, 0xE, fitness)                       # the outgoing (squad index 15 - 11 = 4): his +0xE
    r.ds16(0x80E8 + 0x16 * slot + 0xD, 0x44)
    return r, side, slot, country


class SubstitutionBudget(Case):
    def test_budget_0_injured_only_the_forced_swap(self):
        """C899-C8DB: with no substitution left (DS:9B3A + side = 0) and the outgoing player injured (+0xE < 1) the
        only call is the forced swap C48D(squad, slot); nothing is picked and no count is written."""
        r, side, slot, country = substitute_rig(budget=0, fitness=0)
        sq = SQOFF + 0xBF * country
        r.run("0791:C88D", [1, side, slot, sq, SQSEG])
        self.assertEqual(r.targets(), [("0791:C48D", "0791:C8DB")])
        self.assertEqual(r.args("0791:C48D"), [(SQSEG, sq, slot)])

    def test_budget_0_fit_player_goes_on(self):
        """The twin past C8CE (+0xE = 1, signed >= 1): the map is cleared (214B:0018 on DS:99A2, 14 bytes), C7EB and
        AAE8 are asked, and with no pick and the flag A9B8(country, position, 0x14); none: nothing more."""
        r, side, slot, country = substitute_rig(budget=0, fitness=1)
        r.player(0x44, 6, 3)
        r.run("0791:C88D", [1, side, slot, SQOFF + 0xBF * country, SQSEG])
        self.assertEqual(r.targets(), [("214B:0018", "0791:C8EF"), ("0791:C7EB", "0791:C8F3"),
                                       ("0791:AAE8", "0791:C909"), ("0791:A9B8", "0791:C96B")])
        self.assertEqual(r.args("214B:0018"), [(r.mem.DS, 0x99A2, 0xE, 0)])
        self.assertEqual(r.args("0791:C7EB"), [(BP0,)])
        self.assertEqual(r.args("0791:A9B8"), [(country, 3, 0x14)])

    def test_computer_side_with_budget_0_is_not_scanned(self):
        """8111-8118: an unmanaged side (1771:0B77 0) with DS:9B3A + side = 0 is skipped: no status test 214B:0C57."""
        r = Rig()
        r.ds16(0x831B, 10)
        r.run("0791:8062", answer=answers({"1771:0B77": 0}))
        self.assertEqual(r.targets(), [("1771:0B77", "0791:8082"), ("1771:0B77", "0791:8082")])

    def test_computer_side_with_budget_1_is_scanned(self):
        """The reached twin (811B): side 1 with one substitution left: squad slots 11 down to 1 tested (0C57(6, status),
        element 6 set for each: none is substituted)."""
        r = Rig()
        r.ds8(0x9B3A + 1, 1)
        r.ds8(0x668 + 1, 11)
        for k in range(1, 12):
            r.pitch(11 + k, 0x40 + k)
        r.run("0791:8062", answer=answers({"1771:0B77": 0, "214B:0C57": 1}))
        self.assertEqual(r.targets(), [("1771:0B77", "0791:8082"), ("1771:0B77", "0791:8082")]
                         + [("214B:0C57", "0791:8170")] * 11)


# -- C173 and BF6B: the computer's tactic shift ----------------------------------------------------------------------
class TacticShift(Case):
    def shift(self, mine, theirs):
        r = Rig()
        r.ds8(0x9B3C, mine)
        r.ds8(0x9B3D, theirs)
        r.run("0791:C173", [0x1111], answers({"1771:0B77": [0, 1]}))
        return r

    def test_two_ahead_shifts_back(self):
        """C1C1-C1FC: a computer side two goals ahead (|DS:9B3C - DS:9B3D| = 2, its goals above the other's) calls
        BF6B(0, side, C173's BP): its tactics take elements out."""
        r = self.shift(3, 1)
        self.assertEqual(r.targets(), [("1771:0B77", "0791:C1A2"), ("0791:BF6B", "0791:C1FC"),
                                       ("1771:0B77", "0791:C1A2")])
        self.assertEqual([(a[0] & 0xFF, a[1] & 0xFF, a[2]) for a in r.args("0791:BF6B")], [(0, 0, BP0)])

    def test_two_behind_shifts_forward(self):
        """C1FE-C209: two goals behind: BF6B(1, side, C173's BP)."""
        r = self.shift(1, 3)
        self.assertEqual(r.targets()[1], ("0791:BF6B", "0791:C209"))
        self.assertEqual([(a[0] & 0xFF, a[1] & 0xFF) for a in r.args("0791:BF6B")], [(1, 0)])

    def shift_routine(self, direction):
        r = Rig()
        r.ds16(0x9B34 + 2, 4)                          # side 1's country
        r.lin8(SQSEG * 16 + SQOFF + 0xBF * 4 + 0x2D, 0x21)
        r.run("0791:BF6B", [0x1111, 1, direction], answers({"214B:06B1": [2, 5, 6]}))
        return r

    def test_behind_adds_three_elements(self):
        """BF9F-BFBD: the direction set: BD83(side), then three rand(6) elements added to the country's tactics +0x2D
        (214B:0C79), then BBFF(country, +0x2D)."""
        r = self.shift_routine(1)
        self.assertEqual(r.targets(), [("0791:BD83", "0791:BF95")]
                         + [("214B:06B1", "0791:BFAE"), ("214B:0C79", "0791:BFBD")] * 3
                         + [("0791:BBFF", "0791:BFF4")])
        tactics = SQOFF + 0xBF * 4 + 0x2D
        self.assertEqual(r.args("214B:0C79"), [(2, SQSEG, tactics), (5, SQSEG, tactics), (6, SQSEG, tactics)])
        self.assertEqual([(a[0], a[1] & 0xFF) for a in r.args("0791:BBFF")], [(4, 0x21)])

    def test_ahead_takes_three_elements_out(self):
        """BFBF-BFD7: the direction clear: the three elements taken out (214B:0CA1)."""
        r = self.shift_routine(0)
        self.assertEqual(r.targets()[1:7], [("214B:06B1", "0791:BFC8"), ("214B:0CA1", "0791:BFD7")] * 3)
        self.assertEqual(r.args("214B:0C79"), [])


# -- the kit's events: the injury (7DD9) and the substitution (C7DC) --------------------------------------------------
class EventWriters(Case):
    def test_injury_written_as_7dd9(self):
        """7DD1-7DD9: the side's injuries DS:7B87 + 10 side +1, written by 7DD9 (match.py WRITERS["injury"]) and by no
        other instruction; the player's +0xE := 0 (7D9B); a managed side's keeper raises DS:9B40 (7E55)."""
        r = Rig()
        rec = r.pitch(14, 9)
        r.player(9, 0xE, 50)
        r.ds8(0x7B87 + 10, 1)
        r.run("0791:7D56", [rec, r.mem.DS], answers({"0791:2956": 0, "0791:2974": 1, "0791:7A43": 1,
                                                    "1771:0B77": 1}))
        self.assertEqual(r.written("0791:7DD9"), [(0x7B87 + 10, 1, 2)])
        self.assertEqual([w for w in r.writes if 0x7B7E <= w[0] <= 0x7B91 and w[3] != "0791:7DD9"], [])
        self.assertEqual(r.mem.u8(PSEG * 16 + POFF + 0x14 * 9 + 0xE), 0)
        self.assertEqual(r.written("0791:7E55"), [(0x9B40, 1, 1)])

    def test_no_injury_when_the_side_may_lose_no_more(self):
        """The twin at 7D76: 7A43 answers 0: nothing is written."""
        r = Rig()
        rec = r.pitch(14, 9)
        r.run("0791:7D56", [rec, r.mem.DS], answers({"0791:2956": 0, "0791:2974": 1, "0791:7A43": 0}))
        self.assertEqual(r.writes, [])
        self.assertEqual(r.targets()[-1], ("0791:7A43", "0791:7D76"))

    def test_substitution_written_as_c7dc(self):
        """C7D6-C7DC: the side's substitutions left DS:9B3A + side -1, written by C7DC (WRITERS["substitution"]) and by
        no other instruction; DS:9B55 := 1 (C7E0)."""
        r = Rig()
        rec = r.pitch(15, 0x44)
        r.ds8(0x9B3A + 1, 3)
        r.ds8(0x668 + 1, 11)
        r.run("0791:C5DC", [7, 15, 1], answers({"1771:0B77": 1}))
        self.assertEqual(r.written("0791:C7DC"), [(0x9B3A + 1, 1, 2)])
        self.assertEqual([w for w in r.writes if w[0] in (0x9B3A, 0x9B3B) and w[3] != "0791:C7DC"], [])
        self.assertEqual(r.written("0791:C7E0"), [(0x9B55, 1, 1)])
        self.assertEqual(r.args("0791:A2E6"), [(15, r.mem.DS, rec)])



# -- the branches no match of ALL reaches ----------------------------------------------------------------------------
class Unreached(Case):
    def test_injury_of_an_unavailable_player(self):
        """7D65-7D7A: the record is unavailable (2956 true): nothing is asked or written."""
        r = Rig()
        rec = r.pitch(14, 9)
        r.run("0791:7D56", [rec, r.mem.DS], answers({"0791:2956": 1}))
        self.assertEqual(r.targets(), [("0791:2956", "0791:7D65")])
        self.assertEqual(r.writes, [])

    def keeper_rig(self, last, pos, two_footed, feet):
        r = Rig()
        country = 4
        r.squad(country, [0x60 + k for k in range(1, 21)])
        for k, role, value in ((12, 1, 0x40), (13, 2, 0x30)):
            r.player(0x60 + k, 7, role)
            r.ds8(0x8D5 + 0xE * 3 + role, value)
        r.run("0791:A9B8", [last, 3, country],
              answers({"1771:3216": 0, "23E4:06E3": pos, "1771:3041": two_footed, "1771:3088": feet}))
        return r

    def test_keeper_pick_with_no_bench_slot(self):
        """A9FF-AA07: the last squad slot below 12: no slot is tested, the answer 0."""
        r = self.keeper_rig(0xB, 0, 0, 0)
        self.assertEqual(r.targets(), [("23E4:075A", "0791:A9EC"), ("23E4:06E3", "0791:A9F6")])
        self.assertEqual(r.mem.regs["ax"], 0)

    def test_keeper_pick_with_a_foot(self):
        """AA6B-AAB7: the position has a foot (Pos 5 > 3: foot 1): slot 12 (0x40), one-footed (3041 0) with foot 0, is
        halved to 0x20; slot 13 (0x30), two-footed, keeps it: the pick is 13."""
        r = self.keeper_rig(0xD, 5, [0, 1], [0])
        self.assertEqual(r.mem.regs["ax"], 13)
        self.assertEqual(r.targets(), [("23E4:075A", "0791:A9EC"), ("23E4:06E3", "0791:A9F6"),
                                       ("1771:3216", "0791:AA25"), ("1771:3041", "0791:AA84"),
                                       ("1771:3088", "0791:AA9B"), ("1771:3216", "0791:AA25"),
                                       ("1771:3041", "0791:AA84")])
        self.assertEqual(r.mem.u16(BP0 - 0xA), 0x30)                         # [bp - 0xa], the last value

    def test_keeper_pick_foot_matches(self):
        """AAA3: Pos 2 (not above 3: foot 0) and slot 12's foot 0: not halved, 0x40 beats 0x30: the pick is 12."""
        r = self.keeper_rig(0xD, 2, [0, 0], [0, 1])
        self.assertEqual(r.mem.regs["ax"], 12)

    def test_keeper_pick_without_a_foot(self):
        """The reached twin (AA6F jbe AABA): Pos 0: no foot test, the higher value wins: 12."""
        r = self.keeper_rig(0xD, 0, 0, 0)
        self.assertEqual(r.mem.regs["ax"], 12)
        self.assertEqual(r.args("1771:3041"), [])

    def formation_rig(self, pos, count):
        r = Rig()
        r.player(0x30, 6, 2)                           # the outgoing player's position 2: the row DS:099A + 16
        r.ds8(0x99A + 16, count)
        r.ds8(0x99A + 16 + 1, 5)                       # entry 1: role 5
        r.ds8(0x99A2 + 5, 14)                          # C7EB's map: role 5 -> bench slot 14
        r.run("0791:AAE8", [SQOFF, SQSEG, 0x30], answers({"23E4:06E3": pos, "1771:3041": 1}))
        return r

    def test_formation_row_empty_with_a_foot(self):
        """AB66-AB6E: a foot for the position (Pos 2) and a row of 0 entries: nothing is tested, the answer 0."""
        r = self.formation_rig(2, 0)
        self.assertEqual(r.targets(), [("23E4:075A", "0791:AB36"), ("23E4:06E3", "0791:AB40")])
        self.assertEqual(r.mem.regs["ax"], 0)

    def test_formation_row_with_a_foot(self):
        """The reached twin (AB71): one entry, its bench slot 14 two-footed (3041): the pick is 14."""
        r = self.formation_rig(2, 1)
        self.assertEqual(r.targets()[2:], [("1771:3041", "0791:ABB4")])
        self.assertEqual(r.mem.regs["ax"], 14)

    def big_gap(self, mine, theirs):
        r = Rig()
        r.ds8(0x9B3C, mine)
        r.ds8(0x9B3D, theirs)
        r.run("0791:C173", [0x1111], answers({"1771:0B77": [0, 1]}))
        return r

    def test_three_ahead_excludes(self):
        """C20B-C234 for side 0 (C215): more than two goals ahead: C0DF(side, C173's BP)."""
        r = self.big_gap(4, 1)
        self.assertEqual(r.targets()[1], ("0791:C0DF", "0791:C234"))
        self.assertEqual([(a[0] & 0xFF, a[1]) for a in r.args("0791:C0DF")], [(0, BP0)])

    def test_three_behind_includes(self):
        """C236-C23E: more than two goals behind: C01A(side, C173's BP)."""
        r = self.big_gap(0, 3)
        self.assertEqual(r.targets()[1], ("0791:C01A", "0791:C23E"))

    def test_one_goal_gap_resets(self):
        """The reached twin (C1B8): a gap below 2: BD83(side)."""
        r = self.big_gap(1, 0)
        self.assertEqual(r.targets()[1], ("0791:BD83", "0791:C1BF"))

    def captain_rig(self, unavailable):
        r = Rig()
        rec = r.pitch(15, 0x44)
        r.ds8(0x9B3A + 1, 3)
        r.ds16(0x9B34, 4)                               # side 0's country
        r.squad(4, [0x61, 0x62])
        r.ds16(0x9978, 0x55)                            # side 0's word DS:9978
        r.run("0791:C5DC", [7, 15, 1], answers({"1771:0B77": [1, 1, 0], "1771:3216": unavailable}))
        return r, rec

    def test_unavailable_captain_word_replaced_around_230c(self):
        """C76A-C79D and C7B9-C7CC: a managed side whose word DS:9978 + 10 side is unavailable (3216): the word := its
        country's first squad word, flagged at [bp - 6 + side], 230C, then the word := 0."""
        r, rec = self.captain_rig(1)
        self.assertEqual(r.written("0791:C79D"), [(0x9978, 2, 0x61)])
        self.assertEqual(r.written("0791:C7CC"), [(0x9978, 2, 0)])
        self.assertEqual(r.targets()[-1], ("0791:230C", "0791:C7AA"))
        self.assertEqual(r.mem.u8(BP0 - 6), 1)

    def test_available_captain_word_kept(self):
        """The reached twin (C76C je C7A1): the word available: neither written."""
        r, rec = self.captain_rig(0)
        self.assertEqual(r.written("0791:C79D") + r.written("0791:C7CC"), [])


if __name__ == "__main__":
    unittest.main()
