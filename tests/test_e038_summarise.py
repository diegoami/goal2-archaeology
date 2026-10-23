"""E038 (T82): the summariser's screen-by-screen check of the trace against the DOSBox-X record fails on a difference."""
import contextlib
import copy
import importlib.util
import io
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "experiments" / "E038-new-game-keywait"
spec = importlib.util.spec_from_file_location("e038_summarise", HERE / "summarise.py")
summarise = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summarise)
RECORD = ROOT / "runs" / "E038" / "E038-r0001.json"
TRACE = HERE / "out" / "trace-r0001.json"


def run(record, trace, tmp):
    paths = []
    for name, doc in (("record.json", record), ("trace.json", trace)):
        p = tmp / name
        p.write_text(json.dumps(doc), encoding="utf-8")
        paths.append(str(p))
    with contextlib.redirect_stdout(io.StringIO()) as out:
        code = summarise.main(paths)
    return code, out.getvalue()


class Summarise(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = Path(tempfile.mkdtemp())
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))
        self.trace = json.loads(TRACE.read_text(encoding="utf-8"))

    def test_the_committed_trace_matches_the_record(self):
        code, out = run(self.record, self.trace, self.tmp)
        self.assertEqual(code, 0, out)
        self.assertEqual(out.count("| yes | yes |"), len(summarise.ORDER))

    def test_a_changed_screen_fails(self):
        trace = copy.deepcopy(self.trace)
        read = next(e for e in trace["events"] if e["kind"] == "read" and e["site"] == "1771:28F5")
        read["screen"] = read["screen"].replace("Denmark", "Denmarx", 1)
        code, out = run(self.record, trace, self.tmp)
        self.assertEqual(code, 1)
        self.assertIn("| country-select | 1771:28F5 | 1771:28F5 | yes | NO |", out)

    def test_a_changed_caller_fails(self):
        trace = copy.deepcopy(self.trace)
        read = next(e for e in trace["events"] if e["kind"] == "read" and e["site"] == "000E:75D1")
        read["callers"][0] = "0000:00CC"
        code, _ = run(self.record, trace, self.tmp)
        self.assertEqual(code, 1)

    def reads_cut(self, how):
        """The committed trace with its reads outside the name entry cut (#378): none, the last one, or one more."""
        trace = copy.deepcopy(self.trace)
        idx = [i for i, e in enumerate(trace["events"]) if e["kind"] == "read" and e["site"] != "214B:112B"]
        if how == "none":
            trace["events"] = [e for i, e in enumerate(trace["events"]) if i not in idx]
        elif how == "last":
            del trace["events"][idx[-1]]
        else:
            trace["events"].append(copy.deepcopy(trace["events"][idx[-1]]))
        return trace

    def test_a_trace_with_no_reads_fails(self):
        code, out = run(self.record, self.reads_cut("none"), self.tmp)
        self.assertEqual(code, 1, out)

    def test_a_trace_missing_the_manager_menu_read_fails(self):
        code, out = run(self.record, self.reads_cut("last"), self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn("holds 5 reads", out)

    def test_a_trace_with_one_read_more_fails(self):
        code, out = run(self.record, self.reads_cut("more"), self.tmp)
        self.assertEqual(code, 1, out)
        self.assertIn("holds 7 reads", out)

    def test_each_seed_word_that_differs_fails(self):
        # #379: all six reads present, screens and callers equal, one seed word changed in one read
        for key in ("seed", "seed2"):
            with self.subTest(key):
                trace = copy.deepcopy(self.trace)
                read = next(e for e in trace["events"] if e["kind"] == "read" and e["site"] == "1771:28F5")
                read[key] = "FFFF" if read[key] != "FFFF" else "0000"
                code, out = run(self.record, trace, self.tmp)
                self.assertEqual(code, 1, out)


if __name__ == "__main__":
    unittest.main()
