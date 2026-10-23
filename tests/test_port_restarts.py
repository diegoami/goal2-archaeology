"""T67: the branches of the restarts port that no match of ALL reaches (out/T67/coverage-summary.tsv: 6DCB, 7754, 7779,
78A7, 78FD, 7A89 and 7B12 are executed 0 times in the 62 matches), run on synthetic memory with the listing's values,
each with a reached twin; and the booking's statistics write, which the kit reads as its booking event only when its
writer is 7A01 (match.py WRITERS). No byte of the original."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "runtime"))
from original_match import port
from original_match.port.mem import PlainMem

SEG, OFF = 0x4000, 0x0123            # the pitch record a far pointer names
PSEG, POFF = 0x4800, 0x0010          # the players' table (DS:A91B)
SQSEG, SQOFF = 0x4A00, 0x0020        # the squads (DS:A917)
FSEG, FOFF = 0x4C00, 0x0040          # the fixture (DS:A923): +0x3F the speed setting
ZF = 0x40


class KeyMem(PlainMem):
    """Plain memory with the kit's two key services (mem.keypressed, mem.read_key) answered and recorded."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.waiting = False
        self.polls, self.reads = [], []

    def _keypressed(self, site):
        self.polls.append(site)
        return self.waiting

    def _key(self, site):
        self.reads.append(site)
        self.waiting = False
        return 0x20


