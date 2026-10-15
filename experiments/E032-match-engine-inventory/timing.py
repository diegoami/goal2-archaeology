#!/usr/bin/env python3
"""E032: the cost of one whole watched match of the original in the E021 harness, and whether the delay
calibration changes it.

    python3 -B experiments/E032-match-engine-inventory/timing.py --seeds 0x1234,0x2345 [--delay-count N] --log experiments/E032-match-engine-inventory/out/<new file>.jsonl

Per seed: E011-r0001's watchstart state (sha256 verified), the main seed DS:7B62 written (declared), and
with --delay-count N the delay calibration dword DS:A9FF/AA01 := N (declared; F006: delays only count passes
against it), written at the first clock tick (set_delay_at_kickoff); use N >= 10: the whistle 214B:1F87
divides by N div 10 (read from the listing). No hook and no observer beyond the harness's own. One JSON line
per match, appended to a log
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


def set_delay_at_kickoff(m, n):
    """Write the delay calibration dword DS:A9FF/AA01 := n at the first clock tick (0791:970C entry), a
    declared input recorded in m.inputs. Not at the start: the watchstart state resumes INSIDE a delay
    (214B:1E09) whose pass counter is already above a small n, so a write there never lets it end."""
    from unicorn import UC_HOOK_CODE
    done = []

    def at_tick(uc, address, size, data):
        if done:
            return
        lin = m.DS * 16 + 0xA9FF
        old = m.mem(lin, 4)
        uc.mem_write(lin, n.to_bytes(4, "little"))
        m.inputs.append({"what": "delay calibration dword DS:A9FF/AA01, at the first 0791:970C entry",
                         "linear": lin, "old": old.hex(), "new": n.to_bytes(4, "little").hex()})
        done.append(1)

    m.mu.hook_add(UC_HOOK_CODE, at_tick, begin=m.lin("0791:970C"), end=m.lin("0791:970C"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", required=True)
    ap.add_argument("--delay-count", type=lambda v: int(v, 0), default=None,
                    help="write the delay calibration dword DS:A9FF/AA01 := N at the first clock tick (declared); use N >= 10: the whistle 214B:1F87 divides by N div 10 (listing)")
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
        if a.delay_count is not None:
            set_delay_at_kickoff(m, a.delay_count)
        t, c = time.time(), time.process_time()
        error = None
        try:
            m.run(timeout_s=3600)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
        wall, cpu = round(time.time() - t, 1), round(time.process_time() - c, 1)
        rec = {"seed": seed, "delay_count": a.delay_count, "error": error, "wall_s": wall, "cpu_s": cpu,
               "score": m.state()["score"], "ticks": len(m.tick_marks), "draws": len(m.draws),
               "draws_digest": draws_digest(m.draws), "strays": list(m.strays),
               "stopped_at_board": m.stopped_at_board, "inputs": m.inputs,
               "statistics_raw": m.statistics() if not error else None,
               "templates": dict(collections.Counter(r["template"] for r in m.commentary())) if not error else None,
               "start_record": "E011-r0001", "watchstart_sha256": entry["sha256"]}
        with open(log, "a") as f:
            f.write(json.dumps(rec) + "\n")
        print(json.dumps({k: rec[k] for k in ("seed", "delay_count", "score", "ticks", "draws", "wall_s", "cpu_s", "error")}),
              flush=True)


if __name__ == "__main__":
    main()
