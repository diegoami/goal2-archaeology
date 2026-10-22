"""T66: the branches of the duels port that no match of ALL reaches (out/T66/coverage-summary.tsv: 5B43/5B4A, 5B8F,
5BAD, 5C5A, 5CE3, 5D78, 5F66, 6141, 634A, 68D6 and the cap's jump 6508 -> 6514 are executed 0 times in the 62 matches),
run on synthetic memory with the listing's values, each with a reached twin; and the three the task names (an own goal
in record_goal 6443, the eleventh goal's cap on DS:80F0, a goal taken back in goal_scored 67B6), with the score writes
named as the listing's 685C and 68B3. No byte of the original."""
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


KEEPER = 0x80E8 + 12 * 0x16          # the holder's pitch record when DS:830B = 12


def keeper_rig(**ds):
    r = Rig()
    r.ds8(0x8325, 1)
    for k, v in ds.items():
        r.ds8(int(k[1:], 16), v)
    r.mem.memory[SEG * 16 + OFF + 6] = 1           # the keeper's slot
    return r


def by_ret(table):
    """A responder from {ret_to offset: value}; others answer 0."""
    def answer(request, mem):
        return table.get(request.ret_to[5:], 0)
    return answer


class KeeperAtBall(unittest.TestCase):
    def test_5b43_5b4a_nothing_with_8325_and_8324_clear(self):
        """5B3C-5B4A: with DS:8325 and DS:8324 both clear 5B36 returns at once."""
        r = keeper_rig(d8325=0)
        r.run("0791:5B36", [OFF, SEG])
        self.assertEqual(r.calls, [])
        r = keeper_rig(d8325=0, d8324=1)                 # 5B43's other way: 8324 set goes on (5B4D)
        r.run("0791:5B36", [OFF, SEG], by_ret({"5B56": 1}))
        self.assertEqual(r.targets()[0], ("0791:2B51", "0791:5B56"))

    def test_5b8f_5bad_moving_ball_duel_a_keeper_save(self):
        """5B88-5B8F, 5BAD-5BE6, 5C3E: in his strip with the ball moving (DS:8303) the line is 0x41; the holder's
        06B1(278A(holder, 4)) stays on the stack while the keeper's 06B1(2 * 278A(keeper, 1)) is drawn; larger: 5A8E."""
        r = keeper_rig(d830B=12, d8303=1)
        seen = []

        def answer(request, mem):
            if request.ret_to in ("0791:5BDB", "0791:5BE3"):
                seen.append(mem.u16(mem.ss_lin(mem.regs["sp"])))
            return {"5B7E": 1, "5BC7": 40, "5BCD": 9, "5BDB": 6, "5BE3": 10}.get(request.ret_to[5:], 0)
        r.run("0791:5B36", [OFF, SEG], answer)
        self.assertEqual(r.targets(), [
            ("0791:2B51", "0791:5B56"), ("0791:2EB8", "0791:5B7E"), ("0791:2B28", "0791:5BA6"),
            ("0791:278A", "0791:5BC7"), ("214B:06B1", "0791:5BCD"), ("0791:278A", "0791:5BDB"),
            ("214B:06B1", "0791:5BE3"), ("0791:5A8E", "0791:5C42")])
        self.assertEqual(r.calls[2][1][0] & 0xFF, 0x41)
        self.assertEqual(r.calls[3][1], (4, r.mem.DS, KEEPER))
        self.assertEqual(r.calls[4][1], (40,))
        self.assertEqual(r.calls[5][1], (1, SEG, OFF))
        self.assertEqual(r.calls[6][1], (12,))                     # 5BDB shl ax, 1
        self.assertEqual(seen, [9, 9])
        self.assertEqual(r.calls[7][1], (0x2FFE,))                 # push bp: 5B36's frame

    def test_5b95_still_ball_duel(self):
        """The reached twin of 5B8F/5BAD (5B95, 5BEF): ball still: line 0x0D, the holder's 278A(holder, 0xA) against
        278A(keeper, 1) + 1 (the template is not 0x0B)."""
        r = keeper_rig(d830B=12)
        r.run("0791:5B36", [OFF, SEG], by_ret({"5B7E": 1, "5C0F": 3, "5C1D": 6, "5C39": 2}))
        self.assertEqual(r.calls[2][1][0] & 0xFF, 0x0D)
        self.assertEqual(r.calls[3][0::2], ("0791:278A", "0791:5C09"))
        self.assertEqual(r.calls[3][1], (0xA, r.mem.DS, KEEPER))
        self.assertEqual(r.calls[6][1], (7,))
        self.assertEqual(r.targets()[7:], [("0791:4DA9", "0791:5C4D"), ("0791:2AA3", "0791:5C7C"),
                                           ("0791:4D3F", "0791:5C85")])

    def test_5c5a_foul_coin_to_8206(self):
        """5C51-5C67: the duel lost and 4DA9 true: the coin true calls 8206 with the keeper's slot byte."""
        r = keeper_rig(d830B=12)
        r.run("0791:5B36", [OFF, SEG], by_ret({"5B7E": 1, "5C0F": 9, "5C39": 1, "5C4D": 1, "5C56": 1}))
        self.assertEqual(r.targets()[-3:], [("0791:4DA9", "0791:5C4D"), ("214B:06FA", "0791:5C56"),
                                            ("0791:8206", "0791:5C67")])
        self.assertEqual(r.calls[-1][1], (1,))
        self.assertFalse(r.calls[-1][3])                           # a near call

    def test_5c69_foul_coin_false_saves(self):
        """The reached twin of 5C5A (5C69): the coin false is the save 5A8E."""
        r = keeper_rig(d830B=12)
        r.run("0791:5B36", [OFF, SEG], by_ret({"5B7E": 1, "5C0F": 9, "5C39": 1, "5C4D": 1, "5C56": 0}))
        self.assertEqual(r.targets()[-1], ("0791:5A8E", "0791:5C6D"))

    def test_5ce3_penalty_element_for_event_4(self):
        """5CC6-5D0C: a penalty (DS:8324) with random_is_one(3) true and DS:8327 = 4: the holder's 278A element is
        DS:0801 and BP-6 its half."""
        for event, table in ((4, 0x801), (3, 0x800)):          # 3: the reached twin (5CDF)
            r = keeper_rig(d830B=12, d8302=1, d8324=1, d8327=event)
            r.ds8(0x800, 5)
            r.ds8(0x801, 8)
            r.run("0791:5B36", [OFF, SEG], by_ret({"5CCF": 1, "5D05": 31}))
            self.assertEqual(r.calls[2], ("0791:278A", (r.mem.ds8(table), r.mem.DS, KEEPER), "0791:5D05", True))
            self.assertEqual(r.mem.u16(0x2FFE - 6), 15)            # 5D0C: 31 div 2
            self.assertEqual(r.mem.u16(0x2FFE - 4), 1)             # 5C8F

    def test_5d78_keeper_roll_negative_misses(self):
        """5D6F-5D78: the keeper's roll is sign-extended (cwd): a roll of 0x8000 is below the ball's long, the high
        words decide (jg not taken, jge not taken) and 5B36 ends; a positive larger roll is the reached twin (5D82)."""
        for roll, caught in ((0x8000, False), (0x0007, True)):
            r = keeper_rig(d830B=12, d8302=1)
            r.ds16(0x8300, 3)
            r.run("0791:5B36", [OFF, SEG], by_ret({"5D1E": 1, "5D42": 1, "5D4D": 5, "5D6F": roll}))
            rets = [ret for _, ret in r.targets()]
            self.assertEqual(rets[:7], ["0791:5B56", "0791:5CA4", "0791:5D1E", "0791:5D42", "0791:5D4D",
                                        "0791:5D69", "0791:5D6F"])
            self.assertEqual(len(rets) > 7, caught)