class Rig:
    def __init__(self):
        self.mem = KeyMem(bytearray(0x60000))
        self.mem.regs.update(ss=0, sp=0x3000, bp=0x1234, ds=self.mem.DS, eflags=0x202)
        self.calls = []
        self.writes = []             # (DS offset, size, value, writer 'SSSS:OOOO')
        self.ds16(0xA91B, POFF)
        self.ds16(0xA91D, PSEG)
        self.ds16(0xA917, SQOFF)
        self.ds16(0xA919, SQSEG)
        self.ds16(0xA923, FOFF)
        self.ds16(0xA925, FSEG)
        self.ds8(0x7920, 0xFF)       # the two signed steps, as the original's
        self.ds8(0x7921, 0x01)
        ds = self.mem.DS * 16
        lin = {self.mem.lin(f"0791:{a:04X}"): f"0791:{a:04X}" for a in range(0x6900, 0x7B22)}
        self.all_writes = []

        def watch(address, size, value, at):
            self.all_writes.append((address, size, value, lin.get(at, at)))
            if ds <= address <= ds + 0xFFFF:
                self.writes.append((address - ds, size, value, lin.get(at, at)))
        self.mem.listeners.append((0, len(self.mem.memory), watch))

    def ds8(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off] = value & 0xFF

    def ds16(self, off, value):
        self.mem.memory[self.mem.DS * 16 + off:self.mem.DS * 16 + off + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def lin8(self, lin, value):
        self.mem.memory[lin] = value & 0xFF

    def lin16(self, lin, value):
        self.mem.memory[lin:lin + 2] = (value & 0xFFFF).to_bytes(2, "little")

    def run(self, address, words=(), answer=None):
        entry = port._module_registry("restarts").entries[address]
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

    def written(self, writer):
        return [(off, size, value) for off, size, value, at in self.writes if at == writer]

    def record8(self, k):
        return self.mem.u8(SEG * 16 + OFF + k)


def answers(table, zero_flag=None):
    """A responder from {target: value or [values in order]} (an unlisted target answers 0); zero_flag: {target: ZF
    the callee leaves} (23E4:08DF answers in ZF)."""
    queues = {k: (list(v) if isinstance(v, list) else v) for k, v in table.items()}

    def answer(request, mem):
        if zero_flag and request.target in zero_flag:
            f = mem.regs.get("eflags", 0x202)
            mem.regs["eflags"] = (f | ZF) if zero_flag[request.target] else (f & ~ZF)
        v = queues.get(request.target, 0)
        return v.pop(0) if isinstance(v, list) else v
    return answer


# -- 6D4E: the taker's slot ----------------------------------------------------------------------------------------
def taker_rig(side=1):
    r = Rig()
    r.ds16(0x9B34 + 2 * side, 5)                       # the side's squad
    r.ds8(0x668 + side, 11)                            # the side's first slot - 1
    r.ds8(0x8311 + side, 17)                           # the side's nearest
    return r


class PickDeadBallTaker(unittest.TestCase):
    def test_pick_not_in_the_eleven_goes_to_the_nearest(self):
        """6DB1-6DD7: the managed side's pick (CC7B) is kept at DS:9976 + 10 side + 2 role (6D8A); when 6B65 does not find
        it among the eleven (0xC) the side's nearest DS:8311[side] takes the restart: 6BF1(17, kind)."""
        r = taker_rig(side=1)
        r.run("0791:6D4E", [9, 2, 1], answers({"1771:0B77": 1, "0791:CC7B": 0x0123, "0791:6B65": 0xC}))
        self.assertEqual(r.targets(), [("1771:0B77", "0791:6D65"), ("0791:CC7B", "0791:6D74"),
                                       ("0791:6B65", "0791:6DAE"), ("0791:6BF1", "0791:6DE4")])
        self.assertEqual(r.calls[0][1], (5,))
        self.assertEqual([a & 0xFF for a in r.calls[1][1]], [1, 2])               # CC7B(side, role)
        self.assertEqual(r.written("0791:6D8A"), [(0x9976 + 10 + 4, 2, 0x0123)])
        self.assertEqual(r.calls[3][1][0], 17)
        self.assertEqual(r.calls[3][1][1] & 0xFF, 9)
        self.assertEqual(r.mem.u16(0x3000 - 2 - 2), 17)                            # the local [bp - 2]

    def test_pick_in_the_eleven(self):
        """The reached twin: 6B65 finds the pick at squad index 4: the slot DS:0668[side] + 4 (6DB7-6DC6)."""
        r = taker_rig(side=1)
        r.run("0791:6D4E", [9, 2, 1], answers({"1771:0B77": 1, "0791:CC7B": 0x0123, "0791:6B65": 4}))
        self.assertEqual(r.calls[3][1][0], 11 + 4)

    def test_computer_side_asks_1fdd(self):
        """6D90-6DA1: an unmanaged side's taker: 1FDD(side, DS:0764[role], role), nothing written at 6D8A."""
        r = taker_rig(side=0)
        r.ds8(0x764 + 5, 0x33)
        r.run("0791:6D4E", [8, 5, 0], answers({"1771:0B77": 0, "0791:6B65": 2}))
        self.assertEqual(r.targets()[1], ("0791:1FDD", "0791:6DA4"))
        self.assertEqual([a & 0xFF for a in r.calls[1][1]], [0, 0x33, 5])
        self.assertEqual(r.written("0791:6D8A"), [])


class TakerSquadIndex(unittest.TestCase):
    def squad(self, r, side, words):
        r.ds16(0x9B34 + 2 * side, 3)
        base = SQSEG * 16 + SQOFF + 3 * 0xBF
        for k, w in enumerate(words, 1):
            r.lin16(base + 2 * k - 2, w)

    def test_none_of_the_eleven_is_0xc(self):
        """6B8D-6BC2: no squad word 1..11 is the pick: the loop ends at 0xC and returns it."""
        r = Rig()
        self.squad(r, 1, [0x100 + k for k in range(1, 12)])
        r.ds16(0x9976 + 10 + 2 * 3, 0x200)
        self.assertEqual(r.run("0791:6B65", [3, 1]) & 0xFFFF, 0xC)

    def test_the_pick_is_found(self):
        r = Rig()
        self.squad(r, 1, [0x100 + k for k in range(1, 12)])
        r.ds16(0x9976 + 10 + 2 * 3, 0x104)
        self.assertEqual(r.run("0791:6B65", [3, 1]) & 0xFFFF, 4)


# -- 7621: a free kick's wall --------------------------------------------------------------------------------------
def wall_rig(x, y):
    r = Rig()
    r.ds8(0x830B, 3)
    r.mem.memory[SEG * 16 + OFF + 6] = 14                # the record's slot, not the holder's
    r.ds8(0x8315, x)
    r.ds8(0x8316, y)
    return r


def wall_answers(sign):
    return answers({"0791:2B51": 0, "0791:2BE5": sign, "0791:2BB1": 9, "0791:2CC5": 0},
                   zero_flag={"23E4:08DF": False})


class FreeKickWall(unittest.TestCase):
    def test_far_spot_positive_axes(self):
        """7745-77A1 with DS:8315 >= 0 (7754) and DS:8316 >= 0 (7779): x := DS:7920[0] * 3 + x = 2, y := ((|y| - 26) / 2
        + 0x1C) * DS:7920[0] = -33; then +8 := 1 * (2BB1 - 7) + y (77C5), +7 := 0 * (2BB1 - 7) + x (77EA)."""
        r = wall_rig(5, 0x24)
        r.run("0791:7621", [OFF, SEG], wall_answers(1))
        self.assertEqual(r.targets(), [("0791:2B51", "0791:7644"), ("0791:2BE5", "0791:7661"),
                                       ("0791:2BB1", "0791:769A"), ("23E4:08DF", "0791:76A5"),
                                       ("0791:2BB1", "0791:77AD"), ("0791:2BB1", "0791:77D2"),
                                       ("0791:2CC5", "0791:77F7")])
        self.assertEqual(r.record8(8), (2 - 33) & 0xFF)
        self.assertEqual(r.record8(7), 2)
        frame = 0x3000 - 2                                  # 7621's BP: [bp - 4] .. [bp - 1]
        self.assertEqual([r.mem.u8(frame + k) for k in (-4, -3, -2, -1)], [0, 1, 2, (-33) & 0xFF])

    def test_far_spot_negative_axes(self):
        """The reached twin (7758, 777D): DS:8315 < 0 and DS:8316 < 0 take DS:7920[1] = +1: x = 3 - 5, y = 33."""
        r = wall_rig(-5, -0x24)
        r.run("0791:7621", [OFF, SEG], wall_answers(-1))
        self.assertEqual(r.record8(8), 2 + 33)
        self.assertEqual(r.record8(7), (-2) & 0xFF)


# -- 7881: the walk-off --------------------------------------------------------------------------------------------
def walk_rig(at_off_point=False, quick=False):
    r = Rig()
    r.ds16(0x640, 0x7F7F)
    r.ds16(0x642, 0x2A00)
    rec = 0x80E8 + 0x16 * 4
    r.ds16(rec, 0x7F7F if at_off_point else 0x1005)
    r.ds8(0x8325, 1)
    r.ds8(0x9B41, 7)
    r.ds8(0x9A3E, 1 if quick else 0)
    r.lin8(FSEG * 16 + FOFF + 0x3F, 0)                # the speed setting 0: 214B:1E09(2)
    return r, rec


class WalkPlayerOff(unittest.TestCase):
    def test_already_off_the_pitch(self):
        """78A1-78A7: the record's point is DS:0640 already: nothing written, nothing called."""
        r, rec = walk_rig(at_off_point=True)
        r.run("0791:7881", [4], answers({"0791:2CC5": 1}))       # (a walk would end at once)
        self.assertEqual(r.calls, [])
        self.assertEqual([w for w in r.writes if w[3].startswith("0791:")], [])

    def test_quick_match_no_passes(self):
        """The twin past 78A7 (DS:9A3E set): state 0xC, destination DS:0642, the flags kept and put back, the point
        DS:0640 and state 0, with no pass and no picture."""
        r, rec = walk_rig(quick=True)
        r.run("0791:7881", [4])
        self.assertEqual(r.calls, [])
        self.assertEqual(r.written("0791:78B2"), [(rec + 0x12, 1, 0xC)])
        self.assertEqual(r.written("0791:78BD"), [(rec + 7, 2, 0x2A00)])
        self.assertEqual(r.written("0791:78C7"), [(0x8325, 1, 0)])
        self.assertEqual(r.written("0791:7960"), [(0x8325, 1, 1)])
        self.assertEqual(r.written("0791:795A"), [(0x9B41, 1, 7)])
        self.assertEqual(r.written("0791:796C"), [(rec, 2, 0x7F7F)])
        self.assertEqual(r.written("0791:7982"), [(rec + 0x12, 1, 0)])

    def test_a_key_waiting_is_read_at_7902(self):
        """78F9-78FD: with a key waiting at the poll the walk-off reads it (214B:08DD returning to 7902), as the kit's
        logic answers that site; the far call's return address is left below SP."""
        r, rec = walk_rig()
        r.mem.waiting = True
        r.run("0791:7881", [4], answers({"0791:2CC5": 1}))
        self.assertEqual(r.mem.polls, ["0791:78F9"] * 22)
        self.assertEqual(r.mem.reads, ["0791:7902"])
        self.assertEqual(r.targets()[:4], [("0791:8AE9", "0791:78E7"), ("0791:94E8", "0791:78F4"),
                                           ("214B:1E09", "0791:7916"), ("0791:8537", "0791:7940")])

    def test_no_key_no_read(self):
        """The reached twin: no key at the poll (the kit's answer for a walk-off): 22 polls, no read; the passes run
        until 2CC5, then the picture once more (797C) and state 0."""
        r, rec = walk_rig()
        r.run("0791:7881", [4], answers({"0791:2CC5": [0, 1]}))
        self.assertEqual(r.mem.polls, ["0791:78F9"] * 44)
        self.assertEqual(r.mem.reads, [])
        t = r.targets()
        self.assertEqual(t.count(("0791:8AE9", "0791:78E7")), 2)
        self.assertEqual(t[-1], ("0791:8537", "0791:797F"))
        self.assertEqual(r.written("0791:7982"), [(rec + 0x12, 1, 0)])


# -- 7A43: the cap ---------------------------------------------------------------------------------------------------
def cap_rig(side, lost):
    r = Rig()
    r.ds16(0x9B34 + 2 * side, 2)
    r.ds8(0x7B86 + 10 * side, lost[0])
    r.ds8(0x7B87 + 10 * side, lost[1])
    return r


class SideMayLoseAPlayer(unittest.TestCase):
    def test_managed_side_at_the_cap(self):
        """7A87-7A89: a managed side with sendings off + injuries = 3: 0."""
        r = cap_rig(1, (1, 2))
        self.assertEqual(r.run("0791:7A43", [1], answers({"1771:0B77": 1})) & 0xFF, 0)
        self.assertEqual(r.mem.u8(0x3000 - 2 - 1), 0)

    def test_managed_side_below_the_cap(self):
        """The reached twin: 2 lost: 1."""
        r = cap_rig(1, (1, 1))
        self.assertEqual(r.run("0791:7A43", [1], answers({"1771:0B77": 1})) & 0xFF, 1)

    def test_unmanaged_side_with_11_available(self):
        """7AE1-7B12: an unmanaged side with only 11 of its 20 squad words available (1771:3216 false): 0, though it has
        lost no one."""
        r = cap_rig(0, (0, 0))
        r.run("0791:7A43", [0], answers({"1771:0B77": 0, "1771:3216": [0] * 11 + [1] * 9}))
        self.assertEqual(r.targets().count(("1771:3216", "0791:7AD4")), 20)
        self.assertEqual(r.mem.u8(0x3000 - 2 - 1), 0)
        self.assertEqual(r.mem.u16(0x3000 - 2 - 5), 11)                           # the count [bp - 5]

    def test_unmanaged_side_with_12_available(self):
        """The reached twin: 12 available and none lost: 1."""
        r = cap_rig(0, (0, 0))
        value = r.run("0791:7A43", [0], answers({"1771:0B77": 0, "1771:3216": [0] * 12 + [1] * 8}))
        self.assertEqual(value & 0xFF, 1)


# -- 798D: the booking's event -------------------------------------------------------------------------------------
class Booking(unittest.TestCase):
    def test_the_bookings_count_is_written_by_7a01_once(self):
        """7A01: the side's bookings DS:7B85 + 10 side + 1, written as 7A01 (the kit's booking event, match.py WRITERS);
        DS:8321 + 1 below 5 (7A0C); the player's status +0x10 element 5 through 214B:0C79."""
        r = Rig()
        r.mem.memory[SEG * 16 + OFF + 0xD] = 7               # the player word
        r.ds8(0x7B85 + 10, 2)
        r.ds16(0x8321, 4)
        r.run("0791:798D", [OFF, SEG], answers({"0791:2974": 1, "1771:0B77": 1}))
        self.assertEqual(r.written("0791:7A01"), [(0x7B85 + 10, 1, 3)])
        self.assertEqual([w for w in r.writes if w[0] in range(0x7B7E, 0x7B92) and w[3] != "0791:7A01"], [])
        self.assertEqual(r.written("0791:7A0C"), [(0x8321, 2, 5)])
        c0c79 = [c for c in r.calls if c[0] == "214B:0C79"][0]
        self.assertEqual(c0c79[1], (5, PSEG, POFF + 7 * 0x14 + 0x10))
        self.assertNotIn("1771:33CD", [c[0] for c in r.calls])

    def test_the_tally_stops_at_5(self):
        """7A05: DS:8321 at 5 is not raised; an unmanaged side's player loses his own tactic (1771:33CD)."""
        r = Rig()
        r.mem.memory[SEG * 16 + OFF + 0xD] = 7
        r.ds16(0x8321, 5)
        r.run("0791:798D", [OFF, SEG], answers({"0791:2974": 0, "1771:0B77": 0}))
        self.assertEqual(r.written("0791:7A0C"), [])
        self.assertEqual(r.written("0791:7A01"), [(0x7B85, 1, 1)])
        self.assertEqual(r.targets()[-1], ("1771:33CD", "0791:7A3D"))


if __name__ == "__main__":
    unittest.main()
