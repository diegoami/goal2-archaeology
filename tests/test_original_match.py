"""runtime/original_match (issue 250): the kit that runs the original's watched match interactively for goal2.

- ScreenDriverTests: the closed-loop key choice of screens.MenuPlan on synthetic screen states (no emulator): the
  team menu's items per side, the tactics rows, SELECT TEAM's substitution (mark, swap, the check of the swap),
  the request when substitutions are not allowed now, a position job, a player's own tactics and man-marking.
- ImageTests: the GOAL program's load segment from a synthetic memory control block and PSP; a short image refused.
- MachineTests (unicorn): a far call set up by Machine.far_call returns to its return address with its argument
  popped; a hook that stops is called again with replay=True when the run resumes at its address.
- OriginalTests (skipped without E006-r0001 in .cache/dl): the engine check (E011-r0001's match as E021 recorded
  it), every line the original writes is one commentary event, a half-time substitution made through the
  original's screens (and the memory given back at the image's own size), an image of another build refused, and
  an eleven the original refuses handed back as a decision with the original's message.
- CompetitiveTests (issue 252; same skip): the kinds accepted and refused; a World Cup knockout match (kind 200)
  level after 90 and 120 minutes: extra time's event and its two decisions, the shoot-out, its kicks, its score and
  the winner, the full-time board after it, no pause in it; goal2's shoot-out order taken, kick by kick and past the
  eleventh kick of a side (the takers' rotation); the substitution budget set per side (5 made where the original
  allows 2, none for a side given 0); an extra-time goal marked as such; a ban after a sending off in the result's
  players; a qualifier (kind 2) with its competition table.
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


@unittest.skipUnless(IMAGE.is_file(), "the E006-r0001 image (.cache/dl) missing")
class SetPieceTests(unittest.TestCase):
    def test_original_accepts_chosen_taker_and_unanswered_keeps_pick(self):
        from original_match import Match, Fixture
        image = Image.from_savestate(IMAGE.read_bytes())
        for choose in (False, True):
            m = Match(image, Fixture(7, 19, index=21), managed=7, set_piece=True)
            accepted = []
            m.m.at("0791:D010", lambda replay: replay or accepted.append(m.m.reg("ax")))
            decision = None
            for ev in m.events():
                if ev.kind == "decision":
                    if ev.data["context"] == "set_piece":
                        decision = ev.data
                        target = next(w for w in reversed(decision["available"]) if w != decision["current"])
                        with self.assertRaises(ValueError):
                            m.answer(taker=0)
                        with self.assertRaises(ValueError):
                            m.answer(taker=target, quick=True)
                        m.answer(taker=target) if choose else m.answer()
                    else:
                        m.answer()
                elif ev.kind == "set_piece":
                    self.assertIsNotNone(decision)
                    self.assertEqual(ev.data["player"], target if choose else decision["current"])
                    self.assertEqual(ev.data["role"], decision["role"])
                    self.assertEqual(accepted[-1], ev.data["player"])
                    break
            else:
                self.fail("the original never accepted a set-piece taker")


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

    def test_build_guard_data(self):
        from original_match import build
        from original_match.image import _relocations
        r = _relocations()
        self.assertEqual(len(r), 1916)                                    # the MZ header's relocations
        self.assertEqual(r, sorted(set(r)))
        self.assertLessEqual(max(r) + 2, build.CODE_SIZE)                 # all in the code
        self.assertEqual(len(build.CODE_SHA256), -(-build.CODE_SIZE // build.CODE_BLOCK))
        end = -1
        for s, n in build.DATA_RANGES:
            self.assertGreater(s, end)
            self.assertEqual(s // build.DATA_BLOCK, (s + n - 1) // build.DATA_BLOCK)
            self.assertLessEqual(s + n, 0x7B70)                           # the initialised data only
            end = s + n - 1
        covered = {o for s, n in build.DATA_RANGES for o in range(s, s + n)}
        self.assertTrue({0x07CB, 0x07DB, 0x0648, 0x6BC0} <= covered)      # depth tables, occupancy set, tactics rows
        self.assertFalse({0x7968, 0x7B62} & covered)                       # a start-up variable, the seed


from original_match.machine import Machine  # noqa: E402  (imports without unicorn; a Machine needs it)
try:
    import unicorn  # noqa: F401
except ImportError:                    # a machine without unicorn (CI's code tier installs it, #304)
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

    def test_fixture_without_managed_side_preserves_computer_managers(self):
        from original_match import Match, Fixture, MatchError
        m = Match(self.image, Fixture(1, 2, index=21), managed=7, record_draws=True)
        self.assertIsNone(m.side)
        self.assertEqual([m._manager_byte(c) for c in (1, 2)],
                         [self.image.memory[m._country(c) + 0x2E] for c in (1, 2)])
        with self.assertRaisesRegex(MatchError, "neither side is managed"):
            m.pause()
        with self.assertRaises(ValueError):
            Match(self.image, Fixture(1, 2, index=21), managed=7, captain=1)
        events = list(m.events())
        self.assertFalse([e for e in events if e.kind == "decision"])
        self.assertTrue(m.st["over"])
        self.assertGreater(m.result()["draws"], 0)
        self.assertIsNotNone(m.result()["kickoff_seed"])
        self.assertTrue([e for e in events if e.kind == "full_time"])

    def test_computer_only_seed_and_delay_land_at_actual_play_entry(self):
        from original_match import Match, Fixture
        from original_match.match import PLAY_MATCH, SEED, GAME_PTR
        m=Match(self.image,Fixture(1,2,index=21),managed=7,seed=0x1234,
                delay_byte=2,record_draws=True)
        observed=[]
        def at_play(replay):
            if not replay:
                observed.append((m.m.rd(SEED),m.m.rd_far(GAME_PTR,0x3F,1),m.st["recording"]))
        m.m.at(PLAY_MATCH,at_play)
        events=list(m.events())
        self.assertEqual(observed,[(0x1234,2,True)])
        self.assertEqual(m.result()["kickoff_seed"],0x1234)
        self.assertGreater(m.result()["draws"],0)
        self.assertFalse([e for e in events if e.kind=="decision"])

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

    def refused(self, *edits):
        """The image with `edits` ((linear address, new bytes)) must be refused when a match is made of it."""
        from original_match import Match, Fixture
        other = Image(self.image.memory_component())
        for a, raw in edits:
            other.memory[a:a + len(raw)] = bytes(raw)
        with self.assertRaises(ValueError):
            Match(other, Fixture(7, 19, index=21), managed=7)

    def code(self, address):
        seg, off = address.split(":")
        return (self.image.load + int(seg, 16)) * 16 + int(off, 16)

    def test_another_build_is_refused(self):
        a = self.code("0791:F1F9")                       # run_match's `sub sp, 0xa` frame size: a prefix byte
        self.refused((a + 2, [self.image.memory[a + 2] ^ 0x02]))

    def test_guard_covers_code_beyond_prefixes(self):
        a = self.code("214B:0696")                       # the LCG multiplier (`mov bx, 0x7abd`, F004)
        self.assertEqual(self.image.memory[a:a + 2], bytes([0xBD, 0x7A]))
        self.refused((a, [0xBF, 0x7A]))
        b = self.code("0791:95F3")                       # inside the watched engine 9564: `mov di, 0x82f6`
        self.refused((b, [self.image.memory[b] ^ 0x0E]))

    def test_guard_covers_data_tables(self):
        ds = self.image.DS * 16                          # the defending depth table DS:07CB (F026)
        self.refused((ds + 0x07CB, [self.image.memory[ds + 0x07CB] ^ 0x01]))

    def test_guard_covers_relocated_words(self):
        a = self.code("000E:6F1B")                       # `6F18 call far 0791:F1F6`: its segment word, relocated
        w = int.from_bytes(self.image.memory[a:a + 2], "little")
        self.refused((a, ((w + 1) & 0xFFFF).to_bytes(2, "little")))

    def test_guard_leaves_goal2_state_alone(self):
        from original_match import Match, Fixture
        other = Image(self.image.memory_component())
        ds = other.DS * 16
        players, countries, game = other.far(0xA91B), other.far(0xA917), other.far(0xA923)
        for a, raw in ((players + 20 * 121 + 0x0C, [3]), (countries + 0xBF * 7 + 0x2D, [0xFF]),
                       (ds + 0x7B62, [1, 2]), (ds + 0x8336, [3, 4]), (game + 0x26, [40, 0])):
            other.memory[a:a + len(raw)] = bytes(raw)
        self.assertEqual(other.build_problems(), [])
        Match(other, Fixture(7, 19, index=40), managed=7)

    def test_save_at_full_time_and_at_a_decision(self):
        # PR 251 review R2: every event is a boundary save() accepts; resumed = straight
        from original_match import Match, Fixture

        def play(save_at=None):
            m = Match(self.image, Fixture(7, 19, index=21), managed=7)
            events, i = [], 0
            while True:
                for ev in m.events():
                    events.append((ev.kind, ev.minute, ev.score))
                    if ev.kind == "decision":
                        m.answer()
                    if save_at and ev.kind == save_at and not getattr(m, "_reloaded", False):
                        m = Match.load(m.save())
                        m._reloaded = True
                        break
                else:
                    return events, m.result()
        straight, r = play()
        for kind in ("full_time", "decision", "commentary"):
            events, r2 = play(kind)
            self.assertEqual(events, straight, kind)
            self.assertEqual((r2["score"], r2["board"], r2["squads_after"]), (r["score"], r["board"], r["squads_after"]))

    def test_events_are_stamped_at_the_originals_writes(self):
        # PR 251 review R3: each line's minute and score as the guest had them when 1D4A wrote the line (the ring
        # counter's write), each goal's at the score byte's, each minute's at the clock's: compared stamp by stamp
        from unicorn import UC_HOOK_MEM_WRITE
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21), managed=7, seed=0x0101)
        ds, uc = m.m.DS * 16, m.m.uc
        seen = {"commentary": [], "goal": [], "minute": [], "substitution": []}

        def now():
            mem = uc.mem_read(ds + 0x831F, 2)
            score = uc.mem_read(ds + 0x9B3C, 2)
            return [int.from_bytes(mem, "little"), score[0], score[1]]

        def ring(uc_, access, address, size, value, data):
            if address == ds + 0x80EE and value & 0xFFFF:
                seen["commentary"].append(now())

        def score(uc_, access, address, size, value, data):
            old = uc_.mem_read(ds + 0x9B3C, 2)
            new = bytearray(old)
            for i in range(size):
                if 0 <= address + i - ds - 0x9B3C < 2:
                    new[address + i - ds - 0x9B3C] = (value >> 8 * i) & 0xFF
            for t in (0, 1):
                if new[t] == old[t] + 1 and len(seen["minute"]):
                    seen["goal"].append([now()[0], new[0], new[1]])

        def minute(uc_, access, address, size, value, data):
            if address == ds + 0x831F and seen["commentary"] and (value & 0xFFFF) != now()[0]:
                seen["minute"].append([value & 0xFFFF] + now()[1:])

        def subs(uc_, access, address, size, value, data):      # substitutions left, DS:9B3A + t (C5DC at C7DC)
            t = address - ds - 0x9B3A
            if size == 1 and t in (0, 1) and seen["minute"] and (value & 0xFF) < uc_.mem_read(address, 1)[0]:
                seen["substitution"].append([t] + now())
        uc.hook_add(UC_HOOK_MEM_WRITE, ring, begin=ds + 0x80EE, end=ds + 0x80EF)
        uc.hook_add(UC_HOOK_MEM_WRITE, score, begin=ds + 0x9B3C, end=ds + 0x9B3D)
        uc.hook_add(UC_HOOK_MEM_WRITE, minute, begin=ds + 0x831F, end=ds + 0x8320)
        uc.hook_add(UC_HOOK_MEM_WRITE, subs, begin=ds + 0x9B3A, end=ds + 0x9B3B)
        got = {"commentary": [], "goal": [], "minute": [], "substitution": []}
        for ev in m.events():
            if ev.kind in got:
                got[ev.kind].append(([ev.data["team"]] if ev.kind == "substitution" else []) + [ev.minute] + list(ev.score))
            if ev.kind == "decision":
                m.answer()
        self.assertGreater(len(seen["commentary"]), 900)
        self.assertGreater(len(seen["substitution"]), 2)
        for kind in got:
            self.assertEqual(got[kind], seen[kind], kind)

    def play(self, seed=None, pauses=(), answer=None, save_after=None):
        """The reference fixture; pauses at the given minutes; answer(m, data) answers decisions (play on by
        default); save_after(m, event) True: save there and go on from Match.load. Returns the events, the result
        and the original's own goal counts DS:80F0 (record_goal 6443) read from the guest after the match."""
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21), managed=7, seed=seed)
        events, paused, saved = [], set(), False
        while True:
            for ev in m.events():
                events.append(ev)
                if ev.kind == "minute" and ev.minute in pauses and ev.minute not in paused:
                    paused.add(ev.minute)
                    m.pause()
                if ev.kind == "decision":
                    (answer or (lambda m, d: m.answer()))(m, ev.data)
                if save_after and not saved and save_after(m, ev):
                    saved = True
                    m = Match.load(m.save())
                    break
            else:
                break
        return events, m.result(), [m.m.rd(0x80F0, 1), m.m.rd(0x80F1, 1)]

    def goal_problems(self, events, result, counts):
        # the event stream's scores follow its goal events (a goal +1, a take-back -1 after a goal of that team,
        # nothing else moves the score), end at the board's score, and per team the result's goals are the board's
        # score and the original's own count (record_goal credits an own goal to the side whose byte rises)
        problems, score, open_goals = [], [0, 0], [0, 0]
        for i, ev in enumerate(events):
            if ev.kind in ("goal", "goal_disallowed"):
                t, step = ev.data["team"], 1 if ev.kind == "goal" else -1
                if step < 0 and not open_goals[t]:
                    problems.append((i, "goal_disallowed without a goal before it"))
                open_goals[t] += step
                score[t] += step
            if list(ev.score) != score:
                problems.append((i, ev.kind, ev.minute, list(ev.score), list(score)))
                score = list(ev.score)
        if score != list(result["score"]):
            problems.append(("end", score, result["score"]))
        for t in (0, 1):
            n = sum(1 for g in result["goals"] if g["team"] == t)
            if not n == result["score"][t] == counts[t]:
                problems.append(("team", t, n, result["score"][t], counts[t]))
        return problems

    def test_goal_records_agree_with_the_board_in_every_path(self):
        # PR 251 review round 2, R1: the quick engine (0791:D733) clears DS:9B3C and rolls trial counts into it
        # every minute; only its commit at DA58 adds goals. Watched, quick from minute 1 to 75 at each speed 0..5,
        # quick after a tactic and a substitution, a save inside a quick result, a watched goal taken back.
        def quick(speed, at=0, then=None):
            def answer(m, d):
                if d["context"] == "pause" and m.minute >= at:
                    m.answer(quick=True, speed=speed)
                else:
                    (then or (lambda m, d: m.answer()))(m, d)
            return answer
        sys.path.insert(0, str(ROOT / "experiments" / "E033-original-match-kit"))
        import stamps
        paths = {f"quick from minute {mn}, speed {sp}": dict(pauses=(mn,), answer=quick(sp))
                 for mn, sp in ((1, 0), (15, 1), (30, 2), (45, 3), (60, 4), (75, 5))}
        paths["quick at 60 after a tactic and a substitution at 20, seed 70"] = dict(
            seed=70, pauses=(20, 60), answer=quick(3, at=60, then=stamps.decisions))
        paths["saved inside a quick result from minute 30"] = dict(
            pauses=(30,), answer=quick(3), save_after=lambda m, ev: ev.kind == "minute" and ev.minute == 70)
        paths["watched, a goal taken back, seed 70"] = dict(seed=70, pauses=(20, 60), answer=stamps.decisions)
        taken_back = 0
        for name, kw in paths.items():
            events, result, counts = self.play(**kw)
            taken_back += sum(ev.kind == "goal_disallowed" for ev in events)
            self.assertTrue(sum(result["score"]) > 0, name)
            self.assertEqual(self.goal_problems(events, result, counts)[:5], [], name)
        self.assertGreater(taken_back, 0)

    def test_event_stream_is_in_the_originals_write_order(self):
        # PR 251 review round 2, R2: across kinds, the events come in the order of the original's writes (E033
        # stamps.py's own hooks): seed 70's take-back at minute 29 comes after the lines written before it
        sys.path.insert(0, str(ROOT / "experiments" / "E033-original-match-kit"))
        import stamps
        import original_match
        want, got = stamps.run(original_match, self.image, seed=70, policy=stamps.decisions, pause_at=(20, 60))
        self.assertIn("goal_disallowed", [o[0] for o in want["order"]])
        self.assertGreater(len(want["order"]), 1000)
        self.assertEqual(got["order"], want["order"])

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


    def test_selection_port_refused_eleven_keeps_swap_and_original_message(self):
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21), managed=7, ports=["menus", "selection"])
        refusals = []
        swapped_before_refusal = []
        for ev in m.events():
            if ev.kind == "decision" and ev.data["context"] == "half_time":
                if ev.data.get("refused"):
                    refusals.append(ev.data["refused"])
                    swapped_before_refusal.append((130 not in ev.data["eleven"], 132 in ev.data["eleven"]))
                    m.answer(substitutions=[(121, 133)])
                else:
                    m.answer(substitutions=[(130, 132)])     # the reserve keeper: two keepers
        self.assertEqual(refusals, ["Denmark has too many goalkeepers"])
        self.assertTrue(m.over)
        self.assertEqual(swapped_before_refusal, [(True, True)])
        self.assertGreater(m.ports.calls.get("0791:EA09", 0), 0)


