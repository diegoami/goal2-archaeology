#!/usr/bin/env python3
"""E010 (T24): a slow replay of one record's second half, polled read by read, to find the first
minute and draw where the original and `runtime/model/quick_engine.py` diverge (T24 step 1).

    python3 experiments/E010-q010-quick-engine/replay.py --record E010-r0010 --cycles 300

The record's published half-time savestate (release E010, sha256-checked) is staged as a start
state and loaded into a fresh DOSBox-X at a low `cycles` value, so one game minute lasts seconds
instead of tens of milliseconds and consecutive reads (each a savestate; I2) catch the match
mid-minute. The key that leaves the half-time stall is one Enter (the stall says `hit any key`;
E010's notes batch 2: the wait consumes no RNG). Every read records DS:831F (the minute),
DS:831B, the seed DS:7B62, the score DS:9B3C/9B3D and the substitution budgets DS:9B3A into
`trace-<record>-replay.json` here (an addition; the ten records are never touched). F006: the
cycles value does not change a match. Interventions: I1 (memory reads) and I2 (savestates, one
load); no edit (the record's own half-time state is replayed as published)."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import driver  # noqa: E402
import savestate  # noqa: E402

OUT = Path(__file__).resolve().parent
HALFTIME = ROOT / "scratch" / "e010-halftime"
DL = ROOT / ".cache" / "dl"
SCRATCH_STAGES = ROOT / "scratch" / "e010" / "states"


def halftime_sav(entry):
    """As check_model.halftime_sav: the published, sha256-checked half-time savestate."""
    local = HALFTIME / entry["name"]
    if not local.is_file() or driver.sha256(local.read_bytes()) != entry["sha256"]:
        asset = f"{entry['sha256'][:16]}-{entry['name']}"
        DL.mkdir(parents=True, exist_ok=True)
        path = DL / asset
        if not path.is_file():
            subprocess_run_download(asset)
        data = path.read_bytes()
        if driver.sha256(data) != entry["sha256"]:
            raise SystemExit(f"{path}: sha256 does not match the record's {entry['sha256']}")
        return data
    return local.read_bytes()


def subprocess_run_download(asset):
    import subprocess
    subprocess.run(["gh", "release", "download", "E010", "--repo", "diegoami/goal2-archaeology",
                    "--pattern", asset, "--dir", str(DL)], check=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", required=True, help="an E010 run id, e.g. E010-r0010")
    ap.add_argument("--cycles", type=int, default=300, help="DOSBox-X cycles for the replay")
    ap.add_argument("--timeout", type=float, default=900.0)
    a = ap.parse_args(argv)

    record = json.loads((ROOT / "runs" / "E010" / f"{a.record}.json").read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    blob = halftime_sav(entry)
    if driver.sha256(blob) != entry["sha256"]:
        raise SystemExit("half-time blob hash mismatch")
    sc_digest = savestate.Savestate(blob).screen().digest()

    d = driver.Driver({"cycles": a.cycles}, workdir=driver.SCRATCH / "e010" / f"replay-{a.record}")
    trace = []
    try:
        # stage the published half-time state as this driver's start state (as run.py stages arms)
        SCRATCH_STAGES.mkdir(parents=True, exist_ok=True)
        name = f"{a.record}-halftime-replay"
        (SCRATCH_STAGES / f"{name}.sav").write_bytes(blob)
        meta = {"sha256": entry["sha256"], "screen_digest": sc_digest, "game_dir": str(d.game_dir),
                "drive_layout": d.drive_layout(), "config": {"cycles": a.cycles}}
        (SCRATCH_STAGES / f"{name}.json").write_text(json.dumps(meta))
        st = driver.StartState(name, SCRATCH_STAGES)
        d.launch(st)
        t0 = time.monotonic()
        # wait for the stall to be visibly stable (as match.play does) before the key: an Enter
        # sent in the same breath as the restore is swallowed, and the stall never opens
        prev_dg, sent = None, 0
        while time.monotonic() - t0 < a.timeout and sent < 5:
            times, state, _ = d.read()
            sc = state.screen()
            dg = sc.digest()
            stable = dg == prev_dg
            if stable and "hit any key" in sc.lines()[-1]:
                d.keys("Enter", hold=1.0)   # leave the half-time stall (hit any key; no RNG
                sent += 1                    # consumed); 1 s hold: 0.08 s is missed at 1000 cycles
                stall_dg = dg
            prev_dg = dg
            print(f"pre-read: dg={dg[:6]} stable={stable} sent={sent} last={sc.lines()[-1].strip()[:30]!r}",
                  flush=True)
            if sent and dg != stall_dg:
                break   # the stall has opened; the recording loop takes over

        def dump():
            out = OUT / f"trace-{a.record.lower()}-replay.json"
            out.write_text(json.dumps(trace) + "\n")

        while time.monotonic() - t0 < a.timeout:
            times, state, _ = d.read()
            n = len(trace) + 1
            sc = state.screen()
            rows = sc.lines()
            trace.append({
                "n": n, "t": round(time.monotonic() - t0, 3),
                "m831f": state.ds_word(0x831F), "m831b": state.ds_bytes(0x831B, 1)[0],
                "seed": state.ds_word(0x7B62),
                "score": list(state.ds_bytes(0x9B3C, 2)),
                "budget": list(state.ds_bytes(0x9B3A, 2)),
                "dg": sc.digest()[:6], "ft": any("FULL TIME" in r for r in rows[1:4]),
            })
            last = trace[-1]
            print(f"read {n}: t={last['t']} 831F={last['m831f']} seed={last['seed']:04x} "
                  f"score={last['score']} ft={last['ft']}", flush=True)
            dump()
            dg = sc.digest()
            stable = dg == prev_dg
            prev_dg = dg
            if sent and stable and trace[-1]["ft"]:
                break
    finally:
        d.terminate()
    print(f"{len(trace)} reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
