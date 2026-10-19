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


class ShotAndHeaderFlow(unittest.TestCase):
    def test_header_skips_jitter_draws_preserves_commentary_high_byte_and_wraps_stat(self):
        r = Rig()
        r.w8(0x78F, 4)
        r.w8(0x7B8B, 255)
        def answer(request, mem):
            if request.target == "0791:287C":
                self.assertEqual(request.args, (4, 0x4000, 0x123))
                return 1
            if request.target == "0791:2C86":return 0xF234
            if request.target == "0791:34C1":
                self.assertEqual(request.args, (0xF234, 2, 0x4000, 0x123))
                return 0xAB00
            if request.target == "0791:2AA3":
                self.assertEqual(request.args, (0xAB56,))
                return 0
            self.assertEqual(request.target, "0791:2974")
            return 1
        r.run("0791:3C3F", [0x123, 0x4000, 2, 0x56], answer)
        self.assertEqual([c[0] for c in r.calls],
                         ["0791:287C", "0791:2C86", "0791:34C1", "0791:2AA3", "0791:2974"])
        self.assertEqual((r.mem.ds8(0x80FB), r.mem.ds8(0x8303), r.mem.ds8(0x7B8B)), (1, 1, 0))

    def test_shot_coin_word_is_live_and_all_failed_gates_reach_last_draw(self):
        r = Rig()
        r.w8(0x82F6, 255)
        r.w8(0x8326, 1)
        def answer(request, mem):
            if request.ret_to == "0791:3C52":return 0xAB00
            if request.ret_to == "0791:3C5A":
                self.assertEqual(mem.regs["sp"], 0x2FFC)
                self.assertEqual(mem.u16(0x2FFC), 0)
                return 0xCD01
            if request.ret_to == "0791:3CF2":return 1
            if request.target == "214B:06D0":
                self.assertIn(request.args, ((4,), (3,)))
            return 0
        r.run("0791:3C3F", [0x123, 0x4000, 1, 0x56], answer)
        self.assertEqual(r.mem.ds8(0x82F6), 0)
        self.assertEqual((r.mem.ds8(0x80FB), r.mem.ds8(0x8303)), (0, 0))
        self.assertEqual([c[0] for c in r.calls], ["214B:06FA", "214B:06FA", "0791:287C",
                         "214B:06D0", "0791:29B3", "0791:2C86", "0791:34C1", "0791:2AA3",
                         "214B:06FA", "214B:06D0"])

    def test_shot_four_short_circuits_skill_and_late_one_in_three_draw(self):
        r = Rig()
        r.w8(0x8324, 1)
        r.w8(0x8326, 1)
        r.run("0791:3C3F", [0x123, 0x4000, 4, 0x56],
              lambda request, mem: 1 if request.target == "214B:06FA" else 0)
        self.assertEqual([c[0] for c in r.calls], ["214B:06FA", "214B:06FA", "0791:2C86",
                         "0791:34C1", "0791:2AA3", "214B:06FA"])
        self.assertEqual((r.mem.ds8(0x80FB), r.mem.ds8(0x8303)), (0, 1))


