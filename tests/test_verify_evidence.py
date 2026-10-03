"""A local evidence bundle verifies by sha256 and asset name; a changed byte fails; the release is
listed once and each distinct asset downloaded once (DW3)."""
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

# A fake `gh`: one `release view` prints the fixture release's asset names; `release download`
# copies the named asset from the fixture release. Every invocation is appended to FAKE_GH_LOG.
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
    print("\\n".join(sorted(path.name for path in release.iterdir())))
    sys.exit(0)
if args[:2] == ["release", "download"]:
    asset = args[args.index("-p") + 1]
    dest = Path(args[args.index("-D") + 1])
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(release / asset, dest / asset)
    sys.exit(0)
sys.exit(2)
"""


def run_verify(local: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "tools/verify_evidence.py", "E900",
         "--local", str(local), "--evidence-dir", str(EVIDENCE)],
        cwd=REPO_ROOT, capture_output=True, text=True)


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


class VerifyEvidenceReleaseTest(unittest.TestCase):
    def test_one_listing_and_one_download_per_distinct_asset(self):
        # 3 manifests, 4 distinct assets shared between them: toy-archaeology#11.
        with tempfile.TemporaryDirectory() as tmp:
            fakebin = Path(tmp) / "bin"
            fakebin.mkdir()
            log = Path(tmp) / "gh.log"
            gh = fakebin / "gh"
            gh.write_text(FAKE_GH, encoding="utf-8")
            gh.chmod(0o755)
            shutil.rmtree(REPO_ROOT / ".cache" / "evidence" / "E901", ignore_errors=True)
            env = {
                **os.environ,
                "PATH": f"{fakebin}{os.pathsep}{os.environ['PATH']}",
                "FAKE_GH_LOG": str(log),
                "FAKE_GH_RELEASE": str(BULK / "release"),
            }
            result = subprocess.run(
                [sys.executable, "tools/verify_evidence.py", "E901",
                 "--evidence-dir", str(BULK), "--repo", "diegoami/goal2-archaeology"],
                cwd=REPO_ROOT, capture_output=True, text=True, env=env)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            calls = log.read_text(encoding="utf-8").splitlines()
            listings = [call for call in calls if call.startswith("release view")]
            downloads = [call for call in calls if call.startswith("release download")]
            self.assertLessEqual(len(listings), 1)
            self.assertLessEqual(len(downloads), 4)
            downloaded = {shlex.split(call)[shlex.split(call).index("-p") + 1] for call in downloads}
            self.assertEqual(4, len(downloaded))


if __name__ == "__main__":
    unittest.main()
