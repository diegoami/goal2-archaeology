"""Q016 result-relative player confidence, transcribed from GOAL.EXE.

Listing: 0791:B71C/B364/B7FA (E018 notes). This module models the
post-fixture operations, not temporary in-match morale, injuries, cards,
or the separate effect of arranging a friendly. Callers must preserve
operation order (pool, result, bench draw, and silent-route scorer bonuses).
"""


def _signed(value, bits):
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def _idiv(numerator, denominator):
    return (abs(numerator) // denominator) * (-1 if numerator < 0 else 1)


def change(before, delta):
    """0791:B364: signed byte plus signed word, then clip each call."""
    total = _signed(_signed(before, 8) + _signed(delta, 16), 16)
    return min(32, max(1, total))


def country_rating(continent, continent_rank, world_rank):
    """1771:10E7, country +2C/+2A/+2B (seg_1771_02.asm:697–738)."""
    numerator = _signed((5 - continent) * (33 - continent_rank) + 129 - world_rank, 16)
    return _idiv(numerator, 2)


def result_delta(own_rating, opponent_rating, scores, winner, side, special_kind):
    """0791:B71C; special_kind is the *observed* 1771:5A03 result.

    Ratings are the 1771:10E7 outputs, not line-strength sums. The winner
    byte controls draws and wins, including the shoot-out's winner byte.
    """
    if side not in (0, 1) or winner not in (0, 1, 2) or len(scores) != 2:
        raise ValueError('invalid fixture')
    delta = _idiv(_signed(opponent_rating - own_rating, 16), 32)
    if winner != 2:
        margin = abs(_signed(scores[1], 8) - _signed(scores[0], 8))
        delta = _signed(delta + (margin if winner == side else -margin), 16)
        if (winner == side) == (side == 0 or bool(special_kind)):
            delta = _signed(delta * 2, 16)
    return delta


def participant_values(before, delta, role, draws=None):
    """B7FA exact possible bytes, or singleton with literal bounded draws.

    Draws are in execution order: subtracted draw, then added draw.
    Random draws consumed by fitness/energy are not represented here.
    """
    if role == 'starter':
        if draws is not None:
            raise ValueError('starter has no bench-confidence draws')
        return (change(before, delta),)
    if role not in ('substitute', 'unused'):
        raise ValueError('unknown participation role')
    bound = 2 if role == 'substitute' else 4
    base = change(before, delta) if role == 'substitute' else before
    if draws is None:
        pairs = ((a, b) for a in range(1, bound + 1) for b in range(1, 3))
    else:
        if len(draws) != 2 or not 1 <= draws[0] <= bound or not 1 <= draws[1] <= 2:
            raise ValueError('invalid bench-confidence draws')
        pairs = (draws,)
    return tuple(sorted({change(base, b - a) for a, b in pairs}))
