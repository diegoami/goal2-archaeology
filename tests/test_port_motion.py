"""runtime/original_match/port/motion.py (T62): row T62's ports on synthetic memory (no byte of the original).

The family ALL proves the branches it reaches (experiments/E036-match-port/notes/T62.md, the reach count); these tests
visit the branches it does not, and the edges a comment of the module asserts, on a PlainMem with the listing's
offsets and values. A port that calls the original is driven here by a fake callee per address (the call's target,
arguments, return address and far flag are asserted), the registers the listing hands it included."""
import inspect
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match.port import motion  # noqa: E402
from original_match.port.mem import PlainMem  # noqa: E402

SS, SP, BP = 0x3000, 0x0400, 0x0500
PIC_SEG, BACK_SEG = 0x5000, 0x6000         # where the synthetic DS:7C16 and DS:7C1E point
ZF = 0x40


class Machine:
    """A PlainMem with the stack of a call made, the writes recorded, and the port driven to its return."""

    def __init__(self):
        self.mem = PlainMem(bytearray(0x110000), load=0)
        self.DS = self.mem.DS
        self.writes = []
        self.mem.listeners.append((0, 0x10FFFF, lambda a, n, v, at: self.writes.append((a, n, v, at))))
        self.mem.set_reg("ds", self.DS)
        self.set_far(motion.PICTURE, 0, PIC_SEG)
        self.set_far(motion.BACKGROUND, 0, BACK_SEG)
        self.writes.clear()

    # -- memory --------------------------------------------------------------------------------------------
    def ds(self, off):
        return self.DS * 16 + off

    def put8(self, lin, v):
        self.mem.memory[lin] = v & 0xFF

    def put16(self, lin, v):
        self.mem.memory[lin:lin + 2] = (v & 0xFFFF).to_bytes(2, "little")

    def set_far(self, ds_off, off, seg):
        self.put16(self.ds(ds_off), off)
        self.put16(self.ds(ds_off) + 2, seg)

    def cell(self, seg, row, col):
        return seg * 16 + ((motion.s8(row) * 0xA0 + motion.s8(col) * 2 + motion.CELL) & 0xFFFF)

    def u8(self, lin):
        return self.mem.u8(lin)

    def u16(self, lin):
        return self.mem.u16(lin)

    def written_by(self, at):
        return [w for w in self.writes if w[3] == self.mem.lin(at)]

    # -- a call ------------------------------------------------------------------------------------------
    def run(self, fn, args, far=True, callees=None, variant=None, ax=0, dx=0):
        """args: the words pushed, in push order. callees: {target: fn(machine, call) -> AX}."""
        callees = callees or {}
        sp = SP
        for w in list(args) + ([0x9999] if far else []) + [0x1234]:
            sp -= 2
            self.put16(SS * 16 + sp, w)
        m = self.mem
        for r, v in (("ss", SS), ("sp", sp), ("bp", BP), ("ax", ax), ("dx", dx)):
            m.set_reg(r, v)
        self.entry_sp = sp
        self.calls = []
        m._entries.append((sp, far))
        try:
            value = fn(m, variant)
            if inspect.isgenerator(value):
                gen, sent = value, None
                while True:
                    try:
                        c = gen.send(sent)
                    except StopIteration as stop:
                        value = stop.value
                        break
                    self.calls.append(c)
                    if c.target not in callees:
                        raise AssertionError(f"an unexpected call of {c.target} (returning to {c.ret_to})")
                    sent = callees[c.target](self, c) & 0xFFFF
                    m.set_reg("ax", sent)
        finally:
            m._entries.pop()
        self.value = value
        return value

    def targets(self):
        return [c.target for c in self.calls]


def ret(ax, **regs):
    """A fake callee returning AX (and setting other registers as it returns)."""
    def fn(machine, c):
        for r, v in regs.items():
            machine.mem.set_reg(r, v)
        return ax
    return fn


REC = 0x9000          # a synthetic record in DS (a pitch record, the ball, a sprite: each test says which)


class BallTravel(unittest.TestCase):
    def test_the_long_product_is_handed_to_0279_with_the_listings_registers(self):
        t = Machine()
        t.put16(t.ds(REC) + 6, 0xFFFD)                    # vel_x -3
        t.put16(t.ds(REC) + 8, 2)
        t.put16(t.ds(REC) + 0xA, 4)
        seen = {}

        def mul(machine, c):
            seen.update({r: machine.mem.reg(r) for r in ("ax", "dx", "bx", "cx")})
            self.assertEqual((c.ret_to, c.far, c.args), ("0791:8396", True, ()))
            machine.mem.set_reg("dx", 0)
            return 20
        self.assertEqual(t.run(motion.ball_travel, [t.DS, REC], callees={"23E4:0279": mul}), 20)
        self.assertEqual(seen, {"ax": 4, "dx": 0, "bx": 0, "cx": 5})

    def test_neg_of_0x8000_stays_0x8000_and_the_sum_is_sign_extended(self):
        t = Machine()
        t.put16(t.ds(REC) + 6, 0x8000)                    # `neg ax` leaves 0x8000
        t.put16(t.ds(REC) + 8, 1)
        seen = {}
        t.run(motion.ball_travel, [t.DS, REC],
              callees={"23E4:0279": lambda m, c: seen.update(bx=m.mem.reg("bx"), cx=m.mem.reg("cx")) or 0})
        self.assertEqual(seen, {"cx": 0x8001, "bx": 0xFFFF})


