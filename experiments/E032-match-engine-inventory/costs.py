#!/usr/bin/env python3
"""E032: every cost the match-engine plan states, recounted from the measured logs and the static tables
(PR 243 review round 1, R3; round 2, R4: no assumption where a committed log measures the figure).

    python3 -B experiments/E032-match-engine-inventory/costs.py <out.md>

Writes <out.md> and, beside it, <out>.json with every figure the plan quotes (plancheck.py checks the plan
against it). Both refused if they exist.

Every input is MEASURED from a committed log, or an ASSUMPTION named below and printed as one:
- seconds per oracle match: the completed matches of the delay-count timing logs;
- seconds per hooked match (the stand-in for a port's match): the completed matches of every exact-pilot log;
- falsifier CPU: EVERY falsifier record of the pilot logs, completed or not, at the CPU it consumed (a
  falsifier that hangs runs to pilot_movement.py's 300 s timeout and counts as such);
- seconds per coverage run: the completed coverage runs;
- seconds per proved whole match (route A): T48's logs in experiments/E021-m0-whole-match/out/, the runs that
  reached minute 91 (runs stopped by the 1800 s limit are counted apart);
- instructions: cov-s1234-20261015.json (analyze.part), routines.tsv and calls.tsv, union-5seeds-20261015.md.
Records are validated by compare.py (a malformed log stops the recount). CPU time is one core's; elapsed time
is CPU time divided by WORKERS (2, the brief's limit)."""
import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E032-match-engine-inventory"))
from analyze import incomplete, part  # noqa: E402
import compare  # noqa: E402

OUT = ROOT / "experiments/E032-match-engine-inventory/out"
E021 = ROOT / "experiments/E021-m0-whole-match/out"
WORKERS = 2
# ---- assumptions: none of these is measured by a committed log ----
ASSUMED = {
    "PILOT_MINUTES": (40, "my own time for the pilot (reading, writing, first run), self-reported in notes.md, not logged"),
    "RATE_FACTORS": ({"optimistic (the pilot's rate)": 1.0, "central (half the pilot's rate)": 0.5,
                      "pessimistic (a quarter of it)": 0.25}, "the share of the pilot's rate the rest of the engine allows"),
    "FIXED_HOURS": ({"P0 tooling": 3, "P6 adapter and the port on its own": 4, "P7 start states (preparing them)": 1,
                     "the distribution sheet (work, not CPU)": 2}, "estimates of work that is not porting"),
    "FAMILY": (40, "matches per step check: 20 seeds plain + the same 20 with declared edits (a plan choice)"),
    "CHECKS_PER_STEP": (6, "family checks a step runs while it ports and debugs"),
    "COVERAGE_RUNS": (5, "coverage runs per step (as E032's union)"),
    "STEPS_WITH_CHECKS": (8, "P0-P7 each run family checks"),
    "PORT_SPEED": ("the hooked pilot's mean", "a port's match on its own is unmeasured until P6; the hooked "
                   "pilot's speed stands in"),
    "FALSIFIER_SET": ("the mean measured set", "a step's three falsifiers cost what the pilot's three cost, "
                      "the hung one included"),
    "SHEET_A": ((500, 2, 100), "oracle matches on E011-r0001's state; new start states at P7; matches on each"),
    "SD_GOALS": (1.37, "C-MATCH-27's watched goals sd (measured there, F005), taken as given"),
}
Z_ALPHA, Z_BETA = 1.959964, 0.841621   # two-sided 0.05, power 0.8
EFFECTS = ["skill +4", "energy", "form"] + [f"tactic element {k}" for k in range(1, 9)]   # E026 e1..e8
STEPS = ["P1", "P2", "P3", "P4", "P5", "P7"]
FALSIFIERS = ("coin-swapped", "bound-36", "no-picture")


def A(name):
    return ASSUMED[name][0]


