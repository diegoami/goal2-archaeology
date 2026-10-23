"""T70: the branches of the set-up port (runtime/original_match/port/setup.py) that the task names and those no match of
ALL reaches (out/T70/coverage-summary.tsv), run on synthetic memory with the listing's values, each with a reached
twin: each fixture kind's substitution budget (A54C-A605), the host country (A6E4's 1771:5A03 branch and its two
continents, and D44C), a computer side short of a keeper (AFA3's slot 1 held by a non-keeper with no bench player for
his role: A9B8), and the blocks no match of ALL executes (the coverage run 39907282938): 1073's fixed colours (107D)
and team 1's clash (1117); A4A1 with neither country managed (A65D); A6E4's slot 5 (A715); AFA3's out-of-place starter
(B048) and its replacements (B0BE, B0C8, B0D3, B107); 52CC for a managed country (535F, 5375); and 580B's titles of the
kinds ALL does not play (5816 to 599F). No byte of the original."""
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
        entry = port._module_registry("setup").entries[address]
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


# -- A4A1: each kind's budget ----------------------------------------------------------------------------------------
class Budget(Case):
    def setup(self, kind):
        r = Rig()
        r.ds8(0x66B, 5)                                  # DS:066B: a friendly's budget
        r.ds8(0x66C, 2)                                  # DS:066C: every other kind's
        r.fixture(kind, 7, 19)
        r.run("0791:A4A1", [FXOFF, FXSEG])
        return r

    def test_friendly_takes_066b(self):
        """A547-A554, A5F5-A605: a fixture of kind 1 (a friendly): DS:9A3D := 0, so each side's budget DS:9B3A + side
        := DS:066B (5)."""
        r = self.setup(1)
        self.assertEqual(r.written("0791:A554"), [(0x9A3D, 1, 0)])
        self.assertEqual(r.written("0791:A605"), [(0x9B3A, 1, 5), (0x9B3B, 1, 5)])

    def test_other_kinds_take_066c(self):
        """A552: every other kind (2 a qualifier, 3, 8, 0xC8 a final...): DS:9A3D := 1, the budget DS:066C (2)."""
        for kind in (0, 2, 3, 5, 8, 0x65, 0xC8, 0xFF):
            r = self.setup(kind)
            self.assertEqual(r.written("0791:A554"), [(0x9A3D, 1, 1)], kind)
            self.assertEqual(r.written("0791:A605"), [(0x9B3A, 1, 2), (0x9B3B, 1, 2)], kind)

    def test_the_setup_calls_in_order(self):
        """A4A1's calls, in the listing's order, with their return addresses: the computer sides, the kit colours, the
        clears, the coin, the ball and points, the 22 pitch records, the two side points, 230C, 2FB1, the managed test
        of both countries, the last clear and the screen."""
        r = self.setup(2)
        fills = [("214B:0018", ret) for ret in ("0791:A4C9", "0791:A4EF", "0791:A500", "0791:A511", "0791:A522",
                                                "0791:A533", "0791:A544")]
        self.assertEqual(r.targets(),
                         [("0791:A3DE", "0791:A4AF"), ("0791:1073", "0791:A4B8")] + fills
                         + [("214B:06FA", "0791:A55C"), ("0791:A375", "0791:A581"), ("0791:A3B6", "0791:A58A"),
                            ("0791:A3B6", "0791:A593")] + [("0791:A2E6", "0791:A5B4")] * 22
                         + [("0791:A3B6", "0791:A5F5")] * 2
                         + [("0791:230C", "0791:A612"), ("0791:2FB1", "0791:A615"), ("1771:0B77", "0791:A64C"),
                            ("1771:0B77", "0791:A659"), ("214B:0018", "0791:A67C"), ("0791:A841", "0791:A689")])
        self.assertEqual(r.args("0791:A2E6"), [(k, r.mem.DS, 0x80E8 + 0x16 * k) for k in range(1, 23)])
        self.assertEqual(r.args("0791:A3B6"), [(r.mem.DS, 0x82EE), (r.mem.DS, 0x8304), (r.mem.DS, 0x82E2),
                                                (r.mem.DS, 0x82E8)])


