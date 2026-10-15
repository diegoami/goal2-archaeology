#!/usr/bin/env python3
"""E032: every cost the match-engine plan states, recounted from the measured logs and the static tables
(PR 243's review, R3: a cost stated without recounting the runs it prescribes).

    python3 -B experiments/E032-match-engine-inventory/costs.py <out.md>

Inputs, all committed: the timing logs (oracle seconds per match, plain and with the delay count), the
pilot logs (seconds per match with a ported routine hooked), the coverage runs (seconds per covered match),
cov-s1234-20261015.json (instructions by part, analyze.part), static/goal-exe/routines.tsv and calls.tsv
(the routines no friendly reaches). Only completed matches are counted (analyze.incomplete). Every
ASSUMPTION is a named constant below and is printed with the result. CPU time is one core's; elapsed time is
CPU time divided by the number of workers (WORKERS = 2, the brief's limit). Refused if <out.md> exists."""
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E032-match-engine-inventory"))
from analyze import incomplete, part  # noqa: E402

OUT = ROOT / "experiments/E032-match-engine-inventory/out"
WORKERS = 2
# ---- assumptions (each printed) ----
PILOT_MINUTES = 40          # my time for the pilot: reading, writing and the first run (notes.md)
RATE_FACTORS = {"optimistic (the pilot's rate)": 1.0, "central (half the pilot's rate)": 0.5,
                "pessimistic (a quarter of it)": 0.25}
FIXED_HOURS = {"P0 tooling": 3, "P6 adapter and the port on its own": 4, "P7 start states (preparing them)": 1,
               "the distribution sheet (work, not CPU)": 2}
FAMILY = 40                 # matches per step check: 20 seeds plain + the same 20 with declared edits
CHECKS_PER_STEP = 6         # full family checks a step runs while it ports and debugs
FALSIFIERS = 3              # one match each
COVERAGE_RUNS = 5           # one coverage union per step
REVIEW_CHECKS = 1           # the reviewer re-runs one family check and the falsifiers
SD_GOALS = 1.37             # C-MATCH-27, watched goals per match
Z_ALPHA, Z_BETA = 1.959964, 0.841621   # two-sided 0.05, power 0.8
EFFECTS = ["skill +4", "energy", "form"] + [f"tactic element {k}" for k in range(1, 9)]   # E026 e1..e8
SHEET_A_ORACLE = 500        # the fidelity sheet's oracle matches on E011-r0001's state
SHEET_A_NEW_STATES, SHEET_A_PER_NEW_STATE = 2, 100      # P7's other start states
STEPS = ["P1", "P2", "P3", "P4", "P5", "P7"]


def logs(name):
    return [json.loads(line) for line in (OUT / name).read_text().splitlines() if line.strip()]


def ok(records):
    return [r for r in records if not incomplete(r)]


def secs(records, key="cpu_s"):
    v = [r[key] for r in ok(records)]
    return statistics.mean(v), min(v), max(v), len(v)


def static_rows():
    info, calls = {}, {}
    for line in (ROOT / "static/goal-exe/routines.tsv").read_text().splitlines():
        if line.startswith((";", "segment")):
            continue
        f = line.split("\t")
        info[f[0]] = int(f[2])
    for line in (ROOT / "static/goal-exe/calls.tsv").read_text().splitlines():
        if line.startswith((";", "caller")):
            continue
        a, b, _ = line.split("\t")
        calls.setdefault(a, set()).add(b)
    return info, calls


def step_of(row):
    p = part(row)
    a = row["address"]
    if a in ("0791:8537", "0791:8E24", "0791:9119"):
        return "P2"
    if p in ("geometry and queries", "player attributes (1771)"):
        return "P1"
    if a.startswith(("214B:", "23E4:")) and row["name"].startswith(("u214b_random", "u214b_lcg", "u214b_set",
                                                                   "sys_set", "u214b_long", "sys_long")):
        return "P1"
    if p in ("ball and player motion, offside line", "positioning and marking movement", "marking and leaders",
             "referee"):
        return "P2"
    if p in ("ball, passing, shooting", "decisions and contests"):
        return "P3"
    if p in ("duels and play at the ball", "goals, restarts, set pieces"):
        return "P4"
    if p in ("form, fouls, cards, substitutions", "commentary and ratings", "set-up and computer manager",
             "match frame"):
        return "P5"
    return None


