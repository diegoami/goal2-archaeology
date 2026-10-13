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


# BODY with a frame: every kind of stack write the proof must take as the routine's own
FRAMED = bytes([0x55,                    # 0: push bp
                0x89, 0xE5,              # 1: mov bp, sp
                0x83, 0xEC, 0x02,        # 3: sub sp, 2
                0x89, 0x46, 0xFE,        # 6: mov [bp-2], ax   (a local, at SP)
                0x9C, 0x9D,              # 9: pushf; popf
                0xE8, 0x0A, 0x00,        # 11: call near 24
                0xFF, 0x06, 0x00, 0x01,  # 14: inc word ptr [0x0100]
                0x89, 0xEC,              # 18: mov sp, bp
                0x5D,                    # 20: pop bp
                0xCA, 0x02, 0x00,        # 21: retf 2
                0xC3])                   # 24: ret
FRAMED_RETF = 21


def machine(ss=0x0800, sp=SP0, body=BODY, retf=4):
    mem = bytearray(0x30000)
    mem[CODE * 16:CODE * 16 + len(PROGRAM)] = PROGRAM
    mem[ROUTINE * 16:ROUTINE * 16 + len(body)] = body
    g = Guest(memory=mem, regs={"CS": CODE, "EIP": 0, "SS": ss, "ESP": sp, "DS": 0, "ES": 0})
    retf_runs = []
    g.mu.hook_add(UC_HOOK_CODE, lambda uc, a, s, d: retf_runs.append(a),
                  begin=ROUTINE * 16 + retf, end=ROUTINE * 16 + retf)
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

    def test_an_output_aliased_just_below_the_entry_sp_is_compared(self):
        # Sol's R1 on PR 136's delta: SS = DS = 0 and SP 0x0110, so the output DS:0100 lies 10
        # bytes below the routine's entry SP (0x010A); the routine pushes nothing, so its frame is
        # empty and a model adding 2 is stopped
        from watched_match import ProofError
        g, _ = machine(ss=0, sp=0x0110)
        g.hook("2000:0000", lambda guest: guest.put(0x100, (guest.word_at(0x100) + 2).to_bytes(2, "little")),
               ret=(True, 2), prove=True, ret_at=[4])
        with self.assertRaises(ProofError) as cm:
            g.emulate(END, 5)
        self.assertEqual(str(cm.exception), "call #1 of 2000:0000: written byte #0 differs: the original wrote"
                         " 0x01 at linear 0x00100, the model wrote 0x02 at linear 0x00100")

    def test_a_correct_model_passes_with_the_output_just_below_the_entry_sp(self):
        g, _ = machine(ss=0, sp=0x0110)
        g.hook("2000:0000", lambda guest: guest.put(0x100, (guest.word_at(0x100) + 1).to_bytes(2, "little")),
               ret=(True, 2), prove=True, ret_at=[4])
        g.emulate(END, 5)
        self.assertEqual(g.proved_calls, {"2000:0000": 3})
        self.assertEqual(g.word_at(0x100), 3)

    def test_the_originals_pushes_local_and_nested_call_are_its_frame(self):
        # push bp, a local written at SP, pushf and a near call: none of them is the model's to
        # write; the output below them (SS = DS = 0) is still compared
        for sp, outcome in ((0x0130, "ok"), (0x0130, "+2")):
            g, retf_runs = machine(ss=0, sp=sp, body=FRAMED, retf=FRAMED_RETF)
            step = 1 if outcome == "ok" else 2
            g.hook("2000:0000", lambda guest, k=step: guest.put(0x100, (guest.word_at(0x100) + k).to_bytes(2, "little")),
                   ret=(True, 2), prove=True, ret_at=[FRAMED_RETF])
            if outcome == "ok":
                g.emulate(END, 5)
                self.assertEqual(g.proved_calls, {"2000:0000": 3})
                self.assertEqual(len(retf_runs), 3)              # the original ran each time
                self.assertEqual(g.word_at(0x100), 3)
            else:
                from watched_match import ProofError
                with self.assertRaisesRegex(ProofError, "written byte #0 differs: the original wrote 0x01 at linear 0x00100"):
                    g.emulate(END, 5)


class NestedProofTests(unittest.TestCase):
    """T46: a proved call's original runs as the original's own code, calls inside it included: a hook of
    ANOTHER routine does not fire there (else the proof would compare the model with the model of what
    it calls), and the same routine called from outside the original is still substituted."""
    INNER = 0x3000

    def guest(self):
        program = bytes([0xB8, 0x05, 0x00,                       # 0: mov ax, 5
                         0x50,                                    # 3: push ax
                         0x9A, 0x00, 0x00, 0x00, 0x20,            # 4: call far 2000:0000 (outer)
                         0x9A, 0x00, 0x00, 0x00, 0x30,            # 9: call far 3000:0000 (inner, directly)
                         0xF4])                                   # 14: hlt
        outer = bytes([0x9A, 0x00, 0x00, 0x00, 0x30,              # 0: call far 3000:0000 (inner)
                       0xCA, 0x02, 0x00])                         # 5: retf 2
        inner = bytes([0xFF, 0x06, 0x00, 0x02,                    # 0: inc word ptr [0x0200]
                       0xCB])                                     # 4: retf
        mem = bytearray(0x40000)
        for at, code in ((CODE, program), (ROUTINE, outer), (self.INNER, inner)):
            mem[at * 16:at * 16 + len(code)] = code
        return Guest(memory=mem, regs={"CS": CODE, "EIP": 0, "SS": 0x0800, "ESP": SP0, "DS": 0, "ES": 0})

    @staticmethod
    def inc(linear, by=1):
        return lambda g: g.put(linear, (g.word_at(linear) + by).to_bytes(2, "little"))

    def test_a_hook_inside_a_proved_original_does_not_fire_but_a_direct_call_does(self):
        g = self.guest()
        g.hook("2000:0000", self.inc(0x200), ret=(True, 2), prove=True, ret_at=[5])
        g.hook("3000:0000", self.inc(0x200), ret=(True, 0), prove=True, ret_at=[4])
        g.emulate(CODE * 16 + 14, 5)
        self.assertEqual(g.hook_counts, {"2000:0000": 1, "3000:0000": 1})   # the original's inner call is not counted
        self.assertEqual(g.proved_calls, {"2000:0000": 1, "3000:0000": 1})
        self.assertEqual(g.word_at(0x200), 2)              # the outer's effect once, the direct call's once

    def test_a_model_that_misses_the_inner_effect_is_stopped(self):
        from watched_match import ProofError
        g = self.guest()
        g.hook("2000:0000", self.inc(0x200, 2), ret=(True, 2), prove=True, ret_at=[5])
        g.hook("3000:0000", self.inc(0x200), ret=(True, 0), prove=True, ret_at=[4])
        with self.assertRaises(ProofError):
            g.emulate(CODE * 16 + 14, 5)


