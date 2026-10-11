#!/usr/bin/env python3
"""An input run of the whole-match harness (T38 Done-when 3).

    python3 experiments/E021-m0-whole-match/input_run.py [--record E011-r0001] [--side 0] [--xor 0x01]

From an E011 record's watchstart state (the captain screen, before the kick-off), emulate the match
twice to the full-time board: unchanged, and with one declared input write, the +0x2D byte (the
default team tactic set, F010) of the country playing on `--side` XORed with `--xor` (bit k-1 is
tactic element k; the default 0x01 flips element 1, position: stay back / push forward). The
record written under experiments/E021-m0-whole-match/out/ carries the write (address, old and new
bytes), both runs' scores, scorers and keys, and where the changed run's seed leaves the unchanged
run's trajectory: the first seed write that differs (its index and clock reading), and the first
clock reading at which the changed run's seed takes a value the unchanged run's word never takes
under that reading (F013's rule, the one check.py applies to the ground truth) — or "none", with
why."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import asset, draws_digest, emulate, write_out  # noqa: E402


def first_difference(base, changed):
    """The first index at which the two seed-write sequences differ, with both writes."""
    for i, (a, b) in enumerate(zip(base, changed)):
        if a != b:
            return i, a, b
    if len(base) != len(changed):
        i = min(len(base), len(changed))
        return i, base[i] if i < len(base) else None, changed[i] if i < len(changed) else None
    return None


def first_off_trajectory(base_sets, changed):
    """The first seed write of the changed run whose value (before or after) is not among the
    values the unchanged run's word takes under the same clock reading."""
    for i, (minute, subtick, before, after) in enumerate(changed):
        s = base_sets.get((minute, subtick), ())
        for v in (before, after):
            if v not in s:
                return {"write_index": i, "minute": minute, "sub_tick": subtick, "value": v,
                        "unchanged_values_at_that_reading": len(s)}
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", default="E011-r0001")
    ap.add_argument("--side", type=int, choices=(0, 1), default=0)
    ap.add_argument("--xor", type=lambda s: int(s, 0), default=0x01)
    a = ap.parse_args(argv)
    record = json.loads((ROOT / "runs/E011" / f"{a.record}.json").read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    data = asset(entry)

    base, base_err, base_s = emulate(data, "none")
    if base_err or not base.stopped_at_board:
        raise SystemExit(f"the unchanged run did not reach the board: {base_err}")
    country = base.sides()[a.side]

    def write(m):
        old = m.mem(m.country_lin(country) + 0x2D, 1)[0]
        m.set_country_tactics(country, old ^ a.xor)

    changed, err, secs = emulate(data, "none", inputs=[write])
    diff = first_difference(base.draws, changed.draws)
    off = first_off_trajectory(base.tick_values(), changed.draws)
    if diff is None:
        why = ("the two runs' seed writes are identical: the changed tactic element was never read "
               "on a path that draws, or every read gave the same branch")
    else:
        why = None
    summary = {
        "record": a.record, "start_state": {"name": entry["name"], "sha256": entry["sha256"]},
        "side": a.side, "country": country, "xor": a.xor,
        "declared_write": changed.inputs,
        "unchanged": {"score": base.final["score"], "scorers": base.scorers(), "final": base.final,
                      "draws_count": len(base.draws), "draws_sha256": draws_digest(base.draws),
                      "key_log": base.key_log, "strays": base.strays, "seconds": base_s},
        "changed": {"completed_to_full_time": changed.stopped_at_board, "error": err,
                    "score": changed.final["score"], "scorers": changed.scorers() if changed.stopped_at_board else None,
                    "final": changed.final, "draws_count": len(changed.draws),
                    "draws_sha256": draws_digest(changed.draws), "key_log": changed.key_log,
                    "strays": changed.strays, "seconds": secs},
        "first_differing_seed_write": None if diff is None else {
            "index": diff[0], "unchanged": diff[1], "changed": diff[2]},
        "first_tick_off_the_unchanged_trajectory": off if off is not None else "none",
        "why_none": why,
    }
    if changed.stopped_at_board:
        summary["changed"]["outputs"] = {k: v for k, v in changed.outputs().items() if k != "draws"}
    path = write_out(f"input-tactics-side{a.side}-xor{a.xor:02x}", a.record, summary)
    print(f"{a.record}: declared write {changed.inputs[0]['what']} at linear 0x{changed.inputs[0]['linear']:05x}:"
          f" {changed.inputs[0]['old']} -> {changed.inputs[0]['new']} (plus the declared"
          f" {changed.inputs[-1]['what']} := {changed.inputs[-1]['new']})")
    print(f"  unchanged: score {base.final['score']}, {len(base.draws)} seed writes;"
          f" changed: completed to full time {changed.stopped_at_board}, score {changed.final['score']},"
          f" {len(changed.draws)} seed writes, strays {changed.strays or 'none'}, error {err}")
    if diff is None:
        print(f"  first tick off the unchanged trajectory: none ({why})")
    else:
        print(f"  first differing seed write: #{diff[0]} unchanged {diff[1]} changed {diff[2]}")
        print(f"  first tick off the unchanged trajectory: {off}")
    print(f"  record: {path.relative_to(ROOT)}")
    return 0 if changed.stopped_at_board and not err and not changed.strays else 1


if __name__ == "__main__":
    sys.exit(main())
