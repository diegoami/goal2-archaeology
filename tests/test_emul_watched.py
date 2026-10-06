"""T25: the watched-engine Unicorn harness (runtime/emul/watched.py).

- ResumeTests visit R6's edge: 9AFC stores ONE byte into DS:830B, so the harness's resume
  write must leave DS:830C untouched and take the side base from DS:0668.
- TickValuesTests and MutationTests pin R1's criterion: a checkpoint matches only on its
  exact (minute, sub-tick) curve, so a trajectory shifted by one sub-tick fails. The
  mutation is the reviewer's: the restored DS:831D one lower before emulation (it shifts
  the whole curve by one tick; the pre-fix minute-union criterion accepted it with 19/19).

The emulation tests need an E011 half-time savestate (a release asset, sha256-checked);
they are skipped when it is neither cached nor downloadable.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/E011-q010-watched-engine"

import sys  # noqa: E402
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(ROOT / "runtime/emul"))

try:
    from watched import WatchedHalf  # noqa: E402  (watched.py imports unicorn at module level)
except ModuleNotFoundError:
    # CI does not install python3-unicorn; the module's tests skip with the reason named.
    raise unittest.SkipTest("unicorn not installed")


def halftime_savestate_or_skip(test):
    try:
        from emu_check import halftime_sav
        rec = json.loads((ROOT / "runs/E011/E011-r0001.json").read_text())
        entry = next(o for o in rec["outputs"] if o["name"].endswith("-halftime.sav"))
        return halftime_sav(entry)
    except Exception as e:  # no cached copy and no network: nothing to emulate
        test.skipTest(f"half-time savestate unavailable: {e}")


class ResumeTests(unittest.TestCase):
    """R6: the 9AFC holder write is one byte wide and reads its base from DS:0668."""

    def test_holder_write_preserves_830c(self):
        # seg_0791_16.asm:9AFC is `mov byte ptr [0x830b], al`: a ONE-byte store. The
        # published states carry 0 at DS:830C, which masked the two-byte write; the
        # sentinel here makes the clobber visible (rule 10: the edge, with this test).
        data = halftime_savestate_or_skip(self)
        half = WatchedHalf(data)
        half.wr8(0x830C, 0x7B)                     # the sentinel
        half.apply_resume_tail()
        self.assertEqual(half.rd(0x830C, 1), 0x7B)  # 830C preserved
        side = 1 if half.rd(0x831A, 1) == 0 else 0  # seg_0791_16.asm:9AE3-9AEE
        base = half.rd(0x668 + side, 1)             # the side base, read from DS:0668
        self.assertEqual(half.rd(0x830B, 1), base + 10)
        self.assertEqual(half.rd(0x832A), 0x50)

    def test_word_write_would_clobber_830c(self):
        # The falsifier the byte-width fix removes: the old word-wide wr() cleared 830C.
        data = halftime_savestate_or_skip(self)
        half = WatchedHalf(data)
        half.wr8(0x830C, 0x7B)
        half.wr(0x830B, 21)                         # the pre-fix two-byte write
        self.assertEqual(half.rd(0x830C, 1), 0)


def fake_half(draws, tick_marks, start_seed):
    h = WatchedHalf.__new__(WatchedHalf)
    h.draws, h.tick_marks, h.start_state = draws, tick_marks, {"7B62": start_seed}
    return h


class TickValuesTests(unittest.TestCase):
    """R1: the criterion is per-tick, not per-minute."""

    DRAWS = [  # two ticks in one minute: (minute, sub-tick, before, after)
        (50, 4, 0x1111, 0x2222), (50, 4, 0x2222, 0x3333),
        (50, 3, 0x3333, 0x4444), (50, 3, 0x4444, 0x5555),
    ]
    MARKS = [(50, 4, 0x3333), (50, 3, 0x5555)]

    def test_read_on_its_own_tick_matches(self):
        sets = fake_half(self.DRAWS, self.MARKS, 0x1111).tick_values()
        self.assertIn(0x2222, sets[(50, 4)])
        self.assertIn(0x1111, sets[(50, 4)])   # the entering value
        self.assertIn(0x5555, sets[(50, 3)])

    def test_shifted_by_one_sub_tick_misses(self):
        # The same seed values, assigned to the neighbouring tick, must NOT match: the
        # pre-fix criterion unioned the minute and accepted exactly this shift.
        sets = fake_half(self.DRAWS, self.MARKS, 0x1111).tick_values()
        self.assertNotIn(0x4444, sets[(50, 4)])
        self.assertNotIn(0x2222, sets[(50, 3)])

    def test_tick_without_draws_holds_its_value(self):
        sets = fake_half([], [(60, 9, 0xAAAA)], 0xAAAA).tick_values()
        self.assertEqual(sets[(60, 9)], {0xAAAA})


class MutationTests(unittest.TestCase):
    """R1's regression: the reviewer's one-sub-tick shift must fail the check."""

    def test_initial_subtick_one_lower_is_rejected(self):
        from emu_check import checkpoints, matches
        data = halftime_savestate_or_skip(self)

        class ShiftedHalf(WatchedHalf):
            def run(self, timeout_s=1800):
                self.wr(0x831D, self.rd(0x831D) - 1)  # the mutation under test
                return WatchedHalf.run(self, timeout_s)

        half = ShiftedHalf(data).run()
        rec = json.loads((ROOT / "runs/E011/E011-r0001.json").read_text())
        cps = checkpoints(rec)
        hit = matches(half.tick_values(), cps)
        self.assertLess(hit, len(cps),
                        f"a one-sub-tick shift matched {hit}/{len(cps)}: the criterion is not tick-exact")


if __name__ == "__main__":
    unittest.main()
