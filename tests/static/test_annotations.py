"""T20: the annotations (static/goal-exe/annotations/), their checker and the named view (named/).

- CheckerTests run tools/static/check_annotations.py on a copy of the committed annotations with
  one defect each; every check fails its defect and the committed annotations pass.
- CommittedTests check the committed annotations: every routine a finding cited when T20 was
  written is named, every run-time library routine is labelled.
- NamedViewTests check the committed named/: 1771:10E7 reads the country's three rating fields by
  name and 0791:BBFF stores +0x2D by its field name, where decompiled/ shows offsets; named.py's
  output layout on a made-up input.
"""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "tools" / "static"))

import check_annotations  # noqa: E402
import decompiled  # noqa: E402
import named  # noqa: E402

ANNOTATIONS = ROOT / "static" / "goal-exe" / "annotations"
NAMED = ROOT / "static" / "goal-exe" / "named"
RAW = ROOT / "static" / "goal-exe" / "decompiled"

# The routines T20's Evidence lists as established by a finding (F004..F008) or as its leads.
FINDING_CITED = [
    "1771:97CC", "1771:96D3", "1771:10E7", "1771:9A40", "1771:3947", "1771:3BD3", "1771:3B3F",
    "1771:3AE2", "214B:0688", "214B:06B1", "214B:06D0", "214B:06FA", "23E4:11D7", "214B:1DA7",
    "214B:0D90", "0791:94C9", "0791:94E8", "0791:9564", "0791:D733", "0791:97D0", "0791:9372",
    "0791:A4A1", "0791:A10A", "1771:6730", "1771:76B1",
    # T20 rework round 1: the routines F004..F008 establish beyond that list (F008's player screen)
    "0791:0425", "0791:92FC", "0791:970C", "0791:CC2E", "0791:F1F6", "0791:F3F2", "1771:0B77",
    "1771:0E24", "1771:0F58", "1771:2D15", "1771:2E20", "1771:2E93", "1771:2F37", "1771:2FAD",
    "1771:2FFB", "1771:3041", "1771:3088", "1771:30D9", "1771:3291", "1771:32EB", "1771:3431",
    "1771:3558", "1771:42BC", "1771:4D8A", "1771:98C4", "1771:9B85",
    # round 2: the finding-backed routines F004..F008 cite by bare offset, and every other routine
    # row added in rounds 1 and 2
    "0791:0441", "0791:0A6B", "0791:0B7C", "0791:0C65", "0791:1C78", "0791:7FCF", "0791:ED8A",
    "1771:2EE5", "0000:0000", "000E:70B9", "000E:7439", "0791:7881", "0791:9119", "0791:F098",
    "1771:027B", "1771:157D", "1771:26B9", "1771:33CD", "1771:377E", "1771:3827", "1771:4E22",
    "1771:9873",
    # T22: the routines F011 establishes (the SELECT TEAM screen and the pool path)
    "0791:E44F", "0791:E2E6", "0791:DDCB", "1771:5532", "1771:53E8", "1771:50F1", "1771:0021",
]
# The fields F007 and F008 establish, by offset: every player byte but +0x09, +0x0B and +0x13 (the
# high bytes of the words at +8, +0xA, +0x12) and +0x11 (read by no screen routine; F008).
FINDING_FIELDS = {"player": [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x0A, 0x0C, 0x0D,
                             0x0E, 0x0F, 0x10, 0x12],
                  "country": [0x00, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E]}


def check(directory: Path) -> tuple[int, str]:
    run = subprocess.run([sys.executable, str(ROOT / "tools" / "static" / "check_annotations.py"),
                          "--annotations", str(directory)], capture_output=True, text=True)
    return run.returncode, run.stdout + run.stderr


