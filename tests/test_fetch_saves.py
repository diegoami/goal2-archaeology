"""The owner's saved games are fetched by hash from release `goal2-saves` before a sitting.

A missing or changed save is downloaded (only that one, unless --refresh); a download that
produces wrong bytes fails; a verified cache is never downloaded again; the recorder fetches
before every sitting, warns (and goes on) when the download cannot run, and falls back to a
fetched save when no earlier session has one."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "runtime" / "human"))

from tools import fetch_saves  # noqa: E402
import recorder as rec  # noqa: E402

GOOD = b"a saved game"


def entry(name="2B.GL", data=GOOD):
    return {"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


class FetchSaves(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name) / "saves"
        self.calls = []
        patches = [
            mock.patch.object(fetch_saves, "manifest", return_value={
                "release": "goal2-saves", "saves": [entry(), entry("3.GL", b"other")]}),
            mock.patch.object(fetch_saves.subprocess, "run", self.fake_gh),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.served = {"2B.GL": GOOD, "3.GL": b"other"}

    def fake_gh(self, cmd, **kw):
        self.calls.append(cmd)
        name = cmd[cmd.index("-p") + 1]
        (Path(cmd[cmd.index("-D") + 1]) / name).write_bytes(self.served[name])
        return subprocess.CompletedProcess(cmd, 0, "", "")

    def test_a_missing_save_is_downloaded_and_verified(self):
        fetch_saves.fetch(cache=self.cache)
        self.assertEqual((self.cache / "2B.GL").read_bytes(), GOOD)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(self.calls[0][:3], ["gh", "release", "download"])
        self.assertIn("goal2-saves", self.calls[0])

    def test_a_verified_cache_is_not_downloaded_again(self):
        fetch_saves.fetch(cache=self.cache)
        self.calls.clear()
        fetch_saves.fetch(cache=self.cache)
        self.assertEqual(self.calls, [])

    def test_only_the_bad_save_is_downloaded_again(self):
        fetch_saves.fetch(cache=self.cache)
        self.calls.clear()
        (self.cache / "3.GL").write_bytes(b"changed")
        fetch_saves.fetch(cache=self.cache)
        self.assertEqual([c[c.index("-p") + 1] for c in self.calls], ["3.GL"])

    def test_refresh_downloads_every_save(self):
        fetch_saves.fetch(cache=self.cache)
        self.calls.clear()
        fetch_saves.fetch(cache=self.cache, refresh=True)
        self.assertEqual(len(self.calls), 2)

    def test_wrong_bytes_from_the_release_fail(self):
        self.served["2B.GL"] = b"tampered!!!!"
        with self.assertRaises(SystemExit) as cm:
            fetch_saves.fetch(cache=self.cache)
        self.assertIn("2B.GL", str(cm.exception))

    def test_check_reports_a_missing_save(self):
        problems = fetch_saves.verify(self.cache)
        self.assertEqual(len(problems), 2)
        self.assertIn("missing", problems[0])

    def test_the_real_manifest_lists_2b_with_its_hash(self):
        mock.patch.stopall()
        data = json.loads((REPO_ROOT / "artifacts" / "saves.json").read_text())
        two_b = [e for e in data["saves"] if e["path"] == "2B.GL"][0]
        self.assertEqual((data["release"], two_b["bytes"]), ("goal2-saves", 169553))
        self.assertEqual(two_b["sha256"],
                         "e35ec7edc8f7bdc8409dce9ad6e0df3b1c663fc36d5a0848fbda89e6844b9dd7")


class RecorderFetches(unittest.TestCase):
    def test_a_download_that_cannot_run_warns_and_goes_on(self):
        err = subprocess.CalledProcessError(1, "gh", stderr="no network")
        with mock.patch.object(rec.fetch_saves, "fetch", side_effect=err), \
                mock.patch.object(rec.fetch_saves, "verify", return_value=["2B.GL: missing"]):
            got = rec.fetch_saves_or_warn()
        self.assertEqual((got["fetched"], got["problem"]), (False, "no network"))

    def test_a_hash_mismatch_stops_the_sitting(self):
        with mock.patch.object(rec.fetch_saves, "fetch", side_effect=SystemExit("2B.GL: sha256")):
            with self.assertRaises(SystemExit):
                rec.fetch_saves_or_warn()

    def test_new_session_fetches_before_it_places_a_save(self):
        order = []
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            with mock.patch.object(rec, "SESSIONS", base), \
                    mock.patch.object(rec, "verify_release_or_die"), \
                    mock.patch.object(rec, "fetch_saves_or_warn",
                                      side_effect=lambda: order.append("fetch") or {"fetched": True}), \
                    mock.patch.object(rec, "place_saved_game",
                                      side_effect=lambda *a, **k: order.append("place") or {}), \
                    mock.patch.object(rec.shutil, "copytree", lambda s, d: Path(d).mkdir()), \
                    mock.patch.object(rec, "dosbox_version", return_value="x"):
                _, meta = rec.new_session()
        self.assertEqual(order, ["fetch", "place"])
        self.assertEqual(meta["saves"], {"fetched": True})

    def test_with_no_earlier_session_the_fetched_save_is_placed(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            cache = base / "cache"
            cache.mkdir()
            (cache / "2B.GL").write_bytes(GOOD)
            session = base / "sessions" / "20261014-100000"
            (session / "game").mkdir(parents=True)
            with mock.patch.object(rec.fetch_saves, "CACHE", cache):
                load = rec.place_saved_game(session)
            self.assertEqual((session / "game" / "2B.GL").read_bytes(), GOOD)
            self.assertIn("fetched saves", load["chosen"])

    def test_an_earlier_session_save_wins_over_the_fetched_one(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            cache = base / "cache"
            cache.mkdir()
            (cache / "2B.GL").write_bytes(GOOD)
            (base / "sessions" / "20261014-090000" / "game").mkdir(parents=True)
            (base / "sessions" / "20261014-090000" / "game" / "1.GL").write_bytes(b"mine")
            session = base / "sessions" / "20261014-100000"
            (session / "game").mkdir(parents=True)
            with mock.patch.object(rec.fetch_saves, "CACHE", cache):
                rec.place_saved_game(session)
            self.assertEqual((session / "game" / "1.GL").read_bytes(), b"mine")


if __name__ == "__main__":
    unittest.main()
