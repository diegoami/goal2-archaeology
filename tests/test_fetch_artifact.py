"""The artifact is fetched by hash from the release, and a changed byte fails verification (DW1).

A missing file and a wrong byte count are reported; files come from release `goal2-original` of
this repository, downloaded only when the cache does not verify, and never under `--check`."""
from __future__ import annotations

import contextlib
import io
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import fetch_artifact  # noqa: E402
from tests import netskip  # noqa: E402

SET_ID = "goal2-a949da2f"
# The real set, fetched from the release when the cache lacks it (#236).
needs_release = netskip.needs(f"release set {SET_ID}", lambda: fetch_artifact.fetch(SET_ID))

# A fake `gh` serving `release download` from FAKE_GH_RELEASE; every call is logged to FAKE_GH_LOG.
FAKE_GH = """#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\\n")
if args[:2] != ["release", "download"]:
    sys.exit(2)
if os.environ.get("FAKE_GH_FAIL"):
    sys.exit(1)
name = args[args.index("-p") + 1]
dest = Path(args[args.index("-D") + 1])
dest.mkdir(parents=True, exist_ok=True)
shutil.copy(Path(os.environ["FAKE_GH_RELEASE"]) / name, dest / name)
"""


class FakeReleaseTest(unittest.TestCase):
    """Each test gets an empty cache and a fake `gh` serving the verified set as the release."""

    @needs_release
    def setUp(self):
        self.release = fetch_artifact.fetch(SET_ID)
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        fakebin = tmp / "bin"
        fakebin.mkdir()
        (fakebin / "gh").write_text(FAKE_GH, encoding="utf-8")
        (fakebin / "gh").chmod(0o755)
        self.log = tmp / "gh.log"
        self.log.touch()
        self.cache = tmp / "cache"
        for patch in (
                mock.patch.object(fetch_artifact, "CACHE", self.cache),
                mock.patch.dict(os.environ, {
                    "PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
                    "FAKE_GH_LOG": str(self.log),
                    "FAKE_GH_RELEASE": str(self.release)})):
            patch.start()
            self.addCleanup(patch.stop)

    def calls(self) -> list[list[str]]:
        return [shlex.split(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def files(self) -> list[dict]:
        return fetch_artifact.sets()[SET_ID]["files"]

    def test_download_takes_every_file_from_the_release(self):
        dest = fetch_artifact.download(SET_ID)
        self.assertEqual(self.cache / SET_ID, dest)
        self.assertEqual(
            [["release", "download", "goal2-original", "--repo", "diegoami/goal2-archaeology",
              "-p", entry["path"], "-D", str(dest), "--clobber"] for entry in self.files()],
            self.calls())
        self.assertEqual([], fetch_artifact.verify(SET_ID))

    def test_fetch_downloads_only_when_the_cache_does_not_verify(self):
        self.assertEqual(self.cache / SET_ID, fetch_artifact.fetch(SET_ID))
        self.assertEqual(len(self.files()), len(self.calls()))
        fetch_artifact.fetch(SET_ID)
        self.assertEqual(len(self.files()), len(self.calls()))

    def test_check_never_downloads(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(1, fetch_artifact.main([SET_ID, "--check"]))
        self.assertIn("missing from", out.getvalue())
        self.assertEqual([], self.calls())
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(0, fetch_artifact.main([SET_ID]))
        self.assertIn(f"{SET_ID}: verified", out.getvalue())
        self.assertEqual(len(self.files()), len(self.calls()))

    def test_fetch_exits_when_the_download_does_not_verify(self):
        # The release serves the first file with one byte changed: fetch must not return the set.
        corrupt = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, corrupt, True)
        for path in self.release.iterdir():
            shutil.copy(path, corrupt / path.name)
        first = corrupt / self.files()[0]["path"]
        changed = bytearray(first.read_bytes())
        changed[0] ^= 0xFF
        first.write_bytes(bytes(changed))
        with mock.patch.dict(os.environ, {"FAKE_GH_RELEASE": str(corrupt)}):
            with self.assertRaises(SystemExit) as raised:
                fetch_artifact.fetch(SET_ID)
        self.assertIn(f"{self.files()[0]['path']}: sha256", str(raised.exception))

    def test_download_of_an_unknown_set_exits_naming_it(self):
        with self.assertRaises(SystemExit) as raised:
            fetch_artifact.download("no-such-set-00000000")
        self.assertIn("no-such-set-00000000: unknown artifact set", str(raised.exception))
        self.assertEqual([], self.calls())

    def test_failing_gh_and_https_stop_the_download(self):
        with mock.patch.dict(os.environ, {"FAKE_GH_FAIL": "1"}), \
                mock.patch.object(fetch_artifact, "https_download", return_value=False) as https:
            with self.assertRaises(subprocess.CalledProcessError):
                fetch_artifact.download(SET_ID)
        self.assertEqual(1, len(self.calls()))
        self.assertEqual(1, https.call_count)

    def test_failing_gh_falls_back_to_https_and_verifies(self):
        # [designed: owner, 2026-10-21] a cloud proxy blocks gh's GraphQL: each file then comes over
        # HTTPS from the public release, and the same sha256 check applies.
        def served(repo, tag, name, dest):
            (dest / name).write_bytes((self.release / name).read_bytes())
            return True
        with mock.patch.dict(os.environ, {"FAKE_GH_FAIL": "1"}), \
                mock.patch.object(fetch_artifact, "https_download", side_effect=served) as https:
            fetch_artifact.download(SET_ID)
        self.assertEqual(len(self.files()), https.call_count)
        self.assertEqual([], fetch_artifact.verify(SET_ID))

    def test_missing_file_is_reported(self):
        fetch_artifact.download(SET_ID)
        first = self.files()[0]["path"]
        (self.cache / SET_ID / first).unlink()
        self.assertEqual([f"{first}: missing from {self.cache / SET_ID}"],
                         fetch_artifact.verify(SET_ID))

    def test_wrong_byte_count_is_reported(self):
        fetch_artifact.download(SET_ID)
        entry = self.files()[0]
        with (self.cache / SET_ID / entry["path"]).open("ab") as handle:
            handle.write(b"\0")
        problems = fetch_artifact.verify(SET_ID)
        self.assertIn(f"{entry['path']}: {entry['bytes'] + 1} bytes, known.json says {entry['bytes']}",
                      problems)


@needs_release
class FetchArtifactTest(unittest.TestCase):
    def test_set_verifies_against_known_json(self):
        fetch_artifact.fetch(SET_ID)
        self.assertEqual([], fetch_artifact.verify(SET_ID))

    def test_cli_exits_1_when_one_byte_is_flipped(self):
        artifact = fetch_artifact.fetch(SET_ID) / fetch_artifact.sets()[SET_ID]["files"][0]["path"]
        original = artifact.read_bytes()
        try:
            changed = bytearray(original)
            changed[0] ^= 0xFF
            artifact.write_bytes(bytes(changed))
            result = subprocess.run(
                [sys.executable, "tools/fetch_artifact.py", SET_ID, "--check"],
                cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        finally:
            artifact.write_bytes(original)
        self.assertEqual([], fetch_artifact.verify(SET_ID))

    def test_unknown_set_is_reported(self):
        self.assertTrue(fetch_artifact.verify("no-such-set-00000000"))


if __name__ == "__main__":
    unittest.main()