def routine_body(view: Path, address: str) -> str:
    """The text of one function in a view (decompiled/ or named/), from its index.tsv."""
    rows = [l.split("\t") for l in (view / "index.tsv").read_text(encoding="utf-8").splitlines()]
    header = rows[0]
    row = next(dict(zip(header, r)) for r in rows[1:] if r[0] == address)
    lines = (view / row["file"]).read_text(encoding="utf-8").split("\n")
    i = int(row["line"]) - 1
    out = [lines[i]]
    for line in lines[i + 1:]:
        if line.startswith("// ---- "):
            break
        out.append(line)
    return "\n".join(out)


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()) / "annotations"
        shutil.copytree(ANNOTATIONS, self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir.parent)

    def edit(self, name: str, old: str, new: str) -> None:
        p = self.dir / name
        text = p.read_text(encoding="utf-8")
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, 1), encoding="utf-8")

    def append(self, name: str, row: str) -> None:
        with (self.dir / name).open("a", encoding="utf-8") as f:
            f.write(row + "\n")

    def assertFails(self, message: str) -> None:
        code, out = check(self.dir)
        self.assertEqual(code, 1, out)
        self.assertIn(message, out)

    def test_committed_annotations_pass(self):
        code, out = check(self.dir)
        self.assertEqual(code, 0, out)
        self.assertIn("check_annotations: ok", out)

    def test_coverage_printed_per_segment(self):
        code, out = check(self.dir)
        for seg in ("0791", "1771", "214B", "23E4"):
            self.assertRegex(out, rf"(?m)^{seg}\t\d+\t\d+")

    def test_missing_basis(self):
        self.append("routines.tsv", "1771:377E\tplayer_value\ta player's value\tguess\t")
        self.assertFails("non-empty tab-separated cells")

    def test_basis_not_a_finding_or_read(self):
        self.append("routines.tsv", "1771:377E\tplayer_value\ta player's value\tguess\tsomebody said so")
        self.assertFails("neither a finding id")

    def test_basis_finding_without_file(self):
        self.append("routines.tsv", "1771:377E\tplayer_value\ta player's value\tlikely\tF999")
        self.assertFails("no file findings/F999-*.md")

    def test_basis_read_without_file(self):
        self.append("routines.tsv", "1771:377E\tplayer_value\ta player's value\tlikely\tread decompiled/nope.c")
        self.assertFails("no file static/goal-exe/decompiled/nope.c")

    def test_established_needs_a_finding(self):
        self.append("routines.tsv", "1771:377E\tplayer_value\ta value\testablished\tread decompiled/seg_1771_02.c")
        self.assertFails("established needs a finding id")

    def test_duplicate_name(self):
        self.append("routines.tsv", "1771:377E\tcountry_rating\ta value\tguess\tread decompiled/seg_1771_02.c")
        self.assertFails("name country_rating used 2 times")

    def test_global_and_routine_share_a_name(self):
        self.append("globals.tsv", "DS:9A3E\tcountry_rating\tbyte\ta flag\tguess\tF005")
        self.assertFails("name country_rating used 2 times")

    def test_duplicate_field_name(self):
        self.append("fields.tsv", "player\t0x05\tage\tbyte\tsomething\tguess\tF007")
        self.assertFails("field name player.age used 2 times")

    def test_address_not_in_routines(self):
        self.append("routines.tsv", "1771:377F\tplayer_value\ta value\tguess\tread decompiled/seg_1771_02.c")
        self.assertFails("1771:377F is not a routine of routines.tsv")

    def test_global_outside_data_segment(self):
        self.append("globals.tsv", "DS:FFF0\tfar_away\tbyte\tnothing\tguess\tF005")
        self.assertFails("outside the data segment")

    def test_invalid_identifier(self):
        self.append("routines.tsv", "1771:377E\tplayer-value\ta value\tguess\tread decompiled/seg_1771_02.c")
        self.assertFails("is not a C identifier")

    def test_generated_name_refused(self):
        self.append("routines.tsv", "1771:377E\tf_1771_377E\ta value\tguess\tread decompiled/seg_1771_02.c")
        self.assertFails("looks like a generated name")

    def test_keyword_refused(self):
        self.append("routines.tsv", "1771:377E\twhile\ta value\tguess\tread decompiled/seg_1771_02.c")
        self.assertFails("is a keyword")

    def test_confidence_outside_the_set(self):
        self.append("routines.tsv", "1771:377E\tplayer_value\ta value\tsure\tread decompiled/seg_1771_02.c")
        self.assertFails("confidence 'sure' is not one of")

    def test_field_past_record_end(self):
        self.append("fields.tsv", "player\t0x13\ttail\tword\tsomething\tguess\tF007")
        self.assertFails("runs past the record's")

    def test_fields_overlap(self):
        self.append("fields.tsv", "country\t0x26\tlast_two\tword[2]\tsomething\tguess\tF007")
        self.assertFails("overlaps squad")

    def test_unknown_type(self):
        self.append("fields.tsv", "player\t0x05\tfive\tnibble\tsomething\tguess\tF007")
        self.assertFails("type 'nibble' unknown")

    def test_duplicate_routine_address(self):
        self.append("routines.tsv", "0791:0106\tsummary_board\ta board\tguess\tread decompiled/seg_0791_01.c")
        self.assertFails("address 0791:0106 has more than one row")

    def test_duplicate_global_address(self):
        self.append("globals.tsv", "DS:A917\tcountry_array\tdword\tthe same pointer\tguess\tF007")
        self.assertFails("globals.tsv: address DS:A917 has more than one row")

    def test_wrong_header(self):
        self.edit("globals.tsv", "address\tname\ttype", "address\tname\tkind")
        self.assertFails("globals.tsv:1: header must be")

    def test_missing_file(self):
        (self.dir / "records.tsv").unlink()
        self.assertFails("records.tsv: missing")

    def test_record_size_not_hex(self):
        self.edit("records.tsv", "player\t0x14", "player\t20")
        self.assertFails("size '20' is not 0x<hex> > 0")

    def test_record_defined_twice(self):
        self.append("records.tsv", "player\t0x14\tagain\tF007")
        self.assertFails("record player defined twice")

    def test_global_address_format(self):
        self.append("globals.tsv", "DS:a9ff\tdelay_count\tword\tloops per ms\tlikely\tF004")
        self.assertFails("is not DS:XXXX")

    def test_field_of_unknown_record(self):
        self.append("fields.tsv", "team\t0x00\tfirst\tbyte\tsomething\tguess\tF007")
        self.assertFails("record team not in records.tsv")

    def test_field_offset_not_hex(self):
        self.append("fields.tsv", "player\t17\tseventeen\tbyte\tsomething\tguess\tF007")
        self.assertFails("offset '17' is not 0x<hex>")

    def test_empty_array(self):
        self.append("fields.tsv", "country\t0x30\tnothing\tbyte[0]\tsomething\tguess\tF007")
        self.assertFails("type 'byte[0]' unknown")

    def test_run_time_library_routine_without_row(self):
        text = (self.dir / "routines.tsv").read_text(encoding="utf-8")
        (self.dir / "routines.tsv").write_text(
            "\n".join(l for l in text.split("\n") if not l.startswith("235C:00A2\t")), encoding="utf-8")
        self.assertFails("run-time library segment 235C: 1 routine(s) without a row, first 235C:00A2")