class CrossTarget(unittest.TestCase):
    def test_membership_uses_guest_zf_then_unavailability_and_goal_strip(self):
        r = Rig()
        # Synthetic player array, with nonzero AX high byte from slot's long product.
        r.mem.wds16(0xA91B, 0x400, "0791:3D38")
        r.mem.wds16(0xA91D, 0x4000, "0791:3D38")
        r.mem.w8(r.mem.addr(0x4000, 0x1806), 4, "0791:3D38")
        for slot in range(2, 12):
            r.record(slot, slot, -slot)
            r.mem.wds16(0x80E8 + slot * 22 + 13, 0x100, "0791:3D38")
        active = [None]
        def answer(request, mem):
            if request.target == "0791:2996":return 1
            if request.target == "23E4:08DF":
                active[0] = (mem.u16(mem.ss_lin(mem.regs["bp"] - 8)) - 0x80E8) // 22
                self.assertEqual(request.args, (0x1404, mem.seg(0x0791), 0x3D18))
                mem.regs["eflags"] = 0x242 if active[0] == 3 else 0x202
                return 0xFFFF                                # AX is deliberately unrelated to membership
            if request.target == "1771:3216":
                self.assertEqual(request.args, (0x100,))
                return int(active[0] == 4)
            self.assertEqual(request.target, "0791:2EF0")
            self.assertEqual(request.args[1:], (mem.DS, 0x80E8 + active[0] * 22))
            return int(active[0] != 5)
        regs = r.run("0791:3D38", [2, 0x100, 0x4000], answer)
        self.assertEqual(r.mem.u16(r.mem.addr(0x4000, 0x100)), 0xFA06)
        self.assertEqual(regs["ax"], 0xFA06)
        self.assertEqual(sum(c[0] == "23E4:08DF" for c in r.calls), 4)
        self.assertEqual(sum(c[0] == "1771:3216" for c in r.calls), 3)
        self.assertEqual(sum(c[0] == "0791:2EF0" for c in r.calls), 2)

    def test_no_candidate_preserves_caller_output(self):
        r = Rig()
        r.mem.w16(r.mem.addr(0x4000, 0x100), 0xABCD, "0791:3D38")
        def answer(request, mem):
            if request.target == "0791:2996":return 1
            self.assertEqual(request.target, "23E4:08DF")
            mem.regs["eflags"] = 0x242
            return 1
        r.run("0791:3D38", [2, 0x100, 0x4000], answer)
        self.assertEqual(r.mem.u16(r.mem.addr(0x4000, 0x100)), 0xABCD)
        self.assertEqual(sum(c[0] == "23E4:08DF" for c in r.calls), 9)


class NestedOffside(unittest.TestCase):
    def test_first_launch_only_sets_clock_and_preserves_ax(self):
        r = Rig()
        r.mem.regs["ax"] = 0xABCD
        regs = r.run("0791:333F", [0x2000])
        self.assertEqual(r.calls, [])
        self.assertEqual(r.mem.ds8(0x8325), 1)
        self.assertEqual(regs["ax"], 0xABCD)

    def test_nested_parent_pointer_and_signed_side_direction(self):
        for direction in (1, -1):
            r = Rig()
            r.w8(0x8325, 1)
            r.w8(0x8329, 0xAA)
            r.w8(0x82E9, 5 * direction)
            r.record(2, 3, 9 * direction)
            r.mem.w16(0x2006, 0x123, "0791:333F")
            r.mem.w16(0x2008, 0x4000, "0791:333F")
            r.mem.w8(r.mem.addr(0x4000, 0x129), 13, "0791:333F")
            def answer(request, mem):
                if request.target == "0791:30EA":
                    self.assertEqual(request.args[1:], (0x4000, 0x123))
                    return 3 if request.args[0] == 11 else 2
                if request.target == "0791:2996":return 0
                self.assertEqual(request.target, "0791:2BE5")
                self.assertEqual(request.args, (mem.DS, 0x80E8 + 2 * 22))
                return direction & 0xFF
            r.run("0791:333F", [0x2000], answer)
            self.assertEqual((r.mem.ds8(0x830E), r.mem.ds8(0x8329)), (2, 0))
            self.assertEqual(r.mem.ds16(0x8317), ((9 * direction & 255) << 8) | 3)


