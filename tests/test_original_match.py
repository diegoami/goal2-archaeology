"""runtime/original_match (issue 250): the kit that runs the original's watched match interactively for goal2.

- ScreenDriverTests: the closed-loop key choice of screens.MenuPlan on synthetic screen states (no emulator): the
  team menu's items per side, the tactics rows, SELECT TEAM's substitution (mark, swap, the check of the swap),
  the request when substitutions are not allowed now, a position job, a player's own tactics and man-marking.
- ImageTests: the GOAL program's load segment from a synthetic memory control block and PSP; a short image refused.
- MachineTests (unicorn): a far call set up by Machine.far_call returns to its return address with its argument
  popped; a hook that stops is called again with replay=True when the run resumes at its address.
- OriginalTests (skipped without E006-r0001 in .cache/dl): the engine check (E011-r0001's match as E021 recorded
  it), a half-time substitution made through the original's screens, and an eleven the original refuses handed
  back as a decision with the original's message.
"""
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import screens as S  # noqa: E402
from original_match.image import Image, find_load_segment, MEM_BASE  # noqa: E402

IMAGE = ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav"
IMAGE_SHA = "e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d"


def state(**kw):
    s = {"cursor": 1, "squad": list(range(101, 121)), "allowed": 1, "request": 0, "subs_left": 5,
         "position": lambda p: 3}
    s.update(kw)
    return s


