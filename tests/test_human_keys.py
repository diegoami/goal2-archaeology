"""T34 nested-display recorder tests: the private display, the key logger's privacy, the burst
snapshot, the Xephyr window bind and video, and the screen/key map's rules."""
import hashlib
import importlib.util
import json
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types
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
        # the settled episode's request goes out EVENT_SETTLE_S after its last key event —
        # long before the group's due time (1.5 s), where the window could never fit between
        # keys spaced just over the quiet interval
        self.assertAlmostEqual(ticks[1][0], 1.0 + rec.EVENT_SETTLE_S)
        self.assertEqual(ticks[1][1], "burst")

    def test_a_key_episodes_request_goes_out_at_the_settle_not_at_due(self):
        # Sol r2 R1: the request window must open EVENT_SETTLE_S after the episode's newest
        # event — after that key's release, and well before the due time (last key + quiet),
        # where the window (~0.08 s wide) could never fit between keys spaced 0.527 s apart
        # (the reproduction's measured wire spacing): every pair would share a gap or the
        # next key would land inside the window.
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
        arrivals = [1.0 + 0.527 * k for k in range(3)]
        seen = [0]
        def drain():
            out = []
            while seen[0] < len(arrivals) and arrivals[seen[0]] <= now[0]:
                out.append({"monotonic_s": arrivals[seen[0]]})
                seen[0] += 1
            return out
        keys.drain = drain
        watcher.run(quit_after=4, keys=keys)
        bursts = [t for t in ticks if t[1] == "burst"]
        # group 0 (key 1.0) is due at 1.5; the next key lands 1.527 > due + defer? no: 1.6 is
        # the defer deadline and 1.527 < 1.6, so the key arrives first and the request follows
        # it (1.53), never at 1.5 where its window would swallow the 1.527 key
        self.assertEqual(len(bursts), 3, bursts)
        # each episode's request follows its own key by EVENT_SETTLE_S (not at due: 1.5+)
        self.assertAlmostEqual(bursts[0][0], 1.0 + rec.EVENT_SETTLE_S, delta=0.02)
        self.assertAlmostEqual(bursts[1][0], 1.527 + rec.EVENT_SETTLE_S, delta=0.02)
        for (t, _), a in zip(bursts, arrivals):
            self.assertLess(t, a + 0.5)     # each episode's request, before its due time
        for t, _ in bursts:
            # no request window [t, t + margin] covers a key: each key arrived first
            for a in arrivals:
                self.assertFalse(t <= a <= t + rec.CAPTURE_MARGIN_S, (t, a))

    def test_human_paced_keys_account_for_every_group_in_a_request_or_a_merge(self):
        # R2 end-to-end at the requested 0.5-1.5 s human pace: 10 single-key groups 0.51 s apart
        # (above the 0.5 s quiet). Each tick (save + capture) advances the clock 0.75 s, longer
        # than the 0.51 s gap, so keys keep arriving while a burst snapshot is being captured.
        # R2's overwriting Burst.last produced 4 requests and LOST groups. Since T44 (issue #128)
        # the groups that settle during a save are answered by the next ONE request: fewer than
        # 10 requests, but their merge markers add up to all 10 groups (the last of each merge
        # claimed, the earlier ones recorded as not captured), none lost.
        now = [0.0]
        watcher = rec.Watcher.__new__(rec.Watcher)
        watcher.clock = lambda: now[0]
        watcher.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
        watcher.t0 = 0.0
        watcher.dbx = Mock()
        watcher.dbx.poll.return_value = None
        watcher.log = lambda msg: None
        ticks = []

        merges = []

        def tick(**kw):
            ticks.append((now[0], kw.get("origin", "watcher")))
            if kw.get("merge"):
                merges.append(kw["merge"])
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
        self.assertEqual(len(bursts), len(merges))
        self.assertEqual(sum(m["size"] for m in merges), 10, merges)   # no group lost
        self.assertLess(len(bursts), 10)                    # and the saves did merge some
        self.assertTrue(all(m["claimed"] == m["size"] == len(m["group_last_s"])
                            for m in merges), merges)

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
                                        "--scale", "1", "--quit-after", "8", "--res", "640x400"], env=env,
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
            # The sizes are polled once a second until the sitting exits, so the last sample may
            # already be the finished file (#177: 47150 == 47150 under load): the final size is
            # never SMALLER than any sample (>=); growth during the sitting is shown by the
            # samples alone (len(set(sizes)) > 1 above); and meta's bytes is the file's final size.
            final = (session / "video.mkv").stat().st_size
            self.assertGreaterEqual(meta["video"]["bytes"], max(sizes))
            self.assertEqual(meta["video"]["bytes"], final)
            self.assertGreater(final, 0)
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


