"""E031's checks fail closed (PR 242 review round 2): a failing producer, an emptied saves table, an
emptied log or evidence file, an empty claims table, a guide sentence without backing, and an extra or
corrupted save all make the check fail. No game is run, no network is used."""
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / "experiments" / "E031-play-the-game"
sys.path.insert(0, str(E))
import checks  # noqa: E402
import claims  # noqa: E402
import verify_saves  # noqa: E402


def evidence_copy(tmp):
    """A copy of E031's evidence (claims.tsv, out/ tables) with the session logs linked, not copied."""
    base = Path(tmp) / "e031"
    (base / "out").mkdir(parents=True)
    shutil.copy(E / "claims.tsv", base / "claims.tsv")
    for d in (E / "out").iterdir():
        if d.is_dir():
            (base / "out" / d.name).mkdir()
            for f in d.iterdir():
                (base / "out" / d.name / f.name).symlink_to(f)
        else:
            shutil.copy(d, base / "out" / d.name)
    return base


def replace(path, text):
    path = Path(path)
    if path.is_symlink():
        path.unlink()
    path.write_text(text)


class ChecksRunner(unittest.TestCase):
    def test_a_failing_producer_fails_the_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "checks.txt"
            rc = checks.run([("ok", ["true"], 1), ("broken", ["false"], 1), ("after", ["true"], 1)], out)
            self.assertEqual(rc, 1)
            self.assertTrue(out.read_text().rstrip().endswith("FAILED: broken"))

    def test_all_passing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "checks.txt"
            self.assertEqual(checks.run([("ok", ["true"], 1)], out), 0)
            self.assertTrue(out.read_text().rstrip().endswith("ALL PASSED"))

    def test_checks_sh_propagates_the_exit_status(self):
        text = (E / "checks.sh").read_text()
        self.assertIn("set -euo pipefail", text)
        self.assertNotIn("| tail", text)


class Claims(unittest.TestCase):
    GUIDE = ROOT / "docs" / "play-guide.md"

    def problems(self, base, guide=None):
        return claims.run(base, guide or self.GUIDE, None)[3]

    def test_the_real_evidence_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.problems(evidence_copy(tmp)), [])

    def test_an_emptied_saves_table_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = evidence_copy(tmp)
            replace(base / "out" / "saves.tsv", "")
            self.assertTrue(any("C25c" in p for p in self.problems(base)))

    def test_an_emptied_evidence_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = evidence_copy(tmp)
            replace(base / "out" / "g1" / "game-folder.tsv", "")
            self.assertTrue(any("C42d" in p for p in self.problems(base)))

    def test_an_emptied_session_log_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = evidence_copy(tmp)
            replace(base / "out" / "g1" / "screens.jsonl", "")
            self.assertTrue(any("NOT FOUND" in p for p in self.problems(base)))

    def test_an_empty_claims_table_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = evidence_copy(tmp)
            replace(base / "claims.tsv", "id\tclaim\tkind\tsession\tstep\tneedle\n")
            self.assertIn("claims.tsv has no rows", self.problems(base))

    def test_a_guide_sentence_without_backing_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = evidence_copy(tmp)
            guide = Path(tmp) / "guide.md"
            guide.write_text(self.GUIDE.read_text().replace("## 9.", "The game is easy.\n\n## 9.", 1))
            self.assertTrue(any("no tag or label" in p for p in self.problems(base, guide)))

    def test_a_row_no_sentence_cites_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = evidence_copy(tmp)
            guide = Path(tmp) / "guide.md"
            guide.write_text(self.GUIDE.read_text().replace("[C60]", "(*manual*)"))
            self.assertTrue(any("C60" in p and "cited by no" in p for p in self.problems(base, guide)))


class VerifySaves(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        data = b"x" * 10
        (self.dir / "A.GL").write_bytes(data)
        self.rows = [{"file": "A.GL", "bytes": "10", "sha256": hashlib.sha256(data).hexdigest()}]

    def tearDown(self):
        self.tmp.cleanup()

    def test_matching(self):
        self.assertEqual(verify_saves.compare(self.rows, self.dir), [])

    def test_an_empty_table_fails(self):
        self.assertIn("saves.tsv has no rows", verify_saves.compare([], self.dir))

    def test_a_changed_file_fails(self):
        (self.dir / "A.GL").write_bytes(b"y" * 10)
        self.assertTrue(verify_saves.compare(self.rows, self.dir)[0].startswith("BAD"))

    def test_an_unlisted_file_fails(self):
        (self.dir / "B.GL").write_bytes(b"z")
        self.assertTrue(any(p.startswith("UNLISTED") for p in verify_saves.compare(self.rows, self.dir)))


class Progress(unittest.TestCase):
    def test_an_empty_log_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "x").mkdir()
            (Path(tmp) / "x" / "steps.jsonl").write_text("")
            (Path(tmp) / "x" / "screens.jsonl").write_text("")
            p = subprocess.run([sys.executable, str(E / "progress.py"), "x", "--out-dir", tmp],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 1)


if __name__ == "__main__":
    unittest.main()
