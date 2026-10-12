"""T39b Scope 5-8 (Done-when 4): F12+P while paused resumes through the recorder's own Pause key,
marked as the recorder's; a resume with no logged key is still logged; a closed window still ends
the sitting with `ended` and `stop_reason`; --load and the default copy place the saved game.
Each test fails with its rule removed (experiments/E015-human-playthrough/mutate_pause.py)."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("human_recorder_resume", ROOT / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))
sys.path.insert(0, str(ROOT / "tests"))
from test_human_pause import loop_watcher, pauses  # noqa: E402


def ms(t):
    return int(round(t * 1000))


def chord(t, n_p=1):
    """F12 held from t with the host's autorepeat (release/press pairs every 25 ms, one server
    time each pair), P pressed n_p times 0.1 s apart from t + 0.3, F12 released after; read with
    no delay (the read time is the server time)."""
    ev = [(t, "press", "F12", ms(t))]
    for k in range(1, 8):
        a = t + 0.025 * k
        ev += [(a, "release", "F12", ms(a)), (a + 0.0005, "press", "F12", ms(a))]
    for k in range(n_p):
        a, b = t + 0.3 + 0.1 * k, t + 0.35 + 0.1 * k
        ev += [(a, "press", "p", ms(a)), (b, "release", "p", ms(b))]
    ev.append((t + 0.4 + 0.1 * n_p, "release", "F12", ms(t + 0.4 + 0.1 * n_p)))
    return ev


class ResumeChordTests(unittest.TestCase):
    def sitting(self, folder, arrivals, pause_at, quit_after=12, resume_lag=0.15):
        """A loop on a fake clock whose title says PAUSED from `pause_at` until the recorder's own
        Pause key (resume_key) or forever."""
        spans = [[pause_at, float("inf")]]
        w, sends, keys, _ = loop_watcher(folder, spans, sorted(arrivals))
        pressed = []

        def resume_key():
            pressed.append(w.clock())
            # DOSBox-X ends the pause `resume_lag` later: the second P (0.1 s after the first)
            # still finds it paused, and must not press Pause again
            spans[0][1] = w.clock() + resume_lag
        w.resume_key = resume_key
        w.run(quit_after=quit_after, keys=keys)
        return w, sends, pressed

    def test_f12_p_while_paused_resumes_once_and_the_pausing_chord_does_not(self):
        with tempfile.TemporaryDirectory() as folder:
            # the pausing chord: its P at 1.3 is when DOSBox-X shows PAUSED (the same instant);
            # a P without F12 at 3.0; then F12 held with P twice at 5.3 and 5.4
            arrivals = chord(1.0) + [(3.0, "press", "p"), (3.05, "release", "p")] + chord(5.0, 2)
            w, sends, pressed = self.sitting(folder, arrivals, pause_at=1.3)
            self.assertEqual(len(pressed), 1, pressed)
            self.assertAlmostEqual(pressed[0], 5.3, delta=0.02)
            lines = pauses(folder)
            self.assertEqual([x["event"] for x in lines], ["pause", "resume"])
            self.assertEqual(lines[1].get("by"), "recorder (F12+P)")
            self.assertIn("resume", [o for _, o in sends])

    def test_the_held_pausing_p_repeating_never_resumes(self):
        # rework round 1, R4 (Sol): F12 down 1.0, P down 1.3 (DOSBox-X pauses), the held P
        # repeats at 1.9 with no release (and as a host release/press pair at 2.2), P up 2.5,
        # F12 up 2.6: no Pause; a fresh F12+P at 4.0 resumes (the control)
        arrivals = [(1.0, "press", "F12", 1000), (1.3, "press", "p", 1300),
                    (1.9, "press", "p", 1900), (2.2, "release", "p", 2200),
                    (2.2003, "press", "p", 2200), (2.5, "release", "p", 2500),
                    (2.6, "release", "F12", 2600)] + chord(4.0)
        with tempfile.TemporaryDirectory() as folder:
            w, sends, pressed = self.sitting(folder, arrivals, pause_at=1.3)
            self.assertEqual(len(pressed), 1, pressed)
            self.assertAlmostEqual(pressed[0], 4.3, delta=0.02)

    def test_each_pause_is_started_by_one_chord_and_ended_by_the_next(self):
        # two pause cycles: F12+P pauses (1.3, 6.3), F12+P resumes (3.3, 8.3); after a resume the
        # next chord pauses again and must not press Pause
        spans = [[1.3, float("inf")]]
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, spans,
                                             sorted(chord(1.0) + chord(3.0) + chord(6.0) + chord(8.0)))
            pressed = []

            def resume_key():
                pressed.append(w.clock())
                spans[-1][1] = w.clock() + 0.15
                if len(spans) == 1:
                    spans.append([6.3, float("inf")])
            w.resume_key = resume_key
            w.run(quit_after=10, keys=keys)
            self.assertEqual([round(t, 1) for t in pressed], [3.3, 8.3])
            self.assertEqual([x["event"] for x in pauses(folder)], ["pause", "resume"] * 2)

    def test_no_save_request_while_the_owner_holds_f12(self):
        # rework round 2 (the DW3 rehearsal T39b-scripted-pause-20261012-01.log): a request sent
        # between the owner's F12 and P breaks the chord; none goes out while F12 is held
        arrivals = [(1.0, "press", "F12", 1000), (1.13, "press", "p", 1130),
                    (1.25, "release", "p", 1250), (1.5, "release", "F12", 1500)]
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [], arrivals)
            w.run(quit_after=3, keys=keys)
            times = [t for t, o in sends if o == "burst"]
            self.assertTrue(times and all(t >= 1.5 for t in times), sends)

    def test_a_split_f12_autorepeat_pair_keeps_the_hold(self):
        # Sol's escalation R1 on PR 144: F12 down at 1.0 and held to 2.0; an autorepeat pair at
        # server 1600 is read apart, its release at 1.6 and its press at 1.7: no request between
        with tempfile.TemporaryDirectory() as folder:
            arrivals = [(1.0, "press", "F12", 1000), (1.6, "release", "F12", 1600),
                        (1.7, "press", "F12", 1600), (2.0, "release", "F12", 2000)]
            w, sends, keys, _ = loop_watcher(folder, [], arrivals)
            w.run(quit_after=4, keys=keys)
            times = [t for t, o in sends if o == "burst"]
            self.assertTrue(times and all(t >= 2.0 for t in times), sends)

    def test_a_held_f12_with_no_events_holds_requests_only_for_a_bound(self):
        # a missed F12 release must not stop the snapshots: requests resume HOST_HOLD_MAX_S after
        # the last F12 event
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [], [(1.0, "press", "F12", 1000)])
            w.run(quit_after=6, keys=keys)
            times = [t for t, o in sends if o == "burst"]
            self.assertEqual(len(times), 1, sends)
            self.assertAlmostEqual(times[0], 1.0 + rec.HOST_HOLD_MAX_S, delta=0.05)

    def test_a_late_delivered_pausing_p_never_resumes(self):
        # rework round 2, R1 (Sol): F12 at 1.0, the title shows PAUSED at 1.3, the P that paused
        # it is delivered at 1.9 (pressed at 1.3 on the server's clock): it is the pausing chord,
        # not a resume; a fresh F12+P at 4.0 resumes (the control)
        arrivals = [(1.0, "press", "F12", 1000), (1.9, "press", "p", 1300),
                    (1.95, "release", "p", 1350), (2.0, "release", "F12", 1400)] + chord(4.0)
        with tempfile.TemporaryDirectory() as folder:
            w, sends, pressed = self.sitting(folder, arrivals, pause_at=1.3)
            self.assertEqual(len(pressed), 1, pressed)
            self.assertAlmostEqual(pressed[0], 4.3, delta=0.02)

    def test_a_held_ps_repeat_pair_read_30_ms_apart_never_resumes(self):
        # rework round 2, R2 (Sol): F12 and P held while paused; the logger's reader stalls 30 ms
        # between a repeat pair's release and press (KeyLogger.pump on a raw stream): their
        # server times are one, so no fresh press and no Pause
        with tempfile.TemporaryDirectory() as folder:
            k = rec.KeyLogger({"DISPLAY": ":601"}, ":0", Path(folder) / "keys.jsonl")

            def stream():
                for kind, code, t in (("Press", 96, 1000), ("Press", 33, 1300)):
                    yield from (f"EVENT type 13 (Raw{'Key' + kind})\n", f"    time:   {t}\n",
                                f"    detail: {code}\n")
                yield from ("EVENT type 14 (RawKeyRelease)\n", "    time:   1800\n",
                            "    detail: 33\n")
                time.sleep(0.03)                       # the reader stalls inside the pair
                yield from ("EVENT type 13 (RawKeyPress)\n", "    time:   1800\n",
                            "    detail: 33\n")
            k.proc = types.SimpleNamespace(stdout=stream())
            k.pump(rec.KeyParser({96: "F12", 33: "p"}))
            logged = [json.loads(x) for x in (Path(folder) / "keys.jsonl").read_text().splitlines()]
            self.assertGreaterEqual(logged[3]["monotonic_s"] - logged[2]["monotonic_s"], 0.025)
            w = rec.Watcher.__new__(rec.Watcher)
            pressed = []
            w.clock, w.log, w.resume_key = time.monotonic, (lambda m: None), (lambda: pressed.append(1))
            w.paused = False
            w.resume_chord(logged[:2])                 # F12+P: the chord that pauses
            w.paused = True                            # the title shows the pause, read
            w._pause_since = logged[1]["monotonic_s"]  # right after the pausing P was
            w.resume_chord(logged[2:])                 # the held P's repeat pair
            self.assertEqual(pressed, [])

    def test_an_unreadable_title_holds_every_send(self):
        # rework round 1, R3 (Sol): paused [0, 3), the title unreadable [0, 1): "unknown" is not
        # "running"; no request until the resume at 3.0 is read
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [], [])
            reads = [0]

            def probe():
                reads[0] += 1
                if reads[0] > 5000:
                    raise RuntimeError("the pause was read without the loop sleeping")
                return None if w.clock() < 1.0 else w.clock() < 3.0
            w.pause_probe = probe
            w.run(quit_after=5, keys=keys)
            self.assertTrue(sends and all(t >= 3.0 for t, _ in sends), sends)
            self.assertEqual([x["event"] for x in pauses(folder)], ["pause", "resume"])

    def test_a_resume_with_no_logged_key_is_logged_within_the_poll_bound(self):
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [(2.0, 10.0)], [])
            w.run(quit_after=12, keys=keys)
            lines = pauses(folder)
            self.assertEqual([x["event"] for x in lines], ["pause", "resume"])
            self.assertLessEqual(lines[1]["monotonic_s"] - 10.0, rec.PAUSE_POLL_S + 0.011)
            self.assertNotIn("by", lines[1])

    def test_an_unanswered_title_read_is_unknown_not_a_crash(self):
        def hang(args, env=None, timeout=10):
            raise subprocess.TimeoutExpired(args, timeout)
        with mock.patch.object(rec, "xdotool", hang):
            self.assertIsNone(rec.window_paused("7", {}))


class InjectedKeyTests(unittest.TestCase):
    def logger(self):
        k = rec.KeyLogger.__new__(rec.KeyLogger)
        k.expected, k.lock = {}, __import__("threading").Lock()
        return k

    def test_the_injected_pause_is_marked_as_the_recorders(self):
        k = self.logger()
        k.expect_injected("Pause")
        now = time.monotonic()
        marks = [k.mark({"event": ev, "keysym": sym}, t).get("by") for ev, sym, t in
                 (("press", "p", now), ("press", "Pause", now), ("release", "Pause", now),
                  ("press", "Pause", now))]
        # the press and its release are the recorder's; any other key, and a third Pause, are not
        self.assertEqual(marks, [None, "recorder", "recorder", None])

    def test_two_injections_before_the_logger_catches_up_are_both_marked(self):
        # R1: with the logger behind, a second Pause injected before the first is delivered owes
        # its own press and release
        k = self.logger()
        k.expect_injected("Pause")
        k.expect_injected("Pause")
        marks = [k.mark({"event": ev, "keysym": "Pause"}).get("by")
                 for ev in ("press", "release", "press", "release", "press")]
        self.assertEqual(marks, ["recorder"] * 4 + [None])

    def test_a_delayed_logger_still_marks_the_injected_key(self):
        # rework round 1, R1 (Sol): the logger delivers the injected Pause 2.3 s late (xinput
        # stopped and continued); a known injection stays the recorder's
        with tempfile.TemporaryDirectory() as folder:
            k = rec.KeyLogger({"DISPLAY": ":601"}, ":0", Path(folder) / "keys.jsonl")
            started = []

            def late_lines():
                started.append(time.monotonic())
                time.sleep(2.3)
                yield from ("EVENT type 13 (RawKeyPress)\n", "    detail: 110\n",
                            "EVENT type 14 (RawKeyRelease)\n", "    detail: 110\n")
            k.proc = types.SimpleNamespace(stdout=late_lines())
            k.expect_injected("Pause")
            k.pump(rec.KeyParser({110: "Pause"}))
            logged = [json.loads(x) for x in (Path(folder) / "keys.jsonl").read_text().splitlines()]
            self.assertEqual([(e["event"], e.get("by")) for e in logged],
                             [("press", "recorder"), ("release", "recorder")])
            self.assertGreater(logged[0]["monotonic_s"] - started[0], 2.2)

    def test_inject_pause_key_focuses_the_window_then_presses_pause_down_and_up(self):
        calls, expected = [], []
        keys = types.SimpleNamespace(expect_injected=lambda sym: expected.append((sym, len(calls))))
        with mock.patch.object(rec, "xdotool", lambda args, env=None, **kw: (
                calls.append(args), types.SimpleNamespace(returncode=0))[1]):
            self.assertTrue(rec.inject_pause_key("77", {"DISPLAY": ":600"}, keys, sleep=lambda s: None))
        self.assertEqual(calls, [["windowfocus", "77"], ["keydown", "Pause"], ["keyup", "Pause"]])
        self.assertEqual(expected, [("Pause", 0)])     # marked before the first key goes out

    def test_the_recorders_keys_are_no_owner_press_and_no_burst(self):
        import keymap
        states = [{"entry": {"request_s": r, "sent_s": r, "elapsed_s": r + 0.8},
                   "screen_text": t, "screen_digest": "d", "error": None}
                  for r, t in ((0.0, "A"), (9.0, "B"))]
        events = [{"monotonic_s": 5.0, "event": "press", "keysym": "Pause", "by": "recorder"},
                  {"monotonic_s": 5.05, "event": "release", "keysym": "Pause", "by": "recorder"},
                  {"monotonic_s": 6.0, "event": "press", "keysym": "Return"}]
        result = keymap.build_map(states, events, 0)
        self.assertEqual((result["summary"], [r["keys"] for r in result["transitions"]]),
                         ("screens: 2, transitions: 1, keys: 1", [["Return"]]))
        with tempfile.TemporaryDirectory() as folder:
            arrivals = [(5.0, "press", "Pause"), (5.05, "release", "Pause")]
            w, sends, keys, _ = loop_watcher(folder, [], arrivals)
            drain = keys.drain
            keys.drain = lambda: [dict(e, by="recorder") for e in drain()]
            w.run(quit_after=8, keys=keys)
            self.assertEqual([o for _, o in sends], ["watcher"])


class CleanEndTests(unittest.TestCase):
    def test_a_dead_key_logger_ends_the_loop_without_raising(self):
        with tempfile.TemporaryDirectory() as folder:
            w, sends, keys, _ = loop_watcher(folder, [], [])
            keys.proc.poll.return_value = 1          # the logger's display (Xephyr) is gone
            w.run(quit_after=5, keys=keys)
            self.assertTrue(w.stop_cause.startswith("key logger stopped"))

    def play(self, folder, run):
        """play() with every process faked: the sitting's Watcher.run is `run`."""
        session = Path(folder) / "s"

        def new_session(load=None, fresh=False):
            session.mkdir()
            meta = {"ended": None, "stop_reason": None, "load": {"fresh": True, "file": None}}
            (session / "meta.json").write_text(json.dumps(meta))
            return session, meta

        class FakeWatcher:
            problems, stop_cause, t0 = [], None, 0.0

            def __init__(self, *a, **kw):
                pass

            def run(self, **kw):
                return run(self)

            def shutdown_stage(self, sha):
                return None

            def activity(self):
                return False, 0

        class FakeKeys:
            def __init__(self, env, outer, path):
                Path(path).write_text("")

            def start(self):
                pass

            def stop(self):
                pass
        dbx = mock.Mock()
        dbx.poll.return_value = 0                       # DOSBox-X has exited: the window closed
        dbx.pid, dbx.returncode = 4242, 0
        with mock.patch.dict(os.environ, {"DISPLAY": ":0"}), \
                mock.patch.object(rec.driver, "require_dosbox", return_value="dosbox-x"), \
                mock.patch.object(rec, "new_session", new_session), \
                mock.patch.object(rec, "start_nested", return_value=(
                    types.SimpleNamespace(pid=4343), {"DISPLAY": ":601"}, "9")), \
                mock.patch.object(rec, "KeyLogger", FakeKeys), \
                mock.patch.object(rec, "WriteWatch", lambda p: mock.Mock()), \
                mock.patch.object(rec.subprocess, "Popen", return_value=dbx), \
                mock.patch.object(rec, "find_window", return_value="1"), \
                mock.patch.object(rec, "Watcher", FakeWatcher), \
                mock.patch.object(rec, "terminate"), \
                mock.patch.object(rec.signal, "signal"), \
                mock.patch("builtins.print"):
            try:
                rec.play()
            except RuntimeError:
                pass
        return json.loads((session / "meta.json").read_text())

    def test_a_closed_window_writes_ended_and_stop_reason(self):
        # the recorder's own loop, on a fake clock, whose key logger dies as Xephyr goes (the
        # owner closed the window; sitting 20261011-215411's end)
        def closed(fake):
            with tempfile.TemporaryDirectory() as folder:
                w, sends, keys, _ = loop_watcher(folder, [], [])
                keys.proc.poll.return_value = 1
                out = w.run(quit_after=5, keys=keys)
                fake.stop_cause = w.stop_cause
                return out
        with tempfile.TemporaryDirectory() as folder:
            meta = self.play(folder, closed)
            self.assertIsNotNone(meta["ended"])
            self.assertEqual(meta["stop_reason"], "window-closed")

    def test_an_error_still_writes_ended_and_its_cause(self):
        def broken(w):
            raise RuntimeError("something broke")
        with tempfile.TemporaryDirectory() as folder:
            meta = self.play(folder, broken)
            self.assertIsNotNone(meta["ended"])
            self.assertIn("something broke", meta["stop_reason"])


