#!/usr/bin/env python3
"""E010 (T24): a slow replay of one record's second half, polled read by read, to find the first
minute and draw where the original and `runtime/model/quick_engine.py` diverge (T24 step 1).

    python3 experiments/E010-q010-quick-engine/replay.py --record E010-r0010 [--delay 5]

The record's published half-time savestate (release E010, sha256-checked) is staged with ONE byte
edited — the match delay byte at [DS:A923]+0x3F, 1 -> `--delay` (5) — and loaded into a fresh
DOSBox-X at the normal cycles (30000). The delay byte is timing, not RNG: the 9382-93BB loop of
`0791:9372` (seg_0791_15.asm) always performs its SIX iterations and `6-delay` only selects which
byte of table DS:0882 each iteration writes (T24 round 1 review R7; notes.md:630-632 — the actual
delay gating is 0425/0441's), and none of it is read by D733 or its callees (F004/F005's
territory). With it raised, one game minute lasts seconds instead of milliseconds, so consecutive
reads (each a savestate; I2) catch the match mid-minute while the emulator still runs at full
speed (a low `cycles` value instead makes the half-time key miss: 0.08 s holds are lost below
~5000 cycles, and a 1 s hold storms the DOS keyboard buffer with repeats that open `0791:ED8A`'s
menu once per minute).

The keys that leave half time are match.play's own (runtime/driver/match.py `wants_key`): one Enter
on the `hit any key` stall, then one Enter on the team screen (`location:`, the default ` play `
option) — the same two keys the original records were made with, so the RNG path is unchanged (the
waits consume no RNG; E010's notes batch 2). A key is never resent and the read counter is never
reset: while the screen awaits a key's acknowledgement (unchanged digest), the probe neither sends
another key nor restarts the KEY_TAKEN_READS budget, and if the screen does not change within
KEY_TAKEN_READS reads the probe aborts with a failure (round 1's resends storm the DOS key buffer
and open `0791:ED8A`'s menu once per minute; T24 round 1 review R4). Every read records DS:831F
(the minute), DS:831B, the seed DS:7B62, the score DS:9B3C/9B3D and the substitution budgets
DS:9B3A into `trace-<record>-replay<suffix>.json` here (an addition; the ten records are never
touched, and no earlier trace is ever overwritten: the probe refuses a trace path that exists
before launch — round 1 review R3). A run that times out without reaching full time fails (exit 1).
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


def trace_path(record, suffix):
    return OUT / f"trace-{record.lower()}-replay{suffix}.json"


class TraceWriter:
    """The probe's incremental trace dump. The constructor REFUSES a path that exists:
    a committed trace is measured evidence and is never overwritten (L207; round 1's
    review R3 — the round-1 default suffix "2" selected the already committed
    trace-e010-r0010-replay2.json, so the refusal must fire before the game launches).
    tests/test_model_replay_guards.py visits this edge (rule 10)."""

    def __init__(self, path):
        if path.exists():
            raise SystemExit(f"{path}: exists already — a trace is never overwritten; "
                             "pass a fresh --suffix")
        self.path = path

    def dump(self, trace):
        self.path.write_text(json.dumps(trace) + "\n")


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


def wants_key(sc):
    """match.play's rule exactly (runtime/driver/match.py): the half-time waits."""
    text = sc.text()
    if "location:" in text:
        return "team screen"
    if "hit any key" in sc.lines()[-1] and not any("FULL TIME" in r for r in sc.lines()[1:4]):
        return "hit any key"
    return None


