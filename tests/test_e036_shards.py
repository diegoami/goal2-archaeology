"""experiments/E036-match-port/shards.py (#361): the shards of a family run on Actions, and their join."""
import json
import tempfile
import unittest
from pathlib import Path

from tests.test_e036_compare import E036, FAMILIES, record  # noqa: E402  (sets up the import paths)

import importlib.util
_spec = importlib.util.spec_from_file_location("e036_shards", E036 / "shards.py")
shards = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shards)

IDS = [m.id for name in sorted(FAMILIES) for m in FAMILIES[name].matches]


class Plan(unittest.TestCase):
    def test_the_selection_is_the_family_runs_in_its_order(self):
        self.assertEqual(shards.selected_ids("ALL"), IDS)
        self.assertEqual(shards.selected_ids("ALL", f"{IDS[5]},{IDS[1]}"), [IDS[1], IDS[5]])
        for bad in (f"{IDS[0]},{IDS[0]}", "F40/nosuch"):
            with self.subTest(bad), self.assertRaises(shards.Refused):
                shards.selected_ids("ALL", bad)

    def test_shards_are_consecutive_cover_every_match_once_and_differ_by_at_most_one(self):
        for n in (1, 2, 7, 31, len(IDS), len(IDS) + 5):
            with self.subTest(n):
                plan = shards.plan(IDS, n)
                self.assertEqual([p["shard"] for p in plan], list(range(min(n, len(IDS)))))
                parts = [p["only"].split(",") for p in plan]
                self.assertEqual([i for part in parts for i in part], IDS)
                self.assertLessEqual(max(map(len, parts)) - min(map(len, parts)), 1)
        with self.assertRaises(shards.Refused):
            shards.plan(IDS, 0)

    def test_the_command_prints_a_matrix(self):
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            self.assertEqual(shards.main(["plan", "--family", "O8", "--shards", "3"]), 0)
        matrix = json.loads(buf.getvalue())
        self.assertEqual(len(matrix["include"]), 3)
        self.assertEqual(",".join(m["only"] for m in matrix["include"]), ",".join(m.id for m in FAMILIES["O8"].matches))


class Collect(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.ids = [m.id for m in FAMILIES["O8"].matches]

    def tearDown(self):
        self.tmp.cleanup()

    def shard(self, name, ids):
        p = self.d / name
        p.write_text("".join(json.dumps(record(i)) + "\n" for i in ids))
        return str(p)

    def test_the_join_is_in_the_family_order_with_each_line_as_written(self):
        a = self.shard("a.jsonl", reversed(self.ids[4:]))           # a shard's own order does not matter
        b = self.shard("b.jsonl", self.ids[:4])
        out = self.d / "all.jsonl"
        self.assertEqual(shards.collect(self.ids, [a, b], out), 8)
        lines = out.read_text().splitlines()
        self.assertEqual([json.loads(l)["id"] for l in lines], self.ids)
        self.assertEqual(set(lines), set(Path(a).read_text().splitlines()) | set(Path(b).read_text().splitlines()))

    def test_a_missing_twice_or_unselected_match_is_refused_and_nothing_is_written(self):
        out = self.d / "all.jsonl"
        cases = {"missing": [self.shard("m.jsonl", self.ids[1:])],
                 "twice": [self.shard("t1.jsonl", self.ids), self.shard("t2.jsonl", self.ids[:1])],
                 "unselected": [self.shard("u.jsonl", self.ids + ["F40/e032-0101"])]}
        for name, paths in cases.items():
            with self.subTest(name), self.assertRaises(shards.Refused):
                shards.collect(self.ids, paths, out)
            self.assertFalse(out.exists())

    def test_an_existing_output_is_never_overwritten(self):
        out = self.d / "all.jsonl"
        out.write_text("x\n")
        with self.assertRaises(shards.Refused):
            shards.collect(self.ids, [self.shard("a.jsonl", self.ids)], out)
        self.assertEqual(out.read_text(), "x\n")


if __name__ == "__main__":
    unittest.main()
