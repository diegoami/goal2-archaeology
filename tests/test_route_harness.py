"""runtime/original_match/route.py (T119a, #427): one call of the original's route_fixture 000E:6CA7 on a kit Machine.

- KeyPolicyTests (no emulator): the default policy names every read and poll site route.py catalogues; a key found
  at the first poll waits until a read takes it (the owner's 2026-11-03 rule: 04F5's tune stops at once, 0572's
  animation runs once); a poll answered None finds no key; a site the policy does not name, and a read the policy
  gives no key, raise.
- RouteTests (unicorn and the published E006-r0001 state, `.cache/dl`, as tests/test_original_match.py; skipped
  without either, saying which): from the manager menu with the managed friendly 27 v 7 next (fixture 1), with a
  Prover installed on the machine (port/prove.py, no ports: it refuses a machine with a foreign hook or a tap), one
  call stops at 000E:6F18 in Match's frame, plays the match by Match(tail=False), which ends at 000E:6F1D, resumes
  there with SP + 4, runs route_fixture's own B7FA once as guest code and returns to 000E:70D4. The record replayed
  over the start memory gives the memory the call left (every write is in it), each RNG word's steps chain from its
  start value to its end value, the news page's read 000E:0629 is in it, answered from the policy; and a policy
  without 000E:0629 raises there.
- CompetitiveRouteTests (T119c, #647; unicorn and the published E015-r0009 state 3, `.cache/dl`, fetched by E040's
  runner `--fetch`; skipped without either): from the manager menu with the managed qualifier 16 v 3 next (fixture
  22, kind 2, round 6 in its +1), one call with the default policy plays it through Match(tail=False), whose set-up
  writes nothing route_fixture had not left (no inputs), resumes at 000E:6F1D and returns; the confidence term
  B71C/B6CC (000E:6F80, 6F86) runs for both sides; every write is in the record.
- ProvedRouteTests (T119c, #647; unicorn and the published E006-r0004 state, E040-r0004's, fetched by E040's runner
  `--fetch`): with Route(record_writes=False) and the ports postmatch, update, quick and setup installed, a Prover
  on the Route's machine proves every armed call of one call (each port call proved, or nested in a proved one);
  the record keeps the seeds' steps, the key visits and the 6F18 stop, holds no guest write, and replay() refuses it.
- DefaultFixtureTests (the same state as CompetitiveRouteTests): a default Match still writes its fixture record FE 00 kind 00 first second
  (the round byte +1 := 0, its memory otherwise the image's but for its declared inputs), and only Match(tail=False)
  keeps +1 and +3.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import route as R  # noqa: E402
from original_match.machine import GuestError, MEM_SIZE  # noqa: E402
from original_match.match import SS_PARAGRAPH  # noqa: E402

IMAGE = ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav"
IMAGE_SHA = "e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d"
FETCH = ("gh release download E006 --pattern e0afff6751747233-e006-1000-r0001.sav --dir .cache/dl "
         "(as .github/workflows/family-run.yml)")

try:
    import unicorn  # noqa: F401
    HAVE_UNICORN = True
except ImportError:
    HAVE_UNICORN = False


class KeyPolicyTests(unittest.TestCase):
    def test_the_default_policy_names_every_catalogued_site(self):
        self.assertEqual(set(R.DEFAULT_KEYS), set(R.READS) | set(R.POLLS))
        self.assertEqual(R.DEFAULT_KEYS["214B:157C<0791:E86E"], R.KEY_N)     # the watch prompt: declined
        self.assertEqual(R.DEFAULT_KEYS["000E:0629"], R.ENTER)

    def test_the_table_reads_are_in_the_default_policy(self):
        # 6970's score page for a 0xFE fixture reaches 0791:E929's table screen: Match answers it Enter (T119c)
        from original_match.match import TABLE_READS, TABLE_KEY
        for caller in TABLE_READS:
            self.assertEqual(R.DEFAULT_KEYS[R.MENU_SITE + "<" + caller], R.ENTER, caller)
        self.assertEqual(R.DEFAULT_KEYS[TABLE_KEY], R.ENTER)
        self.assertEqual(set(R.DEFAULT_KEYS) - set(R.READS) - set(R.POLLS), set())

    def test_a_key_at_the_first_poll_waits_for_the_read(self):
        k = R.Keys(R.DEFAULT_KEYS)
        self.assertEqual(k.poll("000E:0515"), (True, "policy"))           # 04F5: a key before the first note
        self.assertEqual(k.poll("000E:05EC"), (True, "waiting"))          # 0572: one 045D, then the same key
        self.assertEqual(k.poll("000E:05EC"), (True, "waiting"))
        self.assertEqual(k.read("000E:0629"), (R.ENTER, "waiting"))       # 05F6 takes it
        self.assertIsNone(k.waiting)
        self.assertEqual(k.read("000E:0629"), (R.ENTER, "policy"))        # a read with none waiting: the policy's

    def test_a_poll_answered_none_finds_no_key(self):
        k = R.Keys({"000E:6BF7": None, "000E:6B92": 0xAE})
        self.assertEqual(k.poll("000E:6BF7"), (False, "policy"))
        self.assertIsNone(k.waiting)
        self.assertEqual(k.read("000E:6B92", None), (0xAE, "policy"))
        k = R.Keys({"000E:6B89": lambda route, site: 0x20})                 # a callable answer
        self.assertEqual(k.poll("000E:6B89"), (True, "policy"))
        self.assertEqual(k.waiting, 0x20)

    def test_a_site_without_an_answer_raises(self):
        with self.assertRaisesRegex(GuestError, "000E:0629 has no answer"):
            R.Keys({}).read("000E:0629")
        with self.assertRaisesRegex(GuestError, "000E:05EC has no answer"):
            R.Keys({"000E:0629": R.ENTER}).poll("000E:05EC")
        with self.assertRaisesRegex(GuestError, "gives no key"):
            R.Keys({"000E:0629": None}).read("000E:0629")


@unittest.skipUnless(HAVE_UNICORN, "unicorn missing (pip install -r runtime/emul/requirements.txt)")
@unittest.skipUnless(IMAGE.is_file(), f"the published E006-r0001 state {IMAGE.relative_to(ROOT)} is absent: {FETCH}")
class RouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import hashlib
        from original_match import port
        from original_match.image import Image
        from original_match.port.prove import Prover
        data = IMAGE.read_bytes()
        if hashlib.sha256(data).hexdigest() != IMAGE_SHA:
            raise AssertionError(f"{IMAGE} is not the published E006-r0001 state")
        cls.image = Image.from_savestate(data)
        cls.r = r = R.Route(cls.image)
        cls.b7fa = []
        r.m.at("0791:B7FA", lambda replay: replay or cls.b7fa.append(r.m.reg("sp")))
        cls.prover = Prover(r.m, port.install(r.m, []))   # refuses a machine with a foreign hook or a tap
        cls.record = r.call()

    def test_the_machine_is_provable(self):
        self.assertEqual(self.r.m.foreign_hooks, 0)
        self.assertTrue(self.r.m.proving)
        self.assertEqual(sum(self.prover.proved.values()), 0)

    def test_one_call_stops_at_6F18_plays_the_match_and_resumes(self):
        kinds = [e[0] for e in self.record if e[0] in ("stop", "match", "resume", "return")]
        self.assertEqual(kinds, ["stop", "match", "resume", "return"])
        stop = next(e for e in self.record if e[0] == "stop")
        self.assertEqual(stop[1], "000E:6F18")
        self.assertEqual((stop[2]["esp"] & 0xFFFF, stop[2]["ebp"] & 0xFFFF), (0x3EC4, 0x3EDE))
        match = next(e[1] for e in self.record if e[0] == "match")
        self.assertEqual((match["fixture"], match["first"], match["second"], match["kind"], match["managed"]),
                         (1, 27, 7, 1, 7))
        resume = next(e for e in self.record if e[0] == "resume")
        self.assertEqual(resume[1:], ("000E:6F1D", 0x3EC8))
        m = self.r.matches[0]
        self.assertIs(m.opts["tail"], False)
        self.assertEqual(m.st["phase"], "done")
        self.assertEqual(m.m.pc(), m.m.lin("000E:6F1D"))                  # Match's machine: never into B7FA
        self.assertEqual(self.b7fa, [0x3EC0])                              # route_fixture's own, at 6FF8
        self.assertEqual(self.r.m.pc(), self.r.m.lin("000E:70D4"))
        self.assertEqual(self.r.m.reg("sp"), 0x3EE2)
        self.assertEqual(self.r.m.word_at(self.r.m.far(0xA923) + 0x26), 2)  # the cursor moved past fixture 1

    def test_every_write_is_in_the_record(self):
        self.assertEqual(self.r.replay(self.r.origin), self.r.m.read(0, MEM_SIZE))
        after = self.record.index(next(e for e in self.record if e[0] == "resume"))
        self.assertTrue(any(e[0] == "w" for e in self.record[after:]))     # the guest's own, after the match
        self.assertTrue(any(e[0] == "k" and e[1] == "match" for e in self.record))

    def test_the_rng_steps_chain(self):
        for name, off in R.SEEDS.items():
            steps = [e for e in self.record if e[0] == "rng" and e[1] == name]
            word = int.from_bytes(self.r.origin[self.r.m.DS * 16 + off:][:2], "little")
            for e in steps:
                self.assertEqual(e[2], word, f"a step of {name} missing before {e}")
                word = e[3]
            self.assertEqual(word, self.r.m.rd(off), name)
        wheres = {e[5] for e in self.record if e[0] == "rng" and e[1] == "7B62"}
        self.assertEqual(wheres, {"route", "match"})

    def test_the_key_visits(self):
        keys = [e for e in self.record if e[0] == "key"]
        self.assertIn(("key", "000E:0629", "read", R.ENTER, "policy"), keys)
        self.assertTrue(all(e[1] in R.DEFAULT_KEYS for e in keys))

    def test_a_key_site_without_an_answer_raises(self):
        keys = {s: k for s, k in R.DEFAULT_KEYS.items() if s != "000E:0629"}
        with self.assertRaisesRegex(GuestError, "000E:0629 has no answer"):
            R.Route(self.image, keys=keys).call()



QUALIFIER = ROOT / ".cache" / "dl" / "46bbf5dabaaa9553-snap-0003-20261011T195415Z.sav"
QUALIFIER_SHA = "46bbf5dabaaa95537b7dd88de00563b9e8594db021fb3d4a75254ed379465bea"   # evidence/E015 manifest
QUALIFIER_FETCH = "python3 -B experiments/E040-route-fixture-writes/runner.py --fetch"
CONFIDENCE = ("000E:6F80", "000E:6F86")     # route_fixture's calls of B71C and B6CC, the side [bp-3] 0, then 1
# (seg_000E_09.asm 6F3B-6F8F: [bp-3] := 0; ... inc; cmp [bp-3], 1; jne)


def _qualifier_image():
    import hashlib
    from original_match.image import Image
    data = QUALIFIER.read_bytes()
    if hashlib.sha256(data).hexdigest() != QUALIFIER_SHA:
        raise AssertionError(f"{QUALIFIER} is not the published E015-r0009 state 3")
    return Image.from_savestate(data)


@unittest.skipUnless(HAVE_UNICORN, "unicorn missing (pip install -r runtime/emul/requirements.txt)")
@unittest.skipUnless(QUALIFIER.is_file(), f"the published E015-r0009 state 3 {QUALIFIER.relative_to(ROOT)} is absent: "
                     f"{QUALIFIER_FETCH}")
class CompetitiveRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = r = R.Route(_qualifier_image())
        m = r.m
        cls.base = m.far(0xA92B) + 8 * 21                 # fixture 22 (FIXTURES_PTR, 8 bytes a fixture)
        cls.before = m.read(cls.base, 8)
        cls.confidence = []

        def hit(site):
            def h(replay):
                if not replay:
                    cls.confidence.append((site, m.read(m.reg("ss") * 16 + m.reg("bp") - 3, 1)[0]))
            return h
        for site in CONFIDENCE:
            m.at(site, hit(site))
        cls.record = r.call()

    def test_the_state(self):
        self.assertEqual(self.before.hex(), "fe06020010000300")    # 16 v 3, kind 2, round 6 in +1

    def test_the_qualifier_plays_through_match_and_resumes(self):
        kinds = [e[0] for e in self.record if e[0] in ("stop", "match", "resume", "return")]
        self.assertEqual(kinds, ["stop", "match", "resume", "return"])
        match = next(e[1] for e in self.record if e[0] == "match")
        self.assertEqual((match["fixture"], match["first"], match["second"], match["kind"], match["managed"]),
                         (22, 16, 3, 2, 16))
        mt = self.r.matches[0]
        self.assertIs(mt.opts["tail"], False)
        self.assertEqual(mt.inputs, [])                    # its set-up found every byte as route_fixture left it
        self.assertEqual(mt.st["phase"], "done")
        resume = next(e for e in self.record if e[0] == "resume")
        self.assertEqual(resume[1:], ("000E:6F1D", 0x3EC8))
        self.assertEqual(self.r.m.pc(), self.r.m.lin("000E:70D4"))
        self.assertEqual(self.r.m.reg("sp"), 0x3EE2)
        self.assertEqual(self.r.m.word_at(self.r.m.far(0xA923) + 0x26), 23)
        after = self.r.m.read(self.base, 8)
        self.assertEqual(list(after[:2]), match["score"])  # the result: the goals in +0, +1, the winner in +3
        self.assertEqual(after[3], match["winner"])

    def test_the_confidence_term_runs_for_both_sides(self):
        self.assertEqual(sorted(self.confidence), sorted([(s, side) for s in CONFIDENCE for side in (0, 1)]))

    def test_every_write_is_in_the_record(self):
        self.assertEqual(self.r.replay(self.r.origin), self.r.m.read(0, MEM_SIZE))


PROVED = ROOT / ".cache" / "dl" / "f8b22081eeb072e5-e006-1337-r0004.sav"           # E040-r0004's state
PROVED_SHA = "f8b22081eeb072e5b371a5b36628a745cc359efcfdabf6dc2cdaab4ebc66263c"   # evidence/E006 manifest


@unittest.skipUnless(HAVE_UNICORN, "unicorn missing (pip install -r runtime/emul/requirements.txt)")
@unittest.skipUnless(PROVED.is_file(), f"the published E006-r0004 state {PROVED.relative_to(ROOT)} is absent: "
                     f"{QUALIFIER_FETCH}")
class ProvedRouteTests(unittest.TestCase):
    """The write listener reads the pc at stack writes, which ports make as 214B:0000 (port/runtime.py STACK_AT), and
    the Prover refuses that; record_writes=False drops only the listener (T119c, T120's probe)."""

    @classmethod
    def setUpClass(cls):
        import hashlib
        from original_match import port
        from original_match.image import Image
        from original_match.port.prove import Prover
        data = PROVED.read_bytes()
        if hashlib.sha256(data).hexdigest() != PROVED_SHA:
            raise AssertionError(f"{PROVED} is not the published E006-r0004 state")
        cls.r = r = R.Route(Image.from_savestate(data), record_writes=False)
        cls.ports = port.install(r.m, ["postmatch", "update", "quick", "setup"])
        cls.prover = Prover(r.m, cls.ports)
        cls.record = r.call()

    def test_every_armed_call_is_proved(self):
        self.assertEqual(self.r.m.foreign_hooks, 0)
        self.assertTrue(self.r.m.proving)
        summary = self.prover.summary()
        self.assertGreater(sum(v["proved"] for v in summary.values()), 0)
        self.assertEqual(sum(v["before"] for v in summary.values()), 0)      # armed from the start
        for routine, n in self.ports.calls.items():
            v = summary[routine]
            self.assertEqual(v["proved"] + v["nested"], n, routine)       # every call: proved, or inside a proved one
        for routine in ("0791:B7FA", "0791:D050", "0791:A3DE", "1771:8757"):   # update, postmatch, setup, quick
            self.assertGreater(summary[routine]["proved"], 0, routine)

    def test_the_call_runs_and_keeps_its_record_but_the_writes(self):
        kinds = [e[0] for e in self.record if e[0] in ("stop", "match", "resume", "return")]
        self.assertEqual(kinds, ["stop", "match", "resume", "return"])
        self.assertEqual(self.r.m.pc(), self.r.m.lin("000E:70D4"))
        self.assertFalse(any(e[0] == "w" for e in self.record))
        self.assertTrue(any(e[0] == "rng" for e in self.record))
        self.assertTrue(any(e[0] == "key" for e in self.record))
        with self.assertRaisesRegex(ValueError, "record_writes=False"):
            self.r.replay(self.r.origin)


@unittest.skipUnless(HAVE_UNICORN, "unicorn missing (pip install -r runtime/emul/requirements.txt)")
@unittest.skipUnless(QUALIFIER.is_file(), f"the published E015-r0009 state 3 {QUALIFIER.relative_to(ROOT)} is absent: "
                     f"{QUALIFIER_FETCH}")
class DefaultFixtureTests(unittest.TestCase):
    """_write_fixture also serves goal2's own matches: the default path stays byte for byte (T119c's hazard)."""

    def _set_up(self, **kw):
        from original_match.match import Match, Fixture
        image = _qualifier_image()
        origin = bytes(image.memory[:MEM_SIZE])
        match = Match(image, Fixture(first=16, second=3, index=22, kind=2), **kw)
        base = match.m.far(0xA92B) + 8 * 21
        return match, origin, base

    def test_a_default_match_writes_its_fixture_as_before(self):
        match, origin, base = self._set_up()
        legacy = bytes([0xFE, 0, 2, 0]) + (16).to_bytes(2, "little") + (3).to_bytes(2, "little")
        self.assertEqual(match.m.read(base, 8), legacy)
        fx = [i for i in match.inputs if i["linear"] == base]
        self.assertEqual(fx, [{"what": "fixture 22 := 16 v 3, kind 2", "linear": base, "old": "fe06020010000300",
                               "new": legacy.hex()}])
        expect = bytearray(origin)                         # the image, with exactly the declared inputs made
        for i in match.inputs:
            new = bytes.fromhex(i["new"])
            expect[i["linear"]:i["linear"] + len(new)] = new
        now = match.m.read(0, MEM_SIZE)
        stack = match.m.seg(SS_PARAGRAPH) * 16             # but for the stack segment, where _call pushes its frame
        self.assertEqual(now[:stack], bytes(expect[:stack]))
        self.assertEqual(now[stack + 0x4000:], bytes(expect[stack + 0x4000:]))

    def test_only_the_route_mode_keeps_the_round_and_plus_3(self):
        match, origin, base = self._set_up(tail=False)
        self.assertEqual(match.m.read(base, 8).hex(), "fe06020010000300")
        self.assertEqual([i for i in match.inputs if i["linear"] == base], [])


if __name__ == "__main__":
    unittest.main()
