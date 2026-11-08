"""Main701-counter-compatibility: historical digests omit only unused new telemetry."""
import copy
import unittest
from tests import test_route_entry_config as target


class HistoricalCounters(unittest.TestCase):
    def record(self):
        return dict(result={'score': [1, 2], 'ports': {'names': ['selection'],
                    'calls': {'0791:DEA6': 0, 'other': 3}}}, events=[{'tick': 7}],
                    keys=[13], draws=[2], returned={'EFLAGS': 2}, memory=b'full memory')

    def test_missing_counter_and_original_without_ports_are_unchanged(self):
        for original in (False, True):
            row = self.record()
            if original:
                del row['result']['ports']
            before = copy.deepcopy(row)
            target.accepted_default_fields(row)
            self.assertEqual(row, before)

    def test_zero_counter_only_is_omitted_from_detached_historical_copy(self):
        row = self.record()
        expected = target.accepted_default_fields(row)
        row['result']['ports']['calls']['0791:DDCB'] = 0
        before = copy.deepcopy(row)
        self.assertEqual(target.accepted_default_fields(row), expected)
        self.assertEqual(row, before)

    def test_nonzero_counter_is_refused_without_mutation(self):
        for count in (1, -1, 2):
            row = self.record()
            row['result']['ports']['calls']['0791:DDCB'] = count
            before = copy.deepcopy(row)
            with self.assertRaises(AssertionError):
                target.accepted_default_fields(row)
            self.assertEqual(row, before)

    def test_every_other_field_and_counter_remains_part_of_digest(self):
        row = self.record()
        baseline = target.accepted_default_fields(row)
        for field in row:
            changed = copy.deepcopy(row)
            if field == 'result':
                changed[field]['ports']['calls']['other'] += 1
            elif field == 'memory':
                changed[field] += b'!'
            elif field == 'returned':
                changed[field]['EFLAGS'] += 1
            else:
                changed[field].append(9)
            with self.subTest(field=field):
                self.assertNotEqual(target.accepted_default_fields(changed)[field], baseline[field])