def knockout_events(image, index, policy, **kw):
    from original_match import Match, Fixture
    m = Match(image, Fixture(7, 19, index=index, kind=200), managed=7, **kw)
    events = []
    for ev in m.events():
        events.append(ev)
        if ev.kind == "decision":
            policy(m, ev)
    return m, events


@unittest.skipIf(Machine is None or not IMAGE.is_file(), "unicorn or the E006-r0001 image (.cache/dl) missing")
class CompetitiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = IMAGE.read_bytes()
        assert hashlib.sha256(data).hexdigest() == IMAGE_SHA
        cls.image = Image.from_savestate(data)

    def test_kinds_and_budget_arguments(self):
        from original_match import Match, Fixture
        for kind in (0, 4, 9, 204):          # 4 is a decider no builder writes (F023 section 9); 9, 204: none
            with self.assertRaises(ValueError):
                Match(self.image, Fixture(7, 19, index=21, kind=kind), managed=7)
        for budget in (256, -1, (5,), (1, 2, 3), "5"):
            with self.assertRaises(ValueError):
                Match(self.image, Fixture(7, 19, index=21, kind=200), managed=7, substitutions=budget)

    def test_penalties_after_extra_time(self):
        # index 42, kind 200, every decision played on: 0-0 after 90 and 120 minutes, 3-2 on penalties in sudden
        # death (12 kicks; E034 probe-kinds-20261016d, stamps-competitive-20261016a)
        from original_match import MatchError
        from original_match.check import goal_problems
        refused = []

        def policy(m, ev):
            m.answer()

        m, events = knockout_events(self.image, 42, policy)
        r = m.result()
        kinds = [e.kind for e in events]
        self.assertEqual(kinds.count("extra_time"), 1)
        et = events[kinds.index("extra_time")]
        self.assertEqual((et.minute, list(et.score)), (89, r["score_90"]))
        self.assertEqual(r["score_90"][0], r["score_90"][1])
        halves = [e.data["half"] for e in events if e.kind == "decision" and e.data["context"] == "extra_time"]
        self.assertEqual(halves, [1, 2])
        self.assertEqual(kinds.count("shootout"), 1)
        self.assertLess(kinds.index("shootout"), kinds.index("full_time"))      # the board after the shoot-out
        so = r["shootout"]
        kicks = [e.data for e in events if e.kind == "shootout_kick"]
        self.assertEqual(len(kicks), len(so["kicks"]))
        self.assertGreater(len(kicks), 10)                                        # sudden death
        self.assertEqual(so["score"], [sum(k["scored"] for k in kicks if k["team"] == t) for t in (0, 1)])
        self.assertEqual(r["winner"], 0 if so["score"][0] > so["score"][1] else 1)
        self.assertEqual([k["team"] for k in kicks[:2]], [1 - kicks[1]["team"], kicks[1]["team"]])   # alternate
        self.assertEqual(goal_problems(events, r), [])
        self.assertEqual((r["kind"], r["extra_time"], r["substitution_budget"]), (200, True, [2, 2]))
        self.assertEqual(r["board"]["final_score"], [r["score"][t] + so["score"][t] for t in (0, 1)])
        # the kit takes no pause in the shoot-out: the `shootout` event is the one moment a client could ask (the
        # order decision then waits, and after its answer the kicks run to the board in one stretch, as no tick
        # comes between them)
        from original_match import Match, Fixture
        m2 = Match(self.image, Fixture(7, 19, index=42, kind=200), managed=7)
        for ev in m2.events():
            if ev.kind == "decision":
                m2.answer()
            if ev.kind == "shootout":
                with self.assertRaises(MatchError) as caught:
                    m2.pause()
                refused.append(str(caught.exception))
                break
        self.assertEqual(len(refused), 1)
        self.assertIn("shoot-out", refused[0])

    def test_goal2s_shootout_order(self):
        # index 9, kind 200, a quick result from half time: Povlsen (131) sent off, level, and with the original's
        # order (Enter: the eleven from the top) 24 kicks (E034 probe-kinds-20261016e). goal2's order, the available
        # reversed, is refused when invalid and then taken kick by kick; with the default order the takers come
        # round again after the tenth (the eleventh entry is empty after the sending off: A006 skips it).
        def run(order_of):
            orders = []

            def policy(m, ev):
                d = ev.data
                if d["context"] == "half_time":
                    m.answer(quick=True)
                elif d["context"] == "shootout_order":
                    self.assertEqual((d["takers"], len(d["available"])), (10, 10))
                    self.assertNotIn(131, d["available"])
                    with self.assertRaises(ValueError):
                        m.answer(shootout_order=[d["bench"][0]])                 # not one of the eleven
                    with self.assertRaises(ValueError):
                        m.answer(shootout_order=[131])                           # sent off
                    with self.assertRaises(ValueError):
                        m.answer(shootout_order=[d["available"][0]] * 2)         # twice
                    with self.assertRaises(ValueError):
                        m.answer(shootout_order=d["available"][:1], tactics={4: True})
                    orders.append(order_of(d["available"]))
                    m.answer(shootout_order=orders[0])
                else:
                    m.answer()

            m, events = knockout_events(self.image, 9, policy)
            ours = [e.data for e in events if e.kind == "shootout_kick" and e.data["team"] == 0]
            self.assertEqual([k["round"] for k in ours], list(range(1, len(ours) + 1)))
            r = m.result()                      # 1-1 after 120 minutes: the board's bytes hold both
            kicks = [sum(e.data["scored"] for e in events if e.kind == "shootout_kick" and e.data["team"] == t)
                     for t in (0, 1)]
            self.assertEqual((r["score"], r["shootout"]["score"]), ([1, 1], kicks))
            self.assertEqual(r["board"]["final_score"], [1 + kicks[0], 1 + kicks[1]])
            return orders[0], [k["player"] for k in ours]

        order, ours = run(lambda avail: list(reversed(avail)))
        self.assertGreaterEqual(len(ours), 5)
        self.assertEqual(ours, order[:len(ours)])
        order, ours = run(lambda avail: [])                             # the original's: Enter from the top
        self.assertGreater(len(ours), 10)
        self.assertEqual(ours, [121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 121, 122][:len(ours)])

    def test_substitution_budget_is_settable_per_side(self):
        # goal2's own rule is its choice (the owner, 2026-10-15): here 5 for goal2's side, where the original allows 2
        # in a competitive fixture, and 0 for the computer's, whose rule (8062) then makes none
        made = []

        def policy(m, ev):
            d = ev.data
            if d["context"] == "half_time" and not made:
                self.assertEqual(d["substitutions_left"], 5)
                pos = dict(d["positions"])
                subs = [(off, on) for off, on in zip(d["eleven"][8:11], [w for w in d["bench"] if w and pos[w] != 0])]
                made.extend(subs)
                m.answer(substitutions=subs, quick=True)
            else:
                m.answer()

        m, events = knockout_events(self.image, 30, policy, substitutions=(5, 0))
        r = m.result()
        self.assertEqual(r["substitution_budget"], [5, 0])
        self.assertEqual(len(made), 3)
        self.assertEqual([(s["off"], s["on"]) for s in r["substitutions"] if s["team"] == 0][:3], made)
        self.assertEqual([s for s in r["substitutions"] if s["team"] == 1], [])
        defaults = knockout_events(self.image, 30, lambda m, ev: m.answer(quick=True) if ev.data["context"] == "half_time"
                                   else m.answer())[0].result()
        self.assertEqual(defaults["substitution_budget"], [2, 2])

    def test_selection_port_substitution_budget_per_side(self):
        # goal2's own rule is its choice (the owner, 2026-10-15): here 5 for goal2's side, where the original allows 2
        # in a competitive fixture, and 0 for the computer's, whose rule (8062) then makes none
        made = []

        def policy(m, ev):
            d = ev.data
            if d["context"] == "half_time" and not made:
                self.assertEqual(d["substitutions_left"], 5)
                pos = dict(d["positions"])
                subs = [(off, on) for off, on in zip(d["eleven"][8:11], [w for w in d["bench"] if w and pos[w] != 0])]
                made.extend(subs)
                m.answer(substitutions=subs, quick=True)
            else:
                m.answer()

        m, events = knockout_events(self.image, 30, policy, substitutions=(5, 0), ports=["menus", "selection"])
        r = m.result()
        self.assertEqual(r["substitution_budget"], [5, 0])
        self.assertEqual(len(made), 3)
        self.assertEqual([(s["off"], s["on"]) for s in r["substitutions"] if s["team"] == 0][:3], made)
        self.assertEqual([s for s in r["substitutions"] if s["team"] == 1], [])
        defaults = knockout_events(self.image, 30, lambda m, ev: m.answer(quick=True) if ev.data["context"] == "half_time"
                                   else m.answer())[0].result()
        self.assertEqual(defaults["substitution_budget"], [2, 2])

    def test_extra_time_goal_marked(self):
        # index 30, kind 200, played on: 2-2 after 90 minutes, 3-2 after extra time (probe-kinds-20261016d)
        m, events = knockout_events(self.image, 30, lambda m, ev: m.answer())
        r = m.result()
        self.assertEqual((r["score_90"], r["score"], r["shootout"]), ([2, 2], [3, 2], None))
        start = [e.kind for e in events].index("extra_time")
        late = [e for e in events[start:] if e.kind == "goal"]
        self.assertEqual(len(late), 1)
        self.assertEqual([bool(g.get("extra_time")) for g in r["goals"]], [False] * 4 + [True])
        self.assertEqual(r["winner"], 0)

    def test_competitive_stream_is_in_the_originals_write_order(self):
        # E034 stamps_competitive.py's own hooks (E033's, plus extra time at 9B15, the shoot-out at A10A, a kick's
        # end at A1EF with its side from DS:8319): index 9 as a quick result from half time, 24 kicks
        sys.path.insert(0, str(ROOT / "experiments" / "E034-kit-competitive"))
        import stamps_competitive as E034
        import original_match
        want, got, r = E034.run(original_match, self.image, index=9, kind=200, policy=E034.quick_at_half_time)
        kinds = [o[0] for o in want["order"]]
        self.assertEqual((kinds.count("extra_time"), kinds.count("shootout"), kinds.count("shootout_kick")), (1, 1, 24))
        self.assertEqual(len(r["shootout"]["kicks"]), 24)
        self.assertEqual(got, want)

    def test_consequences_of_a_sending_off(self):
        # seed 1 at calendar number 40, kind 200: Povlsen (131) is sent off at 15' (E034 probe-kinds-20261016b); the
        # post-match update B7FA turns the red card into a ban for the next fixture (B27F: element 6 -> element 8,
        # status 0x80, F027 section 2), which result()["players"] reports with the before and after bytes
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=40, kind=200), managed=7, seed=1)
        for ev in m.events():
            if ev.kind == "decision":
                m.answer()
        r = m.result()
        self.assertEqual([(s["team"], s["player"], s["minute"]) for s in r["sendings_off"]], [(0, 131, 15)])
        p = {q["player"]: q for q in r["players"]}
        self.assertEqual((p[131]["status"], p[131]["suspended"]), ([0, 0x80], True))
        self.assertEqual([w for w, q in p.items() if q["suspended"]], [131])
        self.assertEqual(len(p), 40)
        for q in p.values():
            self.assertEqual(len(q["confidence"]) + len(q["energy"]), 4)
            self.assertEqual(q["injured"], q["energy"][1] == 0)

    def test_qualifier(self):
        # kind 2 (a group match): not a decider, so no extra time even when level; the budget is 2; after it
        # run_match shows the competition's table (E929 -> 1771:958D), answered with one key
        from original_match import Match, Fixture
        m = Match(self.image, Fixture(7, 19, index=21, kind=2), managed=7)
        events = []
        for ev in m.events():
            events.append(ev)
            if ev.kind == "decision":
                m.answer()
        r = m.result()
        self.assertEqual((r["kind"], r["substitution_budget"], r["extra_time"], r["shootout"]), (2, [2, 2], False, None))
        self.assertFalse(any(e.kind in ("extra_time", "shootout", "shootout_kick") for e in events))
        self.assertEqual(r["winner"], 2 if r["score"][0] == r["score"][1] else int(r["score"][0] < r["score"][1]))
        self.assertEqual({p["team"] for p in r["players"]}, {0, 1})


if __name__ == "__main__":
    unittest.main()
