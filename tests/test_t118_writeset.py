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


def sack():
    return json.loads((HERE / "sack.json").read_text())


class SackWriteSet(unittest.TestCase):
    """T118b1 (#427): post_match_news_and_sack's own routines, the sack score and unmanage_country."""

    def test_the_table_is_complete_and_its_rules_cite_the_listing(self):
        self.assertEqual(check.check(sack()), [])
        self.assertEqual(sack()["scope"], ["000E:4E0E", "000E:4DB7", "000E:319B", "000E:0B77", "000E:01FA"])

    def test_deleting_any_row_fails(self):
        base = sack()
        for i, row in enumerate(base["rows"]):
            t = copy.deepcopy(base)
            del t["rows"][i]
            with self.subTest(site=row["site"]):
                self.assertTrue(any(row["site"] in p for p in check.check(t)))

    def test_a_rule_without_a_listing_line_fails(self):
        for evidence in ("F025", "seg_000E_04.asm:999999"):
            t = sack()
            t["rules"][0]["evidence"] = evidence
            with self.subTest(evidence=evidence):
                self.assertNotEqual(check.check(t), [])

    def test_the_sack_flag_is_a_store_into_4e0e_s_frame(self):
        row = next(r for r in sack()["rows"] if r["site"] == "000E:37AC")
        self.assertEqual((row["op"], row["class"]), ("store", "frame"))
        self.assertIn("bp-2 := 1", row["target"])
        self.assertIn("-128..-11", row["condition"])

    def test_the_game_state_the_sack_changes(self):
        """[confirmed: seg_000E_01.asm:226-356] unmanage_country is 4E0E's only game-state writer in this scope."""
        state = {r["site"]: r["class"] for r in sack()["rows"]
                 if r["class"] in ("game", "managers", "countries", "players", "fixtures", "ds-global")}
        self.assertEqual(state, {"000E:0229": "game", "000E:0231": "managers", "000E:0290": "players",
                                 "000E:02D8": "players", "000E:02FD": "countries", "000E:037E": "fixtures"})

    def test_319b_draws_nine_times_on_its_paths(self):
        rng = [(r["site"], r["callee"]) for r in sack()["rows"] if r["class"] == "rng"]
        self.assertEqual(len(rng), 9)
        self.assertTrue(all(c == "214B:06B1" for _, c in rng))


def news():
    return json.loads((HERE / "news.json").read_text())


RNG_CALLEES = {"214B:06B1", "214B:06FA", "214B:06D0", "214B:0688"}


class NewsWriteSet(unittest.TestCase):
    """T118b2 (#427): the post-match news's text routines draw on 7B62 and write no game state."""

    def test_the_table_is_complete(self):
        self.assertEqual(check.check(news()), [])
        self.assertEqual(len(news()["scope"]), 31)

    def test_deleting_any_row_fails(self):
        base = news()
        for i, row in enumerate(base["rows"]):
            t = copy.deepcopy(base)
            del t["rows"][i]
            with self.subTest(site=row["site"]):
                self.assertTrue(any(row["site"] in p for p in check.check(t)))

    def test_every_call_of_a_random_routine_is_an_rng_row_and_only_those(self):
        rows = news()["rows"]
        self.assertEqual({r["site"] for r in rows if r.get("callee") in RNG_CALLEES},
                         {r["site"] for r in rows if r["class"] == "rng"})
        self.assertEqual(sum(r["class"] == "rng" for r in rows), 49)

    def test_no_row_writes_game_state(self):
        """[derived: the seven non-frame stores read one by one, seg_000E_01.asm:516, 538, 609, 1052;
        seg_000E_03.asm:130; 3AE6; 485A] screen, sound, a display byte or a caller's frame."""
        state = [r["site"] for r in news()["rows"] if r["class"] in ("game", "managers", "countries", "players", "fixtures")]
        self.assertEqual(state, [])

    def test_only_the_crowd_animation_draws_in_a_loop(self):
        looped = {r["site"] for r in news()["rows"] if r["class"] == "rng" and "inside the loop" in r["condition"]}
        self.assertEqual(looped, {"000E:047B", "000E:0487", "000E:04B2"})
