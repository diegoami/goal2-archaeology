#!/usr/bin/env python3
"""E033: the watchstart image differs from E006-r0005 in the computer side's squad order and one player's position
(its own run_match had run the set-up: 0791:BC5D sorts the computer squad and writes its eleven's positions from
R011, F010). Put E006-r0005's country-19 record and its players' records into the watchstart image: if the
engine check then holds, the match depends on the image through the teams' records only (as the original carries
them from fixture to fixture), not on the stack, the screens or the rest of the data segment.

    python3 -B experiments/E033-original-match-kit/team_state.py --log experiments/E033-original-match-kit/out/<new>.jsonl"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E033-original-match-kit"))
from image_dependence import load, play, R5, WS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    r5, ws = load(R5), load(WS)
    out = open(log, "x")
    for label, countries in (("country 19's record and players from E006-r0005", (19,)),
                             ("country 7's record and players from E006-r0005", (7,)),
                             ("both teams' records and players from E006-r0005", (7, 19))):
        img = load(WS)
        pbase, cbase = img.far(0xA91B), img.far(0xA917)
        moved = []
        for c in countries:
            img.memory[cbase + 0xBF * c:cbase + 0xBF * (c + 1)] = r5.memory[cbase + 0xBF * c:cbase + 0xBF * (c + 1)]
            for w in set(r5.squad(c)) | set(load(WS).squad(c)):
                img.memory[pbase + 20 * w:pbase + 20 * (w + 1)] = r5.memory[pbase + 20 * w:pbase + 20 * (w + 1)]
                moved.append(w)
        rec = {"run": "watchstart with " + label, "players_moved": len(moved), **play(img)}
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print(json.dumps(rec), flush=True)


if __name__ == "__main__":
    main()
