#!/usr/bin/env python3
"""Fitness, energy and confidence in a match, at equal skill (Q018, T36; F021, E020).

What a player's condition does in GOAL.EXE's match engines, as code with the listing line behind
each number:

- **Quick engine** (`0791:D733`). The line sums are 377E(w) per squad word, and 377E reads exactly
  two condition bytes: energy `+0xE` (signed) and form/confidence `+0xC` (signed). `strength` below
  is `quick_engine.QuickMatch.player_strength` itself, called on a literal record: no constant of
  1771:377E is copied here. Fitness `+0xD` is read by no match code; it reaches a match only
  through energy, at the end of the previous one (`0791:CB7D` copies it to a positive `+0xE`).
- **Watched engine** (`0791:9564`). Every skill read is `0791:278A`, which blends the same two
  bytes differently from 377E; `contest` is `keeping.contest_value`, called as it is.
- **The size of the effect.** `attempt_probability` is the exact probability that one of B19D's
  scoring attempts succeeds, from the two sides' line sums, treating every `rand(n)` as uniform on
  1..n and the three contests of an attempt as independent (both are ASSUMPTIONS, named here: the
  generator is a 16-bit LCG whose consecutive outputs are neither). `play`/`tally` run the quick
  model's own second half from a start seed; `E020`'s `effect.py` calls them for every one of the
  65,536 seeds the generator can hold, so the win/draw/loss counts are exact over the model's own
  draws, not a sample.

The scenarios (`SCENARIOS`) are (energy, form) pairs: `fit` and `tired` are the ends of the ranges
the game itself produces (energy 1..32: F018; form 1..32: F019, `0791:B364`'s clamp); `example_low`
and `example_high` are the task's boundary examples (energy 0x3E / 0x7F, form 0x00 / 0x3F), which
are outside what play produces but inside what 377E accepts.

Standard library only (the quick model imports the driver's savestate reader)."""
import copy
from fractions import Fraction

try:                                   # imported as runtime.model.condition (the tests)
    from . import keeping, quick_engine
except ImportError:                    # imported as a top-level module (runtime/model on sys.path)
    import keeping
    import quick_engine

# 1771:377E's 0x20 form threshold, the 0..0x100 clamp and the s8 reads are quick_engine's own;
# the constants below are the ones THIS module adds.
DEFENCE_FACTOR = 2          # 0791:B207: rand(2 * the opponent's defence sum) (shl, seg_0791_18.asm)
MAX_SUM = 0x8000            # B19D compares the draws with a signed `jle`: a sum >= 0x8000 would wrap
SEED_COUNT = 0x10000        # the main seed DS:7B62 is a 16-bit LCG word (F004): 65,536 start seeds

# (energy +0xE, form +0xC); the first two are the ends of what play produces, the last two the
# task's boundary examples.
SCENARIOS = {
    "fit": (32, 31),
    "tired": (1, 1),
    "fit_form32": (32, 32),
    "example_high": (0x7F, 0x3F),
    "example_low": (0x3E, 0x00),
}


class _Record(quick_engine.QuickMatch):
    """A QuickMatch holding only literal player records and the two foot tables 377E's wrong-foot
    test reads (DS:0E60, DS:0E7C): enough to call `player_strength` unchanged."""

    def __init__(self, records, foot_table, foot_index):
        self.playerrec = {word: bytearray(rec) for word, rec in records.items()}
        self.t_foot = bytearray(foot_table)
        self.t_footix = bytearray(foot_index)


def strength(word, record, foot_table, foot_index):
    """1771:377E(word) of the 20-byte player record, as the quick engine computes it."""
    if len(record) != 20:
        raise ValueError("a player record is 20 bytes")
    return _Record({word: record}, foot_table, foot_index).player_strength(word)


def with_condition(record, energy, form):
    """The record with energy +0xE and form +0xC set (fitness +0xD and every skill byte kept)."""
    out = bytearray(record)
    out[0xC], out[0xE] = form, energy
    return bytes(out)


def sweep(word, record, foot_table, foot_index, energies, forms):
    """{(energy, form): 377E} over the grid, at fixed skills."""
    return {(e, f): strength(word, with_condition(record, e, f), foot_table, foot_index)
            for e in energies for f in forms}


def contest(record, element, class_table, profile_table, **flags):
    """0791:278A(pitch, element) of the 20-byte record (the watched engine's only skill read)."""
    return keeping.contest_value(plus4=record[4], plus5=record[5], plus7=record[7],
                                 plus_c=record[0xC], plus_e=record[0xE], element=element,
                                 class_table=class_table, profile_table=profile_table, **flags)


def draw_win(n_own, n_opp):
    """P(rand(n_own) > rand(n_opp)) with both uniform on 1..n (`rand(0)` is 1: 214B:0688 adds 1
    to the high word of seed * n). The contests of B19D test `b <= a` as lost (signed `jle`)."""
    if not 0 <= n_own < MAX_SUM or not 0 <= n_opp < MAX_SUM:
        raise ValueError("a sum outside 0..0x7FFF: B19D's signed compare would not be this")
    n_own, n_opp = max(n_own, 1), max(n_opp, 1)
    wins = sum(min(b - 1, n_opp) for b in range(1, n_own + 1))    # a in 1..n_opp with a < b
    return Fraction(wins, n_own * n_opp)


def attempt_probability(own, opp):
    """P(one B19D attempt scores) for the side with line sums `own` against `opp`; each is
    (keeper, defence, midfield, attack) = the sums at DS:9B45 + 2*side + 4*k, k = 0..3 (0BC4).
    Contest 1: rand(mid_opp) vs rand(mid_own); 2: rand(2*def_opp) vs rand(atk_own); 3: rand(gk_opp)
    vs rand(atk_own) (seg_0791_18.asm:B1DF-B24D). Independent uniform draws are assumed."""
    gk_o, de_o, mi_o, _ = opp
    _, _, mi, at = own
    return draw_win(mi, mi_o) * draw_win(at, DEFENCE_FACTOR * de_o) * draw_win(at, gk_o)


def play(match, seed):
    """The model's second half from `seed`: a copy of the QuickMatch with the main seed set, run;
    returns the final (team 0, team 1) goals. The generator word DS:7B62 is `rng.seed` (F004)."""
    fresh = copy.deepcopy(match)
    fresh.rng.seed = seed
    return tuple(fresh.run()["score"])


def tally(scores):
    """(team 0 wins, draws, team 1 wins, team 0 goals, team 1 goals) over final scores. A draw is
    a draw: equal goals, never a constant."""
    w0 = d = w1 = g0 = g1 = 0
    for a, b in scores:
        g0, g1 = g0 + a, g1 + b
        if a > b:
            w0 += 1
        elif a == b:
            d += 1
        else:
            w1 += 1
    return w0, d, w1, g0, g1