class RehearsalGuardTests(unittest.TestCase):
    def test_a_later_pauses_resume_snapshot_never_counts_for_an_earlier_pause(self):
        # rework round 1, R5 (Sol): pause 1 [10, 15) has no resume snapshot; pause 2 [20, 25)'s,
        # at 25.05, must not be credited to pause 1
        import scripted_pause
        spans = [(10.0, 15.0), (20.0, 25.0)]
        index = [{"origin": "watcher", "request_s": 0.0}, {"origin": "resume", "request_s": 25.05}]
        self.assertEqual(scripted_pause.missing_resume_snapshots(spans, index, 0.0), [(10.0, 15.0)])
        index.append({"origin": "resume", "request_s": 15.05})
        self.assertEqual(scripted_pause.missing_resume_snapshots(spans, index, 0.0), [])


class SavedGameTests(unittest.TestCase):
    def sessions(self, folder):
        base = Path(folder)
        for name, data, age in (("20261011-100000", b"old save", 200), ("20261011-110000", b"new save", 100)):
            g = base / name / "game"
            g.mkdir(parents=True)
            (g / "1.GL").write_bytes(data)
            t = time.time() - age
            os.utime(g / "1.GL", (t, t))
        new = base / "20261011-120000"
        (new / "game").mkdir(parents=True)
        return base, new

    def test_the_default_copies_the_newest_gl_and_records_its_sha256(self):
        with tempfile.TemporaryDirectory() as folder:
            base, new = self.sessions(folder)
            load = rec.place_saved_game(new)
            self.assertEqual((new / "game" / "1.GL").read_bytes(), b"new save")
            self.assertEqual((load["file"], load["sha256"], load["bytes"]),
                             ("game/1.GL", rec.sha256(b"new save"), 8))
            self.assertIn("20261011-110000", load["source"])

    def test_load_copies_the_named_file(self):
        with tempfile.TemporaryDirectory() as folder:
            base, new = self.sessions(folder)
            load = rec.place_saved_game(new, load=base / "20261011-100000" / "game" / "1.GL")
            self.assertEqual((new / "game" / "1.GL").read_bytes(), b"old save")
            self.assertEqual((load["sha256"], load["chosen"]), (rec.sha256(b"old save"), "--load"))

    def test_fresh_copies_none(self):
        with tempfile.TemporaryDirectory() as folder:
            base, new = self.sessions(folder)
            self.assertEqual(rec.place_saved_game(new, fresh=True), {"fresh": True, "file": None})
            self.assertFalse((new / "game" / "1.GL").exists())

    def test_a_new_session_records_the_copy_in_meta(self):
        with tempfile.TemporaryDirectory() as folder:
            base, new = self.sessions(folder)
            with mock.patch.object(rec, "SESSIONS", base), \
                    mock.patch.object(rec, "verify_release_or_die"), \
                    mock.patch.object(rec.shutil, "copytree", lambda src, dst: Path(dst).mkdir()), \
                    mock.patch.object(rec, "dosbox_version", return_value="2024.03.01"):
                session, meta = rec.new_session()
            self.assertEqual(meta["load"]["sha256"], rec.sha256(b"new save"))
            self.assertEqual(json.loads((session / "meta.json").read_text())["load"]["file"], "game/1.GL")
            self.assertEqual((session / "game" / "1.GL").read_bytes(), b"new save")

    def test_play_sh_with_no_subcommand_plays(self):
        with mock.patch.object(rec, "play", return_value=0) as play:
            self.assertEqual(rec.main([]), 0)
            self.assertEqual(rec.main(["--fresh"]), 0)
        self.assertEqual([c.kwargs.get("fresh") for c in play.call_args_list], [False, True])


if __name__ == "__main__":
    unittest.main()