class CommittedTests(unittest.TestCase):
    def test_finding_cited_routines_named(self):
        rows = check_annotations.Checker(ANNOTATIONS, ROOT / "static/goal-exe/routines.tsv",
                                         ROOT / "findings", ROOT / "static/goal-exe")
        rows.load()
        named_addresses = {r["address"] for _, r in rows.rows["routines.tsv"]}
        self.assertEqual([a for a in FINDING_CITED if a not in named_addresses], [])

    def test_finding_fields_named(self):
        c = check_annotations.Checker(ANNOTATIONS, ROOT / "static/goal-exe/routines.tsv",
                                      ROOT / "findings", ROOT / "static/goal-exe")
        c.load()
        have = {(r["record"], int(r["offset"], 16)) for _, r in c.rows["fields.tsv"]}
        missing = [(rec, hex(o)) for rec, offs in FINDING_FIELDS.items() for o in offs if (rec, o) not in have]
        self.assertEqual(missing, [])

    def test_run_time_library_fully_labelled(self):
        c = check_annotations.Checker(ANNOTATIONS, ROOT / "static/goal-exe/routines.tsv",
                                      ROOT / "findings", ROOT / "static/goal-exe")
        c.check()
        for seg, n, total in c.coverage():
            if seg in check_annotations.RTL_SEGMENTS:
                self.assertEqual(n, total, seg)