class BurstPipelineTests(unittest.TestCase):
    """Sol delta r2 R1: keys ~0.53 s apart (the 0.51 s-sleep reproduction's measured wire
    spacing) must EACH be mapped — one request window between every pair of keys, with the
    staging captures off the loop's critical path (a ~0.8 s capture used to delay the next
    request until after the next key had arrived, leaving key pairs between two windows)."""

    def test_ten_keys_at_051_s_gaps_are_all_accounted_for(self):
        from tests import test_human_record as fixture
        import keymap
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            (session / "snapshots").mkdir()
            live = session / "state.sav"
            live.write_bytes(fixture.tiny_zip(b"vga-0"))
            writes = queue.Queue()

            def serve_writes():
                # [designed] a serialized stand-in for DOSBox-X's savestate writer: each save
                # request is answered 0.6 s later with one fresh atomic write (a new inode),
                # slower than the 0.527 s key spacing — a scheduler that waits for the previous
                # capture cannot keep up, which is the blocking defect the pipeline removes
                n = 0
                while True:
                    item = writes.get()
                    if item is None:
                        return
                    time.sleep(0.6)
                    tmp = live.with_name(live.name + ".tmp")
                    tmp.write_bytes(fixture.tiny_zip(f"vga-{item}".encode()))
                    tmp.replace(live)

            threading.Thread(target=serve_writes, daemon=True).start()
            counter = [0]

            def xrun(argv):
                time.sleep(0.03)          # the XSendEvent send duration (probe: ~26 ms)
                counter[0] += 1
                writes.put(counter[0])

            w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                            xrun=xrun, alive=lambda: True, log=lambda m: None)
            arrivals = [w.t0 + 1.0 + 0.527 * k for k in range(10)]

            class FakeKeys:
                error = None
                proc = types.SimpleNamespace(poll=lambda: None)

                def __init__(self):
                    self.events = []
                    for k, t in enumerate(arrivals):
                        self.events.append({"monotonic_s": t, "event": "press", "keysym": f"k{k}"})
                        # [designed] the release lag is xdotool's ~12 ms key duration: the
                        # recorder groups on ALL events, so a slower release (0.05 s) would
                        # chain every pair into one group (0.527 < 0.05 + quiet)
                        self.events.append({"monotonic_s": t + 0.012, "event": "release",
                                            "keysym": f"k{k}"})
                    self.i = 0

                def drain(self):
                    now = time.monotonic()
                    out = []
                    while self.i < len(self.events) and self.events[self.i]["monotonic_s"] <= now:
                        out.append(self.events[self.i])
                        self.i += 1
                    return out

            entries = w.run(quit_after=8.5, keys=FakeKeys())
            writes.put(None)
            index = [json.loads(line) for line in (session / "index.jsonl").read_text().splitlines()]
            requests = [json.loads(line) for line in
                        (session / "requests.jsonl").read_text().splitlines()]
            # T44 (issue #128): each save (0.6 s) is longer than the 0.527 s key spacing, so one
            # request is in flight at a time and the groups that settle during it are answered
            # by the next one request. The pre-T44 form of this test asserted all 10 presses
            # mapped; that held only while requests overlapped (and were superseded on a real
            # emulator). A request now goes out when the previous one ends, at whatever moment
            # that is, and a key arriving inside its window stays ambiguous (keymap.py's rule),
            # so what is asserted is the accounting: no group lost, every press either mapped,
            # listed under a merge (not captured / claimed) or counted unmapped
            bursts = [r for r in requests if r["origin"] == "burst"]
            self.assertEqual(len(entries), 1 + len(bursts))
            self.assertEqual([e["origin"] for e in index], ["watcher"] + ["burst"] * len(bursts))
            self.assertEqual([r["seq"] is not None for r in requests], [True] * len(requests))
            self.assertEqual(sum(r["merge"]["size"] for r in bursts), 10)   # no group lost
            states = [{"entry": e, "screen_text": f"SCREEN-{e['seq']}", "error": None}
                      for e in index]
            events = sorted(FakeKeys().events, key=lambda e: e["monotonic_s"])
            result = keymap.build_map(states, events, w.t0, quiet=rec.BURST_QUIET_S,
                                      margin=rec.CAPTURE_MARGIN_S, requests=requests)
            accounted = (sum(r["count"] * len(r["keys"]) for r in result["transitions"])
                         + sum(len(g["keys"]) for g in result["not_captured"])
                         + sum(len(g["keys"]) for g in result["merged_claimed"])
                         + result["unmapped_keys"])
            self.assertEqual(accounted, 10, result)

    def test_a_pipeline_timeout_marks_the_request_skipped(self):
        # Sol r2 R1c: a capture that times out is logged as a request that staged nothing —
        # its group is skipped (its bursts unmapped), never silently covered by a later
        # group's snapshot
        from tests import test_human_record as fixture
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            (session / "snapshots").mkdir()
            live = session / "state.sav"
            live.write_bytes(fixture.tiny_zip(b"vga"))
            clock = fixture.FakeClock()
            w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                            clock=clock, sleep=clock.sleep, xrun=lambda a: None,
                            alive=lambda: True, log=lambda m: None)
            self.assertIsNone(w._stage_job(rec.file_signature(live), 0.0, 0.03, "burst", 0))
            line = json.loads((session / "requests.jsonl").read_text())
            # the group is marked skipped: a request that staged nothing (its window may span
            # the gate's resends; what the map needs is the seq of None)
            self.assertEqual((line["request_s"], line["origin"], line["seq"]),
                             (0.0, "burst", None))
            self.assertFalse((session / "index.jsonl").exists())


class DeferredCaptureTests(unittest.TestCase):
    """Sol delta r3 R1/R2: a stage job that runs late (the reviewer's wrap-_stage_job 2 s
    sleep) must not stage the live savestate's CURRENT bytes under the slow request's window —
    by then later requests have overwritten the file. The request is marked superseded, the
    map unmaps its group, and the acceptance guard rejects the sitting with 'request
    attribution lost'."""

    def _sitting(self, delay_first_job, quit_after):
        # the r2 reproduction's harness: a serialized stand-in writer (0.6 s per atomic save),
        # keys 0.527 s apart, staging off the loop's critical path
        from tests import test_human_record as fixture
        session = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, session, ignore_errors=True)
        (session / "snapshots").mkdir()
        live = session / "state.sav"
        live.write_bytes(fixture.tiny_zip(b"vga-0"))
        writes = queue.Queue()

        def serve_writes():
            n = 0
            while True:
                item = writes.get()
                if item is None:
                    return
                time.sleep(0.6)
                tmp = live.with_name(live.name + ".tmp")
                tmp.write_bytes(fixture.tiny_zip(f"vga-{item}".encode()))
                tmp.replace(live)

        threading.Thread(target=serve_writes, daemon=True).start()
        counter = [0]

        def xrun(argv):
            time.sleep(0.03)
            counter[0] += 1
            writes.put(counter[0])

        w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                        xrun=xrun, alive=lambda: True, log=lambda m: None)
        # T44 (issue #128): the loop's one-in-flight gate keeps requests from piling up, which is
        # what made these captures supersede each other. Here the gate is OFF: the defence in
        # depth (the ownership guards of T35) must still catch a pile-up if one ever got through
        w.request_in_flight = lambda: False
        if delay_first_job:
            # the r3 reproduction: the recorder child's _stage_job sleeps 2 s before its
            # first burst capture; while it waits, later requests rewrite the live savestate
            original = w._stage_job
            slept = [False]

            def slow_first(*args, **kwargs):
                if not slept[0]:
                    slept[0] = True
                    time.sleep(2.0)
                return original(*args, **kwargs)
            w._stage_job = slow_first
        arrivals = [w.t0 + 1.0 + 0.527 * k for k in range(10)]

        class FakeKeys:
            error = None
            proc = types.SimpleNamespace(poll=lambda: None)

            def __init__(self):
                self.events = []
                for k, t in enumerate(arrivals):
                    self.events.append({"monotonic_s": t, "event": "press", "keysym": f"k{k}"})
                    self.events.append({"monotonic_s": t + 0.012, "event": "release",
                                        "keysym": f"k{k}"})
                self.i = 0

            def drain(self):
                now = time.monotonic()
                out = []
                while self.i < len(self.events) and self.events[self.i]["monotonic_s"] <= now:
                    out.append(self.events[self.i])
                    self.i += 1
                return out

        entries = w.run(quit_after=quit_after, keys=FakeKeys())
        writes.put(None)
        index = []
        if (session / "index.jsonl").is_file():   # a fully-superseded sitting stages nothing
            index = [json.loads(line) for line in
                     (session / "index.jsonl").read_text().splitlines()]
        requests = [json.loads(line) for line in
                    (session / "requests.jsonl").read_text().splitlines()]
        return session, w, entries, index, requests

    def test_a_deferred_stage_job_is_marked_superseded_and_never_stages(self):
        # R1: the slow job wakes to a live savestate later requests have already rewritten
        # (a completed, unconsumed write predating the job); it must stage NOTHING under its
        # own request window and be marked superseded in requests.jsonl
        import keymap
        session, w, entries, index, requests = self._sitting(True, quit_after=14)
        superseded = [r for r in requests if r.get("superseded")]
        self.assertTrue(superseded, requests)          # the deferred capture was caught
        for r in superseded:
            self.assertIsNone(r["seq"])                # superseded requests stage nothing
        # no staged entry carries a superseded request's window
        windows = {(e["request_s"]) for e in index}
        for r in superseded:
            self.assertNotIn(r["request_s"], windows)
        # the map unmaps the superseded groups' presses: their boundary is lost, not guessed
        # (every superseded request is a sample that staged nothing, so the keys beside it
        # lose a bracket; at minimum the first deferred group's own key is unmapped)
        states = [{"entry": e, "screen_text": f"SCREEN-{e['seq']}", "error": None}
                  for e in index]
        events = []
        for k in range(10):
            events.append({"monotonic_s": w.t0 + 1.0 + 0.527 * k, "event": "press",
                           "keysym": f"k{k}"})
        result = keymap.build_map(states, events, w.t0, quiet=rec.BURST_QUIET_S,
                                  margin=rec.CAPTURE_MARGIN_S, requests=requests)
        self.assertGreaterEqual(result["unmapped_keys"], 1)

    def test_the_guard_rejects_a_superseded_sitting(self):
        # R2: the acceptance guard (check_attribution, as scripted_keys.main runs it first)
        # must reject the deferred-capture sitting with the attribution error, and must NOT
        # reject a clean sitting's requests — including identical staged screens — on hash
        # grounds (R2c: the check is on attribution, not uniqueness)
        import scripted_keys
        _, _, _, _, requests = self._sitting(True, quit_after=14)
        ok, why = scripted_keys.check_attribution(requests)
        self.assertFalse(ok)
        self.assertIn("request attribution lost", why)
        self.assertIn("lost boundary", why)
        clean = [{"request_s": 0.0, "sent_s": 0.03, "origin": "watcher", "seq": 1,
                  "pre_sig": [1, 4096, 10, 11], "accept_sig": [1, 4096, 12, 13],
                  "pre_events": 0, "accept_events": 54,
                  "request_file": "requests/rq-0001.sav", "request_sha256": "h1"},
                 {"request_s": 20.0, "sent_s": 20.03, "origin": "watcher", "seq": 2,
                  "pre_sig": [1, 4096, 20, 21], "accept_sig": [1, 4096, 22, 23],
                  "pre_events": 54, "accept_events": 108,
                  "request_file": "requests/rq-0002.sav", "request_sha256": "h2"},
                 {"request_s": 40.0, "sent_s": 40.03, "origin": "watcher", "seq": 3,
                  "pre_sig": [1, 4096, 40, 41], "accept_sig": [1, 4096, 42, 43],
                  "pre_events": 108, "accept_events": 162,
                  "request_file": "requests/rq-0003.sav", "request_sha256": "h3"}]
        ok, why = scripted_keys.check_attribution(clean)
        self.assertTrue(ok)
        no_requests_ok, _ = scripted_keys.check_attribution([])
        self.assertTrue(no_requests_ok)

    def test_a_clean_pipeline_sitting_has_no_superseded_requests(self):
        # control: without the injected delay the same sitting (the r2 10/10 reproduction)
        # must stage every request — the attribution check is additive, not breaking
        _, _, entries, _, requests = self._sitting(False, quit_after=8.5)
        self.assertEqual(len(entries), 11)
        self.assertFalse([r for r in requests if r.get("superseded")], requests)


