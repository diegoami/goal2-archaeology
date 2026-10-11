"""T38: the whole-match harness's substitution hook (runtime/emul/watched_match.py, Guest.hook).

- SyntheticHookTests run a three-call guest program on a bare machine: the routine at 2000:0000
  increments the word DS:0100 and returns with `retf 2`. Hooked, its own code is never reached
  (the word stays 0, its `retf` never executes), the fn's AX comes back, the stack balances as
  the routine's own `retf 2` would leave it, and the count is exactly 3. Unhooked, the same
  program runs the routine 3 times (the control).
- ListingReturnTests pin the return form read from the listing: 214B:0688 ends in `retf 6`.
- RealGuestTests (skipped without the E011 watchstart savestate) resume the captain screen and run
  40 clock ticks: unhooked, 214B:0688's body runs; hooked with F004's step, it never runs, the
  count is the literal number of calls, and the seed word's trajectory is the same.
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime/emul"))
sys.path.insert(0, str(ROOT / "experiments/E021-m0-whole-match"))

try:
    from unicorn import UC_HOOK_CODE  # noqa: E402
    from watched_match import Guest, routine_return  # noqa: E402  (watched_match.py imports unicorn at module level)
except ModuleNotFoundError:
    # CI does not install python3-unicorn; the module's tests skip with the reason named.
    raise unittest.SkipTest("unicorn not installed")

CODE, ROUTINE = 0x1000, 0x2000
PROGRAM = bytes([
    0xB9, 0x03, 0x00,              # 0: mov cx, 3
    0xB8, 0x05, 0x00,              # 3: mov ax, 5
    0x50,                          # 6: push ax
    0x9A, 0x00, 0x00, 0x00, 0x20,  # 7: call far 2000:0000
    0xE2, 0xF5,                    # 12: loop 3
    0xF4,                          # 14: hlt
])
BODY = bytes([0xFF, 0x06, 0x00, 0x01,   # 0: inc word ptr [0x0100]
              0xCA, 0x02, 0x00])        # 4: retf 2
END = CODE * 16 + 14
SP0 = 0xFF00


def machine():
    mem = bytearray(0x30000)
    mem[CODE * 16:CODE * 16 + len(PROGRAM)] = PROGRAM
    mem[ROUTINE * 16:ROUTINE * 16 + len(BODY)] = BODY
    g = Guest(memory=mem, regs={"CS": CODE, "EIP": 0, "SS": 0x0800, "ESP": SP0, "DS": 0, "ES": 0})
    retf_runs = []
    g.mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, d: retf_runs.append(a),
                  begin=ROUTINE * 16 + 4, end=ROUTINE * 16 + 4)
    return g, retf_runs


class SyntheticHookTests(unittest.TestCase):
    def test_unhooked_routine_runs_as_guest_code(self):
        g, retf_runs = machine()
        g.emulate(END, 5)
        self.assertEqual(g.word_at(0x100), 3)       # the body ran three times
        self.assertEqual(len(retf_runs), 3)
        self.assertEqual(g.reg("ax"), 5)
        self.assertEqual(g.reg("sp"), SP0)

    def test_hooked_routine_is_not_executed_and_the_count_is_exact(self):
        g, retf_runs = machine()
        seen = []

        def fn(guest):
            seen.append(guest.arg(0))               # the pushed argument, past the far return
            guest.set_reg("ax", guest.arg(0) * 2 + 1)

        key = g.hook("2000:0000", fn, ret=(True, 2))
        g.emulate(END, 5)
        self.assertEqual(key, "2000:0000")
        self.assertEqual(g.hook_counts, {"2000:0000": 3})
        self.assertEqual(seen, [5, 5, 5])
        self.assertEqual(g.word_at(0x100), 0)       # the routine's `inc` never ran
        self.assertEqual(retf_runs, [])             # nor its `retf 2`
        self.assertEqual(g.reg("ax"), 11)
        self.assertEqual(g.reg("sp"), SP0)          # returned as `retf 2` would
        self.assertEqual(g.reg("cs"), CODE)
        self.assertEqual(g.reg("ip"), 14)

    def test_an_error_in_fn_stops_the_run_and_is_raised(self):
        g, _ = machine()

        def fn(guest):
            raise ValueError("model failed")

        g.hook("2000:0000", fn, ret=(True, 2))
        with self.assertRaises(ValueError):
            g.emulate(END, 5)
        self.assertEqual(g.hook_counts, {"2000:0000": 1})


class ListingReturnTests(unittest.TestCase):
    def test_lcg_step_returns_far_popping_six(self):
        self.assertEqual(routine_return("214B:0688"), (True, 6))   # seg_214B_01.asm:894 `retf 6`

    def test_near_routine(self):
        self.assertEqual(routine_return("000E:05F6"), (False, 6))


def watchstart_or_skip(test):
    try:
        from check import asset
        rec = json.loads((ROOT / "runs/E011/E011-r0001.json").read_text())
        entry = next(o for o in rec["outputs"] if o["name"].endswith("-watchstart.sav"))
        return asset(entry)
    except BaseException as e:  # no cached copy and no network: nothing to emulate
        test.skipTest(f"watchstart savestate unavailable: {e}")


class RealGuestTests(unittest.TestCase):
    TICKS = 40

    def run_match(self, hooked):
        from check import f004_step
        from watched_match import WatchedMatch
        m = WatchedMatch(watchstart_or_skip(self))
        body = []
        lin = m.lin("214B:0689")                    # the step's second instruction
        m.mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, d: body.append(a), begin=lin, end=lin)
        if hooked:
            m.hook("214B:0688", f004_step())
        m.run(max_ticks=self.TICKS)
        return m, body

    def test_hooked_step_never_runs_and_keeps_the_trajectory(self):
        plain, plain_body = self.run_match(False)
        hooked, hooked_body = self.run_match(True)
        self.assertEqual(len(plain.tick_marks), self.TICKS)
        self.assertEqual(len(plain_body), 1558)    # 0688 calls (main seed and DS:8336), 40 ticks
        self.assertEqual(hooked_body, [])           # hooked: the guest's step never ran
        self.assertEqual(hooked.hook_counts, {"214B:0688": 1558})
        self.assertEqual(hooked.draws, plain.draws)
        self.assertEqual(hooked.tick_marks, plain.tick_marks)


if __name__ == "__main__":
    unittest.main()
