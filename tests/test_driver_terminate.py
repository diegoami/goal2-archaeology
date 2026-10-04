"""Driver.terminate (#19) and the DOS-prompt restore edge of launch()'s parenthetical (R1, T07 review).

#19: DOSBox-X ignored SIGTERM after a restore in 30 of 30 E002 records (F003) and was ended by
SIGKILL only after 10 s; the fixed terminate bounds the SIGTERM wait (TERM_GRACE) and SIGKILLs the
group, logging the method and the time to `events`, which each record's log carries. The terminate
tests run real OS processes that stand in for DOSBox-X and Xvfb -- one that ignores SIGTERM like the
restored DOSBox-X of F003, one that exits on it like F001's M:terminate measured -- so they need no
DOSBox-X and run on CI. Every signal goes to a process group the driver started
(start_new_session=True), by PID, never pkill.

R1: launch()'s parenthetical says a restore into a session booted to the DOS prompt (GOAL never
started) failed with "Save state corrupted! ... Memory_Size" and no savestate afterwards; the
driver's guard is launch()'s own title-screen wait and displace key before any restore. The test
boots a prompt session through Driver.launch() itself (a subclass whose autoexec omits `goal`) and
asserts the guard holds there: launch ends in its own "title screen: not seen" timeout and no
restore is attempted. It needs DOSBox-X, Xvfb and xdotool, so it skips everywhere they are absent
(CI), runs locally, and fails if the guard is removed (see the class docstring).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import driver  # noqa: E402

LOCAL = all(shutil.which(t) for t in ("dosbox-x", "Xvfb", "xdotool"))

POLITE = "import time; print('up', flush=True); time.sleep(60)"
IGNORES_SIGTERM = ("import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); "
                   "print('up', flush=True); time.sleep(60)")


def spawn(code):
    """One process in its own session (what the driver does when it starts one); its pid is its group.
    Waits for the child's `up` line, printed after its SIGTERM handler is installed, so a test's
    SIGTERM cannot race the child's startup (a young python still has the default disposition)."""
    p = subprocess.Popen([sys.executable, "-c", code], stdout=subprocess.PIPE, text=True,
                         start_new_session=True)
    line = p.stdout.readline().strip()
    if line != "up":
        p.kill()
        p.wait()
        raise AssertionError(f"stand-in did not come up: {line!r}")
    return p


def events_log(d):
    return "; ".join(w for _, w in d.events)


class Terminate(unittest.TestCase):
    """terminate() against real processes: bounded, logged, and only the driver's own groups."""

    def setUp(self):
        self.d = driver.Driver(workdir=Path(tempfile.mkdtemp(prefix="drv-term-")))
        self.extra = []

    def tearDown(self):
        for p in self.extra + [self.d.dbx, self.d.xvfb]:
            if p and p.poll() is None:
                p.kill()
                p.wait()
            if p and p.stdout and not p.stdout.closed:
                p.stdout.close()
        shutil.rmtree(self.d.workdir, ignore_errors=True)

    def test_a_sigterm_ignoring_process_is_gone_within_2s(self):
        # F003: DOSBox-X ignored SIGTERM after a restore in 30 of 30 E002 records and was ended by
        # SIGKILL only after the 10 s wait; the fix bounds that wait to TERM_GRACE.
        self.d.dbx = spawn(IGNORES_SIGTERM)
        self.d.xvfb = spawn(POLITE)
        t0 = time.monotonic()
        gone = self.d.terminate()
        dt = time.monotonic() - t0
        self.assertTrue(gone)
        self.assertLess(dt, 2.0, f"terminate took {dt:.2f}s")
        self.assertFalse(Path(f"/proc/{self.d.dbx.pid}").exists())
        self.assertFalse(Path(f"/proc/{self.d.xvfb.pid}").exists())

    def test_the_log_names_the_method_and_the_time_for_each_process(self):
        # Done-when of #19: the record's log shows the method and the time; the events carry them.
        self.d.dbx = spawn(IGNORES_SIGTERM)
        self.d.xvfb = spawn(POLITE)
        self.d.terminate()
        log = events_log(self.d)
        self.assertRegex(log, r"dosbox-x pid \d+ alive [0-9.]+s after SIGTERM \(grace 0\.5s\): SIGKILL to its group")
        self.assertRegex(log, r"dosbox-x pid \d+ ended by SIGKILL [0-9.]+s after the first signal")
        self.assertRegex(log, r"Xvfb pid \d+ ended by SIGTERM [0-9.]+s after the first signal")
        self.assertNotRegex(log, r"Xvfb pid \d+(?:(?!dosbox-x).)*SIGKILL")

    def test_a_clean_sigterm_exit_is_never_sigkilled(self):
        # F001 M:terminate: a session that restored nothing exited 0.02 s after SIGTERM; such a
        # process must end by SIGTERM alone. Fails if the driver is switched to SIGKILL directly.
        self.d.dbx = spawn(POLITE)
        self.d.xvfb = spawn(POLITE)
        gone = self.d.terminate()
        self.assertTrue(gone)
        log = events_log(self.d)
        self.assertNotIn("SIGKILL", log)
        self.assertRegex(log, r"dosbox-x pid \d+ ended by SIGTERM [0-9.]+s after the first signal")

    def test_no_group_the_driver_did_not_start_is_signalled(self):
        # Another project's session on this shared machine: its own group, unknown to the driver.
        innocent = spawn(POLITE)
        self.extra.append(innocent)
        real_killpg, seen = os.killpg, []
        self.d.dbx = spawn(IGNORES_SIGTERM)
        self.d.xvfb = spawn(POLITE)
        with mock.patch("os.killpg", lambda pgid, sig: (seen.append((pgid, sig)), real_killpg(pgid, sig))[1]):
            gone = self.d.terminate()
        self.assertTrue(gone)
        self.assertTrue(seen, "terminate sent no signal at all")
        groups = {self.d.dbx.pid, self.d.xvfb.pid}
        self.assertEqual({pgid for pgid, _ in seen}, groups)
        self.assertTrue(Path(f"/proc/{innocent.pid}").exists(), "a process the driver did not start was killed")
        self.assertIn(innocent.pid, [p.pid for p in self.extra])


