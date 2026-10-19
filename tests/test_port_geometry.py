"""runtime/original_match/port/geometry.py (T60): the geometry queries, on synthetic memory (no byte of the original).

The stack arguments and DS fields are the listing's; the expected values are worked out from the listing by hand (the
comment names the lines). The ports that call the original (guest calls, port/guest.py) are driven by hand: each Call
they yield is checked (target, argument words in push order, the return address inside the routine) and answered with
a chosen AX. The branches ALL does not reach (the skill halving 27F8, the unavailable-slot advance 2A39, the
opposite-side flag 2A03, the wide x test of 2E00, the clamp of 2022) are here. FuzzAgainstOriginal runs each port
against the original's code on random inputs when the reference image is in .cache/dl and unicorn is installed."""
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import port  # noqa: E402
from original_match.port.guest import Call  # noqa: E402
from original_match.port.mem import PlainMem  # noqa: E402

S = 0x4000                          # a data segment (linear 0x40000)
PLAYERS, COUNTRIES = 0x1000, 0x2000   # offsets in S of the players array and the countries array
PITCH = 0x80E8


class Geo:
    """Plain memory, DS fields, pitch records, and a way to run a port (plain function or generator)."""

    def __init__(self):
        self.mem = PlainMem(bytearray(0x60000))
        self.ds = self.mem.DS
        self.mem.regs.update(ss=0, sp=0x2000, ds=self.ds, eflags=0x202)
        self.ds_far(0xA91B, PLAYERS)
        self.ds_far(0xA917, COUNTRIES)
        self.cs_poke(0x276A, bytes([0x18]) + bytes(31))            # the keeper-events set {3, 4}
        self.ds_poke(0x7920, bytes([0xFF, 0x01]))                  # direction by side index
        self.ds_poke(0x668, bytes([11, 0]))                        # side bases by 2996's flag: 0 -> 11, 1 -> 0
        self.calls = []

    # -- memory --------------------------------------------------------------------------------------------------
    def ds_poke(self, off, data):
        self.mem.memory[self.ds * 16 + off:self.ds * 16 + off + len(data)] = bytes(data)

    def ds_peek(self, off, n=1):
        return bytes(self.mem.memory[self.ds * 16 + off:self.ds * 16 + off + n])

    def ds_far(self, off, target, seg=S):
        self.ds_poke(off, target.to_bytes(2, "little") + seg.to_bytes(2, "little"))

    def cs_poke(self, off, data):
        base = self.mem.seg(0x791) * 16
        self.mem.memory[base + off:base + off + len(data)] = bytes(data)

    def rec(self, slot):
        return PITCH + 0x16 * slot

    def set_rec(self, slot, x=0, y=0, slot_byte=None, player=0, state=0, **fields):
        off = self.rec(slot)
        data = bytearray(0x16)
        data[0], data[1] = x & 0xFF, y & 0xFF
        data[6] = slot if slot_byte is None else slot_byte
        data[0xD:0xF] = player.to_bytes(2, "little")
        data[0x11] = fields.get("b11", 0)
        data[0x12] = state
        data[0x13] = fields.get("halved", 0)
        self.ds_poke(off, data)
        return off

    def set_player(self, index, **fields):
        data = bytearray(0x14)
        for name, value in fields.items():
            data[int(name[1:], 16)] = value & 0xFF
        self.mem.memory[S * 16 + PLAYERS + 0x14 * index:S * 16 + PLAYERS + 0x14 * (index + 1)] = data

    def ball(self, slot, second=0):
        self.ds_poke(0x830B, bytes([slot, second]))

    # -- running -------------------------------------------------------------------------------------------------
    def run(self, address, args=(), answers=(), variant=None, **regs):
        """Run the port; for a generator, answer each guest call with the next AX of `answers`. Returns the registers;
        self.calls lists the (target, args, ret_to, far) the port made."""
        entry = port._module_registry("geometry").entries[address]
        sp = 0x2000
        layout = [0x1234] + ([0x5678] if entry.far else []) + [a & 0xFFFF for a in args]
        for i, w in enumerate(layout):
            self.mem.memory[sp + 2 * i:sp + 2 * i + 2] = (w & 0xFFFF).to_bytes(2, "little")
        self.mem.regs["sp"] = sp
        self.mem.regs["bp"] = 0x1111
        self.mem.regs.update(regs)
        self.calls = []
        self.mem._entries.append((sp, entry.far))
        try:
            out = entry.fn(self.mem, variant)
            if out is not None and hasattr(out, "send"):
                answers = list(answers)
                sent = None
                while True:
                    try:
                        request = out.send(sent)
                    except StopIteration:
                        break
                    assert isinstance(request, Call), request
                    self.calls.append((request.target, request.args, request.ret_to, request.far))
                    ax = answers.pop(0) if answers else 0
                    self.mem.regs["ax"] = ax
                    sent = ax
        finally:
            self.mem._entries.pop()
        return self.mem.regs


