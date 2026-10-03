#!/usr/bin/env python3
"""Tests for check_quotes.py on a small invented help file, in memory. Run: python3 sources/test_check_quotes.py"""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_quotes as cq

HLP = b"alpha one\r\n  beta two\r\n\r\ngamma three\r\ndelta four\r\n\x1a"
SHA = hashlib.sha256(HLP).hexdigest()


def page(*passages, sha=SHA):
    head = [f"Artifact sha256 `{sha}`.", ""] if sha else ["No hash here.", ""]
    body = []
    for pid, lines, quote in passages:
        body += [f"#### {pid}", f"Lines {lines}", "", "```text", *quote, "```", ""]
    return "\n".join(head + body)


GOOD = page(("P01", "1", ["alpha one"]), ("P02", "2–4", ["  beta two", "", "gamma three"]))


class Quotes(unittest.TestCase):
    def test_exact_quotes_pass(self):
        self.assertEqual(cq.check_quotes(GOOD, HLP), (2, []))

    def test_cr_is_dropped_and_eof_byte_is_not_a_line(self):
        self.assertEqual(cq.hlp_lines(HLP), ["alpha one", "  beta two", "", "gamma three", "delta four"])

    def test_changed_word_fails(self):
        md = page(("P01", "1", ["alpha won"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_lost_indentation_fails(self):
        md = page(("P01", "2", ["beta two"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_quote_stretched_past_its_lines_fails(self):
        md = page(("P01", "1", ["alpha one", "  beta two"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_quote_short_of_its_lines_fails(self):
        md = page(("P01", "1–2", ["alpha one"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_wrong_line_numbers_fail(self):
        md = page(("P01", "5", ["gamma three"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_lines_past_the_end_fail(self):
        md = page(("P01", "5–6", ["delta four", "\x1a"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_wrong_sha_fails(self):
        md = page(("P01", "1", ["alpha one"]), sha="0" * 64)
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_missing_sha_fails(self):
        md = page(("P01", "1", ["alpha one"]), sha=None)
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_duplicate_id_fails(self):
        md = page(("P01", "1", ["alpha one"]), ("P01", "1", ["alpha one"]))
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)

    def test_unclosed_block_fails(self):
        md = f"sha256 `{SHA}`\n#### P01\nLines 1\n\n```text\nalpha one\n"
        n, bad = cq.check_quotes(md, HLP)
        self.assertEqual((n, len(bad)), (0, 1))

    def test_heading_without_lines_fails(self):
        md = f"sha256 `{SHA}`\n#### P01\nalpha one\n"
        self.assertEqual(len(cq.check_quotes(md, HLP)[1]), 1)


def row(area, status, src="[1](sources/goal-hlp.md#p01)"):
    return f"| {area} | {status} | needs | {src} |"


KM = "| Area | Status | Needs | Source |\n| --- | --- | --- | --- |\n"


class Map(unittest.TestCase):
    def test_documented_with_a_link_passes(self):
        self.assertEqual(cq.check_map(KM + row("A", "`documented` (basis `doc`)"), GOOD), [])

    def test_documented_without_a_link_fails(self):
        self.assertEqual(len(cq.check_map(KM + row("A", "`documented` (basis `doc`)", "10"), GOOD)), 1)

    def test_link_to_a_missing_passage_fails(self):
        src = "[1](sources/goal-hlp.md#p09)"
        self.assertEqual(len(cq.check_map(KM + row("A", "`documented`", src), GOOD)), 1)

    def test_unknown_with_a_reason_passes(self):
        status = "`unknown`, the help file only names it"
        self.assertEqual(cq.check_map(KM + row("A", status, "—"), GOOD), [])

    def test_unknown_without_a_reason_fails(self):
        self.assertEqual(len(cq.check_map(KM + row("A", "`unknown`", "—"), GOOD)), 1)

    def test_a_status_above_documented_fails(self):
        for status in ("`supported`", "`corroborated`", "`hypothesis`"):
            self.assertEqual(len(cq.check_map(KM + row("A", status), GOOD)), 1, status)


if __name__ == "__main__":
    unittest.main()
