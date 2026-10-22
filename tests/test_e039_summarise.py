"""E039 (T83): the per-date check of the trace against the DOSBox-X record passes on the committed logs and fails
when the year, the stage or a screen differs."""
import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "experiments" / "E039-start-year"
spec = importlib.util.spec_from_file_location("e039_summarise", HERE / "summarise.py")
summarise = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarise)
CASES = (("E039-r0001.json", "trace-1990.json"), ("E039-r0002.json", "trace-1992.json"))


def run(record, trace):
    tmp = Path(tempfile.mkdtemp())
    paths = []
    for name, doc in (("record.json", record), ("trace.json", trace)):
        (tmp / name).write_text(json.dumps(doc), encoding="utf-8")
        paths.append(str(tmp / name))
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = summarise.main(paths)
    return code, out.getvalue()


def load(rec, tr):
    return (json.loads((ROOT / "runs" / "E039" / rec).read_text(encoding="utf-8")),
            json.loads((HERE / "out" / tr).read_text(encoding="utf-8")))


class Summarise(unittest.TestCase):
    def test_both_dates_match(self):
        for rec, tr in CASES:
            code, out = run(*load(rec, tr))
            self.assertEqual(code, 0, out)

    def test_the_two_dates_give_two_start_years_and_stages(self):
        ends = [load(rec, tr)[1]["final"]["game_38_41"] for rec, tr in CASES]
        self.assertEqual(ends[0][4:8], "c807")   # 1992 at +0x3A
        self.assertEqual(ends[1][4:8], "ca07")   # 1994
        self.assertEqual((ends[0][8:10], ends[1][8:10]), ("02", "05"))   # stage +0x3C

    def test_a_changed_year_fails(self):
        record, trace = load(*CASES[0])
        trace = copy.deepcopy(trace)
        for e in trace["events"]:
            if e["kind"] == "read" and "A9FD" in e:
                e["A9FD"] = "07C8"
        self.assertEqual(run(record, trace)[0], 1)

    def test_a_changed_stage_fails(self):
        record, trace = load(*CASES[1])
        trace = copy.deepcopy(trace)
        ev = [e for e in trace["events"] if e["kind"] == "read" and e.get("game_38_41")][-1]
        ev["game_38_41"] = ev["game_38_41"][:8] + "02" + ev["game_38_41"][10:]
        self.assertEqual(run(record, trace)[0], 1)

    def test_a_changed_screen_fails(self):
        record, trace = load(*CASES[0])
        trace = copy.deepcopy(trace)
        ev = next(e for e in trace["events"] if e["kind"] == "read")
        ev["screen"] = ev["screen"].replace("Y/N", "Y/X", 1)
        self.assertEqual(run(record, trace)[0], 1)


if __name__ == "__main__":
    unittest.main()