class AttributionBypassTests(unittest.TestCase):
    """Sol delta r4 R1: the r3 fix caught the 2 s deferred capture, but faster
    overwrites still pass — the lag check runs only on the first poll, and the
    stability fallback re-stages bytes the pipeline already consumed. Both
    bypasses stage a LATER request's savestate under an earlier request's window
    with an ordinary, successful request line.

    The injected write source models the MEASURED real writer: one DOSBox-X save
    produces 53-54 write events on state.sav (evidence/E015/
    T34-probe-closes-20261009-01.log; the old docstring's '27 close events'
    counted only CLOSE_WRITE), so two saves landing in one poll gap are ~108
    events — the write accounting that ownership needs."""

    def _sitting(self, actions):
        """A Watcher on a fake clock whose sleeps run `actions` (one per sleep),
        with an injected write source (busy, events) the actions drive."""
        from tests import test_human_record as fixture
        session = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, session, ignore_errors=True)
        (session / "snapshots").mkdir()
        live = session / "state.sav"
        live.write_bytes(fixture.tiny_zip(b"vga-0"))
        state = {"busy": False, "events": 0}

        class ScriptedClock:
            LIMIT_S = 3600.0

            def __init__(self, actions):
                self.t = 0.0
                self.actions = list(actions)

            def __call__(self):
                return self.t

            def sleep(self, s):
                self.t += s
                if self.t > self.LIMIT_S:
                    raise AssertionError("fake clock ran away")
                if self.actions:
                    self.actions.pop(0)()

        self.clock = ScriptedClock(actions)
        w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                        clock=self.clock, sleep=self.clock.sleep, xrun=lambda a: None,
                        alive=lambda: True, log=lambda m: None)
        w.activity = lambda: (state["busy"], state["events"])   # the write source
        w._submitted, w._finished = 2, 0    # a later request is already queued
        return session, w, live, state

    def test_a_fast_overwrite_is_superseded_not_staged(self):
        # reproduction 1: the first poll sees no completed write (the r3 lag check's
        # blind side); the first sleep serves BOTH queued requests, so two saves'
        # write events (108) land in one gap and the live file holds the LATER
        # request's bytes. Pre-fix, the fresh-arrival branch staged them.
        from tests import test_human_record as fixture
        import scripted_keys

        def later_writes(live, state):
            live.write_bytes(fixture.tiny_zip(b"LATER REQUEST BYTES"))
            state["events"] = 108        # two saves' write events in one poll gap
        session, w, live, state = self._sitting([])
        pre = rec.file_signature(live)
        state["events"] = 0
        # arm the write after the pre-send snapshot: the first capture sleep serves
        # both queued requests
        self.clock.actions.append(lambda: later_writes(live, state))
        entry = w._stage_job(pre, 0.0, 0.03, "burst", 0,
                             session / "requests" / "rq-0001.sav")
        line = json.loads((session / "requests.jsonl").read_text())
        self.assertIsNone(entry)                    # nothing staged under its window
        self.assertTrue(line.get("superseded"), line)
        self.assertIsNone(line["seq"])
        self.assertFalse((session / "index.jsonl").exists())
        ok, why = scripted_keys.check_attribution([line])
        self.assertFalse(ok)

    def test_a_one_save_of_later_write_events_is_not_staged_under_the_earlier_request(self):
        # Sol delta r4 R1, the residual (issue #111 R1): the every-poll ownership check
        # only bounds the UPPER end of the event advance (> ONE_SAVE_MAX_EVENTS), and the
        # r3 lag check runs only on the first poll. So when a job's first poll sees NO
        # completed write (lag already > 1: a later request is queued) and a later
        # request's save then lands within one save's bound of write events, the
        # fresh-arrival branch staged those bytes under the earlier request's window with
        # an ordinary, successful line — the reviewer's 'STAGED LATER BYTES UNDER FIRST
        # REQUEST: True' (PR #106 delta r4 review, R1). The injection is the Sol
        # reproduction's: injected clock, _submitted=2/_finished=0, event count 0 at the
        # first poll, then one write of LATER REQUEST BYTES advancing the count to 2.
        from tests import test_human_record as fixture
        import scripted_keys
        session, w, live, state = self._sitting([])
        pre = rec.file_signature(live)
        state["events"] = 0
        self.clock.actions.append(
            lambda: (live.write_bytes(fixture.tiny_zip(b"LATER REQUEST BYTES")),
                     state.__setitem__("events", 2)))
        entry = w._stage_job(pre, 0.0, 0.03, "burst", 0,
                             session / "requests" / "rq-0001.sav")
        line = json.loads((session / "requests.jsonl").read_text())
        self.assertIsNone(entry)                    # nothing staged under its window
        self.assertTrue(line.get("superseded"), line)
        self.assertIsNone(line["seq"])
        self.assertFalse((session / "index.jsonl").exists())
        ok, why = scripted_keys.check_attribution([line])
        self.assertFalse(ok)
        self.assertIn("lost boundary", why)

    def test_a_head_jobs_two_saves_in_one_poll_gap_are_refused(self):
        # the every-poll magnitude check's own shape (T34 r4 R1), which the T35 unanchored-
        # capture gate deliberately does NOT cover: this job IS the pipeline's head (lag 1,
        # no later request queued), so the fresh-arrival gate accepts on head grounds — but
        # two saves' write events (108 > ONE_SAVE_MAX_EVENTS) in one poll gap mean the live
        # file now holds the NEXT request's save. The magnitude check must still refuse it:
        # T35's mutation sweep showed the check had become redundant against every test this
        # suite visits (the lag-2 shapes now die on the gate instead), so this visits the
        # lag-1 shape the gate cannot see.
        from tests import test_human_record as fixture
        session, w, live, state = self._sitting([])
        w._submitted, w._finished = 1, 0        # the pipeline's head: nothing else queued
        pre = rec.file_signature(live)
        state["events"] = 0
        self.clock.actions.append(
            lambda: (live.write_bytes(fixture.tiny_zip(b"TWO SAVES LATER")),
                     state.__setitem__("events", 2 * 54)))
        entry = w._stage_job(pre, 0.0, 0.03, "burst", 0,
                             session / "requests" / "rq-0001.sav")
        line = json.loads((session / "requests.jsonl").read_text())
        self.assertIsNone(entry)                # nothing staged under its window
        self.assertTrue(line.get("superseded"), line)
        self.assertIn("more than one save", (w.problems or [""])[0])

    def test_the_stability_fallback_never_restages_consumed_bytes(self):
        # reproduction 2: the live savestate already holds the later request's save,
        # an earlier job already consumed it (_fast_consumed matches its event count
        # and signature). Pre-fix, the stability fallback read the LIVE file and
        # staged those consumed bytes again under the earlier request.
        from tests import test_human_record as fixture
        session, w, live, state = self._sitting([])
        pre = rec.file_signature(live)              # the pre-send savestate (vga-0)
        live.write_bytes(fixture.tiny_zip(b"LATER REQUEST BYTES"))
        state["events"] = 108
        w._fast_consumed = (108, rec.file_signature(live))
        entry = w._stage_job(pre, 0.0, 0.03, "burst", 0)   # no per-request path: the
        #                                                     fallback must still not read live
        line = json.loads((session / "requests.jsonl").read_text())
        self.assertIsNone(entry)
        self.assertIsNone(line["seq"], line)
        self.assertFalse((session / "index.jsonl").exists())
        # the sitting this produces is rejected: the skipped request (seq None)
        # unmaps its group (the coverage guard, as test_a_skipped_snapshot_request_
        # unmaps_its_burst proves), and the pre-fix ordinary staged line — what the
        # bypass used to write — now fails the guard's evidence requirement
        import scripted_keys
        ok, why = scripted_keys.check_attribution(
            [{"request_s": 0.0, "sent_s": 0.03, "origin": "burst", "seq": 1}])
        self.assertFalse(ok)


