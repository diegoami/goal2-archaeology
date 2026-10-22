"""T65: the branches of the contests port no match of ALL reaches (out/T65/coverage-summary.tsv: 4F16, 5180, 5224 and
53AF are executed 0 times in the 62 matches), run on synthetic memory with the listing's values; and the holder's roll
4DA9 keeps live on the guest stack across two calls (4DFC-4E11). No byte of the original."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port
from original_match.port.mem import PlainMem

SEG, OFF = 0x4000, 0x0123            # the pitch record a far pointer names
PSEG, POFF = 0x4800, 0x0010          # the players' table (DS:A91B)
PARENT, GRANDPARENT = 0x3100, 0x3200  # frames of the nesting routines (57AC's, 5565's)


class Rig:
    def __init__(self):
        self.mem = PlainMem(bytearray(0x60000))
        self.mem.regs.update(ss=0, sp=0x3000, bp=0x1234, ds=self.mem.DS, eflags=0x202)
        self.calls = []
        self.ds16(0xA91B, POFF)
        self.ds16(0xA91D, PSEG)
        # 57AC's frame: its far pointer argument at bp+6; 5565's frame points to 57AC's through bp+4
        self.ss16(GRANDPARENT + 6, OFF)
        self.ss16(GRANDPARENT + 8, SEG)
        self.ss16(PARENT + 4, GRANDPARENT)
        self.ss16(PARENT + 6, OFF)
        self.ss16(PARENT + 8, SEG)

    def ds8(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off] = value & 0xFF

    def ds16(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off:self.mem.DS * 16 + off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def ss16(self, off, value):
        self.mem.memory[off:off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def rec8(self, k, value):
        self.mem.memory[SEG * 16 + OFF + k] = value & 0xFF

    def rec16(self, k, value):
        self.mem.memory[SEG * 16 + OFF + k:SEG * 16 + OFF + k + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def player(self, pid, position):
        self.rec16(0xD, pid)
        self.mem.memory[PSEG * 16 + POFF + pid * 0x14 + 6] = position

    def run(self, address, words=(), answer=None):
        entry = port._module_registry("contests").entries[address]
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
                    sent = answer(request, self.mem) if answer else 0
                    self.mem.regs["ax"] = sent & 0xFFFF
        finally:
            self.mem._entries.pop()
        return value

    def targets(self):
        return [(t, ret) for t, _, ret, _ in self.calls]


def answers(table):
    """A responder from {target: value or [values in order]}; an unlisted target answers 0."""
    queues = {k: (list(v) if isinstance(v, list) else v) for k, v in table.items()}

    def answer(request, mem):
        v = queues.get(request.target, 0)
        return v.pop(0) if isinstance(v, list) else v
    return answer


class HolderChoice(unittest.TestCase):
    def test_4f16_position_3_with_element_1_clear_passes(self):
        """4EE4-4F23: a position 3 or 4 holder with effective element 1 clear passes (3323 returning to 4F23)."""
        for position in (3, 4):
            r = Rig()
            r.player(7, position)
            r.rec8(0, 0)
            r.rec8(1, 0)                              # row 0: neither far forward nor deep (4E72, 4EBB)
            r.rec8(6, 9)
            r.run("0791:4E28", [PARENT], answers({"0791:261A": [5, 2], "0791:2BE5": 1, "0791:26D7": 0}))
            self.assertEqual(r.targets(), [
                ("0791:261A", "0791:4E4D"), ("0791:2BE5", "0791:4E5E"), ("0791:2BE5", "0791:4EA7"),
                ("0791:261A", "0791:4EC0"), ("0791:26D7", "0791:4EF5"), ("0791:3323", "0791:4F23")])
            self.assertEqual(r.calls[4][1], (1, SEG, OFF))
            self.assertEqual(r.calls[5][1:], ((SEG, OFF), "0791:4F23", True))
            # the holder's player record kept at BP-4 (4E44-4E47); 4E28's BP is 0x3000 - 2
            self.assertEqual(r.mem.u16(0x2FFE - 4), POFF + 7 * 0x14)
            self.assertEqual(r.mem.u16(0x2FFE - 2), PSEG)

    def test_4ef9_position_3_with_element_1_set_dribbles(self):
        """The reached twin of 4F16 (4EF9): element 1 set dribbles to the record's own slot (384C)."""
        r = Rig()
        r.player(7, 3)
        r.rec8(6, 9)
        r.run("0791:4E28", [PARENT], answers({"0791:261A": [5, 2], "0791:2BE5": 1, "0791:26D7": 1}))
        self.assertEqual(r.calls[-1], ("0791:384C", (9, SEG, OFF), "0791:4F14", True))


def _5049_answers(**extra):
    table = {"0791:2C29": 1, "0791:045D": 0, "0791:2C86": 0x0504}
    table.update(extra)
    return answers(table)


