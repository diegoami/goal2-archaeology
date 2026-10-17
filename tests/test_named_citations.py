"""Citations of named-view lines (issues #307, #310): `tools/static/named_citations.py`.

The repository test fails when a line or range cited in a finding, spec row or experiment note no longer holds
the text recorded for it in `static/goal-exe/named-citations.tsv` (what happens after a regeneration of
`static/goal-exe/named/` moves lines, or when a line inside a cited range changes), when a citation has no row,
or when text that looks like a citation cannot be parsed. The other tests run the tool on a throwaway git
repository: every citation form the repository uses, the failures above, and that `remap` moves a citation (both
ends of a range, an abbreviated one) to the lines that hold its text again. No game file and no network is used."""
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


def named_text(extra_top=0, rename=None, interior=None):
    """Lines 1-2 a header, then `extra_top` inserted lines, then BODY (body line k is file line k + 2 + extra_top)."""
    body = list(BODY)
    if interior:
        body[interior] = body[interior] + " /* changed */"
    lines = ["// header", ""] + ["// inserted"] * extra_top + body
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
        self.write_doc(doc_text)
        self.commit("start")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, capture_output=True, text=True, check=True).stdout.strip()

    def write_named(self, text):
        (self.root / "static/goal-exe/named/seg_0791_01.c").write_text(text)

    def write_doc(self, text):
        (self.root / "findings/F900.md").write_text(text)

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
    def test_every_cited_named_range_holds_the_text_recorded_for_it(self):
        problems, cited = nc.check()
        self.assertEqual(problems, [])
        self.assertGreater(cited, 100)      # the scan finds the citations: an empty scan would pass

    def test_the_repository_uses_the_forms_the_parser_handles(self):
        cites = nc.all_cites()
        self.assertTrue(any(sep == ".." for c in cites for _a, sep, _b in c.items), "no `..` range found")
        self.assertTrue(any(c.abbreviated for c in cites), "no abbreviated citation found")
        self.assertTrue(any(sep == "–" for c in cites for _a, sep, _b in c.items), "no en-dash range found")
        self.assertTrue(any(sep == "-" for c in cites for _a, sep, _b in c.items), "no hyphen range found")