def poll(d, a, writer, t0):
    """The read loop: returns 0 only at full time. An unchanged screen while a key is
    pending never resends and never resets the counter (R4), the KEY_TAKEN_READS abort
    returns 1, and a timeout without full time also returns 1 (R4).
    tests/test_model_replay_guards.py visits these edges (rule 10)."""
    trace = []
    prev_dg, waiting, grab_hits = None, None, 0
    while time.monotonic() - t0 < a.timeout:
        times, state, data = d.read()
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
        writer.dump(trace)
        if a.grab_seed and last["seed"] == int(a.grab_seed, 16):
            grab_hits += 1
            if grab_hits == 2:      # a stable read at the seed: a pause, not a mid-step pass
                gname = f"{a.record}-goalpause"
                (SCRATCH_STAGES / f"{gname}.sav").write_bytes(data)
                gmeta = {"sha256": driver.sha256(data), "screen_digest": sc.digest(),
                         "game_dir": str(d.game_dir), "drive_layout": d.drive_layout(),
                         "config": {"cycles": a.cycles}}
                (SCRATCH_STAGES / f"{gname}.json").write_text(json.dumps(gmeta))
                print(f"  goal-pause state staged as {gname} "
                      f"(sha256 {gmeta['sha256'][:16]})", flush=True)
        else:
            grab_hits = 0
        dg = sc.digest()
        stable = dg == prev_dg
        prev_dg = dg
        if waiting is not None:
            if dg != waiting[0]:
                waiting = None       # the key was acted on
            elif len(trace) - waiting[1] > KEY_TAKEN_READS:
                print(f"key not acted on within {KEY_TAKEN_READS} reads; aborting", flush=True)
                return 1
            else:
                # awaiting acknowledgement with an UNCHANGED screen: do not resend (the
                # resend storms the DOS key buffer and opens 0791:ED8A's menu) and do not
                # reset waiting's read counter — the abort above must stay armed (R4)
                continue
        if not stable:
            continue
        if last["ft"]:
            break
        why = wants_key(sc)
        if why:
            d.keys("Enter")
            print(f"  Enter ({why}) at t={last['t']}", flush=True)
            waiting = (dg, len(trace))
    if not trace or not trace[-1]["ft"]:
        # the timeout expired without full time: a failure, not a success (R4)
        print("timeout without full time; failing", flush=True)
        return 1
    print(f"{len(trace)} reads")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--record", required=True, help="an E010 run id, e.g. E010-r0010")
    ap.add_argument("--delay", type=int, default=5, help="the match delay byte written into the replay (I3)")
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--suffix", default="2", help="the trace file suffix (never overwrite an earlier trace)")
    ap.add_argument("--cycles", type=int, default=30000,
                    help="DOSBox-X cycles: 30000 for the keyed half-time phase, low to slow the run")
    ap.add_argument("--state", default=None,
                    help="launch from this staged savestate name (scratch/e010/states/) instead of "
                         "the record's half time (no delay edit: the staged blob keeps its own)")
    ap.add_argument("--grab-seed", default=None,
                    help="write the savestate of the SECOND consecutive read whose DS:7B62 equals "
                         "this hex seed to scratch/e010/states/<record>-goalpause.sav and go on")
    a = ap.parse_args(argv)
    # R3: refuse the trace path BEFORE anything is launched or staged — an existing file
    # is committed evidence and is never overwritten
    writer = TraceWriter(trace_path(a.record, a.suffix))
    d = driver.Driver({"cycles": a.cycles}, workdir=driver.SCRATCH / "e010" / f"replay-{a.record}")
    try:
        SCRATCH_STAGES.mkdir(parents=True, exist_ok=True)
        if a.state:
            name = a.state          # already staged (e.g. the goal pause of an earlier replay)
        else:
            record = json.loads((ROOT / "runs" / "E010" / f"{a.record}.json").read_text())
            entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
            blob = halftime_sav(entry)
            st0 = savestate.Savestate(blob)
            dly = players.far_pointer(st0, DELAY_PTR)[2] + 0x3F
            before = st0.memory(dly, 1)[0]
            blob = savestate.with_memory(blob, dly, bytes([a.delay]))
            st1 = savestate.Savestate(blob)
            print(f"delay byte at [DS:A923]+0x3F (0x{dly:x}): {before} -> {a.delay} (I3)")
            name = f"{a.record}-halftime-replay"
            (SCRATCH_STAGES / f"{name}.sav").write_bytes(blob)
            meta = {"sha256": driver.sha256(blob), "screen_digest": st1.screen().digest(),
                    "game_dir": str(d.game_dir), "drive_layout": d.drive_layout(),
                    "config": {"cycles": a.cycles}}
            (SCRATCH_STAGES / f"{name}.json").write_text(json.dumps(meta))
        st = driver.StartState(name, SCRATCH_STAGES)
        d.launch(st)
        return poll(d, a, writer, time.monotonic())
    finally:
        d.terminate()


if __name__ == "__main__":
    sys.exit(main())
