"""register_artifact prints an artifact-set/1 manifest whose id is the canonical manifest's prefix."""
from __future__ import annotations

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
                 "--how", "generated", "--when", "2026-10-03", "--writes", "*.sav"],
                cwd=REPO_ROOT, capture_output=True, text=True, check=True)
            manifest = json.loads(result.stdout)
            self.assertEqual("artifact-set/1", manifest["schema"])
            self.assertTrue(manifest["id"].startswith("goal2-test-"))
            body = {key: value for key, value in manifest.items() if key not in ("id", "acquired")}
            self.assertEqual(ga.canonical_set_hash(body)[:8], manifest["id"].rsplit("-", 1)[1])
            self.assertEqual(
                [{"path": "one.txt"}, {"path": "sub/two.bin"}],
                [{"path": entry["path"]} for entry in manifest["files"]])
            self.assertEqual(["*.sav"], manifest["runtime_writes"])
            self.assertEqual([], ga.validate(manifest, ga.schema("artifact-set/1")))
            self.assertEqual([], ga.semantic_errors("artifact-set/1", manifest))


if __name__ == "__main__":
    unittest.main()