class ScreenDriverTests(unittest.TestCase):
    def test_menu_items_per_side(self):
        p = S.MenuPlan(0, tactics={4: True})
        self.assertEqual(p.menu_key(10), S.UP)          # side 0: tactics is item 6
        self.assertEqual(p.menu_key(6), S.ENTER)
        self.assertEqual(p.in_screen, "tactics")
        self.assertEqual(p.menu_key(6), S.DOWN)         # back from the screen: next step, play = item 10
        self.assertEqual(p.menu_key(10), S.ENTER)
        q = S.MenuPlan(1, subs=[(101, 112)])
        self.assertEqual(q.menu_key(5), S.UP)           # side 1: select team is item 2
        self.assertEqual(q.menu_key(2), S.ENTER)

    def test_tactics_rows(self):
        p = S.MenuPlan(0, tactics={4: True, 8: False})
        rows = [0, 1, 2, 3, 4, 5, 6, 7, 8]              # row r toggles element r
        self.assertEqual(p.tactics_key(1, rows, 0x80), S.DOWN)
        self.assertEqual(p.tactics_key(4, rows, 0x80), S.ENTER)
        self.assertEqual(p.tactics_key(4, rows, 0x88), S.DOWN)      # element 4 set, element 8 still set
        self.assertEqual(p.tactics_key(8, rows, 0x88), S.ENTER)
        self.assertEqual(p.tactics_key(8, rows, 0x08), S.ESC)
        with self.assertRaises(ValueError):
            S.MenuPlan(0, tactics={3: True}).tactics_key(1, [0, 1, 2, 4, 4, 5, 6, 7, 8], 0)

    def test_substitution_mark_swap_and_check(self):
        p = S.MenuPlan(0, subs=[(105, 113)])
        self.assertEqual(p.select_key(state(cursor=1)), S.DOWN)
        self.assertEqual(p.select_key(state(cursor=5)), S.ENTER)    # mark the player going off
        self.assertEqual(p.select_key(state(cursor=5)), S.DOWN)
        self.assertEqual(p.select_key(state(cursor=13)), S.ENTER)   # the swap
        swapped = list(range(101, 121))
        swapped[4], swapped[12] = 113, 105
        self.assertEqual(p.select_key(state(cursor=13, squad=swapped)), S.ESC)
        self.assertEqual(p.done, [("sub", 105, 113)])
        q = S.MenuPlan(0, subs=[(105, 113)])
        for c in (5, 5, 13):
            q.select_key(state(cursor=c))
        q.last_message = "Denmark has too many goalkeepers"
        self.assertEqual(q.select_key(state(cursor=13)), S.ESC)     # not swapped: refused, with the message
        self.assertEqual(q.refused, [(("sub", 105, 113), "Denmark has too many goalkeepers")])

    def test_request_when_not_allowed_now(self):
        p = S.MenuPlan(0, subs=[(105, 113)])
        self.assertEqual(p.select_key(state(allowed=0)), S.ENTER)   # toggles DS:9B40 on
        self.assertEqual(p.select_key(state(allowed=0, request=1)), S.ESC)
        self.assertTrue(p.requested)
        q = S.MenuPlan(0, subs=[(105, 113)])
        self.assertEqual(q.select_key(state(allowed=0, request=1)), S.ESC)   # already asked: Enter would cancel it

    def test_position_job(self):
        pos = {"code": 3}
        p = S.MenuPlan(0, positions={104: 5})
        self.assertEqual(p.select_key(state(cursor=4, position=lambda w: pos["code"])), S.KEY_R)
        pos["code"] = 4
        self.assertEqual(p.select_key(state(cursor=4, position=lambda w: pos["code"])), S.KEY_R)
        pos["code"] = 5
        self.assertEqual(p.select_key(state(cursor=4, position=lambda w: pos["code"])), S.ESC)
        self.assertEqual(p.done, [("position", 104, 5)])

    def test_own_tactics_and_marking(self):
        p = S.MenuPlan(0, own={107: {1: True}}, marking={107: 333})
        self.assertEqual(p.select_key(state(cursor=7)), S.KEY_T)
        self.assertEqual(p.own_key(1, 0x00, 0, 0x8B, True), S.ENTER)        # row 1: no override -> override clear
        self.assertEqual(p.own_key(1, 0x10, 0, 0x8B, True), S.ENTER)        # -> override set
        self.assertEqual(p.own_key(1, 0x11, 0, 0x8B, True), S.DOWN)         # element 1 done; marking: row 5
        self.assertEqual(p.own_key(5, 0x11, 0, 0x8B, True), S.ENTER)        # cycles the marked opponent
        self.assertEqual(p.own_key(5, 0x11, 333, 0x8B, True), S.ESC)
        self.assertEqual(p.select_key(state(cursor=7)), S.ESC)
        self.assertEqual(p.done[0][:2], ("own", 107))
        q = S.MenuPlan(0, marking={107: 333})
        q.select_key(state(cursor=7))
        self.assertEqual(q.own_key(1, 0, 0, 0, False), S.ESC)               # no man-marking row: refused
        q.select_key(state(cursor=7))
        self.assertEqual(q.done, [])
        self.assertEqual(len(q.refused), 1)


class ImageTests(unittest.TestCase):
    def test_load_segment_from_mcb(self):
        memory = bytearray(0x110000)
        mcb = 0x700
        memory[mcb * 16:mcb * 16 + 16] = b"M" + (mcb + 1).to_bytes(2, "little") + b"\x00" * 5 + b"GOAL\x00\x00\x00\x00"
        memory[(mcb + 1) * 16:(mcb + 1) * 16 + 2] = b"\xcd\x20"
        self.assertEqual(find_load_segment(memory), mcb + 1 + 0x10)
        memory[(mcb + 1) * 16] = 0
        with self.assertRaises(ValueError):
            find_load_segment(memory)

    def test_short_image_refused(self):
        with self.assertRaises(ValueError):
            Image(bytes(MEM_BASE + 100))


try:
    from original_match.machine import Machine
except ModuleNotFoundError:            # CI does not install python3-unicorn
    Machine = None