class WhatIsACitation(unittest.TestCase):
    def ranges(self, text):
        return [(c.file, c.ranges()) for c in nc.citations_in("d.md", text)]

    def test_every_form(self):
        text = ("`named/seg_0791_09.c:28-67`; `static:static/goal-exe/named/seg_1771_04.c:651`; "
                "`named/seg_0791_06.c:565–572,656`, `seg_000E_04.c:994`; `named/seg_0791_09.c:540..548`; "
                "`named/seg_0791_09.c:890..922`; and `named/seg_0791_09.c`: the whole routine, `named/seg_0791_09.c`. Or 5.")
        self.assertEqual(self.ranges(text), [("seg_0791_09.c", [(28, 67)]), ("seg_1771_04.c", [(651, 651)]),
                                             ("seg_0791_06.c", [(565, 572), (656, 656)]), ("seg_000E_04.c", [(994, 994)]),
                                             ("seg_0791_09.c", [(540, 548)]), ("seg_0791_09.c", [(890, 922)])])

    def test_both_ends_of_a_dotted_range_are_cited_lines(self):
        (c,) = nc.citations_in("d.md", "`named/seg_0791_06.c:1087..463`")
        self.assertEqual(list(c.endpoints()), [1087, 463])

    def test_an_abbreviated_citation_takes_the_file_of_the_one_before_it(self):
        text = "calls (`named/seg_0791_05.c:906–908`);\n  the reaction (`:628..643`); and a bare `:12` later.\n"
        got = nc.citations_in("d.md", text)
        self.assertEqual([(c.file, c.ranges(), c.abbreviated) for c in got],
                         [("seg_0791_05.c", [(906, 908)], False), ("seg_0791_05.c", [(628, 643)], True),
                          ("seg_0791_05.c", [(12, 12)], True)])

    def test_an_abbreviated_citation_after_a_raw_view_or_far_away_is_not_a_named_one(self):
        self.assertEqual(nc.citations_in("d.md", "`code/seg_0791_13.asm:1-2` then `:557`"), [])
        self.assertEqual(nc.citations_in("d.md", "`seg_000E_06.asm:549-725` shows it at `:557`"), [])
        far = nc.citations_in("d.md", "`named/seg_0791_05.c:906`\n\n\nlater `:628`")
        self.assertEqual([c.ranges() for c in far], [[(906, 906)]])

    def test_raw_views_and_unprefixed_are_not_named_citations(self):
        text = ("`decompiled/seg_0791_09.c:28`, `seg_0791_08.c:12` after it, `code/seg_0791_22.asm:126`, "
                "and `seg_0791_10.c:5` with no prefix at all.")
        self.assertEqual(self.ranges(text), [])

    def test_text_that_looks_like_a_citation_and_is_not_parsable_is_an_error(self):
        for bad in ("`named/seg_0791_09.c:12abc`", "`named/seg_0791_09.c:3-4-5`", "`named/seg_0791_09.c:12.5`",
                    "`named/seg_0791_09.c:7–9–11`", "`named/seg_0791_09.c`, lines 5 and 7",
                    "`named/seg_0791_09.c:5`, `:6x`",
                    # the round-2 repros: a colon that is not followed by a line list, and continuations
                    "See `named/seg_0791_09.c:garbage`.", "`named/seg_0791_09.c:12, 15`", "`named/seg_0791_09.c:12—15`",
                    "`named/seg_0791_09.c:890..`", "`named/seg_0791_09.c:12:34`", "`named/seg_0791_09.c:12 and 15`",
                    "`named/seg_0791_09.c:`", "`named/seg_0791_09.c:12-`", "`static:static/goal-exe/named/seg_0791_09.c:x`",
                    "`named/seg_0791_09.c:5`, `seg_0791_08.c:garbage`",
                    "`named/seg_0791_05.c:906`;\n(`:12, 15`)", "`named/seg_0791_05.c:906`;\n(`:12 and 15`)",
                    "`named/seg_0791_05.c:906`;\n(`:12—15`)", "`named/seg_0791_05.c:906`;\n(`:12..`)",
                    "`named/seg_0791_05.c:906`;\n(`:12"):
            with self.subTest(bad=bad):
                cites, errors = nc.scan("d.md", bad)
                self.assertEqual(len(errors), 1, (cites, errors))
                with self.assertRaises(nc.CitationError):
                    nc.citations_in("d.md", bad)

    def test_a_colon_in_prose_after_a_file_name_is_not_a_citation(self):
        for ok in ("`named/seg_0791_09.c`: the routine", "named/seg_0791_09.c: the routine", "see named/seg_0791_09.c:",
                   "`named/seg_0791_09.c`, `named/seg_0791_08.c` and `named/seg_0791_07.c`"):
            with self.subTest(ok=ok):
                self.assertEqual(nc.scan("d.md", ok), ([], []))

    def test_a_sentence_ending_after_a_citation_is_not_an_error(self):
        self.assertEqual(nc.scan("d.md", "See `named/seg_0791_09.c:12`. And `named/seg_0791_09.c:5-7`, then")[1], [])