class PushOpcodeTests(unittest.TestCase):
    def test_the_instructions_that_write_below_sp(self):
        from watched_match import pushes
        for code in ("06", "0E", "16", "1E", "50", "55", "57", "60", "6834 12", "6A01", "9A00000020",
                     "9C", "C8040000", "CC", "CD21", "CE", "E80000", "0FA0", "0FA8",
                     "FF16 0001", "FF1E 0001", "FF36 0001", "2EFF36 0001", "36 55"):
            self.assertTrue(pushes(bytes.fromhex(code.replace(" ", "")) + bytes(6)), code)
        for code in ("58", "5D", "9D", "07", "1F", "8946FE", "FF060001", "FF0E0001", "FF260001",
                     "FF2E0001", "8F060001", "0FA1", "AB", "C7060001 3412", "2E8946FE"):
            self.assertFalse(pushes(bytes.fromhex(code.replace(" ", "")) + bytes(6)), code)


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

    def prove_reader(self, fn, ticks=400):
        from check import SKILL_READER, skill_reader
        from watched_match import WatchedMatch
        m = WatchedMatch(watchstart_or_skip(self))
        m.hook(SKILL_READER, fn, prove=True)
        m.run(max_ticks=ticks)
        return m

    def test_the_skill_reader_278a_is_proved_by_the_model(self):
        # T42: keeping.contest_trace decides 0791:278A's AX and DX; every call proved
        from check import SKILL_READER, skill_reader
        m = self.prove_reader(skill_reader())
        self.assertGreater(m.proved_calls[SKILL_READER], 0)
        self.assertEqual(m.proved_calls[SKILL_READER], m.hook_counts[SKILL_READER])

    def test_the_skill_reader_falsifiers_are_stopped(self):
        from check import skill_reader
        from watched_match import ProofError
        with self.assertRaises(ProofError):
            self.prove_reader(skill_reader(product_plus=1), ticks=3000)

    def test_the_gate_falsifier_is_not_reached_by_e011(self):
        # T42 DW2 as amended (2026-10-12): no 278A call in E011 reaches the 282D-2837 keeper set
        # test with an event in {3, 4, 0x18}, so the pre-T40 gate proves; #164 tracks a match
        # that reaches it, and then this test must expect a ProofError
        from check import SKILL_READER, skill_reader
        m = self.prove_reader(skill_reader(gate=frozenset({0x18})), ticks=3000)
        self.assertGreater(m.proved_calls[SKILL_READER], 0)

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


class FakeGuest:
    """The few Guest methods a hook fn reads, over a flat memory: DS = 0x1000, the player array at
    0x3000:0x0100 (DS:A91B holds the far pointer), the foot tables DS:0E60 and DS:0E7C as given."""
    DS = 0x1000

    def __init__(self, w, record, foot=None, footix=(0, 0, 0)):
        self.memory = bytearray(0x100000)
        self.w = w
        self.regs = {}
        self.set(0xA91B, 0x0100)
        self.set(0xA91D, 0x3000)
        base = (0x0100 + ((w * 20) & 0xFFFF)) & 0xFFFF
        self.memory[0x30000 + base:0x30000 + base + 20] = record
        for i, v in (foot or {}).items():
            self.memory[self.DS * 16 + 0xE60 + i] = v
        self.memory[self.DS * 16 + 0xE7C:self.DS * 16 + 0xE7F] = bytes(footix)

    def set(self, off, value):
        self.memory[self.DS * 16 + off:self.DS * 16 + off + 2] = value.to_bytes(2, "little")

    def arg(self, i):
        return self.w if i == 0 else 0xBEEF       # 377E takes one argument word

    def rd(self, off, n=2):
        return int.from_bytes(self.memory[self.DS * 16 + off:self.DS * 16 + off + n], "little")

    def mem(self, linear, n):
        return bytes(self.memory[linear:linear + n])

    def set_reg(self, name, value):
        self.regs[name] = value


def record(p2=0, p4=100, p5=7, p6=1, p7=1, form=5, energy=0x20, flags=0):
    r = bytearray(20)
    r[2], r[4], r[5], r[6], r[7], r[0xC], r[0xE], r[0x10] = p2, p4, p5, p6, p7, form, energy, flags
    return bytes(r)


