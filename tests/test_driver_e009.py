"""E009 (T22, Q007): the pool screen's data checks in experiments/E009-q007-squad-pool/summarise.py.

The check predicates (pool_ok, base_ok, pool_records_ok, positions_sorted_ok) and the parsing helpers
(words_obs, base_obs, records_obs, names_obs) are tested on synthetic data with the sizes and offsets
from the listing (2139:0000: [A927] 0x3C2 bytes; 1771:98C4: the base DS:6D18 + 2*manager, the record
number 0xA00 + counter), not from the module. The committed record (runs/E009, never rewritten) is
checked with each predicate on its own observations.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))

import players  # noqa: E402


def load_by_path(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


summarise = load_by_path("e009_summarise", "experiments/E009-q007-squad-pool/summarise.py")

N_POOL = 80
POOL_FIRST = 0xA00


def good_words():
    """A pool index array that satisfies pool_ok: word 0 = 0, words 1..80 = 2561..2640, rest 0."""
    words = [0] * 481
    words[1:N_POOL + 1] = list(range(POOL_FIRST + 1, POOL_FIRST + N_POOL + 1))
    return words


def record(country, position):
    return bytes([country]) + b"\x00" * 5 + bytes([position]) + b"\x00" * 13


def good_recs():
    """The 80 pool records (country 7) and the two past records (zero)."""
    recs = {n: record(7, 0) for n in range(POOL_FIRST + 1, POOL_FIRST + N_POOL + 1)}
    recs[POOL_FIRST + N_POOL + 1] = b"\x00" * 20
    recs[POOL_FIRST + N_POOL + 2] = b"\x00" * 20
    return recs


class Predicates(unittest.TestCase):
    def test_pool_ok(self):
        self.assertTrue(summarise.pool_ok(good_words()))
        w = good_words()
        w[1] = 2560                       # a record number below 2561
        self.assertFalse(summarise.pool_ok(w))
        w = good_words()
        del w[80]                          # one of the 80 missing
        self.assertFalse(summarise.pool_ok(w))
        w = good_words()
        w[0] = 1                           # word 0 must be 0
        self.assertFalse(summarise.pool_ok(w))
        w = good_words()
        w[81] = 3000                       # a word past the pool is not 0
        self.assertFalse(summarise.pool_ok(w))

    def test_base_ok(self):
        base = [0, 1, 81, 161, 241, 321, 401, 0]
        self.assertTrue(summarise.base_ok(base))
        base[1] = 2                        # manager 1's base is 1, not 2
        self.assertFalse(summarise.base_ok(base))
        base = [0, 1, 81, 161, 241, 321, 402, 0]
        self.assertFalse(summarise.base_ok(base))   # manager 6's base is 401

    def test_pool_records_ok(self):
        self.assertEqual(summarise.pool_records_ok(good_recs()), (True, True))
        recs = good_recs()
        recs[2561] = record(8, 0)          # a pool record of another country
        self.assertEqual(summarise.pool_records_ok(recs), (False, True))
        recs = good_recs()
        recs[2641] = record(7, 0)          # the record just past the pool is not zero
        self.assertEqual(summarise.pool_records_ok(recs), (True, False))

    def test_positions_sorted_ok(self):
        words = good_words()
        recs = {n: record(7, 0) for n in words[1:N_POOL + 1]}
        self.assertTrue(summarise.positions_sorted_ok(recs, words))
        recs[words[5]] = record(7, 9)      # a later position before an earlier one
        self.assertFalse(summarise.positions_sorted_ok(recs, words))

    def test_screen_has(self):
        self.assertTrue(summarise.screen_has("a b c", ["a", "c"]))
        self.assertFalse(summarise.screen_has("a b c", ["a", "d"]))


class Parsing(unittest.TestCase):
    def make_record(self, words, base_bytes, recs):
        obs = []
        obs.append({"field": "x: DS:A927 (the pool index array, word[481]) as decimal words 0..480",
                    "value": json.dumps(words)})
        obs.append({"field": "x: DS:6D18..6D27 (the per-manager pool base table, 8 words) hex",
                    "value": base_bytes.hex()})
        for n, r in recs.items():
            obs.append({"field": f"x: the 20 bytes of player record {n} at [DS:A91B] + 0x14 n, hex",
                        "value": r.hex()})
        return {"observations": obs}

    def test_observations_round_trip(self):
        words = good_words()
        base = [0, 1, 81, 161, 241, 321, 401, 0]
        recs = good_recs()
        rec = self.make_record(words, b"".join(w.to_bytes(2, "little") for w in base), recs)
        self.assertEqual(summarise.words_obs(rec), words)
        self.assertEqual(summarise.base_obs(rec), base)
        got = summarise.records_obs(rec)
        self.assertEqual(got[2561][0], 7)
        self.assertEqual(got[2641], b"\x00" * 20)
        self.assertEqual(len(got), 82)     # 80 pool + the two past


class CommittedRecord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        recs = sorted((ROOT / "runs" / "E009").glob("E009-r*.json"))
        cls.recs = [json.loads(p.read_text()) for p in recs]

    def test_there_is_one_completed_record(self):
        self.assertEqual(len(self.recs), 1)
        self.assertEqual(self.recs[0]["status"], "completed")

    def test_every_check_holds_on_the_record(self):
        for rec in self.recs:
            words = summarise.words_obs(rec)
            base = summarise.base_obs(rec)
            recs20 = summarise.records_obs(rec)
            self.assertTrue(summarise.pool_ok(words))
            self.assertTrue(summarise.base_ok(base))
            self.assertEqual(summarise.pool_records_ok(recs20), (True, True))
            self.assertTrue(summarise.positions_sorted_ok(recs20, words))
            surnames, initials = summarise.names_obs(rec)
            pool_screen = summarise.screen_text(rec, "SELECT TEAM, pool view")
            squad_screen = summarise.screen_text(rec, "SELECT TEAM, squad view")
            self.assertTrue(summarise.screen_has(pool_screen,
                                                 [players.full_name(surnames, initials, n) for n in words[1:21]]))
            self.assertTrue(summarise.screen_has(
                squad_screen,
                [players.full_name(surnames, initials, n) for n in range((7 - 1) * 20 + 1, 7 * 20 + 1)]))

    def test_the_pool_is_the_80_records_past_2560(self):
        # the pool records are 2561..2640, distinct from Denmark's 20 squad records 121..140
        for rec in self.recs:
            words = summarise.words_obs(rec)
            pool = words[1:N_POOL + 1]
            self.assertEqual(sorted(pool), list(range(2561, 2641)))
            self.assertTrue(all(n > 2560 for n in pool))
            self.assertFalse(set(pool) & set(range(121, 141)))   # no squad record in the pool


if __name__ == "__main__":
    unittest.main()