class TableAndMessages(unittest.TestCase):
    def test_draw_table_byte_returns_the_entry_and_steps_the_index(self):
        g = Geo()
        g.ds_poke(0x8437, (5).to_bytes(2, "little"))
        g.ds_poke(0x8337 + 5, b"\x09")
        regs = g.run("0791:261A", ax=0xAA00, dx=0x77)
        self.assertEqual((regs["ax"], regs["dx"]), (9, 0x77))
        self.assertEqual(g.ds_peek(0x8437, 2), (6).to_bytes(2, "little"))

    def test_draw_table_index_wraps_from_0xff_to_1(self):
        g = Geo()
        g.ds_poke(0x8437, (0xFF).to_bytes(2, "little"))
        g.ds_poke(0x8337 + 0xFF, b"\x0C")
        self.assertEqual(g.run("0791:261A")["ax"], 0x0C)
        self.assertEqual(g.ds_peek(0x8437, 2), (1).to_bytes(2, "little"))

    def test_set_message_word(self):
        g = Geo()
        regs = g.run("0791:26A0", [1], ax=0x1234, dx=0x5678)
        self.assertEqual(g.ds_peek(0x8308, 2), (0x0EAF).to_bytes(2, "little"))
        self.assertEqual(g.ds_peek(0x8328), b"\x01")
        self.assertEqual((regs["ax"], regs["dx"]), (0x1234, 0x5678))
        g.run("0791:26A0", [0x100])                                         # only the low byte is tested
        self.assertEqual(g.ds_peek(0x8308, 2), (0x0EAE).to_bytes(2, "little"))

    def test_show_message_calls_9079_with_the_message_pointer_then_clears_8328(self):
        g = Geo()
        g.ds_poke(0x8328, b"\x01")
        g.run("0791:26C2", answers=[0x4242])
        self.assertEqual(g.calls, [("0791:9079", (g.ds, 0x8304), "0791:26CE", True)])
        self.assertEqual(g.ds_peek(0x8328), b"\x00")


