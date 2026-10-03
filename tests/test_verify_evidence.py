"""A local evidence bundle verifies by sha256 and asset name; a changed byte fails; the release is
listed once and each distinct asset downloaded once; a stale cache never stands in for this run's
download; a changed byte, a failed download and an asset absent from the release are each reported
by name (DW3, toy-archaeology#11)."""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = REPO_ROOT / "tests" / "fixtures" / "evidence"
LOCAL = EVIDENCE / "local"
BULK = REPO_ROOT / "tests" / "fixtures" / "evidence_bulk"
BULK_RELEASE = BULK / "release"
BULK_ASSETS = ("8ed3f6ad685b959e-a.bin", "f144a6907dc4284d-b.bin",
               "b9dd960c1753459a-c.bin", "4f4a9410ffcdf895-d.bin")

# A fake `gh`: one `release view` prints the fixture release's asset names; `release download`
# behaves per FAKE_GH_MODE. Every invocation is appended to FAKE_GH_LOG.
#   ok             - copy the named asset from the fixture release into the cache
#   fail           - exit 1, producing no file
#   empty          - exit 0, producing no file (a silent drop)
#   fail-with-file - copy the asset, then exit 1 (the file is there, but gh says it failed)
#   flaky          - the first download of each asset is a silent drop, the second is ok
FAKE_GH = """#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\\n")
release = Path(os.environ["FAKE_GH_RELEASE"])
mode = os.environ.get("FAKE_GH_MODE", "ok")
if args[:2] == ["release", "view"]:
    print("\\n".join(sorted(path.name for path in release.iterdir())))
    sys.exit(0)
if args[:2] == ["release", "download"]:
    asset = args[args.index("-p") + 1]
    dest = Path(args[args.index("-D") + 1])
    dest.mkdir(parents=True, exist_ok=True)
    if mode == "fail":
        sys.exit(1)
    if mode == "empty":
        sys.exit(0)
    if mode == "flaky":
        seen = Path(os.environ["FAKE_GH_LOG"] + "." + asset)
        if not seen.exists():
            seen.touch()
            sys.exit(0)
    shutil.copy(release / asset, dest / asset)
    sys.exit(1 if mode == "fail-with-file" else 0)
sys.exit(2)
"""


def cache_dir(experiment: str) -> Path:
    """The cache `verify_evidence.py` uses for an experiment."""
    return REPO_ROOT / ".cache" / "evidence" / experiment


def run_verify(local: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/verify_evidence.py", "E900",
         "--local", str(local), "--evidence-dir", str(EVIDENCE)],
        cwd=REPO_ROOT, capture_output=True, text=True)


def fake_gh(tmp: Path) -> tuple[Path, Path]:
    """A directory holding the fake `gh` and the log; return (fakebin, log)."""
    fakebin = tmp / "bin"
    fakebin.mkdir()
    log = tmp / "gh.log"
    gh = fakebin / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    return fakebin, log


def run_verify_release(fakebin: Path, log: Path, mode: str, release: Path = BULK_RELEASE,
                       experiment: str = "E901") -> subprocess.CompletedProcess:
    """Run the release verification against the fake `gh` serving `release`, in a download mode."""
    env = {
        **os.environ,
        "PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
        "FAKE_GH_LOG": str(log),
        "FAKE_GH_RELEASE": str(release),
        "FAKE_GH_MODE": mode,
    }
    return subprocess.run(
        [sys.executable, "tools/verify_evidence.py", experiment, "--evidence-dir", str(BULK)],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env)


def downloaded_assets(log: Path) -> list[str]:
    """The asset named by each `release download` call in the fake `gh` log, in order."""
    found = []
    for call in log.read_text(encoding="utf-8").splitlines():
        if call.startswith("release download"):
            words = shlex.split(call)
            found.append(words[words.index("-p") + 1])
    return found


def release_copy(tmp: Path) -> Path:
    """A writable copy of the fixture release, to corrupt or trim in one test."""
    release = tmp / "release"
    shutil.copytree(BULK_RELEASE, release)
    return release


