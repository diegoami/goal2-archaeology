#!/usr/bin/env python3
"""E034: the fixture index for the knockout worked example (example.play_knockout, its answers fixed).

    python3 -B experiments/E034-kit-competitive/find_knockout.py --log experiments/E034-kit-competitive/out/<new>.jsonl \
        --indexes 30,31,35

The candidates are the indexes probe-kinds-20261016d.jsonl found level after 90 minutes with every decision played
on: the example answers nothing before extra time, so its 90 minutes are those; its answers from extra time on
change the rest. One line per index: the stages reached and the result. Refuses an existing log."""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image  # noqa: E402
from original_match import example  # noqa: E402

IMAGE = ROOT / ".cache" / "dl" / "e0afff6751747233-e006-1000-r0001.sav"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--indexes", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"{log} exists: never overwritten")
    image = Image.from_savestate(IMAGE.read_bytes())
    with log.open("x") as f:
        for index in [int(x) for x in a.indexes.split(",")]:
            t0 = time.time()
            r = example.play_knockout(image, quiet=True, resume_at=None, index=index)
            rec = {"index": index, "score_90": r["score_90"], "score": r["score"], "extra_time": r["extra_time"],
                   "shootout": r["shootout"] and r["shootout"]["score"], "winner": r["winner"],
                   "substitutions": [[s["team"], s["minute"]] for s in r["substitutions"]],
                   "decisions": [[d["context"], d["minute"]] for d in r["decisions"]], "seconds": round(time.time() - t0, 1)}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(json.dumps(rec))


if __name__ == "__main__":
    main()
