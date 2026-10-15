#!/usr/bin/env python3
"""Issue #141 (Sol's R2 on PR 240): every number PR 240 states, recounted from the committed logs.

  python3 experiments/E015-human-playthrough/count_141.py \
      --out experiments/E015-human-playthrough/fix-141-counts-01.log
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRANCH_RUNS = {"38776112306", "38769381289"}   # this branch's runs in the history log


def rows(name):
    out = []
    for line in (HERE / name).read_text().splitlines():
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass   # the CI extracts also caught repro_141's printed summary dict
                # ({'pass': 6}), which the JSON summary line beside it repeats
    return out


def runs(name):
    """(label of the batch, run rows) per batch in a repro log."""
    batches, label = [], None
    for r in rows(name):
        if "label" in r and "runs" in r and "result" not in r:
            label = r["label"]
            batches.append((label, []))
        elif "result" in r:
            batches[-1][1].append(r)
    return batches


def rng(values):
    return f"{min(values):.2f}-{max(values):.2f}" if values else "-"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = []

    # CI history: attempt rows "<run> <attempt> <conclusion> {...}"
    hist = (HERE / "fix-141-ci-history-01.log").read_text().splitlines()
    att = [ln for ln in hist if re.match(r"^\d+ \d+ ", ln)]
    pre = [ln for ln in att if ln.split()[0] not in BRANCH_RUNS]
    fails = [ln for ln in pre if "'EarlySaveTests': (" in ln and "'FAIL')" in ln]
    ok = [ast.literal_eval(ln.split(" ", 3)[3])["EarlySaveTests"][0] for ln in pre
          if "'FAIL')" not in ln.split("GuardTests")[0]]
    bad = [ast.literal_eval(ln.split(" ", 3)[3])["EarlySaveTests"][0] for ln in fails]
    out.append(f"ci-history: {len(att)} attempt rows, {len(att) - len(pre)} of this branch, "
               f"{len(pre)} before it; EarlySaveTests failed in {len(fails)} of {len(pre)}")
    out.append(f"ci-history: passing EarlySaveTests durations {rng(ok)} s; failing {sorted(bad)}")
    out.append("ci-history: failure tails: " + str(
        [ln.strip() for ln in hist if ln.startswith("RuntimeError")]))
    binds = re.findall(r"\[(\d\d):(\d\d):(\d\d)\] (dosbox-x started|game window|window bind failed|signal 15)",
                       "\n".join(hist))
    out.append("ci-history: session log events (time, event) of the failures: " + str(
        [f"{h}:{m}:{s} {e}" for h, m, s, e in binds]))

    # CI and local reproductions
    for name in sorted(p.name for p in HERE.glob("fix-141-repro-*.log")):
        for label, rs in runs(name):
            counts = {}
            for r in rs:
                counts[r["result"]] = counts.get(r["result"], 0) + 1
            bind = [r["marks_s"]["window_id"] - r["marks_s"]["session"] for r in rs
                    if "window_id" in r["marks_s"] and "session" in r["marks_s"]]
            idx = [r["marks_s"]["index"] for r in rs if "index" in r["marks_s"]]
            logger = sum(any("key logger stopped" in x for x in r.get("log", [])) for r in rs)
            settled = [x for r in rs for x in r.get("log", []) if "test early save" in x]
            sup = [re.search(r"superseded: (\d+)", x).group(1) for r in rs for x in r.get("log", [])
                   if "superseded:" in x]
            out.append(f"{name} [{label}]: {len(rs)} runs {counts}; bind after session {rng(bind)} s;"
                       f" index {rng(idx)} s; key logger stopped {logger}; superseded {sup};"
                       f" hook {settled[:2]}")
    # mutations and reruns
    m = (HERE / "fix-141-mutations-04.log").read_text()
    out.append("mutations-04: " + str(re.findall(r"^## (m\d|unmutated[^:]*)[^\n]*exit (\d)", m, re.M)))
    rr = (HERE / "fix-141-ci-reruns-01.log").read_text()
    out.append("ci-reruns-01: " + str(re.findall(r"^\d+ (\d) (\w+) .*'EarlySaveTests': \(([\d.]+)", rr, re.M))
               + f"; 'Ran 961 tests' x{rr.count('Ran 961 tests')}, 'OK (skipped=18)' x{rr.count('OK (skipped=18)')}")
    probe = rows("fix-141-probe-logger-01.log")
    out.append(f"probe-logger-01: {sum(1 for r in probe if 'trial' in r)} trials, "
               f"{sum(1 for r in probe if r.get('exited'))} exited")
    Path(a.out).write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
