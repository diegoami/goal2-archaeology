#!/usr/bin/env python3
"""T79: sheet A, the fidelity sheet, from the two arms' records.

    python3 -B experiments/E036-match-port/sheet_a.py <oracle.jsonl> <port.jsonl> <sheet-a.md>

For each of the board's ten statistics (records.STAT_NAMES), the score and the board's two bars
(match.py BARS, rows 0x13 and 0x14), per side (first: the fixture's first country, the managed
one; second: the other): N, the mean and its 95% interval (mean +- 1.96 sd / sqrt(N), the sample
standard deviation), for the oracle and for the port, and in how many matches the two are equal.
Only matches completed in both arms enter a row; a match not completed in either is named with its
error. The sheet states what the records hold: nothing is smoothed, rounded before the mean, or
dropped beyond those named matches. The output is created exclusively (never overwritten).
"""
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import records  # noqa: E402


def load(path):
    return {r["id"]: r for r in map(json.loads, Path(path).read_text().splitlines())}


def values(rec):
    """The sheet's quantities of one record, name -> (first side, second side)."""
    out = {name: tuple(rec["board"]["statistics"][name]) for name in records.STAT_NAMES}
    out["goals"] = tuple(rec["score"])
    for row, pair in enumerate(rec["board"]["bars"]):
        out[f"bar row {0x13 + row:#04x}"] = tuple(pair)
    return out


def interval(xs):
    mean = statistics.fmean(xs)
    half = 1.96 * statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else float("nan")
    return mean, half


def main(argv):
    oracle_path, port_path, out_path = argv
    out = open(out_path, "x")
    oracle, port = load(oracle_path), load(port_path)
    ids = sorted(set(oracle) | set(port))
    done = [i for i in ids if i in oracle and i in port and records.is_completed(oracle[i]) and records.is_completed(port[i])]
    def state(arm, i):
        if i not in arm:
            return "missing"
        return "completed" if records.is_completed(arm[i]) else (arm[i]["error"] or "not completed")
    left = [(i, state(oracle, i), state(port, i)) for i in ids if i not in done]
    o_vals, p_vals = {i: values(oracle[i]) for i in done}, {i: values(port[i]) for i in done}
    names = list(o_vals[done[0]]) if done else []
    lines = ["# Sheet A: the original's board statistics and the port's", "",
             f"Oracle `{oracle_path}` ({len(oracle)} records), port `{port_path}` ({len(port)} records); "
             f"{len(done)} matches completed in both arms enter the rows.", ""]
    if left:
        lines += ["Not in the rows (not completed in an arm, or missing):", ""]
        lines += [f"- `{i}`: oracle {o}, port {p}" for i, o, p in left] + [""]
    lines += ["| Quantity | Side | N | Oracle mean ± 95% | Port mean ± 95% | Equal in |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for name in names:
        for side, label in ((0, "first"), (1, "second")):
            o = [o_vals[i][name][side] for i in done]
            p = [p_vals[i][name][side] for i in done]
            (om, oh), (pm, ph) = interval(o), interval(p)
            equal = sum(a == b for a, b in zip(o, p))
            lines.append(f"| {name} | {label} | {len(done)} | {om:.3f} ± {oh:.3f} | {pm:.3f} ± {ph:.3f} | {equal} of {len(done)} |")
    identical = sum(o_vals[i] == p_vals[i] for i in done)
    lines += ["", f"Every quantity equal match for match in {identical} of {len(done)} matches."]
    out.write("\n".join(lines) + "\n");out.close()
    print("\n".join(lines[-1:]))


if __name__ == "__main__":
    main(sys.argv[1:])
