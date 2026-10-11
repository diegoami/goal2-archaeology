"""T39a: screen kinds (identify.py) and the catalogue (build.py), over the committed E015 records."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "screens"))

import build  # noqa: E402
import common  # noqa: E402
import identify  # noqa: E402

KINDS = common.load_kinds()
R3 = common.read_record("E015-r0003")
R7 = common.read_record("E015-r0007")
K3 = identify.identify_record(R3, KINDS)
K7 = identify.identify_record(R7, KINDS)


def rows():
    lines = common.CATALOGUE.read_text(encoding="utf-8").splitlines()
    cols = lines[0].split("\t")
    return [dict(zip(cols, line.split("\t"))) for line in lines[1:]]


_KINDS = {"E015-r0003": K3, "E015-r0007": K7}
_RECORDS = {"E015-r0003": R3, "E015-r0007": R7}


def state_of(ref):
    run_id, n = ref.split(" state ")
    if run_id not in _RECORDS:
        _RECORDS[run_id] = common.read_record(run_id)
    return _RECORDS[run_id], int(n)


class Identify(unittest.TestCase):
    def test_every_state_of_r0003_and_r0007_is_named_or_unknown(self):
        self.assertEqual((len(K3), len(K7)), (4, 224))
        unknown = (list(K3.values()).count("unknown"), list(K7.values()).count("unknown"))
        self.assertEqual(unknown, (0, 0))                     # the PR quotes these counts per record
        self.assertTrue(all(isinstance(k, str) and k for k in list(K3.values()) + list(K7.values())))

    def test_three_pairs_of_different_screens_get_different_kinds_and_one_rule_each(self):
        pairs = [(16, 76), (3, 28), (31, 119)]                # manager menu / substitutions; country / watch prompt; live match / team tactics
        for a, b in pairs:
            ma = common.kinds_matching(R7["states"][a]["text"], KINDS)
            mb = common.kinds_matching(R7["states"][b]["text"], KINDS)
            self.assertEqual(len(ma), 1, f"state {a}: {ma}")
            self.assertEqual(len(mb), 1, f"state {b}: {mb}")
            self.assertNotEqual(ma, mb, f"states {a} and {b}")
        self.assertEqual([K7[x] for x in (16, 76, 3, 28, 31, 119)],
                         ["manager-menu", "squad-substitution-take-off", "country-select",
                          "match-watch-prompt", "match-live", "team-tactics"])

    def test_no_screen_of_any_record_satisfies_two_rules(self):
        for path in common.record_paths():
            rec = common.read_record(path)
            for n, s in rec["states"].items():
                if s["text"] is not None:
                    self.assertLessEqual(len(common.kinds_matching(s["text"], KINDS)), 1, f"{path.stem} state {n}")

    def test_a_kind_does_not_follow_the_digest_or_the_names(self):
        # the same fixed text with other names and numbers is still the same kind
        text = R7["states"][16]["text"].replace("Italy", "Spain-").replace("Turkey", "Brazil").replace("2028", "1994")
        self.assertEqual(common.identify_text(text, KINDS), "manager-menu")
        # a common word alone merges nothing: the fixture list and the manager menu both say "Hit"
        self.assertEqual(common.identify_text("Hit", KINDS), "unknown")

    def test_two_rules_on_one_screen_raise(self):
        both = common.parse_rule("+Do you want")
        extra = [("a", "+Do you want", both, ""), ("b", "+watch", common.parse_rule("+watch"), "")]
        with self.assertRaises(ValueError):
            common.identify_text("Do you want to watch", extra)

    def test_rule_syntax_is_checked(self):
        with self.assertRaises(ValueError):
            common.parse_rule("phrase without a sign")


class Catalogue(unittest.TestCase):
    def test_rebuild_is_byte_identical_to_the_committed_file(self):
        self.assertEqual(build.build(), common.CATALOGUE.read_text(encoding="utf-8"))

    def test_every_row_has_a_source_and_its_kinds_rule(self):
        rule_of = {k[0]: k[1] for k in KINDS}
        rs = rows()
        self.assertGreater(len(rs), 100)
        for r in rs:
            self.assertTrue(r["source"], r)
            self.assertTrue(r["source"] in ("screen", "owner") or r["source"].startswith(("run:", "static:")), r)
            self.assertEqual(r["rule"], rule_of[r["kind"]], r)

    def test_screen_rows_quote_text_that_occurs_in_their_state(self):
        n = 0
        for r in rows():
            if r["source"] != "screen":
                continue
            rec, state = state_of(r["state"])
            self.assertEqual(rec["states"][state]["text"] is not None, True)
            self.assertIn(common.normalize(r["quote"]), common.normalize(rec["states"][state]["text"]), r)
            kinds = _KINDS.setdefault(rec["run_id"], identify.identify_record(rec, KINDS))
            self.assertEqual(kinds[state], r["kind"], r)
            n += 1
        self.assertGreater(n, 60)

    def test_run_rows_before_and_after_kinds_are_what_identify_gives(self):
        n = 0
        for r in rows():
            if not r["source"].startswith("run:"):
                continue
            ref = r["source"][len("run:"):]
            rec, before = state_of(ref)
            rec2, after = state_of(r["to_state"])
            self.assertEqual(rec["run_id"], rec2["run_id"])
            kinds = _KINDS.setdefault(rec["run_id"], identify.identify_record(rec, KINDS))
            self.assertEqual(kinds[before], r["kind"], r)
            self.assertEqual(kinds[after], r["to_kind"], r)
            self.assertIn(rec["run_id"], build.REAL_SITTINGS)
            n += 1
        self.assertGreater(n, 40)

    def test_a_run_row_is_a_burst_not_a_per_key_cause(self):
        # a burst of several presses is one row with the presses in order, never split per key
        multi = [r for r in rows() if r["source"].startswith("run:") and " " in r["key"]]
        self.assertTrue(multi)
        for r in multi:
            self.assertTrue(r["effect"].startswith("burst: "), r)

    def test_scripted_acceptance_sittings_are_not_counted(self):
        for r in rows():
            for run in ("E015-r0004", "E015-r0005", "E015-r0006"):
                self.assertNotIn(run, r["source"])

    def test_every_kind_has_at_least_one_row(self):
        have = {r["kind"] for r in rows()}
        self.assertEqual(have, {k[0] for k in KINDS})

    def test_hint_rows_are_confirmed_on_a_screen_not_invented(self):
        # a HINTS entry whose text is on no recorded screen produces no row
        saved = build.HINTS
        build.HINTS = [("this text is on no GOAL2 screen", "Q", "quit", "")]
        try:
            text = build.build()
        finally:
            build.HINTS = saved
        screen_rows = [l.split("\t") for l in text.splitlines()[1:] if l.split("\t")[4] == "screen"]
        self.assertTrue(screen_rows)
        self.assertEqual({r[1] for r in screen_rows}, {""})          # only the "no key known" rows remain
        self.assertEqual({r[3] for r in screen_rows}, {"no key known"})


if __name__ == "__main__":
    unittest.main()
