"""#318: the heavy jobs (the family runner, check.py, the unit suite) take a slot of tools/harness/heavy.sh.

runtime/heavy_slot.py's `take` re-runs the command under heavy.sh, so it waits behind the machine's other heavy
jobs; the real script runs here in a throwaway lock folder. Each rule has a test that fails without it."""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
import heavy_slot  # noqa: E402

HEAVY = ROOT / "tools" / "harness" / "heavy.sh"
FAMILY = ROOT / "experiments" / "E036-match-port" / "family.py"
USABLE = HEAVY.is_file() and os.access(HEAVY, os.X_OK)


# [designed] timing constants (nothing here is evidence about the machine; heavy.sh's defaults are justified in heavy.sh
# and notes/318-heavy/). POLL: 0.1 s instead of the default 1 s, so a queued job notices a freed slot in about 0.05 s and the
# tests stay short. HOLD: a holder keeps the only slot 2 s (about 20 polls, and well over the 0.1-0.3 s a Python child
# takes to start); the probe is asserted to wait more than 0.8 s, not 2 s, so a slow `up` read cannot make it flaky.
# The unit-suite test holds 3 s because ci_gate.py's interpreter start-up comes before its first poll.
POLL = "0.1"
HOLD = 2
SUITE_HOLD = 3
MIN_WAIT = 0.8


def env_for(lock_dir, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("CI", "HARNESS_HEAVY_HELD", "HARNESS_HEAVY_OFF")}
    env.update(HARNESS_HEAVY_DIR=str(lock_dir), HARNESS_HEAVY_SLOTS="1", HARNESS_HEAVY_POLL=POLL,
               PYTHONPATH=str(ROOT / "runtime"))
    env.update(extra)
    return env


# What a heavy job prints when it has its slot: whether it is inside a heavy job.
PROBE = "import heavy_slot, os; heavy_slot.take('probe'); print('held=' + os.environ.get('HARNESS_HEAVY_HELD', '-'))"


@unittest.skipUnless(USABLE, "tools/harness/heavy.sh is not executable")
class TakeTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.locks = Path(self._dir.name) / "locks"

    def probe(self, **extra):
        return subprocess.Popen([sys.executable, "-c", PROBE], env=env_for(self.locks, **extra),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def test_a_job_waits_for_the_slot_a_heavy_job_holds_and_then_runs(self):
        holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {HOLD}"], env=env_for(self.locks),
                                  stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.stdout.close)
        self.addCleanup(holder.wait)
        self.assertEqual(holder.stdout.readline(), "up\n")       # the holder has the only slot
        t0 = time.time()
        out, err = self.probe().communicate(timeout=30)
        self.assertGreater(time.time() - t0, MIN_WAIT, "the probe ran while the slot was held")
        self.assertIn("heavy: probe: waiting for a slot (0 ahead)", err)
        self.assertEqual(out, "held=probe\n")                    # it ran inside its own heavy job

    def test_inside_a_heavy_job_it_runs_at_once(self):
        out, err = self.probe(HARNESS_HEAVY_HELD="outer").communicate(timeout=30)
        self.assertEqual(out, "held=outer\n")                    # not re-run: the outer job holds the slot
        self.assertEqual(err, "")

    def test_in_ci_and_when_switched_off_it_runs_as_it_is(self):
        for var in ("CI", "HARNESS_HEAVY_OFF"):
            out, err = self.probe(**{var: "1"}).communicate(timeout=30)
            self.assertEqual((out, err), ("held=-\n", ""), var)

    def test_the_weight_is_the_number_of_slots_held(self):
        code = ("import heavy_slot; heavy_slot.take('w', weight=2); import subprocess; "
                f"print(subprocess.run(['{HEAVY}', '--status'], capture_output=True, text=True).stdout)")
        r = subprocess.run([sys.executable, "-c", code], env=env_for(self.locks, HARNESS_HEAVY_SLOTS="2"),
                           capture_output=True, text=True, timeout=30)
        # --status asked from inside the job: both slots are busy
        self.assertIn("2 of 2 slots busy", r.stdout, r.stdout + r.stderr)

    def test_take_replaces_the_process_by_heavy_sh_with_the_original_command(self):
        with mock.patch.dict(os.environ, {"HARNESS_HEAVY_HELD": "", "CI": "", "HARNESS_HEAVY_OFF": ""}), \
                mock.patch("heavy_slot.os.execv") as execv:
            heavy_slot.take("x", weight=2, argv=["python3", "-m", "pkg.mod", "--a"])
        execv.assert_called_once_with(str(HEAVY), [str(HEAVY), "--weight", "2", "x", "--", "python3", "-m", "pkg.mod", "--a"])


class ConstantsTest(unittest.TestCase):
    def test_the_timings_relate_as_their_comment_says(self):
        self.assertLess(MIN_WAIT, HOLD)               # the probe must be able to see the wait
        self.assertGreaterEqual(HOLD, 10 * float(POLL))
        self.assertGreater(SUITE_HOLD, 1)             # more than interpreter start-up plus a few polls


