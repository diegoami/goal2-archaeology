"""F031's literal cases against the predicate (T81, Done-when 2).

Run from the repository root: python3 -m unittest discover -s experiments/E037-exchange-windows -t experiments/E037-exchange-windows
Every row of cases.tsv is visited; changing any row (its inputs, its verdict, its evidence level or its text) fails:
the verdict is recomputed from the inputs, and the file's sha256 is pinned.
"""
import csv
import hashlib
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import predicate  # noqa: E402
import tours  # noqa: E402

CASES = os.path.join(HERE, 'cases.tsv')
CASES_SHA256 = 'PIN'
CODES = {
    'allowed': predicate.ALLOWED,
    'finals': predicate.REFUSED_FINALS,
    'tour': predicate.REFUSED_TOUR,
    'in_match': predicate.REFUSED_IN_MATCH,
    'sacked': predicate.REFUSED_SACKED,
    'unknown': predicate.UNKNOWN,
}


def load():
    with open(CASES, newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


class Cases(unittest.TestCase):
    def test_every_row_matches_the_predicate(self):
        rows = load()
        visited = []
        for row in rows:
            with self.subTest(row=row['id']):
                self.assertEqual(predicate.evaluate_row(row), CODES[row['expected']], row['moment'])
                visited.append(row['id'])
        self.assertEqual(visited, ['C%02d' % k for k in range(1, len(rows) + 1)])
        self.assertEqual(len(visited), 29)

    def test_evidence_levels(self):
        for row in load():
            with self.subTest(row=row['id']):
                self.assertIn(row['evidence'], ('confirmed', 'inferred', 'unknown'))
                if row['expected'] == 'unknown':
                    self.assertNotEqual(row['evidence'], 'confirmed')

    def test_table_is_pinned(self):
        with open(CASES, 'rb') as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), CASES_SHA256)


class Flag(unittest.TestCase):
    def test_route_sets_only_for_finals_group_kinds(self):
        for kind in (1, 2, 3, 5, 6, 7, 8, 101, 102, 103, 200, 201, 202, 203):
            with self.subTest(kind=kind):
                self.assertEqual(predicate.finals_flag_after_route(0, kind), 1 if kind in (3, 7) else 0)
                self.assertEqual(predicate.finals_flag_after_route(1, kind), 1)

    def test_only_the_qualifying_builds_clear(self):
        for stage in range(2, 9):
            with self.subTest(stage=stage):
                self.assertEqual(predicate.finals_flag_after_build(1, stage), 0 if stage in (2, 5) else 1)


class Tours(unittest.TestCase):
    def test_stage7_friendlies(self):
        fx = tours.stage7_friendlies()
        self.assertEqual(len(fx), 320)
        loop1 = [f for f in fx if f[1] == 1]
        loop2 = [f for f in fx if f[1] == 2]
        self.assertTrue(all(tours.continent_of(a) != tours.continent_of(b) for _, _, _, a, b in loop1))
        self.assertTrue(all(tours.continent_of(a) == tours.continent_of(b) for _, _, _, a, b in loop2))
        per = {p: [] for p in range(1, 129)}
        for _, _, _, a, b in fx:
            per[a].append('A')
            per[b].append('B')
        for p, sides in per.items():
            with self.subTest(position=p):
                self.assertEqual(sides, ['A'] * 4 + ['B'] if p % 2 else ['B'] * 4 + ['A'])


if __name__ == '__main__':
    unittest.main()
