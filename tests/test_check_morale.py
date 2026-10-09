"""Tests for the E019 events-morale checker (R2, R3, R4).

The checker (experiments/E019-q017-events-morale/check_morale.py) compares
literal-input/expected-output records against the runtime model. The
contracts (from T31, applied to E019):

- every record carries `expected_live`/`expected_saved` (for adjust-form)
  or `expected_panel` (for team-panel) AND `got_live`/`got_saved`/
  `got_panel` (the captured model output); the captured must equal the
  model output, and the expected must equal the captured. R3.
- empty sets fail. R2.
- no supersession exemption on output bytes (the only exemptible field
  is `draw`, which this task has none of). R2.

These tests fail the checker with each kind of record tampering.
"""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'morale_checker', ROOT / 'experiments/E019-q017-events-morale/check_morale.py'
)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


PROBE_PATH = ROOT / 'experiments/E019-q017-events-morale/probe-literal-001.json'


def fresh_record():
    """A copy of the canonical probe record, in memory."""
    return json.loads(PROBE_PATH.read_text())


class CheckerTests(unittest.TestCase):
    def run_checker(self, record, *, directory=None):
        """Run the checker on a single in-memory record."""
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            tmp_path = Path(tmp)
            (tmp_path / 'probe-literal-001.json').write_text(json.dumps(record))
            if directory is None:
                directory = tmp_path
            with patch('sys.argv', ['checker', '--directory', str(directory)]):
                return CHECKER.main()

    def test_canonical_record_passes(self):
        # The committed probe record has 22 cases and all match the model.
        self.assertEqual(self.run_checker(fresh_record()), 0)

    # R3: the captured got_* must equal the model's output for the case to
    # count. Mutating got_panel/got_live/got_saved to a different value
    # (or removing them) makes the checker fail.

    def test_mutated_got_panel_fails(self):
        record = fresh_record()
        # Find a panel case and change its got_panel.
        for case in record['cases']:
            if 'starters' in case:
                case['got_panel'] = 99
                break
        # The checker compares the model's output to BOTH got_panel and
        # expected_panel; mutating got_panel to 99 (≠ model output) fails.
        self.assertEqual(self.run_checker(record), 1)

    def test_missing_got_panel_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'starters' in case:
                del case['got_panel']
                break
        with self.assertRaisesRegex(ValueError, 'missing got_panel'):
            self.run_checker(record)

    def test_mutated_got_live_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'before' in case and 'delta_high' in case:
                case['got_live'] = 99
                break
        self.assertEqual(self.run_checker(record), 1)

    def test_missing_got_live_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'before' in case and 'delta_high' in case:
                del case['got_live']
                break
        with self.assertRaisesRegex(ValueError, 'missing got_live'):
            self.run_checker(record)

    def test_mutated_expected_panel_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'starters' in case:
                case['expected_panel'] = 99
                break
        self.assertEqual(self.run_checker(record), 1)

    def test_mutated_expected_live_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'before' in case and 'delta_high' in case:
                case['expected_live'] = 99
                break
        self.assertEqual(self.run_checker(record), 1)

    def test_empty_set_fails(self):
        with self.assertRaisesRegex(ValueError, 'empty comparison set'):
            self.run_checker({'schema': 'E019-events-morale-probe/1', 'cases': []})

    def test_unknown_schema_fails(self):
        record = fresh_record()
        record['schema'] = 'E019-events-morale-probe/0'
        with self.assertRaisesRegex(ValueError, 'unknown schema'):
            self.run_checker(record)

    def test_case_without_known_shape_fails(self):
        record = fresh_record()
        record['cases'].append({'case': 'unknown_shape', 'method': 'none'})
        with self.assertRaisesRegex(ValueError, 'unknown shape'):
            self.run_checker(record)


if __name__ == '__main__':
    unittest.main()
