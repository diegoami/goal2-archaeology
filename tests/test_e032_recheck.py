"""E032's recheck fails closed when an expected input is missing, broken or extra (PR 243 review round 5).

Builds a fixture repository in a temp dir: the E032 scripts under test (compare.py, record_schema.py,
recheck.sh and, when present, recheck.py) and the committed state the manifest names (recheck.LOGS and
recheck.TRANSCRIPTS of the CURRENT recheck.py, copied from out/), then runs `sh .../recheck.sh` from the
fixture's root. The full fixture must pass (exit 0); with any one transcript removed, any one log removed,
any one log replaced by `{}`, only the seven logs the round-4 script read after its loop, an unexpected extra
log, or a transcript that does not end with `batch exit 0`, it must exit 2. No emulator runs.

The scripts under test come from E032_RECHECK_DIR (a directory) when set, which is how these tests were shown
to fail on 23fc03a's recheck.sh (whose loop skipped a stamp when its pilot transcript was missing)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E032 = ROOT / "experiments/E032-match-engine-inventory"
SCRIPTS = Path(os.environ.get("E032_RECHECK_DIR", E032))
sys.path.insert(0, str(E032))
import recheck  # noqa: E402  (the manifest: the committed state the fixture copies)

AFTER_LOOP = ["timing-plain-20261015.jsonl", "timing-delay20-kickoff-20261015.jsonl", "timing-plain-8seeds-20261015.jsonl",
              "timing-delay20-8seeds-20261015.jsonl", "timing-delay20-20261015.jsonl",
              "skip-0791-8E24_0791-9079_0791-0481_0791-1829_0791-0425_0791-0441_0791-94E8-20261015.jsonl",
              "pilot-exact-try1-20261015.jsonl"]


class RecheckFailsClosed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.n = 0

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def fixture(self, logs=None, transcripts=None):
        self.__class__.n += 1
        root = Path(self.tmp.name) / f"f{self.n}"
        d = root / "experiments/E032-match-engine-inventory"
        (d / "out").mkdir(parents=True)
        for s in ("compare.py", "record_schema.py", "recheck.sh", "recheck.py"):
            if (SCRIPTS / s).is_file():
                shutil.copy(SCRIPTS / s, d / s)
        for n in (recheck.LOGS if logs is None else logs):
            shutil.copy(E032 / "out" / n, d / "out" / n)
        for n in (recheck.TRANSCRIPTS if transcripts is None else transcripts):
            shutil.copy(E032 / "out" / n, d / "out" / n)
        return root, d / "out"

    def run_recheck(self, root):
        return subprocess.run(["sh", "experiments/E032-match-engine-inventory/recheck.sh"], cwd=root,
                              capture_output=True, text=True, timeout=600)

    def test_the_full_state_passes(self):
        root, _ = self.fixture()
        r = self.run_recheck(root)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:])

    def test_each_missing_transcript_fails(self):
        bad = []
        for t in recheck.TRANSCRIPTS:
            root, _ = self.fixture(transcripts=[x for x in recheck.TRANSCRIPTS if x != t])
            rc = self.run_recheck(root).returncode
            if rc != 2:
                bad.append(f"without {t}: exit {rc}")
        self.assertEqual(bad, [])

    def test_each_missing_log_fails(self):
        bad = []
        for log in recheck.LOGS:
            root, _ = self.fixture(logs=[x for x in recheck.LOGS if x != log])
            rc = self.run_recheck(root).returncode
            if rc != 2:
                bad.append(f"without {log}: exit {rc}")
        self.assertEqual(bad, [])

    def test_each_log_replaced_by_an_empty_object_fails(self):
        bad = []
        for log in recheck.LOGS:
            root, out = self.fixture()
            (out / log).write_text("{}\n")
            rc = self.run_recheck(root).returncode
            if rc != 2:
                bad.append(f"{log} as {{}}: exit {rc}")
        self.assertEqual(bad, [])

    def test_only_the_seven_logs_after_the_old_loop_fails(self):
        root, _ = self.fixture(logs=AFTER_LOOP, transcripts=[])
        self.assertEqual(self.run_recheck(root).returncode, 2)

    def test_an_unexpected_log_fails(self):
        root, out = self.fixture()
        shutil.copy(out / recheck.LOGS[0], out / "extra-20261016.jsonl")
        self.assertEqual(self.run_recheck(root).returncode, 2)

    def test_a_transcript_without_a_clean_end_fails(self):
        root, out = self.fixture()
        t = out / "pilot-batch-review4.txt"
        t.write_text(t.read_text().replace("batch exit 0", "batch exit 2"))
        self.assertEqual(self.run_recheck(root).returncode, 2)


if __name__ == "__main__":
    unittest.main()
