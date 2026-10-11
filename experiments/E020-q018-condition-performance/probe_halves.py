#!/usr/bin/env python3
"""The ORIGINAL binary's second half on edited half-time states, as immutable records.

    python3 experiments/E020-q018-condition-performance/probe_halves.py fit tired records/half-fit-tired-001.json

The state is E010-r0010's half-time savestate with common.equal_skill_edits(A, B) applied (equal
skills, A's (energy, form) on team 0, B's on team 1, no home share), then, per seed, the main
seed DS:7B62 set. emu_quick.run_half emulates the original's tick loop; the record keeps the
original's final score, final seed and draw count per seed, and the edits (by player word), so
check_condition.py can apply the same bytes and compare the model. Exclusive-create output."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
import emu_quick  # noqa: E402
sys.path.insert(0, str(common.ROOT))
from runtime.model import condition  # noqa: E402

SEEDS = [0, 1, 777, 12345, 31337, 40000, 50000, 65535]


def main():
    a, b, out = sys.argv[1], sys.argv[2], HERE / sys.argv[3]
    data = common.load_state()
    ea, fa = condition.SCENARIOS[a]
    eb, fb = condition.SCENARIOS[b]
    edits = common.equal_skill_edits(data, ea, fa, eb, fb)
    edited = common.apply_edits(data, edits)
    comparisons = []
    for seed in SEEDS:
        run = emu_quick.run_half(common.apply_edits(edited, [common.seed_edit(seed)]))
        if run["strays"] or run["minute_831F"] != 91:
            raise SystemExit(f"seed {seed}: the emulation did not finish cleanly: {run}")
        comparisons.append({"seed": seed, "score": list(run["score"]), "final_seed": run["seed"],
                            "draws": run["draws"]})
        print(seed, run, flush=True)
    with out.open("x") as f:
        json.dump({"schema": "E020-half/1", "method": "Unicorn original 0791:97D3..983C on an edited half-time state",
                   "source_sha256": common.STATE_SHA256, "source_release": "E010",
                   "scenario": {"A_team0": a, "B_team1": b, "A_energy_form": [ea, fa],
                                "B_energy_form": [eb, fb]},
                   "edits": edits, "comparisons": comparisons}, f, indent=1)
        f.write("\n")


if __name__ == "__main__":
    main()
