"""T34 nested-display recorder tests."""
import importlib.util
import unittest
import tempfile
import subprocess
import os
import time
import json
from pathlib import Path
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location("human_recorder", Path(__file__).resolve().parents[1] / "runtime/human/recorder.py")
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)


class NestedDisplayTests(unittest.TestCase):
    def test_try_start_skips_busy_number_and_changes_only_child_display(self):
        busy, free = Mock(), Mock()
        busy.poll.return_value = 1
        free.poll.return_value = None
        env = {"DISPLAY": ":612", "OTHER": "kept"}
        with patch.object(rec.subprocess, "Popen", side_effect=[busy, free]) as launch, patch.object(rec.time, "sleep"):
            proc, nested = rec.start_nested(env, "800x600", None)
        self.assertIs(proc, free)
        self.assertEqual(env["DISPLAY"], ":612")
        self.assertEqual(nested, {"DISPLAY": ":601", "OTHER": "kept"})
        self.assertEqual(launch.call_args_list[0].args[0], ["Xephyr", ":600", "-screen", "800x600", "-nolisten", "tcp"])
        self.assertEqual(launch.call_args_list[1].kwargs["env"], env)

    def test_self_test_requires_nested_tools(self):
        with patch.object(rec, "ensure_cache", return_value="fixture"), patch.object(rec, "dosbox_version", return_value="2024.03.01"), patch.object(rec.shutil, "which", side_effect=lambda name: None if name in ("Xephyr", "xinput") else name):
            self.assertEqual(rec.self_test(), 1)


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

    def test_private_display_logs_game_keys_not_outer_app_keys(self):
        outer = None
        nested = None
        app = None
        logger = None
        with tempfile.TemporaryDirectory() as folder:
            try:
                for number in range(710, 730):
                    outer = subprocess.Popen(["Xvfb", f":{number}", "-screen", "0", "800x600x24"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                    time.sleep(1)
                    if outer.poll() is None:
                        break
                self.assertIsNone(outer.poll())
                env = dict(os.environ, DISPLAY=f":{number}")
                nested, child = rec.start_nested(env, "640x400", subprocess.DEVNULL)
                app = subprocess.Popen(["xev", "-name", "T34-other-app"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                logger = rec.KeyLogger(child, env["DISPLAY"], Path(folder) / "keys.jsonl")
                logger.start()
                time.sleep(1)
                subprocess.run(["xdotool", "key", "a", "b"], env=child, check=True)
                wid = subprocess.check_output(["xdotool", "search", "--name", "T34-other-app"], env=env, text=True).split()[0]
                subprocess.run(["xdotool", "key", "--window", wid, "x", "y", "z"], env=env, check=True)
                time.sleep(0.5)
                logger.stop()
                events = [json.loads(line) for line in (Path(folder) / "keys.jsonl").read_text().splitlines()]
                self.assertEqual([(e["event"], e["keysym"]) for e in events], [("press", "a"), ("release", "a"), ("press", "b"), ("release", "b")])
                for e in events:
                    self.assertIsInstance(e["monotonic_s"], float)
                    self.assertIn("+00:00", e["utc"])
                    self.assertIsInstance(e["keycode"], int)
            finally:
                if logger:
                    logger.stop()
                for proc in (app, nested, outer):
                    rec.terminate(proc)


class MapTests(unittest.TestCase):
    def test_map_boundaries_order_identity_and_counts(self):
        from tests import test_human_record  # registers extract for keymap
        import keymap
        import hashlib

        def state(when, text, error=None):
            return {"entry": {"elapsed_s": when}, "screen_text": text,
                    "screen_digest": "attributes-digest", "error": error}

        def press(when, key, kind="press"):
            return {"monotonic_s": when, "event": kind, "keysym": key}

        # Deliberately shuffled inputs; snapshots at the exact input/quiet
        # boundaries distinguish strict-before from inclusive-after.
        states = [state(6.8, "LATER"), state(5.7, "TEAM"), state(1, "MENU"), state(2, "AT KEY"),
                  state(2.7, "TEAM"), state(2.3, "TOO EARLY"),
                  state(2.6, "INVALID", "bad snapshot"), state(4, "MENU")]
        events = [press(5.2, "b", "release"), press(2.2, "b", "release"),
                  press(5.1, "b"), press(2.1, "b"), press(5, "a"),
                  press(2, "a"), press(0, "unbracketed"),
                  press(9, "unbracketed"), press(8, "release-only", "release")]
        result = keymap.build_map(states, events, 0)
        self.assertEqual(result["summary"], "screens: 5, transitions: 1, keys: 6")
        self.assertEqual(result["unmapped_keys"], 2)
        self.assertEqual(result["transitions"], [{
            "screen": hashlib.sha256(b"MENU").hexdigest(), "headline": "MENU",
            "keys": ["a", "b"], "after": hashlib.sha256(b"TEAM").hexdigest(),
            "after_headline": "TEAM", "count": 2}])

    def test_literal_session_map(self):
        from tests import test_human_record as fixture
        import keymap
        with tempfile.TemporaryDirectory() as folder:
            session = Path(folder)
            chain = [({0: text}, fixture.player_array(), fixture.country_array(), fixture.state_tuple(), 0) for text in ("MENU", "TEAM", "MENU")]
            fixture.write_session(session, chain)
            meta = json.loads((session / "meta.json").read_text())
            meta["monotonic_start_s"] = 100.0
            (session / "meta.json").write_text(json.dumps(meta))
            events = [{"monotonic_s": t, "utc": "2026-10-09T00:00:00+00:00", "event": kind, "keycode": code, "keysym": sym} for t, kind, code, sym in ((121.0, "press", 38, "a"), (121.1, "release", 38, "a"), (141.0, "press", 9, "Escape"), (141.1, "release", 9, "Escape"))]
            (session / "keys.jsonl").write_text("".join(json.dumps(e) + "\n" for e in events))
            result = keymap.read_session(session)
            self.assertEqual(result["summary"], "screens: 2, transitions: 2, keys: 2")
            rows = [(r["headline"], r["keys"], r["after_headline"], r["count"]) for r in result["transitions"]]
            self.assertEqual(rows, [("MENU", ["a"], "TEAM", 1), ("TEAM", ["Escape"], "MENU", 1)])
            self.assertEqual(result["unmapped_keys"], 0)
            states = [fixture.extract.read_snapshot(session, e, [1]) for e in fixture.extract.read_index(session)[0]]
            record, _ = fixture.extract.build_record(session, states, {}, [1], session / "runs", "fixture", "2026-10-09T00:00:00Z", 0)
            self.assertEqual(json.loads(next(o["value"] for o in record["observations"] if o["field"] == "screen/key map (JSON)")), result)
