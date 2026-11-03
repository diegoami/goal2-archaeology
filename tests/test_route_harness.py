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
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import route as R  # noqa: E402
from original_match.machine import GuestError, MEM_SIZE  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
