"""Publishing is by hash and idempotent: an asset already on the release with the same sha256 is
not uploaded again (DW4a); an asset there with another sha256 stops the tool, which never replaces
an asset, and writes no manifest (DW4b); a manifest already present with other content is never
overwritten (DW4c); and the manifest is written only after the upload is verified by downloading
the asset back — an upload that stored nothing or stored other bytes is caught by that check and
stops the tool with no manifest. The tests run the tool against a fake `gh` serving a directory as
the release: no `gh` access, nothing leaves the machine."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "publish"
RUNS = FIXTURES / "runs"
EXPERIMENT = "E902"
RUN_ID = "E902-r0001"
sys.path.insert(0, str(REPO_ROOT))

# A fake `gh`: the release is the directory FAKE_GH_RELEASE, and every invocation is appended to
# FAKE_GH_LOG.
#   release view <tag> ...      print the directory's file names; exit 1 when it does not exist
#   release create <tag> ...    create the directory
#   release upload <tag> <file> refuse a name the release already has (as the real gh does),
#                               else copy the file in; FAKE_GH_SILENT_UPLOAD exits 0 storing
#                               nothing, FAKE_GH_CORRUPT_UPLOAD stores the file plus a suffix
#   release download <tag> -p <asset> -D <dir>  copy the asset out, exit 1 when it is not there
FAKE_GH = """#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\\n")
release = Path(os.environ["FAKE_GH_RELEASE"])
if args[:2] == ["release", "view"]:
    if not release.is_dir():
        sys.exit(1)
    print("\\n".join(sorted(path.name for path in release.iterdir())))
    sys.exit(0)
if args[:2] == ["release", "create"]:
    release.mkdir(parents=True, exist_ok=True)
    sys.exit(0)
if args[:2] == ["release", "upload"]:
    source = Path(args[3])
    destination = release / source.name
    if destination.exists():
        print(f"asset {source.name} already exists", file=sys.stderr)
        sys.exit(1)
    if os.environ.get("FAKE_GH_SILENT_UPLOAD"):
        sys.exit(0)
    shutil.copyfile(source, destination)
    if os.environ.get("FAKE_GH_CORRUPT_UPLOAD"):
        destination.write_bytes(source.read_bytes() + b"uploaded with other bytes\\n")
    sys.exit(0)
if args[:2] == ["release", "download"]:
    asset = args[args.index("-p") + 1]
    destination = Path(args[args.index("-D") + 1])
    if not destination.is_dir():
        sys.exit(1)  # the caller makes the directory
    if not (release / asset).is_file():
        sys.exit(1)
    shutil.copyfile(release / asset, destination / asset)
    sys.exit(0)
sys.exit(2)
"""

PAYLOAD = b"the savestate bytes of E902-r0001\n"
SHA256 = hashlib.sha256(PAYLOAD).hexdigest()
ASSET = f"{SHA256[:16]}-state.sav"


def run_publish(fakebin: Path, log: Path, files: list[Path], evidence_dir: Path,
                extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Run the tool against the fake `gh` with the fixture run record; the manifest goes to
    `evidence_dir`, never to the repository's evidence/."""
    env = {
        **os.environ,
        "PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
        "FAKE_GH_LOG": str(log),
        "FAKE_GH_RELEASE": str(fakebin.parent / "release"),
        **(extra_env or {}),
    }
    return subprocess.run(
        [sys.executable, "tools/publish_evidence.py", EXPERIMENT, "--run", RUN_ID,
         "--evidence-dir", str(evidence_dir), "--runs-dir", str(RUNS),
         *[flag for path in files for flag in ("--file", str(path))]],
        cwd=REPO_ROOT, capture_output=True, text=True, env=env)


def fake_gh(tmp: Path) -> tuple[Path, Path]:
    """The fake `gh` and its log in `tmp`; the release directory starts absent."""
    fakebin = tmp / "bin"
    fakebin.mkdir()
    gh = fakebin / "gh"
    gh.write_text(FAKE_GH, encoding="utf-8")
    gh.chmod(0o755)
    return fakebin, tmp / "gh.log"


