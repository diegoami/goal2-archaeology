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

    OLD, NEW = 'fixture-probe-old.json', 'fixture-probe-new.json'

    def declare(self, defects=('squad', 'status')):
        return {self.OLD: {'replacement': self.NEW, 'defects': list(defects), 'reason': 'defective'}}

    def op(self, case, word, site):
        return next(o for o in case['operations'] if o['player_word'] == word and o['return_ip'] == site)

    def break_squad(self, case):
        # Swap the injected squad words of slots 1 and 2 of country 1 (literal bytes).
        country = case['countries'][0]
        record = bytes.fromhex(country['record'])
        country['record'] = (record[2:4] + record[0:2] + record[4:]).hex()

    def break_status(self, case):
        # The participant's status written at +7 instead of +0x10, as the declared defect.
        p = next(p for p in case['before'] if p['slot'] == 12)
        record = bytearray(bytes.fromhex(p['record']))
        record[16], record[7] = 0, 8
        p['record'] = record.hex()

    def test_consistent_record_cannot_be_declared_defective(self):
        record = self.record()
        with self.assertRaisesRegex(ValueError, 'case 1 passes its declared squad check'):
            self.run_checker({self.OLD: record, self.NEW: record}, self.declare())

    def test_wrong_delta_with_consistent_squad_is_not_set_aside(self):
        old = self.record()
        self.op(old['cases'][0], 1, 0xB951)['delta_word'] += 1
        with self.assertRaisesRegex(ValueError, 'case 1 passes its declared squad check'):
            self.run_checker({self.OLD: old, self.NEW: self.record()}, self.declare())
        with self.assertRaisesRegex(ValueError, 'case 1 passes its declared squad check'):
            self.run_checker({self.OLD: old, self.NEW: self.record()}, self.declare(['squad']))

    def test_one_defective_case_is_not_set_aside(self):
        old = self.record()
        self.break_squad(old['cases'][0])
        self.break_status(old['cases'][0])
        with self.assertRaisesRegex(ValueError, 'case 2 passes its declared squad check'):
            self.run_checker({self.OLD: old, self.NEW: self.record()}, self.declare())

    def test_every_declared_defect_must_fail(self):
        old = self.record()
        for case in old['cases']:
            self.break_squad(case)
        with self.assertRaisesRegex(ValueError, 'case 1 passes its declared status check'):
            self.run_checker({self.OLD: old, self.NEW: self.record()}, self.declare())
        self.assertEqual(self.run_checker({self.OLD: old, self.NEW: self.record()}, self.declare(['squad'])), 0)
        for case in old['cases']:
            self.break_status(case)
        self.assertEqual(self.run_checker({self.OLD: old, self.NEW: self.record()}, self.declare()), 0)

    def test_retained_defective_probe_is_set_aside_by_its_declaration(self):
        directory = ROOT / 'experiments/E018-q016-confidence'
        records = {name: json.loads((directory / name).read_text())
                   for name in ('fixture-probe-002.json', 'fixture-probe-003.json')}
        supersessions = json.loads((directory / 'supersessions.json').read_text())
        self.assertEqual(self.run_checker(records, supersessions), 0)

    def test_declaration_must_name_known_defects(self):
        for defects in ([], ['squad', 'squad'], ['delta']):
            with self.subTest(defects=defects):
                with self.assertRaisesRegex(ValueError, 'declared defects'):
                    self.run_checker({self.OLD: self.record(), self.NEW: self.record()}, self.declare(defects))

    def test_unpaired_or_uncovered_supersession_fails(self):
        with self.assertRaisesRegex(ValueError, 'unpaired or chained'):
            self.run_checker({self.OLD: self.record()}, self.declare())
        short = self.record()
        short['cases'] = short['cases'][1:]
        with self.assertRaisesRegex(ValueError, 'does not cover'):
            self.run_checker({self.OLD: self.record(), self.NEW: short}, self.declare())

    def assert_kept_fails(self, record, message):
        with self.assertRaisesRegex(ValueError, message):
            self.run_checker({self.NEW: record}, {})

    def test_kept_record_checks_declared_inputs(self):
        record = self.record()
        self.break_squad(record['cases'][3])
        self.assert_kept_fails(record, 'declared slot disagrees with injected squad')
        record = self.record()
        self.break_status(record['cases'][3])
        self.assert_kept_fails(record, r'declared status disagrees with injected \+0x10')
        record = self.record()
        p = record['cases'][3]['before'][0]
        p['record'] = (bytes.fromhex(p['record'])[:16] + b'\x04' + bytes.fromhex(p['record'])[17:]).hex()
        self.assert_kept_fails(record, r'declared status disagrees with injected \+0x10')

    def test_kept_record_guards(self):
        # One literal edit per guard of check_case; each must fail the checker.
        def strays(case):
            case['strays'] = [{'ip': 1}]

        def sites(case):
            self.op(case, 1, 0xB951)['return_ip'] = 0xB991

        def b71c(case):
            self.op(case, 1, 0xB951)['delta_word'] += 1

        def bounds(case):
            count = self.op(case, 13, 0xB9BB)['draw_count']
            case['draws'][count - 2]['bound'] = 2

        def arithmetic(case):
            self.op(case, 13, 0xB9BB)['delta_word'] += 1

        def unaccounted(case):
            case['operations'].append({'return_ip': 0xB951, 'delta_word': 0, 'player_word': 999, 'draw_count': 0})

        def missing(case):
            del case['after'][0]

        for edit, message in [(strays, 'skipped a reachable call'),
                              (sites, 'unexpected confidence call sites'),
                              (b71c, 'result delta disagrees with original B71C'),
                              (bounds, 'confidence draw bounds disagree'),
                              (arithmetic, 'confidence draw arithmetic disagrees'),
                              (unaccounted, 'unaccounted confidence calls'),
                              (missing, 'missing or duplicate player-word comparison')]:
            with self.subTest(guard=message):
                record = self.record()
                edit(record['cases'][0])
                self.assert_kept_fails(record, message)
        record = self.record()
        record['schema'] = 'E018-confidence-probe/0'
        self.assert_kept_fails(record, 'unknown record schema')

    def test_checker_reads_the_kind_set(self):
        # Kind 3 is in the retained DS:0F3E bytes (0x98: bits 3, 4, 7). Declaring
        # it for case 1 (3-1, side 1 lost) removes side 1's doubling, so the
        # guest's recorded delta (from kind 1) no longer agrees.
        record = self.record()
        fixture = bytearray(bytes.fromhex(record['cases'][0]['fixture']))
        fixture[2] = 3
        record['cases'][0]['fixture'] = fixture.hex()
        self.assert_kept_fails(record, 'result delta disagrees with original B71C')

    def test_empty_comparisons_fail(self):
        with self.assertRaisesRegex(ValueError, 'empty comparison set'):
            self.run_checker({}, {})

    def test_kept_mismatch_fails(self):
        record = self.record()
        record['cases'][0]['after'][0]['confidence'] = 0
        self.assertEqual(self.run_checker({'fixture-probe-new.json': record}, {}), 1)

    def test_run_observation_divergence_fails(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            root = Path(directory)
            (root / 'runs/E018').mkdir(parents=True)
            record = self.record()
            (root / 'fixture-probe-new.json').write_text(json.dumps(record))
            (root / 'supersessions.json').write_text('{}')
            case = record['cases'][0]
            case['after'][0]['confidence'] = 0
            run = {'observations': [{'field': 'trace fixture-probe-new.json'},
                                    {'value': json.dumps(case)}]}
            (root / 'runs/E018/E018-r0001.json').write_text(json.dumps(run))
            with patch.object(CHECKER, 'ROOT', root), patch.object(CHECKER, '__file__', str(root / 'check_confidence.py')):
                with patch('sys.argv', ['checker', '--directory', directory]):
                    with self.assertRaisesRegex(ValueError, 'run observations disagree'):
                        CHECKER.main()

from runtime.model.confidence import change, result_delta, participant_values, country_rating, match_form


class ConfidenceTests(unittest.TestCase):
    def test_literal_arithmetic_boundaries(self):
        for before, delta, expected in [(0, 0, 1), (1, 0, 1), (2, 0, 2),
                                        (31, 0, 31), (32, 0, 32), (33, 0, 32),
                                        (127, 0, 32), (128, 0, 1), (255, 0, 1),
                                        (1, 32767, 1), (1, 32768, 1)]:
            self.assertEqual(change(before, delta), expected)
        for opponent, expected in [(67, -1), (68, -1), (69, 0),
                                   (131, 0), (132, 1), (133, 1)]:
            self.assertEqual(result_delta(100, opponent, (0, 0), 2, 0, False), expected)
        for live, expected in [(0, (1, 1)), (1, (1, 1)), (31, (31, 31)),
                               (32, (32, 32)), (33, (33, 32)),
                               (127, (127, 32)), (128, (1, 1))]:
            self.assertEqual(match_form(live, 16, 0, True), expected)
        for role, draws, expected in [('substitute', (1, 1), (16,)),
                                      ('substitute', (2, 2), (16,)),
                                      ('unused', (1, 1), (16,)),
                                      ('unused', (4, 2), (14,))]:
            self.assertEqual(participant_values(16, 0, role, draws), expected)
        for role, draws in [('substitute', (0, 1)), ('substitute', (3, 1)),
                            ('unused', (0, 1)), ('unused', (5, 1)),
                            ('unused', (1, 0)), ('unused', (1, 3))]:
            with self.assertRaises(ValueError):
                participant_values(16, 0, role, draws)

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

    def test_term_size_not_monotonic_in_margin(self):
        # Ratings 128 vs 1, q = +/-3; the sign follows margin minus -q, the
        # doubling (winner==side) == (side==0 or 5A03) breaks monotonicity.
        cases = [((128, 1, (1, 0), 0, 0, False), -4),   # strong side 0 wins by 1
                 ((128, 1, (0, 0), 2, 0, False), -3),   # strong side 0 draws
                 ((128, 1, (0, 1), 1, 0, False), -4),   # strong side 0 loses by 1
                 ((1, 128, (1, 0), 0, 1, False), 4),    # weak side 1 loses by 1
                 ((1, 128, (0, 0), 2, 1, False), 3),    # weak side 1 draws
                 ((1, 128, (0, 1), 1, 1, False), 4)]    # weak side 1 wins by 1
        for inputs, expected in cases:
            with self.subTest(inputs=inputs):
                self.assertEqual(result_delta(*inputs), expected)

    def test_equal_scores_with_winner_byte_are_not_a_draw(self):
        # 1-1 with winner byte 0 (a shoot-out): not the draw branch; doubling applies.
        self.assertEqual(result_delta(100, 164, (1, 1), 0, 0, False), 4)
        self.assertEqual(result_delta(100, 164, (1, 1), 2, 0, False), 2)

    def test_participating_substitute_gets_result_term(self):
        self.assertEqual(participant_values(16, 4, 'substitute', (1, 1)), (20,))

    def test_invalid_inputs_rejected(self):
        for inputs in [(100, 100, (1, 0), 0, 2, False), (100, 100, (1, 0), 3, 0, False),
                       (100, 100, (1, 0, 0), 0, 0, False)]:
            with self.subTest(inputs=inputs):
                with self.assertRaises(ValueError):
                    result_delta(*inputs)
        with self.assertRaises(ValueError):
            participant_values(16, 4, 'starter', (1, 1))
        with self.assertRaises(ValueError):
            participant_values(16, 4, 'reserve', (1, 1))

    def test_exact_given_draws(self):
        self.assertEqual(participant_values(32, 4, 'substitute', (2, 1)), (31,))
        self.assertEqual(participant_values(16, 99, 'unused', (4, 1)), (13,))
        self.assertEqual(participant_values(16, 99, 'unused', (1, 2)), (17,))