class GuardAttributionTests(unittest.TestCase):
    """Sol delta r4 R2: absence of `superseded` is not ownership evidence — the
    bypasses produced ordinary successful request lines. check_attribution must
    require the recorder's write accounting on every staged request."""

    def setUp(self):
        import scripted_keys
        self.sk = scripted_keys

    def _evidenced(self, seq, request_s, pre, acc, pre_sig=True):
        line = {"request_s": request_s, "sent_s": request_s + 0.03, "origin": "burst",
                "seq": seq, "pre_events": pre, "accept_events": acc,
                "request_file": f"requests/rq-{seq:04d}.sav",
                "request_sha256": f"hash-{seq}"}
        if pre_sig:
            # the signature pair every staged line of this tree carries (T35 R2): the live
            # savestate's signature hash before the send and at the accepted capture, taken
            # a write apart so the pair differs
            line["pre_sig"] = [1234, 4096, 1_700_000_000_000_000_000, 1_700_000_000_000_000_001]
            line["accept_sig"] = [1235, 4096, 1_700_000_000_000_000_100, 1_700_000_000_000_000_101]
        return line

    def test_an_ordinary_staged_line_without_evidence_is_rejected(self):
        # the exact line shape the bypasses produced (all four acceptance checks
        # returned true on it pre-fix)
        line = self._evidenced(1, 0.0, 0, 54, pre_sig=False)
        del line["pre_events"], line["accept_events"], line["request_file"], line["request_sha256"]
        ok, why = self.sk.check_attribution([line])
        self.assertFalse(ok)
        self.assertIn("ownership evidence", why)

    def test_a_line_with_write_accounting_but_no_pre_send_state_is_rejected(self):
        # Sol delta r4 R2 (issue #111 R2): the r4 R1 bypass's request line carries the
        # recorder's whole write accounting (pre_events/accept_events, the per-request
        # file and its hash) yet ties those bytes to no pre-send state — the bytes on
        # the live savestate when the request was sent. Absence of `superseded` plus
        # self-reported counts is evidence-free: the guard must reject it, with the
        # bracketing snapshot and key event that made the other three checks pass.
        line = self._evidenced(1, 0.0, 0, 2, pre_sig=False)
        ok, why = self.sk.check_attribution([line])
        self.assertFalse(ok)
        self.assertIn("evidence-free", why)
        self.assertIn("pre-send state", why)

    def test_a_line_without_the_accept_time_state_is_rejected(self):
        # T35's class sweep, the missing half of the same evidence: the recorder writes the
        # signature pair on every staged line (capture always returns an accept-time
        # signature), so a line that names a pre-send state but no accept-time state is
        # evidence-free in exactly the way the r4 bypass's line was — nothing ties its bytes
        # to a fresh write inside this request's window.
        line = self._evidenced(1, 0.0, 0, 54)
        del line["accept_sig"]
        ok, why = self.sk.check_attribution([line])
        self.assertFalse(ok)
        self.assertIn("evidence-free", why)
        self.assertIn("accept-time state", why)

    def test_a_request_that_staged_nothing_is_rejected(self):
        # 'Missing-staged requests fail' (T35 Scope 2): a request line with no seq is a
        # screen the recorder could not see; certifying it would certify a boundary it
        # never owned.
        ok, why = self.sk.check_attribution(
            [{"request_s": 0.0, "sent_s": 0.03, "origin": "burst", "seq": None,
              "pre_sig": None, "pre_events": 0}])
        self.assertFalse(ok)
        self.assertIn("staged nothing", why)

    def test_two_saves_in_one_request_window_are_rejected(self):
        line = self._evidenced(1, 0.0, 0, 108)      # > ONE_SAVE_MAX_EVENTS
        ok, why = self.sk.check_attribution([line])
        self.assertFalse(ok)
        self.assertIn("more than one save", why)

    def test_staged_requests_must_own_increasing_writes(self):
        lines = [self._evidenced(1, 0.0, 0, 54), self._evidenced(2, 1.0, 0, 54)]
        ok, why = self.sk.check_attribution(lines)
        self.assertFalse(ok)
        self.assertIn("distinct writes", why)

    def test_a_well_evidenced_sitting_passes(self):
        lines = [self._evidenced(1, 0.0, 0, 54), self._evidenced(2, 1.0, 54, 108)]
        ok, _ = self.sk.check_attribution(lines)
        self.assertTrue(ok)
        ok, why = self.sk.check_attribution(lines, write_events_total=108)
        self.assertTrue(ok, why)

    def test_a_line_without_only_the_pre_send_state_is_rejected(self):
        # Sol's R2 on PR 112 (round 2): the pre-send requirement must be proved on a line that
        # lacks ONLY its pre-send state — with accept_sig present, removing the requirement
        # must turn this rejection into a pass, not merely change the message
        line = self._evidenced(1, 0.0, 0, 54)
        del line["pre_sig"]
        ok, why = self.sk.check_attribution([line])
        self.assertFalse(ok)
        self.assertIn("pre-send state", why)

    def test_a_later_save_under_a_matching_window_is_rejected(self):
        # Sol's R1 on PR 112 (round 2): plausible accounting, one save per line, the staged
        # snapshot claiming this request's own window, yet the bytes are the LATER request's
        # save. That save happened (the bytes came from it) and no line owns it: the sitting's
        # write total counts three saves for two staged lines. The option-A binding (the
        # owner, 2026-10-11) refuses it; without the total the same lines pass.
        lines = [self._evidenced(1, 0.0, 0, 54), self._evidenced(2, 2.05, 54, 108)]
        self.assertTrue(self.sk.check_attribution(lines)[0])
        ok, why = self.sk.check_attribution(lines, write_events_total=162)
        self.assertFalse(ok)
        self.assertIn("a save no request line owns", why)

    def test_a_line_two_saves_past_the_previous_is_rejected(self):
        # a later save's bytes under line 2, with the save between owned by no line: its own
        # pre-send count is one save back (54 events), but it accepted two saves past line 1
        lines = [self._evidenced(1, 0.0, 0, 54), self._evidenced(2, 1.0, 108, 162)]
        ok, why = self.sk.check_attribution(lines)
        self.assertFalse(ok)
        self.assertIn("not exactly one save", why)

    def test_a_save_before_the_first_request_is_rejected(self):
        # the first line's bytes are the SECOND save of the sitting: the first is owned by none
        ok, why = self.sk.check_attribution([self._evidenced(1, 0.0, 54, 108)])
        self.assertFalse(ok)
        self.assertIn("before the first request", why)

    def test_a_session_without_its_write_total_is_rejected(self):
        # with the session folder the guard needs the recorder's write total: a sitting that
        # records none proves nothing about unowned saves
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "requests").mkdir()
            data = b"own save bytes"
            (Path(tmp) / "requests" / "rq-0001.sav").write_bytes(data)
            line = self._evidenced(1, 0.0, 0, 54)
            line["request_sha256"] = rec.sha256(data)
            ok, why = self.sk.check_attribution([line], session=tmp)
            self.assertFalse(ok)
            self.assertIn("no write_events_total", why)
            ok, why = self.sk.check_attribution([line], session=tmp, write_events_total=54)
            self.assertTrue(ok, why)


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

    def test_request_windows_clustered_after_every_group_fail(self):
        # Sol r2 R2a: 3 for 3 snapshots staged after each group, but every request window
        # opened at 8.5 s — after the last key (2.0 s). The late windows cannot recover the
        # screen boundaries between groups; the guard must reject the sitting.
        groups = [[0.0], [1.0], [2.0]]
        bursts = [{"request_s": 8.5, "elapsed_s": 9.3}, {"request_s": 8.6, "elapsed_s": 9.4},
                  {"request_s": 8.7, "elapsed_s": 9.5}]
        ok, why = self.sk.check_request_windows(groups, bursts, 0.0, 0.05)
        self.assertFalse(ok)
        self.assertIn("after group 1 had ended", why)

    def test_request_windows_interleaved_with_their_groups_pass(self):
        # the pipeline's timing at the reproduction's 0.527 s spacing: group 0's request
        # opens just after group 1's only key arrived, group 1's after group 2's, and the
        # last group's after its defer
        groups = [[0.0], [0.527], [1.054]]
        bursts = [{"request_s": 0.53, "elapsed_s": 1.2}, {"request_s": 1.06, "elapsed_s": 1.8},
                  {"request_s": 1.654, "elapsed_s": 2.4}]
        ok, _ = self.sk.check_request_windows(groups, bursts, 0.0, 0.05)
        self.assertTrue(ok)

    def test_a_request_window_opened_before_its_group_fails(self):
        groups = [[1.0], [2.0]]
        bursts = [{"request_s": 0.9, "elapsed_s": 1.7}, {"request_s": 2.5, "elapsed_s": 3.3}]
        ok, why = self.sk.check_request_windows(groups, bursts, 0.0, 0.05)
        self.assertFalse(ok)
        self.assertIn("before the group's last key", why)

    def test_unmapped_presses_fail_the_coverage_guard(self):
        # Sol r2 R2b/R2c: the pre-fix clean sitting exited 0 with '10 for 10 key group(s)'
        # while 6 of 10 presses were unmapped; the guard must reject that and exit 1
        ok, why = self.sk.check_mapped({"summary": "screens: 2, transitions: 4, keys: 10",
                                        "unmapped_keys": 6})
        self.assertFalse(ok)
        self.assertIn("6 unmapped presses", why)
        ok, _ = self.sk.check_mapped({"summary": "screens: 11, transitions: 10, keys: 10",
                                      "unmapped_keys": 0})
        self.assertTrue(ok)

    @unittest.skipIf(os.environ.get("MUTATION_SWEEP"),
                     "heavy end-to-end scripted sitting; run once in the full suite, skipped per-mutation")
    def test_scripted_sitting_produces_one_burst_snapshot_per_key_group(self):
        # R3(b)/R2(c) end to end: scripted_keys.py with N keys at the 0.5-1.5 s human pace must
        # produce N distinct burst snapshots in the index (the pre-fix recorder merged ten groups
        # into four and the `any` guard still exited 0). Skipped during the mutation sweep so the
        # sweep stays fast; the full suite runs it once.
        before = set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()
        session = None
        try:
            r = subprocess.run([sys.executable,
                                str(ROOT / "experiments/E015-human-playthrough/scripted_keys.py"),
                                "--keys", "a;b;c;d;e", "--gap-min", "0.7", "--gap-max", "0.7",
                                "--seed", "34"],
                               capture_output=True, text=True, timeout=240)
            self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-4000:])
            fresh = (set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()) - before
            self.assertEqual(len(fresh), 1, fresh)
            session = fresh.pop()
            index = [json.loads(line) for line in (session / "index.jsonl").read_text().splitlines()]
            bursts = [e for e in index if e["origin"] == "burst"]
            self.assertEqual(len(bursts), 5, bursts)
        finally:
            if session is not None:
                shutil.rmtree(session, ignore_errors=True)