class HolderTurn(unittest.TestCase):
    def test_5180_moving_ball_attempt_is_a_header(self):
        """5179-518D: in 40BC's strip with 500C set and the ball moving (DS:8303), the holder heads (3EDF), then
        DS:8303 is cleared (51A6); 5049 returns 1."""
        r = Rig()
        r.ds8(0x8303, 1)
        r.ds16(0x646, 0x0203)
        r.rec8(6, 9)
        value = r.run("0791:5049", [PARENT], _5049_answers(**{"0791:40BC": 1, "0791:500C": 1}))
        self.assertEqual(r.targets(), [
            ("0791:2C29", "0791:505C"), ("0791:474D", "0791:5074"), ("0791:045D", "0791:5085"),
            ("0791:4354", "0791:510B"), ("0791:40BC", "0791:510E"), ("0791:2C86", "0791:5126"),
            ("0791:500C", "0791:5135"), ("0791:3EDF", "0791:518D")])
        self.assertEqual(r.calls[5][1], (0x0203, SEG, OFF))
        self.assertEqual(r.calls[6][1], (0x2FFE,))                 # push bp (5131): 5049's own frame
        self.assertEqual(r.calls[7][1], (SEG, OFF))
        self.assertEqual(r.mem.u16(SEG * 16 + OFF + 7), 0x0504)     # 512D
        self.assertEqual(r.mem.ds8(0x8303), 0)                      # 51A6
        self.assertEqual(value & 0xFF, 1)

    def test_518f_still_ball_attempt_is_a_shot_with_template_0x11(self):
        """The reached twin of 5180 (518F): with DS:8303 clear it shoots (3EC5) with AL = 0x11 over 500C's AH."""
        r = Rig()
        r.rec8(6, 9)
        r.run("0791:5049", [PARENT], _5049_answers(**{"0791:40BC": 1, "0791:500C": 0xAB01}))
        self.assertEqual(r.calls[-1], ("0791:3EC5", (0xAB11, SEG, OFF), "0791:519F", True))

    def test_5224_moving_ball_near_goal_with_2ef0_heads(self):
        """5202-5231: near goal (2F28) with the ball moving, 2EF0 of the record's own point true: header (3EDF), then
        DS:8303 is cleared (528A)."""
        r = Rig()
        r.ds8(0x8303, 1)
        r.rec16(0, 0x0A0B)
        r.rec8(6, 9)
        value = r.run("0791:5049", [PARENT], _5049_answers(**{"0791:40BC": 0, "0791:2F28": 1, "0791:2EF0": 1}))
        self.assertEqual(r.targets()[-3:], [
            ("0791:2F28", "0791:51BB"), ("0791:2EF0", "0791:5220"), ("0791:3EDF", "0791:5231")])
        self.assertEqual(r.calls[-2][1], (0x0A0B, SEG, OFF))
        self.assertEqual(r.mem.ds8(0x8303), 0)                      # 528A
        self.assertEqual(value & 0xFF, 1)

    def test_5233_moving_ball_near_goal_without_2ef0_shoots_on_its_chance(self):
        """The reached twin of 5224 (5233): 2EF0 false, the position's chance DS:07E5 + position (06D0) decides a
        shot with template 0x12."""
        r = Rig()
        r.ds8(0x8303, 1)
        r.player(7, 4)
        r.ds8(0x7E5 + 4, 6)
        r.rec8(6, 9)
        r.run("0791:5049", [PARENT], _5049_answers(**{"0791:40BC": 0, "0791:2F28": 1, "0791:2EF0": 0,
                                                       "214B:06D0": 1}))
        self.assertEqual(r.calls[-2], ("214B:06D0", (6,), "0791:525D", True))
        self.assertEqual(r.calls[-1][0::2], ("0791:3EC5", "0791:5271"))
        self.assertEqual(r.calls[-1][1][0] & 0xFF, 0x12)


class FoulOutcome(unittest.TestCase):
    def test_53af_keeper_holding_returns_at_once(self):
        """539F-53AF: when the holder (DS:830B) is a keeper slot (045D), nothing else is done."""
        r = Rig()
        r.ds8(0x830B, 12)
        r.run("0791:539F", [PARENT], answers({"0791:045D": 1}))
        self.assertEqual(r.calls, [("0791:045D", (12,), "0791:53AB", False)])

    def test_53b2_otherwise_4d3f_on_the_holder_record(self):
        """The reached twin of 53AF (53B2): 4D3F on the holder's pitch record, then the beep with DS:8303 clear."""
        r = Rig()
        r.ds8(0x830B, 3)
        r.run("0791:539F", [PARENT], answers({"0791:045D": 0, "214B:06FA": 1}))
        self.assertEqual(r.calls[1], ("0791:4D3F", (r.mem.DS, 0x80E8 + 3 * 0x16), "0791:53C8", True))
        self.assertEqual(r.calls[2], ("214B:1EA1", (0x64, 5), "0791:53DC", True))
        self.assertEqual(r.calls[4], ("0791:869F", (SEG, OFF), "0791:5416", True))   # two frames up (5408-540C)


class LiveStackWords(unittest.TestCase):
    def test_4dfc_holder_roll_stays_on_the_stack_across_two_calls(self):
        """4DFC pushes the holder's roll; it is the word at SP during 2FFB (4E09) and 06B1 (4E11), and 4E12 compares
        the challenger's roll with it: greater -> 1."""
        for challenger, expected in ((8, 1), (7, 0)):
            r = Rig()
            r.rec16(0xD, 0x55)
            seen = []

            def answer(request, mem, challenger=challenger):
                if request.ret_to in ("0791:4E09", "0791:4E11"):
                    seen.append(mem.u16(mem.ss_lin(mem.regs["sp"])))
                return {"1771:2FFB": 10, "214B:06D0": 1}.get(request.target, None) or (
                    7 if request.ret_to == "0791:4DFC" else challenger)
            value = r.run("0791:4DA9", [OFF, SEG], answer)
            self.assertEqual(seen, [7, 7])
            self.assertEqual(r.targets(), [
                ("1771:2FFB", "0791:4DBB"), ("214B:06D0", "0791:4DCA"), ("1771:2FFB", "0791:4DF4"),
                ("214B:06B1", "0791:4DFC"), ("1771:2FFB", "0791:4E09"), ("214B:06B1", "0791:4E11")])
            self.assertEqual(r.calls[1][1], (0x12 - 10,))
            self.assertEqual(value & 0xFF, expected)
            self.assertEqual(r.mem.u8(0x2FFE - 1), expected)          # BP-1 (4E1C); BP = 0x3000 - 2


if __name__ == "__main__":
    unittest.main()
