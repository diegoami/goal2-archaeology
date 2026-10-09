"""Tests for the E019 events-morale checker (R1, R2, R3, R4).

The checker (experiments/E019-q017-events-morale/check_morale.py) compares
literal-input/expected-output records against the runtime model. The
contracts (from T31, applied to E019; extended by the Sol r2 review):

- every record carries `expected_live`/`expected_saved` (for adjust-form)
  or `expected_panel` (for team-panel) AND `got_live`/`got_saved`/
  `got_panel` (the listing-derived value, NOT the model's output); the
  model's output must equal both. R1, R3.
- every record carries `player_word` (adjust) or `player_words`
  (panel — exactly 11 entries). The comparison is keyed by that field,
  not by side/slot. R2.
- empty sets fail. R2.
- no supersession exemption on output bytes (the only exemptible field
  is `draw`, which this task has none of). R2.

R1 regression: the probe generator does NOT import runtime.model.morale,
so the expected_* and got_* values come from the listing. We verify the
checker actually compares the model against the listing (not against
itself) by:
  (a) monkey-patching runtime.model.morale.event_clamp to return (99, 99);
      the model's output diverges from the listing-derived expected_*, so
      the checker must fail.
  (b) mutating one listing-derived expected_live (28 → 99); the model's
      output equals the listing-derived value, so the checker must fail
      (because the listing-derived expected_* no longer matches the
      model).

R2 regression: a record without player_word (or with the wrong
player_words shape) is rejected by the checker before any check runs.

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
    def run_checker(self, record, *, directory=None, monkey=None):
        """Run the checker on a single in-memory record.

        `monkey` is an optional callable that, given the checker module,
        mutates the names the checker uses. Used by the R1 regression
        tests to simulate a broken model — the checker's local `event_clamp`
        and `team_panel_morale` are rebound to broken implementations.
        """
        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            tmp_path = Path(tmp)
            (tmp_path / 'probe-literal-001.json').write_text(json.dumps(record))
            if directory is None:
                directory = tmp_path
            if monkey is None:
                with patch('sys.argv', ['checker', '--directory', str(directory)]):
                    return CHECKER.main()
            # Patch the names in the checker's module namespace. The checker
            # imports event_clamp and team_panel_morale at module load, so
            # patching the source module does NOT affect the checker's
            # already-bound names. Patch the checker module directly.
            saved = {k: getattr(CHECKER, k) for k in (
                'event_clamp', 'team_panel_morale',
            )}
            try:
                monkey(CHECKER)
                with patch('sys.argv', ['checker', '--directory', str(directory)]):
                    return CHECKER.main()
            finally:
                for k, v in saved.items():
                    setattr(CHECKER, k, v)

    def test_canonical_record_passes(self):
        # The committed probe record has 22 cases and all match the model.
        self.assertEqual(self.run_checker(fresh_record()), 0)

    # R1: the probe generator does NOT import runtime.model.morale. Both
    # expected_* and got_* are listing-derived. The checker verifies the
    # model's output equals BOTH. Mutating got_* / expected_* (to a value
    # different from the model's output) makes the checker fail.

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

    # R1 regressions: the checker actually compares the model against the
    # listing (not against itself). The probe generator must NOT import
    # the model — these tests prove the comparison is real.

    def test_r1_monkey_patch_event_clamp_fails_checker(self):
        """If the model's event_clamp returns (99, 99), the checker must
        fail: the listing-derived expected_live (28 for
        injury_high_morale) does not equal the patched model output.

        This regression demonstrates the probe file is independent of the
        model — replacing the model's output changes the check result.
        """
        record = fresh_record()
        def monkey(checker_mod):
            checker_mod.event_clamp = lambda *a, **kw: (99, 99)
        # The checker returns non-zero on a mismatch.
        self.assertEqual(self.run_checker(record, monkey=monkey), 1)

    def test_r1_monkey_patch_team_panel_fails_checker(self):
        """If the model's team_panel_morale returns 99, the checker must
        fail: the listing-derived expected_panel (1 for all_zero) does
        not equal the patched model output.
        """
        record = fresh_record()
        def monkey(checker_mod):
            checker_mod.team_panel_morale = lambda *a, **kw: 99
        self.assertEqual(self.run_checker(record, monkey=monkey), 1)

    def test_r1_wrong_expected_live_fails_checker(self):
        """If the listing-derived expected_live is mutated to 99, the
        checker must fail: the model's output (28 for
        injury_high_morale) does not equal the listing-derived value.

        This regression demonstrates the checker compares the model
        against the listing (not against itself).
        """
        record = fresh_record()
        for case in record['cases']:
            if case['case'] == 'injury_high_morale':
                # 28 is the listing-derived answer; 99 is a wrong value.
                case['expected_live'] = 99
                # Note: got_live stays at 28 (listing-derived).
                break
        self.assertEqual(self.run_checker(record), 1)

    def test_r1_wrong_expected_panel_fails_checker(self):
        """If the listing-derived expected_panel is mutated to 99, the
        checker must fail: the model's output (1 for all_zero) does not
        equal the listing-derived value.
        """
        record = fresh_record()
        for case in record['cases']:
            if case['case'] == 'all_zero':
                case['expected_panel'] = 99
                break
        self.assertEqual(self.run_checker(record), 1)

    # R2: every record must carry player_word (adjust) or player_words
    # (panel — exactly 11 entries). The comparison is keyed by that
    # field, not by side/slot. Records without the field are rejected.

    def test_r2_missing_player_word_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'before' in case and 'delta_high' in case:
                del case['player_word']
                break
        with self.assertRaisesRegex(ValueError, 'missing player_word'):
            self.run_checker(record)

    def test_r2_missing_player_words_panel_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'starters' in case:
                del case['player_words']
                break
        with self.assertRaisesRegex(ValueError, 'missing player_words'):
            self.run_checker(record)

    def test_r2_wrong_player_words_length_fails(self):
        record = fresh_record()
        for case in record['cases']:
            if 'starters' in case:
                case['player_words'] = list(range(1, 11))  # only 10
                break
        with self.assertRaisesRegex(ValueError, 'player_words must have 11 elements'):
            self.run_checker(record)

    def test_r2_player_word_must_be_16bit(self):
        record = fresh_record()
        for case in record['cases']:
            if 'before' in case and 'delta_high' in case:
                case['player_word'] = 70000  # > 0xFFFF
                break
        with self.assertRaisesRegex(ValueError, 'not a 16-bit unsigned int'):
            self.run_checker(record)

    def test_r2_side_slot_only_no_player_word_fails(self):
        """A record keyed only by side/slot (no player_word) is the
        exact case the review called out. The checker must reject it
        before any check runs.
        """
        record = fresh_record()
        for case in record['cases']:
            if 'before' in case and 'delta_high' in case:
                del case['player_word']
                # side and slot are still present.
                self.assertIn('side', case)
                self.assertIn('slot', case)
                break
        with self.assertRaisesRegex(ValueError, 'missing player_word'):
            self.run_checker(record)

    # R3 (kept from previous rework): empty sets fail, unknown schema
    # fails, unknown case shape fails.

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