class MoveBall(unittest.TestCase):
    """83A2 on the ball record (+0 x, +1 y, +6/+8 velocity, +0xA timer, +0xD in flight)."""

    def ball(self, t, x, y, vx=0, vy=0, timer=0, flight=0):
        b = t.ds(REC)
        t.put8(b, x), t.put8(b + 1, y), t.put16(b + 6, vx), t.put16(b + 8, vy)
        t.put16(b + 0xA, timer), t.put8(b + 0xD, flight)
        return b

    def callees(self, **extra):
        c = {"0791:835F": ret(3), "0791:2E00": ret(1), "0791:8F10": ret(0), "0791:2DCA": ret(0), "0791:0441": ret(0),
             "0791:2BE5": ret(1), "0791:82EB": ret(0), "0791:698E": ret(0), "0791:690C": ret(0),
             "0791:6E11": ret(0), "0791:6E6E": ret(0), "0791:2996": ret(0x5500), "0791:6F01": ret(0)}
        c.update(extra)
        return c

    def test_in_play_the_step_lands_and_the_timer_counts_down(self):
        t = Machine()
        b = self.ball(t, 2, 3, vx=0xFF, vy=1, timer=7, flight=1)
        t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:2DCA": ret(1)}))
        self.assertEqual((t.u8(b), t.u8(b + 1), t.u16(b + 0xA), t.u8(b + 0xD)), (1, 4, 6, 1))
        self.assertEqual(t.targets(), ["0791:835F", "0791:2E00", "0791:8F10", "0791:2DCA"])
        self.assertEqual(t.calls[1].args, (0x0401,))       # 2E00 gets the new position word

    def test_a_travel_of_two_lands_the_ball(self):
        t = Machine()
        b = self.ball(t, 0, 0, timer=0, flight=1)
        t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:835F": ret(2), "0791:2DCA": ret(1)}))
        self.assertEqual((t.u8(b + 0xD), t.u16(b + 0xA)), (0, 0))     # ja: 2 is not > 2; a zero timer stays
        self.assertEqual(t.written_by("0791:83D2"), [])

    def test_a_refused_square_keeps_the_ball(self):
        t = Machine()
        b = self.ball(t, 2, 3, vx=1, vy=1)
        t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:2E00": ret(0), "0791:2DCA": ret(1)}))
        self.assertEqual(t.u16(b), 0x0302)
        self.assertEqual(t.written_by("0791:840B"), [])

    def test_off_the_pitch_with_830E_set_and_x_beyond_1_calls_82EB_and_stops(self):
        t = Machine()
        b = self.ball(t, 0xFE, 0x26, timer=5)             # x -2
        t.put8(t.ds(0x830E), 1)
        t.put8(t.ds(0x830C), 9)
        t.run(motion.move_ball, [t.DS, REC], callees=self.callees())
        self.assertEqual(t.targets()[-2:], ["0791:0441", "0791:82EB"])
        self.assertEqual((t.u8(t.ds(0x830C)), t.u16(b + 0xA)), (9, 4))   # 8474 never reached: nothing cleared
        self.assertEqual(t.calls[-2].args, (2,))

    def test_off_the_pitch_with_830E_set_x_within_1_and_the_holder_on_the_ball_side_calls_82EB(self):
        t = Machine()
        self.ball(t, 1, 0xFE)                             # y -2
        t.put8(t.ds(0x830E), 1)
        t.put8(t.ds(0x830B), 3)
        t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:2BE5": ret(1)}))
        self.assertEqual(t.targets()[-2:], ["0791:2BE5", "0791:82EB"])
        di = (3 * 0x16 + 0x80E8)
        self.assertEqual(t.calls[-2].args, (t.DS, di))
        self.assertEqual(t.calls[-2].ret_to, "0791:845D")
        self.assertEqual((t.mem.reg("ax"), t.mem.reg("dx")), (0, 0xFFFF))  # 82EB's AX; the imul's DX (-2 * 1)

    def test_off_the_pitch_with_830E_set_x_within_1_and_the_other_side_falls_to_the_restarts(self):
        t = Machine()
        b = self.ball(t, 1, 2, timer=3)
        t.put8(t.ds(0x830E), 1)
        for a in (0x830C, 0x830A, 0x830D, 0x8325, 0x8327):
            t.put8(t.ds(a), 5)
        t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:2BE5": ret(1)}))
        self.assertEqual(t.targets()[-3:], ["0791:2BE5", "0791:2BE5", "0791:690C"])   # 2 * 1 >= 0: 690C
        self.assertEqual([t.u8(t.ds(a)) for a in (0x830C, 0x830A, 0x830D, 0x8325, 0x8327)], [0] * 5)
        self.assertEqual(t.u16(b + 0xA), 0)
        self.assertEqual(t.value, 0)

    def test_the_restart_by_end_and_side(self):
        # (x, y, 2BE5's AL) -> the restart: x within 1: 698E (y * dir < 0) or 690C; else y within 0x25: 6E11;
        # else 6E6E (y * dir < 0) or 6F01
        cases = [((0, 0xF0, 1), "0791:698E"), ((0xFF, 0x10, 1), "0791:690C"), ((5, 0x25, 1), "0791:6E11"),
                 ((5, 0xDB, 1), "0791:6E11"), ((5, 0x26, 0xFF), "0791:6E6E"), ((5, 0x26, 1), "0791:6F01"),
                 ((5, 0xDA, 1), "0791:6E6E")]
        for (x, y, d), restart in cases:
            t = Machine()
            self.ball(t, x, y)
            t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:2BE5": ret(d)}))
            self.assertEqual(t.targets()[-1], restart, (x, y, d))

    def test_the_goal_kick_or_free_kick_gets_the_side_with_2996s_high_byte(self):
        for al, side in ((0, 1), (1, 0)):
            t = Machine()
            self.ball(t, 5, 0x26)
            t.run(motion.move_ball, [t.DS, REC], callees=self.callees(**{"0791:2996": ret(0x5500 | al)}))
            c = t.calls[-1]
            self.assertEqual((c.target, c.args, c.ret_to, c.far), ("0791:6F01", (0x5500 | side, 0x5500), "0791:8523",
                                                                    False))


