#!/usr/bin/env python3
"""E026 (T52): one arm of the tactics-effect measurement, on the E021 whole-match harness.

    python3 -B experiments/E026-tactics-effect/arm.py --arm e1 --first 0 --count 20 --log experiments/E026-tactics-effect/out/<file>.jsonl

An arm is a name in ARMS: the tactic byte (+0x2D) of the country playing on engine side 0 is set
to its start-state value XOR the arm's mask (Denmark's 0x8B in E011-r0001; the mask flips one
element, bit k-1 = element k, F010). Match i of the family uses the main seed SEEDS[i] (DS:7B62,
F004) written into the start state; the arms use the SAME seed list, so match i of two arms
differs only by the tactic byte. The start state is E011-r0001's watchstart state (Denmark 7 vs
country 19; the kick-off side was drawn before the state, so it is the same in every match).
One JSON line per match is appended (never rewritten) to --log, which must not exist; each line
carries what the analysis reads plus the declared writes and the draw trace's digest, so a re-run
is comparable line by line."""
import argparse
import json
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E021-m0-whole-match"))
from check import asset, draws_digest, emulate  # noqa: E402

START_RECORD = "E011-r0001"
SIDE = 0
# one element flipped per arm; "base" flips nothing.  element k = bit k-1.
ARMS = {"base": 0x00, **{f"e{k}": 1 << (k - 1) for k in range(1, 9)}}
# 16-bit seeds, a fixed family: draws of random.Random(52026), no repeats.
_rng = random.Random(52026)
SEEDS = []
while len(SEEDS) < 2000:
    s = _rng.randrange(1, 0x10000)
    if s not in SEEDS:
        SEEDS.append(s)


def one(data, arm, seed):
    mask = ARMS[arm]

    def write(m):
        country = m.sides()[SIDE]
        old = m.mem(m.country_lin(country) + 0x2D, 1)[0]
        m.set_seed(seed)
        if mask:
            m.set_country_tactics(country, old ^ mask)

    m, err, secs = emulate(data, "none", inputs=[write])
    rec = {"arm": arm, "mask": mask, "seed": seed, "error": err, "seconds": secs,
           "stopped_at_board": m.stopped_at_board, "strays": list(m.strays)}
    if m.stopped_at_board and not err:
        o = m.outputs()
        st = {}
        for r in o["statistics_raw"]:
            st[r["row_label"]] = r.get("raw_bytes") or r.get("raw_words")
        rec.update({"score": o["score"], "clock": [o["final"]["831F"], o["final"]["831D"]],
                    "stats": st, "sides": o["sides_9B34"],
                    "scorers": [[(x["name"], x["minute_byte_raw"]) for x in side] for side in o["scorers"]],
                    "man_of_the_match": o["man_of_the_match"], "commentary_calls": o["commentary_writer_calls_1D4A"],
                    "board_sha256": o["board_screen_sha256"], "draws_count": len(m.draws),
                    "draws_sha256": draws_digest(m.draws), "inputs": o["inputs"]})
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arm", choices=sorted(ARMS), required=True)
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args(argv)
    log = Path(a.log)
    if log.exists():
        raise SystemExit(f"{log} exists: measured outputs are never overwritten")
    log.parent.mkdir(parents=True, exist_ok=True)
    record = json.loads((ROOT / "runs/E011" / f"{START_RECORD}.json").read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    data = asset(entry)
    for i in range(a.first, a.first + a.count):
        c0 = time.process_time()
        rec = one(data, a.arm, SEEDS[i])
        rec["i"] = i
        rec["cpu_seconds"] = round(time.process_time() - c0, 1)    # added after the first 5 matches (probe, base, e5)
        with log.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"{a.arm} i={i} seed={SEEDS[i]:#06x} score={rec.get('score')} {rec['seconds']}s err={rec['error']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
