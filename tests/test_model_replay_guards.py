"""T24 rework round 1, R3 and R4: replay.py's evidence guards, on fakes (no DOSBox-X).

R3: the probe's trace dump refuses a path that exists before launch — a committed
trace is measured evidence and is never overwritten (L207). The round-1 review sent
the default suffix "2" at the already committed trace-e010-r0010-replay2.json.

R4: while a key is pending and the screen is UNCHANGED, the probe neither resends
(the resend storms the DOS key buffer and opens 0791:ED8A's menu once per minute)
nor resets the read counter — the KEY_TAKEN_READS abort must stay armed; and a
timeout without full time is a failure, not a success. The review's mocked
unchanged team screen sent 49 Enters over 50 reads and returned 0.

Each test fails when its guard is removed from replay.py (the mutation runs are in
the PR body; rule 9)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments" / "E010-q010-quick-engine"))
import replay  # noqa: E402  (inserts runtime/driver into sys.path itself)

SCRATCH = ROOT / "scratch" / "test-replay-guards"


class FakeScreen:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text

    def lines(self):
        return self._text.split("\n")

    def digest(self):
        return "digest-" + str(hash(self._text) & 0xFFFFFF)


class FakeState:
    """Only what poll() reads: a screen plus constant DS words."""

    def __init__(self, text):
        self._sc = FakeScreen(text)

    def screen(self):
        return self._sc

    def ds_word(self, off):
        return 1

    def ds_bytes(self, off, n):
        return bytes([0]) * n


class FakeDriver:
    """d.read() pops one (times, state, data) per call, then repeats the last;
    d.keys() records every key it was sent."""

    def __init__(self, screens):
        self.screens = list(screens)
        self.i = 0
        self.keys_sent = []
        self.game_dir = "/nowhere"
        self.drive_layout = lambda: {}

    def read(self):
        if self.i < len(self.screens):
            sc = self.screens[self.i]
            self.i += 1
        else:
            sc = self.screens[-1]
        return None, sc if isinstance(sc, FakeState) else FakeState(sc), b""

    def keys(self, k):
        self.keys_sent.append(k)


TEAM_SCREEN = "location:  play  (default)\nTeam Screen\nstuff\nquit"
PLAIN = "the match runs\nno key here\nno full time"


class Args:
    timeout = 900.0
    grab_seed = None
    record = "E010-r0010"
    suffix = "test"
    cycles = 30000


def poll_with(d, timeout=900.0):
    """poll() on a fresh trace path inside the worktree scratch dir; the trace file
    is removed afterwards (test scratch, never committed)."""
    SCRATCH.mkdir(parents=True, exist_ok=True)
    target = SCRATCH / "trace-test.json"
    if target.exists():
        target.unlink()
    writer = replay.TraceWriter(target)
    a = Args()
    a.timeout = timeout
    import time
    try:
        return replay.poll(d, a, writer, time.monotonic()), writer
    finally:
        target.unlink()


class TestTraceWriter(unittest.TestCase):
    """R3: a dump to an existing path refuses (round 1 review: dump() unconditionally
    overwrote, and the default suffix selected a committed trace)."""

    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        for p in SCRATCH.iterdir():
            p.unlink()

    def tearDown(self):
        if SCRATCH.is_dir():
            for p in SCRATCH.iterdir():
                p.unlink()
            SCRATCH.rmdir()

    def test_existing_path_refused_and_not_overwritten(self):
        target = SCRATCH / "trace-test.json"
        target.write_text("ORIGINAL EVIDENCE\n")
        with self.assertRaises(SystemExit):
            replay.TraceWriter(target)
        self.assertEqual(target.read_text(), "ORIGINAL EVIDENCE\n")

    def test_fresh_path_dumps_incrementally(self):
        target = SCRATCH / "trace-test.json"
        writer = replay.TraceWriter(target)
        writer.dump([{"n": 1}])
        writer.dump([{"n": 1}, {"n": 2}])
        import json
        self.assertEqual(json.loads(target.read_text()), [{"n": 1}, {"n": 2}])

    def test_main_refuses_committed_trace_before_launch(self):
        # the review's exact case: the default suffix "2" selects the committed
        # trace-e010-r0010-replay2.json; the refusal fires before any launch
        self.assertTrue(replay.trace_path("E010-r0010", "2").exists())
        with self.assertRaises(SystemExit):
            replay.main(["--record", "E010-r0010"])
        with self.assertRaises(SystemExit):
            replay.main(["--record", "E010-r0010", "--suffix", "2"])


class TestPendingKeyGuard(unittest.TestCase):
    """R4: an unchanged screen while a key is pending neither resends nor resets."""

    def test_unchanged_screen_never_resends_and_aborts(self):
        d = FakeDriver([TEAM_SCREEN] * 50)
        rc, _ = poll_with(d)
        self.assertEqual(rc, 1)
        # exactly ONE Enter: the first send; every later read waits without resending
        self.assertEqual(d.keys_sent, ["Enter"])
        # the counter was never reset: the abort fired after KEY_TAKEN_READS + 1
        # reads past the send, not after 50
        self.assertLess(d.i, 50)

    def test_acted_key_allows_the_next_wait(self):
        # the screen changes after the key (acted on), a second wait behaves like the
        # first (one Enter), then the match runs on with no further key
        d = FakeDriver([TEAM_SCREEN, TEAM_SCREEN, PLAIN, PLAIN, TEAM_SCREEN, TEAM_SCREEN, PLAIN])
        rc, _ = poll_with(d, timeout=0.5)
        self.assertEqual(d.keys_sent, ["Enter", "Enter"])
        self.assertEqual(rc, 1)          # no full time anywhere: failure (R4's timeout rule)

    def test_full_time_success(self):
        ft = "result\nFULL TIME\nx\ny"
        d = FakeDriver([PLAIN, PLAIN, ft])
        rc, _ = poll_with(d)
        self.assertEqual(rc, 0)
        self.assertEqual(d.keys_sent, [])

    def test_timeout_without_full_time_fails(self):
        # no key wait ever fires (the screen keeps changing), full time never comes:
        # the timeout must return failure, not the round-1 success
        screens = [f"minute {i}\nmid-match\nno key\n" for i in range(200)]
        d = FakeDriver(screens)
        rc, _ = poll_with(d, timeout=0.05)
        self.assertEqual(rc, 1)
        self.assertEqual(d.keys_sent, [])


if __name__ == "__main__":
    unittest.main()
