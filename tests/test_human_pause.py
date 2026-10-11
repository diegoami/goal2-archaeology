"""T39b: the recorder's pause (DOSBox-X's own, F12+P; the title says PAUSED) and the key map's
paused spans. Every test runs on a fake clock with no emulator; each fails with its rule removed
(experiments/E015-human-playthrough/mutate_pause.py makes the mutations in place)."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("human_recorder_pause", ROOT / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))

PROBE_LIMIT = 5000   # a loop that polls the title without sleeping never ends on a fake clock


def loop_watcher(session, paused_spans, arrivals):
    """A Watcher made without __init__ (as the loop tests in test_human_keys do), on a fake clock
    that moves only when the loop sleeps; `paused_spans` are the [start, end) seconds the window
    title says PAUSED; `arrivals` are (time, event, keysym) key events. Returns (watcher, sends,
    keys, probes): `sends` collects (time, origin) of every save request the loop makes."""
    now = [0.0]
    w = rec.Watcher.__new__(rec.Watcher)
    w.clock = lambda: now[0]
    w.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
    w.t0 = 0.0
    w.dbx = Mock()
    w.dbx.poll.return_value = None
    w.log = lambda msg: None
    w.session = Path(session)
    w.pauses_path = Path(session) / "pauses.jsonl"
    probes = [0]

    def probe():
        probes[0] += 1
        if probes[0] > PROBE_LIMIT:
            raise RuntimeError("the pause was read without the loop sleeping")
        return any(lo <= now[0] < hi for lo, hi in paused_spans)
    w.pause_probe = probe
    sends = []
    w.tick = lambda **kw: sends.append((now[0], kw.get("origin", "watcher")))
    keys = Mock()
    keys.error = None
    keys.proc.poll.return_value = None
    events = [{"monotonic_s": t, "event": e, "keysym": k} for t, e, k in arrivals]
    seen = [0]

    def drain():
        out = []
        while seen[0] < len(events) and events[seen[0]]["monotonic_s"] <= now[0]:
            out.append(events[seen[0]])
            seen[0] += 1
        return out
    keys.drain = drain
    return w, sends, keys, probes


def pauses(session):
    return [json.loads(line) for line in (Path(session) / "pauses.jsonl").read_text().splitlines()]


# a key group still open when the pause begins: `a`, then F12+P 20-40 ms later; DOSBox-X shows
# PAUSED at 1.045 (the P press), `x` typed while paused, the Pause key resumes at 10.0, `b` after
MID_BURST = [(1.000, "press", "a"), (1.012, "release", "a"), (1.020, "press", "F12"),
             (1.040, "press", "p"), (1.052, "release", "p"), (1.060, "release", "F12"),
             (5.000, "press", "x"), (5.012, "release", "x"),
             (10.000, "press", "Pause"), (10.012, "release", "Pause"),
             (12.000, "press", "b"), (12.012, "release", "b")]


class PauseLoopTests(unittest.TestCase):
    def test_a_pause_mid_burst_sends_no_request_while_paused_and_loses_no_key(self):
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [(1.045, 10.005)], MID_BURST)
            w.run(quit_after=15, keys=keys)
            # the opening tick, the pause's snapshot right after the resume, b's burst
            self.assertEqual([o for _, o in sends], ["watcher", "resume", "burst"], sends)
            for t, origin in sends:
                self.assertFalse(1.045 <= t < 10.005, (t, origin))
            # no key lost: every key event lies before a request that brackets it, the resume's
            # request after the last key of the pause (the Pause key's release), b's after b
            resume_t = sends[1][0]
            self.assertGreaterEqual(resume_t, 10.012 + rec.EVENT_SETTLE_S - 1e-9)
            self.assertLess(resume_t, 12.0)
            self.assertGreaterEqual(sends[2][0], 12.012)
            lines = pauses(folder)
            self.assertEqual([x["event"] for x in lines], ["pause", "resume"])
            self.assertEqual(lines[0]["snapshot"], "after-resume")
            self.assertAlmostEqual(lines[0]["monotonic_s"], 1.045, delta=0.02)
            self.assertAlmostEqual(lines[1]["monotonic_s"], 10.005, delta=0.02)
            self.assertAlmostEqual(lines[1]["paused_s"], 8.96, delta=0.04)

    def test_the_pause_is_read_again_before_every_send(self):
        # PAUSED appears 20 ms after the last key event (DOSBox-X's lag), before the 50 ms settle
        # and long before the next periodic read: only the read before the send can see it
        arrivals = [(1.000, "press", "a"), (1.012, "release", "a")]
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [(1.032, 9.0)], arrivals)
            w.run(quit_after=12, keys=keys)
            for t, origin in sends:
                self.assertFalse(1.032 <= t < 9.0, (t, origin))
            self.assertEqual([o for _, o in sends], ["watcher", "resume"], sends)

    def test_a_pause_skips_its_cadence_ticks_and_the_loop_sleeps_while_paused(self):
        # a pause across the 20 s tick and no keys: no request until the pause ends, then the
        # pause's one snapshot, and the next cadence tick at 40 s, not a stale one at once
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, probes = loop_watcher(folder, [(15.0, 25.0)], [])
            w.run(quit_after=45, keys=keys)
            self.assertEqual([o for _, o in sends], ["watcher", "resume", "watcher"], sends)
            self.assertAlmostEqual(sends[1][0], 25.0, delta=0.06)
            self.assertAlmostEqual(sends[2][0], 40.0, delta=0.02)
            # the title is read every PAUSE_POLL_S, not on every pass of a loop that never sleeps
            self.assertLess(probes[0], 45 / rec.PAUSE_POLL_S + 50)

    def test_a_watcher_without_a_pause_probe_never_pauses(self):
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [(0.5, 30.0)], [])
            w.pause_probe = None
            w.run(quit_after=21, keys=keys)
            self.assertEqual([o for _, o in sends], ["watcher", "watcher"])
            self.assertFalse((Path(folder) / "pauses.jsonl").exists())


class PauseCaptureTests(unittest.TestCase):
    """A capture whose request a pause followed never sends F12+S again: DOSBox-X dropped any
    request it got while paused (probe_pause log), so a resend after the resume would stage
    post-resume play under the pre-pause request's window."""

    def watcher(self, folder):
        from tests import test_human_record as fixture
        session = Path(folder)
        (session / "snapshots").mkdir()
        live = session / "state.sav"
        live.write_bytes(fixture.tiny_zip(b"vga"))
        clock = fixture.FakeClock()
        sends = []
        w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                        clock=clock, sleep=clock.sleep, xrun=lambda argv: sends.append(argv),
                        alive=lambda: True, log=lambda m: None, writing=lambda: False)
        return w, live, sends

    def test_a_request_a_pause_followed_is_never_sent_again(self):
        with tempfile.TemporaryDirectory() as folder:
            w, live, sends = self.watcher(folder)
            w.pause_epoch = 1                    # a pause began after this request (epoch 0)
            with self.assertRaises(TimeoutError):
                w.capture(rec.file_signature(live), epoch=0)
            self.assertEqual(sends, [])

    def test_no_request_is_sent_again_while_paused(self):
        with tempfile.TemporaryDirectory() as folder:
            w, live, sends = self.watcher(folder)
            w.paused = True
            with self.assertRaises(TimeoutError):
                w.capture(rec.file_signature(live), epoch=0)
            self.assertEqual(sends, [])

    def test_control_an_unpaused_request_is_sent_again(self):
        with tempfile.TemporaryDirectory() as folder:
            w, live, sends = self.watcher(folder)
            with self.assertRaises(TimeoutError):
                w.capture(rec.file_signature(live), epoch=0)
            self.assertGreater(len(sends), 0)