class Managed(Case):
    def flag(self, managed):
        r = Rig()
        r.fixture(2, 7, 19)
        r.ds16(0x9B34, 7)
        r.ds16(0x9B36, 19)
        r.run("0791:A4A1", [FXOFF, FXSEG], answers({"1771:0B77": managed}))
        return r

    def test_neither_managed(self):
        """A64C-A65D: neither country managed (1771:0B77 of DS:9B36, then of DS:9B34, both 0): DS:80FD := 0."""
        r = self.flag([0, 0])
        self.assertEqual(r.args("1771:0B77"), [(19,), (7,)])
        self.assertEqual(r.written("0791:A663"), [(0x80FD, 1, 0)])

    def test_one_managed(self):
        """The reached twins: the second country managed (A64E jne A661, one test) or the first (A65B): DS:80FD := 1."""
        r = self.flag([1])
        self.assertEqual(r.args("1771:0B77"), [(19,)])
        self.assertEqual(r.written("0791:A663"), [(0x80FD, 1, 1)])
        r = self.flag([0, 1])
        self.assertEqual(r.args("1771:0B77"), [(19,), (7,)])
        self.assertEqual(r.written("0791:A663"), [(0x80FD, 1, 1)])


# -- 1073: the kit colours -------------------------------------------------------------------------------------------
class KitColours(Case):
    def colours(self, fixed, first, second):
        """first, second: the three kit bytes of country 7 (team 0) and 19 (team 1) at DS:9D80 + 3 country."""
        r = Rig()
        r.ds8(0xA964, fixed)
        r.ds16(0x9B34, 7)
        r.ds16(0x9B36, 19)
        for c, kit in ((7, first), (19, second)):
            for k, v in enumerate(kit):
                r.ds8(0x9D80 + 3 * c + k, v)
        r.run("0791:1073")
        return {off: v for off, _, v, _ in r.writes if off in (0x832E, 0x832F, 0x8330, 0x8331)}, r

    def test_fixed_colours(self):
        """107D-108C: with DS:A964 set the colours are 4, 1, 0xC, 9 whatever the countries' kits."""
        got, r = self.colours(1, (2, 3, 5), (6, 7, 8))
        self.assertEqual(got, {0x832F: 1, 0x832E: 4, 0x8331: 9, 0x8330: 0xC})
        self.assertEqual(r.written("0791:107D"), [(0x832F, 1, 1)])

    def test_team_1_clash(self):
        """110E-1125: team 1's second colour equal to team 0's shirt: 8331 := team 1's third byte."""
        got, r = self.colours(0, (2, 3, 5), (6, 7, 2))
        self.assertEqual(got, {0x832F: 6, 0x8331: 7, 0x832E: 2, 0x8330: 5})
        self.assertEqual(r.written("0791:1125"), [(0x8331, 1, 7)])

    def test_no_clash(self):
        """The reached twin (1115 jne 1128): no colour equal: the kits as they are."""
        got, r = self.colours(0, (2, 3, 5), (6, 7, 8))
        self.assertEqual(got, {0x832F: 6, 0x8331: 8, 0x832E: 2, 0x8330: 5})
        self.assertEqual(r.written("0791:1125"), [])

    def test_team_0_clashes(self):
        """The reached 10E1 and 10FD: team 0's shirt, else its second colour, equal to team 1's shirt: its third byte."""
        got, _ = self.colours(0, (6, 3, 5), (6, 7, 8))
        self.assertEqual(got[0x832E], 3)
        got, _ = self.colours(0, (2, 3, 6), (6, 7, 8))
        self.assertEqual(got[0x8330], 3)