class StrengthReaderTests(unittest.TestCase):
    """T43: check.strength_reader (1771:377E) on literal guest memory; AX and DX are what the proof
    compares, DX derived from the listing (the docstring). Every guest read is covered by a case
    that a one-off or wrong-table read breaks (the mutations are listed in the PR)."""

    def call(self, w=5, rec=None, foot=None, footix=(0, 0, 0), **kw):
        from check import EXPECTED_377E, strength_reader
        g = FakeGuest(w, rec if rec is not None else record(), foot, footix)
        tally = dict.fromkeys(EXPECTED_377E, 0)
        strength_reader(tally, **kw)(g)
        return g.regs["ax"], g.regs["dx"], tally

    def test_available_right_foot_ax_and_dx(self):
        # 100 + 0x20 - 0x3E = 70; form 5 < 0x20: + 5 = 75; DX = +5 (3041's mov dx, ax)
        ax, dx, tally = self.call()
        self.assertEqual((ax, dx), (75, 7))
        self.assertEqual(tally["form<0x20"], 1)

    def test_the_word_decides_the_record(self):
        # two words, two records: AX follows the argument word (3784-378C)
        self.assertEqual(self.call(w=9, rec=record(p4=110))[0], 85)

    def test_wrong_foot_dx_is_the_remainder_of_the_value_before_halving(self):
        # position 0 with +7 != 0 is wrong (31DF-31EE); 380C-3813 divides the value by 2 and leaves the
        # remainder of that value in DX: 75 -> 37 r 1, 74 -> 37 r 0, 77 -> 38 r 1, 76 -> 38 r 0
        for form, ax, dx in ((5, 37, 1), (4, 37, 0), (7, 38, 1), (6, 38, 0)):
            got = self.call(rec=record(p6=0, p7=1, form=form))
            self.assertEqual(got[:2], (ax, dx), form)
            self.assertEqual(got[2]["wrong foot"], 1)

    def test_the_foot_table_decides_the_wrong_foot(self):
        # DS:0E60[14 * DS:0E7C[w % 3] + (+7)]: w = 4 -> E7C[1] = 1 -> row 1, +7 = 2 -> byte 16 (3088; DS:0E7C = 0E60 + 28 starts the index table, so rows are 0 and 1);
        # position 3, foot != 0, not two-footed -> wrong (3139 set, 31AE-31C0). Every other byte is 0.
        rec = record(p6=3, p7=2)
        got = self.call(w=4, rec=rec, foot={16: 1}, footix=(0, 1, 0))
        self.assertEqual((got[:2], got[2]["wrong foot"]), ((37, 1), 1))
        self.assertEqual(self.call(w=4, rec=rec)[2]["wrong foot"], 0)
        # the neighbouring bytes and rows do not count
        for other in (15, 17, 14, 2, 18, 27):
            self.assertEqual(self.call(w=4, rec=rec, foot={other: 1}, footix=(0, 1, 0))[0], 75, other)

    def test_the_foot_index_table_is_indexed_by_the_word_mod_3(self):
        rec = record(p6=3, p7=2)
        foot, footix = {16: 1}, (0, 1, 0)
        self.assertEqual(self.call(w=4, rec=rec, foot=foot, footix=footix)[0], 37)   # 4 % 3 = 1 -> row 1
        self.assertEqual(self.call(w=5, rec=rec, foot=foot, footix=footix)[0], 75)   # 5 % 3 = 2 -> row 0
        self.assertEqual(self.call(w=3, rec=rec, foot=foot, footix=footix)[0], 75)   # 3 % 3 = 0 -> row 0

    def test_foot_zero_in_the_second_position_set(self):
        # foot byte 0 and position 4 (3159 set): wrong (31C8-31DA); with foot != 0 it is not
        rec = record(p6=4, p7=2)
        self.assertEqual(self.call(w=4, rec=rec, foot={}, footix=(0, 1, 0))[0], 37)
        self.assertEqual(self.call(w=4, rec=rec, foot={16: 1}, footix=(0, 1, 0))[0], 75)

    def test_the_form_threshold_edge_0x20(self):
        # form 0x20: 70 - 70 // 16 = 66 (37CD-37D8); form 0x1F: 70 + 31 = 101
        self.assertEqual(self.call(rec=record(form=0x20))[0], 66)
        self.assertEqual(self.call(rec=record(form=0x1F))[0], 101)
        self.assertEqual(self.call(rec=record(form=0x20))[2]["form==0x20"], 1)

    def test_the_clamp_edges(self):
        # 255 + 127 - 62 = 320, + 5 > 0x100 -> 0x100 (37FA-37FC); 10 + 1 - 62 + 5 < 0 -> 0 (37EC-37F0)
        ax, _, tally = self.call(rec=record(p4=255, energy=0x7F))
        self.assertEqual((ax, tally["clamped"]), (0x100, 1))
        ax, _, tally = self.call(rec=record(p4=10, energy=1))
        self.assertEqual((ax, tally["clamped"]), (0, 1))
        self.assertEqual(self.call()[2]["clamped"], 0)

    def test_the_tally_follows_the_models_own_run(self):
        # R3 of review 1: a model that does not clamp (returns 325) is not reported as clamping, and one
        # that reports a clamp is counted, whatever the record's bytes say
        from check import _Record
        for flag in (False, True):
            class Injected(_Record):
                def strength_trace(self, w, flag=flag):
                    return {"unavailable": None, "form_high": False, "clamped": flag, "wrong_foot": False,
                            "halved_from": None, "value": 325}
            ax, _, tally = self.call(rec=record(p4=255, energy=0x7F), record_class=Injected)
            self.assertEqual((ax, tally["clamped"]), (325, int(flag)))

    def test_unavailable_by_energy_leaves_the_high_word_of_the_record_offset(self):
        # 3233: +0xE < 1 -> 0; DX = 3222's `mul dx` high word, w * 20 >> 16 (4000 * 20 = 80000 -> 1)
        ax, dx, tally = self.call(w=4000, rec=record(energy=0))
        self.assertEqual((ax, dx, tally["unavailable"]), (0, 1, 1))

    def test_unavailable_by_flag_leaves_the_element_minus_one(self):
        # 3248 (element 8, bit 7), 325F (6, bit 5), 3276 (3, bit 2): the first set one wins
        for flags, dx in ((0x80, 7), (0x20, 5), (0x04, 2), (0xA4, 7), (0x24, 5)):
            ax, got, _ = self.call(rec=record(flags=flags))
            self.assertEqual((ax, got), (0, dx), hex(flags))

    def test_the_falsifiers_change_the_result(self):
        from check import ThresholdMutant
        self.assertEqual(self.call(rec=record(form=0x20), result_plus=1)[0], 67)
        # threshold 0x21: form 0x20 takes the `+ form` branch, 70 + 32
        self.assertEqual(self.call(rec=record(form=0x20), record_class=ThresholdMutant)[0], 102)
        self.assertEqual(self.call(rec=record(form=0x21), record_class=ThresholdMutant)[0], 70 - 70 // 16)


class GateGuest:
    """The Guest methods check.gate_reader reads, over a flat memory: DS = 0x1000; the far pointer at
    DS:A978 (offset) / DS:A97A (segment) points to the seed word, which lies away from DS:7B62."""
    DS = 0x1000
    SEED_SEG, SEED_OFF = 0x2000, 0x0040

    def __init__(self, seed, off=0x0123, seg=0x3000, element=7, decoy=0xBEEF):
        self.memory = bytearray(0x100000)
        self.args = (off, seg, element)
        self.regs = {}
        self.writes = []
        self.set(0xA978, self.SEED_OFF)
        self.set(0xA97A, self.SEED_SEG)
        self.put(self.SEED_SEG * 16 + self.SEED_OFF, seed.to_bytes(2, "little"))
        self.set(0x7B62, decoy)                       # the main seed: not the one 287C steps
        self.writes.clear()

    def set(self, off, value):
        self.memory[self.DS * 16 + off:self.DS * 16 + off + 2] = value.to_bytes(2, "little")

    def arg(self, i):
        return self.args[i]

    def rd(self, off, n=2):
        return int.from_bytes(self.memory[self.DS * 16 + off:self.DS * 16 + off + n], "little")

    def far(self, off):
        return self.rd(off + 2) * 16 + self.rd(off)

    def word_at(self, linear):
        return int.from_bytes(self.memory[linear:linear + 2], "little")

    def put(self, linear, raw):
        self.writes.append((linear, bytes(raw)))
        self.memory[linear:linear + len(raw)] = raw

    def set_reg(self, name, value):
        self.regs[name] = value


class GateReaderTests(unittest.TestCase):
    """T46: check.gate_reader (0791:287C) on literal guest memory, 278A's value given (check.skill_trace
    is replaced: T42's proofs cover its reads). AL, AH, DX and the seed write are what the proof
    compares; each read is covered by a case a one-off mutation breaks (the PR lists them)."""

    def call(self, value=100, seed=0x1234, tally=None, **kw):
        from unittest import mock
        import check
        g = GateGuest(seed)
        seen = []

        def stub(guest, off, seg, element, gate=None):
            seen.append((off, seg, element))
            return value, 0

        with mock.patch.object(check, "skill_trace", stub):
            check.gate_reader(tally, **kw)(g)
        return g, seen

    def test_result_registers_and_the_seed_write(self):
        g, seen = self.call()
        # n = 4, seed 0x1234 -> new 21363, draw 2: AL = 1, AH = 0, DX = 2 (contests.py)
        self.assertEqual(g.regs, {"ax": 1, "dx": 2})
        self.assertEqual(g.writes, [(GateGuest.SEED_SEG * 16 + GateGuest.SEED_OFF, (21363).to_bytes(2, "little"))])
        self.assertEqual(g.rd(0x7B62), 0xBEEF)               # the decoy seed word is untouched

    def test_the_arguments_reach_278a_in_the_stack_order(self):
        self.assertEqual(self.call()[1], [(0x0123, 0x3000, 7)])

    def test_the_seed_is_read_through_the_far_pointer(self):
        # the draw follows the word DS:A978 points to (seed 0 -> draw 1 at n = 4 -> AL = 0)
        g, _ = self.call(seed=0)
        self.assertEqual(g.regs, {"ax": 0, "dx": 1})

    def test_n_follows_278as_value(self):
        # seed 0x1234: the draw is 1 up to n = 3 (values 31, 95), 2 for n = 4 (96, 100), 668 for n = 2048
        for value, draw in ((31, 1), (95, 1), (96, 2), (100, 2), (0xFFFF, 668)):
            self.assertEqual(self.call(value=value)[0].regs["dx"], draw, value)

    def test_ah_is_the_draws_high_byte(self):
        g, _ = self.call(value=0xFFFF, seed=1)               # draw 1199 = 0x4AF
        self.assertEqual(g.regs, {"ax": 0x0401, "dx": 1199})

    def test_the_tally_follows_the_models_own_run(self):
        tally = {}
        self.call(tally=tally)
        self.call(seed=0, tally=tally)
        self.assertEqual(tally, {"calls": 2, "non-zero": 1, "zero": 1})
        tally = {}
        self.call(tally=tally, invert=True)                  # the tally counts the model's draw, not the output
        self.assertEqual(tally, {"calls": 1, "non-zero": 1})

    def test_the_falsifiers_change_the_result(self):
        self.assertEqual(self.call(invert=True)[0].regs["ax"], 0)
        self.assertEqual(self.call(seed=0, invert=True)[0].regs["ax"], 1)
        # n + 1: value + 32 -> n = 5; the seed's draw changes with n (the same seed, 4 -> 2, 5 -> 2 or 3)
        base, plus = self.call(seed=0x0007)[0], self.call(seed=0x0007, value_plus=32)[0]
        self.assertNotEqual(base.regs["dx"], plus.regs["dx"])


class WrapperReaderTests(unittest.TestCase):
    """T47: check.wrapper_reader (214B:06B1 and 214B:06D0) on literal guest memory (GateGuest: the far pointer at
    DS:A978 leads to the seed; n is arg(0), [bp + 6]). AX, DX and the seed write (address AND bytes) are what the
    proof compares; every assertion is an exact value, per wrapper (06B1 = which 1, 06D0 = which 0). The mutation
    each test must kill is named in its docstring (tests/mutations_t47.py runs them in memory)."""
    SEED_LIN = GateGuest.SEED_SEG * 16 + GateGuest.SEED_OFF
    # name: (seed, n, draw, new seed) -- the draw of 1..n and the stepped word (recreate.draw)
    CASES = {"A": (0x1234, 4, 2, 21363), "B": (1, 2048, 1199, 38348), "C": (0, 4, 1, 6927),
             "D": (1, 3, 2, 38348), "E": (0, 3, 1, 6927), "F": (15, 3, 1, 19490)}

    def call(self, which, n=4, seed=0x1234, tally=None, **kw):
        import check
        g = GateGuest(seed)
        g.args = (n,)
        check.wrapper_reader(which, tally, **kw)(g)
        return g

    @staticmethod
    def regs(which, draw):
        """06B1: AX = DX = draw (06C4-06C7). 06D0: AL = 1 when the draw is 1 else 0 (06E3-06EC), AH the draw's
        high byte, DX the draw."""
        return {"ax": draw if which else (draw & 0xFF00) | (draw == 1), "dx": draw}

    def test_every_register_and_the_seed_write_of_each_wrapper(self):
        """Kills, per wrapper: AX = low byte only, AX = 0, AX + 1, DX = 0, DX = draw + 1, AH dropped (06D0),
        AL = the draw (06D0), AL inverted, the seed write dropped, written to another address, written
        unchanged (the input seed) or with the wrong stepped value, the seed written big-endian."""
        for which in (1, 0):
            for name, (seed, n, draw, new) in self.CASES.items():
                g = self.call(which, n=n, seed=seed)
                with self.subTest(which=which, case=name):
                    self.assertEqual(g.regs, self.regs(which, draw))
                    self.assertEqual(g.writes, [(self.SEED_LIN, new.to_bytes(2, "little"))])
                    self.assertEqual(g.rd(0x7B62), 0xBEEF)       # the decoy main seed is untouched

    def test_06d0_al_and_ah_cases(self):
        """Kills: AL = draw & 0xFF (B: draw 1199 -> AL would be 0xAF), AH from the wrong byte, AL true on the
        wrong draw (A: draw 2 -> 0; C: draw 1 -> 1)."""
        self.assertEqual(self.call(0, n=2048, seed=1).regs, {"ax": 0x0400, "dx": 1199})
        self.assertEqual(self.call(0).regs, {"ax": 0, "dx": 2})
        self.assertEqual(self.call(0, seed=0).regs, {"ax": 1, "dx": 1})

    def test_n_is_the_first_argument_and_16_bit_free_of_other_args(self):
        """Kills: n read from arg(1) or arg(2) (GateGuest gives (n, 0x...)), n ignored."""
        for which in (1, 0):
            g = GateGuest(1)
            g.args = (2048, 3, 5)
            import check
            check.wrapper_reader(which)(g)
            self.assertEqual(g.regs, self.regs(which, 1199))

    def test_the_seed_is_read_through_the_far_pointer(self):
        """Kills: the seed read from DS:7B62 (the decoy 0xBEEF), the pointer's segment or offset swapped."""
        for which in (1, 0):
            self.assertEqual(self.call(which, seed=0).regs, self.regs(which, 1))
            self.assertEqual(self.call(which, seed=0).writes, [(self.SEED_LIN, (6927).to_bytes(2, "little"))])

    def test_the_tally_counts_exactly(self):
        """Kills: any counter's condition or increment. Six calls A-F per wrapper: 'n+1 changes the draw' is
        True for D and F (2; A, B, C, E keep their draw); 'draw is 1' for C, E and F (3; A and D draw 2, so
        'draw == 2' gives 2); F also separates the honest draw from the n+1 falsifier's (1 -> 2); 'value+1' and
        'inverted' count every call (6); 'seed-write changes the seed' counts every call (6: 0688's step never maps a word to itself, the multiplier 0x7ABD
        - 1 being even and the increment odd). Under a falsifier the tally still counts the honest run."""
        for kw in ({}, {"falsifier": "n+1"}, {"falsifier": "value+1"}, {"falsifier": "seed-write"}):
            t06b1, t06d0 = {}, {}
            for name, (seed, n, _, _) in self.CASES.items():
                self.call(1, n=n, seed=seed, tally=t06b1, **kw)
                self.call(0, n=n, seed=seed, tally=t06d0, **kw)
            with self.subTest(**kw):
                self.assertEqual(t06b1, {"calls": 6, "n+1 changes the draw": 2, "value+1 changes AX": 6,
                                         "seed-write changes the seed": 6})
                self.assertEqual(t06d0, {"calls": 6, "draw is 1": 3, "inverted changes AL": 6,
                                         "seed-write changes the seed": 6})
        t = {}
        self.call(1, tally=t, falsifier="inverted")
        self.assertEqual(t["calls"], 1)

    def test_falsifier_n_plus_1(self):
        """Kills: the falsifier not adding 1 to n, adding it on the wrong wrapper's draw (06B1 case D: n = 3
        draws 3 instead of 2, the stepped seed is the honest one), the seed write or DX disturbed."""
        g = self.call(1, n=3, seed=1, falsifier="n+1")
        self.assertEqual(g.regs, {"ax": 3, "dx": 3})
        self.assertEqual(g.writes, [(self.SEED_LIN, (38348).to_bytes(2, "little"))])
        g = self.call(1, n=3, seed=0, falsifier="n+1")           # case E: n + 1 does not change the draw
        self.assertEqual(g.regs, {"ax": 1, "dx": 1})
        self.assertEqual({self.call(1, n=3, seed=s, falsifier="n+1").regs["dx"] for s in range(0, 65536, 5)},
                         {1, 2, 3, 4})

    def test_falsifier_value_plus_1(self):
        """Kills: AX not + 1, DX also + 1, the seed write dropped or changed."""
        g = self.call(1, falsifier="value+1")
        self.assertEqual(g.regs, {"ax": 3, "dx": 2})
        self.assertEqual(g.writes, [(self.SEED_LIN, (21363).to_bytes(2, "little"))])
        self.assertEqual(self.call(1, n=2048, seed=1, falsifier="value+1").regs, {"ax": 1200, "dx": 1199})

    def test_falsifier_inverted(self):
        """Kills: AL not flipped, AH or DX disturbed, the seed write dropped or changed."""
        g = self.call(0, falsifier="inverted")
        self.assertEqual(g.regs, {"ax": 1, "dx": 2})
        self.assertEqual(g.writes, [(self.SEED_LIN, (21363).to_bytes(2, "little"))])
        self.assertEqual(self.call(0, seed=0, falsifier="inverted").regs, {"ax": 0, "dx": 1})
        self.assertEqual(self.call(0, n=2048, seed=1, falsifier="inverted").regs, {"ax": 0x0401, "dx": 1199})

    def test_falsifier_seed_write(self):
        """Kills: the seed write kept, or the registers changed when it is dropped."""
        for which in (1, 0):
            g = self.call(which, falsifier="seed-write")
            self.assertEqual(g.writes, [])
            self.assertEqual(g.regs, self.regs(which, 2))
            self.assertEqual(g.word_at(self.SEED_LIN), 0x1234)   # the word stays the input seed


class LongGuest:
    """The Guest methods check.long_max_reader / long_mul_reader use, over literal registers and stack words:
    arg(i) is the i-th stack word past the far return address, reg/set_reg the register file (FLAGS merged)."""
    def __init__(self, args=(), flags=0x0ED7, **regs):
        self.args = args
        self.regs = {"flags": flags, "si": 0x3333, "di": 0x4444, "es": 0x5555, "bx": 0, "cx": 0, "ax": 0, "dx": 0}
        self.regs.update(regs)
        self.writes = []

    def arg(self, i):
        return self.args[i]

    def reg(self, name):
        return self.regs[name]

    def set_reg(self, name, value):
        self.regs[name] = value

    def put(self, linear, raw):
        self.writes.append((linear, bytes(raw)))


class LongReaderTests(unittest.TestCase):
    """T48: check.long_max_reader (214B:0D56) and check.long_mul_reader (23E4:0279) on literal registers. Every
    assertion is an exact full register file (including the scratch registers and FLAGS, merged into a guest FLAGS
    of 0x0ED7: all six arithmetic flags, IF and DF set, so a flag the model should clear shows), and the tallies
    are exact dicts. The mutation each test must kill is in tests/mutations_t48.py."""
    FLAGS_IN = 0x0ED7
    NON_ARITH = 0x0602                    # what the routines leave of FLAGS_IN: bit 1, IF, DF

    def max_call(self, a, b, **kw):
        import check
        g = LongGuest(args=(b & 0xFFFF, b >> 16, a & 0xFFFF, a >> 16))
        tally = kw.pop("tally", None)
        check.long_max_reader(tally, **kw)(g)
        return g

    def mul_call(self, ax, dx, bx, cx, tally=None, **kw):
        import check
        g = LongGuest(ax=ax, dx=dx, bx=bx, cx=cx)
        check.long_mul_reader(tally, **kw)(g)
        return g

    def test_max_registers_are_exact(self):
        """Kills: the arguments taken in another order (a/b swapped, lo/hi swapped), AX/DX/ES from the wrong word, ES
        left alone, FLAGS not merged or merged over the non-arithmetic bits, any branch of the model."""
        want = {  # (a, b): (ax, dx, es, arithmetic flags)
            (5, 3): (5, 0, 0, 0), (3, 5): (5, 0, 0, 0x91), (7, 7): (7, 0, 0, 0x44),
            (0x20000, 0x10005): (0, 2, 2, 0), (0x10005, 0x20000): (0, 2, 2, 0x95),
            (0xFFFFFFFF, 0xFFFFFFFE): (0xFFFF, 0xFFFF, 0xFFFF, 0), (0, 0xFFFFFFFF): (0, 0, 0, 0x11)}
        for (a, b), (ax, dx, es, fl) in want.items():
            g = self.max_call(a, b)
            with self.subTest(a=hex(a), b=hex(b)):
                self.assertEqual(g.regs, {"ax": ax, "dx": dx, "es": es, "flags": self.NON_ARITH | fl, "si": 0x3333,
                                          "di": 0x4444, "bx": 0, "cx": 0})
                self.assertEqual(g.writes, [])

    def test_max_tally_counts_exactly(self):
        """Kills: any counter's condition or increment. Eight calls: a wins 4 ((5,3) (0x20000,0x10005) (-1,-2) (0,-1)),
        b wins 2, ties 2; the high words differ in 3; min changes the result in the 6 non-ties; tie-a in none."""
        cases = [(5, 3), (3, 5), (7, 7), (0x20000, 0x10005), (0x10005, 0x20000), (0xFFFFFFFF, 0xFFFFFFFE),
                 (0x12345678, 0x12345678), (0, 0xFFFFFFFF), (0x18000, 0x17FFF)]
        want = {"calls": 9, "high words differ (jg or jl taken)": 3, "a wins": 5, "b wins": 2, "ties (a == b)": 2, "lowword-signed changes the result": 1,
                "min changes the result": 7, "tie-a changes the result": 0}
        for kw in ({}, {"falsifier": "min"}, {"falsifier": "tie-a"}, {"falsifier": "lowword-signed"}):
            tally = {}
            for a, b in cases:
                self.max_call(a, b, tally=tally, **kw)
            with self.subTest(**kw):
                self.assertEqual({k: v for k, v in tally.items() if v or k in want}, want)

    def test_max_falsifiers(self):
        """Kills: min not applied (returns the max), min applied on a tie, tie-a changing a non-tie, tie-a
        swapping the registers."""
        self.assertEqual((self.max_call(5, 3, falsifier="min").regs["ax"], self.max_call(5, 3, falsifier="min").regs["dx"]), (3, 0))
        g = self.max_call(0x10005, 0x20000, falsifier="min")
        self.assertEqual((g.regs["ax"], g.regs["dx"], g.regs["es"]), (5, 1, 2))     # min of the values; ES stays the honest winner's high word
        g = self.max_call(7, 7, falsifier="min")
        self.assertEqual((g.regs["ax"], g.regs["dx"]), (7, 0))
        # lowword-signed (jle for jbe): equal high words, low 0x8000 vs 0x7FFF: unsigned a wins, signed b wins
        g = self.max_call(0x18000, 0x17FFF, falsifier="lowword-signed")
        self.assertEqual((g.regs["ax"], g.regs["dx"]), (0x7FFF, 1))
        g = self.max_call(0x17FFF, 0x18000, falsifier="lowword-signed")
        self.assertEqual((g.regs["ax"], g.regs["dx"]), (0x7FFF, 1))
        for a, b in ((5, 3), (3, 5), (7, 7), (0x20000, 0x10005), (0xFFFFFFFF, 0xFFFFFFFE)):   # same side of 0x8000 or other high words: honest
            self.assertEqual(self.max_call(a, b, falsifier="lowword-signed").regs, self.max_call(a, b).regs)
        for a, b in ((5, 3), (3, 5), (7, 7), (0x10005, 0x20000)):                  # tie-a: equal results everywhere
            honest = self.max_call(a, b)
            self.assertEqual(self.max_call(a, b, falsifier="tie-a").regs, honest.regs)

    def test_mul_registers_are_exact(self):
        """Kills: the operands taken from other registers (CX is the LOW word of the second operand), a term
        dropped (AX*CX, AX*BX, DX*CX), the carry out of AX*CX dropped, SI/DI/BX/CX not left as the listing leaves
        them, FLAGS not those of the last add."""
        want = {  # (ax, dx, bx, cx): (ax, dx, bx, cx, si, di, arithmetic flags)
            (3, 0, 0, 5): (0xF, 0, 0, 0, 3, 0, 0x44), (2, 3, 5, 7): (0xE, 0x1F, 0xA, 0x15, 2, 3, 0),
            (0xFFFF, 0, 0, 2): (0xFFFE, 1, 0, 0, 0xFFFF, 0, 0), (2, 0, 1, 0): (0, 2, 2, 0, 2, 0, 0),
            (0, 1, 0, 1): (0, 1, 0, 1, 0, 1, 0), (0xFFFF, 0xFFFF, 0, 1): (0xFFFF, 0xFFFF, 0, 0xFFFF, 0xFFFF, 0xFFFF, 0x84)}
        for regs, (ax, dx, bx, cx, si, di, fl) in want.items():
            g = self.mul_call(*regs)
            with self.subTest(regs=regs):
                self.assertEqual(g.regs, {"ax": ax, "dx": dx, "bx": bx, "cx": cx, "si": si, "di": di, "es": 0x5555,
                                          "flags": self.NON_ARITH | fl})

    def test_mul_tally_counts_exactly(self):
        """Kills: any counter's condition or increment. Seven calls (3,0,0,5) (2,3,5,7) (0xFFFF,0,0,2) (0,0,0xFFFF,0xFFFF)
        (2,0,1,0) (0,1,0,1) (4,0,3,0): DX non-zero 2, BX non-zero 4, the mul-bx term non-zero 3 (calls 2, 5, 7), the
        mul-cx term non-zero 2 (calls 2, 6: the counts differ, so the two terms cannot be exchanged), a carry out of
        AX*CX 1, product+1 7, SI differs at entry 7 (the guest's SI is 0x3333, no AX)."""
        cases = [(3, 0, 0, 5), (2, 3, 5, 7), (0xFFFF, 0, 0, 2), (0, 0, 0xFFFF, 0xFFFF), (2, 0, 1, 0), (0, 1, 0, 1), (4, 0, 3, 0)]
        want = {"calls": 7, "DX operand (a high word) non-zero": 2, "BX operand (b high word) non-zero": 4,
                "mul bx term (AX * BX low word) non-zero = no-cross-term changes DX": 3,
                "mul cx term (DX * CX low word) non-zero": 2, "carry out of AX * CX non-zero": 1,
                "product+1 changes the result": 7, "SI differs at entry = the scratch falsifier shows": 7}
        for kw in ({}, {"falsifier": "product+1"}, {"falsifier": "no-cross-term"}, {"falsifier": "scratch"}):
            tally = {}
            for regs in cases:
                self.mul_call(*regs, tally=tally, **kw)
            with self.subTest(**kw):
                self.assertEqual(tally, want)
        tally = {}
        import check
        check.long_mul_reader(tally)(LongGuest(ax=3, dx=0, bx=0, cx=5, si=3))
        self.assertEqual(tally["SI differs at entry = the scratch falsifier shows"], 0)

    def test_mul_falsifiers(self):
        """Kills: product+1 adding to AX only (no carry into DX), adding 2, or changing the scratch registers; the
        no-cross-term falsifier dropping the wrong term (the DX*CX one), or changing AX; scratch writing SI."""
        g = self.mul_call(3, 0, 0, 5, falsifier="product+1")
        self.assertEqual((g.regs["ax"], g.regs["dx"], g.regs["bx"], g.regs["cx"]), (0x10, 0, 0, 0))
        g = self.mul_call(0xFFFF, 0, 0, 1, falsifier="product+1")                    # 0xFFFF + 1 carries into DX
        self.assertEqual((g.regs["ax"], g.regs["dx"]), (0, 1))
        g = self.mul_call(2, 3, 5, 7, falsifier="no-cross-term")                     # DX = 0x1F - 0xA = 0x15 (the DX*CX term only)
        self.assertEqual((g.regs["ax"], g.regs["dx"], g.regs["bx"], g.regs["cx"]), (0xE, 0x15, 0xA, 0x15))
        g = self.mul_call(0xFFFF, 0, 2, 0xFFFF, falsifier="no-cross-term")          # DX = 0xFFFC - 0xFFFE wraps to 0xFFFE (16 bits)
        self.assertEqual((g.regs["ax"], g.regs["dx"]), (1, 0xFFFE))
        g = self.mul_call(2, 3, 5, 7, falsifier="scratch")
        self.assertEqual((g.regs["si"], g.regs["di"], g.regs["ax"], g.regs["dx"]), (0x3333, 3, 0xE, 0x1F))   # SI left as it was


class LongProofTests(unittest.TestCase):
    """T48: the long readers PROVED against the original machine code on a bare machine (tests/longs_original.py
    places the listing's bytes at 2000:offset and calls them): the real Guest.hook(prove=True) runs the original,
    then the model, and compares AX/DX/SP/BP/SS/DS/CS/IP and every written byte outside the dead frame; the scratch
    registers and FLAGS are counted in scratch_differences. Fast (no savestate)."""
    MAX_AT, MUL_AT = "2000:0D56", "2000:0279"
    MAX_CASES = [(5, 3), (3, 5), (7, 7), (0x20000, 0x10005), (0x10005, 0x20000), (0xFFFF0000, 1), (1, 0xFFFF0000),
                 (0xFFFFFFFF, 0xFFFFFFFE), (0xFFFFFFFE, 0xFFFFFFFF), (0x18000, 0x17FFF), (0x17FFF, 0x18000),
                 (0x80000000, 0x7FFFFFFF), (0x7FFFFFFF, 0x80000000), (0x12345678, 0x12345678)]
    MUL_CASES = [(3, 0, 0, 5), (2, 3, 5, 7), (0xFFFF, 0, 0, 2), (0, 0, 0xFFFF, 0xFFFF), (2, 0, 1, 0), (0, 1, 0, 1),
                 (0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF), (0x1234, 0x5678, 0x9ABC, 0xDEF0)]

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / "tests"))
        import longs_original
        cls.O = longs_original

    def guest(self, caller):
        O = self.O
        mem = bytearray(0x40000)
        for off in (0x0D56, 0x0279):
            for o, b in O.routine_bytes(0x214B if off == 0x0D56 else 0x23E4, off).items():
                mem[O.ROUTINE_SEG * 16 + o] = b
        code = caller + bytes([0xF4])
        mem[O.CODE_SEG * 16:O.CODE_SEG * 16 + len(code)] = code
        regs = {"CS": O.CODE_SEG, "EIP": 0, "SS": O.SS, "ESP": O.SP0, "DS": 0, "EFLAGS": 0x0202, **O.SENTINEL}
        return Guest(memory=mem, regs=regs), O.CODE_SEG * 16 + len(code) - 1

    def max_program(self):
        push = lambda w: bytes([0xB8, w & 0xFF, (w >> 8) & 0xFF, 0x50])
        call = bytes([0x9A, 0x56, 0x0D, 0x00, 0x20])
        return b"".join(push(a >> 16) + push(a & 0xFFFF) + push(b >> 16) + push(b & 0xFFFF) + call for a, b in self.MAX_CASES)

    def mul_program(self):
        call = bytes([0x9A, 0x79, 0x02, 0x00, 0x20])
        return b"".join(bytes([0xB8, ax & 0xFF, ax >> 8, 0xBA, dx & 0xFF, dx >> 8, 0xBB, bx & 0xFF, bx >> 8,
                               0xB9, cx & 0xFF, cx >> 8]) + call for ax, dx, bx, cx in self.MUL_CASES)

    def run_max(self, falsifier=None):
        import check
        g, end = self.guest(self.max_program())
        tally = {}
        g.hook(self.MAX_AT, check.long_max_reader(tally, falsifier), ret=(True, 8), prove=True, ret_at=[0x0D8D])
        g.emulate(end, 20)
        return g, tally

    def run_mul(self, falsifier=None):
        import check
        g, end = self.guest(self.mul_program())
        tally = {}
        g.hook(self.MUL_AT, check.long_mul_reader(tally, falsifier), ret=(True, 0), prove=True, ret_at=[0x0293])
        g.emulate(end, 20)
        return g, tally

    def test_the_models_are_proved_with_no_scratch_difference(self):
        g, _ = self.run_max()
        self.assertEqual((g.hook_counts, g.proved_calls), ({self.MAX_AT: 14}, {self.MAX_AT: 14}))
        self.assertEqual(g.scratch_differences[self.MAX_AT], dict.fromkeys(("BX", "CX", "SI", "DI", "ES", "FLAGS"), 0))
        g, _ = self.run_mul()
        self.assertEqual((g.hook_counts, g.proved_calls), ({self.MUL_AT: 8}, {self.MUL_AT: 8}))
        self.assertEqual(g.scratch_differences[self.MUL_AT], dict.fromkeys(("BX", "CX", "SI", "DI", "ES", "FLAGS"), 0))

    def test_each_stopping_falsifier_is_stopped_naming_the_helper_and_the_call(self):
        from watched_match import ProofError
        for run, falsifier, call in ((self.run_max, "min", 1), (self.run_mul, "product+1", 1),
                                     (self.run_mul, "no-cross-term", 2), (self.run_max, "lowword-signed", 10)):   # case 1 (3*5) has no cross term: stops at call 2
            with self.subTest(falsifier=falsifier), self.assertRaises(ProofError) as cm:
                run(falsifier)
            self.assertIn(f"call #{call} of ", str(cm.exception))
            self.assertIn("register", str(cm.exception))

    def test_tie_a_is_not_stopped_it_changes_no_register(self):
        g, tally = self.run_max("tie-a")
        self.assertEqual(g.proved_calls, {self.MAX_AT: 14})
        self.assertEqual(tally["ties (a == b)"], 2)
        self.assertEqual(tally["tie-a changes the result"], 0)

    def test_the_scratch_falsifier_is_counted_not_stopped(self):
        g, _ = self.run_mul("scratch")
        self.assertEqual(g.proved_calls, {self.MUL_AT: 8})
        self.assertEqual(g.scratch_differences[self.MUL_AT], {"BX": 0, "CX": 0, "SI": 8, "DI": 0, "ES": 0, "FLAGS": 0})


if __name__ == "__main__":
    unittest.main()
