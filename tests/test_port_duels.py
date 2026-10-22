"""T66: the branches of the duels port that ALL does not reach, run on synthetic memory with the listing's values (an own
goal in record_goal 6443, the eleventh goal's cap on DS:80F0, a goal taken back in goal_scored 67B6), each with its
reached twin; and the score writes named as the listing's 685C and 68B3. No byte of the original."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port
from original_match.port.mem import PlainMem

SEG, OFF = 0x4000, 0x0123            # the pitch record a far pointer names
PSEG, POFF = 0x4800, 0x0010          # the players' table (DS:A91B)
SQSEG, SQOFF = 0x4A00, 0x0020        # the squads (DS:A917)
PARENT, GRANDPARENT = 0x3100, 0x3200


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
        self.ss16(GRANDPARENT + 6, OFF)
        self.ss16(GRANDPARENT + 8, SEG)
        self.ss16(PARENT + 4, GRANDPARENT)
        self.ss16(PARENT + 6, OFF)
        self.ss16(PARENT + 8, SEG)
        ds = self.mem.DS * 16
        lin = {self.mem.lin(f"0791:{a:04X}"): f"0791:{a:04X}" for a in range(0x5B36, 0x68EA)}

        def watch(address, size, value, at):
            self.writes.append((address - ds, size, value, lin.get(at, at)))
        self.mem.listeners.append((ds, ds + 0xFFFF, watch))

    def ds8(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off] = value & 0xFF

    def ds16(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off:self.mem.DS * 16 + off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def ss16(self, off, value):
        self.mem.memory[off:off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def run(self, address, words=(), answer=None):
        entry = port._module_registry("duels").entries[address]
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

    def score_writes(self):
        return [(off, value, at) for off, size, value, at in self.writes if off in (0x9B3C, 0x9B3D)]


def answers(table):
    """A responder from {target: value or [values in order]}; an unlisted target answers 0."""
    queues = {k: (list(v) if isinstance(v, list) else v) for k, v in table.items()}

    def answer(request, mem):
        v = queues.get(request.target, 0)
        return v.pop(0) if isinstance(v, list) else v
    return answer


def goal_rig(own_goal=False, count=0, side=1):
    """record_goal's world: slot 5 of side `side` scores at minute 33; DS:7920 = (-1, +1) as the original's."""
    r = Rig()
    r.ds8(0x7920, 0xFF)
    r.ds8(0x7921, 0x01)
    r.ds8(0x7C39, 1 if own_goal else 0)
    rec = 0x80E8 + 5 * 0x16
    r.ds16(rec + 0xD, 7)                                   # the scorer's player number
    r.ds16(0x9B34 + 2 * side, 2)                           # the side's squad (DS:9B34 + 2 * side)
    r.ds16(0x9B34 + 2 * (1 - side), 3)
    for squad, base in ((2, 0x100), (3, 0x200)):          # each squad's player words at +2 * k - 2 (6566)
        for k in range(1, 12):
            lin = SQSEG * 16 + SQOFF + squad * 0xBF + 2 * k - 2
            r.mem.memory[lin:lin + 2] = (base + k).to_bytes(2, "little")
    r.ds8(0x80F0 + side, count)
    r.ds8(0x80F0 + 1 - side, count)
    return r, rec


class RecordGoal(unittest.TestCase):
    def test_own_goal_line_0x27_other_side_credited_no_scorer_goal(self):
        """645D-646A, 64E7-64FA, 6588, 6590: an own goal (DS:7C39 set) says 0x27, gives the scorer no goal and no top
        scorer, takes his form down by DS:7920[0] (-1), credits the count of the other side, marks the row's minute
        +0x80 and skips 3C20."""
        r, rec = goal_rig(own_goal=True, side=1)
        r.run("0791:6443", [33, 5, 1], answers({"0791:2BB1": 4}))
        self.assertEqual(r.targets(), [("0791:2AA3", "0791:646A"), ("0791:7CC5", "0791:64E1"),
                                       ("0791:2BB1", "0791:6547")])
        self.assertEqual(r.calls[0][1][0] & 0xFF, 0x27)
        self.assertEqual(r.calls[1][1], (0xFFFF, 0xFF01, r.mem.DS, rec))
        self.assertEqual(r.mem.u16(PSEG * 16 + POFF + 7 * 0x14 + 0xA), 0)          # no goal for the scorer
        self.assertEqual(r.mem.ds8(0x80F1), 0)
        self.assertEqual(r.mem.ds8(0x80F0), 1)                                      # 6510: side 0 credited
        self.assertEqual(r.mem.u8(0x2FFE + 8), 0)                                   # 64FA: the argument reversed
        row = 0x7BD1 + 0x21 * 0 + 3 * 1
        self.assertEqual(r.mem.ds16(row), 0x100 + 4)                                # squad of the scorer's side
        self.assertEqual(r.mem.ds8(row + 2), 33 + 0x80)                             # 6576, 6588

    def test_goal_of_the_scorers_side(self):
        """The reached twin: line 0x26, the scorer's goals +1 (6484), 5A03 then B3B7, form +1 (DS:7920[1]), the count
        of his side +1, the row with the plain minute, 3C20(side)."""
        r, rec = goal_rig(side=1)
        r.ds16(0x7C2A, 0x0044)
        r.ds16(0x7C2C, 0x5000)
        r.mem.memory[SQSEG * 16 + SQOFF + 2 * 0xBF + 0x2C] = 9            # the competition of squad 2
        r.run("0791:6443", [33, 5, 1], answers({"1771:5A03": 1, "0791:2BB1": 4}))
        self.assertEqual(r.targets(), [("0791:2AA3", "0791:6472"), ("1771:5A03", "0791:6493"),
                                       ("0791:B3B7", "0791:64BF"), ("0791:7CC5", "0791:64E1"),
                                       ("0791:2BB1", "0791:6547"), ("0791:3C20", "0791:659E")])
        self.assertEqual(r.calls[1][1], (0x5000, 0x0044))
        self.assertEqual(r.calls[2][1], (7, 9))
        self.assertEqual(r.calls[3][1], (1, 1, r.mem.DS, rec))
        self.assertEqual(r.calls[5][1][0] & 0xFF, 1)
        self.assertEqual(r.mem.u16(PSEG * 16 + POFF + 7 * 0x14 + 0xA), 1)
        self.assertEqual(r.mem.ds8(0x80F1), 1)
        row = 0x7BD1 + 0x21 * 1 + 3 * 1
        self.assertEqual(r.mem.ds16(row), 0x100 + 4)
        self.assertEqual(r.mem.ds8(row + 2), 33)

    def test_eleventh_goal_cap(self):
        """6503-6508: with DS:80F0 + side at 11 the count stays (no write at 6510) and the row written is the
        eleventh's again (DS:7BD1 + 0x21 * side + 3 * 11)."""
        r, rec = goal_rig(count=11, side=0)
        r.run("0791:6443", [70, 5, 0], answers({"0791:2BB1": 2}))
        self.assertEqual(r.mem.ds8(0x80F0), 11)
        self.assertFalse([w for w in r.writes if w[3] == "0791:6510"])
        row = 0x7BD1 + 3 * 11
        self.assertEqual(r.mem.ds16(row), 0x100 + 2)
        self.assertEqual(r.mem.ds8(row + 2), 70)

    def test_tenth_goal_counts(self):
        """The reached twin: below 11 the count grows (6510)."""
        r, rec = goal_rig(count=10, side=0)
        r.run("0791:6443", [70, 5, 0], answers({"0791:2BB1": 2}))
        self.assertEqual(r.mem.ds8(0x80F0), 11)
        self.assertEqual([w[2] for w in r.writes if w[3] == "0791:6510"], [11])


