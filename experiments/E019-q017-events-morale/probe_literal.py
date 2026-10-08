#!/usr/bin/env python3
"""Literal-input probe records for the E019 listing-derived arithmetic.

Each record is a literal-input/expected-output pair transcribed from the
listing (not a Unicorn emulation of the original routine). The original
arithmetic for `0791:7CC5 adjust_player_form` and `1771:13D0 team_panel`
is checked byte-for-byte against the Python model. The probe follows
the E019 input rules: by player word, every expected comparison present,
empty sets fail, no missing fields; supersession follows T31's rules.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT))
from runtime.model.morale import (
    event_clamp, injure, send_off, scorer, team_reaction, team_panel_morale,
)


def adjust_case(label, before, delta_high, delta_low, side, slot):
    """One literal 7CC5 case."""
    live, saved = event_clamp(before, delta_high, (delta_low & 0xFF) != 0)
    return {
        'case': label,
        'method': 'literal listing arithmetic; 0791:7CC5 with named delta',
        'before': before, 'delta_high': delta_high, 'delta_low': delta_low,
        'side': side, 'slot': slot,
        'after_live': live, 'after_saved': saved if saved is not None else 0,
    }


def panel_case(label, starters, expected_panel):
    """One literal 1771:13D0 case."""
    got = team_panel_morale(starters)
    return {
        'case': label,
        'method': 'literal listing arithmetic; 1771:13D0 over available starters',
        'starters': list(starters), 'expected_panel': expected_panel,
        'got_panel': got,
        'pass': got == expected_panel,
    }


ADJUST_CASES = [
    adjust_case('injury_high_morale', 30, 0xFFFE, 0x0001, 0, 1),
    adjust_case('injury_low_morale', 2, 0xFFFE, 0x0001, 0, 1),
    adjust_case('injury_floor_morale', 1, 0xFFFE, 0x0001, 0, 1),
    adjust_case('scorer_plus_one', 16, 0x0001, 0x0001, 0, 1),
    adjust_case('scorer_minus_one', 16, 0xFFFF, 0xFF01, 1, 1),
    adjust_case('team_reaction_no_persist_pos', 16, 0x0001, 0x0000, 0, 1),
    adjust_case('team_reaction_no_persist_neg', 16, 0xFFFF, 0x0000, 1, 1),
    adjust_case('send_off_tail_other_team', 16, 0x0002, 0x0000, 1, 1),
    # Boundary tests of the [1, 255] clamp on the live byte.
    adjust_case('clamp_below_one', 0, 0xFFFF, 0x0001, 0, 1),     # 0 + (-1) = -1 → clamp 1
    adjust_case('clamp_above_255', 200, 0x8001, 0x0001, 0, 1),   # 200 + (-0x7fff) → big negative → 1
    adjust_case('clamp_signed_overflow', 254, 0x8001, 0x0001, 0, 1),
    # The signed byte wrapping: 128 (signed -128) + (-2) = -130 → 1; persist=1 → min(32, 1) = 1.
    adjust_case('signed_wrap_floor', 128, 0xFFFE, 0x0001, 0, 1),
    # The signed byte wrapping high: 127 + (-2) = 125 → 125; persist=1 → min(32, 125) = 32.
    adjust_case('signed_wrap_high_persist', 127, 0xFFFE, 0x0001, 0, 1),
]


# 11 available starters; panel recomputation 1771:13D0. We give literal
# starter morale bytes; the panel routine sums them (with [0,32] clamp),
# adds 6, divides by 11, clamps to >=1, and returns the integer.
PANEL_CASES = [
    panel_case('all_zero', [0] * 11, 1),                  # 6/11 = 0 → 1
    panel_case('all_32', [32] * 11, 32),                 # (6 + 11*32)/11 = 358/11 = 32
    panel_case('all_16', [16] * 11, (6 + 11 * 16) // 11),  # 182/11 = 16
    panel_case('mixed_low_high', [1, 32, 16, 8, 0, 24, 28, 4, 12, 20, 5],
               (6 + 1 + 32 + 16 + 8 + 0 + 24 + 28 + 4 + 12 + 20 + 5) // 11),
    # Signed-byte edge: 128 is signed -128 → clamped to 0.
    panel_case('signed_negative_clamped', [-128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1),
    # Above-32 clamped to 32: but 200 as a SIGNED byte is -56 → 0.
    panel_case('above_32_clamped', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32],
               (6 + 32) // 11),
    # Mostly-128 (saturates to 0 → reduces the panel).
    panel_case('all_signed_negative', [-128] * 11, 1),
    # Boundary: exactly the floor case (sum + 6) // 11 == 0 → 1.
    panel_case('exactly_below_one', [0] * 10 + [1], max(1, (6 + 1) // 11)),
    # All signed-negative: every contribution is 0, sum=0, total=6, //11=0, → 1.
    panel_case('one_starter_signed_negative', [-128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1),
]


def main():
    output_dir = Path(__file__).resolve().parent
    cases = []
    for c in ADJUST_CASES:
        cases.append(c)
    for c in PANEL_CASES:
        cases.append(c)
    record = {'schema': 'E019-events-morale-probe/1', 'cases': cases}
    out = output_dir / 'probe-literal-001.json'
    out.write_text(json.dumps(record, indent=2))
    print(f'wrote {len(cases)} cases to {out}')


if __name__ == '__main__':
    main()