class Deflection(unittest.TestCase):
    def test_5f66_moving_ball_in_the_set_deflects_with_line_0x20(self):
        """5F2C-5F3A, 5F4F-5F6C: the ball moving and DS:8327 in the set at 0791:5EE6 (08DF leaves ZF clear): 5E41 on
        the record two frames up, line 0x20, then DS:8303 := the coin."""
        r = Rig()
        r.ds8(0x8303, 1)
        r.ds8(0x8327, 0x1E)

        def answer(request, mem):
            mem.regs["eflags"] = 0x202                              # ZF clear: a member
            return {"214B:06FA": 0}.get(request.target, 0)
        r.run("0791:5F06", [PARENT], answer)
        self.assertEqual(r.targets(), [
            ("0791:2B51", "0791:5F23"), ("23E4:08DF", "0791:5F3A"), ("0791:5E41", "0791:5F60"),
            ("0791:2AA3", "0791:5F6C"), ("214B:06FA", "0791:5F81")])
        self.assertEqual(r.calls[1][1][1:], (0x0791, 0x5EE6))
        self.assertEqual(r.calls[2][1], (SEG, OFF))
        self.assertEqual(r.calls[3][1][0] & 0xFF, 0x20)
        self.assertEqual(r.mem.ds8(0x8303), 0)

    def test_5f3c_moving_ball_not_in_the_set_goes_to_5eab(self):
        """The reached twin of 5F66 (5F3C): ZF set: 5EAB and nothing else."""
        r = Rig()
        r.ds8(0x8303, 1)

        def answer(request, mem):
            mem.regs["eflags"] = 0x242
            return 0
        r.run("0791:5F06", [PARENT], answer)
        self.assertEqual(r.targets()[-1], ("0791:5EAB", "0791:5F4D"))
        self.assertEqual(r.mem.ds8(0x8303), 1)