class VerifyEvidenceTest(unittest.TestCase):
    def test_local_bundle_exits_0(self):
        result = run_verify(LOCAL)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_changed_byte_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp)
            for source in LOCAL.iterdir():
                shutil.copy(source, local / source.name)
            asset = next(local.iterdir())
            changed = bytearray(asset.read_bytes())
            changed[0] ^= 0xFF
            asset.write_bytes(bytes(changed))
            result = run_verify(local)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("sha256", result.stdout)

    def test_missing_asset_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_verify(Path(tmp))
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("c82cd5ca5a74f844-after.sav: missing from", result.stdout)

    def test_experiment_without_manifests_exits_1(self):
        result = subprocess.run(
            [sys.executable, "tools/verify_evidence.py", "E999", "--local", str(LOCAL),
             "--evidence-dir", str(EVIDENCE)],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("no manifest under", result.stdout)


class VerifyEvidenceReleaseTest(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(cache_dir("E901"), ignore_errors=True)
        self.addCleanup(shutil.rmtree, cache_dir("E901"), True)

    def test_one_listing_and_one_download_per_distinct_asset(self):
        # 3 manifests, 4 distinct assets shared between them: toy-archaeology#11.
        with tempfile.TemporaryDirectory() as tmp:
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "ok")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            calls = log.read_text(encoding="utf-8").splitlines()
            listings = [call for call in calls if call.startswith("release view")]
            downloads = [call for call in calls if call.startswith("release download")]
            self.assertLessEqual(len(listings), 1)
            self.assertLessEqual(len(downloads), 4)
            # Release E901 of this repository, by default.
            self.assertEqual(["release view E901 --repo diegoami/goal2-archaeology --json assets"
                              " -q .assets[].name"], listings)
            for call in downloads:
                self.assertTrue(call.startswith("release download E901 --repo diegoami/goal2-archaeology "
                                                "-p "), call)
                self.assertIn(f" -D {cache_dir('E901')} ", call)
            self.assertEqual(sorted(BULK_ASSETS), sorted(downloaded_assets(log)))
            self.assertIn("ok: 3 manifest(s) verified", result.stdout)

    def test_byte_flipped_in_the_release_exits_1_naming_the_asset(self):
        # The release serves c.bin with one byte changed: its sha256 no longer matches the manifests.
        with tempfile.TemporaryDirectory() as tmp:
            release = release_copy(Path(tmp))
            asset = release / "b9dd960c1753459a-c.bin"
            changed = bytearray(asset.read_bytes())
            changed[0] ^= 0xFF
            asset.write_bytes(bytes(changed))
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "ok", release)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            problems = result.stdout.splitlines()
            self.assertTrue(problems)
            for line in problems:
                self.assertIn("b9dd960c1753459a-c.bin: sha256", line)

    def test_asset_absent_from_the_release_is_reported_by_name_and_not_downloaded(self):
        # The manifests list c.bin, but the release does not have it.
        with tempfile.TemporaryDirectory() as tmp:
            release = release_copy(Path(tmp))
            (release / "b9dd960c1753459a-c.bin").unlink()
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "ok", release)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            problems = result.stdout.splitlines()
            self.assertTrue(problems)
            for line in problems:
                self.assertIn("b9dd960c1753459a-c.bin: not an asset of release E901", line)
            self.assertEqual(sorted(set(BULK_ASSETS) - {"b9dd960c1753459a-c.bin"}),
                             sorted(downloaded_assets(log)))


class VerifyEvidenceDownloadTest(unittest.TestCase):
    """A download must produce this run's file; the cache is never a substitute (toy-archaeology#11)."""

    def setUp(self):
        shutil.rmtree(cache_dir("E901"), ignore_errors=True)
        self.addCleanup(shutil.rmtree, cache_dir("E901"), True)

    def test_cold_cache_silent_drop_is_retried_and_reported_by_name(self):
        # No cache, and every download exits 0 producing nothing: each distinct asset is attempted
        # once and retried once, then reported by name.
        with tempfile.TemporaryDirectory() as tmp:
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "empty")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual(sorted(BULK_ASSETS * 2), sorted(downloaded_assets(log)))
            for asset in BULK_ASSETS:
                self.assertIn(f"{asset}: download failed", result.stdout)

    def test_cold_cache_silent_drop_recovered_by_the_retry_exits_0(self):
        # Every first download drops its file silently; the retry brings it, so nothing is reported.
        with tempfile.TemporaryDirectory() as tmp:
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "flaky")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertEqual(sorted(BULK_ASSETS * 2), sorted(downloaded_assets(log)))

    def test_download_exiting_1_is_a_failure_even_when_it_leaves_a_file(self):
        # gh writes a correct file but exits 1: a failed download, never a verified one.
        with tempfile.TemporaryDirectory() as tmp:
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "fail-with-file")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual(sorted(BULK_ASSETS * 2), sorted(downloaded_assets(log)))
            for asset in BULK_ASSETS:
                self.assertIn(f"{asset}: download failed", result.stdout)

    def test_warm_cache_failed_download_exits_1_naming_the_asset(self):
        # The cache already holds every asset and the current downloads exit 1: the stale copies
        # must not stand in for this run's download.
        shutil.copytree(BULK_RELEASE, cache_dir("E901"))
        with tempfile.TemporaryDirectory() as tmp:
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "fail")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            for asset in BULK_ASSETS:
                self.assertIn(f"{asset}: download failed", result.stdout)

    def test_warm_cache_empty_download_exits_1_naming_the_asset(self):
        # The cache already holds every asset and the current downloads exit 0 producing nothing.
        shutil.copytree(BULK_RELEASE, cache_dir("E901"))
        with tempfile.TemporaryDirectory() as tmp:
            fakebin, log = fake_gh(Path(tmp))
            result = run_verify_release(fakebin, log, "empty")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            for asset in BULK_ASSETS:
                self.assertIn(f"{asset}: download failed", result.stdout)


if __name__ == "__main__":
    unittest.main()
