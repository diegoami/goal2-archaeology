"""Synthetic branches of the T63 listing port, using a guest-call model.

The expected depth table addresses and branch conditions here come from
seg_0791_07.asm and seg_0791_08.asm. Whole matches validate the real guest.
"""
import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match.port.mem import PlainMem
from original_match.port.positioning import PORTS


class Sim:
    def __init__(self, variant=None):
        self.mem = PlainMem(bytearray(0x110000))
        self.mem.regs.update(ss=0x6000, sp=0x3f00, bp=0x3e00, cs=self.mem.seg(0x0791), ax=0, dx=0)
        self.variant = variant
        self.calls = []
        self.answers = {}
        self.ptr(0xA91B, 0, 0x4000)
        self.ptr(0xA917, 0, 0x5000)
        self.byte(0x07BA, bytes([3, 2, 2, 1]))
        self.byte(0x07CB, bytes(range(10, 26)))
        self.byte(0x07DB, bytes(range(30, 38)))
        self.word(0x3e00 + 6, 0, seg=0x6000)
        self.word(0x3e00 + 8, 0x7000, seg=0x6000)
        self.rec = 0x7000 * 16
        self.record(6, 2)
        self.record(0xd, 0)
        self.mem.memory[0x4000 * 16 + 6] = 6

    def byte(self, off, value, seg=None):
        if isinstance(value, int):
            value = bytes([value & 0xff])
        start = (self.mem.DS if seg is None else seg) * 16 + off
        self.mem.memory[start:start + len(value)] = value

    def word(self, off, value, seg=None):
        self.byte(off, (value & 0xffff).to_bytes(2, "little"), seg)

    def ptr(self, off, ptr_off, ptr_seg):
        self.word(off, ptr_off)
        self.word(off + 2, ptr_seg)

    def record(self, off, value):
        self.mem.memory[self.rec + off] = value & 0xff

    def run(self, address, *args):
        entry = PORTS.entries[address]
        mem = self.mem
        sp0, bp0 = mem.reg("sp"), mem.reg("bp")
        sp = sp0
        for value in list(args) + ([mem.seg(0x0791)] if entry.far else []) + [0xfffe]:
            sp -= 2
            mem.w16(mem.ss_lin(sp), value, "0791:0000")
        mem.set_reg("sp", sp)
        mem._entries.append((sp, entry.far))
        try:
            result = entry.fn(mem, self.variant)
            if inspect.isgenerator(result):
                result = self.drive(result)
            if result is not None:
                mem.set_reg("ax", result)
            return mem.reg("ax")
        finally:
            mem._entries.pop()
            mem.set_reg("sp", sp0)
            mem.set_reg("bp", bp0)

    def drive(self, gen):
        answer = None
        while True:
            try:
                request = gen.send(answer)
            except StopIteration as stopped:
                return stopped.value
            self.calls.append((request.target, request.args, request.ret_to))
            source = self.answers[request.target]
            answer = source(request) if callable(source) else source
            self.mem.set_reg("ax", answer)


