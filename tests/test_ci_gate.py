"""T297 (issue #297): tools/ci_gate.py decides which checks a CI run needs.

Each assertion fails if the behaviour it names is removed: the classification is checked against
the paths a trace of the six slow test modules recorded (notes/T297/slow-module-deps-20261017.json, and
notes/T304/deps-test_emul_match-20261017.json for the sixth),
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

Q, C = G.QUICK, G.CODE
NOTHING = frozenset()
DOCS = frozenset({Q})
FAST = frozenset({Q, C})
KEYS, REC, VID, REC32, CMP36, EMUL = ("test_human_keys", "test_human_record", "test_screens_video",
                                      "test_e032_recheck", "test_e036_compare", "test_emul_match")


def fast_plus(*mods):
    return frozenset({Q, C, *mods})


class Classify(unittest.TestCase):
    def test_what_examples_oblige(self):
        cases = {
            "experiments/E021-m0-whole-match/out/r1.json": NOTHING,
            "tools/screens/mutations-20261011-01.log": NOTHING,
            "CLAUDE.md": DOCS,
            "docs/tasks/T99.md": DOCS,
            "docs/lessons.md": DOCS,
            "notes/T58.md": DOCS,
            "spec/anything.md": DOCS,
            # prose that a test reads is code
            "docs/process.md": FAST,
            "docs/review-brief.md": FAST,
            "docs/play-guide.md": FAST,
            "docs/match-engine-plan.md": FAST,
            "findings/F001.md": FAST,
            "runs/E014/E014-r0001.json": FAST,
            "tools/harness/review.mjs": FAST,
            ".opencode/agents/reviewer.md": FAST,
            "tests/test_model_ageing.py": FAST,
            "tests/static/test_map.py": FAST,
            "static/goal-exe-map.md": FAST,
            "runtime/model/ratings.py": fast_plus(EMUL),
            # test_emul_match (issue #304: CI installs unicorn, so it runs there) reads these; the two cheap
            # emul modules run in the code tier and gate nothing of their own
            "static/goal-exe/code/seg_214B_01.asm": fast_plus(EMUL),
            "runs/E011/E011-r0001.json": fast_plus(EMUL),
            "runtime/emul/watched_match.py": fast_plus(EMUL),
            "runtime/emul/requirements.txt": fast_plus(EMUL),
            "experiments/E021-m0-whole-match/check.py": fast_plus(EMUL),
            "tests/test_emul_match.py": fast_plus(EMUL),
            "tests/test_emul_watched.py": FAST,
            "tests/test_emul_skip_ret.py": FAST,
            # what the slow modules read
            "runtime/human/recorder.py": fast_plus(KEYS, REC),
            "runtime/driver/driver.py": fast_plus(KEYS, REC, VID, EMUL),
            "tests/test_human_keys.py": fast_plus(KEYS, REC),  # each imports the other
            "tests/netskip.py": fast_plus(KEYS, REC),
            "tools/net.py": fast_plus(KEYS, REC),
            "tools/screens/video.py": fast_plus(VID),
            "experiments/E032-match-engine-inventory/recheck.sh": fast_plus(REC32),
            "experiments/E036-match-port/compare.py": fast_plus(CMP36),
            "runtime/original_match/check.py": fast_plus(CMP36),
            "artifacts/known.json": fast_plus(KEYS),
            "archaeology.json": fast_plus(REC),
            # the CI definition obliges everything
            ".github/workflows/ci.yml": G.ALL,
            "tools/ci_gate.py": G.ALL,
        }
        for path, want in cases.items():
            with self.subTest(path=path):
                self.assertEqual(G.classify(path), want)

    def test_every_document_with_a_named_view_citation_obliges_the_quick_tier(self):
        """Issue #307/#310: the named-citation check runs in the quick tier, so a PR that touches only a spec,
        docs or notes file (or a finding or an experiment's notes) that cites a line of the named view runs it,
        and so does one that regenerates the view."""
        sys.path.insert(0, str(ROOT / "tools" / "static"))
        import named_citations as nc
        cited = {c.doc for c in nc.all_cites()}
        self.assertTrue({"spec/friendlies.md", "docs/play-guide.md"} <= cited)
        self.assertTrue(any(d.startswith("findings/") for d in cited))
        self.assertTrue(any(d.startswith("experiments/") for d in cited))
        for path in sorted(cited) + ["static/goal-exe/named/seg_0791_01.c", "static/goal-exe/named-citations.tsv",
                                     "tools/static/named_citations.py"]:
            with self.subTest(path=path):
                self.assertIn(Q, G.classify(path))

    def test_a_change_obliges_the_union_of_its_files(self):
        self.assertEqual(G.obligations(["CLAUDE.md", "tools/harness/review.mjs"]), FAST)
        self.assertEqual(G.obligations(["CLAUDE.md", "tools/screens/x.py", "a.log"]), fast_plus(VID))
        self.assertEqual(G.obligations(["tools/screens/x.py", "tools/net.py"]), fast_plus(VID, KEYS, REC))
        self.assertEqual(G.obligations(["a.log"]), NOTHING)
        self.assertEqual(G.obligations([]), NOTHING)

    def test_every_path_a_slow_module_reads_obliges_that_module(self):
        """The traces of the six slow modules: every repo file one opens or executes must oblige it."""
        trace = json.loads((ROOT / "notes/T297/slow-module-deps-20261017.json").read_text())
        t304 = json.loads((ROOT / "notes/T304/deps-test_emul_match-20261017.json").read_text())
        self.assertTrue(t304["ok"])
        trace["tests/test_emul_match.py"] = {"repo_paths_opened_or_executed": t304["files"]}
        self.assertEqual(sorted(trace), sorted(f"tests/{m}.py" for m in G.SLOW))
        for module, rec in trace.items():
            name = Path(module).stem
            for path in rec["repo_paths_opened_or_executed"]:
                # measured outputs run nothing on a push by the owner's rule of 2026-10-12, even
                # the ones the recheck and compare modules read; the nightly full run is the net
                if not (ROOT / path).is_file() or G.OUTPUT_RE.search(path) or path.startswith(".cache/"):
                    continue
                with self.subTest(module=name, path=path):
                    self.assertIn(name, G.classify(path))

    def test_every_dependency_prefix_exists(self):
        for mod, deps in G.SLOW_DEPS.items():
            for p in deps:
                with self.subTest(module=mod, path=p):
                    self.assertTrue((ROOT / p).exists(), f"{p} does not exist: a renamed path silently stops gating {mod}")
        for p in G.EVERYTHING_PATHS:
            self.assertTrue((ROOT / p).exists(), p)

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
    def ob(self, whole, push, ok, **env):
        calls = []

        def succeeded(repo, sha):
            calls.append((repo, sha))
            return ok
        ob, _ = G.decide({**ENV, **env}, fake_diff(whole, push), succeeded)
        return ob, calls

    def test_manual_runs_are_everything(self):
        self.assertEqual(G.decide({"EVENT": "workflow_dispatch"})[0], G.ALL)

    def test_the_nightly_run_is_everything_only_when_code_landed_in_the_day(self):
        class Out:
            def __init__(self, text):
                self.stdout = text
        real = G.git
        try:
            G.git = lambda *a: Out("CLAUDE.md\ndocs/tasks/T9.md\n\nnotes/x.md\n")
            self.assertEqual(G.decide({"EVENT": "schedule"})[0], NOTHING)
            G.git = lambda *a: Out("CLAUDE.md\n\ntools/harness/review.mjs\n")
            self.assertEqual(G.decide({"EVENT": "schedule"})[0], G.ALL)
            G.git = lambda *a: Out("")
            self.assertEqual(G.decide({"EVENT": "schedule"})[0], NOTHING)
        finally:
            G.git = real

    def test_a_new_pr_obliges_what_its_whole_diff_does(self):
        for action in ("opened", "reopened", "ready_for_review"):
            ob, calls = self.ob(["CLAUDE.md"], None, True, ACTION=action)
            self.assertEqual((ob, calls), (DOCS, []))
        ob, _ = self.ob(["CLAUDE.md", "tools/harness/x.mjs"], None, True, ACTION="ready_for_review")
        self.assertEqual(ob, FAST)

    def test_a_docs_push_to_a_code_pr_runs_docs_when_the_previous_head_passed(self):
        ob, calls = self.ob(["runtime/driver/a.py", "CLAUDE.md"], ["CLAUDE.md"], True)
        self.assertEqual(ob, DOCS)
        self.assertEqual(calls, [("o/r", "p")])

    def test_a_docs_push_to_a_code_pr_runs_the_whole_pr_when_the_previous_head_did_not_pass(self):
        """The case the rule exists for: a red run followed by a prose-only fix must not go green."""
        ob, _ = self.ob(["runtime/driver/a.py", "CLAUDE.md"], ["CLAUDE.md"], False)
        self.assertEqual(ob, fast_plus(KEYS, REC, VID, EMUL))

    def test_a_push_runs_only_the_modules_it_touches(self):
        ob, _ = self.ob(["runtime/driver/a.py", "tools/screens/b.py"], ["tools/screens/b.py"], True)
        self.assertEqual(ob, fast_plus(VID))

    def test_an_output_only_push_runs_nothing_only_after_a_pass(self):
        self.assertEqual(self.ob(["tools/harness/x.mjs", "a.log"], ["a.log"], True)[0], NOTHING)
        self.assertEqual(self.ob(["tools/harness/x.mjs", "a.log"], ["a.log"], False)[0], FAST)

    def test_a_push_that_obliges_all_the_pr_does_does_not_ask(self):
        ob, _ = G.decide(ENV, fake_diff(["runtime/driver/a.py", "CLAUDE.md"], ["runtime/driver/a.py"]), must_not_ask)
        self.assertEqual(ob, fast_plus(KEYS, REC, VID, EMUL))

    def test_an_unreadable_diff_runs_everything(self):
        self.assertEqual(G.decide(ENV, fake_diff(None, None), must_not_ask)[0], G.ALL)

    def test_a_force_push_whose_old_head_is_gone_takes_the_whole_pr(self):
        ob, _ = G.decide(ENV, fake_diff(["tools/harness/x.mjs"], None), must_not_ask)
        self.assertEqual(ob, FAST)

    def test_no_before_takes_the_whole_pr(self):
        ob, _ = G.decide({**ENV, "BEFORE": ""}, fake_diff(["tools/harness/x.mjs"], ["CLAUDE.md"]), must_not_ask)
        self.assertEqual(ob, FAST)


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
    def modules(self, mods=()):
        out = set()

        def walk(s):
            for t in s:
                if isinstance(t, unittest.TestSuite):
                    walk(t)
                else:
                    out.add(type(t).__module__.rsplit(".", 1)[-1])
        walk(G.select_suite(mods))
        return out

    def test_the_slow_modules_run_only_when_named(self):
        everything, none = self.modules(G.SLOW), self.modules()
        self.assertIn(EMUL, G.SLOW)
        self.assertTrue(set(G.SLOW) <= everything, set(G.SLOW) - everything)
        self.assertEqual(everything - none, set(G.SLOW))
        one = self.modules([VID])
        self.assertEqual(one - none, {VID})
        self.assertIn("test_ci_gate", none)


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

    def test_the_named_citation_check_runs_in_the_quick_tier_of_both_jobs(self):
        """Issue #307/#310: `named_citations.py check` is a step of the push-to-main `quick` job and, in the
        `checks` job, of the quick tier (not the code tier: a spec-only PR is quick only)."""
        step = "python3 tools/static/named_citations.py check"
        quick_job = self.TEXT.split("  quick:\n", 1)[1].split("  checks:\n", 1)[0]
        self.assertIn(step, quick_job)
        checks_job = self.TEXT.split("  checks:\n", 1)[1]
        i = checks_job.index(step)
        self.assertEqual(checks_job.count(step), 1)
        gate = checks_job[checks_job.rindex("- if:", 0, i):i]
        self.assertIn("steps.gate.outputs.quick == 'true'", gate)
        self.assertNotIn("code", gate)

    def test_the_unit_suite_gets_the_modules_the_gate_chose(self):
        self.assertIn("run-tests --modules=\"${{ steps.gate.outputs.modules }}\"", self.TEXT)

    def test_the_code_tier_installs_the_pinned_unicorn(self):
        """Issue #304: without unicorn the emulator tests skip and their assertions never run in CI."""
        reqs = (ROOT / "runtime/emul/requirements.txt").read_text().split()
        self.assertEqual(reqs, ["unicorn==2.1.4"])
        step = [l for l in self.TEXT.splitlines() if l.strip().startswith("run: pip install")]
        self.assertEqual(len(step), 1)
        self.assertIn("-r runtime/emul/requirements.txt", step[0])
        i = self.TEXT.index(step[0])
        self.assertIn("steps.gate.outputs.code == 'true'", self.TEXT[self.TEXT.rindex("- if:", 0, i):i])

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
