"""register_artifact prints an artifact-set/1 manifest whose id is the canonical manifest's prefix;
a path that is not a directory, or a manifest the schema rejects, exits 1."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402


class RegisterArtifactTest(unittest.TestCase):
    def test_manifest_id_and_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "one.txt").write_text("one", encoding="utf-8")
            (directory / "sub").mkdir()
            (directory / "sub" / "two.bin").write_bytes(b"\x00\x01\x02")
            result = subprocess.run(
                [sys.executable, "tools/register_artifact.py", str(directory),
                 "--label", "goal2-test", "--title", "GOAL2 test", "--version", "1.0",
                 "--how", "generated", "--when", "2026-10-03", "--note", "a test set",
                 "--writes", "*.sav"],
                cwd=REPO_ROOT, capture_output=True, text=True, check=True)
            manifest = json.loads(result.stdout)
            self.assertEqual("artifact-set/1", manifest["schema"])
            self.assertEqual("GOAL2 test", manifest["title"])
            self.assertEqual("1.0", manifest["version"])
            self.assertEqual({"how": "generated", "when": "2026-10-03", "note": "a test set"},
                             manifest["acquired"])
            self.assertTrue(manifest["id"].startswith("goal2-test-"))
            body = {key: value for key, value in manifest.items() if key not in ("id", "acquired")}
            self.assertEqual(ga.canonical_set_hash(body)[:8], manifest["id"].rsplit("-", 1)[1])
            # Every file entry asserts the bytes and sha256 of the fixture contents written above,
            # derived here independently of the tool's own output (R2).
            expected = {
                "one.txt": {"path": "one.txt", "bytes": 3,
                            "sha256": hashlib.sha256(b"one").hexdigest()},
                "sub/two.bin": {"path": "sub/two.bin", "bytes": 3,
                                "sha256": hashlib.sha256(b"\x00\x01\x02").hexdigest()},
            }
            self.assertEqual(sorted(expected), sorted(entry["path"] for entry in manifest["files"]))
            for entry in manifest["files"]:
                self.assertEqual(expected[entry["path"]], entry, entry["path"])
            self.assertEqual(["*.sav"], manifest["runtime_writes"])
            self.assertEqual([], ga.validate(manifest, ga.schema("artifact-set/1")))
            self.assertEqual([], ga.semantic_errors("artifact-set/1", manifest))

    def test_not_a_directory_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_register(Path(tmp) / "absent", "goal2-test")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("absent: not a directory", result.stderr)

    def test_manifest_the_schema_rejects_exits_1(self):
        # Upper case is not allowed in an id: the schema rejects it and nothing is printed.
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "one.txt").write_text("one", encoding="utf-8")
            result = run_register(Path(tmp), "GOAL2")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stdout)
            self.assertIn("$.id: does not match pattern", result.stderr)


def run_register(directory: Path, label: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/register_artifact.py", str(directory), "--label", label,
         "--title", "t", "--version", "1", "--how", "generated", "--when", "2026-10-03"],
        cwd=REPO_ROOT, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
