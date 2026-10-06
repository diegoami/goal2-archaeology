#!/usr/bin/env python3
"""Check the watched-engine Unicorn harness against the E011 ground truth (Done-when 1).

    python3 experiments/E011-q010-watched-engine/emu_check.py [--runs runs/E011]

For each E011 run record: take its half-time savestate (the output asset named by sha256, from
scratch/e011-outputs/ or downloaded from release E011), emulate the second half with
runtime/emul/watched.py (the original binary's own 0791:983F, tick loop, watched engine 9564,
display and clock as real guest code), and check every mid-play second-half read of the record
(minute DS:831F >= 46, clock running) against the emulated trajectory: the read's DS:7B62 must
be one of the values the seed word takes at that minute (E011 notes.md §6 — a savestate read
catches the guest mid-tick, so its phase is host timing, but its minute and seed value are on
the curve). Cross-checks every other record's reads against each emulation. Ends with
`match: N/N`; every checkpoint must match."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import driver  # noqa: E402
import savestate  # noqa: E402
from watched import WatchedHalf  # noqa: E402

HALFTIME = ROOT / "scratch/e011-outputs"
DL = ROOT / ".cache/dl"


def halftime_sav(entry):
    """The half-time savestate an E011 record names, sha256-checked (downloaded when missing)."""
    local = HALFTIME / entry["name"]
    if not local.is_file() or driver.sha256(local.read_bytes()) != entry["sha256"]:
        asset = f"{entry['sha256'][:16]}-{entry['name']}"
        DL.mkdir(parents=True, exist_ok=True)
        path = DL / asset
        if not path.is_file():
            subprocess.run(["gh", "release", "download", "E011", "--repo", "diegoami/goal2-archaeology",
                            "--pattern", asset, "--dir", str(DL)], check=True)
        data = path.read_bytes()
        if driver.sha256(data) != entry["sha256"]:
            raise SystemExit(f"{path}: sha256 does not match the record's {entry['sha256']}")
        return data
    return local.read_bytes()


def trajectory(record):
    """The record's mid-play reads: [(minute, sub-tick, seed)] (the ground-truth observation)."""
    obs = next(o for o in record["observations"] if o.get("field", "").startswith("ground-truth trajectory"))
    return [tuple(p) for p in json.loads(obs["value"])]


def checkpoints(record):
    return [(m, s) for (m, d, s) in trajectory(record) if m >= 46]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs/E011"))
    a = ap.parse_args(argv)
    records = sorted(Path(a.runs).glob("E011-r*.json"))
    if not records:
        raise SystemExit(f"no records under {a.runs}")
    n = ok = 0
    for p in records:
        record = json.loads(p.read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
        half = WatchedHalf(halftime_sav(entry)).run()
        print(f"{record['run_id']}: emulated second half: {half.final['ticks']} clock ticks,"
              f" {len(half.draws)} main-seed draws, final minute {half.final['831F']},"
              f" seed 0x{half.final['7B62']:04x}, score {half.final['score']};"
              f" 000E strays: {half.strays or 'none'}", flush=True)
        if half.strays:
            raise SystemExit(f"{record['run_id']}: the 000E wait family ran: the skip is wrong, the run is void")
        sets = half.minute_values()
        # the record's own checkpoints, then every other record's (they lie on the same curve)
        for q in records:
            other = json.loads(q.read_text())
            for minute, seed in checkpoints(other):
                n += 1
                hit = seed in sets.get(minute, ())
                ok += hit
                if not hit:
                    print(f"  MISS: {other['run_id']} read at minute {minute} seed 0x{seed:04x}"
                          f" is not on {record['run_id']}'s emulated curve"
                          f" ({len(sets.get(minute, ()))} values that minute)")
    print(f"match: {ok}/{n}")
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