def slow_start_dosbox(tmp, delay_s):
    """An environment whose emulator is frozen for `delay_s` seconds right after its window
    appears (issue #141): a wrapper for the real dosbox-x that answers `-version` at once, so the
    version check passes, then execs the real emulator (same pid, so the recorder's window bind
    holds) with a background helper that SIGSTOPs that pid when its window exists and SIGCONTs it
    `delay_s` later. That is how a loaded CI runner looks to the recorder (the window is up but
    keys are not read yet), made deterministic. Selected through $DOSBOX_X, which
    driver.dosbox_x() reads; no production code changes."""
    sys.path.insert(0, str(ROOT / "runtime" / "driver"))
    import driver
    real = driver.dosbox_x()
    wrapper = Path(tmp) / "dosbox-x-slow"
    wrapper.write_text("#!/bin/sh\n"
                       f'case "$1" in -version) exec "{real}" "$@";; esac\n'
                       "pid=$$\n"
                       "(\n"
                       "  n=0\n"
                       '  while [ $n -lt 300 ]; do\n'
                       '    for w in $(xdotool search --class dosbox 2>/dev/null); do\n'
                       '      if [ "$(xdotool getwindowpid $w 2>/dev/null)" = "$pid" ]; then\n'
                       '        kill -STOP $pid; sleep %s; kill -CONT $pid; exit 0\n'
                       "      fi\n"
                       "    done\n"
                       "    n=$((n+1)); sleep 0.02\n"
                       "  done\n"
                       ") >/dev/null 2>&1 &\n"
                       f'exec "{real}" "$@"\n' % delay_s)
    wrapper.chmod(0o755)
    return dict(os.environ, DOSBOX_X=str(wrapper))


