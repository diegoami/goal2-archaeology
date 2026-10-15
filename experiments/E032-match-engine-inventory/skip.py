#!/usr/bin/env python3
"""E032: which display, sound and delay routines a watched match can do without (the port's boundary).

    python3 -B experiments/E032-match-engine-inventory/skip.py --skip 0791:8E24,0791:9079 --seeds 0x1234,0x2345 --log experiments/E032-match-engine-inventory/out/<new file>.jsonl

Per seed: the timing.py match (E011-r0001's watchstart state, the main seed written, the delay count 20
written at kick-off, both declared), with every routine named in --skip substituted by a hook that does
nothing and returns as the routine's listing says (runtime/emul/watched_match.py `Guest.hook`, not proved:
the point is to drop the routine). One JSON line per match, in timing.py's format plus the skipped
routines and their call counts. compare.py against the timing log of the same seeds says whether the
match (score, ticks, main-seed draws and their digest, the board's statistics, the commentary's template
counts) is unchanged: a routine whose skip leaves every field identical neither draws from the main seed
nor writes anything the match reads, on these seeds."""
import argparse
import collections
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E021-m0-whole-match"))
sys.path.insert(0, str(ROOT / "experiments" / "E032-match-engine-inventory"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
from check import asset, draws_digest  # noqa: E402
from timing import set_delay_at_kickoff, RECORD  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip", required=True)
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    log.parent.mkdir(parents=True, exist_ok=True)
    record = json.loads(RECORD.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    data = asset(entry)
    skips = a.skip.split(",")
    for s in a.seeds.split(","):
        seed = int(s, 0)
        m = WatchedMatch(data)
        m.set_seed(seed)
        set_delay_at_kickoff(m, 20)
        for address in skips:
            m.hook(address, lambda g: None)
        t, c = time.time(), time.process_time()
        error = None
        try:
            m.run(timeout_s=1200)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        wall, cpu = round(time.time() - t, 1), round(time.process_time() - c, 1)
        stats = templates = None
        if not error:
            try:
                stats = m.statistics()
                templates = dict(collections.Counter(r["template"] for r in m.commentary()))
            except Exception as e:      # a skipped drawer can leave the board unreadable
                error = f"outputs: {type(e).__name__}: {e}"
        rec = {"seed": seed, "delay_count": 20, "skipped": skips, "hook_counts": dict(m.hook_counts),
               "error": error, "wall_s": wall, "cpu_s": cpu,
               "score": m.state()["score"], "ticks": len(m.tick_marks), "draws": len(m.draws),
               "draws_digest": draws_digest(m.draws), "strays": list(m.strays),
               "stopped_at_board": m.stopped_at_board, "inputs": m.inputs,
               "statistics_raw": stats, "templates": templates,
               "start_record": "E011-r0001", "watchstart_sha256": entry["sha256"]}
        with open(log, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps({k: rec[k] for k in ("seed", "skipped", "score", "ticks", "draws", "cpu_s", "error")}),
              flush=True)


if __name__ == "__main__":
    main()
