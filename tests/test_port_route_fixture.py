"""T121: the fixture router and its news/watch helpers, pinned to the listing."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port

class Registry(unittest.TestCase):
    def test_the_ten_routines_and_their_returns(self):
        reg = port._module_registry("route")
        self.assertEqual({a: e.ret for a, e in reg.entries.items()}, {
            "000E:6CA7": "ret", "000E:6C21": "ret 4", "0791:E80D": "retf 4",
            "000E:6685": "ret 4", "000E:038E": "ret", "000E:05F6": "ret 6",
            "000E:062F": "ret 0xc", "000E:070B": "ret 6", "000E:075F": "ret 0xc",
            "000E:5978": "ret 4"})

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_port_silent import Rig as SilentRig, responder, GAME, FIXTURES_SEG, FIXTURES_OFF
from test_port_update import Case


class Rig(SilentRig):
    def run(self, address, words=(), answer=None, variant=None):
        entry = port._module_registry("route").entries[address]
        for i, value in enumerate([0x5678] + ([0x9ABC] if entry.far else []) + list(words)):
            self.lin16(0x3000 + i * 2, value)
        self.mem._entries.append((0x3000, entry.far))
        try:
            gen, sent = entry.fn(self.mem, variant), None
            while True:
                try:
                    request = gen.send(sent)
                except StopIteration as stop:
                    return stop.value
                self.calls.append((request.target, request.args, request.ret_to, request.far))
                if len(self.calls) > 5000:
                    raise AssertionError("port did not return")
                sent = answer(request, self.mem) if answer else 0
                self.mem.regs["ax"] = sent & 0xFFFF
        finally:
            self.mem._entries.pop()


class Routing(Case):
    def rig(self, kind=2, first_byte=0xFE, managed=(3,)):
        r = Rig()
        r.lin16(GAME + 0x26, 1)
        r.lin16(GAME + 0x28, 2)
        base = FIXTURES_SEG * 16 + FIXTURES_OFF
        r.mem.memory[base:base + 8] = bytes([first_byte, 0, kind, 0, 3, 0, 4, 0])
        for country in (3, 4):
            r.country(country, 0x2C, 1)
            r.country(country, 0x2E, country + (0x80 if country in managed else 0))
        return r

    def answer(self, r, managed=(3,), watch=0, sets=()):
        def answer(request, mem):
            if request.target == "1771:0B77":
                return int(request.args[0] in managed)
            if request.target == "000E:6C21":
                return 1 if request.args[0] & 255 == 0 else watch
            if request.target == "23E4:08DF":
                mem.regs["eflags"] = 0 if request.args[-1] in sets else 0x40
            if request.target == "000E:6970":
                parent = request.args[0]
                r.lin8(parent - 2, 1)
                r.lin16(GAME + 0x26, r.u16(GAME + 0x26) + 1)
            return 0
        return answer

    def test_managed_competitive_confidence_includes_the_unmanaged_side(self):
        r = self.rig()
        r.run("000E:6CA7", answer=self.answer(r))
        self.assertEqual([a[0] for a in r.args("0791:B6CC")], [0x83, 4])
        self.assertEqual([a[-1] & 255 for a in r.args("0791:B71C")], [0, 1])
        self.assertEqual(len(r.args("000E:4E0E")), 1)
        self.assertEqual(r.u16(GAME + 0x26), 2)
        self.assertEqual(r.targets()[-2:], [("0791:B7FA", "000E:6FFD"), ("1771:8757", "000E:7009")])

    def test_friendly_and_unplayed_have_no_confidence_and_unplayed_has_no_news(self):
        for kind in (0, 1):
            r = self.rig(kind=kind)
            r.run("000E:6CA7", answer=self.answer(r))
            self.assertEqual(r.args("0791:B71C"), [])
            self.assertEqual(r.args("0791:B6CC"), [])
            self.assertEqual(len(r.args("0791:BB2F")), int(kind == 0))
            self.assertEqual(len(r.args("0791:F1F6")), int(kind != 0))
            self.assertEqual(len(r.args("000E:4E0E")), int(kind != 0))

    def test_kinds_3_and_7_mark_only_managed_sides(self):
        for kind in (3, 7):
            r = self.rig(kind=kind)
            r.lin8(GAME + 0x41 + 3, 9)
            r.run("000E:6CA7", answer=self.answer(r, sets=(0x6C87,)))
            self.assertEqual(r.mem.memory[GAME + 0x13 + 3], 1)
            self.assertEqual(r.mem.memory[GAME + 0x41 + 3], 0)
            self.assertEqual(r.mem.memory[GAME + 0x13 + 4], 0)

    def test_silent_loop_sets_up_the_real_parent_frame(self):
        r = self.rig(first_byte=0xFF, managed=())
        r.run("000E:6CA7", answer=self.answer(r, managed=()))
        self.assertEqual(r.args("000E:6970"), [(0x2FFE,)])
        self.assertEqual(r.u16(0x2FFE - 6), 1)
        self.assertEqual(r.mem.memory[0x2FFE - 2], 1)
        self.assertEqual(r.args("0791:F1F6"), [])
        self.assertEqual(r.targets()[-1], ("1771:8757", "000E:706E"))

    def test_gate_flag_is_zero_for_managed_fe_and_one_for_unmanaged_fe(self):
        for managed, flag in (((3,), 0), ((), 1)):
            r = self.rig(managed=managed)
            r.run("000E:6CA7", answer=self.answer(r, managed=managed))
            self.assertEqual(r.args("000E:6C21")[0][0] & 255, flag)

    def test_final_news_follows_silent_kind_cb(self):
        r = self.rig(kind=0xCB, first_byte=0xFF, managed=())
        r.run("000E:6CA7", answer=self.answer(r, managed=()))
        self.assertEqual(r.args("000E:6685"), [(FIXTURES_SEG, FIXTURES_OFF)])
        self.assertEqual(r.targets()[-2:], [("000E:6685", "000E:7066"), ("1771:8757", "000E:706E")])


class Gate(Case):
    def test_prior_silent_results_are_shown_before_the_flag_is_tested(self):
        r = Rig()
        parent = 0x3200
        r.lin8(parent - 2, 1)
        self.assertEqual(r.run("000E:6C21", [parent, 0]), 1)
        self.assertEqual(r.targets(), [("214B:0329", "000E:6C4A"), ("214B:08DD", "000E:6C4F")])
        self.assertEqual(r.args("214B:0329"), [(r.mem.DS, 0x14A6, r.mem.DS, 0xA96A)])

    def test_watch_answer_is_returned_and_zero_flag_bypasses_it(self):
        for flag, answer in ((1, 0), (1, 1), (0, 0)):
            r = Rig()
            r.lin16(GAME + 0x26, 1)
            value = r.run("000E:6C21", [0x3200, flag], responder({"0791:E80D": answer}))
            self.assertEqual(value & 255, answer if flag else 1)
            self.assertEqual(len(r.args("0791:E80D")), flag)


class News(Case):
    def test_background_unpack_order(self):
        r = Rig()
        r.run("000E:038E")
        self.assertEqual([a[1] for a in r.args("214B:0329")], [0x4ED8, 0x5796, 0x14A6])

    def test_wait_has_no_celebration_without_a_flag(self):
        for flags in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)):
            r = Rig()
            r.run("000E:05F6", flags)
            self.assertEqual(r.targets()[0], ("23E4:025D", "000E:060E"))
            self.assertEqual(r.targets()[-1], ("214B:08DD", "000E:0629"))
            self.assertEqual(len(r.args("000E:0572")), int(any(flags)))

    def test_competition_news_always_draws_twice_in_order(self):
        for choice in (1, 2, 3):
            r = Rig()
            # Empty table disables only the optional heading, not either draw.
            r.ds16(0xA93F, 0x8000)
            r.ds16(0xA941, 0)
            r.country(4, 0x2C, 1)
            r.run("000E:6685", [FIXTURES_OFF, FIXTURES_SEG],
                  responder({"1771:5C94": 3, "1771:5CCB": 4, "214B:06B1": [2, choice]}))
            self.assertEqual(r.args("214B:06B1"), [(3,), (3,)])
            self.assertEqual([c[2] for c in r.calls_of("214B:06B1")], ["000E:67EC", "000E:680E"])
            self.assertEqual(len(r.args("000E:075F")), 1)
            self.assertEqual(r.targets()[-1], ("000E:05F6", "000E:6863"))