# -- A6E4 and D44C: the host country ---------------------------------------------------------------------------------
class Host(Case):
    def host(self, in_set, flag40, continent):
        r = Rig()
        r.fixture(2, 7, 19)
        r.country(19, 0x2C, continent)                   # the second country's continent
        r.lin8(GSEG * 16 + GOFF + 0x40, flag40)
        for c in range(6):                               # the hosts [A923] + 0x2C + 2 c
            r.lin16(GSEG * 16 + GOFF + 0x2C + 2 * c, 100 + c)
        value = r.run("0791:A6E4", [FXOFF, FXSEG], answers({"1771:5A03": in_set}))
        self.assertEqual(r.targets(), [("1771:5A03", "0791:A707")])
        self.assertEqual(r.args("1771:5A03"), [(FXSEG, FXOFF)])
        return value

    def test_not_in_the_set_the_second_country(self):
        """A74A: 1771:5A03 false for the fixture: the second country (+6)."""
        self.assertEqual(self.host(0, 1, 3), 19)

    def test_in_the_set_with_0x40_slot_5(self):
        """A70B-A715, A737-A741: 5A03 true and [A923]+0x40 set: the host word [A923] + 0x2C + 2 * 5."""
        self.assertEqual(self.host(1, 1, 3), 105)

    def test_in_the_set_the_continent(self):
        """A71C-A741: 5A03 true and [A923]+0x40 clear: the host of the second country's continent (+0x2C)."""
        self.assertEqual(self.host(1, 0, 3), 103)
        self.assertEqual(self.host(1, 0, 0), 100)

    def test_second_team_is_host(self):
        """D44C-D472: 1 when A6E4's answer is the fixture's +6, else 0 (D46C)."""
        for host, expected in ((19, 1), (7, 0), (103, 0)):
            r = Rig()
            r.fixture(2, 7, 19)
            value = r.run("0791:D44C", [FXOFF, FXSEG], answers({"0791:A6E4": host}))
            self.assertEqual(value & 0xFF, expected, host)
            self.assertEqual(r.targets(), [("0791:A6E4", "0791:D463")])
            self.assertEqual(r.args("0791:A6E4"), [(FXSEG, FXOFF)])


# -- AFA3: a computer side short of a keeper -------------------------------------------------------------------------
def lineup_rig(keeper_role):
    """Country 4's squad words 0x41.. ; the player in slot 1 plays in goal (+6 = 0) and has the natural role
    `keeper_role` (+7); B11F's frame at PARENT with the country word at [bp + 6]."""
    r = Rig()
    country = 4
    r.squad(country, [0x40 + k for k in range(1, 21)])
    r.player(0x41, 6, 0)
    r.player(0x41, 7, keeper_role)
    r.lin16(PARENT + 6, country)
    r.lin16(PARENT - 2, 0x7777)
    return r, country


class ShortOfAKeeper(Case):
    def test_no_bench_keeper_takes_a9b8s_choice(self):
        """B0A3-B0BE, B0D3-B10D: slot 1 held by a non-keeper (+7 = 3), no bench player for him (AAE8 0) and none
        unavailable (3216) or out of place (3179): A9B8(country, his +6, 0x14) picks one (slot 15), written into
        B11F's [bp - 2] (B0F9), and swapped in: AD8F(1, B11F's BP)."""
        r, country = lineup_rig(keeper_role=3)
        r.run("0791:AFA3", [PARENT], answers({"0791:A9B8": 15}))
        self.assertEqual(r.args("0791:A9B8"), [(country, 0, 0x14)])
        self.assertEqual(r.targets()[:5], [("0791:AAE8", "0791:AFE7"), ("1771:3216", "0791:B093"),
                                           ("1771:3179", "0791:B09F"), ("0791:A9B8", "0791:B0F6"),
                                           ("0791:AD8F", "0791:B110")])
        self.assertEqual(r.args("0791:AD8F"), [(1, PARENT)])
        self.assertEqual(r.u16(PARENT - 2), 0)          # slot 11's AAE8 answer is the last write (AFEA)
        self.assertEqual(len(r.args("0791:AAE8")), 11)

    def test_no_keeper_anywhere_nothing(self):
        """B100: A9B8 finds none (0): nothing is swapped in."""
        r, country = lineup_rig(keeper_role=3)
        r.run("0791:AFA3", [PARENT])
        self.assertEqual(r.args("0791:A9B8"), [(country, 0, 0x14)])
        self.assertEqual(r.args("0791:AD8F"), [])

    def test_a_keeper_in_goal_stays(self):
        """The twin (B0B7 je B110): slot 1 held by a keeper (+7 = 0): no A9B8, no swap."""
        r, country = lineup_rig(keeper_role=0)
        r.run("0791:AFA3", [PARENT], answers({"0791:A9B8": 15}))
        self.assertEqual(r.args("0791:A9B8"), [])
        self.assertEqual(r.args("0791:AD8F"), [])


