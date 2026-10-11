#!/usr/bin/env python3
"""How well does condition.attempt_probability (uniform, independent draws) describe the real
generator? For each scenario pair, the model's own B19D (`roll_quick_goals(12)`, the attempts of one
D733 call) is run once from every one of the 65,536 seeds on the equal-skill state; the observed
share of scoring attempts per team is printed next to the exact fraction.

    python3 experiments/E020-q018-condition-performance/attempt_check.py attempt-check-001.json"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import ROOT  # noqa: E402
sys.path.insert(0, str(ROOT))
from runtime.model import condition  # noqa: E402
import effect  # noqa: E402

ATTEMPTS = 12           # DS:0A8A[8319 != 0x0F] (F012: B19D's attempts per D733 call)


def main():
    out = HERE / sys.argv[1]
    results = []
    for a, b in (("fit", "tired"), ("fit", "fit"), ("example_high", "example_low")):
        match, _ = effect.build(a, b)
        sums = [match.line_sums(0, 0, match.teams[0]), match.line_sums(0, 1, match.teams[1])]
        goals = [0, 0]
        for seed in range(condition.SEED_COUNT):
            match.rng.seed = seed
            fresh = match.roll_quick_goals(ATTEMPTS)
            goals[0] += fresh[0]
            goals[1] += fresh[1]
        n = condition.SEED_COUNT * ATTEMPTS
        exact = [condition.attempt_probability(sums[0], sums[1]), condition.attempt_probability(sums[1], sums[0])]
        row = {"A_team0": a, "B_team1": b, "line_sums_team0": sums[0], "line_sums_team1": sums[1],
               "attempts_per_team": n, "scoring_attempts_team0": goals[0], "scoring_attempts_team1": goals[1],
               "observed_team0": goals[0] / n, "observed_team1": goals[1] / n,
               "exact_team0": float(exact[0]), "exact_team1": float(exact[1])}
        print(row, flush=True)
        results.append(row)
    with out.open("x") as f:
        json.dump({"schema": "E020-attempt-check/1", "source_sha256": common.STATE_SHA256,
                   "results": results}, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
