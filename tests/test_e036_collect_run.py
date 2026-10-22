"""experiments/E036-match-port/collect_run.sh, the collector of .github/workflows/family-run.yml (#361, #364).

The script runs as the workflow runs it: in a clone of a scratch origin on the dispatched branch, with the workflow's
environment. A re-run of the same run ("Re-run all jobs": the same run id, the next attempt) writes a folder of its own
and pushes; before #364 its rebase stopped on an add/add conflict in the first attempt's manifest.json."""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_e036_compare import ROOT, E036, FAMILIES, record  # noqa: E402

SCRIPT = E036 / "collect_run.sh"
BRANCH = "task/T99-scratch"


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


@unittest.skipUnless(shutil.which("git"), "git is not installed")
class CollectRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        # the scratch origin: the code the collector runs (shards.py and what it imports), on the branch
        seed = self.d / "seed"
        ignore = shutil.ignore_patterns("__pycache__", "out")
        shutil.copytree(E036, seed / "experiments/E036-match-port", ignore=ignore)
        shutil.copytree(ROOT / "runtime", seed / "runtime", ignore=ignore)
        git(seed, "init", "-q", "-b", BRANCH)
        git(seed, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
        git(seed, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "seed")
        self.origin = self.d / "origin.git"
        git(self.d, "clone", "-q", "--bare", str(seed), str(self.origin))
        self.sha = git(seed, "rev-parse", "HEAD").strip()
        self.ids = [m.id for m in FAMILIES["O8"].matches][:2]

    def tearDown(self):
        self.tmp.cleanup()

    def attempt(self, n, ids=None):
        """One collector in a fresh clone at the dispatch commit, as attempt n of run 123; (exit status, output)."""
        work = self.d / f"attempt-{n}"
        git(self.d, "clone", "-q", "-b", BRANCH, str(self.origin), str(work))
        git(work, "reset", "-q", "--hard", self.sha)              # every attempt starts from the dispatched commit
        shards = work / "shards"
        shards.mkdir()
        for i, mid in enumerate(ids or self.ids):
            (shards / f"shard-{i}.jsonl").write_text(json.dumps(record(mid)) + "\n")
            (shards / f"shard-{i}-run.txt").write_text("exit 0\n")
        env = dict(os.environ, TASK="T99", NAME="all-actions", FAMILY="O8", ONLY=",".join(self.ids), INPUTS="{}",
                   GITHUB_RUN_ID="123", GITHUB_RUN_ATTEMPT=str(n), GITHUB_WORKFLOW="E036 family run",
                   GITHUB_REF_NAME=BRANCH, GITHUB_SHA=self.sha, GITHUB_SERVER_URL="https://github.com",
                   GITHUB_REPOSITORY="o/r", RETRY_SLEEP="0", GIT_TERMINAL_PROMPT="0")
        p = subprocess.run(["bash", str(SCRIPT)], cwd=work, env=env, capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def tip_files(self):
        listing = git(self.origin, "ls-tree", "-r", "--name-only", BRANCH)
        return sorted(l for l in listing.splitlines() if l.startswith("experiments/E036-match-port/out/"))

    def test_a_rerun_of_the_same_run_writes_its_own_folder_and_both_are_pushed(self):
        code1, out1 = self.attempt(1)
        self.assertEqual(code1, 0, out1)
        code2, out2 = self.attempt(2)
        self.assertEqual(code2, 0, out2)
        base = "experiments/E036-match-port/out/T99/"
        files = self.tip_files()
        for folder, attempt in (("all-actions-123/", "1"), ("all-actions-123-attempt-2/", "2")):
            self.assertIn(base + folder + "all-actions.jsonl", files)
            manifest = json.loads(git(self.origin, "show", f"{BRANCH}:{base}{folder}manifest.json"))
            self.assertEqual((manifest["run_id"], manifest["run_attempt"]), ("123", attempt))
        joined = git(self.origin, "show", f"{BRANCH}:{base}all-actions-123/all-actions.jsonl").splitlines()
        self.assertEqual([json.loads(l)["id"] for l in joined], self.ids)

    def test_a_refused_join_commits_the_shards_and_fails(self):
        code, out = self.attempt(1, ids=self.ids[:1])            # a shard missing: the join is refused
        self.assertEqual(code, 2, out)
        base = "experiments/E036-match-port/out/T99/all-actions-123/"
        files = self.tip_files()
        self.assertIn(base + "shard-0.jsonl", files)             # the shards are committed all the same
        self.assertNotIn(base + "all-actions.jsonl", files)
        self.assertIn("exit 2", git(self.origin, "show", f"{BRANCH}:{base}collect.txt"))


if __name__ == "__main__":
    unittest.main()
