"""The record tools use the checker fetched from game-archaeologist at the pinned commit (DW5)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tools import ga  # noqa: E402


def run_validate(*paths) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/validate_runs.py", *[str(p) for p in paths]],
        cwd=REPO_ROOT, capture_output=True, text=True)


class ValidateRunsTest(unittest.TestCase):
    def test_help_prints_usage_and_runs_directory_behaves_as_before(self):
        # `--help` is an argparse request, not a path; a directory argument validates its
        # `*.json` files (the `runs` directory holds no documents today).
        help_result = subprocess.run(
            [sys.executable, "tools/validate_runs.py", "--help"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, help_result.returncode, help_result.stderr)
        self.assertIn("usage:", help_result.stdout)
        runs_result = run_validate(REPO_ROOT / "runs")
        self.assertEqual(0, runs_result.returncode, runs_result.stdout + runs_result.stderr)
        self.assertTrue(runs_result.stdout.startswith("ok:"))

    def test_invalid_example_exits_1(self):
        example = ga.example("invalid/run-1--interpretation-field.json")
        result = run_validate(example)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("additional property 'reinforcement_rule' not allowed", result.stdout)

    def test_valid_example_exits_0(self):
        example = ga.example("valid/run-1--seeded-crafted-state.json")
        result = run_validate(example)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_valid_evidence_manifest_exits_0(self):
        example = ga.example("valid/evidence-manifest-1--toy-run.json")
        result = run_validate(example)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_canonical_set_hash_is_exposed(self):
        manifest = {
            "schema": "artifact-set/1",
            "title": "x",
            "version": "1",
            "acquired": {"how": "generated", "when": "2000-01-01"},
            "files": [{"path": "a", "bytes": 1, "sha256": "0" * 64}],
            "runtime_writes": [],
        }
        digest = ga.canonical_set_hash(manifest)
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        # The digest is the sha256 of the canonical form built here from the documented rules
        # (without id and acquired, files sorted by path, sorted keys, ',', ':' separators), so a
        # constant or content-blind implementation fails (R2 sweep).
        canonical = {k: v for k, v in manifest.items() if k not in ("id", "acquired")}
        canonical["files"] = sorted(canonical["files"], key=lambda f: f["path"])
        text = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.assertEqual(hashlib.sha256(text.encode("utf-8")).hexdigest(), digest)
        # id and acquired are excluded from the canonical form.
        self.assertEqual(digest, ga.canonical_set_hash({**manifest, "id": "x-" + digest[:8]}))


if __name__ == "__main__":
    unittest.main()
