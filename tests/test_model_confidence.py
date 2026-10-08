"""Literal inputs/outputs for the listing's confidence arithmetic."""
import unittest
import importlib.util
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('confidence_checker', ROOT / 'experiments/E018-q016-confidence/check_confidence.py')
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class CheckerTests(unittest.TestCase):
    def run_checker(self, records, supersessions):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            for name, record in records.items():
                (Path(directory) / name).write_text(json.dumps(record))
            (Path(directory) / 'supersessions.json').write_text(json.dumps(supersessions))
            with patch('sys.argv', ['checker', '--directory', directory]):
                return CHECKER.main()

    def record(self):
        return json.loads((ROOT / 'experiments/E018-q016-confidence/fixture-probe-003.json').read_text())

    def test_consistent_record_cannot_be_declared_defective(self):
        record = self.record()
        with self.assertRaisesRegex(ValueError, 'passes its consistency check'):
            self.run_checker({'fixture-probe-old.json': record, 'fixture-probe-new.json': record},
                             {'fixture-probe-old.json': {'replacement': 'fixture-probe-new.json', 'reason': 'defective'}})

    def test_empty_comparisons_fail(self):
        with self.assertRaisesRegex(ValueError, 'empty comparison set'):
            self.run_checker({}, {})

    def test_kept_mismatch_fails(self):
        record = self.record()
        record['cases'][0]['after'][0]['confidence'] = 0
        self.assertEqual(self.run_checker({'fixture-probe-new.json': record}, {}), 1)

from runtime.model.confidence import change, result_delta, participant_values, country_rating, match_form


class ConfidenceTests(unittest.TestCase):
    def test_persisting_and_temporary_match_form(self):
        for inputs, expected in [((16, 16, 1, False), (17, 16)),
                                 ((17, 16, 1, True), (18, 18)),
                                 ((32, 32, 1, True), (33, 32)),
                                 ((127, 16, 1, True), (128, 128)),
                                 ((127, 16, 200, False), (255, 16)),
                                 ((1, 16, -2, True), (1, 1))]:
            self.assertEqual(match_form(*inputs), expected)

    def test_ranks_not_line_sums(self):
        for inputs, expected in [((1, 1, 1), 128), ((4, 32, 128), 1),
                                 ((2, 5, 20), 96), ((5, 1, 132), -1)]:
            self.assertEqual(country_rating(*inputs), expected)

    def test_clipping_and_signed_byte(self):
        for before, delta, after in [(1, -1, 1), (32, 1, 32), (16, 3, 19),
                                     (255, 3, 2), (128, 127, 1), (32, -31, 1),
                                     (16, 65535, 15), (32, 32767, 1)]:
            with self.subTest(before=before, delta=delta):
                self.assertEqual(change(before, delta), after)

    def test_result_term(self):
        # own rating, opponent rating, scores, result byte, side, special-kind flag
        cases = [((100, 100, (3, 1), 0, 0, False), 4),
                 ((100, 100, (3, 1), 0, 1, False), -4),
                 ((100, 100, (1, 3), 1, 0, False), -2),
                 ((100, 100, (1, 3), 1, 1, False), 2),
                 ((100, 100, (1, 3), 1, 1, True), 4),
                 ((100, 131, (0, 0), 2, 0, False), 0),
                 ((100, 132, (0, 0), 2, 0, False), 1),
                 ((132, 100, (0, 0), 2, 1, True), -1),
                 ((131, 100, (0, 0), 2, 0, False), 0),
                 ((100, 164, (1, 2), 1, 0, False), 1),
                 ((100, 164, (255, 1), 0, 0, False), 8)]
        for inputs, expected in cases:
            with self.subTest(inputs=inputs):
                self.assertEqual(result_delta(*inputs), expected)

    def test_bench_draws_and_sequential_clipping(self):
        self.assertEqual(participant_values(16, 4, 'starter'), (20,))
        self.assertEqual(participant_values(32, 4, 'substitute'), (31, 32))
        self.assertEqual(participant_values(1, -4, 'substitute'), (1, 2))
        self.assertEqual(participant_values(16, 99, 'unused'), (13, 14, 15, 16, 17))
        self.assertEqual(participant_values(1, 99, 'unused'), (1, 2))
        self.assertEqual(participant_values(32, 99, 'unused'), (29, 30, 31, 32))

    def test_exact_given_draws(self):
        self.assertEqual(participant_values(32, 4, 'substitute', (2, 1)), (31,))
        self.assertEqual(participant_values(16, 99, 'unused', (4, 1)), (13,))
        self.assertEqual(participant_values(16, 99, 'unused', (1, 2)), (17,))
