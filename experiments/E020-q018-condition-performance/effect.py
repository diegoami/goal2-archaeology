#!/usr/bin/env python3
"""The effect of condition at equal skill, through the quick-engine model, over all 65,536 seeds.

    python3 experiments/E020-q018-condition-performance/effect.py effect-001.json [A:B ...]

For each scenario pair (A, B) of (energy +0xE, form +0xC) - see runtime/model/condition.py SCENARIOS -
the E010-r0010 half-time state is edited (common.equal_skill_edits) so both sides have identical
skill bytes, tactics and manager, no home share (DS:80FC = 0), score 0-0, and A's condition on
team 0, B's on team 1; the model then plays the second half (46 D733 calls, F012) from EVERY value
of the 16-bit main seed. The same is done with the conditions swapped between the teams, so the
draw order of B19D (the opponent's draw first) cannot favour one side. Counts are exact over the
model's own draws: a seed is a draw, a final score with equal goals is a draw.

The line sums and the exact per-attempt scoring probability (uniform, independent draws assumed:
condition.attempt_probability) are recorded next to the counts."""
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import ROOT  # noqa: E402
sys.path.insert(0, str(ROOT))
from runtime.model import condition, quick_engine  # noqa: E402
import savestate  # noqa: E402

PAIRS = [("fit", "tired"), ("fit", "fit"), ("tired", "tired"), ("fit", "fit_form32"),
         ("example_high", "example_low")]

_MATCH = None


def _init(match):
    global _MATCH
    _MATCH = match


def _chunk(seeds):
    return [condition.play(_MATCH, s) for s in seeds]


def build(a, b):
    data = common.load_state()
    ea, fa = condition.SCENARIOS[a][0], condition.SCENARIOS[a][1]
    eb, fb = condition.SCENARIOS[b][0], condition.SCENARIOS[b][1]
    edits = common.equal_skill_edits(data, ea, fa, eb, fb)
    state = savestate.Savestate(common.apply_edits(data, edits))
    return quick_engine.QuickMatch(state), edits


def run_pair(a, b):
    match, edits = build(a, b)
    sums = [match.line_sums(0, 0, match.teams[0]), match.line_sums(0, 1, match.teams[1])]
    seeds = list(range(condition.SEED_COUNT))
    chunks = [seeds[i::16] for i in range(16)]
    with Pool(4, initializer=_init, initargs=(match,)) as pool:
        parts = pool.map(_chunk, chunks)
    scores = [None] * condition.SEED_COUNT
    for i, part in enumerate(parts):
        for j, sc in enumerate(part):
            scores[chunks[i][j]] = sc
    w0, d, w1, g0, g1 = condition.tally(scores)
    return {"A": a, "B": b, "A_energy_form": condition.SCENARIOS[a], "B_energy_form": condition.SCENARIOS[b],
            "line_sums_team0_gk_def_mid_att": sums[0], "line_sums_team1_gk_def_mid_att": sums[1],
            "attempt_probability_team0": str(condition.attempt_probability(sums[0], sums[1])),
            "attempt_probability_team1": str(condition.attempt_probability(sums[1], sums[0])),
            "seeds": condition.SEED_COUNT, "team0_wins": w0, "draws": d, "team1_wins": w1,
            "team0_goals": g0, "team1_goals": g1}


def main():
    out = HERE / sys.argv[1]
    pairs = [tuple(arg.split(":")) for arg in sys.argv[2:]] or PAIRS    # optional A:B arguments
    results = []
    for a, b in pairs:
        for first, second in ((a, b), (b, a)) if a != b else ((a, b),):
            r = run_pair(first, second)
            print(first, "vs", second, r["team0_wins"], r["draws"], r["team1_wins"],
                  r["line_sums_team0_gk_def_mid_att"], r["line_sums_team1_gk_def_mid_att"], flush=True)
            results.append(r)
    with out.open("x") as f:
        json.dump({"schema": "E020-effect/1", "source_sha256": common.STATE_SHA256,
                   "method": "quick-engine model over every 16-bit main seed; second half from 0-0",
                   "results": results}, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