class EarlySaveTests(unittest.TestCase):
    """Sol's round-3 R1 on PR 112: a save the running emulator writes before the Watcher exists
    must be counted, so the acceptance guard sees it as a save before the first request (owned by
    no line) and refuses the sitting. Before the fix the write watch started with the Watcher, the
    early save was uncounted, and the sitting exited 0."""

    @unittest.skipIf(os.environ.get("MUTATION_SWEEP"),
                     "heavy end-to-end scripted sitting; run once in the full suite and by the sweep's heavy mutations")
    def test_a_save_before_the_watcher_is_refused(self):
        before = set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                # [designed] 6 s: longer than the hook's first wait, so a hook that does not wait
                # for the write fails every time; a loaded runner is slow by seconds, not minutes
                env = dict(slow_start_dosbox(tmp, 6), GOAL2_RECORDER_TEST_EARLY_SAVE="1")
                r = subprocess.run([sys.executable,
                                    str(ROOT / "experiments/E015-human-playthrough/scripted_keys.py"),
                                    "--sleep", "2", "--keys", "a;b;c", "--seed", "34"],
                                   env=env, capture_output=True, text=True, timeout=240)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 1, out[-4000:])
            self.assertIn("a save before the first request is owned by no request line", out)
            fresh = (set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()) - before
            self.assertEqual(len(fresh), 1, fresh)
            meta = json.loads((next(iter(fresh)) / "meta.json").read_text())
            self.assertGreaterEqual(meta["write_events_total"], 1, meta)
        finally:
            fresh = (set(rec.SESSIONS.glob("*")) if rec.SESSIONS.is_dir() else set()) - before
            for session in fresh:
                shutil.rmtree(session, ignore_errors=True)


class ReproductionWrapperTests(unittest.TestCase):
    """T35 (issue #111): the two Sol delta r4 reproductions are commands, and the wrapper
    compares their exit — exit 1 means the recorder (R1) or the acceptance guard (R2) rejected
    the bypass, anything else means the bypass sailed through. Both commands exited 0 on the
    tree they were written against (evidence/E015/T35-r*/pre-fix-*.log): the r4-R1 fresh-arrival
    path staged a later request's bytes under the earlier request's window, and all four
    acceptance checks were green on those bytes."""

    def _run(self, *args):
        tmp = ROOT / "scratch" / "t34-tmp"
        tmp.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(tmp))
        return subprocess.run(
            [sys.executable,
             str(ROOT / "experiments" / "E015-human-playthrough" / "mutate_keys.py"), *args],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)

    def test_the_r4_r1_reproduction_is_refused(self):
        r = self._run("--r4-r1", "--clock", "injected", "--_submitted=2", "--_finished=0",
                      "--keys", "a;b;c")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out[-4000:])
        self.assertIn("stability fallback", out)

    def test_the_r4_r2_reproduction_is_refused(self):
        r = self._run("--r4-r2", "--bracket", "--later-bytes", "--keys", "a;b;c")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out[-4000:])
        self.assertIn("evidence-free", out)

    def test_the_matching_window_reproduction_is_refused(self):
        # Sol's R1 on PR 112 (round 2): the later bytes with the snapshot claiming the burst
        # request's own window, which the round-2 guard certified
        r = self._run("--r4-r2", "--bracket", "--later-bytes", "--matching-window", "--keys", "a;b;c")
        out = r.stdout + r.stderr
        self.assertEqual(r.returncode, 1, out[-4000:])
        self.assertIn("a save no request line owns", out)