class PlayerSprite(unittest.TestCase):
    """8537 on a pitch record (+0 position, +2 old position, +4 glyph, +6 slot, +0xF run direction)."""

    def record(self, t, pos, old, glyph=0x0F41, slot=4, run=0):
        r = t.ds(REC)
        t.put16(r, pos), t.put16(r + 2, old), t.put16(r + 4, glyph), t.put8(r + 6, slot), t.put8(r + 0xF, run)
        t.put16(t.ds(motion.NO_POSITION), 0x7F7F)
        return r

    def callees(self, holder=0, keeper=0, area=0, d=1):
        return {"0791:2C29": ret(holder), "0791:045D": ret(keeper), "0791:2EB8": ret(area), "0791:2BE5": ret(d),
                "0791:8F10": ret(0)}

    def test_the_old_cell_is_restored_and_the_sprite_drawn(self):
        t = Machine()
        r = self.record(t, 0x0302, 0x0201)
        t.put16(t.cell(BACK_SEG, 1, 2), 0x0D2E)
        t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees())
        self.assertEqual(t.u16(t.cell(PIC_SEG, 1, 2)), 0x0D2E)
        self.assertEqual(t.u16(t.cell(PIC_SEG, 2, 3)), 0x0F41)
        self.assertEqual(t.u16(r + 2), 0x0302)
        self.assertEqual(t.targets(), ["0791:2C29"])

    def test_no_draw_variant_restores_the_old_cell_and_draws_nothing(self):
        t = Machine()
        self.record(t, 0x0302, 0x0201)
        t.put16(t.cell(BACK_SEG, 1, 2), 0x0D2E)
        t.put16(t.cell(PIC_SEG, 1, 2), 0x0F41)
        t.put16(t.cell(PIC_SEG, 2, 3), 0x0D2E)
        t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees(), variant="no-draw")
        self.assertEqual((t.u16(t.cell(PIC_SEG, 1, 2)), t.u16(t.cell(PIC_SEG, 2, 3))), (0x0D2E, 0x0D2E))

    def test_no_position_draws_nothing(self):
        t = Machine()
        r = self.record(t, 0x7F7F, 0x7F7F)
        t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees())
        self.assertEqual([w for w in t.writes if w[0] != r + 2 and w[0] < SS * 16], [])

    def test_the_holder_of_glyph_1_is_drawn_one_up(self):
        t = Machine()
        self.record(t, 0x0302, 0x0302, glyph=1, slot=4)
        t.put8(t.ds(0x830B), 4)
        t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees())
        self.assertEqual(t.u16(t.cell(PIC_SEG, 2, 3)), 2)

    def test_the_ball_follows_its_holder_by_the_run_direction_and_wraps_at_the_goal_lines(self):
        # (run direction, 2BE5's AL, the ball's y before the step) -> y after
        for run, d, y, after in ((1, 1, 5, 6), (2, 0xFF, 5, 4), (5, 1, 0x25, 0x24), (3, 1, 5, 4), (4, 1, 0x25, 0x24),
                                 (3, 1, 0xDB, 0xDC), (4, 1, 0xD9, 0xDC), (0, 1, 5, 5)):
            t = Machine()
            self.record(t, 0x0302, 0x0302, run=run)
            t.put8(t.ds(0x82F7), y)
            t.put16(t.ds(REC), (y << 8) | 3)
            t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees(holder=1, d=d))
            self.assertEqual(t.u8(t.ds(0x82F7)), after, (run, d, y))
            self.assertEqual(t.calls[-1].args, (t.DS, 0x82F6))

    def test_a_keeper_in_its_area_carries_the_ball_without_a_step(self):
        t = Machine()
        self.record(t, 0x0302, 0x0302, run=1)
        t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees(holder=1, keeper=1, area=1))
        self.assertEqual(t.targets(), ["0791:2C29", "0791:045D", "0791:2EB8", "0791:8F10"])
        self.assertEqual(t.calls[2].args, (0x0302, t.DS, REC))
        self.assertEqual(t.u16(t.ds(0x82F6)), 0x0302)

    def test_a_keeper_out_of_its_area_steps_the_ball(self):
        t = Machine()
        self.record(t, 0x0302, 0x0302, run=4)
        t.run(motion.move_player_sprite, [t.DS, REC], callees=self.callees(holder=1, keeper=1, area=0))
        self.assertEqual(t.u8(t.ds(0x82F7)), 4)


