#!/usr/bin/env python3
"""Tabulate E002's records for F003: one line per record, then the checks of T07's Done-when 1-3.

    python3 experiments/E002-g1-driver-cycle/summarise.py [runs/E002/E002-r0011.json ...]

Reads the records only; interprets nothing beyond equality of the recorded values."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def val(rec, label, what):
    for o in rec["observations"]:
        if o.get("field", "").startswith(label + ": ") and what in o["field"]:
            return o["value"]
    return None


def main(argv):
    paths = [Path(p) for p in argv] or sorted((ROOT / "runs/E002").glob("E002-r*.json"))
    rows = []
    print("run | status | commit | launch UTC | launch local | before | stored | after | reset | mode b/a/r | ticks pre/before/after/reset")
    for p in paths:
        r = json.loads(p.read_text())
        g = lambda label, what: val(r, label, what)  # noqa: E731
        pre = "before restore (title screen displaced by the key)"
        stored = next((o["value"] for o in r["observations"] if o.get("field") == "screen sha256 stored with the start state"), None)
        launch = {o["field"]: o["value"] for o in r["observations"] if o.get("field", "").startswith("host ") and "at launch" in o["field"]}
        row = {"run": r["run_id"], "status": r["status"], "state": r["start_state"]["sha256"], "restore": r["start_state"]["restore"],
               "before": g("before", "sha256"), "stored": stored, "after": g("after", "sha256"), "reset": g("reset (Host+L again)", "sha256"),
               "modes": [g(lb, "0040:0049") for lb in ("before", "after", "reset (Host+L again)")],
               "ticks": [g(lb, "0040:006C") for lb in (pre, "before", "after", "reset (Host+L again)")]}
        rows.append(row)
        s = lambda x: (x or "-")[:8]  # noqa: E731
        print(" | ".join([row["run"], row["status"][:40], r["code_commit"], launch.get("host UTC time at launch", "-"),
                          launch.get("host local time at launch, with UTC offset, and zone name", "-"),
                          s(row["before"]), s(row["stored"]), s(row["after"]), s(row["reset"]),
                          "/".join(m or "-" for m in row["modes"]),
                          " / ".join((t or "-").split(" ")[0] for t in row["ticks"])]))
    done = [x for x in rows if x["status"] == "completed"]
    print(f"\n{len(rows)} records, {len(done)} completed")
    print("distinct before digests (completed):", sorted({x["before"] for x in done}))
    print("distinct start_state.sha256 (all):", sorted({x["state"] for x in rows}))
    print("restore names Host+L:", sum("Host+L" in x["restore"] for x in rows), "of", len(rows))
    print("before == stored and reset == stored:", sum(x["before"] == x["stored"] == x["reset"] for x in done), "of", len(done))
    print("mode byte 03 at every read:", sum(all(m == "03" for m in x["modes"]) for x in done), "of", len(done))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
