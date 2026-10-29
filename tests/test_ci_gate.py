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
            "docs/process.md": DOCS,  # no test reads it since the review harness went (2026-10-20)
            "docs/play-guide.md": FAST,
            "docs/match-engine-plan.md": FAST,
            "findings/F001.md": FAST,
            "runs/E014/E014-r0001.json": FAST,
            "tools/check_links.py": FAST,
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

    def test_a_change_obliges_the_union_of_its_files(self):
        self.assertEqual(G.obligations(["CLAUDE.md", "tools/check_links.py"]), FAST)
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
            G.git = lambda *a: Out("CLAUDE.md\n\ntools/check_links.py\n")
            self.assertEqual(G.decide({"EVENT": "schedule"})[0], G.ALL)
            G.git = lambda *a: Out("")
            self.assertEqual(G.decide({"EVENT": "schedule"})[0], NOTHING)
        finally:
            G.git = real

    def test_a_new_pr_obliges_what_its_whole_diff_does(self):
        for action in ("opened", "reopened", "ready_for_review"):
            ob, calls = self.ob(["CLAUDE.md"], None, True, ACTION=action)
            self.assertEqual((ob, calls), (DOCS, []))
        ob, _ = self.ob(["CLAUDE.md", "tools/x.py"], None, True, ACTION="ready_for_review")
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
        self.assertEqual(self.ob(["tools/x.py", "a.log"], ["a.log"], True)[0], NOTHING)
        self.assertEqual(self.ob(["tools/x.py", "a.log"], ["a.log"], False)[0], FAST)

    def test_a_push_that_obliges_all_the_pr_does_does_not_ask(self):
        ob, _ = G.decide(ENV, fake_diff(["runtime/driver/a.py", "CLAUDE.md"], ["runtime/driver/a.py"]), must_not_ask)
        self.assertEqual(ob, fast_plus(KEYS, REC, VID, EMUL))

    def test_an_unreadable_diff_runs_everything(self):
        self.assertEqual(G.decide(ENV, fake_diff(None, None), must_not_ask)[0], G.ALL)

    def test_a_force_push_whose_old_head_is_gone_takes_the_whole_pr(self):
        ob, _ = G.decide(ENV, fake_diff(["tools/x.py"], None), must_not_ask)
        self.assertEqual(ob, FAST)

    def test_no_before_takes_the_whole_pr(self):
        ob, _ = G.decide({**ENV, "BEFORE": ""}, fake_diff(["tools/x.py"], ["CLAUDE.md"]), must_not_ask)
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


