"""T24 rework round 1, R3 and R4: replay.py's evidence guards, on fakes (no DOSBox-X).

R3: the probe's trace dump refuses a path that exists before launch — a committed
trace is measured evidence and is never overwritten (L207). The round-1 review sent
the default suffix "2" at the already committed trace-e010-r0010-replay2.json.

R1 (round 2): the refusal must be an EXCLUSIVE, ATOMIC reservation made before
launch and kept for every incremental write — two probes picking the same fresh
suffix must not both pass a mere existence check and then truncate each other's
evidence.

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
        writer.close()
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
        try:
            writer.dump([{"n": 1}])
            writer.dump([{"n": 1}, {"n": 2}])
            import json
            self.assertEqual(json.loads(target.read_text()), [{"n": 1}, {"n": 2}])
        finally:
            writer.close()

    def test_two_writers_same_fresh_path_second_refused_first_intact(self):
        # round-2 review R1: the pre-fix guard only checked `path.exists()`, so
        # two probes that picked the same fresh suffix could BOTH construct a
        # TraceWriter before either dumped its first read, both pass the check,
        # launch, and then truncate the same evidence file through write_text().
        # Here writer A has reserved the path but not dumped yet (exactly the
        # interleave the review reproduced); B's claim must be refused at
        # construction — atomically — and A's measured content must survive.
        # Against the pre-fix TraceWriter both constructions succeed and B's
        # dump silently replaces A's, failing this test (mutation run in the PR
        # body; rule 9).
        target = SCRATCH / "trace-test.json"
        a = replay.TraceWriter(target)
        try:
            with self.assertRaises(SystemExit):
                replay.TraceWriter(target)
            a.dump([{"n": 1, "seed": 0x1234}])
            a.dump([{"n": 1, "seed": 0x1234}, {"n": 2, "seed": 0x5678}])
            import json
            self.assertEqual(json.loads(target.read_text()),
                             [{"n": 1, "seed": 0x1234}, {"n": 2, "seed": 0x5678}])
        finally:
            a.close()

    def test_main_refuses_committed_trace_before_launch(self):
        # the review's exact case: the default suffix "2" selects the committed
        # trace-e010-r0010-replay2.json; the refusal fires before any launch.
        # Driver is stubbed so that, even with the refusal REMOVED (the mutation
        # run), main can never reach a real DOSBox-X launch from this test —
        # the round-1 defect must fail the test, not launch the game
        self.assertTrue(replay.trace_path("E010-r0010", "2").exists())
        real_driver = replay.driver.Driver

        class NoLaunch:
            def __init__(self, *a, **kw):
                raise AssertionError("main got past the trace refusal and built a Driver")

        replay.driver.Driver = NoLaunch
        try:
            with self.assertRaises(SystemExit):
                replay.main(["--record", "E010-r0010"])
            with self.assertRaises(SystemExit):
                replay.main(["--record", "E010-r0010", "--suffix", "2"])
        finally:
            replay.driver.Driver = real_driver


class TestPendingKeyGuard(unittest.TestCase):
    """R4: an unchanged screen while a key is pending neither resends nor resets."""

    def test_unchanged_screen_never_resends_and_aborts(self):
        # timeout 2 s: ample for the fixed probe (it aborts at read 13) but bounded
        # for the round-1 defect, which would otherwise spin resending for 900 s
        d = FakeDriver([TEAM_SCREEN] * 50)
        rc, _ = poll_with(d, timeout=2.0)
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