class Replacements(Case):
    def rig(self, starter, bench):
        """Slot 1's player 0x41 with (+6, +7) = starter; bench slot 13's player 0x4D with +7 = bench."""
        r, country = lineup_rig(keeper_role=starter[1])
        r.player(0x41, 6, starter[0])
        r.player(0x4D, 7, bench)
        return r

    def test_out_of_place_starter_gives_way_to_the_role(self):
        """B020-B07F: the bench player b = 13 (AAE8) is not stronger (1771:377E 40 against the starter's 50), but the
        starter plays away from his +7 (+6 2, +7 3) and b's +7 is the starter's +6 (B048): AD8F(1) at B07F."""
        r = self.rig((2, 3), 2)
        r.run("0791:AFA3", [PARENT], answers({"0791:AAE8": [13] + [0] * 10, "1771:377E": [50, 40]}))
        self.assertEqual(r.args("1771:377E"), [(0x41,), (0x4D,)])
        self.assertEqual(r.targets()[:4], [("0791:AAE8", "0791:AFE7"), ("1771:377E", "0791:B003"),
                                           ("1771:377E", "0791:B01B"), ("0791:AD8F", "0791:B088")])
        self.assertEqual(r.args("0791:AD8F"), [(1, PARENT)])

    def test_bench_player_replaces_an_unplaced_keeper(self):
        """B07D jne B08B, then B0A3-B0C8: b's +7 is not the starter's +6, the starter (a non-keeper in slot 1) is
        replaced by b (B0C1: B11F's [bp - 2] = 13): AD8F(1) at B0C8, no A9B8."""
        r = self.rig((2, 3), 4)
        r.run("0791:AFA3", [PARENT], answers({"0791:AAE8": [13] + [0] * 10, "1771:377E": [50, 40]}))
        self.assertEqual(r.targets()[3:7], [("1771:3216", "0791:B093"), ("1771:3179", "0791:B09F"),
                                            ("0791:AD8F", "0791:B0D1"), ("0791:AAE8", "0791:AFE7")])
        self.assertEqual(r.args("0791:A9B8"), [])

    def test_unavailable_starter_replaced(self):
        """B093 jne B0BE: an unavailable starter (1771:3216) in slot 2 with a bench player: AD8F(2) at B0C8."""
        r, country = lineup_rig(keeper_role=0)
        r.run("0791:AFA3", [PARENT], answers({"0791:AAE8": [0, 14] + [0] * 9, "1771:377E": [50, 40],
                                              "1771:3216": [0, 1] + [0] * 9}))
        self.assertEqual(r.args("0791:AD8F"), [(2, PARENT)])
        self.assertIn(("0791:AD8F", "0791:B0D1"), r.targets())

    def test_stronger_bench_player(self):
        """The reached twin (B01E ja B07F): a stronger bench player comes in at once."""
        r = self.rig((0, 0), 0)
        r.run("0791:AFA3", [PARENT], answers({"0791:AAE8": [13] + [0] * 10, "1771:377E": [40, 50]}))
        self.assertEqual(r.targets()[3], ("0791:AD8F", "0791:B088"))


