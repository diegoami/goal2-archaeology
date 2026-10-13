#!/usr/bin/env python3
"""Summarise probe.py --seeds logs (watched E011-r0001 start state under seeds) into out/seeds-summary-<UTC>.log.

    python3 experiments/E027-discipline-rules/summarise_seeds.py out/probe-seeds-<stamp>.log [more]

Per seed: 8206 (fouls), 7EEF, 798D, 7B77, 7D56, 8062, C88D entries, the end statistics (DS:7B7E + side*10 + k, k = 7 bookings,
8 sendings off, 9 injuries), the whistles (DS:831F, DS:8321) and DS:831F at the end. Checks: DS:7B84 sum == 8206 entries;
the full-time DS:831F == 91 + min(5, events); the half-time whistle DS:831F is 46 whatever the first half's events.
"""
import ast
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

HERE = Path(__file__).resolve().parent
seeds = []
for path in sys.argv[1:]:
    cur = None
    for line in Path(path).read_text().splitlines():
        m = re.match(r"=== E011-r\d+ seed (\d+)", line)
        if m:
            cur = {"seed": int(m.group(1)), "entered": {}, "stats": {}}
            seeds.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"\s+0791:([0-9A-F]+) entered (\d+)", line)
        if m:
            cur["entered"][m.group(1)] = int(m.group(2))
        m = re.match(r"  stats side (\d) .*?: (\[.*\])", line)
        if m:
            cur["stats"][int(m.group(1))] = ast.literal_eval(m.group(2))
        if line.startswith("whistles"):
            cur["whistles"] = ast.literal_eval(line.split(": ", 1)[1])
        m = re.match(r"run: ticks (\d+), score .*831F (\d+)", line)
        if m:
            cur["831F"] = int(m.group(2))
done = [s for s in seeds if len(s["stats"]) == 2]
out = []


def say(s):
    print(s)
    out.append(s)


say(f"{len(done)} complete watched matches of E011-r0001's start state, seeds {[s['seed'] for s in done]}")
bad = []
for s in done:
    ev = sum(s["stats"][i][k] for i in (0, 1) for k in (7, 8, 9))
    fouls = sum(s["stats"][i][6] for i in (0, 1))
    if fouls != s["entered"].get("8206", 0) or s["831F"] != 91 + min(5, ev):
        bad.append((s["seed"], fouls, s["entered"].get("8206"), s["831F"], ev))
    s["ev"] = ev
    s["fouls"] = fouls
say(f"checks: Fouls count == 8206 entries and DS:831F == 91 + min(5, events) in {len(done) - len(bad)} of {len(done)}; others {bad}")
for key, name in (("8206", "fouls (8206)"), ("7EEF", "7EEF"), ("8062", "8062 asks"), ("C88D", "C88D"), ("798D", "798D"), ("7B77", "7B77"), ("7D56", "7D56")):
    v = [s["entered"].get(key, 0) for s in done]
    say(f"  {name}: total {sum(v)}, mean per match {mean(v):.2f}" + (f" (sd {stdev(v):.2f}, se {stdev(v)/len(v)**0.5:.2f})" if len(v) > 1 else "") + f"; values {v}")
for k, name in ((7, "bookings"), (8, "sendings off"), (9, "injuries")):
    v = [s["stats"][0][k] + s["stats"][1][k] for s in done]
    say(f"  {name}: total {sum(v)}, mean per match {mean(v):.2f}" + (f" (se {stdev(v)/len(v)**0.5:.2f})" if len(v) > 1 else "") + f"; values {v}")
ht = [(s["seed"], w[1], w[3]) for s in done for w in s.get("whistles", []) if w[0] == "half time"]
say(f"half-time whistles (seed, DS:831F, DS:8321): {ht}")
side_max = max(max(s["stats"][i][8] + s["stats"][i][9] for i in (0, 1)) for s in done)
say(f"largest (sendings off + injuries) of one side in a match: {side_max}")
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
(HERE / "out" / f"seeds-summary-{stamp}.log").write_text("\n".join(out) + "\n")
