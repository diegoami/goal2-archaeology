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


if __name__ == "__main__":
    unittest.main()
