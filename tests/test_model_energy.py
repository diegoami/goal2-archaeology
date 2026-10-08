"""Literal player records and expected bytes for Q015's instruction paths."""
import unittest
import importlib.util
import contextlib
import io
from pathlib import Path

from runtime.model import energy

spec = importlib.util.spec_from_file_location(
    'check_energy', Path(__file__).resolve().parents[1] /
    'experiments/E017-q015-energy/check_energy.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class Supersession(unittest.TestCase):
    def test_prints_name_and_reason(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            selected = checker.select_records(
                [Path('old.json'), Path('new.json')],
                {'old.json': {'superseded_by': 'new.json', 'reason': 'missing draw'}})
        self.assertEqual(selected, [Path('new.json')])
        self.assertIn('old.json', output.getvalue())
        self.assertIn('missing draw', output.getvalue())

    def test_missing_successor_fails(self):
        with self.assertRaises(ValueError):
            checker.select_records([Path('old.json')],
                {'old.json': {'superseded_by': 'new.json', 'reason': 'missing draw'}})

    def test_every_other_record_is_retained(self):
        with contextlib.redirect_stdout(io.StringIO()):
            selected = checker.select_records(
                [Path('old.json'), Path('new.json'), Path('other.json')],
                {'old.json': {'superseded_by': 'new.json', 'reason': 'missing draw'}})
        self.assertEqual(selected, [Path('new.json'), Path('other.json')])


class Energy(unittest.TestCase):
    def test_quick_period_and_signed_floor(self):
        record = bytes.fromhex('001e190040000000000000001018020000000000')
        self.assertEqual(energy.quick_tick(record, 4), record)
        self.assertEqual(energy.quick_tick(record, 5)[12:15], b'\x10\x18\x01')
        for value in (0, 1, 128, 255):
            r = record[:14] + bytes([value]) + record[15:]
            self.assertEqual(energy.quick_tick(r, 5), r)

    def test_watched_strict_threshold_and_reset(self):
        record = bytes.fromhex('001e190040000000000000001018020000000000')
        self.assertEqual(energy.watched_step(record, 180, True), (record, 180))
        self.assertEqual(energy.watched_step(record, 181, False), (record, 181))
        changed, counter = energy.watched_step(record, 181, True)
        self.assertEqual(changed[12:15], b'\x10\x18\x01')
        self.assertEqual(counter, 0)
        r = record[:14] + b'\x00' + record[15:]
        self.assertEqual(energy.watched_step(r, 181, True), (r, 0))

    def test_restore_not_full_32(self):
        record = bytes.fromhex('001e190040000000000000001018020000000000')
        self.assertEqual(energy.restore(record, 7)[12:15], b'\x07\x18\x18')
        for value in (0, 128, 255):
            r = record[:14] + bytes([value]) + record[15:]
            self.assertEqual(energy.restore(r, 7)[12:15], bytes([7, 24, value]))

    def test_recovery_flag_nonzero_draw_order(self):
        record = bytes.fromhex('001e190040000000000000001010080000000000')
        self.assertEqual(energy.recover(record, 1, [2, 8], [32, 24])[12:15], b'\x10\x16\x16')
        self.assertEqual(energy.recover(record, 255, [1, 8], [32, 24])[12:15], b'\x10\x17\x17')

    def test_recovery_flag_zero_extra_below_16(self):
        record = bytes.fromhex('001e190040000000000000001010080000000000')
        self.assertEqual(energy.recover(record, 0, [3, 1], [32, 24])[12:15], b'\x10\x0f\x0f')
        self.assertEqual(energy.recover(record, 0, [2, 2], [32, 24])[12:15], b'\x10\x10\x10')

    def test_injured_draw_and_recovery_gate(self):
        record = bytes.fromhex('001e190040000000000000001010000000000000')
        self.assertEqual(energy.recover(record, 1, [1, 8, 2], [32, 24])[12:15], b'\x10\x09\x00')
        self.assertEqual(energy.recover(record, 0, [1, 8, 1], [32, 24])[12:15], b'\x10\x09\x09')

    def test_negative_energy_uses_noninjured_branch_but_gate_draw(self):
        record = bytes.fromhex('001e190040000000000000001010ff0000000000')
        self.assertEqual(energy.recover(record, 1, [2, 8, 3], [32, 24])[12:15], b'\x10\x16\xff')

    def test_recovery_bounds_age_strict_and_signed_fitness(self):
        record = bytes.fromhex('001c19004000000000000000101f080000000000')
        self.assertEqual(energy.recover(record, 1, [1, 8], [32, 24])[12:15], b'\x10\x20\x20')
        older = b'\x00\x1d' + record[2:]
        self.assertEqual(energy.recover(older, 1, [1, 8], [32, 24])[12:15], b'\x10\x18\x18')
        negative = record[:13] + b'\xff\x00' + record[15:]
        self.assertEqual(energy.recover(negative, 0, [1, 8, 1], [32, 24])[12:15], b'\x10\x01\x01')

    def test_exact_draw_consumption(self):
        record = bytes.fromhex('001e190040000000000000001010080000000000')
        for draws in ([], [1], [1, 8, 1], [3, 8], [1, 9]):
            with self.assertRaises(ValueError):
                energy.recover(record, 1, draws, [32, 24])

    def test_form_instruction_and_injury_store(self):
        record = bytes.fromhex('001e190040000000000000001018020000000000')
        self.assertEqual(energy.form_delta(record, -2)[12:15], b'\x0e\x18\x02')
        self.assertEqual(energy.form_delta(record, -20)[12:15], b'\x01\x18\x02')
        self.assertEqual(energy.form_delta(record, 256)[12:15], b'\xff\x18\x02')
        self.assertEqual(energy.injure(record)[12:15], b'\x10\x18\x00')


if __name__ == '__main__':
    unittest.main()