class PauseMapTests(unittest.TestCase):
    def setUp(self):
        from tests import test_human_record  # noqa: F401  (registers extract for keymap)
        import keymap
        self.keymap = keymap

    def states(self):
        def state(request, text):
            return {"entry": {"request_s": request, "sent_s": request, "elapsed_s": request + 0.8},
                    "screen_text": text, "screen_digest": "d", "error": None}
        return [state(0.0, "MENU"), state(40.0, "TEAM")]

    def test_a_paused_span_is_no_time_to_the_quiet_gap_rule(self):
        # `a` at 10.0, a pause from 10.1 to 30.0, `b` at 30.2: 20.2 s apart on the clock, 0.3 s
        # of emulated time — one burst, mapped MENU -> TEAM
        events = [{"monotonic_s": 10.0, "event": "press", "keysym": "a"},
                  {"monotonic_s": 30.2, "event": "press", "keysym": "b"}]
        result = self.keymap.build_map(self.states(), events, 0, pauses=[(10.1, 30.0)])
        self.assertEqual(([r["keys"] for r in result["transitions"]], result["unmapped_keys"]),
                         ([["a", "b"]], 0))
        # control: without the pause they are two bursts in one gap, unmapped
        result = self.keymap.build_map(self.states(), events, 0)
        self.assertEqual((result["transitions"], result["unmapped_keys"]), ([], 2))

    def test_only_the_paused_seconds_are_removed(self):
        # keys 0.9 s apart less a 0.4 s pause between them leave 0.5 s, not more than the quiet:
        # one burst, mapped; 0.95 s apart leave 0.55 s: two bursts in one gap, unmapped
        one = [{"monotonic_s": 10.0, "event": "press", "keysym": "a"},
               {"monotonic_s": 10.9, "event": "press", "keysym": "b"}]
        result = self.keymap.build_map(self.states(), one, 0, pauses=[(10.2, 10.6)])
        self.assertEqual(result["unmapped_keys"], 0)
        two = [dict(one[0]), dict(one[1], monotonic_s=10.95)]
        result = self.keymap.build_map(self.states(), two, 0, pauses=[(10.2, 10.6)])
        self.assertEqual(result["unmapped_keys"], 2)

    def test_pause_spans_pair_each_pause_with_its_resume(self):
        lines = [{"event": "resume", "monotonic_s": 20.0}, {"event": "pause", "monotonic_s": 10.0},
                 {"event": "pause", "monotonic_s": 30.0}]
        self.assertEqual(self.keymap.pause_spans(lines, end=50.0), [(10.0, 20.0), (30.0, 50.0)])

    def test_the_session_map_reads_pauses_jsonl(self):
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            (session / "meta.json").write_text(json.dumps({"monotonic_start_s": 0.0}))
            (session / "keys.jsonl").write_text(
                json.dumps({"monotonic_s": 10.0, "event": "press", "keysym": "a"}) + "\n"
                + json.dumps({"monotonic_s": 30.2, "event": "press", "keysym": "b"}) + "\n")
            (session / "pauses.jsonl").write_text(
                json.dumps({"event": "pause", "monotonic_s": 10.1}) + "\n"
                + json.dumps({"event": "resume", "monotonic_s": 30.0}) + "\n")
            result = self.keymap.read_session(session, states=self.states())
            self.assertEqual(result["unmapped_keys"], 0)


if __name__ == "__main__":
    unittest.main()