class FamilyWorkersTest(unittest.TestCase):
    """family.py holds one slot per match process: --workers 2 holds two."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(FAMILY.parent))
        import family
        cls.family = family

    OUT = ["--family", "S", "--out", "never-written.jsonl"]

    def run_main(self, argv):
        """The `workers` main() hands to run_family for this command line (run_family stubbed: no match runs)."""
        seen = []
        stub = mock.patch.object(self.family, "run_family", side_effect=lambda sel, out, workers, *a, **k: seen.append(workers) or [])
        with stub, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(self.family.main(argv), 0)
        return seen[0]

    def test_the_weight_is_the_workers_main_uses_whatever_the_spelling(self):
        # each spelling argparse accepts: the last of a repeated option wins, --opt=value, an abbreviation
        for tail, workers in ((["--workers", "2"], 2), (["--workers=2"], 2), (["--workers", "1", "--workers", "2"], 2),
                              (["--workers", "2", "--workers", "1"], 1), (["--workers=1", "--workers=2"], 2),
                              (["--work", "2"], 2), (["--wor=2"], 2), (["--workers", "2", "--wor", "1"], 1), ([], 1)):
            argv = self.OUT + tail
            self.assertEqual(self.family._workers(argv), self.run_main(argv), argv)   # the two cannot disagree
            self.assertEqual(self.family._workers(argv), workers, argv)

    def test_a_command_line_main_refuses_holds_no_slot(self):
        for argv in (self.OUT + ["--workers", "0"], self.OUT + ["--workers", "-1"], self.OUT + ["--workers", "3"],
                     self.OUT + ["--workers", "x"], self.OUT + ["--workers"], self.OUT + ["--workers", "1", "--workers", "9"],
                     self.OUT + ["--bogus"], ["--out", "x"], ["--help"]):
            self.assertIsNone(self.family._workers(argv), argv)   # argparse's own error then speaks, once, from main()

    def test_parsed_prints_nothing_and_returns_none_on_a_refused_line(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertIsNone(heavy_slot.parsed(self.family.parser(), ["--workers", "3"]))
        self.assertEqual(err.getvalue(), "")


@unittest.skipUnless(USABLE, "tools/harness/heavy.sh is not executable")
class EntryPointsTest(unittest.TestCase):
    """The three commands call heavy_slot.take as their first act when run as scripts (not when imported)."""

    def test_the_entry_points_take_a_slot(self):
        for rel, name in (("experiments/E036-match-port/family.py", "family"), ("runtime/original_match/check.py", "check"),
                          ("tools/ci_gate.py", "unit-suite")):
            text = (ROOT / rel).read_text()
            tail = text[text.index('if __name__ == "__main__":'):]
            self.assertIn("heavy_slot", tail, rel)
            self.assertIn(f'take("{name}"', tail, rel)

    def test_the_unit_suite_waits_in_the_queue(self):
        with tempfile.TemporaryDirectory() as d:
            env = env_for(Path(d) / "locks")
            holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {SUITE_HOLD}"], env=env,
                                      stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(holder.stdout.readline(), "up\n")
                # a module that is not slow is refused, but only after the wait: the job was queued
                gate = str(ROOT / "tools" / "ci_gate.py")
                r = subprocess.run([sys.executable, gate, "run-tests", "--modules", "nope"], env=env,
                                   capture_output=True, text=True, timeout=60)
                self.assertIn("heavy: unit-suite: waiting for a slot", r.stderr)
                self.assertEqual(r.returncode, 2)
            finally:
                holder.wait()
                holder.stdout.close()

    def test_a_command_line_the_script_refuses_does_not_queue(self):
        # the slot is held for SUITE_HOLD s; a refused line must answer at once with argparse's message, not wait for it
        with tempfile.TemporaryDirectory() as d:
            env = env_for(Path(d) / "locks")
            holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", f"echo up; sleep {SUITE_HOLD}"], env=env,
                                      stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(holder.stdout.readline(), "up\n")
                for argv in ([str(ROOT / "tools" / "ci_gate.py"), "run-tests", "--bogus"],
                             [str(FAMILY), "--family", "S", "--out", "x", "--workers", "1", "--workers", "9"],
                             ["-m", "original_match.check", "--bogus"]):
                    t0 = time.time()
                    r = subprocess.run([sys.executable, *argv], env=env, cwd=ROOT / "runtime" if argv[0] == "-m" else ROOT,
                                       capture_output=True, text=True, timeout=60)
                    self.assertNotEqual(r.returncode, 0, argv)
                    self.assertNotIn("waiting", r.stderr, argv)
                    self.assertLess(time.time() - t0, SUITE_HOLD - 1, argv)
                    self.assertEqual(r.stderr.count("error:"), 1, argv)       # argparse speaks once
            finally:
                holder.wait()
                holder.stdout.close()


if __name__ == "__main__":
    unittest.main()