def main():
    dest = Path(sys.argv[1])
    if dest.exists():
        sys.exit(f"refused: {dest} exists")
    L = []
    say = L.append
    say("# E032 cost recount (PR 243 review, R3)\n")
    say("Assumptions: " + "; ".join([
        f"pilot time {PILOT_MINUTES} min", f"workers {WORKERS}", f"family {FAMILY} matches per check",
        f"{CHECKS_PER_STEP} checks per step", f"{FALSIFIERS} falsifier matches per step",
        f"{COVERAGE_RUNS} coverage runs per step", f"sd of goals {SD_GOALS}", f"{len(EFFECTS)} effects: " +
        ", ".join(EFFECTS)]) + ".\n")

    # -- seconds per match, measured --
    plain = logs("timing-plain-20261015.jsonl") + logs("timing-plain-8seeds-20261015.jsonl")
    d20 = logs("timing-delay20-kickoff-20261015.jsonl") + logs("timing-delay20-8seeds-20261015.jsonl")
    hooked = logs("pilot-exact-try1-20261015.jsonl") + logs("pilot-exact-8seeds-20261015.jsonl")
    cov = [json.loads((OUT / f"cov-d20-{s}-20261015.json").read_text())
           for s in ("0x1234", "0x2345", "0x4c1d", "0xc3c3", "0xe719")]
    cov_s = [c["seconds"] for c in cov if not incomplete(c)]
    pm, pmin, pmax, pn = secs(plain)
    om, omin, omax, on = secs(d20)
    hm, hmin, hmax, hn = secs(hooked)
    say("## Seconds per whole match (CPU, measured)\n")
    say(f"- oracle, plain: mean {pm:.1f} s, range {pmin}-{pmax} s, n = {pn}")
    say(f"- oracle, delay count at kick-off: mean {om:.1f} s, range {omin}-{omax} s, n = {on}")
    say(f"- oracle with the pilot's port hooked: mean {hm:.1f} s, range {hmin}-{hmax} s, n = {hn}")
    say(f"- coverage run (block hook): mean {statistics.mean(cov_s):.1f} s, n = {len(cov_s)}\n")
    ORACLE, HOOKED, COV = om, hm, statistics.mean(cov_s)

    # -- instructions by step --
    run = json.loads((OUT / "cov-s1234-20261015.json").read_text())
    if incomplete(run):
        sys.exit("refused: the coverage run is incomplete")
    by_step = {s: 0 for s in STEPS}
    for row in run["routines"]:
        if row["exec_match"] > 0:
            s = step_of(row)
            if s:
                by_step[s] += row["instructions_static"]
    info, calls = static_rows()
    reached = {row["address"] for row in run["routines"] if row["exec_match"] > 0}
    setup = ["0791:A4A1"] + [c for c in sorted(calls["0791:A4A1"]) if c.startswith("0791") and c not in reached]
    by_step["P5"] += sum(info[c] for c in setup)
    frontier = [line.split(" | ")[0].strip("| ") for line in (OUT / "union-5seeds-20261015.md").read_text().splitlines()
                if line.startswith("| 0791:") or line.startswith("| 1771:")]
    frontier = [c for c in frontier if c != "0791:D733"]          # the quick engine is modelled (F012)
    shootout = ["0791:A10A"] + [c for c in sorted(calls["0791:A10A"])
                                if c.startswith("0791") and c not in reached and c not in setup]   # A841: in P5
    by_step["P7"] = sum(info[c] for c in frontier + shootout)
    total_instr = sum(by_step.values())
    say("## Instructions by step (static, counted)\n")
    for s in STEPS:
        say(f"- {s}: {by_step[s]:,}")
    say(f"- P5 includes the set-up {', '.join(setup)}; P7 is the frontier {', '.join(frontier)} and the shoot-out "
        f"{', '.join(shootout)}")
    say(f"- total: {total_instr:,}\n")

    pilot = ["0791:8889", "0791:86D0", "0791:2BE5", "0791:2974", "0791:045D", "0791:2CC5", "0791:2DCA",
             "23E4:08DF", "214B:0688", "214B:06B1", "214B:06FA"]
    pilot_instr = sum(info[c] for c in pilot)
    rate = pilot_instr / (PILOT_MINUTES / 60)
    say(f"## Implementer hours\n\nThe pilot: {pilot_instr} static instructions ({', '.join(pilot)}) in "
        f"{PILOT_MINUTES} min = {rate:.0f} an hour.\n")
    fixed = sum(FIXED_HOURS.values())
    say("Fixed hours: " + ", ".join(f"{k} {v} h" for k, v in FIXED_HOURS.items()) + f" = {fixed} h.\n")
    say("| rate | " + " | ".join(STEPS) + " | porting | with fixed hours |")
    say("| --- | " + " | ".join("---" for _ in STEPS) + " | --- | --- |")
    totals = {}
    for label, f in RATE_FACTORS.items():
        hrs = {s: by_step[s] / (f * rate) for s in STEPS}
        port = sum(hrs.values())
        totals[label] = port + fixed
        say(f"| {label} | " + " | ".join(f"{hrs[s]:.1f}" for s in STEPS) + f" | {port:.1f} | {port + fixed:.1f} |")
    say("")

    # -- CPU per step and per review --
    check_cpu = FAMILY * HOOKED
    step_cpu = CHECKS_PER_STEP * check_cpu + FALSIFIERS * HOOKED + COVERAGE_RUNS * COV
    review_cpu = REVIEW_CHECKS * check_cpu + FALSIFIERS * HOOKED
    say("## CPU per step\n")
    say(f"- one family check: {FAMILY} x {HOOKED:.1f} s = {check_cpu / 60:.1f} CPU min, "
        f"{check_cpu / 60 / WORKERS:.1f} min elapsed on {WORKERS} workers")
    say(f"- one step: {CHECKS_PER_STEP} checks + {FALSIFIERS} falsifiers + {COVERAGE_RUNS} coverage runs = "
        f"{step_cpu / 3600:.2f} CPU h, {step_cpu / 3600 / WORKERS:.2f} h elapsed")
    say(f"- one review: {REVIEW_CHECKS} check + {FALSIFIERS} falsifiers = {review_cpu / 60:.1f} CPU min, "
        f"{review_cpu / 60 / WORKERS:.1f} min elapsed")
    say(f"- seven steps with checks (P0-P5, P7; P6's check is the same family): {7 * step_cpu / 3600:.1f} CPU h\n")

    # -- sample sizes --
    def n_per_arm(d):
        return math.ceil(2 * (Z_ALPHA + Z_BETA) ** 2 * SD_GOALS ** 2 / d ** 2)
    n25, n50 = n_per_arm(0.25), n_per_arm(0.5)
    say("## Matches per arm (goals, two arms, alpha 0.05, power 0.8)\n")
    say(f"- 0.25 goals: {n25}; 0.5 goals: {n50}")
    one_effect_oracle = 2 * n25 * ORACLE
    say(f"- route B, one effect at 0.25 goals, the oracle's two arms: {2 * n25} matches = "
        f"{one_effect_oracle / 3600:.2f} CPU h ({one_effect_oracle / 3600 / WORKERS:.2f} h elapsed); the model's "
        f"two arms come on top, at the model's speed\n")

    # -- the distribution sheets --
    say("## The distribution sheets\n")
    a_oracle = SHEET_A_ORACLE + SHEET_A_NEW_STATES * SHEET_A_PER_NEW_STATE
    a_port_p6, a_port_p7 = SHEET_A_ORACLE, SHEET_A_ORACLE + SHEET_A_NEW_STATES * SHEET_A_PER_NEW_STATE
    a_cpu = a_oracle * ORACLE + (a_port_p6 + a_port_p7) * HOOKED
    say(f"- Sheet A (fidelity; required): the oracle's {SHEET_A_ORACLE} matches on E011-r0001's state are run "
        f"once, at P6, and reused at P7, which adds {SHEET_A_NEW_STATES} x {SHEET_A_PER_NEW_STATE} on its new "
        f"start states: {a_oracle} oracle matches; the port runs {a_port_p6} at P6 and {a_port_p7} at P7 "
        f"(the port changes between them). At {ORACLE:.1f} s an oracle match and {HOOKED:.1f} s a port match "
        f"(ASSUMED: the port's speed on its own is unmeasured until P6; the hooked pilot's speed stands in): "
        f"{a_cpu / 3600:.1f} CPU h, {a_cpu / 3600 / WORKERS:.1f} h elapsed")
    arms = len(EFFECTS) + 1
    for d, n in ((0.25, n25), (0.5, n50)):
        m = arms * n
        say(f"- Sheet B (effects for the bot; optional, goal2's call) at {d} goals: {len(EFFECTS)} effect arms and "
            f"ONE baseline arm shared by all effects = {arms} arms x {n} = {m:,} matches; at the oracle's "
            f"{ORACLE:.1f} s: {m * ORACLE / 3600:.1f} CPU h, {m * ORACLE / 3600 / WORKERS:.1f} h elapsed. Run once, "
            f"after P7, on whichever engine is faster (an exact port gives the oracle's results)")
    say("")
    say("## Option D's first stage\n")
    say(f"- P0 tooling + the image adapter: {FIXED_HOURS['P0 tooling'] + FIXED_HOURS['P6 adapter and the port on its own']} h of "
        f"implementer time, then {ORACLE:.1f} s a match (range {omin}-{omax} s)")
    say("")
    say("## Totals\n")
    for label, t in totals.items():
        say(f"- implementer hours, {label}: {t:.1f}")
    out = "\n".join(L) + "\n"
    dest.write_text(out)
    print(out)


if __name__ == "__main__":
    main()
