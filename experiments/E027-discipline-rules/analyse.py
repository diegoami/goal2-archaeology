#!/usr/bin/env python3
"""Summarise the quick-second-half logs of E027 (written by quick_second_half.py) into a new analysis log.

    python3 experiments/E027-discipline-rules/analyse.py out/quick-second-half-<stamp>.log [more logs]

Per seed line it reads the D5C1 / 7EEF / 7D56 / 798D / 7B77 / 7A43 / C88D counts, the match statistics of both sides
(DS:7B7E + side*10 + k: k = 7 bookings, 8 sendings off, 9 injuries), DS:9B3A, DS:8321 and DS:831F at the half's end. It prints
  - the totals and the per-half means with their standard errors;
  - the cap check: the largest (sendings off + injuries) of any side in any half (7A43 allows a loss while the sum is < 3, so 3);
  - the added-time check: DS:831F at the end against 91 + min(5, bookings + sendings off + injuries of both sides) per seed
    (the first half of the savestate is a friendly with none of these events);
  - the substitution count: DS:9B3A before (2) and after, per seed.
Seeds whose line is missing a field stop the script.
"""
import ast
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

HERE = Path(__file__).resolve().parent


def parse(path):
    for line in Path(path).read_text().splitlines():
        if not line.startswith("seed "):
            continue
        d = {"seed": int(re.match(r"seed (\d+)", line).group(1))}
        d["counts"] = ast.literal_eval(re.search(r"counts (\{.*?\}) stats", line).group(1))
        d["s0"] = ast.literal_eval(re.search(r"stats\(side0\) (\[.*?\])", line).group(1))
        d["s1"] = ast.literal_eval(re.search(r"stats\(side1\) (\[.*?\])", line).group(1))
        d["9B3A"] = ast.literal_eval(re.search(r"9B3A (\(.*?\))", line).group(1))
        d["8321"] = int(re.search(r"8321 (\d+)", line).group(1))
        d["831F"] = int(re.search(r"831F (\d+)", line).group(1))
        yield d


def main():
    paths = sys.argv[1:]
    out = []

    def say(s=""):
        print(s)
        out.append(s)

    rows = []
    for p in paths:
        rows.extend(parse(p))
    n = len(rows)
    say(f"analysis of {n} second halves from {paths}")
    if not n:
        raise SystemExit("no seed lines")

    def c(r, k):
        return r["counts"].get(k, 0)

    for k in ("D5C1", "7EEF", "798D", "7B77", "7D56", "7A43", "C88D", "C5DC", "8062"):
        v = [c(r, k) for r in rows]
        say(f"  {k}: total {sum(v)}, mean per half {mean(v):.3f}" + (f" (sd {stdev(v):.3f}, se {stdev(v)/n**0.5:.3f})" if n > 1 else ""))
    for name, k in (("bookings", 7), ("sendings off", 8), ("injuries", 9)):
        v = [r["s0"][k] + r["s1"][k] for r in rows]
        say(f"  {name} (both sides): total {sum(v)}, mean per half {mean(v):.3f}"
            + (f" (sd {stdev(v):.3f}, se {stdev(v)/n**0.5:.3f})" if n > 1 else "") + f"; histogram {[v.count(i) for i in range(max(v) + 1)]}")
    # per D5C1 entry
    d5 = sum(c(r, "D5C1") for r in rows)
    e7 = sum(c(r, "7EEF") for r in rows)
    say(f"  7EEF entries per D5C1 entry: {e7}/{d5} = {e7/d5:.4f}")
    b = sum(r["s0"][7] + r["s1"][7] for r in rows)
    so = sum(r["s0"][8] + r["s1"][8] for r in rows)
    inj = sum(r["s0"][9] + r["s1"][9] for r in rows)
    say(f"  per 7EEF entry: bookings {b}/{e7} = {b/e7:.4f}, sendings off {so}/{e7} = {so/e7:.4f}, injuries {inj}/{e7} = {inj/e7:.4f}")
    # cap
    worst = max(max(r["s0"][8] + r["s0"][9], r["s1"][8] + r["s1"][9]) for r in rows)
    over = [r["seed"] for r in rows if max(r["s0"][8] + r["s0"][9], r["s1"][8] + r["s1"][9]) > 3]
    say(f"cap: the largest (sendings off + injuries) of one side in one half is {worst}; halves above 3: {over}")
    asked = sum(c(r, "7A43") for r in rows)
    taken = sum(r["s0"][8] + r["s0"][9] + r["s1"][8] + r["s1"][9] for r in rows)
    say(f"  7A43 asked {asked} times; sendings off + injuries that happened: {taken}; refused: {asked - taken}")
    # added time
    bad = []
    for r in rows:
        ev = sum(r[s][k] for s in ("s0", "s1") for k in (7, 8, 9))
        if r["831F"] != 91 + min(5, ev):
            bad.append((r["seed"], r["831F"], ev))
    say(f"added time: DS:831F at the end equals 91 + min(5, events) in {n - len(bad)} of {n} halves; others (seed, 831F, events): {bad}")
    say("events histogram -> 831F: " + str(sorted({(sum(r[s][k] for s in ('s0', 's1') for k in (7, 8, 9)), r['831F']) for r in rows})))
    # substitutions
    subs = {}
    for r in rows:
        key = (2 - r["9B3A"][0], 2 - r["9B3A"][1])
        subs[key] = subs.get(key, 0) + 1
    say(f"substitutions made (side 0, side 1) -> halves: {dict(sorted(subs.items()))}; C88D with the budget 2 never exceeds it: "
        f"{all(min(r['9B3A']) >= 0 for r in rows)}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    (HERE / "out" / f"analysis-{stamp}.log").write_text("\n".join(out) + "\n")
    print("log:", HERE / "out" / f"analysis-{stamp}.log")


if __name__ == "__main__":
    main()