def completed_records(*names):
    recs = []
    for n in names:
        for r in compare.load(OUT / n).values():
            if not compare.completed(r):
                recs.append(r)
    return recs


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
    if p in ("ball and player motion, offside line", "positioning and marking movement", "marking and leaders"):
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
    jdest = dest.with_suffix(".json")
    if dest.exists() or jdest.exists():
        sys.exit(f"refused: {dest} or {jdest} exists")
    J = {}
    L = []
    say = L.append
    say("# E032 cost recount (PR 243 review rounds 1 and 2)\n")
    say("## Assumptions (not measured by any committed log)\n")
    for k, (v, why) in ASSUMED.items():
        say(f"- {k} = {v}: {why}")
    say("")

    # -- seconds, measured --
    plain = completed_records("timing-plain-20261015.jsonl", "timing-plain-8seeds-20261015.jsonl")
    d20 = completed_records("timing-delay20-kickoff-20261015.jsonl", "timing-delay20-8seeds-20261015.jsonl")
    hooked = completed_records("pilot-exact-try1-20261015.jsonl", "pilot-exact-8seeds-20261015.jsonl",
                               "pilot-exact-8seeds-review1.jsonl")
    sets = {}
    for stamp in ("20261015", "review1"):
        rows = []
        for v in FALSIFIERS:
            for r in compare.load(OUT / f"pilot-{v}-{stamp}.jsonl").values():
                rows.append((v, r["cpu_s"], "completed" if not compare.completed(r) else "did not complete"))
        sets[stamp] = rows
    covs = [compare.record_schema.loads((OUT / f"cov-d20-{s}-20261015.json").read_text())
            for s in ("0x1234", "0x2345", "0x4c1d", "0xc3c3", "0xe719")]
    cov_s = [c["seconds"] for c in covs if not incomplete(c)]
    if len(cov_s) != len(covs) or not all(compare.record_schema.finite_number(s, 1e-9, 1e6) for s in cov_s):
        sys.exit("refused: a coverage run is incomplete or its seconds are not a positive number")
    proved, stopped = [], []
    # ASCII digits only ([0-9]: \d would match other scripts' digits); seconds a plain decimal (round 4)
    pat = re.compile(r"emulated ([0-9]+) clock ticks, [0-9]+ seed writes, ([0-9]+(?:\.[0-9]+)?) s; "
                     r"full time: minute ([0-9]+)")
    # an explicit list (round 5): a glob that matched fewer logs would shrink the measurement silently
    t48 = ["t48-m2-longs" + s + ".log" for s in (
        "+0279-no-cross-term-run2", "+0279-no-cross-term-run3", "+0279-no-cross-term", "+0279-product+1",
        "+0279-scratch-run2", "+0279-scratch-run3", "+0279-scratch", "+0d56-lowword-signed", "+0d56-min",
        "+0d56-tie-a-run2", "+0d56-tie-a-run3", "+0d56-tie-a", "-run2", "")] + [
        f"t48-regression-{s}.log" for s in ("m1-377e", "m2-287c", "m2-draws")]
    missing = [n for n in t48 if not (E021 / n).is_file()]
    if missing:
        sys.exit(f"refused: T48 logs missing: {missing}")
    for log in (E021 / n for n in t48):
        for m in pat.finditer(log.read_text()):
            (proved if int(m.group(3)) == 91 else stopped).append(float(m.group(2)))

    def stat(v):
        return statistics.mean(v), min(v), max(v), len(v)
    pm, pmin, pmax, pn = stat([r["cpu_s"] for r in plain])
    om, omin, omax, on = stat([r["cpu_s"] for r in d20])
    hm, hmin, hmax, hn = stat([r["cpu_s"] for r in hooked])
    set_totals = {k: sum(c for _, c, _ in v) for k, v in sets.items()}
    FSET = statistics.mean(set_totals.values())
    COV = statistics.mean(cov_s)
    say("## Seconds, measured (CPU)\n")
    say(f"- oracle, plain: mean {pm:.1f} s, range {pmin}-{pmax} s, n = {pn}")
    say(f"- oracle, delay count at kick-off: mean {om:.1f} s, range {omin}-{omax} s, n = {on}")
    say(f"- hooked pilot port (exact): mean {hm:.1f} s, range {hmin}-{hmax} s, n = {hn}")
    for k, v in sets.items():
        say(f"- falsifier set {k}: " + ", ".join(f"{n} {c} s ({st})" for n, c, st in v) + f"; total {set_totals[k]:.1f} s")
    say(f"- falsifier set, mean of the {len(sets)} sets: {FSET:.1f} s (budgeting them at the hooked mean would give "
        f"{3 * hm:.1f} s)")
    say(f"- coverage run: mean {COV:.1f} s, n = {len(cov_s)}")
    say(f"- T48 proved whole matches (route A): {len(proved)} reached minute 91 in {min(proved) / 60:.0f}-"
        f"{max(proved) / 60:.0f} min (median {statistics.median(proved) / 60:.0f}); {len(stopped)} more stopped at a "
        f"time limit\n")
    J.update(oracle_mean=round(om, 1), oracle_min=omin, oracle_max=omax, plain_min=pmin, plain_max=pmax,
             hooked_mean=round(hm, 1), falsifier_set=round(FSET, 1), proved_min_minutes=round(min(proved) / 60),
             proved_max_minutes=round(max(proved) / 60), proved_n=len(proved), proved_stopped=len(stopped))

    # -- instructions by step --
    run = compare.record_schema.loads((OUT / "cov-s1234-20261015.json").read_text())
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
                if line.startswith(("| 0791:", "| 1771:"))]
    frontier = [c for c in frontier if c != "0791:D733"]          # the quick engine is modelled (F012)
    shootout = ["0791:A10A"] + [c for c in sorted(calls["0791:A10A"])
                                if c.startswith("0791") and c not in reached and c not in setup]
    by_step["P7"] = sum(info[c] for c in frontier + shootout)
    total_instr = sum(by_step.values())
    say("## Instructions by step (static, counted)\n")
    for s in STEPS:
        say(f"- {s}: {by_step[s]:,}")
    say(f"- P5 includes the set-up {', '.join(setup)}; P7 is the frontier {', '.join(frontier)} and the shoot-out "
        f"{', '.join(shootout)}")
    say(f"- total: {total_instr:,}\n")
    J.update({f"instr_{s}": by_step[s] for s in STEPS}, instr_total=total_instr)

    pilot = ["0791:8889", "0791:86D0", "0791:2BE5", "0791:2974", "0791:045D", "0791:2CC5", "0791:2DCA",
             "23E4:08DF", "214B:0688", "214B:06B1", "214B:06FA"]
    pilot_instr = sum(info[c] for c in pilot)
    rate = pilot_instr / (A("PILOT_MINUTES") / 60)
    fixed = sum(A("FIXED_HOURS").values())
    say(f"## Implementer hours\n\nThe pilot: {pilot_instr} static instructions ({', '.join(pilot)}) in "
        f"{A('PILOT_MINUTES')} min (ASSUMED) = {rate:.0f} an hour.\n")
    say("Fixed hours (ASSUMED): " + ", ".join(f"{k} {v} h" for k, v in A("FIXED_HOURS").items()) + f" = {fixed} h.\n")
    say("| rate | " + " | ".join(STEPS) + " | porting | with fixed hours |")
    say("| --- | " + " | ".join("---" for _ in STEPS) + " | --- | --- |")
    for label, f in A("RATE_FACTORS").items():
        hrs = {s: by_step[s] / (f * rate) for s in STEPS}
        port = sum(hrs.values())
        say(f"| {label} | " + " | ".join(f"{hrs[s]:.1f}" for s in STEPS) + f" | {port:.1f} | {port + fixed:.1f} |")
        key = label.split()[0]
        J[f"hours_{key}"] = round(port + fixed, 1)
        J[f"porting_{key}"] = round(port, 1)
        if key == "central":
            # P7 adds its hour of preparing start states (FIXED_HOURS); one decimal, as the table
            J.update({f"hours_central_{s}": round(hrs[s] + (1 if s == "P7" else 0), 1) for s in STEPS})
    J.update(pilot_instr=pilot_instr, pilot_rate=round(rate), fixed_hours=fixed, pilot_minutes=A("PILOT_MINUTES"),
             hours_P0=A("FIXED_HOURS")["P0 tooling"], hours_P6=A("FIXED_HOURS")["P6 adapter and the port on its own"],
             family=A("FAMILY"), sheet_a_base=A("SHEET_A")[0], falsifier_at_hooked=round(3 * hm, 1), oracle_n=on)
    say("")

    # -- CPU per step and per review --
    check_cpu = A("FAMILY") * hm
    step_cpu = A("CHECKS_PER_STEP") * check_cpu + FSET + A("COVERAGE_RUNS") * COV
    review_cpu = check_cpu + FSET
    say("## CPU per step and per review\n")
    say(f"- one family check: {A('FAMILY')} x {hm:.1f} s = {check_cpu / 60:.1f} CPU min, "
        f"{check_cpu / 60 / WORKERS:.1f} min elapsed on {WORKERS} workers")
    say(f"- one step: {A('CHECKS_PER_STEP')} checks + one falsifier set ({FSET:.1f} s, measured) + "
        f"{A('COVERAGE_RUNS')} coverage runs = {step_cpu / 3600:.2f} CPU h, {step_cpu / 3600 / WORKERS:.2f} h elapsed")
    say(f"- one review: one check + one falsifier set = {review_cpu / 60:.1f} CPU min, "
        f"{review_cpu / 60 / WORKERS:.1f} min elapsed")
    say(f"- all {A('STEPS_WITH_CHECKS')} steps: {A('STEPS_WITH_CHECKS') * step_cpu / 3600:.1f} CPU h, "
        f"{A('STEPS_WITH_CHECKS') * step_cpu / 3600 / WORKERS:.1f} h elapsed\n")
    J.update(check_cpu_min=round(check_cpu / 60, 1), check_elapsed_min=round(check_cpu / 60 / WORKERS, 1),
             step_cpu_h=round(step_cpu / 3600, 2), step_elapsed_h=round(step_cpu / 3600 / WORKERS, 2),
             review_cpu_min=round(review_cpu / 60, 1), review_elapsed_min=round(review_cpu / 60 / WORKERS, 1),
             steps_cpu_h=round(A("STEPS_WITH_CHECKS") * step_cpu / 3600, 1))

    # -- sample sizes --
    def n_per_arm(d):
        return math.ceil(2 * (Z_ALPHA + Z_BETA) ** 2 * A("SD_GOALS") ** 2 / d ** 2)
    n25, n50 = n_per_arm(0.25), n_per_arm(0.5)
    one_effect = 2 * n25 * om
    say("## Matches per arm (goals, two arms, alpha 0.05, power 0.8)\n")
    say(f"- 0.25 goals: {n25}; 0.5 goals: {n50}")
    say(f"- route B, one effect at 0.25 goals, the oracle's two arms: {2 * n25} matches = "
        f"{one_effect / 3600:.1f} CPU h ({one_effect / 3600 / WORKERS:.1f} h elapsed)\n")
    J.update(n25=n25, n50=n50, effect_matches=2 * n25, effect_cpu_h=round(one_effect / 3600, 1),
             effect_elapsed_h=round(one_effect / 3600 / WORKERS, 1))

    # -- the distribution sheets --
    base, nstates, per = A("SHEET_A")
    a_oracle = base + nstates * per
    a_port = base + (base + nstates * per)
    a_cpu = a_oracle * om + a_port * hm
    say("## The distribution sheets\n")
    say(f"- Sheet A: {a_oracle} oracle matches ({base} at P6, reused at P7, plus {nstates} x {per}); {a_port} port "
        f"matches ({base} at P6, {base + nstates * per} at P7); {a_cpu / 3600:.1f} CPU h, "
        f"{a_cpu / 3600 / WORKERS:.1f} h elapsed (the port at the hooked speed, ASSUMED)")
    J.update(sheet_a_oracle=a_oracle, sheet_a_port=a_port, sheet_a_cpu_h=round(a_cpu / 3600, 1),
             sheet_a_elapsed_h=round(a_cpu / 3600 / WORKERS, 1))
    arms = len(EFFECTS) + 1
    for d, n, key in ((0.25, n25, "b25"), (0.5, n50, "b50")):
        m = arms * n
        say(f"- Sheet B at {d} goals: {len(EFFECTS)} effect arms + one shared baseline = {arms} arms x {n} = "
            f"{m:,} matches at the oracle's {om:.1f} s: {m * om / 3600:.1f} CPU h, {m * om / 3600 / WORKERS:.1f} h elapsed")
        J.update({f"sheet_{key}_matches": m, f"sheet_{key}_cpu_h": round(m * om / 3600, 1),
                  f"sheet_{key}_elapsed_h": round(m * om / 3600 / WORKERS, 1)})
    say("")
    d_hours = A("FIXED_HOURS")["P0 tooling"] + A("FIXED_HOURS")["P6 adapter and the port on its own"]
    say(f"## Option D's first stage\n\n- P0 tooling + the image adapter: {d_hours} h, then {omin}-{omax} CPU s a match\n")
    J.update(option_d_hours=d_hours)
    dest.write_text("\n".join(L) + "\n")
    jdest.write_text(json.dumps(J, indent=1, sort_keys=True) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
