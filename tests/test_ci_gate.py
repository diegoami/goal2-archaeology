"""T297 (issue #297): tools/ci_gate.py decides which checks a CI run needs.

Each assertion fails if the behaviour it names is removed: the classification is checked against
the paths a trace of the five slow test modules recorded (notes/T297/slow-module-deps-20261017.json),
and the decision against fake diffs and fake check-run answers, never against the network."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("ci_gate", ROOT / "tools" / "ci_gate.py")
G = importlib.util.module_from_spec(spec)
sys.modules["ci_gate"] = G
spec.loader.exec_module(G)


class Classify(unittest.TestCase):
    def test_tiers_of_examples(self):
        cases = {
            "experiments/E021-m0-whole-match/out/r1.json": G.NONE,
            "tools/screens/mutations-20261011-01.log": G.NONE,
            "CLAUDE.md": G.DOCS,
            "docs/tasks/T99.md": G.DOCS,
            "docs/lessons.md": G.DOCS,
            "notes/T58.md": G.DOCS,
            "spec/anything.md": G.DOCS,
            # prose that a test reads is code
            "docs/process.md": G.FAST,
            "docs/review-brief.md": G.FAST,
            "docs/play-guide.md": G.FAST,
            "docs/match-engine-plan.md": G.FAST,
            "findings/F001.md": G.FAST,
            "runs/E014/E014-r0001.json": G.FAST,
            "tools/harness/review.mjs": G.FAST,
            ".opencode/agents/reviewer.md": G.FAST,
            "tests/test_model_ageing.py": G.FAST,
            "tests/static/test_map.py": G.FAST,
            "static/goal-exe-map.md": G.FAST,
            # what the slow modules read
            "runtime/emul/watched_match.py": G.FULL,
            "runtime/human/recorder.py": G.FULL,
            "tests/test_human_keys.py": G.FULL,
            "tests/netskip.py": G.FULL,
            "tools/net.py": G.FULL,
            "tools/screens/video.py": G.FULL,
            "experiments/E036-match-port/compare.py": G.FULL,
            "runs/E015/E015-r0001.json": G.FULL,
            # not read by any module that runs in CI (the emul modules skip: no unicorn)
            "static/goal-exe/code/seg_214B_01.asm": G.FAST,
            "runs/E011/E011-r0001.json": G.FAST,
            ".github/workflows/ci.yml": G.FULL,
            "tools/ci_gate.py": G.FULL,
        }
        for path, want in cases.items():
            with self.subTest(path=path):
                self.assertEqual(G.classify(path), want)

    def test_a_change_takes_its_highest_tier(self):
        self.assertEqual(G.tier_of(["CLAUDE.md", "tools/harness/review.mjs"]), G.FAST)
        self.assertEqual(G.tier_of(["CLAUDE.md", "runtime/driver/x.py", "a.log"]), G.FULL)
        self.assertEqual(G.tier_of(["a.log"]), G.NONE)
        self.assertEqual(G.tier_of([]), G.NONE)

    def test_every_path_the_slow_modules_read_is_full(self):
        """The trace of the five slow modules: no repo file they open or execute may fall below FULL."""
        trace = json.loads((ROOT / "notes/T297/slow-module-deps-20261017.json").read_text())
        self.assertEqual(sorted(trace), sorted(f"tests/{m}.py" for m in G.SLOW))
        for module, rec in trace.items():
            for path in rec["repo_paths_opened_or_executed"]:
                # measured outputs run nothing on a push by the owner's rule of 2026-10-12, even
                # the ones test_e032_recheck reads; the nightly full run is the net for those
                if not (ROOT / path).is_file() or G.OUTPUT_RE.search(path):
                    continue
                with self.subTest(module=module, path=path):
                    self.assertEqual(G.classify(path), G.FULL)

    def test_every_full_path_exists(self):
        for p in G.FULL_PATHS:
            with self.subTest(path=p):
                self.assertTrue((ROOT / p).exists(), f"{p} does not exist: a renamed path silently stops gating")

    def test_every_doc_a_test_reads_exists(self):
        for p in G.DOCS_READ_BY_TESTS:
            self.assertTrue((ROOT / p).is_file(), p)


def fake_diff(whole, push):
    def diff(a, b, three_dots=False):
        return whole if three_dots else push
    return diff


ENV = {"EVENT": "pull_request", "ACTION": "synchronize", "BASE": "b", "HEAD": "h", "BEFORE": "p", "REPO": "o/r"}


def must_not_ask(repo, sha):
    raise AssertionError("asked the check-runs API when the answer could not matter")


class Decide(unittest.TestCase):
    def tier(self, whole, push, ok, **env):
        calls = []

        def succeeded(repo, sha):
            calls.append((repo, sha))
            return ok
        t, _ = G.decide({**ENV, **env}, fake_diff(whole, push), succeeded)
        return t, calls

    def test_nightly_and_manual_runs_are_full(self):
        self.assertEqual(G.decide({"EVENT": "workflow_dispatch"})[0], G.FULL)

    def test_a_new_pr_takes_the_tier_of_its_whole_diff(self):
        for action in ("opened", "reopened", "ready_for_review"):
            t, calls = self.tier(["CLAUDE.md"], None, True, ACTION=action)
            self.assertEqual((t, calls), (G.DOCS, []))
        t, _ = self.tier(["CLAUDE.md", "tools/harness/x.mjs"], None, True, ACTION="ready_for_review")
        self.assertEqual(t, G.FAST)

    def test_a_docs_push_to_a_code_pr_is_docs_when_the_previous_head_passed(self):
        t, calls = self.tier(["runtime/a.py", "CLAUDE.md"], ["CLAUDE.md"], True)
        self.assertEqual(t, G.DOCS)
        self.assertEqual(calls, [("o/r", "p")])

    def test_a_docs_push_to_a_code_pr_is_the_whole_pr_when_the_previous_head_did_not_pass(self):
        """The case the rule exists for: a red run followed by a prose-only fix must not go green."""
        t, _ = self.tier(["runtime/a.py", "CLAUDE.md"], ["CLAUDE.md"], False)
        self.assertEqual(t, G.FULL)

    def test_an_output_only_push_runs_nothing_only_after_a_pass(self):
        self.assertEqual(self.tier(["tools/harness/x.mjs", "a.log"], ["a.log"], True)[0], G.NONE)
        self.assertEqual(self.tier(["tools/harness/x.mjs", "a.log"], ["a.log"], False)[0], G.FAST)

    def test_a_push_that_holds_the_prs_highest_tier_does_not_ask(self):
        t, _ = G.decide(ENV, fake_diff(["runtime/a.py", "CLAUDE.md"], ["runtime/a.py"]), must_not_ask)
        self.assertEqual(t, G.FULL)

    def test_an_unreadable_diff_runs_everything(self):
        self.assertEqual(G.decide(ENV, fake_diff(None, None), must_not_ask)[0], G.FULL)

    def test_a_force_push_whose_old_head_is_gone_takes_the_whole_pr(self):
        t, _ = G.decide(ENV, fake_diff(["tools/harness/x.mjs"], None), must_not_ask)
        self.assertEqual(t, G.FAST)

    def test_no_before_takes_the_whole_pr(self):
        t, _ = G.decide({**ENV, "BEFORE": ""}, fake_diff(["tools/harness/x.mjs"], ["CLAUDE.md"]), must_not_ask)
        self.assertEqual(t, G.FAST)


class CheckRuns(unittest.TestCase):
    class R:
        def __init__(self, code, out):
            self.returncode, self.stdout = code, out

    def ask(self, runs, code=0):
        return G.previous_head_succeeded(
            "o/r", "sha", lambda *a, **k: self.R(code, json.dumps({"check_runs": runs})))

    def test_only_a_successful_checks_job_counts(self):
        self.assertTrue(self.ask([{"name": "checks", "conclusion": "success"}]))
        for c in ("failure", "cancelled", "skipped", None):
            self.assertFalse(self.ask([{"name": "checks", "conclusion": c}]), c)
        self.assertFalse(self.ask([{"name": "quick", "conclusion": "success"}]))
        self.assertFalse(self.ask([]))
        self.assertFalse(self.ask([{"name": "checks", "conclusion": "success"}], code=1))

    def test_garbage_is_not_a_pass(self):
        self.assertFalse(G.previous_head_succeeded("o/r", "s", lambda *a, **k: self.R(0, "not json")))


class Suite(unittest.TestCase):
    def modules(self, tier):
        out = set()

        def walk(s):
            for t in s:
                if isinstance(t, unittest.TestSuite):
                    walk(t)
                else:
                    out.add(type(t).__module__.rsplit(".", 1)[-1])
        walk(G.select_suite(tier))
        return out

    def test_fast_leaves_out_exactly_the_slow_modules(self):
        full, fast = self.modules("full"), self.modules("fast")
        self.assertTrue(set(G.SLOW) <= full, set(G.SLOW) - full)
        self.assertEqual(full - fast, set(G.SLOW))
        self.assertIn("test_ci_gate", fast)


class Workflow(unittest.TestCase):
    TEXT = (ROOT / ".github/workflows/ci.yml").read_text()

    def test_the_status_job_has_no_needs_and_no_gate_output_in_its_if(self):
        """A PR that is not a draft always gets a `checks` status: a skipped job must not block."""
        self.assertNotIn("needs:", self.TEXT)
        block = self.TEXT.split("  checks:\n", 1)[1]
        self.assertIn("name: CI", self.TEXT)
        first_if = [l for l in block.splitlines() if l.startswith("    if:")][0]
        self.assertNotIn("steps.", first_if)
        self.assertIn("github.event.pull_request.draft", first_if)

    def test_the_cheap_checks_run_in_every_tier_that_runs(self):
        for needle in ("tools/check_links.py", "tools/check_citations.py", "git ls-files"):
            line = [l for l in self.TEXT.splitlines() if needle in l and "run:" in l]
            self.assertTrue(line, needle)
        self.assertIn("steps.gate.outputs.quick == 'true'", self.TEXT)

    def test_the_merge_commit_of_a_research_pr_skips_quick_on_main(self):
        self.assertIn("!startsWith(github.event.head_commit.message, 'Merge pull request #')", self.TEXT)

    def test_no_unquoted_if_holds_a_hash(self):
        """In YAML a ` #` inside a plain scalar starts a comment: the first push of PR 298 made
        'if: ... startsWith(msg, 'Merge pull request #')' an invalid workflow."""
        for line in self.TEXT.splitlines():
            s = line.strip()
            if s.startswith(("if:", "- if:")):
                value = s.split("if:", 1)[1].strip()
                if " #" in value:
                    self.assertTrue(value.startswith(('"', "'")), line)

    def test_a_nightly_full_run_on_main_exists(self):
        self.assertIn("schedule:", self.TEXT)
        self.assertIn("workflow_dispatch:", self.TEXT)


if __name__ == "__main__":
    unittest.main()