def state_file(tmp: Path, content: bytes = PAYLOAD) -> Path:
    path = tmp / "state.sav"
    path.write_bytes(content)
    return path


def log_lines(log: Path) -> list[str]:
    return log.read_text(encoding="utf-8").splitlines() if log.exists() else []


def manifest_path(evidence_dir: Path) -> Path:
    return evidence_dir / EXPERIMENT / f"{RUN_ID}.manifest.json"


class PublishEvidenceTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)
        self.evidence = self.tmp / "evidence"
        self.fakebin, self.log = fake_gh(self.tmp)

    def test_publish_creates_the_release_uploads_and_writes_the_manifest_last(self):
        result = run_publish(self.fakebin, self.log, [state_file(self.tmp)], self.evidence)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        calls = log_lines(self.log)
        self.assertEqual(1, sum(call.startswith("release create") for call in calls), calls)
        uploads = [call for call in calls if call.startswith("release upload")]
        self.assertEqual(1, len(uploads), calls)
        self.assertTrue(uploads[0].startswith(f"release upload {EXPERIMENT} "), uploads[0])
        staged = uploads[0].split()[3]
        self.assertEqual(ASSET, Path(staged).name, uploads[0])
        self.assertTrue((self.fakebin.parent / "release" / ASSET).is_file())
        written = json.loads(manifest_path(self.evidence).read_text(encoding="utf-8"))
        self.assertEqual({
            "schema": "evidence-manifest/1",
            "run_id": RUN_ID,
            "experiment": EXPERIMENT,
            "store": f"release:{EXPERIMENT}",
            "artifact": {"set": "goal2-a949da2f", "variant": None},
            "files": [{"name": "state.sav", "bytes": len(PAYLOAD), "sha256": SHA256,
                       "asset": ASSET, "class": "save"}],
        }, written)
        # The tool's manifest output validates as evidence-manifest/1 by the pinned validator
        # (the suite-shared fetch, as in test_validate_runs).
        from tools import ga
        self.assertEqual([], ga.validate_document(written))

    def test_asset_already_present_with_the_same_sha256_is_not_uploaded_again(self):
        # DW4a: the release already holds the asset, byte for byte; the tool keeps it and writes
        # the manifest. Remove the skip in check_or_upload (always stage and upload) and this
        # fails: a second upload appears in the log, which the real gh would refuse.
        release = self.fakebin.parent / "release"
        release.mkdir()
        (release / ASSET).write_bytes(PAYLOAD)
        result = run_publish(self.fakebin, self.log, [state_file(self.tmp)], self.evidence)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual([], [call for call in log_lines(self.log)
                              if call.startswith("release upload")])
        self.assertIn("already on the release, same sha256", result.stdout)
        self.assertTrue(manifest_path(self.evidence).is_file())

    def test_asset_already_present_with_another_sha256_stops_and_writes_no_manifest(self):
        # DW4b: the asset name is taken but holds other bytes; replacing it is forbidden (releases
        # are shared state), so the tool stops. Remove the sha256 comparison in check_or_upload
        # and this fails: the tool exits 0 and writes the manifest over the wrong content.
        release = self.fakebin.parent / "release"
        release.mkdir()
        (release / ASSET).write_bytes(b"some other run's state\n")
        result = run_publish(self.fakebin, self.log, [state_file(self.tmp)], self.evidence)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn(ASSET, result.stdout)
        self.assertIn("not replacing it", result.stdout)
        self.assertEqual([], [call for call in log_lines(self.log)
                              if call.startswith("release upload")])
        self.assertFalse(manifest_path(self.evidence).exists())

    def test_asset_read_back_after_upload_with_another_sha256_stops_and_writes_no_manifest(self):
        # gh may report an upload that landed other bytes than the staged file's: the check
        # downloads the asset back and hashes it before any manifest names it.
        # FAKE_GH_CORRUPT_UPLOAD makes the fake store the staged file plus a suffix. Remove the
        # download-and-hash check after the upload in check_or_upload and this fails: the tool
        # exits 0 and writes the manifest for an asset it never verified.
        result = run_publish(self.fakebin, self.log, [state_file(self.tmp)], self.evidence,
                             extra_env={"FAKE_GH_CORRUPT_UPLOAD": "1"})
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("after upload with sha256", result.stdout)
        self.assertFalse(manifest_path(self.evidence).exists())
        # The bad asset stays: the tool never deletes or replaces what a release holds.
        self.assertTrue((self.fakebin.parent / "release" / ASSET).is_file())

    def test_download_failing_after_upload_stops_and_writes_no_manifest(self):
        # gh may report an upload that stored nothing: the check downloads the asset back, and
        # only a download that returns the bytes lets the manifest be written.
        # FAKE_GH_SILENT_UPLOAD makes the fake exit 0 without storing the file, so the
        # download-after-upload finds no asset. Remove the download-and-hash check after the
        # upload in check_or_upload and this fails: the tool exits 0 and writes the manifest
        # though nothing reached the release.
        result = run_publish(self.fakebin, self.log, [state_file(self.tmp)], self.evidence,
                             extra_env={"FAKE_GH_SILENT_UPLOAD": "1"})
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("download-after-upload", result.stdout)
        self.assertFalse(manifest_path(self.evidence).exists())
        self.assertFalse((self.fakebin.parent / "release" / ASSET).is_file())

    def test_existing_manifest_with_other_content_is_never_overwritten(self):
        # DW4c: E902-r0001.manifest.json already describes another bundle; the tool stops before
        # touching the release. Remove the existing-manifest comparison in publish() and this
        # fails: the manifest is overwritten (and the release grows an asset).
        self.evidence.mkdir(parents=True)
        existing = self.evidence / EXPERIMENT / f"{RUN_ID}.manifest.json"
        existing.parent.mkdir()
        other = {
            "schema": "evidence-manifest/1", "run_id": RUN_ID, "experiment": EXPERIMENT,
            "store": f"release:{EXPERIMENT}", "artifact": {"set": "goal2-a949da2f",
                                                           "variant": None},
            "files": [{"name": "earlier.sav", "bytes": 3, "sha256": "0" * 64,
                       "asset": "0" * 16 + "-earlier.sav", "class": "save"}],
        }
        before = json.dumps(other, indent=2) + "\n"
        existing.write_text(before, encoding="utf-8")
        result = run_publish(self.fakebin, self.log, [state_file(self.tmp)], self.evidence)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("exists with other content; not overwriting it", result.stdout)
        self.assertEqual(before, existing.read_text(encoding="utf-8"))
        self.assertEqual([], [call for call in log_lines(self.log)
                              if call.startswith(("release create", "release upload"))])

    def test_rerunning_the_same_command_changes_nothing(self):
        # DW3, as the tests see it: the second run uploads nothing and leaves the manifest byte
        # for byte, not even rewritten in place.
        path = state_file(self.tmp)
        self.assertEqual(0, run_publish(self.fakebin, self.log, [path], self.evidence).returncode)
        first = manifest_path(self.evidence).read_bytes()
        stamp = manifest_path(self.evidence).stat().st_mtime_ns
        second_log = self.tmp / "gh2.log"
        result = run_publish(self.fakebin, second_log, [path], self.evidence)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual([], [call for call in log_lines(second_log)
                              if call.startswith("release upload")])
        self.assertIn("already as published", result.stdout)
        self.assertEqual(first, manifest_path(self.evidence).read_bytes())
        self.assertEqual(stamp, manifest_path(self.evidence).stat().st_mtime_ns)

    def test_missing_file_and_missing_run_record_stop_with_an_error(self):
        result = run_publish(self.fakebin, self.log, [self.tmp / "absent.sav"], self.evidence)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("no such file", result.stdout)
        self.assertFalse(manifest_path(self.evidence).exists())
        evidence2 = self.tmp / "evidence2"
        result = subprocess.run(
            [sys.executable, "tools/publish_evidence.py", EXPERIMENT, "--run", "E902-r9999",
             "--evidence-dir", str(evidence2), "--runs-dir", str(RUNS),
             "--file", str(state_file(self.tmp))],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("no run record", result.stdout)
        self.assertFalse((evidence2 / EXPERIMENT / "E902-r9999.manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
