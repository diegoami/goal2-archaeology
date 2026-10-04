"""Driver.terminate (#19) and the DOS-prompt restore edge of launch()'s parenthetical (R1, T07 review).

#19: DOSBox-X ignored SIGTERM after a restore in 30 of 30 E002 records (F003) and was ended by
SIGKILL only after 10 s; the fixed terminate bounds the SIGTERM wait (TERM_GRACE) and SIGKILLs the
group, logging the method and the time to `events`, which each record's log carries. The terminate
tests run real OS processes that stand in for DOSBox-X and Xvfb -- one that ignores SIGTERM like the
restored DOSBox-X of F003, one that exits on it like F001's M:terminate measured -- so they need no
DOSBox-X and run on CI. Every signal goes to a process group the driver started
(start_new_session=True), by PID, never pkill.

R1: launch()'s parenthetical says a restore into a session booted to the DOS prompt (GOAL never
started) failed with "Save state corrupted! ... Memory_Size" and no savestate afterwards; that test
needs DOSBox-X, Xvfb and xdotool, so it skips everywhere they are absent (CI) and runs locally.
"""
import os
import shutil
import signal
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
    """R1 (T07 review): launch()'s parenthetical documents that restoring a savestate into a session
    booted to the DOS prompt (GOAL never started) failed once with "Save state corrupted! Program in
    inconsistent state! - Memory_Size" and no savestate afterwards; the driver therefore boots GOAL
    to the title screen before any restore. This test visits that edge: it builds the guard-removed
    session itself (launch()'s autoexec without `goal`), drives the driver's own restore, and asserts
    the documented failure. Local only; skipped on CI."""

    def setUp(self):
        try:
            self.st = driver.StartState("title")
        except FileNotFoundError:
            self.st = driver.make_state("title")

    def session_at_the_dos_prompt(self):
        """launch()'s mechanics minus the guard: the autoexec mounts C: and stops at the prompt."""
        d = driver.Driver(workdir=driver.SCRATCH / "test-dosprompt")
        d.workdir.mkdir(parents=True, exist_ok=True)
        (d.workdir / "cap").mkdir(exist_ok=True)
        driver.verify_release(driver.CACHE)
        shutil.rmtree(d.game_dir, ignore_errors=True)
        shutil.copytree(driver.CACHE, d.game_dir)
        conf = d.conf_text().replace("goal\nexit\n", "")  # the guard: launch() runs GOAL to the title
        (d.workdir / "dosbox.conf").write_text(conf)
        d.t0 = time.monotonic()
        d._start_xvfb()
        d.env = dict(os.environ, DISPLAY=d.display, SDL_AUDIODRIVER="dummy")
        args = [os.environ.get("DOSBOX_X", "dosbox-x"), "-conf", str(d.workdir / "dosbox.conf"),
                "-fastlaunch", "-nogui", "-nomenu", "-savedir", str(d.workdir),
                "-set", f"dosbox savefile={d.savefile}"]
        d.dbx_out = open(d.workdir / "dosbox.out", "w")  # closed by the test, after terminate()
        d.dbx = subprocess.Popen(args, env=d.env, stdout=d.dbx_out,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        d.log("dosbox-x started")
        d.wid = d._wait_window(15)
        d._x("windowfocus", d.wid)
        return d

    def wait_prompt(self, d, timeout=15):
        """Poll savestates until the screen shows a DOS prompt (Host+S works before the load)."""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            text = d.screen().text()
            if ">" in text:
                return text
            time.sleep(0.3)
        raise RuntimeError("no DOS prompt seen within 15s")

    def test_restore_into_a_dos_prompt_session_fails_as_documented(self):
        d = self.session_at_the_dos_prompt()
        out = ""
        try:
            prompt = self.wait_prompt(d)
            self.assertIn("C:\\>", prompt)  # the session sits at the prompt, GOAL never started
            with self.assertRaises(RuntimeError):
                d.restore(self.st, timeout=8)
            # and no savestate afterwards (F003 Method), while Host+S worked at the prompt above
            with self.assertRaises(RuntimeError):
                d.save_state(timeout=5, resend_after=2.0)
            # DOSBox-X's stdout is block-buffered and the corruption line only reaches the file when
            # it handles a SIGTERM (measured 0.16 s after the signal, twice, scratch probes of
            # 2026-10-04; the delay varies, so poll). SIGTERM to the group the driver started here;
            # terminate() in the finally sends its own, and no SIGKILL has happened yet.
            if d.dbx.poll() is None:
                os.killpg(d.dbx.pid, signal.SIGTERM)
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                out = (d.workdir / "dosbox.out").read_text(errors="replace")
                if "Save state corrupted!" in out and "Memory_Size" in out:
                    break
                time.sleep(0.1)
        finally:
            gone = d.terminate()
            d.dbx_out.close()
        self.assertTrue(gone)
        self.assertIn("Save state corrupted!", out)
        self.assertIn("Memory_Size", out)


if __name__ == "__main__":
    unittest.main()