# -- 52CC: the squad sort of a managed country -----------------------------------------------------------------------
class SortManaged(Case):
    def sort(self, managed):
        r = Rig()
        country = 4
        words = [0x40 + k for k in range(1, 21)]
        r.squad(country, words)
        for k, w in enumerate(words, 1):
            r.player(w, 6, k % 7)
        r.ds8(0xF3A, 1)
        r.ds8(0xF3B, 12)
        r.ds8(0xF3C, 11)
        r.ds8(0xF3D, 20)

        def answer(request, mem):
            if request.target == "1771:0B77":
                return managed
            if request.target == "1771:3216":
                return 1 if request.args[0] in (0x43, 0x4E) else 0
            return 0
        r.run("1771:52CC", [country], answer)
        return r, words

    def test_managed_unavailable_sort_last(self):
        """5359-5378: for a managed country (1771:0B77 nonzero) each player is asked (1771:3216); an unavailable one's
        +6 := 0xE before the sort (517A(lo, hi, 52CC's BP) for 1..11 and 12..20), then every +6 is put back from the
        saved bytes (53CD)."""
        r, words = self.sort(1)
        self.assertEqual([a[0] for a in r.args("1771:3216")], words)
        lin = [PSEG * 16 + POFF + 0x14 * w + 6 for w in (0x43, 0x4E)]
        self.assertEqual(r.written("1771:5378"), [(lin[0], 1, 0xE), (lin[1], 1, 0xE)])
        self.assertEqual(r.args("1771:517A"), [(1, 11, BP0), (12, 20, BP0)])
        back = {off: v for off, _, v in r.written("1771:53CD")}
        self.assertEqual(back[lin[0]], 3 % 7)
        self.assertEqual(back[lin[1]], 14 % 7)
        self.assertEqual(len(back), 20)

    def test_computer_side_not_asked(self):
        """The reached twin (5359 je 537D): a computer country: no 3216, no 0xE."""
        r, words = self.sort(0)
        self.assertEqual(r.args("1771:3216"), [])
        self.assertEqual(r.written("1771:5378"), [])
        self.assertEqual(r.args("1771:517A"), [(1, 11, BP0), (12, 20, BP0)])


# -- 580B: the kind's title ------------------------------------------------------------------------------------------
TITLES = {0: (0x577F, "5829"), 1: (0x5789, "5844"), 2: (0x5792, "5864"), 5: (0x5792, "5864"), 6: (0x579D, "587F"),
          3: (0x57A6, "589F"), 7: (0x57A6, "589F"), 0xC8: (0x57B2, "58BA"), 0x65: (0x57BC, "58DA"),
          0xC9: (0x57BC, "58DA"), 0x67: (0x57C7, "58FA"), 0xCB: (0x57C7, "58FA"), 0x66: (0x57CD, "591A"),
          0xCA: (0x57CD, "591A"), 8: (0x57D7, "5935"), 0xFC: (0x57DF, "594F"), 0xFD: (0x57E6, "5969"),
          0xFE: (0x57EC, "5983"), 0xFF: (0x57F7, "599D"), 4: (0x57FF, "59B2"), 9: (0x57FF, "59B2"),
          0x64: (0x57FF, "59B2"), 0xC7: (0x57FF, "59B2"), 0x102: (0x57FF, "59B2")}


class KindTitle(Case):
    def test_every_kind(self):
        """5811-59AD: each kind's string of segment 1771 (the listing's `mov di, n` of its block) is stored with
        23E4:0644(CS:n, the result, 0xC), returning to the instruction after that block's call; any other kind takes
        CS:57FF (599F)."""
        for kind, (src, ret) in TITLES.items():
            r = Rig()
            r.run("1771:580B", [kind, 0x0123, 0x0456])
            self.assertEqual(r.calls, [("23E4:0644", (r.mem.seg(0x1771), src, 0x0456, 0x0123, 0xC), f"1771:{ret}",
                                        True)], hex(kind))


if __name__ == "__main__":
    unittest.main()
