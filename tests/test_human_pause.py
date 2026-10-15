"""T39b: the recorder's pause (DOSBox-X's own, F12+P; the title says PAUSED) and the key map's
paused spans. Every test runs on a fake clock with no emulator; each fails with its rule removed
(experiments/E015-human-playthrough/mutate_pause.py makes the mutations in place)."""
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock
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
    # (time read, event, keysym[, the X server's time in ms]); the stream is in read order
    events = [dict({"monotonic_s": a[0], "event": a[1], "keysym": a[2]},
                   **({"server_ms": a[3]} if len(a) > 3 else {})) for a in arrivals]
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
            self.assertEqual(w.pause_epoch, 1)    # the captures of earlier requests see the pause
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

    def test_a_cadence_tick_due_soon_after_a_pause_begins_reads_the_pause_first(self):
        # fix #169: since T44 a key group settles 0.25 s (EVENT_SETTLE_S), as long as PAUSE_POLL_S,
        # so the periodic read always precedes a burst's send and the test above no longer needs
        # the read before the send. A cadence tick has no settle: PAUSED appears at 1.03 with no
        # key event, the periodic reads fall at ~1.0 and ~1.25, the tick is due at 1.1; only the
        # read before the send can see the pause
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [(1.03, 9.0)], [])
            w.cadence_s = 1.1
            w.run(quit_after=12, keys=keys)
            for t, origin in sends:
                self.assertFalse(1.03 <= t < 9.0, (t, origin))
            self.assertIn("resume", [o for _, o in sends], sends)

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

    def test_no_request_is_sent_again_while_the_owner_holds_f12(self):
        # Sol's escalation R2 on PR 144: a pending capture's resend waits for the owner's F12
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(rec, "HOST_HOLD_MAX_S", 8.0):
            w, live, sends = self.watcher(folder)
            w.note_host_keys([{"keysym": rec.HOST_KEYSYM, "event": "press", "monotonic_s": w.clock()}])
            sent_at = []
            w.xrun = lambda argv: sent_at.append(w.clock())
            with self.assertRaises(TimeoutError):
                w.capture(rec.file_signature(live), epoch=0)
            self.assertTrue(sent_at, "no resend after the hold's bound")
            self.assertGreaterEqual(min(sent_at), 8.0, sent_at)

    def test_control_an_unpaused_request_is_sent_again(self):
        with tempfile.TemporaryDirectory() as folder:
            w, live, sends = self.watcher(folder)
            with self.assertRaises(TimeoutError):
                w.capture(rec.file_signature(live), epoch=0)
            self.assertGreater(len(sends), 0)


class PostResumeWriteTests(unittest.TestCase):
    """The rehearsal's shape (T39b-scripted-pause-20261011-02.log): a request sent just after the
    P press, which DOSBox-X dropped as it paused; after the resume, the resume request's save is
    the next write on the live savestate, one save past the dropped request's pre-send count —
    a pipeline head would take it as its own. It is post-resume play: refused."""

    def capture(self, epoch, pause_epoch, events_at_pause):
        from tests import test_human_record as fixture
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            (session / "snapshots").mkdir()
            live = session / "state.sav"
            live.write_bytes(fixture.tiny_zip(b"before the pause"))
            pre = rec.file_signature(live)
            count = [53]

            class Watch:
                def activity(self):
                    return False, count[0]
            clock = fixture.FakeClock()
            w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                            clock=clock, sleep=clock.sleep, xrun=lambda argv: None,
                            alive=lambda: True, log=lambda m: None, watch=Watch())
            w.pause_epoch, w._events_at_pause = pause_epoch, events_at_pause
            w._submitted, w._finished = 1, 0
            # the resume request's save: a new file, one save (53 events) later
            tmp = live.with_name("state.tmp")
            tmp.write_bytes(fixture.tiny_zip(b"after the resume"))
            tmp.replace(live)
            count[0] = 106
            return w.capture(pre, pre_events=53, fast=True, epoch=epoch)

    def test_a_write_after_a_later_pause_is_not_the_requests_own(self):
        with self.assertRaises(rec._AttributionLost):
            self.capture(epoch=0, pause_epoch=1, events_at_pause={1: 53})

    def test_a_pause_keeps_the_write_count_it_began_at(self):
        with tempfile.TemporaryDirectory() as folder:
            w = rec.Watcher.__new__(rec.Watcher)
            w.clock, w.t0, w.log = (lambda: 5.0), 0.0, (lambda m: None)
            w.pauses_path = Path(folder) / "pauses.jsonl"
            w.activity = lambda: (False, 77)
            w.pause_probe = lambda: True
            self.assertTrue(w.poll_pause())
            self.assertEqual((w.pause_epoch, w._events_at_pause), (1, {1: 77}))

    def test_a_tick_off_the_pipeline_marks_such_a_request_superseded(self):
        from tests import test_human_record as fixture
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            live = session / "state.sav"
            live.write_bytes(fixture.tiny_zip())
            w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                            xrun=lambda argv: None, alive=lambda: True, log=lambda m: None,
                            writing=lambda: False)

            def lost(*args, **kw):
                raise rec._AttributionLost("a write after a later pause")
            w.capture = lost
            self.assertIsNone(w.tick())
            line = json.loads((session / "requests.jsonl").read_text())
            self.assertEqual((line["seq"], line.get("superseded")), (None, True))

    def test_control_without_a_pause_the_write_is_accepted(self):
        data, _, events, _ = self.capture(epoch=1, pause_epoch=1, events_at_pause={1: 0})
        self.assertEqual(events, 106)


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

    def test_keys_typed_while_paused_join_the_burst_in_emulated_time(self):
        # `x` typed at 20.0, inside the pause (10.1 to 30.0): 0.1 s of emulated time after `a`
        events = [{"monotonic_s": 10.0, "event": "press", "keysym": "a"},
                  {"monotonic_s": 20.0, "event": "press", "keysym": "x"},
                  {"monotonic_s": 30.2, "event": "press", "keysym": "b"}]
        result = self.keymap.build_map(self.states(), events, 0, pauses=[(10.1, 30.0)])
        self.assertEqual(([r["keys"] for r in result["transitions"]], result["unmapped_keys"]),
                         ([["a", "x", "b"]], 0))

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