class PassTarget(unittest.TestCase):
    def test_mode_distance_ties_and_replacement_coin_order(self):
        for long_mode, coin, expected, coins in ((0, 0, 4, 1), (0, 1, 3, 1), (1, 1, 4, 0)):
            r = Rig()
            r.w8(0x778, 10)
            r.w8(0x779, 5)
            r.mem.w8(r.mem.addr(0x4000, 0x129), 2, "0791:3111")
            r.record(3, 8, 0)
            r.record(4, -8, 0)
            def answer(request, mem):
                if request.target == "0791:26D7":
                    self.assertEqual(request.args, (3, 0x4000, 0x123))
                    return long_mode
                if request.target == "0791:2C54":return 0
                if request.target == "0791:261A":return 0
                if request.target == "0791:30EA":
                    self.assertEqual(request.args[1:], (0x4000, 0x123))
                    return 4 if request.args[0] == 11 else 2
                if request.target == "214B:06FA":return coin
                self.assertIn(request.target, ("0791:2956", "0791:2D10"))
                return 0
            regs = r.run("0791:3111", [0x123, 0x4000], answer)
            self.assertEqual(regs["ax"], expected)
            self.assertEqual(sum(c[0] == "214B:06FA" for c in r.calls), coins)
            self.assertEqual(sum(c[0] == "0791:2C54" for c in r.calls), int(not long_mode))

    def test_fallback_returns_last_available_even_in_state13(self):
        r = Rig()
        r.mem.w8(r.mem.addr(0x4000, 0x129), 2, "0791:3111")
        def answer(request, mem):
            if request.target == "0791:30EA":return 4 if request.args[0] == 11 else 2
            if request.target == "0791:2956":
                slot = (request.args[-1] - 0x80E8) // 22
                return int(slot == 3)
            if request.target == "214B:06FA":self.fail("fallback must not draw coins")
            return 0
        regs = r.run("0791:3111", [0x123, 0x4000], answer)
        self.assertEqual(regs["ax"], 4)
        self.assertEqual([c[1][0] for c in r.calls if c[0] == "0791:30EA"], [2, 11, 11, 2])


class MoveBallToSlot(unittest.TestCase):
    def test_offside_and_own_goal_strip_short_circuit_launch(self):
        for offside in (0, 1):
            r = Rig()
            r.w8(0x830E, offside)
            r.run("0791:384C", [0x123, 0x4000, 2], lambda request, mem: 1)
            self.assertEqual([c[0] for c in r.calls], ["0791:82EB"] if offside else ["0791:2EB8"])

    def test_self_target_keeps_incremented_draw_live_and_divides_toward_zero(self):
        r = Rig()
        r.w8(0x80FA, 1)
        r.w8(0x830B, 2)
        r.record(2, 4, 5)
        r.mem.w8(r.mem.addr(0x4000, 0x129), 2, "0791:384C")
        def answer(request, mem):
            if request.target == "0791:2EB8":return 0
            if request.target == "0791:261A":return 2
            if request.target == "0791:2BE5":
                self.assertEqual(request.ret_to, "0791:38AA")
                self.assertEqual(mem.regs["sp"], 0x2FF8)
                self.assertEqual(mem.u16(0x2FF8), 3)
                return 0xFF
            if request.target == "0791:34C1":
                self.assertEqual(request.args, (0x0404, 11, 0x4000, 0x123))
                self.assertEqual(mem.ds8(0x80E8 + 2 * 22 + 18), 5)
                mem.wds16(0x8313, 0x0607, "0791:3947")
                return 0
            self.assertEqual(request.target, "0791:835F")
            return 5
        r.run("0791:384C", [0x123, 0x4000, 2], answer)
        self.assertEqual(r.mem.ds8(0x8303), 0)
        self.assertEqual([c[0] for c in r.calls],
                         ["0791:2EB8", "0791:261A", "0791:2BE5", "0791:34C1", "0791:835F"])

    def test_other_target_random_adjustment_has_strict_absolute_25_boundary(self):
        for y in (24, -24, 25, -25):
            r = Rig()
            r.w8(0x80FA, 1)
            r.record(3, 4, y)
            r.mem.w8(r.mem.addr(0x4000, 0x129), 2, "0791:384C")
            r.mem.wds16(0xA91B, 0x2000, "0791:384C")
            r.mem.w8(0x2006, 8, "0791:384C")
            def answer(request, mem):
                if request.target == "0791:2EB8":return 0
                if request.target == "214B:06B1":
                    self.assertEqual(request.args, (8,))
                    return 7
                if request.target == "0791:2BE5":
                    self.assertEqual(request.ret_to, "0791:38FC")
                    self.assertEqual(mem.regs["sp"], 0x2FF8)
                    self.assertEqual(mem.u16(0x2FF8), 7)
                    return 0xFF
                if request.target == "0791:34C1":
                    adjusted = y - 1 if abs(y) < 25 else y
                    self.assertEqual(request.args[0], ((adjusted & 255) << 8) | 4)
                    return 0
                self.assertEqual(request.target, "0791:835F")
                return 21
            r.run("0791:384C", [0x123, 0x4000, 3], answer)
            self.assertEqual(sum(c[0] == "214B:06B1" for c in r.calls), int(abs(y) < 25))
            self.assertEqual(r.mem.ds8(0x8303), 1)


