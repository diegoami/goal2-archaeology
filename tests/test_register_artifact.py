"""tools/register_artifact.py runs game-archaeologist's pinned artifact tool (ADR-009); arguments,
output and exit code pass through. `manifest` registers a directory (a file matching a
runtime_writes glob leaves `files`, U21), `check` re-hashes a copy against a known.json entry, and a
directory holding a special file or a symbolic link out of itself is refused (U24)."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402
from tests import netskip  # noqa: E402


def run_register(*argv) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/register_artifact.py", *[str(a) for a in argv]],
        cwd=REPO_ROOT, capture_output=True, text=True)


def seed(directory: Path) -> None:
    (directory / "one.txt").write_text("one", encoding="utf-8")
    (directory / "sub").mkdir()
    (directory / "sub" / "two.bin").write_bytes(b"\x00\x01\x02")


@netskip.needs_pinned_tools
class RegisterArtifactTest(unittest.TestCase):
    def test_manifest_registers_a_directory_and_runtime_writes_leave_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            seed(directory)
            (directory / "save.sav").write_bytes(b"\x00\x01")  # the game writes this at run time
            result = run_register(
                "manifest", directory,
                "--label", "goal2-test", "--title", "GOAL2 test", "--version", "1.0",
                "--how", "generated", "--when", "2026-10-03", "--note", "a test set",
                "--writes", "*.sav")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            manifest = json.loads(result.stdout)
            self.assertEqual("artifact-set/1", manifest["schema"])
            self.assertEqual("GOAL2 test", manifest["title"])
            self.assertEqual("1.0", manifest["version"])
            self.assertEqual({"how": "generated", "when": "2026-10-03", "note": "a test set"},
                             manifest["acquired"])
            self.assertTrue(manifest["id"].startswith("goal2-test-"))
            # A file matching a runtime_writes glob leaves files (U21); the glob is recorded.
            self.assertEqual(["one.txt", "sub/two.bin"],
                             [entry["path"] for entry in manifest["files"]])
            self.assertEqual(["*.sav"], manifest["runtime_writes"])
            # Every file entry asserts the bytes and sha256 of the fixture contents written above,
            # derived here independently of the tool's own output (R2).
            expected = {
                "one.txt": {"path": "one.txt", "bytes": 3,
                            "sha256": hashlib.sha256(b"one").hexdigest()},
                "sub/two.bin": {"path": "sub/two.bin", "bytes": 3,
                                "sha256": hashlib.sha256(b"\x00\x01\x02").hexdigest()},
            }
            for entry in manifest["files"]:
                self.assertEqual(expected[entry["path"]], entry, entry["path"])
            self.assertEqual([], ga.validate(manifest, ga.schema("artifact-set/1")))
            self.assertEqual([], ga.semantic_errors("artifact-set/1", manifest))

    def test_manifest_the_schema_rejects_exits_1(self):
        # Upper case is not allowed in an id: the schema rejects it and the named errors are
        # printed (stdout), never the manifest.
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            seed(directory)
            result = run_register("manifest", directory, "--label", "GOAL2",
                                  "--title", "t", "--version", "1", "--how", "generated",
                                  "--when", "2026-10-03")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertNotIn('"schema"', result.stdout)
            self.assertIn("$.id: does not match pattern", result.stdout)

    def test_check_rehashes_a_copy_against_a_known_json_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / "set"
            directory.mkdir()
            seed(directory)
            registered = run_register("manifest", directory, "--label", "goal2-test",
                                      "--title", "t", "--version", "1", "--how", "generated",
                                      "--when", "2026-10-03")
            self.assertEqual(0, registered.returncode, registered.stdout + registered.stderr)
            manifest = json.loads(registered.stdout)
            known = Path(tmp) / "known.json"
            known.write_text(json.dumps({"sets": [{"manifest": manifest}]}), encoding="utf-8")
            copy = Path(tmp) / "copy"
            shutil.copytree(directory, copy)
            ok = run_register("check", copy, manifest["id"], "--known", known)
            self.assertEqual(0, ok.returncode, ok.stdout + ok.stderr)
            self.assertIn(f"ok: {manifest['id']}", ok.stdout)
            (copy / "one.txt").write_text("changed", encoding="utf-8")
            bad = run_register("check", copy, manifest["id"], "--known", known)
            self.assertEqual(1, bad.returncode, bad.stdout + bad.stderr)
            self.assertIn("one.txt: sha256", bad.stdout)

    def test_special_file_in_the_directory_fails_manifest(self):
        # A FIFO is never read: registration refuses a directory it cannot observe safely (U24).
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            seed(directory)
            os.mkfifo(directory / "pipe")
            result = run_register("manifest", directory, "--label", "goal2-test",
                                  "--title", "t", "--version", "1", "--how", "generated",
                                  "--when", "2026-10-03")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("pipe: not a regular file or a directory", result.stdout)

    def test_symbolic_link_out_of_the_directory_fails_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside"
            outside.mkdir()
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            directory = Path(tmp) / "set"
            directory.mkdir()
            seed(directory)
            (directory / "link.txt").symlink_to(outside / "secret.txt")
            result = run_register("manifest", directory, "--label", "goal2-test",
                                  "--title", "t", "--version", "1", "--how", "generated",
                                  "--when", "2026-10-03")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("link.txt: symbolic link to outside the directory", result.stdout)

    def test_no_subcommand_is_a_usage_error(self):
        # The pinned tool's CLI is `manifest|check|validate`; without one, argparse exits 2.
        result = run_register()
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("command", result.stderr)


if __name__ == "__main__":
    unittest.main()