class SidesAndSlots(unittest.TestCase):
    def test_ball_slot_side_and_slot_in_side(self):
        g = Geo()
        g.ball(0x0B)
        self.assertEqual(g.run("0791:2996", ax=0x7700)["ax"], 0x7701)
        g.ball(0x0C)
        self.assertEqual(g.run("0791:2996", ax=0x7700)["ax"], 0x7700)
        off = g.set_rec(3, slot_byte=0x0C)
        self.assertEqual(g.run("0791:2BB1", [off, g.ds], ax=0x7799)["ax"], 0x0001, "AH 0, AL = 0xC - 0xB")
        off = g.set_rec(3, slot_byte=0x0B)
        self.assertEqual(g.run("0791:2BB1", [off, g.ds], ax=0x7799)["ax"], 0x770B, "a slot of 0xB keeps AH")
        off = g.set_rec(3, slot_byte=0x16)
        self.assertEqual(g.run("0791:2BB1", [off, g.ds], ax=0x7799)["ax"], 0x000B)

    def test_slot_side_12_variant_changes_slot_12(self):
        g = Geo()
        off = g.set_rec(3, slot_byte=0x0C)
        self.assertEqual(g.run("0791:2BB1", [off, g.ds], variant="slot-side-12")["ax"] & 0xFF, 0x0C)

    def test_second_slot_in_side(self):
        g = Geo()
        g.ball(5, 0)
        self.assertEqual(g.run("0791:2A6D", ax=0x5555, dx=0x66)["ax"], 0)
        g.ball(5, 0x0E)
        g.set_rec(0x0E, slot_byte=0x0E)
        regs = g.run("0791:2A6D")
        self.assertEqual((regs["ax"], regs["dx"]), (3, 0), "0xE - 0xB; DX the mul's high word")

    def test_slot_is_on_ball_side(self):
        g = Geo()
        g.ball(2)
        on = g.set_rec(4, slot_byte=4)
        off = g.set_rec(14, slot_byte=14)
        self.assertEqual(g.run("0791:2B51", [on, g.ds], ax=0x4400)["ax"], 0x4401)
        regs = g.run("0791:2B51", [off, g.ds], ax=0x4400)
        self.assertEqual((regs["ax"], regs["dx"]), (0x4400, 0x4401), "DX is the AX 2996 pushed")

    def test_slot_is_idle_ball_slot(self):
        g = Geo()
        off = g.set_rec(5)
        g.ball(5)
        g.ds_poke(0x8302, b"\x00")
        self.assertEqual(g.run("0791:2C29", [off, g.ds], ax=0x3300)["ax"], 0x3301)
        g.ds_poke(0x8302, b"\x01")
        self.assertEqual(g.run("0791:2C29", [off, g.ds], ax=0x3300)["ax"], 0x3300)
        g.ds_poke(0x8302, b"\x00")
        g.ball(6)
        self.assertEqual(g.run("0791:2C29", [off, g.ds], ax=0x3300)["ax"], 0x3300)

    def test_fill_pitch_state_writes_all_22_records_and_leaves_ax_dx_cx(self):
        g = Geo()
        regs = g.run("0791:2929", [0x37], cx=0x1200)
        for slot in range(1, 23):
            self.assertEqual(g.ds_peek(self.state_off(slot)), b"\x37")
        self.assertEqual(g.ds_peek(self.state_off(0)), b"\x00")
        self.assertEqual((regs["ax"], regs["dx"], regs["cx"]), (22 * 22, 0, 0x1237))

    @staticmethod
    def state_off(slot):
        return PITCH + 0x16 * slot + 0x12

    def test_all_players_in_state_counts_each_reason_and_asks_2956_for_the_rest(self):
        g = Geo()
        for slot in range(1, 23):
            g.set_rec(slot, state=7)
        g.ball(0)
        self.assertEqual(g.run("0791:28B2", [7], ax=0x9900)["ax"] & 0xFF, 1)
        self.assertEqual(g.calls, [], "every record has the state: no question asked")
        g.ds_poke(self.state_off(3), b"\x00")
        g.ball(3)                                                            # the ball slot counts without a question
        self.assertEqual(g.run("0791:28B2", [7])["ax"] & 0xFF, 1)
        self.assertEqual(g.calls, [])
        g.ball(0, 3)                                                         # so does the second slot
        self.assertEqual(g.run("0791:28B2", [7])["ax"] & 0xFF, 1)
        g.ball(0, 0)
        regs = g.run("0791:28B2", [7], answers=[1])                           # 2956 says he cannot play: counted
        self.assertEqual(regs["ax"] & 0xFF, 1)
        self.assertEqual(g.calls, [("0791:2956", (g.ds, g.rec(3)), "0791:2904", True)])
        regs = g.run("0791:28B2", [7], answers=[0])                           # he can: not counted, the result is 0
        self.assertEqual(regs["ax"] & 0xFF, 0)

    def test_player_unavailable_asks_3216_of_the_records_player(self):
        g = Geo()
        off = g.set_rec(4, player=0x0123)
        regs = g.run("0791:2956", [off, g.ds], answers=[0x0001], dx=0x66)
        self.assertEqual(g.calls, [("1771:3216", (0x0123,), "0791:2968", True)])
        self.assertEqual(regs["ax"], 1)

    def test_ball_holder_farther_flag(self):
        g = Geo()
        g.ball(3)                                                            # the holder is below 0xC: the other side's slot 11 + 1
        g.set_rec(12, y=0xF0)                                                 # |y| = 16
        g.set_rec(3, y=0x14)                                                  # |y| = 20
        regs = g.run("0791:29B3", ax=0x1100)
        self.assertEqual(g.ds_peek(0x80FB), b"\x01")
        self.assertEqual((regs["ax"], regs["dx"]), (1, 0))
        g.set_rec(3, y=0x0F)
        self.assertEqual(g.run("0791:29B3")["ax"], 0)
        self.assertEqual(g.ds_peek(0x80FB), b"\x00")
        g.set_rec(3, y=0xF0)                                                  # equal: `jge` is a flag of 1
        self.assertEqual(g.run("0791:29B3")["ax"], 1)
        g.ball(14)                                                           # the holder is 0xC or more: the other side's slot 0 + 1
        g.set_rec(1, y=0x05)
        g.set_rec(14, y=0x05)
        self.assertEqual(g.run("0791:29B3")["ax"], 1)
        g.set_rec(1, y=0x06)
        self.assertEqual(g.run("0791:29B3")["ax"], 0)

    def test_advance_unavailable_ball_slot(self):
        g = Geo()
        g.ball(0)
        g.run("0791:2A15", ax=0x3131)
        self.assertEqual(g.calls, [], "slot 0: nothing")
        g.ball(3)
        g.set_rec(3)
        regs = g.run("0791:2A15", answers=[0])
        self.assertEqual(g.calls, [("0791:2956", (g.ds, g.rec(3)), "0791:2A35", True)])
        self.assertEqual(g.ds_peek(0x830B), b"\x03")
        regs = g.run("0791:2A15", answers=[1, 0])                             # unavailable: next slot, asked again
        self.assertEqual([c[1][1] for c in g.calls], [g.rec(3), g.rec(4)])
        self.assertEqual(g.ds_peek(0x830B), b"\x04")
        g.ball(11)
        g.run("0791:2A15", answers=[1, 0])                                    # past the side's last slot: wraps to base + 2
        self.assertEqual(g.ds_peek(0x830B), b"\x02", "11 + 1 > 0 + 0xB wraps to 11 + 1 - 11 + 2 - 1")
        g.ball(14)                                                           # the other side: slots 11 + 2 .. 11 + 0xB
        g.run("0791:2A15", answers=[1, 0])
        self.assertEqual(g.ds_peek(0x830B), b"\x0F")
        g.ball(22)
        g.run("0791:2A15", answers=[1, 0])
        self.assertEqual(g.ds_peek(0x830B), b"\x0D", "22 + 1 > 11 + 0xB wraps to 22 + 1 - 22 + 13 - 1")


