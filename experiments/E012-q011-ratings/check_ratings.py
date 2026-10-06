#!/usr/bin/env python3
"""Check the ratings predictor (`runtime/model/ratings.py`) against every E012 record.

    python3 experiments/E012-q011-ratings/check_ratings.py

For each `runs/E012/E012-r*.json`: build the predictor from the start squads the record read at
the captain screen, replay the record's commentary line log up to the half-time extent and
compare every squad slot's predicted +0x12 word with the record's half-time read; replay the rest
and compare the full-time read and the man of the match (the word DS:7C3A, CAB0's winner). A
record whose status is not `completed` fails the check. Ends with `match: N/N`."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import ratings as R  # noqa: E402

OUT = ROOT / "runs" / "E012"


def field(obs, needle):
    return next((o["value"] for o in obs if needle in o.get("field", "")), None)


def check(path):
    d = json.loads(Path(path).read_text())
    obs = d["observations"]
    problems = []
    if d["status"] != "completed":
        return [f"{d['run_id']}: status {d['status']!r}"], None
    start = json.loads(field(obs, "captain screen (the match's start)"))
    halftime = json.loads(field(obs, "half-time team-screen stall"))
    fulltime = json.loads(field(obs, "full time (the summary screen)"))
    mom = int(field(obs, "full time: man of the match").split()[0], 16)
    n_half = int(field(obs, "commentary lines seen at the half-time stall"))
    lines = [(t, p1, p2) for _, t, p1, p2, _ in json.loads(field(obs, "commentary line log in ring order"))]
    if len(lines) < n_half:
        return [f"{d['run_id']}: line log shorter than the half-time extent"], None

    r = R.Ratings([s["squad"] for s in start])
    seen_undecided = 0
    r.apply_lines(lines[:n_half])
    for p1, why in r.undecided[seen_undecided:]:
        # a challenge whose outcome (56CB's +10) the log cannot decide: reported separately,
        # never silently matched against a fixed number (T26 rework R1)
        problems.append(f"{d['run_id']}: UNDECIDED challenge, player {p1}: {why}")
    seen_undecided = len(r.undecided)
    pred = r.snapshot()
    for side, (got, want) in enumerate(zip(pred, [s["perf12"] for s in halftime])):
        bad = [f"slot {i + 1}: predicted 0x{p:04x}, read 0x{w:04x}"
               for i, (p, w) in enumerate(zip(got, want)) if p != w]
        if bad:
            problems += [f"{d['run_id']}: half-time side {side} (country {halftime[side]['country']}): " + "; ".join(bad)]
    r.apply_lines(lines[n_half:])
    for p1, why in r.undecided[seen_undecided:]:
        problems.append(f"{d['run_id']}: UNDECIDED challenge, player {p1}: {why}")
    pred = r.snapshot()
    for side, (got, want) in enumerate(zip(pred, [s["perf12"] for s in fulltime])):
        bad = [f"slot {i + 1}: predicted 0x{p:04x}, read 0x{w:04x}"
               for i, (p, w) in enumerate(zip(got, want)) if p != w]
        if bad:
            problems += [f"{d['run_id']}: full-time side {side} (country {fulltime[side]['country']}): " + "; ".join(bad)]
    if r.man_of_the_match() != mom:
        problems.append(f"{d['run_id']}: predicted man of the match {r.man_of_the_match()}, read DS:7C3A = {mom}")
    return problems, {"run": d["run_id"], "lines": len(lines), "first_half": n_half,
                      "subs": sum(1 for t, _, _ in lines if t == R.SUB_TEMPLATE)}


def main():
    records = sorted(OUT.glob("E012-r*.json"))
    if not records:
        print("no E012 records under runs/E012")
        return 1
    n, matched, problems = 0, 0, []
    for p in records:
        probs, info = check(p)
        if info:
            n += 1
            print(f"{info['run']}: {info['lines']} lines ({info['first_half']} in the first half), "
                  f"{info['subs']} substitutions")
            if not probs:
                matched += 1
        for pr in probs:
            print(pr)
        problems += probs
    print(f"match: {matched}/{n}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
