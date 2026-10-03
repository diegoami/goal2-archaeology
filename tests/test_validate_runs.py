"""The record tools use the checker fetched from game-archaeologist at the pinned commit (DW5).

validate_runs checks every `*.json` of a directory, applies the semantic rules as well as the
schema, and reports a missing path, invalid JSON and an unknown schema."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"
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

    def test_semantic_rule_is_applied(self):
        # The asset name breaks a rule no schema can express (formats/examples/expected-errors.json).
        example = ga.example("invalid/evidence-manifest-1--bad-asset-name.json")
        result = run_validate(example)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("$.files[0].asset: must be", result.stdout)

    def test_directory_validates_each_json_document(self):
        result = run_validate(FIXTURES / "runs" / "E900", FIXTURES / "evidence" / "E900")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("ok: 2 document(s) valid", result.stdout.strip())

    def test_missing_path_invalid_json_and_unknown_schema_exit_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            broken = Path(tmp) / "broken.json"
            broken.write_text("{", encoding="utf-8")
            unknown = Path(tmp) / "unknown.json"
            unknown.write_text('{"schema": "nope/1"}', encoding="utf-8")
            absent = Path(tmp) / "absent.json"
            result = run_validate(broken, unknown, absent)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual([f"{broken}: invalid JSON", f"{unknown}: unknown schema 'nope/1'",
                              f"{absent}: no such file or directory"],
                             [line.split(": Expecting")[0] for line in result.stdout.splitlines()])

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


# A fake `gh api` serving one git tree and its blobs from FAKE_GH_TREE (a JSON file:
# {"tree": [...], "blobs": {sha: text}}); every call is logged to FAKE_GH_LOG.
FAKE_GH = """#!/usr/bin/env python3
import base64
import json
import os
import sys

args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as log:
    log.write(" ".join(args) + "\\n")
data = json.loads(open(os.environ["FAKE_GH_TREE"], encoding="utf-8").read())
path = args[1]
if "/git/trees/" in path:
    print(json.dumps({"tree": data["tree"]}))
elif "/git/blobs/" in path:
    text = data["blobs"][path.rsplit("/", 1)[1]]
    print(json.dumps({"content": base64.b64encode(text.encode()).decode()}))
else:
    sys.exit(2)
"""


class GaFetchTest(unittest.TestCase):
    """ga.fetch takes the checker and formats/ at the pinned commit, once, and nothing else."""

    def test_pin_is_archaeology_json(self):
        pinned = json.loads((REPO_ROOT / "archaeology.json").read_text(encoding="utf-8"))
        self.assertEqual((pinned["game-archaeologist"]["repo"], pinned["game-archaeologist"]["commit"]),
                         ga.pin())
        self.assertEqual(ga.CACHE / pinned["game-archaeologist"]["commit"], ga.root())

    def test_fetch_takes_only_the_checker_and_formats_once(self):
        tree = [
            {"path": "tests/formats/check_examples.py", "type": "blob", "sha": "c1"},
            {"path": "formats/run-1.schema.json", "type": "blob", "sha": "f1"},
            {"path": "formats/examples", "type": "tree", "sha": "t1"},
            {"path": "method/research-protocol.md", "type": "blob", "sha": "m1"},
            {"path": "tests/formats/other.py", "type": "blob", "sha": "o1"},
        ]
        blobs = {"c1": "checker", "f1": "{}", "m1": "method", "o1": "other"}
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / "tree.json").write_text(json.dumps({"tree": tree, "blobs": blobs}), encoding="utf-8")
        (tmp / "bin").mkdir()
        (tmp / "bin" / "gh").write_text(FAKE_GH, encoding="utf-8")
        (tmp / "bin" / "gh").chmod(0o755)
        log = tmp / "gh.log"
        env = {"PATH": f"{tmp / 'bin'}{os.pathsep}{os.environ['PATH']}",
               "FAKE_GH_LOG": str(log), "FAKE_GH_TREE": str(tmp / "tree.json")}
        with mock.patch.object(ga, "CACHE", tmp / "cache"), mock.patch.dict(os.environ, env):
            repo, commit = ga.pin()
            dest = ga.fetch()
            self.assertEqual(tmp / "cache" / commit, dest)
            written = sorted(p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file())
            self.assertEqual(["formats/run-1.schema.json", "tests/formats/check_examples.py"], written)
            self.assertEqual("checker", (dest / "tests/formats/check_examples.py").read_text())
            calls = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(f"api repos/{repo}/git/trees/{commit}?recursive=1", calls[0])
            self.assertEqual(sorted([f"api repos/{repo}/git/blobs/c1", f"api repos/{repo}/git/blobs/f1"]),
                             sorted(calls[1:]))
            ga.fetch()
            self.assertEqual(calls, log.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    unittest.main()
