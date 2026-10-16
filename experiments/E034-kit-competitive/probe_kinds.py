#!/usr/bin/env python3
"""E034 probe: competitive fixtures through the kit, every decision played on (no answer), one line per match.

    python3 -B experiments/E034-kit-competitive/probe_kinds.py --log experiments/E034-kit-competitive/out/<new>.jsonl \
        --kind 200 --seeds 1-20 [--index 40] [--first 7 --second 19] [--quick]

Records per match: the score at full time of the 90 minutes, whether extra time and a shoot-out came, the final
score, and the first line of any error (the kit stops on what it does not declare). Refuses an existing log."""
import argparse
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, Match, Fixture  # noqa: E402

IMAGE = ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--kind", type=int, default=200)
    ap.add_argument("--seeds", default="1-10")
    ap.add_argument("--index", type=int, default=40)
    ap.add_argument("--first", type=int, default=7)
    ap.add_argument("--second", type=int, default=19)
    ap.add_argument("--quick", action="store_true", help="answer the first decision with quick=True")
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"{log} exists: never overwritten")
    lo, hi = (int(x) for x in a.seeds.split("-"))
    image = Image.from_savestate(IMAGE.read_bytes())
    with log.open("x") as f:
        for seed in range(lo, hi + 1):
            t0 = time.time()
            rec = {"kind": a.kind, "seed": seed, "index": a.index, "first": a.first, "second": a.second,
                   "quick": a.quick}
            kinds, contexts, last = {}, [], None
            try:
                m = Match(image, Fixture(a.first, a.second, index=a.index, kind=a.kind), managed=a.first, seed=seed)
                for ev in m.events():
                    kinds[ev.kind] = kinds.get(ev.kind, 0) + 1
                    last = str(ev)
                    if ev.kind == "full_time" and "score_90" not in rec:
                        rec["score_90"] = list(ev.score)
                    if ev.kind == "decision":
                        contexts.append([ev.data["context"], ev.minute])
                        m.answer(quick=a.quick and len(contexts) == 1)
                r = m.result()
                rec.update(score=r["score"], ok=True)
                for k in ("extra_time", "shootout", "winner", "score_after_90", "score_after_120"):
                    if k in r:
                        rec[k] = r[k]
            except Exception as e:   # noqa: BLE001 - the probe records what stopped the kit
                rec.update(ok=False, error=f"{type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}",
                           where=traceback.format_exc().splitlines()[-3].strip(), last_event=last)
            rec.update(events=kinds, decisions=contexts, seconds=round(time.time() - t0, 1))
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(json.dumps({k: rec.get(k) for k in ("seed", "ok", "score_90", "score", "error", "decisions")}))


if __name__ == "__main__":
    main()
