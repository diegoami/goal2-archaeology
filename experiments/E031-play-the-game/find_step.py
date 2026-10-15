#!/usr/bin/env python3
"""List the logged steps of a session whose screen holds a text (or whose request holds it, --req).
No game is run. Usage: find_step.py S "text" [--req] [--max 10] [--from N]"""
import argparse
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "out"


def load(session):
    d = OUT / session
    screens = {}
    for line in (d / "screens.jsonl").read_text().splitlines():
        s = json.loads(line)
        screens[s["digest"]] = s["text"]
    steps = [json.loads(line) for line in (d / "steps.jsonl").read_text().splitlines()]
    return steps, screens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("text")
    ap.add_argument("--req", action="store_true")
    ap.add_argument("--max", type=int, default=10)
    ap.add_argument("--from", dest="first", type=int, default=0)
    a = ap.parse_args()
    steps, screens = load(a.session)
    n = 0
    for st in steps:
        if st["n"] < a.first:
            continue
        hay = json.dumps(st.get("req"), ensure_ascii=False) if a.req else screens.get(st.get("digest"), "")
        if a.text in hay:
            line = next((r for r in hay.split("\n") if a.text in r), "")
            print(f"{st['n']} {st['utc'][:19]} {json.dumps(st.get('req'), ensure_ascii=False)[:80]} | {line.strip()[:90]}")
            n += 1
            if n >= a.max:
                break


if __name__ == "__main__":
    main()