class Commentary(unittest.TestCase):
    def test_with_the_ball_slot(self):
        g = Geo()
        g.ball(0x0E, 0)
        g.set_rec(0x0E, slot_byte=0x0E)
        g.run("0791:2AA3", [0x2B], ax=0x4400, dx=0x99)
        # 2996 -> AL 0 (slot 0xE is not below 0xC), AH kept; 2BB1 -> 0xE - 0xB = 3; 2A6D -> 0 (no second slot); the code
        self.assertEqual(g.calls, [("0791:1EB5", (0x4400, 3, 0, 0x2B), "0791:2ACE", False)])

    def test_with_both_slots(self):
        g = Geo()
        g.ball(0x05, 0x0E)
        g.set_rec(5, slot_byte=5)
        g.set_rec(0x0E, slot_byte=0x0E)
        g.run("0791:2AD4", [0x31], ax=0x4400)
        # [830C] = 0xE is not below 0xC: 0; 2A6D = 3; the ball slot's slot in side = 5; the code
        self.assertEqual(g.calls, [("0791:1EB5", (0x4400, 3, 5, 0x31), "0791:2B09", False)])

    def test_plain_and_for_a_record(self):
        g = Geo()
        g.run("0791:2B0F", [0x1FF], ax=0x4400)
        self.assertEqual(g.calls, [("0791:1EB5", (0x4401, 0, 0, 0xFF), "0791:2B22", False)])
        off = g.set_rec(4, slot_byte=0x0D)
        g.run("0791:2B28", [off, g.ds, 0x50], ax=0x4400)
        self.assertEqual(g.calls, [("0791:1EB5", (0x4400, 2, 0, 0x50), "0791:2B4B", False)])
        off = g.set_rec(4, slot_byte=0x03)
        g.run("0791:2B28", [off, g.ds, 0x50], ax=0x4400)
        self.assertEqual(g.calls, [("0791:1EB5", (0x4401, 3, 0, 0x50), "0791:2B4B", False)])


class Directions(unittest.TestCase):
    def setup_dir(self, g, half, left):
        g.ds_poke(0x8319, bytes([half & 0xFF]))
        g.ds_poke(0x831B, left.to_bytes(2, "little"))

    def test_own_half_and_mirror(self):
        g = Geo()
        self.setup_dir(g, 0x10, 0x20)                                         # 0x20 > 0x10: flag 1
        on = g.set_rec(2, slot_byte=2, y=0x05)                               # side 1: direction index 1 ^ 1 = 0 -> -1
        off = g.set_rec(14, slot_byte=14, y=0x05)                            # side 0: index 0 ^ 1 = 1 -> +1
        regs = g.run("0791:2C54", [on, g.ds], ax=0x5500)
        self.assertEqual((regs["ax"], regs["dx"]), (0xFF01, 0xFFFF), "y 5 * direction -1 = -5: AH and DX are the product's")
        regs = g.run("0791:2C54", [off, g.ds], ax=0x5500)
        self.assertEqual((regs["ax"], regs["dx"]), (0, 0), "y 5 * +1 is positive")
        g.set_rec(14, slot_byte=14, y=0)
        self.assertEqual(g.run("0791:2C54", [off, g.ds])["ax"], 0, "zero is not the own half")
        self.assertEqual(g.run("0791:2C54", [off, g.ds], variant="own-half-zero")["ax"] & 0xFF, 1)

    def test_mirror_to_team_frame_multiplies_both_bytes_and_writes_the_argument(self):
        g = Geo()
        self.setup_dir(g, 0x10, 0x20)
        on = g.set_rec(2, slot_byte=2)                                        # direction -1
        regs = g.run("0791:2C86", [on, g.ds, 0x0305])                          # x = 5, y = 3
        self.assertEqual(regs["ax"], 0xFD << 8 | 0xFB, "(-3, -5) as bytes")
        self.assertEqual(g.mem.memory[0x2000 + 8:0x2000 + 10], bytes([0xFB, 0xFD]), "written into the caller's argument word")

    def test_player_at_ball(self):
        g = Geo()
        g.ds_poke(0x82F6, bytes([5, 7]))
        off = g.set_rec(2, x=5, y=7)
        self.assertEqual(g.run("0791:2CEC", [off, g.ds], ax=0x1200)["ax"], 0x0701, "AH is the record's y byte")
        off = g.set_rec(2, x=5, y=8)
        self.assertEqual(g.run("0791:2CEC", [off, g.ds], ax=0x1200)["ax"], 0x0800)

    def test_ball_ahead_of_by_and_ahead_of_ball_by(self):
        g = Geo()
        self.setup_dir(g, 0x10, 0x20)
        on = g.set_rec(2, slot_byte=2, y=0x05)                               # direction -1: y * dir = -5
        g.ds_poke(0x82F7, bytes([0xF0]))                                      # ball y -16: * -1 = 16
        # ball ahead of the record by more than n: 16 > -5 + n
        for n, want in ((20, 1), (21, 0), (22, 0), (0, 1)):
            self.assertEqual(g.run("0791:2D10", [on, g.ds, n])["ax"] & 0xFF, want, n)
        # the record (-5) ahead of the ball (16) by more than n: -5 > 16 + n: never for n >= 0
        self.assertEqual(g.run("0791:2D6D", [on, g.ds, 0])["ax"] & 0xFF, 0)
        g.ds_poke(0x82F7, bytes([0x10]))                                      # ball y 16 * -1 = -16: -5 > -16 + n
        for n, want in ((10, 1), (11, 0), (12, 0)):
            self.assertEqual(g.run("0791:2D6D", [on, g.ds, n])["ax"] & 0xFF, want, n)

    def test_ahead_inclusive_variant_counts_a_tie(self):
        g = Geo()
        self.setup_dir(g, 0x10, 0x20)
        on = g.set_rec(2, slot_byte=2, y=0x05)
        g.ds_poke(0x82F7, bytes([0xF0]))                                      # 16 against -5 + 21
        self.assertEqual(g.run("0791:2D10", [on, g.ds, 21])["ax"] & 0xFF, 0)
        self.assertEqual(g.run("0791:2D10", [on, g.ds, 21], variant="ahead-inclusive")["ax"] & 0xFF, 1)


