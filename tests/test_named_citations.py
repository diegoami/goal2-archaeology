"""Citations of named-view lines (issue #307): `tools/static/named_citations.py`.

The repository test fails when a line cited in a finding, spec row or experiment note no longer holds the text
recorded in `static/goal-exe/named-citations.tsv`, which is what happens after a regeneration of
`static/goal-exe/named/` moves lines. The other tests run the tool on a throwaway git repository: what counts
as a citation, that a shifted line, an unrecorded citation and an orphan row are each found, and that `remap`
moves a citation to the line that holds its text again. No game file and no network is used."""
import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "static"))
import named_citations as nc  # noqa: E402

BODY = [f"line {i} of the routine" for i in range(1, 41)]
BODY[9] = "x = compute(param_1);"
BODY[10] = "y = x + 1;"
BODY[11] = "return y;"


def named_text(extra_top=0, rename=None):
    lines = ["// header", ""] + ["// inserted"] * extra_top + BODY
    if rename:
        lines = [ln.replace("compute(", rename + "(") for ln in lines]
    return "\n".join(lines) + "\n"


class Repo:
    """A git repository with one named-view part and one document citing it."""

    def __init__(self, tmp, doc_text):
        self.root = Path(tmp)
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            self.git(*args)
        (self.root / "static/goal-exe/named").mkdir(parents=True)
        (self.root / "findings").mkdir()
        self.write_named(named_text())
        (self.root / "findings/F900.md").write_text(doc_text)
        self.commit("start")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=True).stdout.strip()

    def write_named(self, text):
        (self.root / "static/goal-exe/named/seg_0791_01.c").write_text(text)

    def commit(self, msg):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", msg)
        return self.git("rev-parse", "HEAD")

    def doc(self):
        return (self.root / "findings/F900.md").read_text()

    def __enter__(self):
        self.saved = (nc.ROOT, nc.MANIFEST)
        nc.ROOT, nc.MANIFEST = self.root, self.root / "static/goal-exe/named-citations.tsv"
        return self

    def __exit__(self, *exc):
        nc.ROOT, nc.MANIFEST = self.saved


def run(*argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return nc.main(list(argv))


class RepositoryCitations(unittest.TestCase):
    def test_every_cited_named_line_holds_the_text_recorded_for_it(self):
        problems, cited = nc.check()
        self.assertEqual(problems, [])
        self.assertGreater(cited, 100)      # the scan finds the citations: an empty scan would pass


class WhatIsACitation(unittest.TestCase):
    def cites(self, text):
        return [(c.file, [e for e in c.endpoints()]) for c in nc.citations_in("d.md", text)]

    def test_forms(self):
        text = ("`named/seg_0791_09.c:28-67`; `static:static/goal-exe/named/seg_1771_04.c:651`; "
                "`named/seg_0791_06.c:565–572,656`, `seg_000E_04.c:994` and `named/seg_0791_09.c`.")
        self.assertEqual(self.cites(text), [("seg_0791_09.c", [28, 67]), ("seg_1771_04.c", [651]),
                                            ("seg_0791_06.c", [565, 572, 656]), ("seg_000E_04.c", [994])])

    def test_raw_views_and_unprefixed_are_not_named_citations(self):
        text = ("`decompiled/seg_0791_09.c:28`, `seg_0791_08.c:12` after it, `code/seg_0791_22.asm:126`, "
                "and `seg_0791_10.c:5` with no prefix at all.")
        self.assertEqual(self.cites(text), [])


class ChecksOnAThrowawayRepo(unittest.TestCase):
    DOC = "The result is returned (`named/seg_0791_01.c:13-14`).\n"

    def start(self, tmp):
        repo = Repo(tmp, self.DOC)
        repo.__enter__()
        self.addCleanup(repo.__exit__)
        self.assertEqual(run("update"), 0)
        return repo

    def test_a_recorded_citation_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.start(tmp)
            self.assertEqual(nc.check(), ([], 2))
            self.assertIn("x = compute(param_1);", (nc.MANIFEST).read_text())

    def test_a_shifted_line_fails_and_remap_follows_the_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            before = repo.commit("recorded")
            repo.write_named(named_text(extra_top=3))
            problems, _ = nc.check()
            self.assertEqual(len(problems), 2)
            self.assertTrue(all("now holds" in p for p in problems))
            self.assertEqual(run("remap", "--base", before, "--apply"), 0)
            self.assertIn("`named/seg_0791_01.c:16-17`", repo.doc())
            self.assertEqual(nc.check(), ([], 2))

    def test_a_renamed_identifier_on_the_cited_line_fails_until_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            repo.write_named(named_text(rename="calculate"))
            self.assertEqual(len(nc.check()[0]), 1)
            self.assertEqual(run("update"), 1)              # refused: read the line first
            self.assertEqual(len(nc.check()[0]), 1)
            self.assertEqual(run("update", "--accept"), 0)
            self.assertEqual(nc.check()[0], [])

    def test_a_line_past_the_end_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            repo.write_named("// header\n")
            self.assertTrue(all("past the end" in p for p in nc.check()[0]))

    def test_an_unrecorded_citation_and_an_orphan_row_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            (repo.root / "findings/F900.md").write_text(self.DOC + "And `named/seg_0791_01.c:20`.\n")
            self.assertIn("has no row", " ".join(nc.check()[0]))
            (repo.root / "findings/F900.md").write_text("No citation left.\n")
            self.assertIn("has no citation", " ".join(nc.check()[0]))

    def test_authored_view_is_the_one_current_when_the_citation_was_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            repo.commit("recorded")
            repo.write_named(named_text(extra_top=3))
            repo.commit("regenerated: three lines inserted")
            # the document still carries the old numbers: written against the earlier view
            (repo.root / "static/goal-exe/named-citations.tsv").unlink()
            self.assertEqual(run("remap", "--authored", "--apply"), 0)
            self.assertIn("`named/seg_0791_01.c:16-17`", repo.doc())
            self.assertEqual(run("update", "--accept"), 0)
            self.assertEqual(nc.check(), ([], 2))


if __name__ == "__main__":
    unittest.main()
