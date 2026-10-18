"""#318: the heavy jobs (the family runner, check.py, the unit suite) take a slot of tools/harness/heavy.sh.

runtime/heavy_slot.py's `take` re-runs the command under heavy.sh, so it waits behind the machine's other heavy
jobs; the real script runs here in a throwaway lock folder. Each rule has a test that fails without it."""
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


def env_for(lock_dir, **extra):
    env = {k: v for k, v in os.environ.items() if k not in ("CI", "HARNESS_HEAVY_HELD", "HARNESS_HEAVY_OFF")}
    env.update(HARNESS_HEAVY_DIR=str(lock_dir), HARNESS_HEAVY_SLOTS="1", HARNESS_HEAVY_POLL="0.1",
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
        holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", "echo up; sleep 2"], env=env_for(self.locks),
                                  stdout=subprocess.PIPE, text=True)
        self.addCleanup(holder.stdout.close)
        self.addCleanup(holder.wait)
        self.assertEqual(holder.stdout.readline(), "up\n")       # the holder has the only slot
        t0 = time.time()
        out, err = self.probe().communicate(timeout=30)
        self.assertGreater(time.time() - t0, 0.8, "the probe ran while the slot was held")
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


class FamilyWorkersTest(unittest.TestCase):
    """family.py holds one slot per match process: --workers 2 holds two."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(FAMILY.parent))
        import family
        cls.family = family

    def test_workers_read_from_the_command_line(self):
        w = self.family._workers
        self.assertEqual(w(["--family", "ALL"]), 1)
        self.assertEqual(w(["--workers", "2", "--out", "x"]), 2)
        self.assertEqual(w(["--workers=2"]), 2)
        self.assertEqual(w(["--workers", "1"]), 1)
        self.assertEqual(w(["--workers", "7"]), 1)               # main() refuses it; no slots are held for it
        self.assertEqual(w(["--workers"]), 1)


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
            holder = subprocess.Popen([str(HEAVY), "holder", "--", "sh", "-c", "echo up; sleep 3"], env=env,
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


if __name__ == "__main__":
    unittest.main()