class Possession(unittest.TestCase):
    def test_869F_takes_the_slot_and_clears_the_play_bytes(self):
        t = Machine()
        t.put8(t.ds(REC) + 6, 7)
        for a in (0x8300, 0x8301, 0x830C, 0x830D, 0x8302, 0x8303, 0x8327):
            t.put8(t.ds(a), 0x33)
        self.assertEqual(t.run(motion.take_possession, [t.DS, REC], dx=0x4242), 0)
        self.assertEqual(t.u8(t.ds(0x830B)), 7)
        self.assertEqual([t.u8(t.ds(a)) for a in (0x8300, 0x8301, 0x830C, 0x830D, 0x8302, 0x8303, 0x8327)], [0] * 7)
        self.assertEqual(t.mem.reg("dx"), 0x4242)


class UpdatePlayer(unittest.TestCase):
    """8AE9 on a pitch record (+6 slot, +0xD player, +0xF run direction, +0x12 state, +0x14 activity)."""

    def setUp(self):
        t = self.t = Machine()
        r = self.r = t.ds(REC)
        t.put16(r + 0xD, 3)
        t.set_far(0xA91B, 0x100, 0x7000)                 # the position codes: player 3's at 7000:0100 + 3 * 0x14
        self.code = 0x7000 * 16 + 0x100 + 3 * 0x14

    def callees(self, **extra):
        c = {t: ret(0) for t, _ in motion.HANDLERS.values()}
        c.update({"0791:8889": ret(0), "0791:2CEC": ret(0), "0791:2AD4": ret(0), "0791:869F": ret(0),
                  "0791:8537": ret(0)})
        c.update(extra)
        return c

    def test_each_state_calls_its_handler_then_8889_and_8537(self):
        for state, (target, ret_to) in motion.HANDLERS.items():
            self.setUp()
            self.t.put8(self.r + 0x12, state)
            self.t.run(motion.update_player, [self.t.DS, REC], callees=self.callees())
            self.assertEqual(self.t.targets(), [target, "0791:8889", "0791:8537"])
            self.assertEqual(self.t.calls[0].ret_to, ret_to)
        for state in (0, 4, 0x0C, 0x0E):
            self.setUp()
            self.t.put8(self.r + 0x12, state)
            self.t.run(motion.update_player, [self.t.DS, REC], callees=self.callees())
            self.assertEqual(self.t.targets(), ["0791:8889", "0791:8537"], state)

    def test_8889_gets_the_frames_bp(self):
        t = self.t
        t.run(motion.update_player, [t.DS, REC], callees=self.callees())
        self.assertEqual(t.calls[0].args, (t.entry_sp - 2,))
        self.assertEqual((t.calls[0].ret_to, t.calls[0].far), ("0791:8BB7", False))

    def test_state_0a_calls_73ba_before_the_run_step_and_sprite(self):
        # seg_0791_14.asm:8B97-8BA4: state 0x0A takes the 73BA call at 8BA1.
        # Keep the expectation independent of HANDLERS: this branch may be absent from ALL.
        t = self.t
        t.put8(self.r + 0x12, 0x0A)
        t.run(motion.update_player, [t.DS, REC],
              callees={"0791:73BA": ret(0), "0791:8889": ret(0), "0791:8537": ret(0)})
        self.assertEqual(t.targets(), ["0791:73BA", "0791:8889", "0791:8537"])
        self.assertEqual((t.calls[0].args, t.calls[0].ret_to, t.calls[0].far),
                         ((t.DS, REC), "0791:8BA4", True))

    def test_the_activity_counts_unsigned_run_directions_below_5(self):
        for run, plus in ((0, 1), (4, 1), (5, 0), (0x80, 0), (0xFF, 0)):
            self.setUp()
            self.t.put8(self.r + 0xF, run)
            self.t.put16(self.r + 0x14, 10)
            self.t.run(motion.update_player, [self.t.DS, REC], callees=self.callees())
            self.assertEqual(self.t.u16(self.r + 0x14), 10 + plus, run)

    def test_energy_drops_after_180_only_above_1_and_the_counter_resets(self):
        for energy, count, after_energy, after_count in ((5, 0xB5, 4, 0), (1, 0xB5, 1, 0), (0x90, 0xB5, 0x90, 0),
                                                         (5, 0xB4, 5, 0xB4)):
            self.setUp()
            t = self.t
            t.put8(t.ds(0x8325), 1)
            t.put8(self.r + 0xF, 5)
            t.put16(self.r + 0x14, count)
            t.put8(self.code + 0xE, energy)
            value = t.run(motion.update_player, [t.DS, REC], callees=self.callees(**{"0791:8537": ret(0x77)}))
            self.assertEqual((t.u8(self.code + 0xE), t.u16(self.r + 0x14)), (after_energy, after_count), energy)
            self.assertEqual(value, 0 if count > 0xB4 else None)

    def test_the_position_code_is_the_one_at_entry(self):
        t = self.t
        t.put8(t.ds(0x8325), 1)
        t.put8(self.r + 0xF, 5)
        t.put16(self.r + 0x14, 0xB5)
        t.put8(self.code + 0xE, 5)

        def handler(machine, c):
            machine.put16(self.r + 0xD, 9)               # the handler binds another player
            return 0
        t.put8(self.r + 0x12, 5)
        t.run(motion.update_player, [t.DS, REC], callees=self.callees(**{"0791:57AC": handler}))
        self.assertEqual(t.u8(self.code + 0xE), 4)

    def test_the_ball_won_from_the_challenger(self):
        # 8302 set and the record's slot is DS:830D: 2CEC; when it is at the ball (and not state 0xC): 830C := 830D,
        # 2AD4(0x19) when 830B differs and 8303 is clear, 869F, 8303 restored
        for b, flag, at_ball, state, expect in ((2, 0, 1, 0, ["0791:2AD4", "0791:869F"]), (6, 0, 1, 0, ["0791:869F"]),
                                                (2, 1, 1, 0, ["0791:869F"]), (2, 0, 0, 0, []), (2, 0, 1, 0xC, [])):
            self.setUp()
            t = self.t
            t.put8(self.r + 6, 6)
            t.put8(self.r + 0x12, state)
            t.put8(t.ds(0x8302), 1)
            t.put8(t.ds(0x830D), 6)
            t.put8(t.ds(0x830B), b)
            t.put8(t.ds(0x8303), flag)

            def possession(machine, c):
                machine.put8(machine.ds(0x8303), 0)
                return 0
            t.run(motion.update_player, [t.DS, REC], callees=self.callees(**{"0791:2CEC": ret(at_ball),
                                                                              "0791:869F": possession}))
            seen = [x for x in t.targets() if x in ("0791:2AD4", "0791:869F")]
            self.assertEqual(seen, expect, (b, flag, at_ball, state))
            self.assertIn("0791:2CEC", t.targets())
            if expect:
                self.assertEqual(t.u8(t.ds(0x830C)), 6)
                self.assertEqual(t.u8(t.ds(0x8303)), flag)
            if "0791:2AD4" in expect:
                self.assertEqual(t.calls[t.targets().index("0791:2AD4")].args, (0x19,))

    def test_no_challenge_test_when_8302_is_clear_or_another_slot(self):
        for flag, slot in ((0, 6), (1, 5)):
            self.setUp()
            t = self.t
            t.put8(self.r + 6, slot)
            t.put8(t.ds(0x8302), flag)
            t.put8(t.ds(0x830D), 6)
            t.run(motion.update_player, [t.DS, REC], callees=self.callees())
            self.assertNotIn("0791:2CEC", t.targets())


