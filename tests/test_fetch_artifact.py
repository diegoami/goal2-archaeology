"""The artifact is fetched by hash from the release, and a changed byte fails verification (DW1)."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import fetch_artifact  # noqa: E402

SET_ID = "goal2-a949da2f"


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
