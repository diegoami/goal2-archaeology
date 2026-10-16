#!/usr/bin/env python3
"""E032: check that every cost figure docs/match-engine-plan.md quotes equals costs.py's report (PR 243
review round 2, R4's class: a figure on the page that no script ties to its measurement).

    python3 -B experiments/E032-match-engine-inventory/plancheck.py <costs.json> [<plan.md>] [--out <file>]

Each check is a phrase of the plan with the report's value put in; the plan must contain it (white space
folded, so a line break inside a phrase does not matter). Then the reverse check: every number followed by a
cost unit (h, hours, CPU h, CPU minutes, s, CPU seconds, minutes, matches) in the plan must be one of the
values the checks cover, or listed in NOT_COSTS with why. Exits 1 on any miss, 2 on a missing key."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def f1(v):
    return f"{v:.1f}"


def thousands(v):
    return f"{v:,}"


# (phrase with {} for the value, key, formatter)
CHECKS = [
    ("costs 8.3-16.8 CPU seconds", None, None),     # filled from oracle_min / oracle_max below
    ("instead of {}", "plain_range", None),
    ("{} static instructions) in about 40 minutes", "pilot_instr", str),
    ("checked in {} CPU minutes", "check_cpu_min", f1),
    ("({} elapsed on two workers)", "check_elapsed_min", f1),
    ("about 50 hours of implementer time ({};", "hours_central", f1),
    ("{} at the pilot's rate", "hours_optimistic", f1),
    ("{} at a quarter of it", "hours_pessimistic", f1),
    ("{} CPU hours per task", "step_cpu_h", f2 := (lambda v: f"{v:.2f}")),
    ("({} hours elapsed on two workers)", "step_elapsed_h", f2),
    ("{} CPU hours for all eight", "steps_cpu_h", f1),
    ("{} CPU hours ({} elapsed) for the required distribution sheet", ("sheet_a_cpu_h", "sheet_a_elapsed_h"), f1),
    ("for about 7 hours", "option_d_hours", str),
    ("holds? {} proved whole matches", "proved_n", str),
    ("of {}-{} minutes each", ("proved_min_minutes", "proved_max_minutes"), str),
    ("and {} more stopped at a time limit", "proved_stopped", str),
    ("about 50 h ({}-{}) in eight tasks", ("hours_optimistic", "hours_pessimistic"), f1),
    ("{} CPU h each, plus {} CPU h for the required sheet", ("step_cpu_h", "sheet_a_cpu_h"), None),
    ("about 7 h: P0's tooling (3 h) and P6's image adapter (4 h)", None, None),
    ("takes {}\nmatches per arm; 0.5 goals takes {}", ("n25", "n50"), str),
    ("the measured {} CPU seconds an oracle match", "oracle_mean", f1),
    ("alone are {} matches, {} CPU hours ({} elapsed on two workers)", ("effect_matches", "effect_cpu_h", "effect_elapsed_h"), None),
    ("checked on 40 matches at {} s", "hooked_mean", f1),
    ("| 2,449 |", None, None),
    ("| {} | every leaf hooked at once: 40 of 40 identical | {} h |", ("instr_P1", "hours_central_P1"), None),
    ("| {} | the same, with P1's ports in | {} h |", ("instr_P2", "hours_central_P2"), None),
    ("| {} | the same | {} h |", ("instr_P3", "hours_central_P3"), None),
    ("| {} | the same; plus the frontier", "instr_P4", thousands),
    ("where one is cheap (S) | {} h |", "hours_central_P4", f1),
    ("| {} | from kick-off to full time", "instr_P5", thousands),
    ("40 of 40 identical | {} h |", "hours_central_P5", f1),
    ("| {} | identical on each start state", "instr_P7", thousands),
    ("| {} h (1 h of it preparing the start states) |", "hours_central_P7", f1),
    ("({} oracle matches in all)", "sheet_a_oracle", str),
    ("({} port matches)", "sheet_a_port", thousands),
    ("2 h of work; {} CPU h, {} h elapsed on two workers", ("sheet_a_cpu_h", "sheet_a_elapsed_h"), f1),
    ("at 0.25 goals, {} a arm: {} matches, {} CPU h, {} h elapsed", ("n25", "sheet_b25_matches", "sheet_b25_cpu_h", "sheet_b25_elapsed_h"), None),
    ("at 0.5 goals, {} a arm: {} matches, {} CPU h, {} h elapsed", ("n50", "sheet_b50_matches", "sheet_b50_cpu_h", "sheet_b50_elapsed_h"), None),
    ("{} CPU seconds an oracle match (the mean of 10", "oracle_mean", f1),
    ("{} s a hooked port match", "hooked_mean", f1),
    ("and {} s for a step's three falsifiers", "falsifier_set", f1),
    ("Total: {} hours of implementer time, for {} static instructions", ("hours_central", "instr_total"), None),
    ("({} instructions in 40 minutes, about {} an hour", ("pilot_instr", "pilot_rate"), str),
    ("the porting is {}\nhours and the whole {}", ("porting_optimistic", "hours_optimistic"), f1),
    ("{} hours of porting and {} fixed", ("porting_central", "fixed_hours"), None),
    ("the whole is {}.", "hours_pessimistic", f1),
    ("Per step, {} CPU hours ({} elapsed)", ("step_cpu_h", "step_elapsed_h"), f2),
    ("family checks of 40 matches ({} CPU minutes each)", "check_cpu_min", f1),
    ("{} CPU hours for the eight steps", "steps_cpu_h", f1),
    ("({} CPU minutes, {} elapsed)", ("review_cpu_min", "review_elapsed_min"), f1),
    ("a family check is {} CPU minutes ({} elapsed), a step {} CPU hours", ("check_cpu_min", "check_elapsed_min", "step_cpu_h"), None),
    ("the sheets ({} CPU hours for A, {}-{} for B)", ("sheet_a_cpu_h", "sheet_b50_cpu_h", "sheet_b25_cpu_h"), f1),
    ("about 7 hours (option D", None, None),
    ("{}-{} CPU seconds a match, as long as", ("oracle_min", "oracle_max"), f1),
    ("{} of {} matches unchanged", ("oracle_n", "oracle_n"), str),
    ("eight tasks of {}-{} hours", ("hours_P0", "hours_central_P5"), None),
    ("into an engine, at {}-{} CPU seconds", ("oracle_min", "oracle_max"), f1),
    ("then {}-{} CPU s a match", ("oracle_min", "oracle_max"), f1),
    ("(the pilot's hooked speed): {} CPU minutes", "check_cpu_min", f1),
    ("The family is {} matches", "family", str),
    ("its 3 falsifiers caught | {} h |", "hours_P0", str),
    ("its speed per match is stated | {} h |", "hours_P6", str),
    ("The oracle's {} matches on E011-r0001's state", "sheet_a_base", str),
    ("would have given {} s", "falsifier_at_hooked", f1),
    ("the {} minutes are my own account", "pilot_minutes", str),
]

DEFAULT_FMT = {"hours_central": f1, "instr_total": thousands, "fixed_hours": str, "porting_central": f1,
               "effect_matches": str, "effect_cpu_h": f1, "effect_elapsed_h": f1, "step_cpu_h": f2,
               "sheet_a_cpu_h": f1, "instr_P1": thousands, "instr_P2": thousands, "instr_P3": thousands,
               "hours_central_P1": f1, "hours_central_P2": f1, "hours_central_P3": f1, "n25": str, "n50": str,
               "sheet_b25_matches": thousands, "sheet_b50_matches": thousands, "sheet_b25_cpu_h": f1,
               "sheet_b50_cpu_h": f1, "sheet_b25_elapsed_h": f1, "sheet_b50_elapsed_h": f1,
               "check_cpu_min": f1, "check_elapsed_min": f1}


# numbers with a unit on the page that are not costs from the report: (a phrase around them, why)
NOT_COSTS = [
    ("10-15 h to write (an estimate, not measured)", "route B's writing time, stated on the page as an unmeasured estimate"),
    ("at 30 matches per arm", "E026's arm size, cited from F026, not a cost of this plan"),
    ("equals the harness on 40 of 40 matches", "an exit check's count (the family), not a cost"),
    ("ran to the 300 s limit", "pilot_movement.py's timeout_s, a script parameter the falsifier figure includes"),
]


def fold(s):
    return re.sub(r"\s+", " ", s)


def main():
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1])
        del args[i:i + 2]
        if out.exists():
            sys.exit(f"refused: {out} exists")
    J = json.loads(Path(args[0]).read_text())
    plan_path = Path(args[1]) if len(args) > 1 else ROOT / "docs/match-engine-plan.md"
    plan = fold(plan_path.read_text())
    J["plain_range"] = None
    lines, misses = [], 0
    for phrase, keys, fmt in CHECKS:
        if keys is None:
            text = phrase
        elif keys == "plain_range":
            text = phrase.format(f"{J['plain_min']}-{J['plain_max']}")
        else:
            ks = keys if isinstance(keys, tuple) else (keys,)
            vals = []
            for k in ks:
                if k not in J:
                    print(f"MISSING KEY {k}")
                    return 2
                if not isinstance(J[k], (int, float)) or isinstance(J[k], bool):
                    print(f"NOT A NUMBER {k}: {J[k]!r}")
                    return 2
                fm = fmt or DEFAULT_FMT.get(k, str)
                vals.append(fm(J[k]))
            text = phrase.format(*vals)
        if phrase.startswith("costs 8.3-16.8"):
            text = f"costs {J['oracle_min']}-{J['oracle_max']} CPU seconds"
        text = fold(text).replace("holds? ", "hold ")
        ok = text in plan
        misses += not ok
        lines.append(("ok   " if ok else "MISS ") + text)
    lines.append(f"{len(CHECKS)} phrases checked, {misses} missing")
    # the reverse check: every number with a cost unit on the page is inside a checked phrase or listed
    checked = [fold(l[5:]) for l in lines if l.startswith(("ok   ", "MISS "))]
    unit = re.compile(r"(?<![\w.:`-])(\d[\d,]*(?:\.\d+)?(?:-\d[\d,]*(?:\.\d+)?)?) ?(CPU hours|CPU h|CPU minutes|CPU "
                      r"seconds|CPU s|hours|minutes|matches|h|s)\b")
    uncovered = 0
    for m in unit.finditer(plan):
        tok = m.group(0)
        ctx = plan[max(0, m.start() - 40):m.end() + 40]
        if any(tok in c and c in plan and plan.find(c) <= m.start() < plan.find(c) + len(c) for c in checked):
            continue
        why = next((w for t, w in NOT_COSTS if t in ctx), None)
        if why:
            continue
        uncovered += 1
        lines.append(f"UNCOVERED {tok!r} in ...{ctx}...")
    lines.append(f"reverse check: {uncovered} cost figures not tied to the report")
    misses += uncovered
    report = "\n".join(lines) + "\n"
    print(report, end="")
    if out:
        out.write_text(report)
    return 1 if misses else 0


if __name__ == "__main__":
    sys.exit(main())
