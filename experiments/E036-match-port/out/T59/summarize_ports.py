#!/usr/bin/env python3
"""T59: from a family.py log with --count 0791:6E11 (ports.jsonl), 6E11's calls per match by family, the matches with
none, and from the run's printed log the decisions answered while a port's frame was live, per match.

    python3 -B experiments/E036-match-port/out/T59/summarize_ports.py <ports.jsonl> <run log .txt>"""
import json
import sys
from collections import Counter


def main(log, run_log):
    calls = {}
    for line in open(log):
        r = json.loads(line)
        calls[r["id"]] = (r["counts"].get("0791:6E11"), r["port_calls"].get("0791:6E11"))
    for fam in ("F40", "O8", "S"):
        ids = [i for i in calls if i.startswith(fam + "/")]
        n = [calls[i][0] for i in ids]
        print(f"{fam}: {len(ids)} matches; 6E11 executed per match min {min(n)} max {max(n)} total {sum(n)}; "
              f"with none: {[i for i in ids if not calls[i][0]] or 'none'}")
    print("per match (executed, port's calls): " + ", ".join(f"{i} {c[0]}/{c[1]}" for i, c in calls.items()))
    under = Counter(line.split(":")[0] for line in open(run_log) if "answered with port frames live" in line)
    print(f"decisions answered with a port's frame live: {sum(under.values())} in {len(under)} matches: "
          + ", ".join(f"{i} {n}" for i, n in under.items()))


if __name__ == "__main__":
    main(*sys.argv[1:])