class PauseKeyTests(unittest.TestCase):
    """The session's mapper file and the title read."""

    def binds(self, text):
        return {line.split(" ", 1)[0]: line for line in text.split("\n") if line.strip()}

    def test_the_session_mapper_binds_f12_p_to_pause_and_keeps_every_other_bind(self):
        default = self.binds(rec.MAPPER_DEFAULT.read_text())
        session = self.binds(rec.mapper_text())
        self.assertEqual(session["hand_pause"], 'hand_pause "key 72 host" "key 19 host" ')
        # F12+P was the screenshot key: it is the pause's alone now
        self.assertEqual([k for k, v in session.items() if '"key 19 host"' in v], ["hand_pause"])
        self.assertEqual(sorted(default), sorted(session))

    def test_the_session_mapper_has_no_host_bind_but_save_and_pause(self):
        """Issue 175: the save is sent as F12+S, and the owner's R inside that window was F12+R
        (hand_reset), a reset of the emulated machine. Fails with hand_reset's bind put back."""
        default = self.binds(rec.MAPPER_DEFAULT.read_text())
        session = self.binds(rec.mapper_text())
        self.assertEqual(sorted(default), sorted(session))     # every event line still there
        hosted = sorted(k for k, v in session.items() if k.startswith("hand_") and " host" in v)
        self.assertEqual(hosted, ["hand_pause", "hand_savestate"])
        self.assertEqual(session["hand_savestate"], default["hand_savestate"])
        for name in ("hand_reset", "hand_loadstate", "hand_reboot", "hand_rawscrshot"):
            self.assertEqual(session[name], name + " ")

    def test_a_default_mapper_that_is_not_the_recorded_one_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            other = Path(folder) / "other.map"
            other.write_text(rec.MAPPER_DEFAULT.read_text().replace("key 22 host", "key 23 host"))
            with self.assertRaises(RuntimeError):
                rec.mapper_text(other)

    def test_a_new_session_writes_the_mapper_its_config_names(self):
        with tempfile.TemporaryDirectory() as folder:
            with mock.patch.object(rec, "SESSIONS", Path(folder)), \
                    mock.patch.object(rec, "verify_release_or_die"), \
                    mock.patch.object(rec, "fetch_saves_or_warn", return_value={"fetched": True}), \
                    mock.patch.object(rec.fetch_saves, "CACHE", Path(folder) / "no-saves"), \
                    mock.patch.object(rec.shutil, "copytree"), \
                    mock.patch.object(rec, "dosbox_version", return_value="2024.03.01"):
                session, meta = rec.new_session()
            self.assertIn(f"mapperfile={session / 'mapper.map'}", meta["config"])
            self.assertEqual((session / "mapper.map").read_text(), rec.mapper_text())
            self.assertEqual(meta["mapper_sha256"], rec.sha256(rec.mapper_text().encode()))

    def test_the_pause_is_the_title_dosbox_x_shows(self):
        def name(text, code=0):
            return lambda args, env=None, **kw: types.SimpleNamespace(returncode=code, stdout=text)
        with mock.patch.object(rec, "xdotool", name("DOSBox-X 2024.03.01: GOAL - 3000 cycles/ms PAUSED\n")):
            self.assertTrue(rec.window_paused("7", {}))
        with mock.patch.object(rec, "xdotool", name("DOSBox-X 2024.03.01: GOAL - 3000 cycles/ms\n")):
            self.assertFalse(rec.window_paused("7", {}))
        with mock.patch.object(rec, "xdotool", name("", 1)):
            self.assertIsNone(rec.window_paused("7", {}))


if __name__ == "__main__":
    unittest.main()
