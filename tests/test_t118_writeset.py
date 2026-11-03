"""T118a (#427): route_fixture's write-set table is complete against the raw listings, and the check is not vacuous."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "notes" / "427" / "writeset"
_spec = importlib.util.spec_from_file_location("t118_check", HERE / "check.py")
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


def table():
    return json.loads((HERE / "writeset.json").read_text())


class WriteSet(unittest.TestCase):
    def test_the_table_is_complete_and_consistent(self):
        self.assertEqual(check.check(table()), [])

    def test_the_scope_is_route_fixture_its_gate_the_silent_path_and_6685(self):
        self.assertEqual(table()["scope"], ["000E:6CA7", "000E:6C21", "000E:6970", "000E:6685"])

    def test_deleting_any_row_fails(self):
        base = table()
        for i, row in enumerate(base["rows"]):
            t = copy.deepcopy(base)
            del t["rows"][i]
            with self.subTest(site=row["site"]):
                self.assertTrue(any(row["site"] in p for p in check.check(t)))

    def test_a_wrong_line_op_callee_class_or_phase_fails(self):
        base = table()
        call = next(i for i, r in enumerate(base["rows"]) if r["op"] == "call" and r["class"] != "port-owned")
        store = next(i for i, r in enumerate(base["rows"]) if r["op"] == "store")
        for i, key, value in ((store, "line", base["rows"][store]["line"] + 1), (store, "op", "call"),
                              (call, "callee", "0791:0000"), (store, "class", "guess"), (store, "phase", "later"),
                              (store, "condition", "")):
            t = copy.deepcopy(base)
            t["rows"][i][key] = value
            with self.subTest(key=key):
                self.assertNotEqual(check.check(t), [])

    def test_a_duplicate_or_unknown_site_fails(self):
        t = table()
        t["rows"].append(dict(t["rows"][0]))
        self.assertTrue(any("2 rows" in p for p in check.check(t)))
        t = table()
        t["rows"].append(dict(t["rows"][0], site="000E:0001"))
        self.assertTrue(any("not a write or call" in p for p in check.check(t)))

    def test_an_unported_callee_cannot_be_port_owned(self):
        t = table()
        row = next(r for r in t["rows"] if r.get("callee") == "0791:BB2F")
        row["class"] = "port-owned"
        self.assertTrue(any("not a registered port" in p for p in check.check(t)))

    def test_the_tail_runs_confidence_then_news_then_b7fa_then_the_cursor(self):
        """[confirmed: seg_000E_09.asm:298-403] After run_match the order is B71C/B6CC, 4E0E, B7FA, the cursor and
        1771:8757; Match runs B7FA straight after F1F6 (#427's audit note), which this order rules out as equal."""
        order = [r.get("callee") or r["site"] for r in table()["rows"]
                 if r["site"] in ("000E:6F18", "000E:6F80", "000E:6F86", "000E:6FD8", "000E:6FF8", "000E:7000",
                                  "000E:7004")]
        self.assertEqual(order, ["0791:F1F6", "0791:B71C", "0791:B6CC", "000E:4E0E", "0791:B7FA", "000E:7000",
                                 "1771:8757"])

    def test_6685_always_draws_twice_from_7b62(self):
        rng = [r for r in table()["rows"] if r["class"] == "rng"]
        self.assertEqual([(r["site"], r["callee"], r["condition"]) for r in rng],
                         [("000E:67E7", "214B:06B1", "always"), ("000E:6809", "214B:06B1", "always")])


if __name__ == "__main__":
    unittest.main()
