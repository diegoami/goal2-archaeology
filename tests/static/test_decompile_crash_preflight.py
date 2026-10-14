"""A JVM crash report in the worktree blocks the next Ghidra decompile."""
import os
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

    def tearDown(self):
        self.temp.cleanup()

    def run_decompile(self, cwd: Path, output: Path) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ, GHIDRA_HOME=str(self.work / "missing-ghidra"),
                   JAVA_HOME=str(self.work / "missing-jdk"))
        return subprocess.run(["bash", str(SCRIPT), "missing-GOAL.EXE", str(output)], cwd=cwd,
                              env=env, capture_output=True, text=True, timeout=10)

    def test_root_and_nested_markers_block_before_output_from_nested_invocation(self):
        root_marker = ROOT / "hs_err_pid2869680.log"
        nested_marker = self.work / "nested" / "hs_err_pid12345.log"
        self.assertFalse(root_marker.exists(), f"refusing to overwrite existing marker: {root_marker}")
        nested_marker.parent.mkdir()
        root_marker.write_text("root crash marker\n")
        nested_marker.write_text("nested crash marker\n")
        output = self.work / "output"

        try:
            run = self.run_decompile(nested_marker.parent, output)
        finally:
            root_marker.unlink(missing_ok=True)

        self.assertNotEqual(run.returncode, 0)
        self.assertIn("hs_err_pid2869680.log", run.stderr)
        self.assertIn("hs_err_pid12345.log", run.stderr)
        self.assertIn(TRACKER, run.stderr)
        self.assertFalse(output.exists(), "preflight must stop before writing output")
        self.assertNotIn("set GHIDRA_HOME", run.stderr,
                         "crash markers must be reported before tool prerequisite checks")

    def test_no_marker_continues_to_existing_prerequisite_checks(self):
        output = self.work / "output"
        run = self.run_decompile(ROOT, output)

        self.assertNotEqual(run.returncode, 0)
        self.assertIn("decompile.sh: set GHIDRA_HOME to Ghidra 12.1.4 and JAVA_HOME to a JDK 21",
                      run.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