class NamedViewTests(unittest.TestCase):
    # the three rating inputs of 1771:10E7 and the R008 store of 0791:BBFF (F007, F008)
    RATING_OFFSETS = re.compile(r"\+ 0x2[abc]\b")
    TACTICS_OFFSET = re.compile(r"\+ 0x2d\b")

    def assertNamedRating(self, body: str) -> None:
        self.assertIsNone(self.RATING_OFFSETS.search(body), body)
        for field in ("continent_rank", "world_rank", "continent"):
            self.assertRegex(body, rf"(->|\.){field}\b", body)

    def assertNamedTactics(self, body: str) -> None:
        self.assertIsNone(self.TACTICS_OFFSET.search(body), body)
        self.assertRegex(body, r"(->|\.)team_tactics\b", body)

    def test_country_rating_reads_fields_by_name(self):
        self.assertNamedRating(routine_body(NAMED, "1771:10E7"))

    def test_set_team_tactics_stores_field_by_name(self):
        self.assertNamedTactics(routine_body(NAMED, "0791:BBFF"))

    def test_the_raw_view_fails_the_same_checks(self):
        with self.assertRaises(AssertionError):
            self.assertNamedRating(routine_body(RAW, "1771:10E7"))
        with self.assertRaises(AssertionError):
            self.assertNamedTactics(routine_body(RAW, "0791:BBFF"))

    def test_pool_view_reads_pool_globals_by_name(self):
        # F011: 0791:E2E6 lists A927[DS:6D18 + 2*manager + row - 1]; the named view has the two globals
        body = routine_body(NAMED, "0791:E2E6")
        self.assertIn("pool_indices", body)
        self.assertIn("pool_base_table", body)
        self.assertNotIn("DS:A927", body)
        self.assertNotIn("0x6d18", body)
        raw = routine_body(RAW, "0791:E2E6")
        self.assertIn("DS:A927", raw)
        self.assertNotIn("pool_indices", raw)

    def test_render_names_headings_and_calls(self):
        segmap = decompiled.SegMap([(0x0791, 0x2000, 0x10000), (0x1771, 0x4000, 0x10000),
                                   (0x2581, 0xB000, 0x10000)])
        functions = decompiled.parse_raw(
            "@@FUNC 4000:10e7 country_rating __stdcall16far ok\nint country_rating(void)\n{\n  return 0;\n}\n"
            "@@FUNC 2000:0010 f_0791_0010 __stdcall16near ok\nvoid f_0791_0010(void)\n"
            "{\n  func_0x000410e7();\n}\n")
        names = {"1771:10E7": {"address": "1771:10E7", "name": "country_rating", "purpose": "the rating",
                               "confidence": "established", "basis": "F007"}}
        files, rows = named.render(functions, ["0791:0010", "1771:10E7"], segmap, names)
        text = files["seg_1771_01.c"]
        self.assertIn("// ---- 1771:10E7  country_rating  (f_1771_10E7; Ghidra 4000:10E7", text)
        self.assertIn("// the rating  [established; F007]", text)
        self.assertIn("country_rating();", files["seg_0791_01.c"])
        self.assertEqual(rows[1][:3], ["1771:10E7", "country_rating", "established"])
        self.assertEqual(rows[0][1], "")


if __name__ == "__main__":
    unittest.main()