class Strips(unittest.TestCase):
    def test_on_pitch_wide(self):
        g = Geo()
        for word, want in ((0x2709, 1), (0x270A, 0), (0x2809, 0), (0xD909, 1), (0xD9F7, 1), (0xD8F7, 0), (0x0000, 1)):
            self.assertEqual(g.run("0791:2E00", [word], ax=0x6600)["ax"], want, hex(word))

    def test_penalty_strip_word(self):
        g = Geo()
        for word, want in ((0x1905, 1), (0x1906, 0), (0x1805, 0), (0xE705, 1), (0xE7FB, 1), (0xE7FA, 0), (0x7F00, 1)):
            self.assertEqual(g.run("0791:2E82", [word], dx=0x42)["ax"], want, hex(word))
            self.assertEqual(g.mem.regs["dx"], 0x42, "DX untouched")

    def test_penalty_strip_4_variant(self):
        g = Geo()
        self.assertEqual(g.run("0791:2E82", [0x1905])["ax"], 1)
        self.assertEqual(g.run("0791:2E82", [0x1905], variant="penalty-strip-4")["ax"], 0)

    def test_goal_area_and_goal_strips_by_direction(self):
        g = Geo()
        g.ds_poke(0x8319, bytes([0x10]))
        g.ds_poke(0x831B, (0x20).to_bytes(2, "little"))                        # flag 1: side 1 direction -1, side 0 +1
        on = g.set_rec(2, slot_byte=2)                                        # direction -1 (own goal at y positive)
        far = g.set_rec(14, slot_byte=14)                                     # direction +1
        # in_own_goal_area: y * dir < 0, |y| >= 0x21, |x| <= 2
        self.assertEqual(g.run("0791:2E36", [on, g.ds, 0x2102])["ax"] & 0xFF, 1)
        self.assertEqual(g.run("0791:2E36", [on, g.ds, 0x2103])["ax"] & 0xFF, 0)
        self.assertEqual(g.run("0791:2E36", [on, g.ds, 0x2002])["ax"] & 0xFF, 0)
        self.assertEqual(g.run("0791:2E36", [far, g.ds, 0x2102])["ax"] & 0xFF, 0, "y 0x21 * +1 is not negative")
        self.assertEqual(g.run("0791:2E36", [far, g.ds, 0xDF02])["ax"] & 0xFF, 1)
        # the strips: the own end (y * dir < 0) and the opposing end (> 0), through 2E82
        self.assertEqual(g.run("0791:2EB8", [on, g.ds, 0x1905])["ax"] & 0xFF, 1)
        self.assertEqual(g.run("0791:2EB8", [far, g.ds, 0x1905])["ax"] & 0xFF, 0)
        self.assertEqual(g.run("0791:2EB8", [on, g.ds, 0x1805])["ax"] & 0xFF, 0)
        self.assertEqual(g.run("0791:2EF0", [far, g.ds, 0x1905])["ax"] & 0xFF, 1)
        self.assertEqual(g.run("0791:2EF0", [on, g.ds, 0x1905])["ax"] & 0xFF, 0)
        self.assertEqual(g.run("0791:2EF0", [on, g.ds, 0x0005])["ax"] & 0xFF, 0, "y 0: neither end")
        self.assertEqual(g.run("0791:2EB8", [on, g.ds, 0x0005])["ax"] & 0xFF, 0)

    def test_final_third_of_goal(self):
        g = Geo()
        g.ds_poke(0x8319, bytes([0x10]))
        g.ds_poke(0x831B, (0x20).to_bytes(2, "little"))
        g.ds_poke(0x776, bytes([4, 9]))                                       # the |x| limits by |y| > 0x1C
        g.set_player(7, b6=0x10)
        far = g.set_rec(14, slot_byte=14, player=7, x=9, y=0x1D + 0x1C - 0x1C)   # direction +1: y positive: not the own half
        # limit |y| >= 0x10 + 0xC = 0x1C; |y| = 0x1D > 0x1C: x limit 9
        self.assertEqual(g.run("0791:2F28", [far, g.ds])["ax"] & 0xFF, 1)
        far = g.set_rec(14, slot_byte=14, player=7, x=10, y=0x1D)
        self.assertEqual(g.run("0791:2F28", [far, g.ds])["ax"] & 0xFF, 0, "|x| 10 is past 9")
        far = g.set_rec(14, slot_byte=14, player=7, x=4, y=0x1C)
        self.assertEqual(g.run("0791:2F28", [far, g.ds])["ax"] & 0xFF, 1, "|y| 0x1C is not above 0x1C: x limit 4")
        far = g.set_rec(14, slot_byte=14, player=7, x=5, y=0x1C)
        self.assertEqual(g.run("0791:2F28", [far, g.ds])["ax"] & 0xFF, 0)
        far = g.set_rec(14, slot_byte=14, player=7, x=0, y=0x1B)
        self.assertEqual(g.run("0791:2F28", [far, g.ds])["ax"] & 0xFF, 0, "|y| below the player's +6 + 0xC")
        on = g.set_rec(2, slot_byte=2, player=7, x=0, y=0x1D)                # direction -1: y positive is the own half
        self.assertEqual(g.run("0791:2F28", [on, g.ds])["ax"] & 0xFF, 0)