class OffsideLines(unittest.TestCase):
    def test_8CCA_resets_both_lines_through_8C67_with_its_bp(self):
        t = Machine()
        sides = []                                        # 8C67 itself is driven in the next test
        t.run(motion.reset_offside_lines, [], far=False, ax=0xAB00,
              callees={"0791:8C67": lambda m, c: sides.append((c.args, c.ret_to, c.far)) or 0x5A07})
        bp = t.entry_sp - 2
        self.assertEqual(sides, [((0xAB01, bp), "0791:8CD4", False), ((0x5A00, bp), "0791:8CDB", False)])
        self.assertEqual((t.u8(t.ds(0x82EE)), t.u8(t.ds(0x82EF))), (1, 0))
        self.assertEqual((t.u16(t.ds(0x82F0)), t.u16(t.ds(0x82F4))), (1, 1))
        self.assertEqual(t.value, 1)

    def test_8C67_puts_the_line_at_the_keepers_side_times_8(self):
        for side, d, expect in ((0, 1, 8), (1, 0xFF, 0xF8)):
            t = Machine()
            t.put8(t.ds(motion.SIDE_BASE + side), 11 * side)
            t.put8(t.ds(0x82E2 + 6 * side) + 1, 0x33)
            got = []
            t.run(motion.reset_offside_line, [side, 0x0777], far=False,
                  callees={"0791:2BE5": lambda m, c: got.append(c.args) or d})
            line = t.ds(0x82E2 + 6 * side)
            self.assertEqual(got, [(t.DS, (11 * side + 1) * 0x16 + 0x80E8)])
            self.assertEqual((t.u8(line), t.u8(line + 1), t.u16(line + 2)), (expect, 0, expect))

    def track(self, ys, d=(1, 1), ball_y=5, flag=1, sprite=0x0EAE):
        """8CF5 with side 0's slots 2..11 at rows ys[0] and side 1's 13..22 at ys[1]."""
        t = Machine()
        t.put8(t.ds(motion.SIDE_BASE), 0)
        t.put8(t.ds(motion.SIDE_BASE + 1), 11)
        for side in (0, 1):
            for i, y in enumerate(ys[side]):
                t.put8(t.ds(0x80E8 + (11 * side + 2 + i) * 0x16 + 1), y)
        t.put8(t.ds(0x82F7), ball_y)
        t.put8(t.ds(0x8328), flag)
        t.put16(t.ds(0x8308), sprite)
        dirs = iter(d)
        t.run(motion.track_offside_line, [], far=False,
              callees={"0791:2BE5": lambda m, c: next(dirs), "0791:8E24": ret(0), "0791:90C5": ret(0)})
        return t

    def test_the_line_is_the_deepest_outfield_row_times_the_direction_never_above_zero(self):
        t = self.track(([3, 0xFE, 7, 1, 1, 1, 1, 1, 1, 1], [0xF0, 2, 2, 2, 2, 2, 2, 2, 2, 2]), d=(1, 0xFF))
        self.assertEqual(motion.s8(t.u8(t.ds(0x82E3))), -2)       # min(y * 1) = -2, times 1
        self.assertEqual(motion.s8(t.u8(t.ds(0x82E9))), 2)        # min(y * -1) = -2, times -1
        t = self.track(([3] * 10, [3] * 10))
        self.assertEqual((t.u8(t.ds(0x82E3)), t.u8(t.ds(0x82E9))), (0, 0))   # all ahead: the line stays 0

    def test_offside_max_variant_takes_the_most_advanced(self):
        t = Machine()
        t.put8(t.ds(motion.SIDE_BASE + 1), 11)
        for i, y in enumerate([3, 0xFE, 7, 1, 1, 1, 1, 1, 1, 1]):
            t.put8(t.ds(0x80E8 + (2 + i) * 0x16 + 1), y)
        t.run(motion.track_offside_line, [], far=False, variant="offside-max",
              callees={"0791:2BE5": ret(1), "0791:8E24": ret(0), "0791:90C5": ret(0)})
        self.assertEqual(t.u8(t.ds(0x82E3)), 7)

    def test_the_marker_is_placed_only_on_the_balls_side_with_8328_and_a_line(self):
        rows = ([0xFE] + [1] * 9, [0xFE] + [1] * 9)       # side 0's line -2, side 1's line 2 (d -1)
        for ball_y, flag, n in ((0xFB, 1, 1), (5, 1, 1), (0, 1, 1), (5, 0, 0)):
            t = self.track(rows, d=(1, 0xFF), ball_y=ball_y, flag=flag)
            marks = [c for c in t.calls if c.target == "0791:90C5"]
            self.assertEqual(len(marks), n, (ball_y, flag))
        t = self.track(rows, d=(1, 0xFF), ball_y=5)
        c = [c for c in t.calls if c.target == "0791:90C5"][0]
        self.assertEqual((c.args, c.ret_to, c.far), ((0x0EAE, t.u16(t.ds(0x82E8)), t.DS, 0x8304), "0791:8E17", True))
        t = self.track(([3] * 10, [3] * 10), ball_y=0)
        self.assertEqual([c for c in t.calls if c.target == "0791:90C5"], [])    # both lines 0: no marker


