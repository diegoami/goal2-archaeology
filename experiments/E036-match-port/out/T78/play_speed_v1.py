"""T78d Done-when 4: play speed, measured (no threshold).

    python3 -B experiments/E036-match-port/out/T78/play_speed_v1.py --port <port.jsonl> --original <original.jsonl>
        --day <goal2-days.json> --out experiments/E036-match-port/out/T78/play-speed-v1.json

From the T78d family run on the port and an original-engine (Unicorn) run of the same family on
the same machine and load, the CPU and wall seconds per match by policy (how the managed side
plays it: PlayOn to the end, Quick, QuickAtHalfTime, Knockout, ...) and fixture kind (1 friendly,
2 qualifier, 200 knockout), with mean, range and the port/original ratio per match; and one
tournament day of a fresh goal2 career (--day: the day sizes and the measured Unicorn day times
from goal2's Core, with their source), timed at these figures. The kit runs matches without a
display, so a "watched" match is the PlayOn figure: the engine's own cost, not a human's pace.
"""
import argparse
import hashlib
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "experiments/E036-match-port"), str(ROOT)]


def load(path):
    import records
    out = {}
    for line in Path(path).read_text().splitlines():
        r = json.loads(line)
        if records.is_completed(r):
            out[r["id"]] = r
    return out


def summary(values):
    return dict(n=len(values), mean=round(statistics.fmean(values), 2), min=round(min(values), 2),
                max=round(max(values), 2)) if values else dict(n=0)


ap = argparse.ArgumentParser()
ap.add_argument("--port", required=True)
ap.add_argument("--original", required=True)
ap.add_argument("--day", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
out = open(a.out, "x")
import families  # noqa: E402
specs = {m.id: m.spec() for fam in families.select("ALL", families.discover()) for m in fam.matches}
port, original = load(a.port), load(a.original)
groups = {}
for mid, spec in specs.items():
    if mid in port and mid in original:
        key = f"{spec['policy']['name']} kind {spec['fixture'][3]}"
        g = groups.setdefault(key, dict(ids=[], port_cpu=[], original_cpu=[], port_wall=[], original_wall=[], ratio=[]))
        g["ids"].append(mid)
        for side, rec in (("port", port[mid]), ("original", original[mid])):
            g[f"{side}_cpu"].append(rec["cpu_s"]);g[f"{side}_wall"].append(rec["wall_s"])
        g["ratio"].append(port[mid]["cpu_s"] / original[mid]["cpu_s"])
by_kind = {k: dict(matches=len(g["ids"]), port_cpu_s=summary(g["port_cpu"]), original_cpu_s=summary(g["original_cpu"]),
                   port_wall_s=summary(g["port_wall"]), original_wall_s=summary(g["original_wall"]),
                   port_over_original=summary(g["ratio"]), ids=g["ids"]) for k, g in sorted(groups.items())}
every = [port[i]["cpu_s"] / original[i]["cpu_s"] for i in specs if i in port and i in original]
day = json.loads(Path(a.day).read_text())
played = [port[i]["cpu_s"] for i in specs if i in port and specs[i]["policy"]["name"] == "PlayOn"]
original_played = [original[i]["cpu_s"] for i in specs if i in original and specs[i]["policy"]["name"] == "PlayOn"]
report = dict(
    port=dict(path=a.port, sha256=hashlib.sha256(Path(a.port).read_bytes()).hexdigest(), completed=len(port)),
    original=dict(path=a.original, sha256=hashlib.sha256(Path(a.original).read_bytes()).hexdigest(), completed=len(original)),
    matches_compared=len(every), port_over_original_all=summary(every), by_policy_and_kind=by_kind,
    tournament_day=dict(
        source=day["source"], day_sizes=day["sizes"], largest_day_fixtures=max(day["sizes"]),
        unicorn_day_seconds=day["unicorn_days"],
        unicorn_simulated_fixture_s=day["unicorn_simulated_fixture_s"],
        managed_match_cpu_s=dict(port=summary(played), original=summary(original_played)),
        largest_day_estimate_s=dict(
            port_managed_match_plus_unicorn_simulated=round(statistics.fmean(played)
                                                            + (max(day["sizes"]) - 1) * day["unicorn_simulated_fixture_s"], 1),
            note=("simulate_fixture (000E:6970) is not ported yet (the tournament continuation, request 427): "
                  "a day's other fixtures still run on the original engine; their port cost is unmeasured."))),
    diagnostic_not_acceptance=True)
json.dump(report, out, indent=2);out.close()
print(json.dumps({k: report[k] for k in ("matches_compared", "port_over_original_all")}))
