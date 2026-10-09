"""T34 nested-display recorder tests: the private display, the key logger's privacy, the burst
snapshot, the Xephyr window bind and video, and the screen/key map's rules."""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("human_recorder", ROOT / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))


def xvfb(first, last, size="1280x800x24"):
    """A private Xvfb standing in for the owner's desktop: the first number in [first, last) whose
    server stays up (try-start: on this host the sockets are abstract, so nothing is inspected)."""
    for number in range(first, last):
        proc = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", size],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
        time.sleep(1)
        if proc.poll() is None:
            return proc, dict(os.environ, DISPLAY=f":{number}")
    raise RuntimeError(f"no free display in {first}..{last - 1}")


def xev(env, name, stdout=subprocess.DEVNULL):
    """An ordinary application window on `env`'s display; returns (process, window id). `stdout`
    is where xev's own KeyPress log goes — an open file when a caller wants to read what the
    foreign application actually received (R1's positive control)."""
    proc = subprocess.Popen(["xev", "-name", name], env=env, stdout=stdout,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    end = time.monotonic() + 10
    while time.monotonic() < end:
        out = subprocess.run(["xdotool", "search", "--name", f"^{name}$"], env=env,
                             capture_output=True, text=True).stdout.split()
        if out:
            return proc, out[0]
        time.sleep(0.1)
    raise RuntimeError(f"no {name} window")


def logged(path):
    return [(e["event"], e["keysym"]) for e in
            (json.loads(line) for line in Path(path).read_text().splitlines())]


class NestedDisplayTests(unittest.TestCase):
    def test_try_start_skips_busy_number_and_changes_only_child_display(self):
        busy, free = Mock(), Mock()
        busy.poll.return_value = 1
        free.poll.return_value = None
        env = {"DISPLAY": ":612", "OTHER": "kept"}
        found = []

        def find(outer, title):
            found.append((outer, title))
            return "77"
        with patch.object(rec.subprocess, "Popen", side_effect=[busy, free]) as launch:
            proc, nested, wid = rec.start_nested(env, "800x600", None, title="t-1", find=find,
                                                 sleep=lambda s: None)
        self.assertIs(proc, free)
        self.assertEqual(wid, "77")
        self.assertEqual(env["DISPLAY"], ":612")
        self.assertEqual(nested, {"DISPLAY": ":601", "OTHER": "kept"})
        self.assertEqual(launch.call_args_list[0].args[0],
                         ["Xephyr", ":600", "-screen", "800x600", "-nolisten", "tcp", "-title", "t-1"])
        self.assertEqual(launch.call_args_list[1].kwargs["env"], env)
        self.assertEqual(found, [(env, "t-1")])        # the busy one is never searched

    def test_a_live_xephyr_without_its_titled_window_is_never_accepted(self):
        # R4/R6 class: a candidate is accepted on positive proof (its own window), not on a guess
        alive = Mock()
        alive.poll.return_value = None
        now = [0.0]
        with patch.object(rec.subprocess, "Popen", return_value=alive), \
                patch.object(rec, "terminate") as term:
            with self.assertRaises(RuntimeError):
                rec.start_nested({"DISPLAY": ":612"}, "800x600", None, title="t-2",
                                 find=lambda outer, title: None, clock=lambda: now[0],
                                 sleep=lambda s: now.__setitem__(0, now[0] + s))
        term.assert_called_once_with(alive)
        self.assertAlmostEqual(now[0], 10.0, delta=0.06)   # NESTED_START_S, the [designed] bound

    def test_the_xephyr_window_is_the_unique_exact_title(self):
        names = {"1": "t-3 and more", "2": "other", "3": "t-3", "4": "t-3"}

        def fake(args, env=None, timeout=10):
            out = " ".join(names) if args[0] == "search" else names[args[1]] + "\n"
            return Mock(stdout=out, returncode=0)
        with patch.object(rec, "xdotool", side_effect=fake):
            self.assertIsNone(rec.find_xephyr_window({}, "t-3"))       # two exact: refused
            del names["4"]
            self.assertEqual(rec.find_xephyr_window({}, "t-3"), "3")
            self.assertIsNone(rec.find_xephyr_window({}, "t-9"))

    def test_self_test_requires_nested_tools(self):
        with patch.object(rec, "ensure_cache", return_value="fixture"), patch.object(rec, "dosbox_version", return_value="2024.03.01"), patch.object(rec.shutil, "which", side_effect=lambda name: None if name in ("Xephyr", "xinput") else name):
            self.assertEqual(rec.self_test(), 1)

    def test_start_nested_binds_the_real_xephyr_window(self):
        # the R4 failure: the old pid search never matched Xephyr's window (no _NET_WM_PID)
        outer, env = xvfb(770, 780)
        nested = other = None
        try:
            other, _ = xev(env, "Xephyr")       # a foreign window named like Xephyr
            nested, child, wid = rec.start_nested(env, "640x400", subprocess.DEVNULL)
            name = subprocess.run(["xdotool", "getwindowname", wid], env=env,
                                  capture_output=True, text=True).stdout.strip()
            self.assertTrue(name.startswith("goal2-recorder-"), name)
            self.assertEqual(rec.window_geometry(wid, env)[2:], (640, 400))
            self.assertNotEqual(child["DISPLAY"], env["DISPLAY"])
        finally:
            for proc in (other, nested, outer):
                rec.terminate(proc)


class KeyTests(unittest.TestCase):
    def test_logger_rejects_outer_display(self):
        with self.assertRaises(ValueError):
            rec.KeyLogger({"DISPLAY": ":612"}, ":612", Path("unused"))

    def test_raw_events_only_and_key_fields(self):
        parser = rec.KeyParser({38: "a"})
        self.assertIsNone(parser.line("EVENT type 2 (KeyPress)"))
        self.assertIsNone(parser.line("    detail: 38"))
        self.assertIsNone(parser.line("EVENT type 13 (RawKeyPress)"))
        self.assertEqual(parser.line("    detail: 38"), {"event": "press", "keycode": 38, "keysym": "a"})
        parser.line("EVENT type 14 (RawKeyRelease)")
        self.assertEqual(parser.line("    detail: 38"), {"event": "release", "keycode": 38, "keysym": "a"})

    def test_burst_waits_for_quiet_and_only_consumes_once(self):
        burst = rec.Burst()
        burst.add({"monotonic_s": 10.0})
        burst.add({"monotonic_s": 10.2})
        self.assertFalse(burst.due(10.699))
        self.assertTrue(burst.due(10.7))
        burst.consume()
        self.assertFalse(burst.due(12.0))
        burst.add({"monotonic_s": 12.1})
        self.assertTrue(burst.due(12.6))

    def test_burst_preserves_group_boundaries_across_drains(self):
        # R2: keys >= BURST_QUIET_S apart are separate groups, even when they arrive in one drain
        # (while a burst snapshot's capture blocked the loop). The overwriting Burst.last merged
        # them into one; the queue keeps each its own, so each becomes its own snapshot.
        burst = rec.Burst()
        burst.add({"monotonic_s": 0.0})
        burst.add({"monotonic_s": 0.51})   # 0.51 > quiet 0.5: a new group
        burst.add({"monotonic_s": 1.02})   # 1.02 >= 0.51 + 0.5: a new group
        self.assertTrue(burst.due(0.5))    # group 0 due at 0.0 + 0.5
        burst.consume()
        self.assertTrue(burst.due(1.01))   # group 1 due at 0.51 + 0.5
        burst.consume()
        self.assertTrue(burst.due(1.52))   # group 2 due at 1.02 + 0.5
        burst.consume()
        self.assertFalse(burst.due(2.0))

    def test_loop_takes_burst_snapshot_between_cadence_ticks(self):
        now = [0.0]
        watcher = rec.Watcher.__new__(rec.Watcher)
        watcher.clock = lambda: now[0]
        watcher.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
        watcher.t0 = 0
        watcher.dbx = Mock()
        watcher.dbx.poll.return_value = None
        watcher.log = lambda msg: None
        ticks = []
        watcher.tick = lambda **kw: ticks.append((now[0], kw.get("origin", "watcher")))
        keys = Mock()
        keys.error = None
        keys.proc.poll.return_value = None
        sent = [False]
        def drain():
            if now[0] >= 1 and not sent[0]:
                sent[0] = True
                return [{"monotonic_s": 1.0}]
            return []
        keys.drain = drain
        watcher.run(quit_after=2, keys=keys)
        self.assertEqual(len(ticks), 2)
        self.assertEqual(ticks[0], (0.0, "watcher"))
        self.assertAlmostEqual(ticks[1][0], 1.5)
        self.assertEqual(ticks[1][1], "burst")

    def test_human_paced_keys_produce_one_burst_snapshot_each(self):
        # R2 end-to-end at the requested 0.5-1.5 s human pace: 10 single-key groups 0.51 s apart
        # (above the 0.5 s quiet) must produce 10 burst snapshots, not the 4 the overwriting
        # Burst.last produced. Each tick (save + capture) advances the clock 0.75 s, longer than
        # the 0.51 s gap, so keys keep arriving while a burst snapshot is being captured — the
        # exact condition that merged groups before.
        now = [0.0]
        watcher = rec.Watcher.__new__(rec.Watcher)
        watcher.clock = lambda: now[0]
        watcher.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
        watcher.t0 = 0.0
        watcher.dbx = Mock()
        watcher.dbx.poll.return_value = None
        watcher.log = lambda msg: None
        ticks = []

        def tick(**kw):
            ticks.append((now[0], kw.get("origin", "watcher")))
            now[0] += 0.75      # the save + staging capture latency
        watcher.tick = tick
        keys = Mock()
        keys.error = None
        keys.proc.poll.return_value = None
        arrivals = [1.0 + 0.51 * k for k in range(10)]
        sent = [0]

        def drain():
            out = []
            while sent[0] < len(arrivals) and arrivals[sent[0]] <= now[0]:
                out.append({"monotonic_s": arrivals[sent[0]], "keysym": f"k{sent[0]}"})
                sent[0] += 1
            return out
        keys.drain = drain
        watcher.run(quit_after=30, keys=keys)
        bursts = [t for t in ticks if t[1] == "burst"]
        self.assertEqual(len(bursts), 10, bursts)

    def test_private_display_logs_game_keys_not_outer_app_keys(self):
        outer, env = xvfb(710, 730, "800x600x24")
        nested = app = logger = None
        with tempfile.TemporaryDirectory() as folder:
            try:
                nested, child, xephyr_wid = rec.start_nested(env, "640x400", subprocess.DEVNULL)
                xev_log = Path(folder) / "xev-other-app.log"
                with open(xev_log, "w") as xev_out:
                    app, wid = xev(env, "T34-other-app", stdout=xev_out)
                logger = rec.KeyLogger(child, env["DISPLAY"], Path(folder) / "keys.jsonl")
                logger.start()
                time.sleep(1)
                subprocess.run(["xdotool", "key", "a", "b"], env=child, check=True)
                # XSendEvent to another application's window (DW1's send) ...
                subprocess.run(["xdotool", "key", "--window", wid, "x"], env=env, check=True)
                # ... and real XTEST input to it while it holds the outer focus (R3: XSendEvent
                # makes no raw XI2 events, so only this can catch a logger on the outer display)
                subprocess.run(["xdotool", "windowfocus", "--sync", wid], env=env, check=True)
                subprocess.run(["xdotool", "key", "y", "z"], env=env, check=True)
                # the hazard's other half: outer keys while Xephyr holds the focus ARE game input
                subprocess.run(["xdotool", "windowfocus", "--sync", xephyr_wid], env=env, check=True)
                subprocess.run(["xdotool", "key", "c"], env=env, check=True)
                time.sleep(0.5)
                logger.stop()
                events = [json.loads(line) for line in (Path(folder) / "keys.jsonl").read_text().splitlines()]
                self.assertEqual([(e["event"], e["keysym"]) for e in events],
                                 [("press", "a"), ("release", "a"), ("press", "b"), ("release", "b"),
                                  ("press", "c"), ("release", "c")])
                for e in events:
                    self.assertIsInstance(e["monotonic_s"], float)
                    self.assertIn("+00:00", e["utc"])
                    self.assertIsInstance(e["keycode"], int)
                # R1 positive control: the foreign application really received x/y/z (the focused
                # XTEST keys are what a logger on the outer display would have leaked; the XSendEvent
                # `x` and both real XTEST keys must all be in xev's own log). Removing the focused
                # XTEST sends therefore fails this test, and so does a logger that reads the outer
                # display (it would add x/y/z to keys.jsonl).
                foreign = [p["keysym"] for p in rec.xev_presses(xev_log)]
                self.assertEqual(foreign, ["x", "y", "z"])
            finally:
                if logger:
                    logger.stop()
                for proc in (app, nested, outer):
                    rec.terminate(proc)

    def test_the_recorders_own_save_events_make_no_raw_key_burst(self):
        # R8: send_save_event is an XSendEvent, which XI2 raw listeners never see, so a snapshot
        # cannot schedule another burst snapshot; a real key on the same display is the control
        outer, env = xvfb(730, 740, "640x400x24")
        app = logger = None
        with tempfile.TemporaryDirectory() as folder:
            try:
                app, wid = xev(env, "T34-game-stand-in")
                logger = rec.KeyLogger(env, ":outer-unused", Path(folder) / "keys.jsonl")
                logger.start()
                time.sleep(1)
                for _ in range(3):
                    rec.send_save_event(wid, env)
                subprocess.run(["xdotool", "key", "q"], env=env, check=True)
                time.sleep(0.5)
                burst = rec.Burst()
                for event in logger.drain():
                    burst.add(event)
                logger.stop()
                self.assertEqual(logged(Path(folder) / "keys.jsonl"), [("press", "q"), ("release", "q")])
            finally:
                if logger:
                    logger.stop()
                for proc in (app, outer):
                    rec.terminate(proc)


class VideoTests(unittest.TestCase):
    def test_a_video_sitting_records_the_xephyr_window(self):
        # R4: `play.sh --video --quit-after` on private displays; the video grows while it runs
        outer, env = xvfb(780, 800)
        before = set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()
        sitting, session = None, None
        try:
            sitting = subprocess.Popen(["bash", str(ROOT / "runtime/human/play.sh"), "--video",
                                        "--quit-after", "8", "--res", "640x400"], env=env,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                       start_new_session=True)
            sizes, end = [], time.monotonic() + 30
            while time.monotonic() < end and sitting.poll() is None:
                fresh = (set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()) - before
                if fresh:
                    session = fresh.pop()
                    video = session / "video.mkv"
                    if video.is_file():
                        sizes.append(video.stat().st_size)
                time.sleep(1)
            self.assertEqual(sitting.wait(timeout=30), 0)
            self.assertIsNotNone(session)
            meta = json.loads((session / "meta.json").read_text())
            self.assertGreater(len(set(sizes)), 1, sizes)
            self.assertEqual(sizes, sorted(sizes))
            self.assertGreater(meta["video"]["bytes"], max(sizes))
            self.assertEqual(meta["video"]["geometry"][2:], [640, 400])
            self.assertEqual(meta["video"]["ended"], "SIGTERM")
            self.assertEqual((meta["burst_quiet_s"], meta["capture_margin_s"]),
                             (rec.BURST_QUIET_S, rec.CAPTURE_MARGIN_S))   # R7: the map reads these
        finally:
            rec.terminate(sitting)
            rec.terminate(outer)
            if session is not None:
                shutil.rmtree(session, ignore_errors=True)


def state(request, text, error=None, sent=None, staged=None):
    """A parsed snapshot: its save-request window and its screen text."""
    return {"entry": {"request_s": request, "sent_s": request if sent is None else sent,
                      "elapsed_s": request + 0.8 if staged is None else staged},
            "screen_text": text, "screen_digest": "attributes-digest", "error": error}


def press(when, key, kind="press"):
    return {"monotonic_s": when, "event": kind, "keysym": key}


def rows(result):
    return [(r["headline"], r["keys"], r["after_headline"], r["count"]) for r in result["transitions"]]


class MapTests(unittest.TestCase):
    def setUp(self):
        from tests import test_human_record  # noqa: F401  (registers extract for keymap)
        import keymap
        self.keymap = keymap

    def test_map_boundaries_order_identity_and_counts(self):
        # Deliberately shuffled inputs. Gaps: d (no snapshot before), MENU [a b] TEAM, TEAM [c]
        # MENU, MENU [a b] INVALID (an unparsed bracket), LATER [release only] MENU, MENU [a b]
        # TEAM again, z (no snapshot after).
        states = [state(16, "TEAM"), state(10, "LATER"), state(1, "MENU"), state(6, "MENU"),
                  state(8, "INVALID", "bad snapshot"), state(3, "TEAM"), state(14, "MENU")]
        events = [press(15.1, "b"), press(2.2, "b", "release"), press(17, "z"), press(6.6, "b"),
                  press(4.1, "c", "release"), press(2.1, "b"), press(11, "x", "release"),
                  press(15, "a"), press(4, "c"), press(6.5, "a"), press(0.5, "d"), press(2, "a")]
        result = self.keymap.build_map(states, events, 0)
        self.assertEqual(result["summary"], "screens: 3, transitions: 2, keys: 9")
        self.assertEqual(result["unmapped_keys"], 4)
        self.assertEqual(result["transitions"], [
            {"screen": hashlib.sha256(b"MENU").hexdigest(), "headline": "MENU", "keys": ["a", "b"],
             "after": hashlib.sha256(b"TEAM").hexdigest(), "after_headline": "TEAM", "count": 2},
            {"screen": hashlib.sha256(b"TEAM").hexdigest(), "headline": "TEAM", "keys": ["c"],
             "after": hashlib.sha256(b"MENU").hexdigest(), "after_headline": "MENU", "count": 1}])

    def test_a_key_between_a_snapshots_send_and_its_staging_is_on_that_snapshots_screen(self):
        # R1, the reviewer's sitting: `a` at 0.80 s; the burst snapshot (title) requested at
        # 1.31 s and staged at 2.12 s; `b` at 1.72 s was pressed on the title, not the shell
        shell = "Z:\\>mount c /home/someone/goal2/scratch/human/sessions/x/game\nZ:\\>C:\nC:\\>goal"
        states = [state(0.0, shell, sent=0.03, staged=0.8),
                  state(1.31, "TITLE", sent=1.34, staged=2.12),
                  state(2.22, "MENU", sent=2.25, staged=3.0)]
        events = [press(0.80, "a"), press(0.85, "a", "release"),
                  press(1.72, "b"), press(1.78, "b", "release")]
        result = self.keymap.build_map(states, events, 0)
        self.assertEqual(rows(result), [("Z:\\>C:", ["a"], "TITLE", 1), ("TITLE", ["b"], "MENU", 1)])
        self.assertEqual(result["unmapped_keys"], 0)
        self.assertNotIn("/home", json.dumps(result))         # R9: no host path in a headline

    def test_two_bursts_between_the_same_snapshots_are_unmapped(self):
        # R2: the burst snapshot after Return is missing, so Z did not follow Return alone
        states = [state(0, "X"), state(20, "Z")]
        events = [press(5, "Return"), press(10, "Escape")]
        result = self.keymap.build_map(states, events, 0)
        self.assertEqual((rows(result), result["unmapped_keys"]), ([], 2))
        self.assertEqual(result["summary"], "screens: 2, transitions: 0, keys: 2")

    def test_a_skipped_snapshot_request_unmaps_its_burst(self):
        # R2: the recorder logged a request that staged nothing; Z is not Return's screen
        states = [state(0, "X"), state(20, "Z")]
        events = [press(5, "Return")]
        result = self.keymap.build_map(states, events, 0)
        self.assertEqual(rows(result), [("X", ["Return"], "Z", 1)])   # control: nothing skipped
        skipped = [{"request_s": 5.5, "sent_s": 5.53, "origin": "burst", "seq": None},
                   {"request_s": 0, "sent_s": 0, "origin": "watcher", "seq": 1}]
        result = self.keymap.build_map(states, events, 0, requests=skipped)
        self.assertEqual((rows(result), result["unmapped_keys"]), ([], 1))

    def test_a_snapshot_inside_a_burst_splits_it(self):
        # R2: Return 20.0, cadence snapshot Y 20.3, Return 20.4, burst snapshot Z 21.5
        states = [state(0, "X"), state(20.3, "Y"), state(21.5, "Z")]
        events = [press(20.0, "Return"), press(20.4, "Return")]
        result = self.keymap.build_map(states, events, 0)
        self.assertEqual(rows(result), [("X", ["Return"], "Y", 1), ("Y", ["Return"], "Z", 1)])

    def test_the_quiet_interval_decides_one_burst_or_two(self):
        quiet = self.keymap.recorder.BURST_QUIET_S
        states = [state(0, "X"), state(20, "Z")]
        one = self.keymap.build_map(states, [press(5, "Return"), press(5 + quiet - 0.1, "Escape")], 0)
        self.assertEqual(rows(one), [("X", ["Return", "Escape"], "Z", 1)])
        two = self.keymap.build_map(states, [press(5, "Return"), press(5 + quiet + 0.1, "Escape")], 0)
        self.assertEqual((rows(two), two["unmapped_keys"]), ([], 2))

    def test_a_key_inside_a_request_window_is_ambiguous(self):
        margin = self.keymap.recorder.CAPTURE_MARGIN_S
        states = [state(0, "X"), state(10, "Y", sent=10.03), state(20, "Z")]
        inside = self.keymap.build_map(states, [press(10.03 + margin - 0.01, "a")], 0)
        self.assertEqual((rows(inside), inside["unmapped_keys"]), ([], 1))
        outside = self.keymap.build_map(states, [press(10.03 + margin + 0.01, "a")], 0)
        self.assertEqual(rows(outside), [("Y", ["a"], "Z", 1)])
        # a key at the very request time belongs to no screen; its burst-mate goes unmapped too
        at = self.keymap.build_map(states, [press(9.8, "m"), press(10, "k")], 0)
        self.assertEqual((rows(at), at["unmapped_keys"]), ([], 2))
        # a resend: the screen may be from any send in [request, last send]
        resent = [state(0, "X"), state(10, "Y", sent=13.1, staged=13.9), state(20, "Z")]
        mid = self.keymap.build_map(resent, [press(12, "a")], 0)
        self.assertEqual((rows(mid), mid["unmapped_keys"]), ([], 1))

    def test_an_entry_without_a_request_time_brackets_nothing_before_its_staging(self):
        # sittings recorded before the rework: elapsed_s is staging time, the screen's is unknown
        legacy = [{"entry": {"elapsed_s": 0.8}, "screen_text": "X", "error": None},
                  {"entry": {"elapsed_s": 2.12}, "screen_text": "TITLE", "error": None},
                  {"entry": {"elapsed_s": 3.0}, "screen_text": "MENU", "error": None}]
        result = self.keymap.build_map(legacy, [press(1.72, "b")], 0)
        self.assertEqual((rows(result), result["unmapped_keys"]), ([], 1))

    def test_the_headline_skips_host_paths(self):
        self.assertEqual(self.keymap.headline("\n  Z:\\>mount c /home/a/b\nZ:\\>goal\n"), "Z:\\>goal")
        self.assertEqual(self.keymap.headline("/home/a\n\n"), "(no headline)")

    def test_literal_session_map(self):
        from tests import test_human_record as fixture
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            chain = [({0: text}, fixture.player_array(), fixture.country_array(), fixture.state_tuple(), 0) for text in ("MENU", "TEAM", "MENU")]
            fixture.write_session(session, chain)
            meta = json.loads((session / "meta.json").read_text())
            meta.update({"monotonic_start_s": 100.0, "burst_quiet_s": 0.6, "capture_margin_s": 0.07})
            (session / "meta.json").write_text(json.dumps(meta))
            events = [{"monotonic_s": t, "utc": "2026-10-09T00:00:00+00:00", "event": kind, "keycode": code, "keysym": sym} for t, kind, code, sym in ((121.0, "press", 38, "a"), (121.1, "release", 38, "a"), (141.0, "press", 9, "Escape"), (141.1, "release", 9, "Escape"))]
            (session / "keys.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
            result = self.keymap.read_session(session)
            self.assertEqual(result["summary"], "screens: 2, transitions: 2, keys: 2")
            self.assertEqual(rows(result), [("MENU", ["a"], "TEAM", 1), ("TEAM", ["Escape"], "MENU", 1)])
            self.assertEqual(result["unmapped_keys"], 0)
            # R7: the session's own recorded constants, not whatever the code says today
            self.assertEqual((result["burst_quiet_s"], result["capture_margin_s"]), (0.6, 0.07))
            states = [fixture.extract.read_snapshot(session, e, [1]) for e in fixture.extract.read_index(session)[0]]
            record, _ = fixture.extract.build_record(session, states, {}, [1], session / "runs", "fixture", "2026-10-09T00:00:00Z", 0)
            self.assertEqual(json.loads(next(o["value"] for o in record["observations"] if o["field"] == "screen/key map (JSON)")), result)
            # a skipped request between MENU and TEAM (requests.jsonl) unmaps `a` only
            (session / "requests.jsonl").write_text(json.dumps(
                {"request_s": 30.0, "sent_s": 30.03, "origin": "burst", "seq": None}) + "\n")
            result = self.keymap.read_session(session)
            self.assertEqual(rows(result), [("TEAM", ["Escape"], "MENU", 1)])
            self.assertEqual(result["unmapped_keys"], 1)
            record, _ = fixture.extract.build_record(session, states, {}, [1], session / "runs", "fixture", "2026-10-09T00:00:00Z", 0)
            self.assertIn("read save requests requests.jsonl", [o["field"] for o in record["observations"]])

    def test_keymap_prints_and_writes_no_record(self):
        # R5: one record per sitting (extract.py's); keymap.py only prints
        from tests import test_human_record as fixture
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            chain = [({0: text}, fixture.player_array(), fixture.country_array(), fixture.state_tuple(), 0) for text in ("MENU", "TEAM")]
            fixture.write_session(session, chain)
            meta = json.loads((session / "meta.json").read_text())
            meta["monotonic_start_s"] = 100.0
            (session / "meta.json").write_text(json.dumps(meta))
            (session / "keys.jsonl").write_text(json.dumps({"monotonic_s": 121.0, "event": "press", "keysym": "a"}) + "\n")
            listing = sorted(p for p in ROOT.joinpath("runs", "E015").iterdir())
            tables = sorted(ROOT.joinpath("experiments", "E015-human-playthrough").iterdir())
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(self.keymap.main([str(session)]), 0)
            self.assertTrue(out.getvalue().startswith("screens: 2, transitions: 1, keys: 1\n"))
            self.assertEqual(sorted(ROOT.joinpath("runs", "E015").iterdir()), listing)
            self.assertEqual(sorted(ROOT.joinpath("experiments", "E015-human-playthrough").iterdir()), tables)
            self.assertEqual(sorted(p.name for p in session.iterdir()),
                             ["index.jsonl", "keys.jsonl", "meta.json", "snapshots"])


class GuardTests(unittest.TestCase):
    """R3: the acceptance guard (scripted_keys.check_bursts) requires a distinct, correctly timed
    burst snapshot per key group — never "any later snapshot" for every group."""

    def setUp(self):
        import scripted_keys
        self.sk = scripted_keys

    def test_group_presses_splits_on_the_quiet_interval(self):
        events = [{"event": "press", "monotonic_s": t, "keysym": k} for t, k in
                  ((0.0, "a"), (0.2, "b"), (0.9, "c"), (1.6, "d"))]
        self.assertEqual(self.sk.group_presses(events, 0.5), [[0.0, 0.2], [0.9], [1.6]])

    def test_one_snapshot_per_group_passes(self):
        # 3 groups, 3 distinct burst snapshots staged after each group's last key
        groups = [[0.0], [1.0], [2.0]]
        bursts = [{"elapsed_s": 0.7}, {"elapsed_s": 1.7}, {"elapsed_s": 2.7}]
        ok, _ = self.sk.check_bursts(groups, bursts, 100.0)
        self.assertTrue(ok)

    def test_fewer_snapshots_than_groups_fails(self):
        # the R2/R3 bug: 4 snapshots for 10 groups. The old `any(...)` let one final snapshot
        # satisfy every group; the guard must reject it.
        groups = [[k * 0.51] for k in range(10)]
        bursts = [{"elapsed_s": 2.0}, {"elapsed_s": 3.0}, {"elapsed_s": 4.0}, {"elapsed_s": 5.0}]
        ok, why = self.sk.check_bursts(groups, bursts, 0.0)
        self.assertFalse(ok)
        self.assertIn("4 burst snapshots for 10 key group(s)", why)

    def test_the_same_snapshot_cannot_bracket_two_groups(self):
        # one snapshot staged after every key is not "correctly timed": each group needs its own.
        groups = [[0.0], [1.0], [2.0]]
        bursts = [{"elapsed_s": 99.0}]
        ok, _ = self.sk.check_bursts(groups, bursts, 0.0)
        self.assertFalse(ok)
