"""runtime/original_match/port/stages.py (T124a, #427): stage_end 1771:8208's own part, run_stage 76B1's dispatch and
the builders' shared helpers 5D02, 5D94, 5E3A, 5E99, 6617, each proved against the original by port/prove.py.

- RegistryTests (no emulator): the module ports exactly T124a's seven plus T124b1's seven and T124b2's four routines with the listing's returns; 5C94 and
  5CCB stay display's (one port a routine), and display_helpers() gives those two entries alone, installable beside
  stages.
- DirectProofTests (unicorn and the published E006-r0001 state, `.cache/dl`, as tests/test_route_harness.py; skipped
  without either): each routine called directly on the state's memory, from a return address of one of its real
  callers, with a Prover on the machine: every call is proved (the port and the original write the same bytes in the
  same order and return the same AX, DX, SP, BP), including stage_end's paths (a round left: only the rounds byte;
  stage 3 to 4: no ageing, two rounds; stage 7 to 8: four rounds; stage 8 wrapping to 2: yearly_ageing 80DA runs) and
  run_stage at every stage byte 0..9 (each builder, run as the original's, with the helpers nested in the proof:
  display's 5C94 and 5CCB inside 6E59, 71B2 and 74BE).
  The stage and rounds bytes are set on the state for these calls [designed: T124a]: synthetic inputs of the
  routines, not states the game reaches (the round's ends the published states reach are proved in the route
  harness: experiments/E040-route-fixture-writes/out/T124a/prove.py, tests/test_route_harness.py RoundEndTests).
- FalsifierTests (the same): each variant of stages, and display's omit-1771-5c94 and omit-1771-5ccb, raises
  ProofError on a call that reaches what it changes.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match.port import stages as ST  # noqa: E402

IMAGE = ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav"
IMAGE_SHA = "e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d"
FETCH = "python3 -B experiments/E040-route-fixture-writes/runner.py --fetch"

try:
    import unicorn  # noqa: F401
    HAVE_UNICORN = True
except ImportError:
    HAVE_UNICORN = False

GAME = 0xA923
END = "0000:00D5"           # never reached: the call stops at its return address
# Return addresses of the routines' real callers (the listing's next instruction after each call):
RET = {"1771:8208": "000E:70EB", "1771:76B1": "000E:70F9",      # play_round 70E6, 70F4 (seg_000E_09.asm)
       "1771:5D02": "1771:5DC7", "1771:5D94": "1771:5E54",      # add_fixture 5DC4, add_fixture_with_bonus 5E51
       "1771:5E3A": "1771:6DEE", "1771:5E99": "1771:6B6B",      # 6B55's calls at 6DEB, 6B68 (seg_1771_10.asm)
       "1771:6617": "1771:6E55",                                # 6B55's call at 6E52
       "1771:6730": "1771:76C7",                                # run_stage calls6730 at76C4 (T124b2)
       "1771:63A4": "1771:6765",                                # qualifying builder6730 calls at6762 (T124b1)
       "1771:5C94": "1771:92F9", "1771:5CCB": "1771:9321"}      # 1771:91CE's calls at 92F6, 931E


class RegistryTests(unittest.TestCase):
    def test_the_eighteen_routines_with_the_listings_returns(self):
        self.assertEqual({a: e.ret for a, e in ST.PORTS.entries.items()},
                         {"1771:8208": "retf", "1771:76B1": "retf", "1771:5D02": "ret 4", "1771:5D94": "ret 8",
                          "1771:5E3A": "ret 0xa", "1771:5E99": "ret 2", "1771:6617": "ret 2",
                          "1771:114B": "retf 2", "1771:5EE1": "ret 6", "1771:5FD1": "ret 0xa",
                          "1771:602D": "ret 2", "1771:6103": "ret 2", "1771:61F8": "ret 2", "1771:63A4": "ret",
                          "1771:56E4": "ret 2", "1771:56FF": "ret", "1771:6730": "ret", "23E4:11D7": "retf"})

    def test_5C94_and_5CCB_are_displays_and_installable_beside_stages(self):
        from original_match import port
        from original_match.port import display
        reg = ST.display_helpers()
        self.assertEqual(set(reg.entries), {"1771:5C94", "1771:5CCB"})
        for a in reg.entries:
            self.assertIs(reg.entries[a], display.PORTS.entries[a])
            self.assertNotIn(a, ST.PORTS.entries)
        self.assertEqual(set(reg.variants), {"omit-1771-5c94", "omit-1771-5ccb"})
        loaded = port.load(["stages", (reg, None)])
        self.assertEqual([r.name for r, _ in loaded], ["stages", "display"])

    def test_the_builders_by_stage(self):
        self.assertEqual({s: b for s, (b, _) in ST.BUILDERS.items()},
                         {2: "1771:6730", 5: "1771:6730", 3: "1771:6B55", 4: "1771:6E59", 6: "1771:7090",
                          7: "1771:71B2", 8: "1771:74BE"})


def _image():
    import hashlib
    from original_match.image import Image
    data = IMAGE.read_bytes()
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA:
        raise AssertionError(f"{IMAGE} is not the published E006-r0001 state")
    return Image.from_savestate(data)


@unittest.skipUnless(HAVE_UNICORN, "unicorn missing (pip install -r runtime/emul/requirements.txt)")
@unittest.skipUnless(IMAGE.is_file(), f"the published E006-r0001 state {IMAGE.relative_to(ROOT)} is absent: {FETCH}")
class _Calls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = _image()

    def call(self, target, args=(), specs=("stages",), game=None, before=None, sp=0x3E00, bp=0x3E80):
        """One call of `target` (args in push order) from RET[target], a Prover on the machine; returns (machine,
        prover). game: {offset: byte} set in the game record first."""
        from original_match import port
        from original_match.machine import Machine
        from original_match.match import SS_PARAGRAPH
        from original_match.port.prove import Prover
        m = Machine(self.image.memory, self.image.load)
        inst = port.install(m, list(specs))
        prover = Prover(m, inst)
        g = m.far(GAME)
        for off, value in (game or {}).items():
            m.write(g + off, bytes([value]))
        if before:
            before(m)
        ss = m.seg(SS_PARAGRAPH)
        ret = RET[target]
        far = next(e for r, _ in inst.loaded for a, e in r.entries.items() if a == target).far
        rseg, roff = ret.split(":")
        words = [int(roff, 16)] + ([m.seg(int(rseg, 16))] if far else []) + list(reversed(args))
        for i, w in enumerate(words):
            m.write(ss * 16 + sp + 2 * i, (w & 0xFFFF).to_bytes(2, "little"))
        tseg, toff = target.split(":")
        for name, value in (("ss", ss), ("sp", sp), ("bp", bp), ("ds", m.DS), ("es", m.DS),
                            ("cs", m.seg(int(tseg, 16))), ("eip", int(toff, 16))):
            m.set_reg(name, value)
        m.at(ret, lambda replay: replay or m.stop("returned"))
        self.assertEqual(m.run(m.lin(END), 300, fresh=True), "returned")
        self.assertEqual(m.reg("sp"), (sp + 2 * len(words)) & 0xFFFF)
        return m, prover

    def proved(self, prover, target):
        s = prover.summary()
        self.assertEqual((s[target]["proved"], s[target]["before"]), (1, 0), target)
        return s

    def game(self, m, off, n=1):
        return m.read(m.far(GAME) + off, n)


class DirectProofTests(_Calls):
    def test_stage_end_with_a_round_left_only_counts_down(self):
        m, p = self.call("1771:8208", game={0x3D: 2})
        self.proved(p, "1771:8208")
        self.assertEqual(list(self.game(m, 0x3C, 2)), [2, 1])           # the stage stays, one round left

    def test_stage_end_3_to_4_two_rounds_no_ageing(self):
        aged = []
        m, p = self.call("1771:8208", game={0x3C: 3},
                         before=lambda m: m.at("1771:80DA", lambda replay: replay or aged.append(1)))
        self.proved(p, "1771:8208")
        self.assertEqual(list(self.game(m, 0x3C, 2)), [4, 2])
        self.assertEqual(self.game(m, 0x40)[0], 0)
        self.assertEqual(aged, [])

    def test_stage_end_7_to_8_four_rounds(self):
        m, p = self.call("1771:8208", game={0x3C: 7})
        self.proved(p, "1771:8208")
        self.assertEqual(list(self.game(m, 0x3C, 2)), [8, 4])
        self.assertEqual(self.game(m, 0x40)[0], 1)

    def test_stage_end_8_wraps_to_2_and_ages(self):
        aged = []
        m, p = self.call("1771:8208", game={0x3C: 8},
                         before=lambda m: m.at("1771:80DA", lambda replay: replay or aged.append(1)))
        self.proved(p, "1771:8208")
        self.assertEqual(list(self.game(m, 0x3C, 2)), [2, 1])
        self.assertEqual(self.game(m, 0x40)[0], 0)
        self.assertEqual(len(aged), 1)                    # the port's run's visit (the original's is replayed)

    def test_run_stage_dispatches_every_stage_byte(self):
        nested = {}
        for stage in range(10):
            with self.subTest(stage=stage):
                ran = set()

                def hooks(m):
                    for b, _ in ST.BUILDERS.values():
                        m.at(b, lambda replay, b=b: replay or ran.add(b))
                m, p = self.call("1771:76B1", specs=("stages", (ST.display_helpers(), None)),
                                 game={0x3C: stage}, before=hooks)
                s = self.proved(p, "1771:76B1")
                self.assertEqual(ran, {ST.BUILDERS[stage][0]} if stage in ST.BUILDERS else set())
                for helper in ("1771:5D02", "1771:5D94", "1771:5E3A", "1771:5E99", "1771:6617",
                               *ST.HELPERS_FROM_DISPLAY):
                    self.assertEqual(s[helper]["proved"], 0)              # inside 76B1's proof: nested
                if stage in ST.BUILDERS:
                    self.assertGreater(s["1771:5D94"]["nested"], 0)
                nested[stage] = {a: v["nested"] for a, v in s.items() if v["nested"]}
        # 5C94 and 5CCB, which the published round's end does not reach, are nested in 6E59's, 71B2's and 74BE's
        for stage, helpers in ((4, ST.HELPERS_FROM_DISPLAY), (7, ("1771:5C94",)), (8, ST.HELPERS_FROM_DISPLAY)):
            for helper in helpers:
                self.assertGreater(nested[stage].get(helper, 0), 0, (stage, helper))

    def test_the_helpers_on_their_own(self):
        cases = [("1771:5D94", (7, 27, 2, 3)), ("1771:5D94", (12, 27, 1, 0)), ("1771:5E3A", (12, 27, 3, 2, 27)),
                 ("1771:5E3A", (12, 27, 1, 2, 12)), ("1771:5E99", (4,)), ("1771:6617", (0,)), ("1771:6617", (1,))]
        for target, args in cases:
            with self.subTest(target=target, args=args):
                m, p = self.call(target, args, game={0x2: 3} if target == "1771:6617" else None)
                self.proved(p, target)

    def test_add_fixture_writes_the_record(self):
        before = {}

        def keep(m):
            before["n"] = m.word_at(m.far(GAME) + 0x28)
        m, p = self.call("1771:5D94", (7, 27, 2, 3), before=keep)
        self.proved(p, "1771:5D94")
        n = before["n"]
        fx = m.read(m.far(0xA92B) + 8 * (n - 1), 8)
        self.assertEqual(fx[:3].hex(), "fe0302")          # 7 is the managed country: 0xFE, group 3, kind 2
        self.assertEqual((int.from_bytes(fx[4:6], "little"), int.from_bytes(fx[6:8], "little")), (27, 7))
        self.assertEqual(m.word_at(m.far(GAME) + 0x28), n + 1)
        lst = m.far(0xA92F) + 0x48 * 7
        self.assertEqual(m.word_at(lst + 0x46), n)        # the newest fixture last in 7's list

    def test_set_manager_groups_on_a_state_with_managers(self):
        m, p = self.call("1771:5E99", (4,))
        self.proved(p, "1771:5E99")
        self.assertEqual(self.game(m, 2)[0], 4)           # one manager: [A923]+1+1

    def test_the_display_helpers(self):
        def args(m):
            return (m.rd(0xA92D), m.rd(0xA92B) + 8 * 4)  # fixture 5: its far pointer, segment pushed first
        from original_match.machine import Machine
        a = args(Machine(self.image.memory, self.image.load))
        for target in ST.HELPERS_FROM_DISPLAY:
            with self.subTest(target=target):
                m, p = self.call(target, a, specs=[(ST.display_helpers(), None)])
                self.proved(p, target)


class FalsifierTests(_Calls):
    CASES = {
        "ageing-gate-skipped": ("1771:8208", (), {}),
        "playoff-flag-from-4": ("1771:8208", (), {0x3C: 3}),
        "stage-4-one-round": ("1771:8208", (), {0x3C: 3}),
        "three-builds-four": ("1771:76B1", (), {0x3C: 3}),
        "four-builds-three": ("1771:76B1", (), {0x3C: 4}),
        "list-not-shifted": ("1771:5D94", (7, 27, 2, 3), {}),
        "kind-not-raised": ("1771:5D94", (7, 27, 9, 3), {}),
        "managed-not-marked": ("1771:5D94", (7, 27, 2, 3), {}),
        "group-not-written": ("1771:5D94", (7, 27, 2, 3), {}),
        "bonus-on-every-kind": ("1771:5E3A", (12, 27, 1, 2, 27), {}),
        "sides-not-swapped": ("1771:5E3A", (12, 27, 3, 2, 27), {}),
        "group-plus-one": ("1771:5E99", (4,), {}),
        "mark-ff": ("1771:76B1", (), {0x3C: 3}),
        "rounds-of-next-param": ("1771:76B1", (), {0x3C: 3}),
        "ranking-bonus-dropped": ("1771:63A4", (), {}),
        "manager-score-reset-dropped": ("1771:63A4", (), {}),
        "qualifying-draw-order-reversed": ("1771:6730", (), {0x38:0,0x39:0,0x3C:2,0x40:0}),
        "qualifying-group-plus-one": ("1771:6730", (), {0x38:0,0x39:0,0x3C:2,0x40:0}),
    }

    def test_every_variant_is_listed(self):
        self.assertEqual(set(self.CASES), set(ST.PORTS.variants))

    def test_each_stages_variant_is_caught(self):
        from original_match.port.prove import ProofError
        for variant, (target, args, game) in self.CASES.items():
            with self.subTest(variant=variant):
                with self.assertRaises(ProofError):
                    self.call(target, args, specs=["stages." + variant], game=game)

    def test_the_display_helpers_omitted_are_caught(self):
        from original_match.machine import Machine
        from original_match.port.prove import ProofError
        m0 = Machine(self.image.memory, self.image.load)
        a = (m0.rd(0xA92D), m0.rd(0xA92B) + 8 * 4)
        for target in ST.HELPERS_FROM_DISPLAY:
            variant = "omit-" + target.lower().replace(":", "-")
            with self.subTest(variant=variant):
                with self.assertRaisesRegex(ProofError, "register AX at the return"):
                    self.call(target, a, specs=[(ST.display_helpers(), variant)])


if __name__ == "__main__":
    unittest.main()