class Tactics(unittest.TestCase):
    def setup_tactics(self, own, country_byte, side_slot=3, country=1):
        g = Geo()
        off = g.set_rec(side_slot, slot_byte=side_slot, player=2)
        g.set_player(2, bF=own)
        g.ds_poke(0x9B34, bytes([0, 0, country, 0]))                           # side 1's country index
        self.country_off = COUNTRIES + 0xBF * country + 0x2D
        g.mem.memory[S * 16 + self.country_off] = country_byte
        return g, off

    def test_player_setting_wins_when_the_flag_element_is_set(self):
        # k = 2: the flag is element 6 (bit 5), the value element 2 (bit 1)
        g, off = self.setup_tactics(0b00100010, 0)
        regs = g.run("0791:26D7", [off, g.ds, 2], ax=0xAB00)
        self.assertEqual((regs["ax"], regs["dx"]), (1, 1))
        g, off = self.setup_tactics(0b00100000, 0xFF)
        self.assertEqual(g.run("0791:26D7", [off, g.ds, 2])["ax"], 0, "the player's own setting (0) beats the country's")

    def test_country_byte_decides_without_the_flag_or_when_k_is_5_or_more(self):
        g, off = self.setup_tactics(0b00000010, 0b00000100)                    # the flag clear: the country's bit 2 (k = 3)
        self.assertEqual(g.run("0791:26D7", [off, g.ds, 3])["ax"], 1)
        g, off = self.setup_tactics(0xFF, 0b00000000)
        self.assertEqual(g.run("0791:26D7", [off, g.ds, 5])["ax"], 0, "k = 5 never looks at the player")
        g, off = self.setup_tactics(0x00, 0b00010000, side_slot=14, country=2)    # side 0 reads the country at DS:9B34
        g.ds_poke(0x9B34, bytes([2, 0, 0, 0]))
        g.mem.memory[S * 16 + COUNTRIES + 0xBF * 2 + 0x2D] = 0b00010000
        regs = g.run("0791:26D7", [off, g.ds, 5])
        self.assertEqual((regs["ax"], regs["dx"]), (1, 4))