class OneSaveInFlightTests(unittest.TestCase):
    """T44 (issue #128): the owner's first sitting on the new machine sent 537 save requests and 313
    were superseded: the median gap between requests (0.15 s) was shorter than one DOSBox-X save
    (about 0.8 s), so later saves overwrote earlier ones. The watcher keeps one save request in
    flight (`_submitted == _finished` read before every send); the key groups that settle while
    it is written wait, and ONE request answers them all (option A: its snapshot is the screen
    after the last group, the earlier groups' screens are not captured)."""

    def _sitting(self, save_s, arrivals, quit_after):
        from tests import test_human_record as fixture
        session = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, session, ignore_errors=True)
        (session / "snapshots").mkdir()
        live = session / "state.sav"
        live.write_bytes(fixture.tiny_zip(b"vga-0"))
        writes = queue.Queue()

        def serve_writes():
            # [designed] a serialized stand-in for DOSBox-X's savestate writer: each request is
            # answered `save_s` later with one fresh atomic write (a new inode)
            while True:
                item = writes.get()
                if item is None:
                    return
                time.sleep(save_s)
                tmp = live.with_name(live.name + ".tmp")
                tmp.write_bytes(fixture.tiny_zip(f"vga-{item}".encode()))
                tmp.replace(live)

        threading.Thread(target=serve_writes, daemon=True).start()
        counter, in_flight = [0], []

        def xrun(argv):
            # a request is being SENT: the previous ones' jobs must all have finished
            in_flight.append(w._submitted - w._finished)
            time.sleep(0.03)
            counter[0] += 1
            writes.put(counter[0])

        w = rec.Watcher(session, live, "77", fixture.FakeDbx(), {"DISPLAY": ":0"},
                        xrun=xrun, alive=lambda: True, log=lambda m: None)

        class FakeKeys:
            error = None
            proc = types.SimpleNamespace(poll=lambda: None)

            def __init__(self):
                self.events = []
                for k, t in enumerate(arrivals):
                    self.events.append({"monotonic_s": w.t0 + t, "event": "press",
                                        "keysym": f"k{k}"})
                    self.events.append({"monotonic_s": w.t0 + t + 0.012, "event": "release",
                                        "keysym": f"k{k}"})
                self.i = 0

            def drain(self):
                now = time.monotonic()
                out = []
                while self.i < len(self.events) and self.events[self.i]["monotonic_s"] <= now:
                    out.append(self.events[self.i])
                    self.i += 1
                return out

        keys = FakeKeys()
        w.run(quit_after=quit_after, keys=keys)
        writes.put(None)
        index = [json.loads(line) for line in (session / "index.jsonl").read_text().splitlines()]
        requests = [json.loads(line) for line in
                    (session / "requests.jsonl").read_text().splitlines()]
        return w, keys.events, index, requests, in_flight

    def _scroll(self, gap_s):
        import scripted_keys
        arrivals = [0.3 + gap_s * k for k in range(int(6 / gap_s))]     # keys for 6 s
        w, events, index, requests, in_flight = self._sitting(0.8, arrivals, quit_after=9)
        self.assertGreaterEqual(len(in_flight), 2, in_flight)
        self.assertEqual(max(in_flight), 0, f"requests sent with others in flight: {in_flight}")
        self.assertEqual([r for r in requests if r.get("superseded")], [])
        self.assertEqual([r["seq"] is None for r in requests], [False] * len(requests))
        bursts = [e for e in index if e["origin"] == "burst"]
        groups = scripted_keys.group_presses(events, rec.BURST_QUIET_S)
        ok, why = scripted_keys.check_bursts(groups, bursts, w.t0, requests=requests)
        self.assertTrue(ok, why)
        ok, why = scripted_keys.check_request_windows(groups, bursts, w.t0, rec.CAPTURE_MARGIN_S,
                                                      requests=requests)
        self.assertTrue(ok, why)
        merged = sum(r["merge"]["size"] - 1 for r in requests if r.get("merge"))
        print(f"\nT44 scroll, keys every {gap_s} s: {len(requests)} requests, {len(bursts)} burst "
              f"snapshots for {len(groups)} key group(s), merged (not captured) groups: {merged}")
        return requests

    def test_a_scroll_faster_than_the_save_keeps_one_request_in_flight(self):
        # DW1: keys every 0.15 s for 6 s against a save of 0.8 s. The stream never settles
        # (EVENT_SETTLE_S), so the scroll is one episode and one request follows it
        self._scroll(0.15)

    def test_requests_between_keys_wait_for_the_one_in_flight(self):
        # keys every 0.4 s (each settles, so each wants a request) against a save of 0.8 s:
        # without the gate a request goes out every 0.4 s and they overwrite one another
        requests = self._scroll(0.4)
        self.assertGreater(len([r for r in requests if r["origin"] == "burst"]), 3)

    def test_groups_that_settle_in_flight_wait_and_go_out_in_one_request(self):
        import keymap
        import scripted_keys
        # a 2 s save (the opening request ends at ~2.05 s); keys 0.7 s apart: k0 starts a
        # request, k1..k3 settle as groups of their own (gaps over the 0.5 s quiet) while it is
        # written
        arrivals = [2.3, 3.0, 3.7, 4.3, 8.0]
        w, events, index, requests, in_flight = self._sitting(2.0, arrivals, quit_after=14)
        self.assertEqual(max(in_flight), 0, in_flight)
        self.assertEqual([r for r in requests if r.get("superseded")], [])
        bursts = [r for r in requests if r["origin"] == "burst"]
        self.assertEqual([r["merge"]["size"] for r in bursts], [1, 3, 1], bursts)
        merged = bursts[1]["merge"]
        # the marker names the merge: size 3, the last group claimed, the groups' last keys
        self.assertEqual(merged["claimed"], 3)
        self.assertEqual(len(merged["group_last_s"]), 3)
        self.assertAlmostEqual(merged["group_last_s"][-1], 4.312, delta=0.05)
        groups = scripted_keys.group_presses(events, rec.BURST_QUIET_S)
        self.assertEqual(len(groups), 5)
        bursts_idx = [e for e in index if e["origin"] == "burst"]
        ok, why = scripted_keys.check_bursts(groups, bursts_idx, w.t0, requests=requests)
        self.assertTrue(ok, why)
        self.assertIn("2 not captured by merging", why)
        ok, why = scripted_keys.check_request_windows(groups, bursts_idx, w.t0,
                                                      rec.CAPTURE_MARGIN_S, requests=requests)
        self.assertTrue(ok, why)
        # option A in the map: the earlier two groups are listed as not captured with their
        # keys, the third is claimed (screen after only), nothing is unmapped
        states = [{"entry": e, "screen_text": f"SCREEN-{e['seq']}", "error": None} for e in index]
        result = keymap.build_map(states, events, w.t0, requests=requests)
        self.assertEqual(result["not_captured"], [{"keys": ["k1"]}, {"keys": ["k2"]}])
        self.assertEqual([g["keys"] for g in result["merged_claimed"]], [["k3"]])
        self.assertEqual(result["unmapped_keys"], 0)
        self.assertEqual([r["keys"] for r in result["transitions"]], [["k0"], ["k4"]])
        ok, why = scripted_keys.check_mapped(result)
        self.assertTrue(ok, why)

    def test_a_cadence_tick_due_in_flight_is_sent_after_it_once(self):
        # the first request is in flight from 0 s to 45 s, over two cadence periods (CADENCE_S
        # ticks at 20 s and 40 s fall inside it): neither is dropped (a tick goes out the moment
        # the request finishes, at 45 s) and they are not doubled (one tick for both, the next
        # at the grid's 60 s)
        now = [0.0]
        flight_ends = [0.0]
        watcher = rec.Watcher.__new__(rec.Watcher)
        watcher.clock = lambda: now[0]
        watcher.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
        watcher.t0 = 0.0
        watcher.dbx = Mock()
        watcher.dbx.poll.return_value = None
        watcher.log = lambda msg: None
        watcher.request_in_flight = lambda: now[0] < flight_ends[0]
        ticks = []

        def tick(**kw):
            ticks.append(round(now[0], 2))
            flight_ends[0] = now[0] + (45.0 if len(ticks) == 1 else 0.5)
        watcher.tick = tick
        keys = Mock()
        keys.error = None
        keys.proc.poll.return_value = None
        keys.drain = lambda: []
        watcher.run(quit_after=70, keys=keys)
        self.assertEqual(ticks[0], 0.0)
        self.assertAlmostEqual(ticks[1], 45.0, delta=0.05)
        self.assertAlmostEqual(ticks[2], 60.0, delta=0.05)
        self.assertEqual(len(ticks), 3, ticks)

    def test_the_resume_request_waits_for_the_request_in_flight(self):
        now = [0.0]
        watcher = rec.Watcher.__new__(rec.Watcher)
        watcher.clock = lambda: now[0]
        watcher.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
        watcher.t0 = 0.0
        watcher.dbx = Mock()
        watcher.dbx.poll.return_value = None
        watcher.log = lambda msg: None
        watcher.resume_due = True
        watcher.request_in_flight = lambda: now[0] < 3.0
        ticks = []
        watcher.tick = lambda **kw: ticks.append((round(now[0], 2), kw.get("origin", "watcher")))
        keys = Mock()
        keys.error = None
        keys.proc.poll.return_value = None
        keys.drain = lambda: []
        watcher.run(quit_after=5, keys=keys)
        self.assertEqual(ticks[0][1], "resume", ticks)
        self.assertGreaterEqual(ticks[0][0], 3.0, ticks)

    def _loop_with_keys(self, presses):
        now = [0.0]
        watcher = rec.Watcher.__new__(rec.Watcher)
        watcher.clock = lambda: now[0]
        watcher.sleep = lambda secs: now.__setitem__(0, now[0] + secs)
        watcher.t0 = 0.0
        watcher.dbx = Mock()
        watcher.dbx.poll.return_value = None
        watcher.log = lambda msg: None
        ticks = []
        watcher.tick = lambda **kw: ticks.append((round(now[0], 2), kw.get("origin", "watcher")))
        keys = Mock()
        keys.error = None
        keys.proc.poll.return_value = None
        sent = [0]

        def drain():
            out = []
            while sent[0] < len(presses) and presses[sent[0]] <= now[0]:
                out.append({"monotonic_s": presses[sent[0]], "event": "press", "keysym": "Down"})
                sent[0] += 1
            return out
        keys.drain = drain
        watcher.run(quit_after=8, keys=keys)
        return [t for t in ticks if t[1] == "burst"]

    def test_a_fast_run_of_keys_gets_its_one_request_after_the_run(self):
        # 30 presses 0.1 s apart (1.0 s .. 3.9 s): each less than EVENT_SETTLE_S after the
        # previous, so no request is tried between them (it could not fit: a request window
        # is ~0.075 s and the next key is 0.1 s away); the run's one request follows its last
        # key by EVENT_SETTLE_S
        presses = [1.0 + 0.1 * k for k in range(30)]
        bursts = self._loop_with_keys(presses)
        self.assertEqual(len(bursts), 1, bursts)
        self.assertAlmostEqual(bursts[0][0], presses[-1] + rec.EVENT_SETTLE_S, delta=0.03)

    def test_keys_spaced_over_the_settle_get_one_request_each(self):
        # 0.527 s apart (the T34 reproduction): each key's request at the settle, one each
        presses = [1.0 + 0.527 * k for k in range(4)]
        bursts = self._loop_with_keys(presses)
        self.assertEqual(len(bursts), 4, bursts)
        for (at, _), pressed, following in zip(bursts, presses, presses[1:] + [float("inf")]):
            self.assertAlmostEqual(at, pressed + rec.EVENT_SETTLE_S, delta=0.03)
            # the T34 edge at the settle of T44 (0.25 s): the whole request window (send ~0.03 s
            # + CAPTURE_MARGIN_S) closes before the next key, so each key keeps its own window
            self.assertLess(at + 0.03 + rec.CAPTURE_MARGIN_S, following)


