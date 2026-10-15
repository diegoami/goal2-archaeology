#!/usr/bin/env python3
"""E032: the cost of one whole watched match of the original in the E021 harness, and whether the delay
calibration changes it.

    python3 -B experiments/E032-match-engine-inventory/timing.py --seeds 0x1234,0x2345 [--fast-delay] --log experiments/E032-match-engine-inventory/out/<new file>.jsonl

Per seed: E011-r0001's watchstart state (sha256 verified), the main seed DS:7B62 written (declared), and
with --fast-delay the delay calibration dword DS:A9FF/AA01 := 1 (declared; F006: delays only count passes
against it). No hook and no observer beyond the harness's own. One JSON line per match, appended to a log
that must not exist: score, ticks, draws, the draws digest, the full-time board's raw statistics, the
commentary's template counts, wall and CPU seconds."""
import argparse
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E021-m0-whole-match"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
from check import asset, draws_digest  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402

RECORD = ROOT / "runs/E011/E011-r0001.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--fast-delay", action="store_true")
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    log.parent.mkdir(parents=True, exist_ok=True)
    record = json.loads(RECORD.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    data = asset(entry)
    for s in a.seeds.split(","):
        seed = int(s, 0)
        m = WatchedMatch(data)
        m.set_seed(seed)
        if a.fast_delay:
            m.write_input("delay calibration dword DS:A9FF/AA01", m.DS * 16 + 0xA9FF, (1).to_bytes(4, "little"))
        t, c = time.time(), time.process_time()
        error = None
        try:
            m.run(timeout_s=3600)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        wall, cpu = round(time.time() - t, 1), round(time.process_time() - c, 1)
        rec = {"seed": seed, "fast_delay": a.fast_delay, "error": error, "wall_s": wall, "cpu_s": cpu,
               "score": m.state()["score"], "ticks": len(m.tick_marks), "draws": len(m.draws),
               "draws_digest": draws_digest(m.draws), "strays": list(m.strays),
               "stopped_at_board": m.stopped_at_board, "inputs": m.inputs,
               "statistics_raw": m.statistics() if not error else None,
               "templates": dict(collections.Counter(r["template"] for r in m.commentary())) if not error else None,
               "start_record": "E011-r0001", "watchstart_sha256": entry["sha256"]}
        with open(log, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps({k: rec[k] for k in ("seed", "fast_delay", "score", "ticks", "draws", "wall_s", "cpu_s", "error")}),
              flush=True)


if __name__ == "__main__":
    main()
