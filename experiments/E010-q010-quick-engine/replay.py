#!/usr/bin/env python3
"""E010 (T24): a slow replay of one record's second half, polled read by read, to find the first
minute and draw where the original and `runtime/model/quick_engine.py` diverge (T24 step 1).

    python3 experiments/E010-q010-quick-engine/replay.py --record E010-r0010 [--delay 5]

The record's published half-time savestate (release E010, sha256-checked) is staged with ONE byte
edited — the match delay byte at [DS:A923]+0x3F, 1 -> `--delay` (5) — and loaded into a fresh
DOSBox-X at the normal cycles (30000). The delay byte only paces `0791:9372`'s delay loop
(seg_0791_15.asm:9382-93BB: the loop runs 6-delay times over table DS:0882); it is timing, not
RNG: F004/F005's territory, never read by D733 or its callees. With it raised, one game minute
lasts seconds instead of milliseconds, so consecutive reads (each a savestate; I2) catch the
match mid-minute while the emulator still runs at full speed (a low `cycles` value instead makes
the half-time key miss: 0.08 s holds are lost below ~5000 cycles, and a 1 s hold storms the DOS
keyboard buffer with repeats that open `0791:ED8A`'s menu once per minute).

The keys that leave half time are match.play's own (runtime/driver/match.py `wants_key`): one Enter
on the `hit any key` stall, then one Enter on the team screen (`location:`, the default ` play `
option) — the same two keys the original records were made with, so the RNG path is unchanged (the
waits consume no RNG; E010's notes batch 2). A key is never resent: if the screen does not change
within KEY_TAKEN_READS reads the probe aborts (round 1's resends storm the DOS key buffer and open
`0791:ED8A`'s menu). Every read records DS:831F
(the minute), DS:831B, the seed DS:7B62, the score DS:9B3C/9B3D and the substitution budgets
DS:9B3A into `trace-<record>-replay<suffix>.json` here (an addition; the ten records are never
touched, and no earlier trace is ever overwritten: each probe run gets its own suffix).
Interventions: I1 (memory reads), I2 (savestates, one load) and I3 (the one delay byte, above;
declared here and in notes.md)."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import driver  # noqa: E402
import players  # noqa: E402
import savestate  # noqa: E402

OUT = Path(__file__).resolve().parent
HALFTIME = ROOT / "scratch" / "e010-halftime"
DL = ROOT / ".cache" / "dl"
SCRATCH_STAGES = ROOT / "scratch" / "e010" / "states"
DELAY_PTR = 0xA923   # far pointer to the delay record; +0x3F is the match delay byte (F004)
KEY_TAKEN_READS = 10  # match.py's bound: reads after a key within which the screen must change


def dump(trace, record, suffix):
    (OUT / f"trace-{record.lower()}-replay{suffix}.json").write_text(json.dumps(trace) + "\n")


def halftime_sav(entry):
    """As check_model.halftime_sav: the published, sha256-checked half-time savestate."""
    local = HALFTIME / entry["name"]
    if not local.is_file() or driver.sha256(local.read_bytes()) != entry["sha256"]:
        asset = f"{entry['sha256'][:16]}-{entry['name']}"
        DL.mkdir(parents=True, exist_ok=True)
        path = DL / asset
        if not path.is_file():
            import subprocess
            subprocess.run(["gh", "release", "download", "E010", "--repo", "diegoami/goal2-archaeology",
                            "--pattern", asset, "--dir", str(DL)], check=True)
        data = path.read_bytes()
        if driver.sha256(data) != entry["sha256"]:
            raise SystemExit(f"{path}: sha256 does not match the record's {entry['sha256']}")
        return data
    return local.read_bytes()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", required=True, help="an E010 run id, e.g. E010-r0010")
    ap.add_argument("--delay", type=int, default=5, help="the match delay byte written into the replay (I3)")
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--suffix", default="2", help="the trace file suffix (never overwrite an earlier trace)")
    a = ap.parse_args(argv)

    record = json.loads((ROOT / "runs" / "E010" / f"{a.record}.json").read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    blob = halftime_sav(entry)
    st0 = savestate.Savestate(blob)
    dly = players.far_pointer(st0, DELAY_PTR)[2] + 0x3F
    before = st0.memory(dly, 1)[0]
    blob = savestate.with_memory(blob, dly, bytes([a.delay]))
    st1 = savestate.Savestate(blob)
    print(f"delay byte at [DS:A923]+0x3F (0x{dly:x}): {before} -> {a.delay} (I3)")

    d = driver.Driver({"cycles": 30000}, workdir=driver.SCRATCH / "e010" / f"replay-{a.record}")
    trace = []
    try:
        SCRATCH_STAGES.mkdir(parents=True, exist_ok=True)
        name = f"{a.record}-halftime-replay"
        (SCRATCH_STAGES / f"{name}.sav").write_bytes(blob)
        meta = {"sha256": driver.sha256(blob), "screen_digest": st1.screen().digest(),
                "game_dir": str(d.game_dir), "drive_layout": d.drive_layout(), "config": {"cycles": 30000}}
        (SCRATCH_STAGES / f"{name}.json").write_text(json.dumps(meta))
        st = driver.StartState(name, SCRATCH_STAGES)
        d.launch(st)
        t0 = time.monotonic()

        def wants_key(sc):
            """match.play's rule exactly (runtime/driver/match.py): the half-time waits."""
            text = sc.text()
            if "location:" in text:
                return "team screen"
            if "hit any key" in sc.lines()[-1] and not any("FULL TIME" in r for r in sc.lines()[1:4]):
                return "hit any key"
            return None

        prev_dg, waiting = None, None
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
                "last": rows[-1].strip()[:40],
            })
            last = trace[-1]
            print(f"read {n}: t={last['t']} 831F={last['m831f']} seed={last['seed']:04x} "
                  f"score={last['score']} ft={last['ft']} key={wants_key(sc) or '-'}", flush=True)
            dump(trace, a.record, a.suffix)
            dg = sc.digest()
            stable = dg == prev_dg
            prev_dg = dg
            if waiting is not None:
                if dg != waiting[0]:
                    waiting = None       # the key was acted on
                elif len(trace) - waiting[1] > KEY_TAKEN_READS:
                    print(f"key not acted on within {KEY_TAKEN_READS} reads; aborting", flush=True)
                    dump(trace, a.record, a.suffix)
                    return 1
            if not stable:
                continue
            if last["ft"]:
                break
            why = wants_key(sc)
            if why:
                d.keys("Enter")
                print(f"  Enter ({why}) at t={last['t']}", flush=True)
                waiting = (dg, len(trace))
    finally:
        d.terminate()
    print(f"{len(trace)} reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
