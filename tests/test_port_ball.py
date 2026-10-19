"""T64 listing-derived synthetic cases; no original game bytes."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port
from original_match.port.mem import PlainMem


class Rig:
    def __init__(self):
        self.mem = PlainMem(bytearray(0x60000))
        self.mem.regs.update(ss=0, sp=0x3000, bp=0x1234, ds=self.mem.DS, eflags=0x202)
        self.calls = []
        self.w8(0x668, 11)
        self.w8(0x669, 0)
        for slot in range(2, 23):
            self.record(slot, 20, 30, state=13)

    def w8(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off] = value & 0xFF

    def record(self, slot, x, y, state=0):
        off = 0x80E8 + slot * 0x16
        for k, value in ((0, x), (1, y), (6, slot), (0x12, state)):
            self.w8(off + k, value)

    def run(self, address, words=(), answer=None):
        entry = port._module_registry("ball").entries[address]
        for i, value in enumerate([0x5678] + ([0x9ABC] if entry.far else []) + list(words)):
            self.mem.memory[0x3000 + i * 2:0x3002 + i * 2] = (value & 0xFFFF).to_bytes(2, "little")
        self.mem._entries.append((0x3000, entry.far))
        try:
            gen = entry.fn(self.mem, None)
            if gen is None:
                return self.mem.regs
            sent = None
            while True:
                try:
                    request = gen.send(sent)
                except StopIteration:
                    break
                self.calls.append((request.target, request.args, request.ret_to, request.far))
                sent = answer(request, self.mem) if answer else 0
                self.mem.regs["ax"] = sent & 0xFFFF
        finally:
            self.mem._entries.pop()
        return self.mem.regs


class NearestBall(unittest.TestCase):
    @staticmethod
    def responder(unavailable=()):
        def answer(request, mem):
            seg, off = request.args
            slot = (off - 0x80E8) // 0x16
            if request.target == "0791:2956":
                return int(slot in unavailable)
            if request.target == "0791:2BE5":
                return 0xFF if slot > 11 else 1
            raise AssertionError(request.target)
        return answer

    def test_nearest_keeps_first_tie_and_excludes_holder_unavailable_and_state13(self):
        r = Rig()
        r.w8(0x830B, 4)
        r.record(13, 0, -3)
        r.record(14, 0, 3)
        r.record(15, 0, -1)
        r.record(16, 0, -1, state=13)
        r.record(2, 1, 2)
        r.record(3, 0, 4)
        r.record(4, 0, 2)
        r.run("0791:2FB1", answer=self.responder(unavailable=(15,)))
        self.assertEqual((r.mem.ds8(0x8311), r.mem.ds8(0x8312)), (13, 2))
        self.assertEqual((r.mem.ds8(0x830F), r.mem.ds8(0x8310)), (14, 0))
        unavailable = [c for c in r.calls if c[0] == "0791:2956"]
        self.assertEqual(len(unavailable), 20)
        self.assertTrue(all(c[2:] == ("0791:3013", True) for c in unavailable))
        self.assertEqual([c[1][1] for c in unavailable],
                         [0x80E8 + slot * 0x16 for slot in list(range(13, 23)) + list(range(2, 12))])

    def test_no_candidate_clears_both_nearest_arrays(self):
        r = Rig()
        for off in (0x830F, 0x8310, 0x8311, 0x8312):
            r.w8(off, 0xEE)
        r.run("0791:2FB1", answer=self.responder())
        self.assertEqual([r.mem.ds8(off) for off in (0x830F, 0x8310, 0x8311, 0x8312)], [0, 0, 0, 0])
        self.assertEqual(len(r.calls), 20)

    def test_direction_product_is_a_live_stack_word_during_second_call(self):
        r = Rig()
        r.w8(0x82F7, 2)
        r.record(13, 0, 3)
        fallback = self.responder()
        seen = []
        def answer(request, mem):
            if request.ret_to == "0791:3090":
                self.assertEqual(mem.regs["sp"], 0x2FF0)
            if request.ret_to == "0791:30A3":
                self.assertEqual(request.target, "0791:2BE5")
                self.assertEqual(request.args, (mem.DS, 0x80E8 + 13 * 0x16))
                self.assertTrue(request.far)
                self.assertEqual(mem.regs["sp"], 0x2FEE)
                self.assertEqual(mem.u16(0x2FEE), 0xFFFE)         # signed 2 * -1 at3099
                seen.append(request.ret_to)
            return fallback(request, mem)
        r.run("0791:2FB1", answer=answer)
        self.assertEqual(seen, ["0791:30A3"])
        self.assertEqual(r.mem.ds8(0x830F), 13)


class RelativeSlot(unittest.TestCase):
    def test_side_base_and_relative_word_wrap(self):
        for side, index, expected in ((0, 2, 13), (1, 11, 11), (0, 0xFFFE, 9)):
            r = Rig()
            def answer(request, mem):
                self.assertEqual((request.target, request.args, request.ret_to, request.far),
                                 ("0791:2974", (0x4000, 0x123), "0791:30F9", True))
                return side
            regs = r.run("0791:30EA", [0x123, 0x4000, index], answer)
            self.assertEqual(regs["ax"], expected)
            self.assertEqual(r.mem.u16(0x2FFC), expected)         # local at bp-2


class BallWrappers(unittest.TestCase):
    def test_selected_receiver_preserves_full_ax_as_the_target_word(self):
        r = Rig()
        answers = iter((0xAB12, 0xCD34))
        regs = r.run("0791:3323", [0x123, 0x4000], lambda request, mem: next(answers))
        self.assertEqual(r.calls, [
            ("0791:3111", (0x4000, 0x123), "0791:332F", True),
            ("0791:384C", (0xAB12, 0x4000, 0x123), "0791:3339", True)])
        self.assertEqual(regs["ax"], 0xCD34)

    def test_offside_short_circuits_the_random_draw(self):
        r = Rig()
        r.w8(0x830E, 1)
        r.run("0791:3BEE", [0x123, 0x4000])
        self.assertEqual(r.calls, [("0791:82EB", (), "0791:3BFB", False)])

    def test_pass_and_clearance_keep_coin_branches_and_call_sites(self):
        cases = (("0791:3BEE", 0, "0791:3323", "0791:3C1A", (0x4000, 0x123)),
                 ("0791:3BEE", 1, "0791:3B15", "0791:3C0F", (0x4000, 0x123)),
                 ("0791:408E", 0, "0791:3EF8", "0791:40B6", (11, 0x4000, 0x123)),
                 ("0791:408E", 1, "0791:3FAD", "0791:40A7", (11, 0x4000, 0x123)))
        for address, coin, target, ret, args in cases:
            r = Rig()
            r.run(address, [0x123, 0x4000], lambda request, mem: coin if request.target == "214B:06FA" else 0)
            self.assertEqual(len(r.calls), 2)
            self.assertEqual(r.calls[0], ("214B:06FA", (), "0791:3C02" if address == "0791:3BEE" else "0791:4096", True))
            self.assertEqual(r.calls[1], (target, args, ret, True))

    def test_shot_and_header_template_push_preserves_the_incoming_high_byte(self):
        for address, words, template, event, ret in (
                ("0791:3EC5", [0x123, 0x4000, 0xAA56], 0x9A56, 1, "0791:3ED9"),
                ("0791:3EDF", [0x123, 0x4000], 0x9A14, 2, "0791:3EF2")):
            r = Rig()
            r.mem.regs["ax"] = 0x9ABC
            def answer(request, mem):
                self.assertEqual(mem.regs["ax"], event)
                return 0xDE34
            r.run(address, words, answer)
            self.assertEqual(r.calls, [("0791:3C3F", (template, event, 0x4000, 0x123), ret, True)])
            self.assertEqual(r.mem.regs["ax"], 0xDE34)

    def test_counter_side_stride_byte_wrap_and_match_mode_gate(self):
        for side, off in ((0, 0x7B82), (1, 0x7B8C)):
            r = Rig()
            r.w8(off, 255)
            r.run("0791:3C20", [side])
            self.assertEqual(r.mem.ds8(off), 0)
            self.assertEqual((r.mem.regs["ax"], r.mem.regs["dx"]), (side * 10, 0))
        r = Rig()
        r.w8(0x8326, 1)
        r.w8(0x7B82, 7)
        r.mem.regs.update(ax=0x1234, dx=0x5678)
        r.run("0791:3C20", [0])
        self.assertEqual(r.mem.ds8(0x7B82), 7)
        self.assertEqual((r.mem.regs["ax"], r.mem.regs["dx"]), (0x1234, 0x5678))

    def test_keeper_strip_gate_returns_local_boolean_with_last_callee_high_byte(self):
        for inside, expected in ((0, 0xAB00), (1, 0xCD01)):
            r = Rig()
            r.w8(0x830B, 2)
            r.record(2, -3, 4)
            answers = iter((0xAB00 | inside, 0xCD42))
            r.run("0791:4151", answer=lambda request, mem: next(answers))
            self.assertEqual(r.calls[0], ("0791:2EB8", (0x04FD, r.mem.DS, 0x8114), "0791:4180", True))
            self.assertEqual(len(r.calls), 1 + inside)
            if inside:
                self.assertEqual(r.calls[1], ("0791:3FAD", (9, r.mem.DS, 0x8114), "0791:4191", True))
            self.assertEqual(r.mem.regs["ax"], expected)


class LongTargets(unittest.TestCase):
    def test_long_ball_keeps_floor_and_product_words_live_across_guest_calls(self):
        r = Rig()
        r.w8(0x82F6, 1)
        r.w8(0x82F7, 2)
        r.w8(0x78A, 11)
        r.w8(0x78B, 22)
        def answer(request, mem):
            if request.target == "0791:278A":
                self.assertEqual(request.args, (2, 0x4000, 0x123))
                self.assertEqual(mem.regs["sp"], 0x2FF8)
                self.assertEqual((mem.u16(0x2FF8), mem.u16(0x2FFA)), (30, 0))
                return 108
            if request.target == "214B:06B1":
                self.assertEqual(request.args, (27,))
                self.assertEqual(mem.regs["sp"], 0x2FF8)
                return 25
            if request.target == "214B:0D56":
                self.assertEqual(request.args, (0, 30, 0, 25))
                self.assertEqual(mem.regs["sp"], 0x2FFC)
                mem.regs["dx"] = 0
                return 30
            if request.target == "0791:2BE5":
                self.assertEqual(mem.regs["sp"], 0x2FF8)
                self.assertEqual((mem.u16(0x2FF8), mem.u16(0x2FFA)), (30, 0))
                return 0xFFFF
            if request.target == "23E4:0279":
                self.assertEqual((mem.regs["ax"], mem.regs["dx"], mem.regs["cx"], mem.regs["bx"]),
                                 (0xFFFF, 0xFFFF, 30, 0))
                mem.regs["dx"] = 0xFFFF
                return 0xFFE2                                  # -1 * 30
            if request.target == "0791:34C1":
                self.assertEqual(request.args, (0xE401, 10, 0x4000, 0x123))
                self.assertEqual(mem.ds8(0x830C), 255)
                r.w8(0x830C, 0)
                return 0
            self.assertEqual((request.target, request.args, request.ret_to, request.far),
                             ("0791:2AA3", (22,), "0791:3B93", False))
            return 0xF00D
        r.run("0791:3B15", [0x123, 0x4000], answer)
        self.assertEqual((r.mem.ds8(0x8303), r.mem.ds8(0x830C)), (1, 0))
        self.assertEqual(len(r.calls), 7)

    def test_long_kick_uses_each_parallel_mode_row_and_preserves_commentary_ah(self):
        for event, selector, divisor, floor, chosen, point, template in (
                (11, 4, 4, 30, 10, 0x2001, 0xAB18),
                (9, 2, 5, 40, 9, 0x2A01, 0xAB17)):
            r = Rig()
            for off, value in ((0x82F6, 1), (0x82F7, 2), (0x796, 4), (0x797, 2),
                               (0x798, 4), (0x799, 5), (0x79A, 10), (0x79B, 9), (0x79C, 30), (0x79D, 40)):
                r.w8(off, value)
            def answer(request, mem):
                if request.target == "0791:278A":
                    self.assertEqual(request.args, (selector, 0x4000, 0x123))
                    self.assertEqual(mem.regs["sp"], 0x2FF4)
                    self.assertEqual([mem.u16(0x2FF4 + 2*i) for i in range(3)], [divisor, floor, 0])
                    return 100
                if request.target == "214B:06B1":
                    self.assertEqual(request.args, (100 // divisor,))
                    return 3
                if request.target == "214B:0D56":
                    self.assertEqual(request.args, (0, floor, 0, 3))
                    mem.regs["dx"] = 0
                    return floor
                if request.target == "0791:2BE5":
                    self.assertEqual(mem.regs["sp"], 0x2FF6)
                    self.assertEqual(mem.u16(0x2FF6), floor)
                    return 1
                if request.target == "23E4:0279":
                    self.assertEqual((mem.regs["ax"], mem.regs["cx"], mem.regs["bx"]), (1, floor, 0))
                    mem.regs["dx"] = 0
                    return floor
                if request.target == "0791:34C1":
                    self.assertEqual(request.args, (point, chosen, 0x4000, 0x123))
                    return 0xAB00
                self.assertEqual(request.target, "0791:2AA3")
                self.assertEqual(request.args, (template,))
                return 0
            r.run("0791:3EF8", [0x123, 0x4000, event], answer)
            self.assertEqual(r.mem.ds8(0x8303), 1)

    def test_target_slot_point_stays_on_stack_while_half_is_queried(self):
        for half, event in ((0, 7), (1, 8)):
            r = Rig()
            r.record(2, -3, 4)
            r.w8(0x78C, 7)
            r.w8(0x78D, 8)
            def answer(request, mem):
                if request.target == "0791:2C54":
                    self.assertEqual((mem.regs["sp"], mem.u16(0x2FFC)), (0x2FFC, 0x04FD))
                    return half
                if request.target == "0791:34C1":
                    self.assertEqual(request.args, (0x04FD, event, 0x4000, 0x123))
                    self.assertEqual(mem.regs["sp"], 0x2FFE)
                    return 0xABCD
                if request.target == "0791:2AA3":
                    self.assertEqual(request.args, (0xAB03,))
                    return 0
                if request.target == "214B:06FA":
                    return 1
                self.assertEqual((request.target, request.args), ("0791:4D3F", (0x4000, 0x123)))
                return 0x1234
            r.run("0791:3B9E", [0x123, 0x4000, 2], answer)
            self.assertEqual((r.mem.ds8(0x8303), r.mem.ds8(0x830C)), (1, 2))
            self.assertEqual(r.mem.regs["ax"], 0x1234)


class AdvancedStrip(unittest.TestCase):
    def test_strict_marker_and_strip_thresholds_on_both_sides(self):
        for x, y, marker, own, side, expected in (
                (3, 20, 19, 0, 0, 1), (-3, -20, -19, 0, 1, 1),
                (4, 20, 19, 0, 0, 0), (3, 35, 19, 0, 0, 0),
                (3, 19, 19, 0, 0, 0), (3, 20, 19, 1, 0, 0)):
            r = Rig()
            r.record(2, x, y)
            r.w8(0x830B, 2)
            r.w8(0x82E3 + (6 if side == 0 else 0), marker)
            def answer(request, mem):
                if request.target == "0791:2C54":
                    return own
                self.assertEqual((request.target, request.ret_to, request.far), ("0791:2996", "0791:40E8", False))
                return side
            r.run("0791:40BC", answer=answer)
            self.assertEqual(r.mem.regs["ax"] & 255, expected, (x, y, marker, own, side))
            self.assertEqual(len(r.calls), 1 if own else 2)


class ClearanceTargets(unittest.TestCase):
    def test_narrow_wide_and_keeper_paths_preserve_short_circuit_draw_order(self):
        for coin, keeper, x, y, bound, point in (
                (1, 0, 0, 0, 40, 0xFBF4), (0, 1, 0, 0, 40, 0xFBF4),
                (0, 0, 1, -1, 8, 0xCE07), (0, 0, -1, 1, 8, 0x32F9)):
            r = Rig()
            for k, value in ((0, x), (1, y), (6, 2)):
                r.mem.memory[0x40123 + k] = value & 255
            r.w8(0x7920, 255)
            r.w8(0x7921, 1)
            def answer(request, mem):
                if request.target == "214B:06FA":
                    return coin
                if request.target == "0791:045D":
                    self.assertEqual(request.args, (2,))
                    return keeper
                if request.target == "214B:06B1":
                    self.assertEqual(request.args, (bound,))
                    return 5
                if request.target == "0791:34C1":
                    self.assertEqual(request.args, (point, 11, 0x4000, 0x123))
                    return 0xAB00
                self.assertEqual((request.target, request.args, request.far), ("0791:2AA3", (0xAB16,), False))
                return 0
            r.run("0791:3FAD", [0x123, 0x4000, 11], answer)
            self.assertEqual([c[0] for c in r.calls],
                             ["214B:06FA"] + ([] if coin else ["0791:045D"]) +
                             ["214B:06B1", "0791:34C1", "0791:2AA3"])
            self.assertEqual(r.mem.ds8(0x8303), 1)

    def test_cross_uses_candidate_point_without_target_draws_and_inverts_high_ball_draw(self):
        for candidate, high_draw in ((False, 0), (True, 1)):
            r = Rig()
            for k, value in ((0, 1), (1, -1), (6, 2)):
                r.mem.memory[0x40123 + k] = value & 255
            for off, value in ((0x7920, 255), (0x7921, 1), (0x794, 11), (0x795, 22)):
                r.w8(off, value)
            def answer(request, mem):
                if request.target == "0791:3D38":
                    self.assertEqual(request.args, (0, 0x2FFC, 2))
                    self.assertFalse(request.far)
                    if candidate:
                        mem.memory[0x2FFC:0x2FFE] = b"\x34\x12"
                    return 0
                if request.target == "0791:261A":
                    self.assertFalse(candidate)
                    return 8
                if request.target == "214B:06B1":
                    self.assertFalse(candidate)
                    self.assertEqual(request.args, (10,))
                    return 5
                if request.target == "0791:34C1":
                    self.assertEqual(request.args, (0x1234 if candidate else 0xE3FA, 5, 0x4000, 0x123))
                    if candidate:
                        r.w8(0x830C, 0)
                    return 0
                if request.target == "0791:2AA3":
                    self.assertEqual(request.args, (22 if candidate else 11,))
                    return 0
                if request.target == "214B:06D0":
                    self.assertEqual(request.args, (8,))
                    return high_draw
                self.assertEqual(request.target, "0791:4D3F")
                return 0x4444
            r.run("0791:3DF6", [0x123, 0x4000], answer)
            self.assertEqual(r.mem.ds8(0x830C), 0)
            self.assertEqual(r.mem.ds8(0x8303), 1 - high_draw)
            self.assertEqual(r.mem.regs["ax"], 0x4444)


if __name__ == "__main__":
    unittest.main()