class ChecksOnAThrowawayRepo(unittest.TestCase):
    DOC = "The result is returned (`named/seg_0791_01.c:13-14`).\n"

    def start(self, tmp, doc=None):
        repo = Repo(tmp, doc or self.DOC)
        repo.__enter__()
        self.addCleanup(repo.__exit__)
        self.assertEqual(run("update"), 0)
        return repo

    def test_a_recorded_citation_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.start(tmp)
            self.assertEqual(nc.check(), ([], 1))
            self.assertIn("seg_0791_01.c:13-14", nc.MANIFEST.read_text())

    def test_a_shifted_line_fails_and_remap_follows_the_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            before = repo.commit("recorded")
            repo.write_named(named_text(extra_top=3))
            problems, _ = nc.check()
            self.assertEqual(len(problems), 1)
            self.assertIn("no longer holds", problems[0])
            self.assertEqual(run("remap", "--base", before, "--apply"), 0)
            self.assertIn("`named/seg_0791_01.c:16-17`", repo.doc())
            self.assertEqual(nc.check(), ([], 1))

    def test_a_dotted_range_is_moved_at_both_ends(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp, "A range (`named/seg_0791_01.c:13..20`), and a long one (`named/seg_0791_01.c:30..38`).\n")
            before = repo.commit("recorded")
            repo.write_named(named_text(extra_top=3))
            self.assertEqual(run("remap", "--base", before, "--apply"), 0)
            self.assertIn("`named/seg_0791_01.c:16..23`", repo.doc())
            self.assertIn("`named/seg_0791_01.c:33..41`", repo.doc())
            self.assertEqual(nc.check(), ([], 2))

    def test_a_malformed_citation_appended_to_a_document_fails_the_check(self):
        """Round 2: `` `named/...c:garbage` `` was taken for a file-only reference and passed."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            for bad in ("See `named/seg_0791_01.c:garbage`.", "See `named/seg_0791_01.c:13, 15`.",
                        "See `named/seg_0791_01.c:13—15`.", "See `named/seg_0791_01.c:30..`."):
                with self.subTest(bad=bad):
                    repo.write_doc(self.DOC + bad + "\n")
                    self.assertIn("cannot parse", " ".join(nc.check()[0]))
                    self.assertEqual(run("update"), 1)
            repo.write_doc(self.DOC)
            self.assertEqual(nc.check()[0], [])

    def test_the_whole_cited_tail_of_a_range_is_protected_because_open_ranges_are_refused(self):
        """Round 2: `N..` was recorded as the single line N, so a change further down passed."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp, "From here on (`named/seg_0791_01.c:13..40`).\n")
            repo.write_named(named_text(interior=27))
            self.assertEqual(len(nc.check()[0]), 1)

    def test_an_abbreviated_citation_is_moved_with_the_one_before_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp, "Calls (`named/seg_0791_01.c:13–14`);\nthe reaction (`:20..22`).\n")
            before = repo.commit("recorded")
            repo.write_named(named_text(extra_top=3))
            self.assertEqual(run("remap", "--base", before, "--apply"), 0)
            self.assertIn("(`:23..25`)", repo.doc())
            self.assertIn("`named/seg_0791_01.c:16–17`", repo.doc())
            self.assertEqual(nc.check(), ([], 2))

    def test_a_change_inside_a_cited_range_fails(self):
        """The ends and their neighbours are as recorded; line 30 of the range 13-40 is not."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp, "The routine (`named/seg_0791_01.c:13-40`).\n")
            repo.write_named(named_text(interior=27))          # body line 28 = file line 30
            problems, _ = nc.check()
            self.assertEqual(len(problems), 1)
            self.assertIn("a line inside it", problems[0])
            self.assertEqual(run("update"), 1)
            self.assertEqual(run("update", "--accept"), 0)
            self.assertEqual(nc.check()[0], [])

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
            repo.write_doc(self.DOC + "And `named/seg_0791_01.c:20`.\n")
            self.assertIn("has no row", " ".join(nc.check()[0]))
            repo.write_doc("No citation left.\n")
            self.assertIn("has no citation", " ".join(nc.check()[0]))

    def test_an_unparsable_citation_fails_the_check_and_the_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            repo.write_doc(self.DOC + "Bad: `named/seg_0791_01.c:13-14-15`.\n")
            self.assertIn("cannot parse", " ".join(nc.check()[0]))
            self.assertEqual(run("update"), 1)

    def test_authored_view_is_the_one_current_when_the_citation_was_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.start(tmp)
            repo.commit("recorded")
            repo.write_named(named_text(extra_top=3))
            repo.commit("regenerated: three lines inserted")
            # the document still carries the old numbers: written against the earlier view
            nc.MANIFEST.unlink()
            self.assertEqual(run("remap", "--authored", "--apply"), 0)
            self.assertIn("`named/seg_0791_01.c:16-17`", repo.doc())
            self.assertEqual(nc.check(), ([], 1))


if __name__ == "__main__":
    unittest.main()