class Skill(unittest.TestCase):
    def skill_rig(self, form=5, energy=10, halved=0, slot_byte=3, b11=0x22, manager=0):
        g = Geo()
        off = g.set_rec(3, slot_byte=slot_byte, player=2, halved=halved, b11=b11)
        g.set_player(2, bC=form, bE=energy)
        g.ds_poke(0x80FC, bytes([manager]))
        return g, off

    def test_contest_value_formula_and_the_guest_call(self):
        g, off = self.skill_rig()
        regs = g.run("0791:278A", [off, g.ds, 3], answers=[64], dx=0x1234)
        self.assertEqual(g.calls, [("1771:3A06", (2, 3), "0791:27EB", True)])
        # base = (5 + 1) + 10 = 16; skill 64: 16 * 64 div 256 = 4, + 64 div 4 = 16: 20
        self.assertEqual(regs["ax"], 20)
        self.assertEqual(regs["dx"], 0, "the last div (281C) leaves the low byte of the product, 1024 -> 0")

    def test_form_at_0x20_counts_zero_and_a_negative_form_counts_its_sign(self):
        g, off = self.skill_rig(form=0x20)                                    # signed >= 0x20: base 0 + 10
        self.assertEqual(g.run("0791:278A", [off, g.ds, 3], answers=[64])["ax"], 10 * 64 // 256 + 16)
        g, off = self.skill_rig(form=0xF0, energy=0)                          # -16 + 1 = -15 = 0xFFF1
        regs = g.run("0791:278A", [off, g.ds, 3], answers=[64])
        self.assertEqual(regs["ax"], ((0xFFF1 * 64) & 0xFFFF) // 256 + 16)

    def test_penalty_elements_add_0x20_and_ignore_energy(self):
        g, off = self.skill_rig()
        regs = g.run("0791:278A", [off, g.ds, 0x0C], answers=[64])
        self.assertEqual(regs["ax"], (6 + 0x20) * 64 // 256 + 16)

    def test_a_halved_pitch_record_halves_the_skill(self):
        g, off = self.skill_rig(halved=1)
        regs = g.run("0791:278A", [off, g.ds, 3], answers=[64])
        self.assertEqual(regs["ax"], 16 * 32 // 256 + 8)
        self.assertEqual(g.run("0791:278A", [off, g.ds, 3], answers=[64], variant="skill-no-halving")["ax"], 20)
        regs = g.run("0791:278A", [off, g.ds, 3], answers=[65])
        self.assertEqual(regs["ax"], 16 * 32 // 256 + 8, "65 halves to 32")

    def test_the_manager_share_for_outfield_slots(self):
        g, off = self.skill_rig(manager=1)
        regs = g.run("0791:278A", [off, g.ds, 3], answers=[64])
        self.assertEqual((regs["ax"], regs["dx"]), (21, 4), "20 + 20 div 16; DX the remainder 4")
        g, off = self.skill_rig(manager=1, slot_byte=0x0C)
        self.assertEqual(g.run("0791:278A", [off, g.ds, 3], answers=[64])["ax"], 20, "slot 0xC and up has no share")

    def test_the_keeper_extra_by_table_and_by_event(self):
        g, off = self.skill_rig(b11=0x22)
        g.ds_poke(0x769 + 2, b"\x01")                                         # element 2: any nonzero byte adds +0x11
        self.assertEqual(g.run("0791:278A", [off, g.ds, 2], answers=[64])["ax"], 20 + 0x22)
        g.ds_poke(0x8327, b"\x03")                                            # element 1, DS:8327 in {3, 4}: adds
        self.assertEqual(g.run("0791:278A", [off, g.ds, 1], answers=[64])["ax"], 20 + 0x22)
        g.ds_poke(0x8327, b"\x04")
        self.assertEqual(g.run("0791:278A", [off, g.ds, 1], answers=[64])["ax"], 20 + 0x22)
        g.ds_poke(0x8327, b"\x05")
        self.assertEqual(g.run("0791:278A", [off, g.ds, 1], answers=[64])["ax"], 20)
        g.ds_poke(0x8327, b"\x18")                                            # the byte 0x18 is not a member
        self.assertEqual(g.run("0791:278A", [off, g.ds, 1], answers=[64])["ax"], 20)
        g.ds_poke(0x8327, b"\x03")
        self.assertEqual(g.run("0791:278A", [off, g.ds, 1], answers=[64], variant="keeper-gate-off")["ax"], 20)

    def test_skill_draw_passes_asks_278a_and_draws_against_n(self):
        g, off = self.skill_rig()
        g.ds_poke(0xA978, bytes([0x62, 0x7B, g.ds & 0xFF, g.ds >> 8]))
        for seed, skill in ((0x1234, 64), (0, 0), (0xFFFF, 100)):
            g.ds_poke(0x7B62, seed.to_bytes(2, "little"))
            n = skill // 32 + 1
            new = (seed * 0x7ABD + 0x1B0F) & 0xFFFF
            draw = ((new * n) >> 16) + 1
            regs = g.run("0791:287C", [off, g.ds, 7], answers=[skill], dx=0x55)
            self.assertEqual(g.calls, [("0791:278A", (7, g.ds, off), "0791:288E", True)])
            self.assertEqual(regs["ax"], (draw & 0xFF00) | (0 if draw == 1 else 1))
            self.assertEqual(regs["dx"], draw)
            self.assertEqual(g.ds_peek(0x7B62, 2), new.to_bytes(2, "little"))

    def test_energy_gate_chance_draws_against_0x21_minus_energy(self):
        g = Geo()
        g.ds_poke(0xA978, bytes([0x62, 0x7B, g.ds & 0xFF, g.ds >> 8]))
        off = g.set_rec(3, player=2)
        for energy in (10, 0xF6, 0):
            g.set_player(2, bE=energy)
            g.ds_poke(0x7B62, (0x4321).to_bytes(2, "little"))
            n = (0x21 - (energy - 256 if energy > 127 else energy)) & 0xFFFF
            new = (0x4321 * 0x7ABD + 0x1B0F) & 0xFFFF
            draw = ((new * n) >> 16) + 1
            regs = g.run("0791:2B7B", [off, g.ds])
            self.assertEqual(regs["dx"], draw)
            self.assertEqual(regs["ax"] & 0xFF, 1 if draw == 1 else 0)


class StackResidue(unittest.TestCase):
    """The stack bytes the frames leave below the entry SP (E = 0x2000; the caller's BP is 0x1111 here): the memory digests
    of a match include the stack segment."""

    def word(self, g, offset):
        return int.from_bytes(g.mem.memory[0x2000 + offset:0x2000 + offset + 2], "little")

    def test_advance_wrap_uses_side_one_table_entry_and_literal_pushes(self):
        g = Geo()
        # For slot11, 2996 returns1: DS:0669 is the base0, not the byte
        # before the table. Distinct adjacent memory exposes a reversed index.
        g.ds_poke(0x667, b"\x40")
        g.ball(11)
        g.run("0791:2A15", answers=[1, 0])
        self.assertEqual(g.ds_peek(0x830B), b"\x02")
        # The final four arguments sit below the initial BP and pointer pair.
        self.assertEqual([self.word(g, off) for off in (-8, -10, -12, -14, -16)],
                         [2, 11, 1, g.mem.seg(0x791), 0x2A67])

    def test_a_leaf_frame(self):
        g = Geo()
        g.ball(5)
        g.run("0791:2996", ax=0x4400)
        self.assertEqual(self.word(g, -2), 0x1111, "push bp")
        self.assertEqual(g.mem.memory[0x2000 - 3], 1, "[bp-1] = AL")

    def test_nested_frames_down_to_2974(self):
        g = Geo()
        g.ds_poke(0x8319, bytes([0x10]))
        g.ds_poke(0x831B, (0x20).to_bytes(2, "little"))
        off = g.set_rec(2, slot_byte=2, y=5)
        g.run("0791:2C54", [off, g.ds])
        cs = g.mem.seg(0x791)
        # 2C54: bp, then (seg, off, cs, 2C63) for 2BE5, whose frame: bp, the flag word, (seg, off, cs, 2C13) for 2974, bp
        self.assertEqual([self.word(g, o) for o in (-2, -6, -8, -10, -12, -14, -20, -22, -24, -26, -28)],
                         [0x1111, g.ds, off, cs, 0x2C63, 0x1FFE, g.ds, off, cs, 0x2C13, 0x1FF2])
        self.assertEqual(self.word(g, -18) & 0xFF, 1, "the pushed flag word: AL = 1 (0x20 > 0x10)")

    def test_278a_locals(self):
        g = Geo()
        off = g.set_rec(3, slot_byte=3, player=2, b11=0x22)
        g.set_player(2, bC=5, bE=10)
        g.ds_poke(0x80FC, bytes([1]))
        g.run("0791:278A", [off, g.ds, 3], answers=[64])
        bp = 0x2000 - 2
        loc = lambda o: int.from_bytes(g.mem.memory[bp + o:bp + o + 2], "little")
        self.assertEqual((loc(-6), loc(-4), loc(-2)), (64, 21, 21), "[bp-6] the skill, [bp-4] and [bp-2] the value")
        self.assertEqual(loc(-8), S, "[bp-8] the player record's segment")


class Registry(unittest.TestCase):
    def test_the_row(self):
        reg = port._module_registry("geometry")
        self.assertEqual(len(reg.entries), 32)
        self.assertEqual({a.split(":")[0] for a in reg.entries}, {"0791"})
        for address in ("0791:278A", "0791:287C", "0791:2956", "0791:26D7"):
            self.assertEqual((reg.entries[address].far, reg.entries[address].pop), (True, 6 if address != "0791:2956" else 4))
        for address in ("0791:261A", "0791:2996", "0791:29B3"):
            self.assertEqual((reg.entries[address].far, reg.entries[address].pop), (False, 0))


def _image_available():
    if os.environ.get("T60_NO_FUZZ"):             # the mutation check (out/T60/mutations.py) runs the hand-worked tests only
        return False
    try:
        import unicorn  # noqa: F401
    except ImportError:
        return False
    return (ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav").is_file()


@unittest.skipUnless(_image_available(), "needs unicorn and the reference image in .cache/dl")
class FuzzAgainstOriginal(unittest.TestCase):
    def test_every_port_equals_the_original(self):
        sys.path.insert(0, str(ROOT / "experiments" / "E036-match-port" / "out" / "T60"))
        import contextlib
        import io
        import fuzz
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            failed = fuzz.fuzz("geometry", sorted(port._module_registry("geometry").entries), 20, "unit", False,
                               str(ROOT / ".cache" / "dl"), False, None, 1)
        self.assertEqual(failed, 0, out.getvalue())


if __name__ == "__main__":
    unittest.main()
