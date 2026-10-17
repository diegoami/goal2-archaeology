#!/usr/bin/env python3
"""Measure the repository's CI usage from the GitHub Actions API (issue #297).

    python3 tools/ci_minutes.py [--days 30] [--repo OWNER/NAME] [--steps RUN_ID]

Prints, for the runs created in the last N days: run counts by event and conclusion, job counts and
billed-style minutes (each job's wall time rounded up to the minute, as GitHub bills it) by job name,
the runs per PR, and the distribution of job durations.  With --steps it prints one run's step
timings instead.  Needs the `gh` CLI, logged in.
"""
import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from datetime import datetime, timedelta, timezone


def gh_json(path):
    out = subprocess.run(["gh", "api", "--paginate", path], check=True, capture_output=True, text=True).stdout
    # --paginate concatenates one JSON document per page
    dec, i, docs = json.JSONDecoder(), 0, []
    out = out.strip()
    while i < len(out):
        d, j = dec.raw_decode(out, i)
        docs.append(d)
        i = j
        while i < len(out) and out[i].isspace():
            i += 1
    return docs


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def secs(a, b):
    return (ts(b) - ts(a)).total_seconds() if a and b else 0.0


def runs_since(repo, days):
    """The API returns at most 1000 runs per query, so ask in one-day windows."""
    today = datetime.now(timezone.utc).date()
    runs = {}
    for k in range(days + 1):
        d0 = today - timedelta(days=k)
        d1 = d0 + timedelta(days=1)
        for d in gh_json(f"repos/{repo}/actions/runs?per_page=100&created={d0}..{d1}"):
            for r in d["workflow_runs"]:
                if ts(r["created_at"]).date() == d0:
                    runs[r["id"]] = r
    return list(runs.values())


def jobs_of(repo, run_id):
    jobs = []
    for d in gh_json(f"repos/{repo}/actions/runs/{run_id}/jobs?per_page=100"):
        jobs += d["jobs"]
    return jobs


def steps_report(repo, run_id):
    for j in jobs_of(repo, run_id):
        print(f"{j['name']}: {j['conclusion']} {secs(j['started_at'], j['completed_at']):.0f}s")
        for s in j["steps"]:
            print(f"  {secs(s['started_at'], s['completed_at']):6.0f}s  {s['name']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--repo", default="diegoami/goal2-archaeology")
    ap.add_argument("--steps", type=int, metavar="RUN_ID")
    ap.add_argument("--json", metavar="FILE", help="also write the raw per-job rows here")
    a = ap.parse_args()
    if a.steps:
        steps_report(a.repo, a.steps)
        return
    runs = runs_since(a.repo, a.days)
    by_event = defaultdict(lambda: defaultdict(int))
    for r in runs:
        by_event[r["event"]][r["conclusion"] or r["status"]] += 1
    print(f"runs created in the last {a.days} days: {len(runs)}")
    for ev, c in sorted(by_event.items()):
        print(f"  {ev}: {sum(c.values())}  " + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    rows = []
    per_pr = defaultdict(int)
    with ThreadPoolExecutor(8) as ex:
        all_jobs = list(ex.map(lambda r: jobs_of(a.repo, r["id"]), runs))
    for r, jobs in zip(runs, all_jobs):
        if r["event"] == "pull_request" and any(j["conclusion"] != "skipped" for j in jobs):
            per_pr[r["head_branch"]] += 1
        for j in jobs:
            if j["conclusion"] in (None, "skipped", "cancelled") and not j["completed_at"]:
                continue
            rows.append({"run": r["id"], "event": r["event"], "branch": r["head_branch"], "job": j["name"],
                         "conclusion": j["conclusion"], "secs": secs(j["started_at"], j["completed_at"]),
                         "created": r["created_at"]})
    tot = defaultdict(lambda: [0, 0, 0.0])
    for x in rows:
        if x["conclusion"] == "skipped":
            continue
        t = tot[(x["event"], x["job"])]
        t[0] += 1
        t[1] += -(-int(x["secs"]) // 60)  # billed: rounded up to the minute
        t[2] += x["secs"]
    print("\njobs that ran (skipped excluded): event / job: count, billed minutes, wall minutes, mean seconds")
    all_billed = 0
    for (ev, job), (n, billed, wall) in sorted(tot.items()):
        all_billed += billed
        print(f"  {ev:13s} {job:8s} n={n:3d} billed={billed:4d} min wall={wall / 60:6.1f} min mean={wall / n:5.0f}s")
    print(f"  TOTAL billed minutes: {all_billed}")
    print(f"\nPR branches with a run that did work: {len(per_pr)}; such runs per branch (mean {sum(per_pr.values()) / max(1, len(per_pr)):.1f}, "
          f"max {max(per_pr.values(), default=0)})")
    wk = defaultdict(lambda: [0, 0])
    for x in rows:
        if x["conclusion"] != "skipped":
            w = wk[ts(x["created"]).strftime("%Y-%m-%d")[:10]]
            w[0] += 1
            w[1] += -(-int(x["secs"]) // 60)
    print("\nbilled minutes by day (jobs, minutes):")
    for day, (n, m) in sorted(wk.items()):
        print(f"  {day} {n:4d} {m:5d}")
    if a.json:
        with open(a.json, "w") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    sys.exit(main())