def scored_rig(offside):
    r = Rig()
    r.ds8(0x7920, 0xFF)
    r.ds8(0x7921, 0x01)
    r.ds8(0x668 + 0, 0)
    r.ds8(0x668 + 1, 11)
    r.ds8(0x830E, 9 if offside else 0)
    r.ds8(0x830B, 9)
    r.ds16(0x831F, 61)
    r.ds8(0x9B3C, 2)
    r.ds8(0x9B3D, 1)
    return r


class GoalScored(unittest.TestCase):
    def test_goal_taken_back(self):
        """6879-68C3: with DS:830E set the line is said, the score goes up at 685C and back down at 68B3, 82EB and the
        board follow; no record_goal, no after_goal, no replay flag."""
        r = scored_rig(offside=True)
        r.run("0791:67B6", [PARENT], answers({"0791:2996": 1, "214B:06FA": 1}))
        self.assertEqual(r.targets(), [
            ("214B:2031", "0791:67CC"), ("214B:2031", "0791:67DC"), ("0791:2996", "0791:67F8"),
            ("214B:06FA", "0791:6838"), ("0791:2B28", "0791:6848"), ("0791:0712", "0791:6869"),
            ("0791:2AA3", "0791:68AD"), ("0791:82EB", "0791:68BA"), ("0791:0712", "0791:68C3")])
        self.assertEqual(r.score_writes(), [(0x9B3D, 2, "0791:685C"), (0x9B3D, 1, "0791:68B3")])
        self.assertEqual(r.calls[6][1][0] & 0xFF, 0x26)
        self.assertEqual(r.mem.ds8(0x7C37), 0)

    def test_goal_stands(self):
        """The reached twin: DS:830E clear: record_goal(side of DS:830B's record, DS:830B, the minute), after_goal, the
        replay flag DS:7C37; one score write, at 685C."""
        r = scored_rig(offside=False)
        r.run("0791:67B6", [PARENT], answers({"0791:2996": 1, "214B:06FA": 0, "0791:2974": 1}))
        self.assertEqual(r.targets()[4:], [
            ("0791:2B28", "0791:6856"), ("0791:0712", "0791:6869"), ("0791:2974", "0791:6896"),
            ("0791:6443", "0791:68A4"), ("0791:65FE", "0791:68C8")])
        self.assertEqual(r.calls[4][1][1:], (r.mem.DS, 0x80E8 + (0 + 1) * 0x16))   # the other side's first slot
        self.assertEqual(r.calls[4][1][0] & 0xFF, 0x25)
        self.assertEqual(r.calls[7][1], (1, 9, 61))
        self.assertEqual(r.score_writes(), [(0x9B3D, 2, "0791:685C")])
        self.assertEqual(r.mem.ds8(0x7C37), 1)


if __name__ == "__main__":
    unittest.main()
