"""T38: the whole-match harness's substitution hook (runtime/emul/watched_match.py, Guest.hook).

- SyntheticHookTests run a three-call guest program on a bare machine: the routine at 2000:0000
  increments the word DS:0100 and returns with `retf 2`. Hooked, its own code is never reached
  (the word stays 0, its `retf` never executes), the fn's AX comes back, the stack balances as
  the routine's own `retf 2` would leave it, and the count is exactly 3. Unhooked, the same
  program runs the routine 3 times (the control).
- ListingReturnTests pin the return form read from the listing: 214B:0688 ends in `retf 6`.
- RealGuestTests (skipped without the E011 watchstart savestate) resume the captain screen and run
  40 clock ticks: unhooked, 214B:0688's body runs; hooked with F004's step, it never runs, the
  count is the literal number of calls, and the seed word's trajectory is the same; a hook that
  writes 0xDEAD to the seed and restores it before F004's step leaves those writes in the trace,
  which then differs from the original's (review R1); a first key read from an undeclared return
  address raises KeyWaitError instead of taking the captain screen's queued Enter (review R2).
"""
import contextlib
import io
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


def machine(ss=0x0800):
    mem = bytearray(0x30000)
    mem[CODE * 16:CODE * 16 + len(PROGRAM)] = PROGRAM
    mem[ROUTINE * 16:ROUTINE * 16 + len(BODY)] = BODY
    g = Guest(memory=mem, regs={"CS": CODE, "EIP": 0, "SS": ss, "ESP": SP0, "DS": 0, "ES": 0})
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


    def test_every_fn_write_to_a_watched_word_is_reported(self):
        # review R1: a write later undone, and the same-value restore, are reported at write time
        g, _ = machine()
        reports = []
        g.watch_word(0x200, lambda old, new: reports.append((old, new)))

        def fn(guest):
            guest.set_word(0, 0x200, 0xDEAD)
            guest.set_word(0, 0x200, 0)

        g.hook("2000:0000", fn, ret=(True, 2))
        g.emulate(END, 5)
        self.assertEqual(reports, [(0, 0xDEAD), (0xDEAD, 0)] * 3)


    def test_a_correct_model_is_proved_with_no_difference(self):
        # round 2: side by side, the original's `inc word [0x100]` against a model writing the same
        g, retf_runs = machine()
        g.hook("2000:0000", lambda guest: guest.put(0x100, (guest.word_at(0x100) + 1).to_bytes(2, "little")),
               ret=(True, 2), prove=True, ret_at=[4])
        g.emulate(END, 5)
        self.assertEqual(g.hook_counts, {"2000:0000": 3})
        self.assertEqual(g.proved_calls, {"2000:0000": 3})
        self.assertEqual(len(retf_runs), 3)          # the original ran to its retf at each call
        self.assertEqual(g.word_at(0x100), 3)        # once per call: the original's write undone
        self.assertEqual(g.reg("sp"), SP0)
        self.assertEqual(g.reg("ip"), 14)

    def test_a_model_leaving_another_cx_passes_with_a_warning_count(self):
        # the owner, 2026-10-11: BX, CX, SI, DI, ES and the flags are not compared; a difference
        # is a warning, counted per register
        g, _ = machine()

        def fn(guest):
            guest.put(0x100, (guest.word_at(0x100) + 1).to_bytes(2, "little"))
            guest.set_reg("cx", 0x55)

        g.hook("2000:0000", fn, ret=(True, 2), prove=True, ret_at=[4])
        with contextlib.redirect_stderr(io.StringIO()) as err:
            g.emulate(CODE * 16 + 12, 5)            # stop at the loop: one call, CX still the model's
        self.assertEqual(g.proved_calls, {"2000:0000": 1})
        self.assertEqual(g.scratch_differences["2000:0000"],
                         {"BX": 0, "CX": 1, "SI": 0, "DI": 0, "ES": 0, "FLAGS": 0})
        self.assertIn("WARNING: call #1 of 2000:0000: uncompared register CX at the return:"
                      " the original 0x0003, the model 0x0055", err.getvalue())

    def test_a_model_writing_another_byte_is_stopped_with_the_call_and_address(self):
        from watched_match import ProofError
        g, _ = machine()
        g.hook("2000:0000", lambda guest: guest.put(0x100, (guest.word_at(0x100) + 2).to_bytes(2, "little")),
               ret=(True, 2), prove=True, ret_at=[4])
        with self.assertRaises(ProofError) as cm:
            g.emulate(END, 5)
        self.assertEqual(str(cm.exception), "call #1 of 2000:0000: written byte #0 differs: the original wrote"
                         " 0x01 at linear 0x00100, the model wrote 0x02 at linear 0x00100")


    def test_a_write_through_a_mu_writer_bound_before_the_hook_is_recorded(self):
        # Sol's R1 on PR 136's round 2: `write = g.mu.mem_write` taken before the hook was registered
        from watched_match import ProofError
        g, _ = machine()
        write = g.mu.mem_write

        def fn(guest):
            saved = guest.mem(0x200, 2)
            write(0x200, b"\xad\xde")
            write(0x200, saved)
            guest.put(0x100, (guest.word_at(0x100) + 1).to_bytes(2, "little"))

        g.hook("2000:0000", fn, ret=(True, 2), prove=True, ret_at=[4])
        with self.assertRaises(ProofError) as cm:
            g.emulate(END, 5)
        self.assertEqual(str(cm.exception), "call #1 of 2000:0000: written byte #0 differs: the original wrote"
                         " 0x01 at linear 0x00100, the model wrote 0xAD at linear 0x00200")

    def test_an_output_aliased_into_the_stack_segment_below_sp_is_compared(self):
        # Sol's R2 on PR 136's round 2: with SS = DS = 0 the output word DS:0100 lies below SP;
        # only the routine's own dead frame is excluded, so a model adding 2 is stopped
        from watched_match import ProofError
        g, _ = machine(ss=0)
        g.hook("2000:0000", lambda guest: guest.put(0x100, (guest.word_at(0x100) + 2).to_bytes(2, "little")),
               ret=(True, 2), prove=True, ret_at=[4])
        with self.assertRaises(ProofError) as cm:
            g.emulate(END, 5)
        self.assertEqual(str(cm.exception), "call #1 of 2000:0000: written byte #0 differs: the original wrote"
                         " 0x01 at linear 0x00100, the model wrote 0x02 at linear 0x00100")

    def test_a_correct_model_still_passes_with_the_stack_aliased(self):
        g, _ = machine(ss=0)
        g.hook("2000:0000", lambda guest: guest.put(0x100, (guest.word_at(0x100) + 1).to_bytes(2, "little")),
               ret=(True, 2), prove=True, ret_at=[4])
        g.emulate(END, 5)
        self.assertEqual(g.proved_calls, {"2000:0000": 3})
        self.assertEqual(g.word_at(0x100), 3)


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

    def test_a_hidden_seed_write_is_in_the_trace_and_fails_the_comparison(self):
        # review R1: F004's step with 0xDEAD written to the seed and restored before it
        from check import f004_step, hidden_write, trace_difference
        from watched_match import WatchedMatch
        plain, _ = self.run_match(False)
        m = WatchedMatch(watchstart_or_skip(self))
        m.hook("214B:0688", hidden_write(f004_step()))
        m.run(max_ticks=self.TICKS)
        self.assertIn(0xDEAD, [d[3] for d in m.draws])
        self.assertEqual(len(m.draws), 3 * len(plain.draws))   # every main-seed step: 3 writes
        self.assertIsNotNone(trace_difference(plain.draws, m.draws))

    def prove(self, fn):
        from watched_match import WatchedMatch
        m = WatchedMatch(watchstart_or_skip(self))
        m.hook("214B:0688", fn, prove=True)
        m.run(max_ticks=self.TICKS)
        return m

    def test_f004_is_proved_at_every_call_with_no_difference(self):
        from check import f004_step
        plain, _ = self.run_match(False)
        m = self.prove(f004_step())
        self.assertEqual(m.hook_counts, {"214B:0688": 1558})
        self.assertEqual(m.proved_calls, {"214B:0688": 1558})
        self.assertEqual(m.draws, plain.draws)
        self.assertEqual(m.tick_marks, plain.tick_marks)

    def falsifier(self, fn, message):
        from watched_match import ProofError
        with self.assertRaises(ProofError) as cm:
            self.prove(fn)
        self.assertEqual(str(cm.exception), message)

    def test_a_raw_write_to_the_seed_restored_is_stopped(self):
        # round 2, R1: g.mu.mem_write(0xDEAD) then the saved bytes, then F004's step
        from check import f004_step, raw_write
        self.falsifier(raw_write(f004_step()), "call #1 of 214B:0688: written byte #0 differs: the original wrote"
                       " 0x90 at linear 0x355A2 (DS:7B62), the model wrote 0xAD at linear 0x355A2 (DS:7B62)")

    def test_a_write_to_the_sub_tick_restored_is_stopped(self):
        # round 2, R2: DS:831D set to 0xDEAD and restored, then F004's step
        from check import clock_write, f004_step
        self.falsifier(clock_write(f004_step()), "call #1 of 214B:0688: written byte #0 differs: the original wrote"
                       " 0x90 at linear 0x355A2 (DS:7B62), the model wrote 0xAD at linear 0x35D5D (DS:831D)")

    def test_a_wrong_step_off_the_main_seed_is_stopped(self):
        # round 2, R3: the right step on DS:7B62, increment + 1 on any other seed word (DS:8336)
        from check import INC, f004_step, off_seed_increment
        self.falsifier(off_seed_increment(f004_step(), f004_step(inc=INC + 1)),
                       "call #2 of 214B:0688: written byte #0 differs: the original wrote"
                       " 0x2F at linear 0x35D76 (DS:8336), the model wrote 0x30 at linear 0x35D76 (DS:8336)")

    def test_an_undeclared_first_key_read_raises(self):
        # review R2: the queued Enter is for CC7B's read (return 0791:CEED) only
        from watched_match import KeyWaitError, WatchedMatch
        m = WatchedMatch(watchstart_or_skip(self))
        sp = (m.reg("sp") - 4) & 0xFFFF
        m.put(m.reg("ss") * 16 + sp, (0x1234).to_bytes(2, "little") + m.seg(0x791).to_bytes(2, "little"))
        m.set_reg("sp", sp)
        m.set_reg("cs", m.seg(0x214B))
        m.set_reg("eip", 0x08DD)
        with self.assertRaises(KeyWaitError):
            m.emulate(m.lin("0791:1234"), 5)
        self.assertEqual(m.key_log, [])
        self.assertEqual(len(m.keys), 1)


if __name__ == "__main__":
    unittest.main()