class Sprites(unittest.TestCase):
    def sprite(self, t, pos, old, glyph):
        s = t.ds(REC)
        t.put16(s, pos), t.put16(s + 2, old), t.put16(s + 4, glyph)
        return s

    def test_8E24_restores_the_old_cell_only_while_it_still_holds_the_sprite(self):
        for there, restored in ((0x0F41, 0x0D2E), (0x0F42, 0x0F42)):
            t = Machine()
            s = self.sprite(t, 0x0302, 0x0201, 0x0F41)
            t.put16(t.cell(PIC_SEG, 1, 2), there)
            t.put16(t.cell(BACK_SEG, 1, 2), 0x0D2E)
            ax = t.run(motion.move_sprite, [t.DS, REC])
            self.assertEqual(t.u16(t.cell(PIC_SEG, 1, 2)), restored)
            self.assertEqual((t.u16(t.cell(PIC_SEG, 2, 3)), t.u16(s + 2)), (0x0F41, 0x0302))
            self.assertEqual((ax, t.mem.reg("dx")), (2 * 0xA0, 0))

    def test_8E24_negative_rows_and_columns_are_signed(self):
        t = Machine()
        self.sprite(t, 0xFEFF, 0xFEFF, 0x0F41)            # row -1, column -2
        ax = t.run(motion.move_sprite, [t.DS, REC])
        self.assertEqual(t.u16(t.cell(PIC_SEG, 0xFF, 0xFE)), 0x0F41)
        self.assertEqual((ax, t.mem.reg("dx")), ((-0xA0) & 0xFFFF, 0x9F))  # mul of 0xFFFF by 0xA0, unsigned

    def test_90C5_places_the_marker_beside_the_line_and_draws_it_unless_quick(self):
        for glyph, quick, step, drawn in ((0x0EAE, 0, 0xFF, True), (0x0E41, 0, 1, True), (0x0EAE, 1, 0xFF, False)):
            t = Machine()
            t.put8(t.ds(motion.DIRECTIONS), 0xFF)
            t.put8(t.ds(motion.DIRECTIONS + 1), 1)
            t.put8(t.ds(0x9A3E), quick)
            t.run(motion.place_marker, [glyph, 0x0507, t.DS, REC], callees={"0791:8E24": ret(0)})
            s = t.ds(REC)
            self.assertEqual((t.u16(s + 4), t.u8(s), t.u8(s + 1)), (glyph, 7, (5 + motion.s8(step)) & 0xFF))
            self.assertEqual(t.targets(), ["0791:8E24"] if drawn else [])