class MergedMapTests(unittest.TestCase):
    """T44: a gap with several bursts is a merge only when the closing request's marker says so."""

    def _states(self):
        return [{"entry": {"seq": i, "request_s": r, "sent_s": r + 0.03, "elapsed_s": r + 1.0},
                 "screen_text": f"S{i}", "error": None} for i, r in ((1, 0.0), (2, 10.0))]

    def _events(self):
        return [{"monotonic_s": t, "event": "press", "keysym": k}
                for t, k in ((2.0, "a"), (3.0, "b"), (4.0, "c"))]

    def test_without_a_marker_two_bursts_in_a_gap_stay_unmapped(self):
        import keymap
        r = keymap.build_map(self._states(), self._events(), 0.0, quiet=0.5, margin=0.05)
        self.assertEqual((r["unmapped_keys"], r["not_captured"]), (3, []))

    def test_a_marker_smaller_than_the_bursts_excuses_nothing(self):
        import keymap
        lines = [{"request_s": 10.0, "seq": 2, "merge": {"size": 2, "claimed": 2}}]
        r = keymap.build_map(self._states(), self._events(), 0.0, quiet=0.5, margin=0.05,
                             requests=lines)
        self.assertEqual((r["unmapped_keys"], r["not_captured"]), (3, []))

    def test_a_marker_naming_the_merge_lists_the_earlier_groups(self):
        import keymap
        lines = [{"request_s": 10.0, "seq": 2, "merge": {"size": 3, "claimed": 3}}]
        r = keymap.build_map(self._states(), self._events(), 0.0, quiet=0.5, margin=0.05,
                             requests=lines)
        self.assertEqual(r["unmapped_keys"], 0)
        self.assertEqual(r["not_captured"], [{"keys": ["a"]}, {"keys": ["b"]}])
        self.assertEqual([g["keys"] for g in r["merged_claimed"]], [["c"]])
        self.assertIn("not captured groups: 2", r["summary"])