class LaunchBall(unittest.TestCase):
    @staticmethod
    def setup():
        r = Rig()
        r.w8(0x7920, 255)
        r.w8(0x7921, 1)
        r.w8(0x830C, 3)
        r.mem.w8(r.mem.addr(0x4000, 0x129), 2, "0791:34C1")
        return r

    def math_answer(self, request, mem, divide_override=None):
        from original_match.port.mem import s16
        if request.target == "23E4:0294":
            self.assertEqual(mem.regs["sp"], 0x2FF4)
            self.assertEqual((mem.u16(0x2FF4), mem.u16(0x2FF6)), (2, 0))
            value = mem.regs["ax"] if divide_override is None else divide_override
            if divide_override is None:value //= mem.regs["cx"]
            mem.regs["dx"] = value >> 16
            return value & 0xFFFF
        if request.target == "214B:0D56":
            high1, low1, high2, low2 = request.args
            value = max((high1 << 16) | low1, (high2 << 16) | low2)
            mem.regs["dx"] = value >> 16
            return value & 0xFFFF
        if request.target == "23E4:0279":
            value = s16(mem.regs["ax"]) * mem.regs["cx"]
            self.assertEqual(mem.regs["dx"], 0xFFFF if s16(mem.regs["ax"]) < 0 else 0)
            mem.regs["dx"] = (value >> 16) & 0xFFFF
            return value & 0xFFFF
        if request.target == "214B:1EA1":
            self.assertEqual(request.args, (10, 1))
            return 0
        if request.target == "0791:333F":
            self.assertEqual(request.args, (0x2FFE,))
            return 0xAB00
        self.fail("unexpected call " + request.target)

    def test_signed_launch_from_both_sides_and_velocity_ratio(self):
        for x, y, expected in ((-8, 4, (255, 1, 6, 250, 6)),
                                (8, -4, (1, 255, 6, 6, 250)),
                                (4, 8, (1, 2, 4, 4, 8)),
                                (-4, -8, (255, 254, 4, 252, 248))):
            r = self.setup()
            def answer(request, mem):
                if request.target == "23E4:08DF":
                    mem.regs["eflags"] = 0x242
                    return 0
                return self.math_answer(request, mem)
            regs = r.run("0791:34C1", [0x123, 0x4000, 8, ((y & 255) << 8) | (x & 255)], answer)
            actual = (r.mem.ds8(0x82FC), r.mem.ds8(0x82FE), r.mem.ds16(0x8300),
                      r.mem.ds8(0x8313), r.mem.ds8(0x8314))
            self.assertEqual(actual, expected)
            self.assertEqual((r.mem.ds8(0x830D), regs["ax"]), (3, 0xAB03))

    def test_event_membership_uses_zf_and_keeps_long_bound_live(self):
        for event, expected in ((1, 13), (3, 15)):
            r = self.setup()
            r.w8(0x779 + event, 9)
            r.mem.w8(r.mem.addr(0x4000, 0x134), 7, "0791:34C1")
            def answer(request, mem):
                if request.target == "23E4:08DF":
                    self.assertEqual(request.args[-2], mem.seg(0x0791))
                    selected = (event == 1 and request.args[-1] == 0x3481) or (event == 3 and request.args[-1] == 0x34A1)
                    mem.regs["eflags"] = 0x202 if selected else 0x242
                    return 0                                  # AX does not carry the membership result
                if request.target == "0791:278A":
                    self.assertEqual(request.args, (9, 0x4000, 0x123))
                    self.assertEqual(mem.regs["sp"], 0x2FF4)
                    self.assertEqual((mem.u16(0x2FF4), mem.u16(0x2FF6)), (13, 0))
                    return 17 if event == 1 else 45
                return self.math_answer(request, mem)
            r.run("0791:34C1", [0x123, 0x4000, event, 8], answer)
            self.assertEqual(r.mem.ds16(0x8300), expected)

    def test_event6_rewrites_argument_to_long_pass_or_keeper_event(self):
        for target, keeper, own_strip, event in ((21, 0, 0, 7), (8, 1, 1, 8), (8, 1, 0, 6)):
            r = self.setup()
            r.w8(0x830C, 2)                                 # no miscue branch
            def answer(request, mem):
                if request.target == "0791:045D":return keeper
                if request.target == "0791:2EB8":return own_strip
                if request.target == "23E4:08DF":
                    self.assertEqual(request.args[0] & 255, event)
                    mem.regs["eflags"] = 0x242
                    return 0
                return self.math_answer(request, mem)
            r.run("0791:34C1", [0x123, 0x4000, 6, target], answer)
            self.assertEqual(r.mem.ds8(0x8327), event)
            if event != 6:self.assertEqual(r.mem.u16(0x3008), event)

    def test_miscue_shortening_sideways_and_drop_vertical_branches(self):
        cases = ((0, 8, 1, 0, 3, (0, 1, 5, 1)),
                 (0, 8, 0, 1, 3, (0, 1, 5, 1)),
                 (0, 8, 0, 0, 0, (1, 2, 2, 2)),
                 (8, 0, 0, 0, 0, (1, 1, 4, 2)),
                 (8, 4, 0, 0, 0, (1, 0, 12, 1)))
        for x, y, coin, flag, draw, expected in cases:
            r = self.setup()
            r.w8(0x8323, flag)
            coin_count = [0]
            def answer(request, mem):
                if request.target == "23E4:08DF":
                    mem.regs["eflags"] = 0x242
                    return 0
                if request.target in ("0791:287C", "0791:045D"):return 0
                if request.target == "214B:06FA":
                    coin_count[0] += 1
                    return coin if coin_count[0] == 1 else 1
                if request.target == "214B:06B1":
                    self.assertEqual(request.args, (4,))
                    return draw
                return self.math_answer(request, mem)
            r.run("0791:34C1", [0x123, 0x4000, 5, (y << 8) | x], answer)
            self.assertEqual((r.mem.ds16(0x82FC), r.mem.ds16(0x82FE),
                              r.mem.ds16(0x8300), coin_count[0]), expected)
            self.assertEqual((r.mem.ds8(0x830C), r.mem.ds8(0x8323)), (0, 0))

    def test_long_division_high_word_is_forwarded_to_maximum(self):
        r = self.setup()
        def answer(request, mem):
            if request.target == "23E4:08DF":
                mem.regs["eflags"] = 0x242
                return 0
            if request.target == "214B:0D56":
                self.assertEqual(request.args, (0, 2, 1, 0x2345))
            return self.math_answer(request, mem, divide_override=0x12345)
        r.run("0791:34C1", [0x123, 0x4000, 8, 8], answer)
        self.assertEqual((r.mem.ds16(0x8300), r.mem.ds8(0x8313)), (0x2345, 0x45))


if __name__ == "__main__":
    unittest.main()