@unittest.skipIf(Machine is None, "unicorn not installed")
class MachineTests(unittest.TestCase):
    def machine(self, program, at=0x1000):
        memory = bytearray(0x110000)
        memory[at * 16:at * 16 + len(program)] = program
        return Machine(memory, load=0)

    def test_far_call_returns_with_its_argument_popped(self):
        # 2000:0000: mov ax, [bp+?]-free body: inc word [0x0100]; retf 4
        m = self.machine(bytes([0xFF, 0x06, 0x00, 0x01, 0xCA, 0x04, 0x00]), at=0x2000)
        end = m.far_call("2000:0000", [0x1111, 0x2222], "3000:0010", ss=0x5000, sp=0x0100)
        self.assertEqual(m.stack_word(4), 0x2222)            # the last argument nearest the return address
        self.assertIsNone(m.run(end, 5, fresh=True))
        self.assertEqual(m.reg("sp"), 0x0108)
        self.assertEqual((m.reg("cs"), m.reg("ip")), (0x3000, 0x0010))

    def test_stop_and_replay(self):
        # 1000:0000: nop; nop; hlt (the hook at 1000:0001 stops once)
        m = self.machine(bytes([0x90, 0x90, 0xF4]))
        calls = []

        def hook(replay):
            calls.append(replay)
            if len(calls) == 1:
                m.stop("test")
        m.at("1000:0001", hook)
        m.set_reg("cs", 0x1000)
        m.set_reg("eip", 0)
        self.assertEqual(m.run(0x10002, 5, fresh=True), "test")
        self.assertEqual(m.pc(), 0x10001)                    # the hooked instruction is not executed
        self.assertIsNone(m.run(0x10002, 5))
        self.assertEqual(calls, [False, True])


@unittest.skipIf(Machine is None or not IMAGE.is_file(), "unicorn or the E006-r0001 image (.cache/dl) missing")
class OriginalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = IMAGE.read_bytes()
        assert hashlib.sha256(data).hexdigest() == IMAGE_SHA
        cls.image = Image.from_savestate(data)

    def test_engine_is_e011_r0001(self):
        from original_match import check
        ok, diff = check.engine(self.image)
        self.assertTrue(ok, diff)

    def test_every_commentary_line_is_an_event(self):
        # 1D4A writes one line per increment of the ring counter DS:80EE (214B wrap_add 1..200); the set-up A4A1
        # writes it 0 once. Every nonzero write is a line the original wrote: each must be one commentary event.
        from unicorn import UC_HOOK_MEM_WRITE
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21), managed=7)
        writes = []
        lin = m.m.DS * 16 + 0x80EE
        m.m.uc.hook_add(UC_HOOK_MEM_WRITE, lambda uc, a, addr, size, v, d: writes.append(v & 0xFFFF),
                        begin=lin, end=lin)
        events = [ev for ev in m.events() if ev.kind == "commentary"]
        self.assertEqual(writes.count(0), 1)
        self.assertEqual(len(events), len(writes) - 1)
        self.assertGreater(len(events), 1000)

    def test_half_time_substitution(self):
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21), managed=7)
        for ev in m.events():
            if ev.kind == "decision":
                m.answer(substitutions=[(130, 134)] if ev.data["context"] == "half_time" else ())
        subs = [(s["off"], s["on"], s["minute"]) for s in m.result()["substitutions"] if s["team"] == 0]
        self.assertEqual(subs[0], (130, 134, 46))
        before, after = self.image.memory_component(), m.memory_component()   # the image's own size, and only
        self.assertEqual(len(after), len(before))                             # the first 1 MiB + HMA can change
        self.assertEqual(after[0x78 + 0x110000:], before[0x78 + 0x110000:])
        self.assertNotEqual(after[:0x78 + 0x110000], before[:0x78 + 0x110000])

    def test_refused_eleven_comes_back(self):
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21), managed=7)
        refusals = []
        for ev in m.events():
            if ev.kind == "decision" and ev.data["context"] == "half_time":
                if ev.data.get("refused"):
                    refusals.append(ev.data["refused"])
                    m.answer(substitutions=[(121, 133)])
                else:
                    m.answer(substitutions=[(130, 132)])     # the reserve keeper: two keepers
        self.assertEqual(refusals, ["Denmark has too many goalkeepers"])
        self.assertTrue(m.over)


if __name__ == "__main__":
    unittest.main()
