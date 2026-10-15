#!/usr/bin/env python3
"""Print the logged screen after step N of a session (or the screen of a digest prefix), from
out/<S>/steps.jsonl and screens.jsonl. No game is run. Usage: screen.py S N|digest-prefix"""
import json
import sys
from pathlib import Path

d = Path(__file__).resolve().parent / "out" / sys.argv[1]
key = sys.argv[2]
screens = {}
for line in (d / "screens.jsonl").read_text().splitlines():
    s = json.loads(line)
    screens[s["digest"]] = s["text"]
digest = None
if key.isdigit():
    for line in (d / "steps.jsonl").read_text().splitlines():
        st = json.loads(line)
        if st["n"] == int(key):
            digest = st.get("digest")
            print(f"step {st['n']} {st['utc']} {st.get('req')} info={st.get('info')}")
else:
    digest = next((k for k in screens if k.startswith(key)), None)
print(screens.get(digest, f"no screen for {key}"))
