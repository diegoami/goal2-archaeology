"""T39b: the coaching kit's notes (runtime/human/note.py), live view (runtime/human/live.py) and
the extraction placing notes and pauses between the snapshots they fall between."""
import io
import json
import os
import shutil
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "human"))
sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))
from tests.test_human_record import CHAIN, write_session  # noqa: E402
import extract  # noqa: E402
import live  # noqa: E402
import note  # noqa: E402

T0 = 100.0     # the fixture sitting's monotonic start; its screens are at T0 + 19.25, 39.25, 59.25


def workdir(test, name):
    d = ROOT / "scratch" / "test_human_coach" / name
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    test.addCleanup(shutil.rmtree, d, True)
    return d


def session_with_meta(test, name):
    session = workdir(test, name)
    write_session(session, CHAIN)
    meta = json.loads((session / "meta.json").read_text())
    meta["monotonic_start_s"] = T0
    (session / "meta.json").write_text(json.dumps(meta))
    return session


def listing(folder):
    """Every path under `folder` with its size and mtime: what a read-only tool must not change."""
    return sorted((str(p.relative_to(folder)), p.stat().st_size, p.stat().st_mtime_ns)
                  for p in Path(folder).rglob("*"))


class NoteTests(unittest.TestCase):
    def test_a_note_is_appended_with_utc_and_the_monotonic_clock(self):
        session = session_with_meta(self, "note")
        note.append_note(session, "first look at the squad", clock=lambda: 130.0)
        note.append_note(session, "second: the formation", clock=lambda: 170.5)
        lines = [json.loads(x) for x in (session / "notes.jsonl").read_text().splitlines()]
        self.assertEqual([(x["monotonic_s"], x["text"]) for x in lines],
                         [(130.0, "first look at the squad"), (170.5, "second: the formation")])
        self.assertTrue(all(x["utc"].endswith("+00:00") for x in lines))

    def test_a_folder_that_is_not_a_session_is_refused(self):
        folder = workdir(self, "not-a-session")
        with self.assertRaises(SystemExit):
            note.session_dir(str(folder))
        self.assertFalse((folder / "notes.jsonl").exists())


class LiveTests(unittest.TestCase):
    def test_the_newest_screen_and_the_keys_since_the_last_call_writing_nothing_in_the_session(self):
        session = session_with_meta(self, "live")
        keys = [{"event": "press", "keysym": "Return", "monotonic_s": T0 + 5},
                {"event": "release", "keysym": "Return", "monotonic_s": T0 + 5.01},
                {"event": "press", "keysym": "Down", "monotonic_s": T0 + 25}]
        (session / "keys.jsonl").write_text("".join(json.dumps(k) + "\n" for k in keys))
        cursors = workdir(self, "live-cursors")
        before = listing(session)
        first = live.view(session, cursors=cursors)
        self.assertIn("newest snapshot: seq 3", first)
        # the fixture chain's last screen (TITLE), as CP437 text
        self.assertIn("THE international soccer management game", first)
        self.assertIn("Do you want to load a saved game? (Y/N)", first)
        self.assertIn("2 press(es)", first)
        self.assertIn("+5.0s Return +25.0s Down", first)
        # one new key, and a line still being written (no newline yet): only the complete one
        with open(session / "keys.jsonl", "a") as f:
            f.write(json.dumps({"event": "press", "keysym": "Escape", "monotonic_s": T0 + 61}) + "\n")
            f.write('{"event": "press", "keysym": "Ta')
        after_keys = listing(session)
        second = live.view(session, cursors=cursors)
        self.assertIn("1 press(es)", second)
        self.assertIn("+61.0s Escape", second)
        self.assertNotIn("Return", second)
        self.assertEqual(listing(session), after_keys)    # read-only: nothing created or changed
        self.assertEqual([p for p in before if p[0] != "keys.jsonl"],
                         [p for p in after_keys if p[0] != "keys.jsonl"])

    def test_a_paused_sitting_says_so(self):
        session = session_with_meta(self, "live-paused")
        (session / "pauses.jsonl").write_text(json.dumps({"event": "pause", "monotonic_s": T0 + 40}) + "\n")
        out = live.view(session, cursors=workdir(self, "live-paused-cursors"))
        self.assertIn("paused since +40.0s", out)


class ExtractMarksTests(unittest.TestCase):
    def extract(self, session):
        runs = workdir(self, "runs")
        with mock.patch("sys.stdout", io.StringIO()):
            self.assertEqual(extract.main([str(session), "--countries", "1", "--runs-dir", str(runs)]), 0)
        return json.loads(sorted((runs / "E015").glob("*.json"))[-1].read_text())

    def test_notes_and_pauses_land_between_the_states_they_fall_between(self):
        session = session_with_meta(self, "marks")
        note.append_note(session, "after the first screen", clock=lambda: 130.0)
        note.append_note(session, "after the last screen", clock=lambda: 170.0)
        (session / "pauses.jsonl").write_text(
            json.dumps({"event": "pause", "utc": "2026-10-07T17:00:02.500+00:00",
                        "monotonic_s": 140.0, "elapsed_s": 40.0}) + "\n"
            + json.dumps({"event": "resume", "utc": "2026-10-07T17:00:02.900+00:00",
                          "monotonic_s": 150.0, "elapsed_s": 50.0}) + "\n")
        obs = self.extract(session)["observations"]
        fields = [o["field"] for o in obs]
        saves = [i for i, f in enumerate(fields) if f.startswith("state ") and "(bytes" in f
                 and f.endswith("parsed)")]
        self.assertEqual(len(saves), 3)

        def at(fragment):
            hits = [i for i, f in enumerate(fields) if fragment in f]
            self.assertEqual(len(hits), 1, fragment)
            return hits[0]
        first = at("note (notes.jsonl line 1")
        last = at("note (notes.jsonl line 2")
        pause = at("pause of DOSBox-X (pauses.jsonl line 1")
        resume = at("resume of DOSBox-X (pauses.jsonl line 2")
        self.assertTrue(saves[0] < first < saves[1], (saves, first))
        self.assertTrue(saves[1] < pause < resume < saves[2], (saves, pause, resume))
        self.assertTrue(saves[2] < last, (saves, last))
        self.assertIn("between state 1 (snapshots/snap-0001", fields[first])
        self.assertIn("and state 2 (snapshots/snap-0002", fields[first])
        self.assertIn("and state (end)", fields[last])
        self.assertEqual(obs[first]["value"], "after the first screen")
        self.assertEqual(obs[pause]["value"], "pause")
        summary = [o["value"] for o in obs if o["field"].startswith("notes and pauses")]
        self.assertEqual(summary, ["notes: 2, pauses: 1, resumes: 1"])

    def test_without_the_monotonic_clock_a_note_is_placed_by_utc(self):
        # an index entry without a request window (a sitting before T34) has only its UTC
        session = session_with_meta(self, "marks-utc")
        index = [json.loads(x) for x in (session / "index.jsonl").read_text().splitlines()]
        for e in index:
            e.pop("request_s")
        (session / "index.jsonl").write_text("".join(json.dumps(e) + "\n" for e in index))
        (session / "notes.jsonl").write_text(json.dumps(
            {"utc": "2026-10-07T17:00:02.500+00:00", "monotonic_s": 1.0, "text": "n"}) + "\n")
        obs = self.extract(session)["observations"]
        hit = [o["field"] for o in obs if o["field"].startswith("note (")]
        self.assertEqual(len(hit), 1)
        self.assertIn("between state 2 (snapshots/snap-0002", hit[0])


if __name__ == "__main__":
    unittest.main()
