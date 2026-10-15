#!/usr/bin/env python3
"""Print a session's logged steps: number, request, progress bytes, and one row (or a text test) of the
screen after each step, from out/<S>/steps.jsonl and screens.jsonl. No game is run.

    python3 experiments/E031-play-the-game/replay_log.py S [--from N] [--to N] [--row R] [--cols A:B]
"""
import argparse
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--from", dest="first", type=int, default=1)
    ap.add_argument("--to", type=int, default=10 ** 9)
    ap.add_argument("--row", type=int, default=None)
    ap.add_argument("--cols", default="0:80")
    a = ap.parse_args()
    d = OUT / a.session
    screens = {}
    for line in (d / "screens.jsonl").read_text().splitlines():
        s = json.loads(line)
        screens[s["digest"]] = s["text"]
    lo, hi = (int(x) for x in a.cols.split(":"))
    for line in (d / "steps.jsonl").read_text().splitlines():
        st = json.loads(line)
        if not a.first <= st["n"] <= a.to:
            continue
        req = st.get("req", {})
        what = " ".join(req.get("keys", [])) or req.get("text", "") or req.get("cmd", "")
        row = ""
        if a.row is not None and st.get("digest") in screens:
            rows = screens[st["digest"]].split("\n")
            row = rows[a.row][lo:hi] if a.row < len(rows) else ""
        print(f"{st['n']:5d} {st['utc'][11:19]} {req.get('cmd', ''):6s} {what[:30]:30s} {st.get('info') or ''} {row}")


if __name__ == "__main__":
    main()
