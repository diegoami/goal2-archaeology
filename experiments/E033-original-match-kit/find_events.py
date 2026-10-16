#!/usr/bin/env python3
"""E033: find seeds whose match has the rare events (a sending off, an injury) for the stamp check, with Denmark's
tactic element 4 set ("go in hard": more fouls, F026). One JSON line per seed tried; stops after the first seed with
a sending off (or at --last).

    python3 -B experiments/E033-original-match-kit/find_events.py --first 1 --last 60 --log experiments/E033-original-match-kit/out/<new>.jsonl"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, Match, Fixture  # noqa: E402

IMAGE = ("e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d", "e006-1000-r0001.sav")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first", type=int, default=1)
    ap.add_argument("--last", type=int, default=60)
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    data = (ROOT / ".cache/dl" / f"{IMAGE[0][:16]}-{IMAGE[1]}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == IMAGE[0]
    img = Image.from_savestate(data)
    countries = img.countries()
    rec = bytearray(countries[7])
    rec[0x2D] |= 1 << 3
    countries[7] = bytes(rec)
    with open(log, "x") as out:
        for seed in range(a.first, a.last + 1):
            t = time.time()
            m = Match(img, Fixture(7, 19, index=21), managed=7, seed=seed, countries=countries)
            kinds = {}
            for ev in m.events():
                kinds[ev.kind] = kinds.get(ev.kind, 0) + 1
                if ev.kind == "decision":
                    m.answer()
            row = {"seed": seed, "go_in_hard": True, "counts": {k: kinds.get(k, 0) for k in
                   ("booking", "sending_off", "injury", "goal", "goal_disallowed", "substitution")},
                   "wall_s": round(time.time() - t, 1)}
            out.write(json.dumps(row) + "\n")
            out.flush()
            print(json.dumps(row), flush=True)
            if kinds.get("sending_off"):
                break


if __name__ == "__main__":
    main()