class OffBall(unittest.TestCase):
    def test_6141_holder_side_record_is_the_holder_line_0x19(self):
        """6131-6151: a loose ball (DS:8300 = 0) with 2B51 true and DS:830B the record's slot: line 0x19, then 869F."""
        for holder, template, ret in ((9, 0x19, "0791:6151"), (3, 0x23, "0791:6163")):    # 3: the reached twin
            r = Rig()
            r.ds8(0x8325, 1)
            r.ds8(0x830B, holder)
            r.mem.memory[SEG * 16 + OFF + 6] = 9
            r.run("0791:5F8A", [PARENT], by_ret({"5F9A": 1, "5FCF": 5, "612D": 1}))
            self.assertEqual(r.targets(), [
                ("0791:2B51", "0791:5F9A"), ("0791:835F", "0791:5FCF"), ("0791:2F28", "0791:6093"),
                ("0791:2B51", "0791:612D"), ("0791:2B28", ret), ("0791:869F", "0791:6182")])
            self.assertEqual(r.calls[4][1][0] & 0xFF, template)
            self.assertEqual(r.calls[4][1][1:], (SEG, OFF))
            self.assertEqual(r.mem.u8(PARENT - 1), 0)              # 5FDD: near (travel 5)


class KickOffKeeper(unittest.TestCase):
    def test_634a_keeper_holding_gives_the_ball_to_a_random_slot(self):
        """634A-6394: DS:830B a keeper slot (045D): the keeper's destination 2C86(+9), DS:830B := DS:0668[2996] +
        rand(10) + 1, 2A15; then in a quick match (DS:9A3E) the new holder's destination is his point."""
        r = Rig()
        r.ds8(0x830B, 12)
        r.ds16(KEEPER + 9, 0x0A0B)
        r.ds8(0x669, 11)
        r.ds8(0x9A3E, 1)
        new = 0x80E8 + (11 + 4 + 1) * 0x16
        r.ds16(new, 0x0506)
        seen = []

        def answer(request, mem):
            if request.ret_to == "0791:638D":
                seen.append(mem.u16(mem.ss_lin(mem.regs["sp"])))
            return {"6346": 1, "6370": 0x0304, "6377": 1, "638D": 4}.get(request.ret_to[5:], 0)
        r.run("0791:6337", [], answer)
        self.assertEqual(r.targets(), [
            ("0791:045D", "0791:6346"), ("0791:2C86", "0791:6370"), ("0791:2996", "0791:6377"),
            ("214B:06B1", "0791:638D"), ("0791:2A15", "0791:6397")])
        self.assertEqual(r.calls[1][1], (0x0A0B, r.mem.DS, KEEPER))
        self.assertEqual(r.mem.ds16(KEEPER + 7), 0x0304)
        self.assertEqual(r.calls[3][1], (0xA,))
        self.assertEqual(seen, [11])
        self.assertEqual(r.mem.ds8(0x830B), 16)
        self.assertEqual(r.mem.ds16(new + 7), 0x0506)

    def test_6397_outfield_holder_keeps_the_ball(self):
        """The reached twin of 634A (6397): 045D false: only the holder's destination."""
        r = Rig()
        r.ds8(0x830B, 7)
        r.ds8(0x9A3E, 1)
        rec = 0x80E8 + 7 * 0x16
        r.ds16(rec, 0x0102)
        r.run("0791:6337", [], by_ret({}))
        self.assertEqual(r.targets(), [("0791:045D", "0791:6346")])
        self.assertEqual(r.mem.ds16(rec + 7), 0x0102)


class ReplayFlag(unittest.TestCase):
    def test_68d6_with_0c20_set_the_flag_is_kept_in_the_fixture(self):
        """68D6-68E2: after a goal that stands with DS:0C20 set: DS:0C20 := 0, the fixture's +0x3F := DS:7C3C and no
        replay flag DS:7C37."""
        r = scored_rig(offside=False)
        r.ds8(0x0C20, 1)
        r.ds8(0x7C3C, 0x5A)
        r.ds16(0xA923, 0x0100)
        r.ds16(0xA925, 0x5200)
        r.run("0791:67B6", [PARENT], answers({"0791:2996": 1, "0791:2974": 1}))
        self.assertEqual(r.targets()[-1], ("0791:65FE", "0791:68C8"))
        self.assertEqual(r.mem.ds8(0x0C20), 0)
        self.assertEqual(r.mem.u8(0x5200 * 16 + 0x0100 + 0x3F), 0x5A)
        self.assertEqual(r.mem.ds8(0x7C37), 0)


if __name__ == "__main__":
    unittest.main()
