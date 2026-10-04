import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "static"))

import goaldat  # noqa: E402


def synthetic():
    """A file with the block layout and the properties R002..R011 state, written by the test."""
    d = bytearray(44040)
    offs = {n: (o, s, rec, cnt) for n, o, s, rec, cnt in goaldat.block_offsets()}

    def put_str(base, i, rec, text):
        d[base + rec * i] = len(text)
        d[base + rec * i + 1:base + rec * i + 1 + len(text)] = text.encode()

    o, s, rec, n = offs["country_names"]
    for i in range(1, 129):
        put_str(o, i, rec, "Land%d" % i)
    o, s, rec, n = offs["player_names"]
    for i in range(1, 3061):
        put_str(o, i, rec, "Name%d" % (i % 1000))
    o, s, rec, n = offs["player_initials"]
    for i in range(1, 3061):
        d[o + i] = 65 + i % 26
    o, s, rec, n = offs["manager_names"]
    for i in range(1, 129):
        put_str(o, i, rec, "Boss%d" % i)
    o, s, rec, n = offs["manager_initials"]
    for i in range(1, 129):
        d[o + i] = 66
    o, s, rec, n = offs["per_country_3"]
    for i in range(3, 387):
        d[o + i] = 9 + i % 7
    o, s, rec, n = offs["per_country_a"]
    for i in range(1, 129):
        d[o + i] = 50 + i
    for name in ("per_country_b", "per_country_c"):
        o, s, rec, n = offs[name]
        for i in range(129):
            d[o + i] = (i * 5) % 129  # 5 and 129 are coprime: a permutation
    o, s, rec, n = offs["squad_20"]
    first = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 13]
    second = [0, 2, 4, 6, 8, 10, 11, 12, 13]
    for i in range(1, 129):
        d[o + 20 * i:o + 20 * i + 20] = bytes(first + second)
    return d


def status(data):
    return {cid: ok for cid, ok, _ in goaldat.run_checks(bytes(data)).rows}


class GoalDatTests(unittest.TestCase):
    def test_block_sizes_cover_the_file(self):
        self.assertEqual(sum(b[2] for b in goaldat.block_offsets()), 44040)
        self.assertEqual(goaldat.block_offsets()[-1][1] + goaldat.block_offsets()[-1][2], 44040)

    def test_synthetic_file_passes_every_structural_claim(self):
        st = status(synthetic())
        # R001 also needs the real file's hash
        self.assertFalse(st["R001"])
        for cid in ("R002", "R003", "R004", "R005", "R006", "R007", "R008", "R009", "R010", "R011"):
            self.assertTrue(st[cid], cid)

    def test_each_claim_fails_when_its_property_is_broken(self):
        offs = {n: o for n, o, _, _, _ in goaldat.block_offsets()}
        cases = {
            "R002": lambda d: d.__setitem__(offs["country_names"] + 16, 16),            # length > 15
            "R003": lambda d: d.__setitem__(offs["player_names"] + 11 * 5 + 1, 7),      # control byte in a name
            "R004": lambda d: d.__setitem__(offs["player_initials"] + 10, ord("a")),     # lower case
            "R005": lambda d: d.__setitem__(offs["manager_names"] + 13 * 130, 1),        # spare record not zero
            "R006": lambda d: d.__setitem__(offs["manager_initials"] + 131, 66),         # spare byte not zero
            "R007": lambda d: d.__setitem__(offs["per_country_3"] + 30, 8),              # outside 9..15
            "R008": lambda d: d.__setitem__(offs["per_country_a"], 1),                   # record 0 not zero
            "R009": lambda d: d.__setitem__(offs["per_country_b"] + 7, d[offs["per_country_b"] + 8]),   # duplicate
            "R010": lambda d: d.__setitem__(offs["per_country_c"] + 7, d[offs["per_country_c"] + 8]),   # duplicate
            "R011": lambda d: d.__setitem__(offs["squad_20"] + 20 * 3 + 5, 14),          # value above 13
        }
        for cid, mutate in cases.items():
            d = synthetic()
            mutate(d)
            self.assertFalse(status(d)[cid], cid)

    def test_squad_run_split_is_reported_not_required(self):
        d = synthetic()
        o = {n: o for n, o, _, _, _ in goaldat.block_offsets()}["squad_20"]
        d[o + 20 * 7 + 3], d[o + 20 * 7 + 4] = 9, 3  # descending inside the first run
        rows = {cid: (ok, text) for cid, ok, text in goaldat.run_checks(bytes(d)).rows}
        self.assertTrue(rows["R011"][0])
        self.assertIn("in 127 of 128 records", rows["R011"][1])
        self.assertIn("records [7]", rows["R011"][1])


if __name__ == "__main__":
    unittest.main()