class CheckpointGroups(unittest.TestCase):
    @staticmethod
    def ids(suite):
        return [t.id() for t in G.flatten(suite)]

    def test_partition_is_the_exact_disjoint_union_including_future_tests(self):
        suite=G.select_suite(G.SLOW)
        class Future(unittest.TestCase):
            def runTest(self):pass
        future=Future();suite.addTest(future)
        wanted=self.ids(suite)
        groups={group:self.ids(G.partition_suite(suite,group)) for group in G.TEST_GROUPS}
        actual=[case for cases in groups.values() for case in cases]
        self.assertEqual(len(actual),len(set(actual)))
        self.assertCountEqual(actual,wanted)
        self.assertIn(future.id(),groups['general'])
        self.assertEqual(len(groups),11)
        for group,case in G.BOUNDARY_CASES.items():
            self.assertEqual(len(groups[group]),1)
            self.assertTrue(groups[group][0].endswith(case))

    def test_unknown_missing_or_duplicate_boundaries_are_refused(self):
        suite=G.select_suite()
        with self.assertRaises(ValueError):G.partition_suite(suite,'unknown')
        with self.assertRaises(ValueError):G.partition_suite(unittest.TestSuite(),'general')
        all_tests=list(G.flatten(suite))
        target=next(t for t in all_tests if t.id().endswith(G.BOUNDARY_CASES['e034-02']))
        with self.assertRaises(ValueError):
            G.partition_suite(unittest.TestSuite([*all_tests,target]),'general')

    def test_every_matrix_check_must_succeed_at_the_same_head(self):
        def ask(rows):
            return G.previous_head_succeeded('owner/repo','abc',
                lambda *a,**k:type('Reply',(),dict(returncode=0,stdout=json.dumps({'check_runs':rows})))())
        rows=[dict(name=f'checks ({group})',conclusion='success') for group in G.TEST_GROUPS]
        self.assertTrue(ask(rows))
        for bad in ('failure','cancelled','skipped',None):
            broken=[dict(row) for row in rows];broken[3]['conclusion']=bad
            self.assertFalse(ask(broken))
        self.assertFalse(ask(rows[:-1]))
        self.assertFalse(ask([*rows,rows[0]]))
        self.assertFalse(ask([dict(name='checks',conclusion='success'),*rows[:-1]]))

    @staticmethod
    def complete_execution(suite=1):
        return [dict(name=f'checks ({group})',conclusion='success',check_suite={'id':suite})
                for group in G.TEST_GROUPS]

    @staticmethod
    def response(rows):
        return type('Reply',(),dict(returncode=0,stdout=json.dumps({'check_runs':rows})))()

    def test_old_skipped_draft_placeholder_does_not_shadow_real_success(self):
        rows=self.complete_execution()
        rows.append(dict(name='checks (${{ matrix.group }})',conclusion='skipped',check_suite={'id':2}))
        self.assertTrue(G.previous_head_succeeded('owner/repo','abc',lambda *a,**k:self.response(rows)))

    def test_groups_from_separate_executions_never_assemble_success(self):
        rows=self.complete_execution()
        for row in rows[5:]:row['check_suite']={'id':2}
        self.assertFalse(G.previous_head_succeeded('owner/repo','abc',lambda *a,**k:self.response(rows)))
        rows=self.complete_execution()+self.complete_execution(2)
        self.assertFalse(G.previous_head_succeeded('owner/repo','abc',lambda *a,**k:self.response(rows)))

    def test_only_verified_metadata_chain_can_reuse_complete_source(self):
        rows={'meta':[], 'source':self.complete_execution()}
        def api(command,**kwargs):return self.response(rows[command[2].split('/commits/')[1].split('/')[0]])
        parents=lambda sha:'source' if sha=='meta' else None
        self.assertTrue(G.previous_head_succeeded('owner/repo','meta',api,predecessor=parents))
        self.assertFalse(G.previous_head_succeeded('owner/repo','meta',api,predecessor=lambda sha:None))
        rows['meta']=[dict(name='checks (general)',conclusion='failure',check_suite={'id':2})]
        self.assertFalse(G.previous_head_succeeded('owner/repo','meta',api,predecessor=parents))
        for bad in ('cancelled','skipped',None):
            rows['meta'][0]['conclusion']=bad
            self.assertFalse(G.previous_head_succeeded('owner/repo','meta',api,predecessor=parents))

    def test_metadata_parent_checks_actual_git_diff_and_stops_at_source_changes(self):
        from unittest.mock import patch
        def reply(text,code=0):return type('Git',(),dict(returncode=code,stdout=text))()
        for paths,expected in ((['experiments/E036-match-port/out/T78c/a.json','notes/T78c.md'],'parent'),
                               (['experiments/E036-match-port/notes/T78c.md'],None),
                               (['runtime/original_match/match.py'],None),
                               (['tests/test_port_engine.py'],None),
                               (['tools/ci_gate.py'],None),
                               (['docs/play-guide.md'],None)):
            with self.subTest(paths=paths):
                with patch.object(G,'git',side_effect=[reply('parent\n'),reply('\n'.join(paths)+'\n')]):
                    self.assertEqual(G.metadata_parent('head'),expected)
        with patch.object(G,'git',return_value=reply('',1)):
            self.assertIsNone(G.metadata_parent('head'))

    def test_longest_measured_cases_start_with_general_in_the_first_four_slots(self):
        self.assertEqual(G.TEST_GROUPS[:4],('general','e034-01','e033-06','e034-02'))

    def test_workflow_runs_all_groups_without_fast_fail_or_recorder_setup_in_boundary_jobs(self):
        text=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('max-parallel: 4',text)
        self.assertIn('fail-fast: false',text)
        self.assertIn('--group="${{ matrix.group }}"',text)
        self.assertIn("matrix.group == 'general'",text)
        self.assertIn('group: ['+', '.join(G.TEST_GROUPS)+']',text)


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
