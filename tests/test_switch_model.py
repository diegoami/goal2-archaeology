"""switch-model.mjs --ask and --review-kind (fix #182, CLAUDE.md "Choosing models" rule 2a): each flag
writes the expected harness.json in a temp copy, --dry-run writes nothing, and every refusal exits 1
with the file unchanged. The real script runs in a throwaway git directory holding a copy of
harness.json; no OpenCode call is made (no --probe)."""
import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "harness" / "switch-model.mjs"
HAVE_NODE = shutil.which("node") is not None


@unittest.skipUnless(HAVE_NODE, "node is not installed")
class SwitchDispatch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.dir)], check=True)
        self.config = json.loads((ROOT / "harness.json").read_text())
        self.write(self.config)

    def write(self, config):
        (self.dir / "harness.json").write_text(json.dumps(config, indent=2) + "\n")

    def raw(self):
        return (self.dir / "harness.json").read_text()

    def run_cli(self, *args, family="claude"):
        env = {**os.environ, "HARNESS_SESSION_FAMILY": family}
        return subprocess.run(["node", str(SCRIPT), *args], cwd=self.dir, env=env,
                              capture_output=True, text=True)

    def expect_written(self, mutate, *args, **kw):
        r = self.run_cli(*args, **kw)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        want = copy.deepcopy(self.config)
        mutate(want)
        self.assertEqual(json.loads(self.raw()), want)
        return r

    def expect_refused(self, *args, **kw):
        before = self.raw()
        r = self.run_cli(*args, **kw)
        self.assertEqual(r.returncode, 1, r.stderr + r.stdout)
        self.assertIn("Refused", r.stderr)
        self.assertEqual(self.raw(), before)

    # 1. each flag writes the expected harness.json
    def test_ask_on_and_off(self):
        self.expect_written(lambda c: c["dispatch"].update(ask=True), "--ask", "on")
        self.config = json.loads(self.raw())
        self.expect_written(lambda c: c["dispatch"].update(ask=False), "--ask", "off")

    def test_review_kind_sets_the_reviewer_for_that_kind_only(self):
        def m(c):
            c["dispatch"]["reviewerByKind"]["fix"] = "glm"
        self.expect_written(m, "--review-kind", "fix", "--model", "glm")

    def test_review_kind_research(self):
        def m(c):
            c["dispatch"]["reviewerByKind"]["research"] = "luna"
        self.expect_written(m, "--review-kind", "research", "--model", "luna")

    def test_ask_and_review_kind_together(self):
        def m(c):
            c["dispatch"]["ask"] = True
            c["dispatch"]["reviewerByKind"]["fix"] = "glm"
        self.expect_written(m, "--ask", "on", "--review-kind", "fix", "--model", "glm")

    def test_a_missing_dispatch_block_is_created(self):
        del self.config["dispatch"]
        self.write(self.config)
        self.expect_written(lambda c: c.update(dispatch={"ask": False}), "--ask", "off")
        self.config = json.loads(self.raw())
        del self.config["dispatch"]
        self.write(self.config)
        self.expect_written(lambda c: c.update(dispatch={"reviewerByKind": {"fix": "glm"}}),
                            "--review-kind", "fix", "--model", "glm")

    def test_other_keys_are_untouched(self):
        self.run_cli("--ask", "on")
        after = json.loads(self.raw())
        after["dispatch"]["ask"] = False
        self.assertEqual(after, self.config)

    # --dry-run writes nothing
    def test_dry_run_writes_nothing(self):
        before = self.raw()
        for args in (("--ask", "on"), ("--review-kind", "fix", "--model", "glm")):
            r = self.run_cli(*args, "--dry-run")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("dry run", r.stdout)
            self.assertIn("after:", r.stdout)
            self.assertEqual(self.raw(), before)

    # 2. refusals: exit 1, harness.json unchanged
    def test_unknown_model_refused(self):
        self.expect_refused("--review-kind", "fix", "--model", "nosuchmodel")

    def test_inherited_property_name_is_not_a_model(self):
        self.expect_refused("--review-kind", "fix", "--model", "constructor")

    def test_blocked_model_refused(self):
        self.config["blocked"] = ["glm"]
        self.write(self.config)
        self.expect_refused("--review-kind", "fix", "--model", "glm")

    def test_session_family_refused(self):
        self.expect_refused("--review-kind", "fix", "--model", "luna", family="openai")

    def test_unknown_kind_refused(self):
        self.expect_refused("--review-kind", "docs", "--model", "luna")

    def test_ask_maybe_refused(self):
        self.expect_refused("--ask", "maybe")

    def test_review_kind_needs_a_model(self):
        before = self.raw()
        r = self.run_cli("--review-kind", "fix")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(self.raw(), before)

    # 3. --show prints the dispatch line
    def test_show_prints_the_dispatch_line(self):
        r = self.run_cli("--show")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dispatch: ask off; reviewer by kind: fix=luna, research=sol-6.1", r.stdout)

    def test_show_after_a_change(self):
        self.run_cli("--ask", "on")
        self.assertIn("dispatch: ask on;", self.run_cli("--show").stdout)

    def test_show_without_a_dispatch_block(self):
        del self.config["dispatch"]
        self.write(self.config)
        self.assertIn("dispatch: ask on (default, not set); reviewer by kind: none", self.run_cli("--show").stdout)


if __name__ == "__main__":
    unittest.main()
