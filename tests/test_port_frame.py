"""runtime/original_match/port/frame.py (T69): the commentary and the match frame, on the listing and on synthetic memory
(no byte of the original: the callees are stubs, the code under test is the port).

- ListingTests (no emulator): every row of SITES is a call of the listing (the instruction at the offset, its return
  address, its form, the callee's `ret n`); every call of the 14 routines has a row; the ports are the 14 routines of
  row T69 with the listing's return instruction.
- CommentaryTests (plain memory): 1C78 says whether a line repeats the newest and leaves AX and DX as its code does;
  1E53 adds the table's delta to the rating word, and the falsifier `rating-sign` changes it.
- FrameTests (unicorn): the branches the families do not reach, each with the callees stubbed: the tick loop's quick
  branch (D733 in place of the sweep, the stub counting), a replay and a snapshot pending (0C65 and 15B9, which flag
  clears the other), the clock's four ways (idle, sub-tick counting, a minute, the half's end), the sweep's second
  half (no ball in play), 998C's word left on the stack for 1EB5's `ret 8`, play_match's winner byte and its extra
  time and shoot-out; and the falsifiers that change an observable here (clock-reload, rating-sign,
  possession-swapped, sort-ties, ring-players-swapped).
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import port  # noqa: E402
from original_match.port import Registry, frame as F  # noqa: E402
from original_match.port.mem import PlainMem  # noqa: E402
from original_match.machine import Machine, MEM_SIZE  # noqa: E402
try:
    import unicorn  # noqa: F401
except ImportError:                    # a machine without unicorn (CI's code tier installs it, #304)
    Machine = None

LISTING = ROOT / "static/goal-exe/code"
ROUTINES = ("1C78", "1D4A", "1E53", "1EB5", "230C", "9564", "970C", "97D0", "983F", "98C4", "9955", "998C", "9A32",
            "F098")
INSN = re.compile(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)\s*(.*?)\s*$")
HEADER = re.compile(r"^; ---- routine ([0-9A-F]{4}:[0-9A-F]{4}) ")


def read_listing():
    """{'SSSS:OOOO': [(offset, size, text)]} of every routine of the listing."""
    out, current = {}, None
    for path in sorted(LISTING.glob("seg_*.asm")):
        for line in path.read_text().split("\n"):
            m = HEADER.match(line)
            if m:
                current = out.setdefault(m.group(1), [])
                continue
            m = INSN.match(line)
            if m and current is not None:
                current.append((int(m.group(1), 16), len(m.group(2).split()), m.group(3)))
    return out


LIST = read_listing()


def returns(address):
    """{(kind, words)} of the ret / retf instructions of a routine of the listing."""
    found = set()
    for _, _, text in LIST[address]:
        m = re.fullmatch(r"(retf|ret)(?: (0x[0-9a-f]+|[0-9]+))?", text)
        if m:
            found.add((m.group(1), int(m.group(2), 0) // 2 if m.group(2) else 0))
    return found


class ListingTests(unittest.TestCase):
    def test_every_row_is_a_call_of_the_listing(self):
        calls = {}
        for r in ROUTINES:
            instrs = LIST["0791:" + r]
            for i, (off, size, text) in enumerate(instrs):
                if text.startswith("call"):
                    far = "far" in text or (i > 0 and instrs[i - 1][2] == "push cs")
                    target = text.split()[-1]
                    if "far" not in text:
                        target = "0791:%04X" % (int(target, 16) & 0xFFFF)
                    calls[off] = (target, far, "0791:%04X" % (off + size))
        self.assertEqual(sorted(F.SITES), sorted(calls), "SITES has a row for each call of the 14 routines, no other")
        for off, (target, far, ret_to, nargs) in sorted(F.SITES.items()):
            with self.subTest(site="%04X" % off):
                self.assertEqual((target, far, ret_to), calls[off])
                rets = returns(target)
                self.assertEqual(rets, {("retf" if far else "ret", nargs)}, f"{target}: the words it pops")

    def test_a_row_with_the_wrong_words_is_refused(self):
        with self.assertRaises(port.PortError):
            F.go(0x1D5C)                                   # 1C78 pops one word

    def test_the_ports_are_the_14_routines_with_the_listings_returns(self):
        self.assertEqual(sorted(F.PORTS.entries), sorted("0791:" + r for r in ROUTINES))
        for r in ROUTINES:
            entry = F.PORTS.entries["0791:" + r]
            kinds = {(k, w) for k, w in returns("0791:" + r)}
            self.assertEqual(len(kinds), 1, r)
            (kind, words), = kinds
            self.assertEqual((entry.far, entry.pop), (kind == "retf", 2 * words), r)

    def test_the_variants_are_registered(self):
        self.assertEqual(sorted(F.PORTS.variants), ["clock-reload", "possession-swapped", "rating-sign",
                                                    "ring-players-swapped", "sort-ties"])


# -- the commentary on plain memory --------------------------------------------------------------------------------
DS_PARA = 0x2581
DS = DS_PARA * 16
SS = 0x0800
OTHER = 0x3000                     # the segment the country and player arrays are in
COUNTRIES, PLAYERS = 0x0100, 0x0400             # offsets in it


def plain(parent_args):
    """Plain memory with the data the commentary routines read, and a parent frame (BP 0x3000) holding the
    arguments (code byte [bp+4], words [bp+6] and [bp+8], side byte [bp+0xA]); the port's entry: SP 0x2F00 with the
    return address and the parent BP on the stack."""
    memory = bytearray(0x110000)
    mem = PlainMem(memory, 0, DS_PARA, {"ss": SS, "sp": 0x2F00, "bp": 0x2E00})
    code, p1, p2, side = parent_args

    def put(address, data):
        memory[address:address + len(data)] = bytes(data)
    put(DS + 0x0668, [0, 11])                                         # the side's first pitch slot
    put(DS + 0x9B34, (3).to_bytes(2, "little") + (4).to_bytes(2, "little"))      # the sides' countries
    put(DS + 0xA917, COUNTRIES.to_bytes(2, "little") + OTHER.to_bytes(2, "little"))    # DS:A917 far pointer
    put(DS + 0xA91B, PLAYERS.to_bytes(2, "little") + OTHER.to_bytes(2, "little"))      # DS:A91B far pointer
    base = SS * 16
    put(base + 0x3004, [code, 0])
    put(base + 0x3006, p1.to_bytes(2, "little"))
    put(base + 0x3008, p2.to_bytes(2, "little"))
    put(base + 0x300A, [side, 0])
    put(base + 0x2F00 + 2, (0x3000).to_bytes(2, "little"))            # the parent BP, the entry's [sp + 2]
    mem._entries.append((0x2F00, False))
    return mem, memory


def country_words(memory, country, words):
    at = OTHER * 16 + COUNTRIES + 0xBF * country
    for i, w in enumerate(words):
        memory[at + 2 * i:at + 2 * i + 2] = w.to_bytes(2, "little")


class CommentaryTests(unittest.TestCase):
    RING = DS + 0x7C38

    def ring(self, memory, newest, record):
        memory[DS + 0x80EE:DS + 0x80F0] = newest.to_bytes(2, "little")
        at = self.RING + 6 * newest
        memory[at:at + 6] = bytes([record[0]]) + record[1].to_bytes(2, "little") + record[2].to_bytes(2, "little") + bytes([record[3]])

    def run_1c78(self, args, newest_record):
        mem, memory = plain(args)
        country_words(memory, 4, [0x0A0A, 0x0B0B, 0x0C0C, 0x0D0D])   # side 1: country 4's player words (1-based)
        self.ring(memory, 2, newest_record)
        value = F.commentary_record_is_new(mem, None)
        return mem, memory, value

    def test_a_repeated_line_is_not_new(self):
        # the proposed line: code 7, words 2 and 3 of country 4 (0x0B0B, 0x0C0C), side 1
        mem, memory, ax = self.run_1c78((7, 3, 2, 1), (7, 0x0B0B, 0x0C0C, 1))
        self.assertEqual(ax & 0xFF, 0)
        self.assertEqual(memory[SS * 16 + 0x2DFF + 0], 0)            # [bp-1] of the port's frame (bp 0x2EFE)

    def test_each_field_that_differs_makes_the_line_new(self):
        for name, record in (("code", (8, 0x0B0B, 0x0C0C, 1)), ("first word", (7, 0x1111, 0x0C0C, 1)),
                             ("second word", (7, 0x0B0B, 0x1111, 1)), ("side", (7, 0x0B0B, 0x0C0C, 0))):
            with self.subTest(name):
                _, _, ax = self.run_1c78((7, 3, 2, 1), record)
                self.assertEqual(ax & 0xFF, 1)

    def test_a_zero_player_index_is_the_word_zero(self):
        _, _, ax = self.run_1c78((7, 0, 0, 1), (7, 0, 0, 1))
        self.assertEqual(ax & 0xFF, 0)
        _, _, ax = self.run_1c78((7, 0, 0, 1), (7, 0x0B0B, 0, 1))
        self.assertEqual(ax & 0xFF, 1)

    def test_ah_is_the_last_word_the_listing_loaded(self):
        # a mismatch of the first word (the second compare) leaves AH = the high byte of [bp-3] (1D10); a code mismatch
        # leaves the high byte of [bp-5] (the second player word, 1CFE)
        _, _, ax = self.run_1c78((7, 3, 2, 1), (7, 0x1111, 0x0C0C, 1))
        self.assertEqual(ax >> 8, 0x0B)
        _, _, ax = self.run_1c78((7, 3, 2, 1), (8, 0x0B0B, 0x0C0C, 1))
        self.assertEqual(ax >> 8, 0x0C)

    def rating(self, variant):
        mem, memory = plain((2, 0, 3, 1))                          # code 2, slot 3 of side 1 (slot 14)
        memory[DS + 0x0720 + 2] = 0xFE                            # the table's delta for code 2: -2
        rec = DS + 0x80E8 + 14 * 0x16
        memory[rec + 0xD:rec + 0xF] = (5).to_bytes(2, "little")   # the player on that slot
        player = OTHER * 16 + PLAYERS + 5 * 0x14
        memory[player + 0x12:player + 0x14] = (0x0100).to_bytes(2, "little")
        F.apply_perf_delta(mem, variant)
        return mem, int.from_bytes(memory[player + 0x12:player + 0x14], "little")

    def test_the_rating_word_gets_the_table_delta(self):
        mem, rating = self.rating(None)
        self.assertEqual(rating, 0x00FE)
        self.assertEqual((mem.reg("ax"), mem.reg("dx")), (0xFFFE, 0))     # cwde of the delta; mul's high word

    def test_the_falsifier_rating_sign_adds_it_the_other_way(self):
        self.assertEqual(self.rating("rating-sign")[1], 0x0102)


# -- the frame in the emulator, callees stubbed ----------------------------------------------------------------------
STACK_TOP = 0x0400
FLAGS = 0x2100                                    # DS:2100 + k: what stub k returns in AL (and ZF = AL == 0)


class Harness:
    """A machine whose memory holds a stub at every callee of SITES (not the ported ones) that returns a programmed AL
    with ZF = (AL == 0) and pops the words the listing says; the port(s) under test are installed in it."""

    def __init__(self, ports, args=(), start="0791:97D0", script=None, variant=None):
        self.script = script or {}
        sub = Registry("frame")
        for address in ports:
            sub._add(F.PORTS.entries[address])
        self.targets = sorted({row[0] for row in F.SITES.values()} - set(ports))
        memory = bytearray(MEM_SIZE)
        self.rows = {}
        for row in F.SITES.values():
            self.rows.setdefault(row[0], row)
        for k, target in enumerate(self.targets):
            _, far, _, nargs = self.rows[target]
            seg, off = (int(x, 16) for x in target.split(":"))
            code = bytes([0xA0, (FLAGS + k) & 0xFF, (FLAGS + k) >> 8, 0x0A, 0xC0,
                          0xCA if far else 0xC2, (2 * nargs) & 0xFF, 0])
            memory[seg * 16 + off:seg * 16 + off + len(code)] = code
        # the driver at 0791:0000: push the arguments, call the routine, nop (where the run ends)
        entry = int(start.split(":")[1], 16)
        code = b"".join(bytes([0x68, w & 0xFF, w >> 8]) for w in args)
        rel = (entry - (len(code) + 3)) & 0xFFFF
        code += bytes([0xE8, rel & 0xFF, rel >> 8, 0x90])
        memory[0x791 * 16:0x791 * 16 + len(code)] = code
        self.end = 0x791 * 16 + len(code) - 1
        self.m = m = Machine(memory, load=0)
        for reg, v in (("cs", 0x791), ("eip", 0), ("ss", SS), ("sp", STACK_TOP), ("bp", 0x0123), ("ds", m.DS),
                       ("es", m.DS), ("ax", 0), ("dx", 0)):
            m.set_reg(reg, v)
        self.calls = []
        self.counts = {}
        for k, target in enumerate(self.targets):
            m.at(target, lambda replay, target=target, k=k: self.on_call(target, k, replay))
        self.inst = port.install(m, [(sub, variant)])

    def on_call(self, target, k, replay):
        if replay:
            return
        _, far, _, nargs = self.rows[target]
        words = tuple(self.m.stack_word((4 if far else 2) + 2 * i) for i in reversed(range(nargs)))   # in pushing order
        self.calls.append((target, words))
        n = self.counts[target] = self.counts.get(target, 0) + 1
        script = self.script.get(target)
        if script is not None:                     # the AL the n-th call returns
            value = script(n) if callable(script) else script[min(n, len(script)) - 1]
            self.m.write(self.m.DS * 16 + FLAGS + k, bytes([value]))

    def ds(self, off, value=None, size=1):
        if value is not None:
            self.m.write(self.m.DS * 16 + off, int(value).to_bytes(size, "little"))
        return int.from_bytes(self.m.read(self.m.DS * 16 + off, size), "little")

    def run(self):
        self.m.run(self.end, 20, fresh=True)
        assert self.m.reg("sp") == STACK_TOP, hex(self.m.reg("sp"))       # every push popped, every frame left
        assert self.m.reg("bp") == 0x0123
        return [c for c in self.calls]

    def names(self):
        return [c[0].split(":")[1] for c in self.calls]


def addresses(*names):
    return ["0791:" + n for n in names]


@unittest.skipIf(Machine is None, "unicorn not installed")
class TickLoopTests(unittest.TestCase):
    """97D0 (match_tick_loop)."""

    def harness(self, **kw):
        h = Harness(addresses("97D0"), args=(kw.pop("arg", 0),))
        return h

    def test_the_quick_branch_calls_the_quick_result_in_place_of_the_sweep(self):
        h = self.harness()
        h.script["0791:970C"] = [0, 0, 1]                  # the clock says over on its third call
        h.ds(0x9A3E, 1)
        h.run()
        self.assertEqual(h.names(), ["D733", "970C", "D733", "970C", "D733", "970C"])
        self.assertEqual([c[1] for c in h.calls if c[0] == "0791:970C"], [(0x03FA,)] * 3)    # push bp: the loop's BP

    def test_a_replay_pending_runs_the_replay_then_a_sweep_and_clears_both_flags(self):
        h = self.harness()
        h.script["0791:970C"] = [1]
        h.ds(0x7C37, 1)
        h.ds(0x9B55, 1)                                    # a snapshot pending too: the replay comes first
        h.ds(0x0C20, 7)
        h.run()
        self.assertEqual(h.names(), ["0C65", "9564", "8CF5", "9119", "970C"])
        self.assertEqual(h.calls[3][1], (0, h.m.DS, 0x82EE))      # move_referee(0, ds, DS:82EE)
        self.assertEqual((h.ds(0x7C37), h.ds(0x9B55), h.ds(0x0C20)), (0, 0, 0))   # 0C20 cleared as 9B55 was set

    def test_a_snapshot_pending_is_taken_when_no_replay_is(self):
        h = self.harness()
        h.script["0791:970C"] = [1]
        h.ds(0x9B55, 1)
        h.ds(0x0C20, 7)
        h.run()
        self.assertEqual(h.names(), ["15B9", "9564", "8CF5", "9119", "970C"])
        self.assertEqual((h.ds(0x9B55), h.ds(0x0C20)), (0, 0))

    def test_no_flag_pending_goes_straight_to_the_sweep_and_leaves_0c20(self):
        h = self.harness()
        h.script["0791:970C"] = [1]
        h.ds(0x0C20, 7)
        h.run()
        self.assertEqual(h.names(), ["9564", "8CF5", "9119", "970C"])
        self.assertEqual(h.ds(0x0C20), 7)

    def test_the_quick_flag_set_by_the_sweep_skips_the_offside_line_and_the_referee(self):
        h = self.harness()
        h.script["0791:970C"] = [1]
        h.script["0791:9564"] = lambda n: 0
        # the sweep (9564) stub sets the quick flag, as the key poll's `R` does inside the real sweep
        h.m.at("0791:9564", lambda replay: replay or h.ds(0x9A3E, 1))
        h.run()
        self.assertEqual(h.names(), ["9564", "970C"])

    def test_with_the_argument_the_loop_goes_on_while_0c20_is_set(self):
        h = self.harness(arg=1)
        h.script["0791:970C"] = [0, 0, 0]
        h.ds(0x0C20, 1)
        h.m.at("0791:9564", lambda replay: replay or (h.counts.get("0791:9564", 0) >= 3 and h.ds(0x0C20, 0)))
        h.run()
        self.assertEqual(h.names().count("970C"), 3)       # 0C20 stays set for two passes, then clear: out

    def test_without_the_argument_it_loops_until_the_clock_says_over(self):
        h = self.harness(arg=0)
        h.script["0791:970C"] = [0, 0, 0, 0, 1]
        h.run()
        self.assertEqual(h.names().count("970C"), 5)


@unittest.skipIf(Machine is None, "unicorn not installed")
class ClockTests(unittest.TestCase):
    """970C (match_clock)."""

    def harness(self, variant=None):
        h = Harness(addresses("970C"), args=(0x0123,), start="0791:970C", variant=variant)
        h.ds(0x8325, 1)
        return h

    def result(self, h):
        h.run()
        return h.m.reg("ax") & 0xFF

    def test_play_off_returns_false_and_touches_nothing(self):
        h = self.harness()
        h.ds(0x8325, 0)
        h.ds(0x831D, 9, 2)
        self.assertEqual(self.result(h), 0)
        self.assertEqual((h.calls, h.ds(0x831D, size=2)), ([], 9))

    def test_the_sub_tick_counts_down(self):
        h = self.harness()
        h.ds(0x831D, 5, 2)
        self.assertEqual(self.result(h), 0)
        self.assertEqual((h.calls, h.ds(0x831D, size=2), h.ds(0x831F, size=2)), ([], 4, 0))

    def minute(self):
        h = self.harness()
        h.ds(0x831D, 0, 2)
        h.ds(0x831B, 3, 2)
        h.ds(0x8321, 4, 2)
        h.ds(0x8319, 0x2D)
        seen = []
        h.m.watch(h.m.DS * 16 + 0x831F, 2, lambda old, new: seen.append((int.from_bytes(new, "little"), h.m.pc())))
        return h, seen

    def test_a_minute_spends_a_tenth_counts_the_minute_and_redraws(self):
        h, seen = self.minute()
        self.assertEqual(self.result(h), 0)
        self.assertEqual(h.names(), ["054C"])
        self.assertEqual(h.calls[0][1], (2, 3))            # draw_big_digits(DS:831B after, 3)
        self.assertEqual((h.ds(0x831B, size=2), h.ds(0x831D, size=2), h.ds(0x8326)), (2, 0x24, 0))
        self.assertEqual(seen, [(1, h.m.lin("0791:9762"))])    # the minute's write is the instruction 9762's (the kit's)
        self.assertEqual(h.ds(0x831F, size=2), 1)

    def test_the_tenths_run_out_into_the_second_counter_and_the_minute_stops_at_0x80(self):
        h = self.harness()
        h.ds(0x831D, 0, 2)
        h.ds(0x831B, 0, 2)
        h.ds(0x8321, 4, 2)
        h.ds(0x831F, 0x80, 2)
        h.ds(0x8319, 0x2D)
        self.assertEqual(self.result(h), 0)
        self.assertEqual((h.ds(0x831B, size=2), h.ds(0x8321, size=2), h.ds(0x831F, size=2)), (0, 3, 0x80))

    def test_the_target_reached_ends_the_half_with_the_whistle(self):
        h = self.harness()
        h.ds(0x831D, 0, 2)
        h.ds(0x831B, 1, 2)
        h.ds(0x8321, 0, 2)
        h.ds(0x8319, 0)
        h.ds(0x8300, 9, 2)
        self.assertEqual(self.result(h), 1)
        self.assertEqual(h.calls, [("0791:054C", (0, 3)), ("0791:2B0F", (0x40,)), ("0791:0441", (3,)),
                                   ("0791:0425", (4,)), ("0791:0441", (6,))])
        self.assertEqual((h.ds(0x8300, size=2), h.ds(0x8326)), (0, 0))

    def test_the_second_counter_empty_ends_the_half_with_the_other_note(self):
        h = self.harness()
        h.ds(0x831D, 0, 2)
        h.ds(0x831B, 0, 2)
        h.ds(0x8321, 0, 2)
        h.ds(0x8319, 5)
        self.assertEqual(self.result(h), 1)
        self.assertEqual(h.calls[1], ("0791:2B0F", (0x3F,)))
        self.assertEqual(h.ds(0x8326), 1)

    def test_a_negative_target_is_never_reached(self):
        h = self.harness()
        h.ds(0x831D, 0, 2)
        h.ds(0x831B, 0x80, 2)
        h.ds(0x8321, 4, 2)
        h.ds(0x8319, 0xFF)
        self.assertEqual(self.result(h), 0)

    def test_the_falsifier_clock_reload_reloads_0x23(self):
        h = self.harness("clock-reload")
        h.ds(0x831D, 0, 2)
        h.ds(0x831B, 3, 2)
        h.ds(0x8319, 0x2D)
        self.assertEqual(self.result(h), 0)
        self.assertEqual(h.ds(0x831D, size=2), 0x23)


def wrap_add(h, replay, words):
    """The effect of 214B:1C86 on the memory (the stub only returns): *ptr := *ptr + 1, wrapped into 1..200."""
    if replay:
        return
    seg, off = words[0], words[1]
    lin = seg * 16 + off
    value = int.from_bytes(h.m.read(lin, 2), "little")
    h.m.write(lin, (value + 1 if value + 1 <= 200 else 1).to_bytes(2, "little"))


@unittest.skipIf(Machine is None, "unicorn not installed")
class SweepTests(unittest.TestCase):
    """9564 (watched_match_engine), the parts the families do not reach, and its slot loop."""

    def harness(self, **kw):
        return Harness(addresses("9564"), start="0791:9564", **kw)

    def test_play_off_sweeps_the_22_slots_of_the_second_half_only(self):
        h = self.harness(script={"0791:2956": lambda n: n % 2})        # 2956 unavailable: odd calls say yes
        for slot in range(1, 23):
            h.ds(0x883 + slot, 23 - slot)                  # the pitch slot of sweep position `slot`
        h.ds(0x830B, 20)                                   # position 3's slot
        h.ds(0x832A, 0x50, 2)
        h.run()
        expected = []
        for slot in range(1, 23):
            rec = 0x80E8 + 0x16 * (23 - slot)
            expected.append(("0791:2956", (h.m.DS, rec)))
            if slot % 2 == 0:                              # the 2nd, 4th ... call said available (0)
                expected.append(("0791:8AE9", (h.m.DS, rec)))
            if 23 - slot == 20:
                expected.append(("0791:2FB1", ()))
            expected += [("0791:94E8", ()), ("0791:8F10", (h.m.DS, 0x82F6)), ("0791:9372", ())]
        self.assertEqual(h.calls, expected)
        self.assertEqual(h.ds(0x832A, size=2), 0x4E)       # the end of the sweep counts the pause down by 2

    def test_the_pause_counter_stays_at_zero(self):
        h = self.harness()
        h.run()
        self.assertEqual(h.ds(0x832A, size=2), 0)

    def test_the_quick_flag_set_by_the_poll_ends_the_sweep_at_once(self):
        h = self.harness()
        h.ds(0x832A, 0x50, 2)
        h.m.at("0791:9372", lambda replay: replay or (h.counts["0791:9372"] == 3 and h.ds(0x9A3E, 1)))
        h.run()
        self.assertEqual(h.names().count("9372"), 3)
        self.assertEqual(h.ds(0x832A, size=2), 0x50)

    def play_on(self, **kw):
        h = self.harness(**kw)
        h.ds(0x8302, 1)
        h.ds(0x82F7, 3)                                    # the ball is in play
        h.ds(0x7921, 5)                                    # DS:7920 + 1: the direction a ball ahead is attacking
        h.ds(0x0669, 11)                                   # DS:0668 + 1: the second side's first slot
        h.ds(0x82F6, 7)
        h.ds(0x81F0, 7)                                    # the holder's record (slot 12): x equals the ball's
        h.ds(0x884, 3)                                     # slot 1's pitch slot (not DS:830B = 0 -> 2FB1)
        h.script["0791:2BE5"] = [5]                        # the direction 2BE5 says: the possession counter's k
        h.script["0791:2996"] = [0]                        # AL 0: the holder is side 1
        h.script["23E4:08DF"] = [1]                        # the key is in the set: ZF clear
        h.script["0791:2E36"] = [1]
        h.script["0791:59B3"] = [1]                        # AL set: no 6188 loop
        h.ds(0x830B, 9)
        h.m.at("0791:9372", lambda replay: replay or h.ds(0x9A3E, 1))
        return h

    def test_a_ball_in_play_goes_through_the_holders_step(self):
        h = self.play_on()
        h.run()
        ds = h.m.DS
        self.assertEqual(h.calls, [
            ("0791:2BE5", (ds, 0x80FE)), ("0791:83A2", (ds, 0x82F6)), ("0791:2FB1", ()), ("0791:2996", ()),
            ("23E4:08DF", (0x100, 0x791, 0x9544)),         # DS:8327 (0) in the set at 0791:9544; AH from the mul of 960C-9618
            ("0791:2CEC", (ds, 0x81F0)), ("0791:2E36", (0x0307, ds, 0x81F0)), ("0791:8AE9", (ds, 0x81F0)),
            ("0791:59B3", ()),
            ("0791:2956", (ds, 0x80E8 + 0x16 * 3)), ("0791:8AE9", (ds, 0x80E8 + 0x16 * 3)),
            ("0791:94E8", ()), ("0791:8F10", (ds, 0x82F6)), ("0791:9372", ())])
        self.assertEqual((h.ds(0x80F6 + 2, size=2), h.ds(0x80F6, size=2)), (1, 0))   # direction 5 = 7920 + 1: the same

    def test_the_falsifier_possession_swapped_counts_the_other_side(self):
        h = self.play_on(variant="possession-swapped")
        h.run()
        self.assertEqual((h.ds(0x80F6 + 2, size=2), h.ds(0x80F6, size=2)), (0, 1))

    def test_set_on_the_second_gate_and_no_ball_only_the_holder_and_the_sweep_remain(self):
        h = self.play_on()
        h.ds(0x82F7, 0)                                    # no ball in play: 2BE5 and the counter are skipped
        h.ds(0x8303, 1)                                    # the gate's set is asked first, with the slot
        h.script["23E4:08DF"] = [0, 1]                     # the first (the gate): ZF set -> index 1; the second: in set
        h.ds(0x899 + 0x16 + 1, 0)
        h.run()
        self.assertEqual(h.calls[0], ("23E4:08DF", (0, 0x791, 0x9544)))      # the gate asks DS:8327 first; slot 1 stays pushed under it
        self.assertEqual(h.names()[1], "83A2")

    def test_a_slot_over_the_gate_is_skipped_to_its_own_player(self):
        h = self.play_on()
        h.ds(0x899 + 1, 9)                                 # the gate's table for slot 1 says 9 > DS:8300 (0)
        h.run()
        self.assertEqual(h.names(), ["2956", "8AE9", "94E8", "8F10", "9372"])

    def test_the_holder_not_in_play_set_skips_the_update_and_a_zero_59b3_runs_6188_for_the_22_slots(self):
        h = self.play_on()
        h.script["23E4:08DF"] = [0]                        # ZF set: not in the set -> straight to 59B3
        h.script["0791:59B3"] = [0]
        h.run()
        self.assertEqual(h.names()[:5], ["2BE5", "83A2", "2FB1", "2996", "08DF"])
        self.assertEqual(h.names()[5:5 + 23], ["59B3"] + ["6188"] * 22)
        self.assertEqual([c[1][1] for c in h.calls if c[0] == "0791:6188"], [0x80E8 + 0x16 * k for k in range(1, 23)])


@unittest.skipIf(Machine is None, "unicorn not installed")
class HalfTests(unittest.TestCase):
    """983F, 98C4, 9955, 998C, 9A32 with their callees stubbed."""

    def test_a_half_runs_the_ticks_and_takes_the_sprites_off(self):
        h = Harness(addresses("983F"), start="0791:983F")
        for off in (0x9B41, 0x830E, 0x0C20, 0x7C37, 0x8325):
            h.ds(off, 7)
        h.ds(0x9B55, 0)
        h.run()
        ds = h.m.DS
        self.assertEqual(h.calls, [
            ("0791:8062", ()), ("0791:2A15", ()), ("0791:2929", (1,)), ("0791:8CCA", ()), ("0791:97D0", (0,)),
            ("0791:9079", (ds, 0x82E2)), ("0791:9079", (ds, 0x82E8)), ("0791:9079", (ds, 0x82EE)),
            ("214B:1E8D", ())])
        # 9B41, 830E, 8302, 0C20, 7C37 and 8325 end 0; 9B55 is 1 (the stub of 97D0 does not clear it)
        self.assertEqual([h.ds(o) for o in (0x9B41, 0x830E, 0x8302, 0x0C20, 0x7C37, 0x8325, 0x9B55)], [0, 0, 0, 0, 0, 0, 1])

    def test_a_quick_half_only_checks_substitutions_and_runs_the_loop(self):
        h = Harness(addresses("983F"), start="0791:983F")
        h.ds(0x9A3E, 1)
        h.run()
        self.assertEqual(h.names(), ["8062", "2A15", "97D0", "1E8D"])

    def test_the_kickoff_sweeps_until_the_players_are_in_place(self):
        script = {"214B:06B1": [4], "0791:28B2": [0, 0, 1], "0791:2B51": lambda n: 1 if n in (3, 4) else 0}
        h = Harness(addresses("98C4"), start="0791:98C4", script=script)
        h.ds(0x9B3D, 2)                                    # the second side has more goals: the table's second entry
        h.ds(0x0669, 11)
        h.ds(0x0668, 0)
        h.run()
        ds = h.m.DS
        self.assertEqual(h.calls[:2], [("214B:06B1", (0xA,)), ("0791:6BF1", (11 + 5, 3))])      # rand 4 + 1; slot base 11
        self.assertEqual(h.names()[2:2 + 22], ["2B51"] * 22)
        self.assertEqual([c[1] for c in h.calls[2:24]], [(ds, 0x80E8 + 0x16 * k) for k in range(1, 23)])
        self.assertEqual(h.names()[24:], ["6337", "9564", "28B2", "9564", "28B2", "9564", "28B2", "1E8D"])
        self.assertEqual([c[1][0] & 0xFF for c in h.calls if c[0] == "0791:28B2"], [1] * 3)    # the AL; AH is what 98C4 left
        states = [h.ds(0x80E8 + 0x16 * k + 0x12) for k in range(1, 23)]
        self.assertEqual(states, [6 if k in (3, 4) else 0 for k in range(1, 23)])     # 2B51 true: state := 6
        self.assertEqual(h.ds(0x8325), 1)

    def test_the_kickoff_with_the_quick_flag_does_not_sweep(self):
        h = Harness(addresses("98C4"), start="0791:98C4")
        h.ds(0x9A3E, 1)
        h.run()
        self.assertEqual(h.names().count("9564"), 0)
        self.assertEqual(h.names()[-2:], ["6337", "1E8D"])

    def test_the_closing_sweeps_run_until_28b2_says_4(self):
        h = Harness(addresses("9955"), start="0791:9955", script={"0791:28B2": [0, 1]})
        h.ds(0x8325, 1)
        h.ds(0x8302, 1)
        h.run()
        self.assertEqual(h.calls, [("0791:2929", (3,)), ("0791:9564", ()), ("0791:28B2", (4,)), ("0791:9564", ()),
                                   ("0791:28B2", (4,)), ("214B:1E8D", ())])
        self.assertEqual((h.ds(0x8325), h.ds(0x8302)), (0, 0))

    def test_the_closing_with_the_quick_flag_does_nothing_but_clear_the_flags(self):
        h = Harness(addresses("9955"), start="0791:9955")
        h.ds(0x9A3E, 1)
        h.run()
        self.assertEqual(h.names(), ["1E8D"])

    def test_the_halfs_setup_leaves_the_first_word_on_the_stack_for_the_commentary(self):
        script = {"0791:2996": [1, 1, 0], "0791:6B65": [9]}
        h = Harness(addresses("998C"), start="0791:998C", script=script)
        h.ds(0x831A, 1)                                    # the kick-off side
        h.ds(0x0669, 11)
        h.ds(0x9B3C, 0x0302, 2)
        h.run()                                            # (run() checks SP and BP are as the driver left them)
        self.assertEqual(h.names(), ["2996", "2996", "2996", "6B65", "1EB5", "983F"])
        self.assertEqual(h.calls[3][1], (0, 1))            # 6B65(the second 2996's AX, 1)
        self.assertEqual(h.calls[4][1], (1, 9, 0, 0x3B))   # 1EB5 pops four words: the first 2996's AX, 6B65's AX, 0, 0x3B
        self.assertEqual((h.ds(0x831B, size=2), h.ds(0x8319), h.ds(0x830B), h.ds(0x832C, size=2)), (0x5B, 0x2D, 21, 0x0302))

    def half_time(self, **kw):
        h = Harness(addresses("9A32"), start="0791:9A32", **kw)
        players, base = 0x3000, 0x0400
        h.ds(0xA91B, base, 2)
        h.ds(0xA91D, players, 2)
        for j in range(1, 23):
            h.ds(0x80E8 + 0x16 * j + 0xD, j, 2)
            h.m.write(players * 16 + base + 0x14 * j + 0xE, bytes([10]))
        h.ds(0xA96A, 0x0000, 2)
        h.ds(0xA96C, 0xB800, 2)
        h.ds(0xA972, 0x1000, 2)
        h.ds(0xA974, 0x2900, 2)
        h.ds(0x0669, 11)
        h.energy = lambda: [h.m.read(players * 16 + base + 0x14 * j + 0xE, 1)[0] for j in range(1, 23)]
        return h

    def test_half_time_recovers_the_tired_and_shows_the_menu_for_a_key(self):
        h = self.half_time(script={"23E4:08DF": lambda n: 1 if (n <= 22 and n % 2) or n == 23 else 0})
        h.ds(0x831A, 0)
        h.run()
        self.assertEqual(h.names(), ["08DF"] * 22 + ["025D", "0106", "025D", "08DF", "ED8A", "983F"])
        self.assertEqual(h.energy(), [12 if j % 2 else 10 for j in range(1, 23)])
        # AH of the words pushed from AL is what the listing left: 0x0F from `mov ax, 0xfa0` (9AA1)
        self.assertEqual(h.calls[22:], [("23E4:025D", (0xB800, 0x0000, 0x2900, 0x1000, 0xFA0)), ("0791:0106", (0x0F01,)),
                                        ("23E4:025D", (0x2900, 0x1000, 0xB800, 0x0000, 0xFA0)),
                                        ("23E4:08DF", (0x0F00, 0x791, 0x9A12)), ("0791:ED8A", (0x0F00,)),
                                        ("0791:983F", ())])
        self.assertEqual((h.ds(0x9B41), h.ds(0x830B), h.ds(0x832A, size=2)), (1, 21, 0x50))

    def test_half_time_with_the_manager_present_shows_the_menu_without_asking_the_key(self):
        h = self.half_time()
        h.ds(0x80FD, 1)
        h.ds(0x0668, 0)
        h.ds(0x831A, 1)
        h.run()
        self.assertEqual(h.names()[-5:], ["025D", "0106", "025D", "ED8A", "983F"])
        self.assertEqual(h.ds(0x830B), 10)                 # the side to kick off is the other: its first slot (0) + 10

    def test_half_time_without_the_menu_goes_straight_on(self):
        h = self.half_time()
        h.run()
        self.assertEqual(h.names()[-4:], ["0106", "025D", "08DF", "983F"])


@unittest.skipIf(Machine is None, "unicorn not installed")
class PlayMatchTests(unittest.TestCase):
    PARENT, RECORD = 0x0200, 0x0300                        # run_match's BP; the result record's offset in DS

    def harness(self):
        h = Harness(addresses("F098"), args=(self.PARENT,), start="0791:F098")
        h.m.write(SS * 16 + self.PARENT + 6, self.RECORD.to_bytes(2, "little") + h.m.DS.to_bytes(2, "little"))
        return h

    def record(self, h):
        return [h.ds(self.RECORD + k) for k in range(4)]

    def test_a_win_for_the_first_side_sets_the_winner_byte_0(self):
        h = self.harness()
        h.ds(0x9B3C, 0x0102, 2)                            # team 0: 2 goals, team 1: 1
        h.run()
        self.assertEqual(self.record(h), [2, 1, 0, 0])
        self.assertEqual(h.names(), ["998C", "9955", "9A32", "98C4", "9955"])

    def test_a_win_for_the_second_side_sets_1_and_a_draw_sets_2(self):
        h = self.harness()
        h.ds(0x9B3C, 0x0201, 2)
        h.run()
        self.assertEqual(self.record(h)[3], 1)
        h = self.harness()
        h.ds(0x9B3C, 0x0101, 2)
        h.run()
        self.assertEqual(self.record(h), [1, 1, 0, 2])
        self.assertEqual(h.names(), ["998C", "9955", "9A32", "9955"])           # level: no 98C4

    def test_a_level_decider_plays_extra_time_and_the_shootout(self):
        h = self.harness()
        h.ds(0x7C36, 1)
        h.ds(0x9B3C, 0x0101, 2)
        h.ds(0x8323, 5)
        h.m.at("0791:9B5B", lambda replay: replay or h.ds(0x9B3C, 0x0202, 2))       # extra time: still level
        h.m.at("0791:A10A", lambda replay: replay or h.ds(0x9B3C, 0x0503, 2))       # the shoot-out: team 1 wins it
        h.run()
        self.assertEqual(h.names(), ["998C", "9955", "9A32", "9B0C", "9B5B", "A10A", "98C4", "9955"])
        self.assertEqual(self.record(h), [2, 2, 0, 1])      # the record keeps the score before the shoot-out; the winner byte is 1
        self.assertEqual(h.ds(0x8323), 0)

    def test_extra_time_decided_skips_the_shootout(self):
        h = self.harness()
        h.ds(0x7C36, 1)
        h.ds(0x9B3C, 0x0101, 2)
        h.m.at("0791:9B5B", lambda replay: replay or h.ds(0x9B3C, 0x0102, 2))
        h.run()
        self.assertEqual(h.names(), ["998C", "9955", "9A32", "9B0C", "9B5B", "98C4", "9955"])
        self.assertEqual(self.record(h), [2, 1, 0, 0])

    def test_not_a_decider_is_not_played_on_even_when_level(self):
        h = self.harness()
        h.ds(0x9B3C, 0x0101, 2)
        h.run()
        self.assertNotIn("9B0C", h.names())

    def test_the_quick_flag_after_the_half_skips_the_closing(self):
        h = self.harness()
        h.ds(0x9B3C, 0x0102, 2)
        h.m.at("0791:9A32", lambda replay: replay or h.ds(0x9A3E, 1))
        h.run()
        self.assertEqual(h.names(), ["998C", "9955", "9A32"])


if __name__ == "__main__":
    unittest.main()