class Referee(unittest.TestCase):
    """9119 on the referee's sprite record (+0 row, +1 column, +2 old, +4 glyph, +6 target row, +7 target column)."""

    def setUp(self):
        t = self.t = Machine()
        t.put8(t.ds(motion.DIRECTIONS), 0xFF)
        t.put8(t.ds(motion.DIRECTIONS + 1), 1)
        self.s = t.ds(REC)

    def put(self, row, col, old=0x7777, glyph=0x0F52):
        t, s = self.t, self.s
        t.put8(s, row), t.put8(s + 1, col), t.put16(s + 2, old), t.put16(s + 4, glyph)

    def test_with_its_flag_it_goes_one_step_to_the_cell_below_the_ball(self):
        t, s = self.t, self.s
        self.put(3, 3)
        t.put8(t.ds(0x82F6), 6)
        t.put8(t.ds(0x82F7), 0xFE)
        ax = t.run(motion.move_referee, [1, t.DS, REC], callees={"0791:8E24": ret(0)})
        self.assertEqual((t.u8(s + 6), t.u8(s + 7)), (7, 0xFE))
        self.assertEqual((t.u8(s), t.u8(s + 1)), (4, 2))
        self.assertEqual(t.u16(t.cell(PIC_SEG, 4, 2)), 0x0F52)
        self.assertEqual(ax, 4 * 0xA0)
        self.assertEqual(t.targets(), ["0791:8E24"])

    def flagless(self, ball_y, rand, clamp=None, zf=ZF, row=0, col=0, old=0x7777):
        t, s = self.t, self.s
        self.put(row, col, old=old)
        t.put8(t.ds(0x82F7), ball_y)
        got = {}

        def mn(m, c):
            got["min"] = c.args
            a, b = motion.s16(c.args[1]), motion.s16(c.args[3])
            return min(a, b)

        def mx(m, c):
            got["max"] = c.args
            a, b = motion.s16(c.args[1]), motion.s16(c.args[3])
            return max(a, b)

        def clamp_byte(m, c):
            got["clamp"] = (c.args, m.mem.reg("ax"), m.mem.reg("dx"))
            if clamp is not None:
                m.put8(s + 6, clamp)
            return 0

        def in_set(m, c):
            got["set"] = c.args
            m.mem.set_reg("eflags", zf)
            return 0
        t.run(motion.move_referee, [0, t.DS, REC],
              callees={"214B:06B1": lambda m, c: got.setdefault("rand", c.args) and rand, "214B:0D1C": mn,
                       "214B:0D56": mx, "214B:2031": clamp_byte, "23E4:08DF": in_set, "0791:8E24": ret(0)})
        return got

    def test_without_its_flag_it_follows_the_ball_column_within_31_or_32(self):
        t, s = self.t, self.s
        got = self.flagless(5, 2)
        self.assertEqual(got["min"], (0, 6, 0, 32))
        self.assertEqual(motion.s8(t.u8(s + 7)), 6)
        self.assertEqual(t.u8(s + 6), 6 // 4 + 1)
        self.setUp()
        got = self.flagless(0x30, 1)
        self.assertEqual(motion.s8(self.t.u8(self.s + 7)), 31)
        self.assertEqual(self.t.u8(self.s + 6), 31 // 4 + 1)

    def test_a_ball_column_at_or_below_zero_uses_max_and_idiv_truncates(self):
        got = self.flagless(0xF9, 1)                     # -7: max(-8, -0x1e - 1)
        self.assertEqual(got["max"], (0xFFFF, (-8) & 0xFFFF, 0xFFFF, (-31) & 0xFFFF))
        self.assertEqual(motion.s8(self.t.u8(self.s + 7)), -8)
        self.assertEqual(self.t.u8(self.s + 6), (-8 // 4 + 1) & 0xFF)       # idiv: -2, +1
        self.setUp()
        self.flagless(0xF9, 2)
        self.setUp()
        self.flagless(0, 2)                               # 0: the max path
        self.setUp()
        self.flagless(0xFE, 1)                            # -3 / 4 truncates to 0 (not -1): row 1
        self.assertEqual(self.t.u8(self.s + 6), 1)

    def test_the_clamp_gets_the_target_byte_and_the_listings_words(self):
        got = self.flagless(0x0D, 1)                      # min(14, 31) = 14; 14 / 4 + 1 = 4, remainder 2
        args, ax, dx = got["clamp"]
        self.assertEqual(args, (self.t.DS, (REC + 6) & 0xFFFF, 0x00FB, 0x0005))
        self.assertEqual((ax, dx), (5, 2))

    def test_a_step_onto_a_blocking_character_is_taken_back(self):
        t, s = self.t, self.s
        t.put16(t.cell(BACK_SEG, 1, 1), 0x0DB2)
        got = self.flagless(5, 2, clamp=4, zf=0, row=0, col=0, old=0x0000)   # target (4, 6): one step to (1, 1)
        self.assertEqual(got["set"], (0x00B2 | (motion.cell_mul(1)[0] & 0xFF00), t.DS, motion.BLOCKERS))
        self.assertEqual((t.u8(s), t.u8(s + 1)), (0, 0))  # in the set (ZF clear): back to the old position

    def test_a_free_step_stays(self):
        t, s = self.t, self.s
        self.flagless(5, 2, clamp=4, zf=ZF, row=0, col=0, old=0x0000)
        self.assertEqual((t.u8(s), t.u8(s + 1)), (1, 1))

    def test_on_its_target_already_no_step_and_no_set_test(self):
        t, s = self.t, self.s
        got = self.flagless(5, 2, clamp=2, old=0x0602, row=9, col=9)    # target word (2, 6) == old word 0x0602
        self.assertNotIn("set", got)
        self.assertEqual((t.u8(s), t.u8(s + 1)), (9, 9))

    def test_one_axis_at_a_time_when_the_other_is_reached(self):
        t, s = self.t, self.s
        self.flagless(5, 2, clamp=4, row=4, col=0, old=0x0000)          # row reached: only the column steps
        self.assertEqual((t.u8(s), t.u8(s + 1)), (4, 1))

    def test_referee_still_variant_never_steps(self):
        t, s = self.t, self.s
        self.put(0, 0, old=0)
        t.put8(t.ds(0x82F7), 5)
        t.run(motion.move_referee, [0, t.DS, REC], variant="referee-still",
              callees={"214B:06B1": ret(2), "214B:0D1C": ret(6), "214B:2031": ret(0), "0791:8E24": ret(0)})
        self.assertEqual((t.u8(s), t.u8(s + 1)), (0, 0))

    def test_the_long_pushed_before_rand_is_where_0D1C_finds_it(self):
        t = self.t
        self.put(0, 0)
        t.put8(t.ds(0x82F7), 5)
        seen = {}

        def rand(m, c):
            seen["rand_sp"] = m.mem.reg("sp")
            seen["long"] = (m.u16(SS * 16 + m.mem.reg("sp")), m.u16(SS * 16 + m.mem.reg("sp") + 2))
            return 1

        def mn(m, c):
            seen["min_sp"] = m.mem.reg("sp")
            return 6
        t.run(motion.move_referee, [0, t.DS, REC],
              callees={"214B:06B1": rand, "214B:0D1C": mn, "214B:2031": ret(0), "23E4:08DF": ret(0),
                       "0791:8E24": ret(0)})
        frame_sp = t.entry_sp - 2                         # after push bp
        self.assertEqual(seen["rand_sp"], frame_sp - 4)   # the long sits below the frame when rand is called
        self.assertEqual(seen["long"], (6, 0))
        self.assertEqual(seen["min_sp"], frame_sp)        # and 0D1C's call pushes it again in place


if __name__ == "__main__":
    unittest.main()
