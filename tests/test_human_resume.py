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


def chord(t, n_p=1):
    """F12 held from t with the host's autorepeat (press/release pairs every 25 ms), P pressed
    n_p times 0.1 s apart from t + 0.3, F12 released after."""
    ev = [(t, "press", "F12")]
    for k in range(1, 8):
        ev += [(t + 0.025 * k, "release", "F12"), (t + 0.025 * k + 0.0005, "press", "F12")]
    for k in range(n_p):
        ev += [(t + 0.3 + 0.1 * k, "press", "p"), (t + 0.35 + 0.1 * k, "release", "p")]
    ev.append((t + 0.4 + 0.1 * n_p, "release", "F12"))
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
        k.expect_injected("Pause", clock=lambda: 100.0)
        marks = [k.mark({"event": ev, "keysym": sym}, t).get("by") for ev, sym, t in
                 (("press", "p", 100.1), ("press", "Pause", 100.1), ("release", "Pause", 100.2),
                  ("press", "Pause", 100.3))]
        # the press and its release are the recorder's; any other key, and a third Pause, are not
        self.assertEqual(marks, [None, "recorder", "recorder", None])

    def test_an_injected_key_after_its_window_is_the_owners(self):
        k = self.logger()
        k.expect_injected("Pause", clock=lambda: 100.0)
        self.assertNotIn("by", k.mark({"event": "press", "keysym": "Pause"},
                                      100.0 + rec.INJECT_MARK_S + 0.1))

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
