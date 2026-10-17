#!/usr/bin/env python3
"""E036: the size of each task of the watched-engine backlog (docs/tasks/T57.md .. T80.md), from the static tables.

    python3 -B experiments/E036-match-port/sizes.py experiments/E036-match-port/out/backlog/<new>.md

Static only: no run of the game, no original byte read (routines.tsv, calls.tsv and annotations/routines.tsv are
derived extracts, rule 18; E032's coverage runs say which routines a match reached between kick-off and full time).
Writes <new>.md and <new>.json beside it; both refused if they exist.

The universe is what the original-match kit runs as the original's code: the static call closure of run_match
`0791:F1F6` and of the post-match update `0791:B7FA` (runtime/original_match/README.md), every segment included.
Every routine of it is assigned below to exactly one task or to OUT with a reason; an unassigned, doubly assigned or
unknown routine is an error (exit 1). Hours: a porting task is its static instructions at a share of the E032
pilot's pace, plus PER_TASK hours for its checks, tests, annotations and PR, plus any EXTRA; the other tasks are
FIXED estimates. Elapsed time: the tasks scheduled on two workers in task order, each as soon as its dependencies
have merged. Every figure that is not counted is named in ASSUMED and printed with the report."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E032-match-engine-inventory"))
import record_schema  # noqa: E402  (strict JSON: no NaN, no duplicate keys)

E032 = ROOT / "experiments/E032-match-engine-inventory/out"
COVERAGE = ["cov-s1234-20261015.json"] + [f"cov-d20-{s}-20261015.json"
                                          for s in ("0x1234", "0x2345", "0x4c1d", "0xc3c3", "0xe719")]
ROOTS = ("0791:F1F6", "0791:B7FA")
WORKERS = 2

ASSUMED = {
    "PILOT_RATE": (555 / (40 / 60), "static instructions an hour at the E032 pilot's pace (E032 notes: 40 minutes, "
                   "self-reported, not logged)"),
    "RATES": ({"optimistic": 1.0, "central": 0.5, "pessimistic": 0.25},
              "the share of the pilot's pace the rest of the engine allows (the plan's three rates)"),
    "PER_TASK": (1.0, "hours a porting task spends beyond porting: its family checks, unit tests, annotation rows, "
                 "the regenerated named view and the PR"),
    "FIXED": ({"T57": 4, "T58": 5, "T59": 5, "T73": 4, "T78": 5, "T79": 3, "T80": 4},
              "estimates of the tasks that are tooling, classification, assembly or measurement, not porting"),
    "EXTRA": ({"T76": 1, "T77": 1}, "hours a porting task adds: T76 the kit's set-piece taker decision (E033 notes: "
              "about 1 h), T77 finding the start states that reach the frontier (the plan's P7 hour)"),
    "WORKERS": (WORKERS, "tasks at once: the machine allows two workers"),
}


def r(seg, *offs):
    return [f"{seg}:{o}" for o in offs]


TASKS = {   # task: (plan step, title, merge after, routines)
    "T57": ("P0a", "seed families and the fail-closed comparison on the kit", [], []),
    "T58": ("P0b", "the port mode in the kit, with the E032 pilot moved in", [],
            r("0791", "8889", "86D0", "2BE5", "2974", "045D", "2CC5", "2DCA") + r("23E4", "08DF")
            + r("214B", "0688", "06B1", "06FA")),
    "T59": ("P0c", "guest calls, a decision under a port, and the divergence locator", ["T57", "T58"],
            r("0791", "6E11")),
    "T60": ("P1a", "the runtime primitives and the geometry queries", ["T59"],
            r("0791", "261A", "26A0", "26C2", "26D7", "278A", "287C", "28B2", "2929", "2956", "2996", "29B3", "2A15",
              "2A6D", "2AA3", "2AD4", "2B0F", "2B28", "2B51", "2B7B", "2BB1", "2C29", "2C54", "2C86", "2CEC", "2D10",
              "2D6D", "2E00", "2E36", "2E82", "2EB8", "2EF0", "2F28")
            + r("214B", "0000", "0018", "003C", "007B", "009C", "0147", "0329", "05DB", "05F0", "06D0", "09DA", "0C57",
                "0C79", "0CA1", "0CCB", "0CF4", "0D1C", "0D56", "1C86", "1D6F", "2000", "2031")
            + r("23E4", "025D", "0279", "0294", "062A", "0644", "0676", "06B7", "06E3", "072F", "075A", "0787", "07DB",
                "08BF", "11E4", "12F6", "19B2")),
    "T61": ("P1b", "the player attributes (1771)", ["T59"],
            r("1771", "0AA7", "0B77", "0E24", "0E6C", "2E20", "2E93", "2FAD", "2FFB", "3041", "3088", "30D9", "3179",
              "3216", "33CD", "3431", "34E7", "377E", "3A06", "3A82", "3E2F", "3EF8", "5A03")),
    "T62": ("P2a", "ball and player motion, the offside line and the referee", ["T59"],
            r("0791", "835F", "83A2", "8537", "869F", "8AE9", "8C67", "8CCA", "8CF5", "8E24", "90C5", "9119")),
    "T63": ("P2b", "positioning, marking and the leaders", ["T59"],
            r("0791", "1F3C", "1FDD", "20E3", "2218", "419C", "42CB", "4354", "4438", "44C1", "4532", "4649", "474D",
              "47C5", "4A28", "4B64", "4D3F")),
    "T64": ("P3a", "the ball: passing, launching and shooting", ["T59"],
            r("0791", "2FB1", "30EA", "3111", "3323", "333F", "34C1", "384C", "3B15", "3B9E", "3BEE", "3C20", "3C3F",
              "3D38", "3DF6", "3EC5", "3EDF", "3EF8", "3FAD", "408E", "40BC", "4151")),
    "T65": ("P3b", "the holder's decisions and the contests", ["T59"],
            r("0791", "4DA9", "4E28", "500C", "5049", "533B", "539F", "5474", "5513", "5565", "56D9", "5729", "57AC",
              "58E1", "593B", "59B3", "5A33", "5A8E")),
    "T66": ("P4a", "duels, play at the ball, the goal and the after-goal swing", ["T59"],
            r("0791", "5B36", "5E41", "5EAB", "5F06", "5F8A", "6188", "61EC", "6240", "6337", "6443", "65A4", "65FE",
              "6755", "67B6")),
    "T67": ("P4b", "kick-offs, restarts and set pieces, the walk-off and the booking", ["T59"],
            r("0791", "690C", "698E", "69BD", "6AAD", "6AF7", "6B65", "6BF1", "6D4E", "6DEA", "6E6E", "6F01", "6F3E",
              "6FB6", "6FEE", "7069", "70F6", "715A", "717F", "71E8", "7287", "74C2", "7621", "7881", "798D", "7A43")),
    "T68": ("P5a", "fouls, cards, injuries and form; substitutions and the computer manager in play", ["T59"],
            r("0791", "7CC5", "7D56", "7E60", "7EEF", "8062", "8206", "82EB", "A260", "A2E6", "A920", "A9B8", "AAE8",
              "BBFF", "BD03", "BD83", "BF6B", "C173", "C5DC", "C7EB", "C88D")),
    "T69": ("P5b", "the commentary and the match frame (9564 to play_match)", ["T59"],
            r("0791", "1829", "1C78", "1D4A", "1E53", "1EB5", "230C", "9564", "970C", "97D0", "983F", "98C4", "9955",
              "998C", "9A32", "F098")),
    "T70": ("P5c", "the per-match set-up (A4A1 and what it reaches)", ["T59"],
            r("0791", "A4A1", "1073", "A375", "A3B6", "A3DE", "A6E4", "A841", "2648", "AC67", "AD8F", "AFA3", "B11F",
              "D44C") + r("1771", "517A", "52CC", "580B")),
    "T71": ("P5d", "run_match and its tail: the man of the match, the group tables, D050, the tactics reset",
            ["T59"],
            r("0791", "F1F6", "CAB0", "CB7D", "BC5D", "D050", "D016", "D032", "E929")
            + r("1771", "8757", "82BD", "85F7", "59D8")),
    "T72": ("P5e", "the post-match update B7FA and the pool update BA4E", ["T59"],
            r("0791", "B7FA", "B6CC", "B71C", "BA4E", "B27F", "B364")
            + r("1771", "10E7", "3558", "3651", "5A38", "5A8F", "5C60")),
    "T73": ("UI-a", "the display boundary: what is drawn, sounded or waited for, removed or stubbed", ["T59"],
            r("0791", "0000", "006C", "0106", "0425", "0441", "0481", "04C9", "054C", "05C6", "0691", "0712", "0C65",
              "15B9", "8F10", "9079", "94C9", "94E8", "A699", "A75D", "C50C")
            + r("1771", "0947", "0AF8", "0F58", "0FB1", "11E1", "1289", "13D0", "1527", "157D", "2EE5", "2F37", "3827",
                "3947", "3AE2", "3B3F", "3BD3", "42BC", "4D8A", "4E22", "50F1", "5AC4", "5C94", "5CCB", "76FA", "77C3",
                "883F", "8939", "89C1", "89FE", "8A5D", "8A87", "8CA2", "8CCF", "8D84", "8E9A", "9028", "91CE", "937C",
                "9509", "958D")
            + r("214B", "00DB", "00FF", "0123", "01A3", "0205", "026D", "02C8", "0350", "0625", "0643", "0661", "0755",
                "13C5", "1E09", "1E5A", "1E75", "1E8D", "1EA1", "1EBC", "1EF1", "1F87")
            + r("2382", "0099", "00E7", "016D", "0215", "04FC", "0608")),
    "T74": ("UI-b", "the manager's decisions in play: the key poll, the team menu, tactics, positions, marking",
            ["T59"],
            r("0791", "9372", "92FC", "ED8A", "7FCF") + r("1771", "1981", "4859", "4925", "4952", "49B8", "4B61")
            + r("214B", "04F8", "0566", "0723", "08DD", "0983", "0993", "09A7", "13F6", "1452", "14AC", "1507", "1560",
                "158E", "15B1", "1765") + r("235C", "0000", "000B")),
    "T75": ("UI-c", "the manager's substitutions: SELECT TEAM, the swap and the eleven's check", ["T74"],
            r("0791", "E44F", "E022", "DEA6", "EA09", "E949", "DAF8", "DB38", "DBFA", "DC7E", "DDCB", "DE27", "DE51",
              "E2A0", "E2E6") + r("1771", "4FAA", "53E8", "5532", "55FC")),
    "T76": ("P7a", "the takers and the shoot-out: the captain and set-piece prompts, the yes/no questions, extra "
                   "time, the order and the kicks", ["T75"],
            r("0791", "CC7B", "CC2E", "0B7C", "9B0C", "9B5B", "A10A", "0C0B", "9B93", "9ED3", "A006")),
    "T77": ("P7b", "the paths a plain match does not reach: the quick result from a pause, penalties, sendings "
                   "off, the frontier; the family that reaches them", ["T59"],
            r("0791", "D733", "D5C1", "B19D", "6ECF", "73BA", "72F2", "7B77", "7B24", "B3B7", "C01A", "C0DF", "C48D",
              "BEC7", "C24D", "C2A8", "C406") + r("1771", "0BC4")),
    "T78": ("P6", "the engine on its own: no Unicorn",
            ["T60", "T61", "T62", "T63", "T64", "T65", "T66", "T67", "T68", "T69", "T70", "T71", "T72", "T73", "T74",
             "T75", "T76", "T77"], []),
    "T79": ("sheet A", "the fidelity sheet: the original's distributions, and the port's against them", ["T78"], []),
    "T80": ("end", "the end state sealed: no GOAL.EXE bytes at run time", ["T78", "T79"], []),
}

OUT = {   # routine: why it is not ported (the kit never runs it, or it is not the match's)
    **{a: "the help viewer (GOAL.HLP), reached only by a key the decision API never sends" for a in r(
        "16D6", "0000", "0025", "0068", "00C3", "00FE", "01BC", "01F6", "0266", "02FB", "032F", "0349", "036D", "03C7",
        "03F9", "04C3", "055E", "05E7", "065F", "06E7", "0774", "0793", "0828", "0842", "08C5", "0910", "0945")},
    **{a: "saving a goal or the summary to disk and its file-name editor: only after a Yes, which the kit never "
          "answers (F030)" for a in r("0791", "0955", "09C4", "0A6B")
       + r("214B", "0D90", "0E41", "0FB5", "1086", "1869", "19B3", "19F4", "1A36", "1A5F", "1AD1", "1B47", "1BB7", "1BF5")
       + r("23E4", "0194", "01A2", "01AE", "01BC", "01C3", "01CE", "01D6", "0207", "125E", "1341", "143B", "1476",
           "1631", "1655", "16BE", "173B", "1779", "17B0", "1828", "184D", "1899")},
    **{a: "the action replay's playback: only after a Yes, which the kit never answers (F029, F030)"
       for a in r("0791", "0776", "07BA")},
    **{a: "a view the decision API never opens (the in-play poll's Up/Down and Space keys)" for a in r("0791", "1A04")},
    **{a: "printing and the DOS shell from a menu: never chosen by the decision API" for a in r(
        "214B", "0813", "0AB9", "0B4D") + r("235C", "0159", "01F2")},
    **{a: "the heap and the halt: the Turbo Pascal runtime's, used by code outside a match" for a in r(
        "23E4", "00D8", "0329", "0341", "038C", "041D", "04D8", "058B", "05AF", "05C4", "060D", "061B")},
    **{a: "six-byte Real arithmetic: called only by the music (214B:1EF1) and the file name's Val (0A6B)"
       for a in r("23E4", "098B", "098F", "0A52", "0B57", "0BF8", "0C37", "0C93", "0CA5", "0CAB", "0CB9", "0CC5",
                  "0CDF", "0E67", "0F10", "10E8", "1101")},
}


def tsv(path):
    for line in path.read_text().splitlines():
        if line and not line.startswith(";"):
            yield line.split("\t")


def schedule(hours, deps):
    """Two workers, tasks in index order, each started as soon as a worker is free and its dependencies have
    finished; returns {task: (start, end)} and the elapsed total."""
    free = [0.0] * WORKERS
    done, plan, pending = {}, {}, list(hours)
    while pending:
        ready = [t for t in pending if all(d in done for d in deps[t])]
        if not ready:
            raise SystemExit(f"dependency cycle among {pending}")
        t = ready[0]
        w = min(range(WORKERS), key=lambda i: free[i])
        start = max(free[w], max((done[d] for d in deps[t]), default=0.0))
        end = start + hours[t]
        free[w], done[t], plan[t] = end, end, (round(start, 1), round(end, 1))
        pending.remove(t)
    return plan, round(max(done.values()), 1)


def longest_chain(hours, deps):
    memo = {}

    def finish(t):
        if t not in memo:
            memo[t] = hours[t] + max((finish(d) for d in deps[t]), default=0.0)
        return memo[t]
    return round(max(finish(t) for t in hours), 1)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    dest = Path(sys.argv[1])
    jdest = dest.with_suffix(".json")
    if dest.exists() or jdest.exists():
        sys.exit(f"refused: {dest} or {jdest} exists")
    info, calls, names = {}, {}, {}
    for f in tsv(ROOT / "static/goal-exe/routines.tsv"):
        if f[0] != "segment:offset":
            info[f[0]] = int(f[2])
    for f in tsv(ROOT / "static/goal-exe/calls.tsv"):
        if f[0] != "caller":
            calls.setdefault(f[0], set()).add(f[1])
    for f in tsv(ROOT / "static/goal-exe/annotations/routines.tsv"):
        if f[0] != "address":
            names[f[0]] = f[1]
    reached = set()
    for name in COVERAGE:
        run = record_schema.loads((E032 / name).read_text())
        if run.get("error") or not run.get("stopped_at_board"):
            sys.exit(f"refused: {name} is not a completed coverage run")
        reached |= {row["address"] for row in run["routines"] if row["exec_match"] > 0}
    universe, stack = set(), list(ROOTS)
    while stack:
        a = stack.pop()
        if a in universe:
            continue
        universe.add(a)
        stack.extend(sorted(calls.get(a, ())))
    owner, problems = {}, []
    for t, (_, _, deps, rs) in TASKS.items():
        problems += [f"{t} depends on unknown {d}" for d in deps if d not in TASKS]
        for a in rs:
            if a in owner:
                problems.append(f"{a} assigned to {owner[a]} and {t}")
            owner[a] = t
    for a in OUT:
        if a in owner:
            problems.append(f"{a} assigned to {owner[a]} and OUT")
        owner[a] = "OUT"
    problems += [f"{a} is not a routine of routines.tsv" for a in owner if a not in info]
    problems += [f"{a} ({names.get(a, '')}) is in the universe and assigned to nothing" for a in sorted(universe)
                 if a not in owner]
    problems += [f"{a} is assigned but outside the universe of {' and '.join(ROOTS)}" for a in sorted(owner)
                 if a not in universe]
    problems += [f"{a} was reached by E032's coverage but is outside the universe" for a in sorted(reached - universe)
                 if a.startswith(("0791", "1771"))]
    rate = ASSUMED["PILOT_RATE"][0]
    rows, J = [], {"assumed": {k: v[1] for k, v in ASSUMED.items()}, "tasks": {}, "out": {}}
    hours = {label: {} for label in ASSUMED["RATES"][0]}
    for t, (step, title, deps, rs) in TASKS.items():
        instr = sum(info.get(a, 0) for a in rs)
        h = {}
        for label, f in ASSUMED["RATES"][0].items():
            if t in ASSUMED["FIXED"][0]:
                h[label] = float(ASSUMED["FIXED"][0][t])
            else:
                h[label] = round(instr / (rate * f) + ASSUMED["PER_TASK"][0] + ASSUMED["EXTRA"][0].get(t, 0), 1)
            hours[label][t] = h[label]
        n_reached = sum(1 for a in rs if a in reached)
        rows.append((t, step, title, deps, len(rs), instr, n_reached, h))
        J["tasks"][t] = {"step": step, "title": title, "merge_after": deps, "routines": rs, "instructions": instr,
                         "reached_kickoff_to_full_time": n_reached, "hours": h}
    deps = {t: v[2] for t, v in TASKS.items()}
    elapsed = {}
    for label in ASSUMED["RATES"][0]:
        plan, total = schedule(hours[label], deps)
        elapsed[label] = {"two_workers_hours": total, "longest_chain_hours": longest_chain(hours[label], deps),
                          "plan": plan}
    out_instr = sum(info.get(a, 0) for a in OUT)
    J["out"] = {"routines": len(OUT), "instructions": out_instr, "why": sorted(set(OUT.values()))}
    J["universe"] = {"routines": len(universe), "instructions": sum(info[a] for a in universe)}
    J["elapsed"] = elapsed
    J["problems"] = problems
    L = ["# E036 the watched-engine backlog by task: routines, static instructions, hours", "",
         f"Universe: the static call closure of {' and '.join(ROOTS)} (what the kit runs as the original's code): "
         f"{len(universe)} routines, {J['universe']['instructions']:,} static instructions. Reached between kick-off "
         f"and full time: E032's six coverage runs ({', '.join(COVERAGE)}).", "", "## Assumptions (not counted)", ""]
    L += [f"- {k} = {v[0]!r}: {v[1]}" for k, v in ASSUMED.items()]
    L += ["", "## Tasks", "", "| task | step | what | merge after | routines | static instructions | reached kick-off "
          "to full time | hours optimistic | central | pessimistic |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for t, step, title, dp, n, instr, nr, h in rows:
        L.append(f"| {t} | {step} | {title} | {', '.join(dp) or '-'} | {n} | {instr:,} | {nr} | {h['optimistic']} | "
                 f"{h['central']} | {h['pessimistic']} |")
    tot = {k: round(sum(rw[7][k] for rw in rows), 1) for k in ASSUMED["RATES"][0]}
    J["total_hours"] = tot
    L += [f"| all | | | | {sum(rw[4] for rw in rows)} | {sum(rw[5] for rw in rows):,} | {sum(rw[6] for rw in rows)} | "
          f"{tot['optimistic']} | {tot['central']} | {tot['pessimistic']} |", "",
          f"OUT (not ported, each with its reason): {len(OUT)} routines, {out_instr:,} static instructions.", ""]
    L += [f"- {w}" for w in sorted(set(OUT.values()))]
    L += ["", "## Elapsed on two workers", "",
          "| rate | work (hours) | elapsed, two workers in task order | longest dependency chain |",
          "| --- | --- | --- | --- |"]
    for label, e in elapsed.items():
        L.append(f"| {label} | {tot[label]} | {e['two_workers_hours']} | {e['longest_chain_hours']} |")
    L += ["", "Start and end of each task at the central rate (hours from the start): " + ", ".join(
        f"{t} {s}-{e}" for t, (s, e) in elapsed["central"]["plan"].items()), "", "## Routines per task", ""]
    for t, (step, title, dp, rs) in TASKS.items():
        if rs:
            L.append(f"- {t}: " + ", ".join(f"{a}{' ' + names[a] if names.get(a) else ''}"
                                            f"{'' if a in reached else ' (not reached)'}" for a in rs))
    L += ["", "## Problems", ""] + ([f"- {p}" for p in problems] or ["none"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(L) + "\n")
    jdest.write_text(json.dumps(J, indent=1, sort_keys=True) + "\n")
    print(f"{dest}: {len(TASKS)} tasks, {len(problems)} problems; hours {tot}; elapsed "
          f"{ {k: v['two_workers_hours'] for k, v in elapsed.items()} }")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