class PositioningTests(unittest.TestCase):
    def test_position_group_keeper_and_tactic_rows(self):
        sim = Sim()
        sim.answers.update({"0791:26D7": 0, "0791:2B51": 0})
        for position, tactic, own, expected in (
            (0, 0, 0, 4), (3, 0, 0, 3), (3, 1, 1, 2),
            (6, 0, 0, 2), (6, 1, 1, 1), (13, 0, 0, 1),
        ):
            with self.subTest(position=position, tactic=tactic, own=own):
                sim.mem.memory[0x4000 * 16 + 6] = position
                sim.answers["0791:26D7"] = tactic
                sim.answers["0791:2B51"] = own
                self.assertEqual(sim.run("0791:42CB", 0x7000, 0), expected)

    def test_attack_reads_every_depth_table_row(self):
        for tactic in range(2):
            for group in range(1, 5):
                index = tactic * 4 + group
                sim = Sim()
                sim.answers.update({"0791:42CB": group, "0791:26D7": lambda c: tactic if c.args[0] == 7 else 1,
                                    "0791:2D10": 1, "214B:06FA": 1})
                sim.record(0xc, 30 + index - 1)
                self.assertEqual(sim.run("0791:4532", 0x3e00) & 0xff, int(group < 4), index)
                sim.record(0xc, 30 + index)
                self.assertEqual(sim.run("0791:4532", 0x3e00) & 0xff, 0, index)

    def test_defend_reads_every_depth_table_row(self):
        for t5 in range(2):
            for t6 in range(2):
                for group in range(1, 5):
                    index = 8 * t5 + 4 * t6 + group
                    sim = Sim()
                    sim.answers.update({"0791:42CB": group,
                                        "0791:26D7": lambda c: t5 if c.args[0] == 5 else t6,
                                        "0791:2D6D": 1, "0791:2D10": 0})
                    sim.record(0xc, 10 + index + 1)
                    self.assertEqual(sim.run("0791:4649", 0x3e00) & 0xff, int(group < 4), index)
                    sim.record(0xc, 10 + index)
                    self.assertEqual(sim.run("0791:4649", 0x3e00) & 0xff, 0, index)

    def test_sweeper_uses_fifteen_cell_draw_outside_state_nine(self):
        sim = Sim()
        sim.mem.memory[0x4000 * 16 + 6] = 13
        sim.record(0x12, 8)
        sim.record(0xc, 2)
        sim.answers.update({"214B:06B1": 15, "0791:2C86": lambda c: c.args[0]})
        sim.run("0791:4354", 0x7000, 0)
        self.assertIn(("214B:06B1", (15,), "0791:43A7"), sim.calls)
        self.assertEqual(sim.mem.u8(sim.rec + 0xb), 7)

    def test_empty_marking_slot_is_cleared_without_candidate(self):
        sim = Sim()
        sim.byte(0x0668, bytes([0, 11]))
        sim.word(0x9B34, 0)
        sim.word(0x9A3E + 0x28 + 2 * (2 - 11), 0)
        sim.answers.update({"0791:2996": 1, "1771:3216": 1})
        self.assertEqual(sim.run("0791:47C5", 0x3e00) & 0xff, 0)
        self.assertFalse(any(c[0] == "0791:4438" for c in sim.calls))

    def test_keeper_outside_goal_strip_does_not_draw(self):
        sim = Sim()
        sim.record(6, 1)
        sim.answers.update({"0791:045D": 1, "0791:2EB8": 0})
        sim.run("0791:4D3F", 0x7000, 0)
        self.assertEqual([c[0] for c in sim.calls], ["0791:045D", "0791:2EB8"])
        self.assertEqual(sim.mem.u8(sim.rec + 0x12), 0)

    def test_all_unavailable_leader_returns_prior_local_word(self):
        sim = Sim()
        sim.word(0x9B34, 0)
        sim.word(0x3ef4, 0xbeef, seg=0x6000)  # BP-6 after the near call and 1F3C's push BP
        sim.answers["1771:3216"] = 1
        self.assertEqual(sim.run("0791:1F3C", 0), 0xbeef)
        self.assertEqual(sum(c[0] == "1771:3216" for c in sim.calls), 11)

    def test_start_posts_reads_prior_side_local_before_initializing_it(self):
        sim = Sim()
        sim.byte(0x0668, bytes([0, 11]))
        sim.byte(0x3efb, 1, seg=0x6000)  # BP-1 after the near call and push BP
        seen = []
        original_read = sim.mem.read

        def read(linear, n):
            if linear in (sim.mem.DS * 16 + 0x0668, sim.mem.DS * 16 + 0x0669):
                seen.append(linear - sim.mem.DS * 16)
            return original_read(linear, n)

        sim.mem.read = read
        sim.run("0791:419C")
        self.assertEqual(seen[0], 0x0669)

    def test_squad_swap_keeps_three_guest_copy_boundaries(self):
        sim = Sim()
        sim.byte(0x3dff, 0, seg=0x6000)
        sim.word(0x3dfb, 2, seg=0x6000)
        sim.word(0x3dfd, 3, seg=0x6000)
        sim.word(0x9B34, 0)
        sim.answers["214B:007B"] = 0
        sim.run("0791:2218", 0x3e00)
        calls = [c for c in sim.calls if c[0] == "214B:007B"]
        self.assertEqual([c[1][-1] for c in calls], [2, 1, 2])
        self.assertEqual([c[2] for c in calls], ["0791:2270", "0791:22B9", "0791:2306"])


if __name__ == "__main__":
    unittest.main()