@unittest.skipUnless(LOCAL, "dosbox-x/Xvfb/xdotool not on PATH (CI): the edge needs DOSBox-X")
class DosPromptRestoreEdge(unittest.TestCase):
    """R1 (T07 review): the DOS-prompt restore edge must be exercised through Driver.launch() and
    its own guard, so that removing the guard makes this test fail.

    launch()'s parenthetical documents that restoring a savestate into a session booted to the DOS
    prompt (GOAL never started) failed once with "Save state corrupted! Program in inconsistent
    state! - Memory_Size" and no savestate afterwards; the guard is launch()'s wait for the title
    screen plus the displace key before any restore. The test boots a prompt session through
    launch() itself -- PromptBoot below omits only `goal` from the autoexec -- and asserts the
    guard holds there: launch ends in its own "title screen: not seen" timeout and sends no
    Host+L. With the guard removed, launch() goes straight from a focused window to restore() at
    the prompt: "Host+L sent" is logged and launch raises restore's own timeout instead of the
    guard's -- the test fails. Needs DOSBox-X, Xvfb and xdotool: skipped on CI, run locally."""

    # The prompt session never shows the title, so this wait is the guard's full bound, run each
    # time the test executes; 8 s keeps the local run short and is what launch() is asked for.
    TITLE_WAIT = 8

    def setUp(self):
        try:
            self.st = driver.StartState("title")
        except FileNotFoundError:
            self.st = driver.make_state("title")
        self.d = None

    def tearDown(self):
        if self.d:
            self.d.terminate()  # only the groups this driver started; a no-op when launch never got there

    def prompt_boot_driver(self):
        """The driver's own launch path from a DOS-prompt boot: the guard's edge. Only the autoexec
        differs from Driver's (no `goal`); window wait, focus, title wait and restore are launch()'s."""
        class PromptBoot(driver.Driver):
            def conf_text(self):
                return super().conf_text().replace("goal\nexit\n", "")
        self.d = PromptBoot(workdir=driver.SCRATCH / "test-dosprompt")
        return self.d

    def test_launch_never_restores_into_a_dos_prompt_session(self):
        d = self.prompt_boot_driver()
        with self.assertRaisesRegex(RuntimeError, r"title screen: not seen"):  # the guard's own timeout
            d.launch(self.st, timeout=self.TITLE_WAIT)
        # the guard fired before any restore: the driver's own log has no Host+L. This and the
        # timeout message above are the assertions that fail when the guard is removed (launch()
        # then goes straight to restore(), logs Host+L and raises restore's own timeout).
        self.assertNotIn("Host+L sent", events_log(d))
        # The corruption launch()'s parenthetical documents never happens here: no "Save state
        # corrupted!" in DOSBox-X's output. ("Memory_Size" alone is no marker: each Host+S logs a
        # benign "Memory_Size is 4 bytes" line, as this healthy prompt session's log shows. The
        # check is also weak in the other direction -- the corruption line is buffered and can be
        # lost to terminate()'s SIGKILL -- which is why the two assertions above carry the test.)
        out = (d.workdir / "dosbox.out").read_text(errors="replace")
        self.assertNotIn("Save state corrupted!", out)


if __name__ == "__main__":
    unittest.main()
