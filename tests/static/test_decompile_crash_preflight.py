"""A JVM crash report in the worktree blocks the next Ghidra decompile."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "static" / "decompile.sh"
TRACKER = "https://github.com/adoptium/adoptium-support/issues"


class CrashPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix=".test-ghidra-crash-", dir=ROOT)
        self.work = Path(self.temp.name)
        self.fixture_root = self.work / "repository"
        self.script = self.fixture_root / "tools" / "static" / "decompile.sh"
        self.script.parent.mkdir(parents=True)
        shutil.copy2(ROOT / "tools" / "static" / "decompile.sh", self.script)
        self.nested = self.fixture_root / "nested"
        self.nested.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_decompile(self, cwd: Path, output: Path, annotations: Path | None = None
                      ) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ, GHIDRA_HOME=str(self.work / "missing-ghidra"),
                   JAVA_HOME=str(self.work / "missing-jdk"))
        args = (["bash", str(self.script), "--annotations", str(annotations), "missing-GOAL.EXE",
                 str(output)] if annotations else
                ["bash", str(self.script), "missing-GOAL.EXE", str(output)])
        return subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=10)

    def test_root_and_nested_markers_block_both_invocation_forms_before_output(self):
        root_marker = self.fixture_root / "hs_err_pid2869680.log"
        nested_marker = self.nested / "hs_err_pid12345.log"
        self.assertFalse(root_marker.exists())
        root_marker.write_text("root crash marker\n")
        nested_marker.write_text("nested crash marker\n")
        annotations = self.work / "annotations"
        annotations.mkdir()

        for output, annotation_arg in ((self.work / "plain-output", None),
                                       (self.work / "annotated-output", annotations)):
            with self.subTest(annotations=bool(annotation_arg)):
                run = self.run_decompile(self.nested, output, annotation_arg)

                self.assertNotEqual(run.returncode, 0)
                self.assertIn("hs_err_pid2869680.log", run.stderr)
                self.assertIn("hs_err_pid12345.log", run.stderr)
                self.assertIn(TRACKER, run.stderr)
                self.assertNotIn("check_annotations.py", run.stderr,
                                 "preflight must precede annotation checks")
                self.assertNotIn("set GHIDRA_HOME", run.stderr,
                                 "preflight must precede tool prerequisite checks")
                self.assertFalse(output.exists(), "preflight must stop before writing output")

    def test_no_marker_continues_to_existing_prerequisite_checks(self):
        output = self.work / "output"
        run = self.run_decompile(self.fixture_root, output)

        self.assertNotEqual(run.returncode, 0)
        self.assertIn("decompile.sh: set GHIDRA_HOME to Ghidra 12.1.4 and JAVA_HOME to a JDK 21",
                      run.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
