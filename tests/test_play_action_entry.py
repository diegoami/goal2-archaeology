"""T130 (#705): Route(entry="play_action"), the manager menu's Play action by main_menu_loop 000E:7439's own code.

Controls (fast; the original under Unicorn on the published E006-r0001 state, no managed match is played: where a
press reaches the match the harness's _match is replaced by a stop, and the rest end at a synthetic round's end):

- the entry set, its refusals and that construction writes nothing;
- the two existing entries' sites, stacks and return contracts, as literals, and that play_round's own frame (70D1) and
  F1F6 stop are the same through play_action (the Play action calls 70B9 as it did);
- the press's order is the original's: the harness hooks no pre-step routine (57E5, 56F3, 5CF4, ...), and what the
  original's code decides is in the record: retirements, finals_news, play_round;
- a press that replaces a retiree ends at 77CB without play_round, as 57E5's return ends it (the retiree's 20 bytes
  zeroed, a fresh record in the slot, the flag +0x4D+m set); the next press plays;
- at a synthetic round's end the press leaves exactly the memory play_round leaves.

ActualEntry (the original-versus-port comparison, Done-when 2) is not here: the port has no 57E5, 56F3, 54F0, 544D,
50D4, 1771:1B2E, 1771:4CF7, 5CF4 or 5AC5, and PortMachine refuses an unregistered address (see
PortGap, which records the gap).
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import route as R  # noqa: E402
from original_match.image import Image, GAME_PTR  # noqa: E402
from original_match.machine import MEM_SIZE  # noqa: E402
from original_match.match import SS_PARAGRAPH  # noqa: E402

IMAGE = ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav"
IMAGE_SHA = "e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d"
PLAYERS_PTR, COUNTRIES_PTR, ACTIONS = 0xA91B, 0xA917, ("action",)


class _Stopped(Exception):
    """The match is not played: the control has what it needs at 6F18."""


def _stop_at_the_match(route):
    def stop():
        # what _match records first, then no match: the stop's registers are the harness's, as _match takes them
        regs = {k: route.m.reg(k) for k in ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eflags", "cs",
                                              "ds", "es", "ss", "fs", "gs")}
        route.record.append(("stop", R.MATCH_AT, regs))
        raise _Stopped()
    route._match = stop
    return route


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import hashlib
        try:
            import unicorn  # noqa: F401
        except ImportError as exc:
            raise AssertionError("T130's controls need unicorn (pip install -r runtime/emul/requirements.txt)") from exc
        if not IMAGE.is_file():
            raise AssertionError(f"{IMAGE} is missing: gh release download E006 --pattern {IMAGE.name} --dir .cache/dl")
        cls.data = IMAGE.read_bytes()
        if hashlib.sha256(cls.data).hexdigest() != IMAGE_SHA:
            raise AssertionError(f"{IMAGE} is not the published E006-r0001 state")

    def image(self):
        return Image.from_savestate(self.data)

    def route(self, entry, **kw):
        return R.Route(self.image(), entry=entry, **kw)

    # -- the entry set ----------------------------------------------------------------------------------------
    def test_the_entry_is_accepted_and_the_set_keeps_its_order(self):
        self.assertEqual(R.ENTRIES, ("route_fixture", "play_round", "play_action"))
        for entry in R.ENTRIES:
            self.assertEqual(self.route(entry).entry, entry)

    def test_an_unknown_entry_is_refused_before_anything_is_made(self):
        image = self.image()
        before = bytes(image.memory)
        for entry in ("main", "play", "PLAY_ACTION", "", None, "menu_action"):
            with self.subTest(entry=entry), self.assertRaisesRegex(ValueError, "entry .*: one of route_fixture, "
                                                                   "play_round, play_action"):
                R.Route(image, entry=entry)
        self.assertEqual(bytes(image.memory), before)

    def test_an_image_that_is_not_the_registered_build_is_refused_for_the_new_entry_too(self):
        image = self.image()
        base = image.load * 16
        image.memory[base + 0x772A] ^= 0xFF      # a code byte of the branch itself
        for entry in R.ENTRIES:
            with self.subTest(entry=entry), self.assertRaisesRegex(ValueError, "does not hold the registered"):
                R.Route(image, entry=entry)

    def test_constructing_writes_nothing_and_the_image_is_untouched(self):
        image = self.image()
        before = bytes(image.memory)
        r = R.Route(image, entry="play_action")
        self.assertEqual(bytes(image.memory), before)
        self.assertEqual(r.m.read(0, MEM_SIZE), before[:MEM_SIZE])
        self.assertEqual(r.record, [])

    def test_round_takes_the_new_entry_and_still_refuses_route_fixture(self):
        with self.assertRaisesRegex(ValueError, "round\\(\\)"):
            self.route("route_fixture").round()
        r = self._at_the_rounds_end(self.route("play_action"))
        record = r.round()
        self.assertEqual([e for e in record if e[0] == "round_end"],
                         [("round_end", {"cursor": 769, "count": 769, "stage": 2, "rounds": 1})])

    # -- the existing entries, unchanged -----------------------------------------------------------------------
    def test_the_existing_entries_sites_stacks_and_returns_are_the_published_ones(self):
        self.assertEqual((R.ROUTE_FIXTURE, R.CALLER, R.RETURN_TO, R.CALL_SP, R.CALLER_BP),
                         ("000E:6CA7", "000E:70D1", "000E:70D4", 0x3EE0, 0x3EEA))
        self.assertEqual((R.PLAY_ROUND, R.ROUND_CALLER, R.ROUND_RETURN, R.ROUND_SP, R.MENU_BP, R.ROUND_END),
                         ("000E:70B9", "000E:77BF", "000E:77C2", 0x3EEC, 0x3FF6, "000E:70E6"))
        self.assertEqual((R.MATCH_AT, R.MATCH_SP), ("000E:6F18", 0x3EC4))
        self.assertEqual((R.ACTION_AT, R.ACTION_END, R.ACTION_SP, R.ACTION_LOCAL),
                         ("000E:772A", "000E:77CB", 0x3EEE, 0x3FF0))

    def _at_the_first_stop(self, entry):
        """Run one call to the match of the E006-r0001 state's first managed fixture; the frames seen on the way."""
        r = _stop_at_the_match(self.route(entry))
        m = r.m
        ss = m.seg(SS_PARAGRAPH) * 16
        seen = {}
        if entry != "route_fixture":
            m.at("000E:70D1", lambda replay: replay or seen.setdefault("70D1", (
                m.reg("sp"), m.reg("bp"), m.word_at(ss + 0x3EEA), m.word_at(ss + 0x3EEC),
                m.read(m.far(GAME_PTR) + 1, 1)[0])))
        else:
            m.at("000E:6CA7", lambda replay: replay or seen.setdefault("6CA7", (
                m.reg("sp"), m.reg("bp"), m.word_at(ss + R.CALL_SP))))
        try:
            r.call()
        except _Stopped:
            pass
        else:
            self.fail("no stop at the match")
        stop = next(e for e in r.record if e[0] == "stop")
        return r, seen, (stop[1], stop[2]["esp"] & 0xFFFF, stop[2]["ebp"] & 0xFFFF)

    def test_play_round_and_route_fixture_keep_their_frames_and_the_stop(self):
        _, seen, stop = self._at_the_first_stop("play_round")
        self.assertEqual(seen["70D1"], (0x3EE2, 0x3EEA, 0x3FF6, 0x77C2, 1))
        self.assertEqual(stop, ("000E:6F18", 0x3EC4, 0x3EDE))
        r, seen, stop = self._at_the_first_stop("route_fixture")
        self.assertEqual(seen["6CA7"], (0x3EE0, 0x3EEA, 0x70D4))
        self.assertEqual(stop, ("000E:6F18", 0x3EC4, 0x3EDE))
        self.assertNotIn("action", [e[0] for e in r.record])

    def test_the_play_action_reaches_play_round_in_play_rounds_own_frame(self):
        r, seen, stop = self._at_the_first_stop("play_action")
        self.assertEqual(seen["70D1"], (0x3EE2, 0x3EEA, 0x3FF6, 0x77C2, 1))
        self.assertEqual(stop, ("000E:6F18", 0x3EC4, 0x3EDE))

    # -- the order is the original's ---------------------------------------------------------------------------
    def test_the_harness_hooks_no_routine_of_the_pre_step(self):
        r = self.route("play_action")
        hooked = set(r.m._handlers)
        for site in ("000E:57E5", "000E:56F3", "000E:54F0", "000E:544D", "000E:50D4", "000E:5CF4", "000E:5AC5",
                     "000E:7072", "000E:70B9", "000E:7785", "000E:772A"):
            self.assertNotIn(r.m.lin(site), hooked, site)
        # the hooks it has are observations at the decisions (ACTION_SITES), the shared ones, and nothing else
        extra = {r.m.lin(s) for s in R.ACTION_SITES}
        plain = set(self.route("play_round").m._handlers)
        self.assertEqual(hooked - plain, extra)
        self.assertEqual(plain - hooked, set())

    def test_one_press_decides_in_the_original_order(self):
        r = _stop_at_the_match(self.route("play_action"))
        with self.assertRaises(_Stopped):
            r.call()
        self.assertEqual([e for e in r.record if e[0] == "action"],
                         [("action", "retirements", 0), ("action", "finals_news", 0), ("action", "play_round")])
        # 57E5 and 5CF4 ran before 70B9, as guest code: the record's stop is in 70B9's round, not before
        kinds = [e[0] for e in r.record if e[0] in ("action", "stop")]
        self.assertEqual(kinds, ["action", "action", "action", "stop"])

    def _with_a_retiree(self):
        """E006-r0001's state in year 1 with the managed country's first squad player past retirement (age 60,
        no caps): 57E5's first squad scan retires him (1771:7F40; F016, F017)."""
        image = self.image()
        ds = image.DS * 16

        def far(off):
            return image.rd(off + 2) * 16 + image.rd(off)
        game = far(GAME_PTR)
        image.memory[game + 0x38:game + 0x3A] = (1).to_bytes(2, "little")
        manager = image.memory[game + 1]
        country = image.memory[far(0xA91F) + (manager + 0x80) * 3]
        rec = far(COUNTRIES_PTR) + 0xBF * country
        slot0 = int.from_bytes(image.memory[rec:rec + 2], "little")
        player = far(PLAYERS_PTR) + 0x14 * slot0
        image.memory[player + 1] = 60
        image.memory[player + 8:player + 10] = bytes(2)
        self.assertEqual(manager, 1)
        return R.Route(image, entry="play_action"), country, slot0

    def test_a_press_that_replaces_a_retiree_ends_without_play_round(self):
        r, country, retiree = self._with_a_retiree()
        m = r.m
        game = m.far(GAME_PTR)
        cursor = m.word_at(game + 0x26)
        before = m.read(m.far(PLAYERS_PTR) + 0x14 * retiree, 20)
        self.assertNotEqual(before, bytes(20))
        r.call()
        self.assertEqual([e for e in r.record if e[0] == "action"], [("action", "retirements", 1)])
        self.assertEqual(r.record[-1], ("return", "000E:77CB"))
        self.assertEqual([e[0] for e in r.record if e[0] in ("stop", "match", "round_end")], [])
        self.assertEqual((m.reg("sp"), m.reg("bp")), (0x3EEE, 0x3FF6))
        self.assertEqual(m.word_at(game + 0x26), cursor)                       # no fixture was routed
        self.assertEqual(m.read(m.far(PLAYERS_PTR) + 0x14 * retiree, 20), bytes(20))   # the retiree: zeroed (57C0)
        rec = m.far(COUNTRIES_PTR) + 0xBF * country
        fresh = m.word_at(rec)
        self.assertNotEqual(fresh, retiree)
        self.assertNotEqual(m.read(m.far(PLAYERS_PTR) + 0x14 * fresh, 20), bytes(20))   # a fresh record in its slot
        self.assertEqual(m.read(game + 0x4D + 1, 1)[0], 1)                      # the flag 56F3 sets (570D)
        self.assertEqual(r.replay(r.origin), m.read(0, MEM_SIZE))               # every write is in the record

    def test_the_next_press_plays_because_the_original_says_so(self):
        r, _, _ = self._with_a_retiree()
        r.call()
        _stop_at_the_match(r)
        with self.assertRaises(_Stopped):
            r.call()
        self.assertEqual([e for e in r.record if e[0] == "action"],
                         [("action", "retirements", 1),
                          ("action", "retirements", 0), ("action", "finals_news", 0), ("action", "play_round")])

    # -- play_round is not disturbed ------------------------------------------------------------------------------
    @staticmethod
    def _at_the_rounds_end(r):
        game = r.m.far(GAME_PTR)
        r._write("T124a's synthetic input: the cursor +0x26 := the count +0x28", game + 0x26, r.m.read(game + 0x28, 2))
        return r

    def test_at_a_rounds_end_the_press_leaves_the_memory_play_round_leaves(self):
        a = self._at_the_rounds_end(self.route("play_round"))
        a.call()
        b = self._at_the_rounds_end(self.route("play_action"))
        b.call()
        self.assertEqual(a.m.read(0, MEM_SIZE), b.m.read(0, MEM_SIZE))
        self.assertEqual(a.record[-1], ("return", "000E:77C2"))
        self.assertEqual(b.record[-1], ("return", "000E:77CB"))
        self.assertEqual(a.m.reg("sp"), 0x3EEE)
        self.assertEqual(b.m.reg("sp"), 0x3EEE)
        shared = ("round_end", "key", "rng", "match", "stop", "resume", "team")
        self.assertEqual([e for e in a.record if e[0] in shared], [e for e in b.record if e[0] in shared])
        self.assertEqual(b.replay(b.origin), b.m.read(0, MEM_SIZE))

    def test_the_harness_makes_the_one_local_the_branch_reads(self):
        """[bp-6] is 7440-7447's copy of DS:A923: with the stack word cleared in the image, the press still finds the
        game record, and ends with the word the state held."""
        image = self.image()
        ss = (image.load + SS_PARAGRAPH) * 16
        want = bytes(image.memory[ss + R.ACTION_LOCAL:ss + R.ACTION_LOCAL + 4])
        self.assertEqual(want, bytes(image.memory[image.DS * 16 + GAME_PTR:image.DS * 16 + GAME_PTR + 4]))
        image.memory[ss + R.ACTION_LOCAL:ss + R.ACTION_LOCAL + 4] = bytes(4)
        r = self._at_the_rounds_end(R.Route(image, entry="play_action"))
        r.call()
        self.assertEqual(r.m.read(ss + R.ACTION_LOCAL, 4), want)
        self.assertEqual(r.record[-1], ("return", "000E:77CB"))
        self.assertEqual([e[1] for e in r.record if e[0] == "k" and e[1].startswith("main_menu_loop")],
                         ["main_menu_loop 7439's [bp-6]: the game record pointer, as 7440-7447 load it from DS:A923"])



class PortGap(unittest.TestCase):
    def test_the_port_has_no_pre_step(self):
        """Records the gap Done-when 2 meets: no registered port covers these, so the sealed route (PortMachine, which
        refuses an unregistered address) cannot run the Play action's pre-step. It fails the day one is ported: then
        the sealed entry can be built, and this test is replaced by its proof."""
        from original_match import port
        registered = {a for reg, _ in port.load(["all"]) for a, e in reg.entries.items() if e.stub is None}
        missing = {"000E:57E5", "000E:56F3", "000E:54F0", "000E:544D", "000E:50D4", "1771:1B2E", "1771:4CF7",
                   "000E:5CF4", "000E:5AC5"}
        self.assertEqual(missing & registered, set())


if __name__ == "__main__":
    unittest.main()
