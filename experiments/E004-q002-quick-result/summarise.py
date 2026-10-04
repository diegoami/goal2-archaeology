#!/usr/bin/env python3
"""E004 (T10, Q002): tabulate the records of runs/E004. Interprets nothing beyond the recorded values.

    python3 experiments/E004-q002-quick-result/summarise.py [runs/E004]

1. Pairs (records of `run.py pairs`): per start state, the n-th quick result with the n-th watched
   match; per pair the final score (the scoreboard of the full-time screen), the events read from the
   commentary, DS:7B62 at full time, and whether the pair is identical (score, events, DS:7B62).
2. Replays: per start state and arm, each run against the first (score, all commentary lines,
   DS:7B62 at full time).
3. Sample (records of `run.py sample`): goals, bookings, sendings off and injuries per match per arm,
   (goals from the score bytes; the others from the commentary), and two tests of whether the arms differ per measure: a two-sided permutation test of the
   difference of means (arm labels shuffled, PERMUTATIONS times, random.Random(SEED)) and a two-sided
   paired sign-flip test over the DOS minutes both arms have.
4. Checks: aborted runs, goal lines followed by an offside line (disallowed; not counted), commentary gaps, the largest number of lines between two reads, goals counted
   from the commentary against the score bytes."""
import json
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs" / "E004"
PERMUTATIONS = 20000   # [designed] resolution 1/20000 of a p-value; the standard library's random only
SEED = 20261004        # [designed] any fixed value: makes the printed p-values reproducible
MEASURES = ("goals", "bookings", "sendings off", "injuries")
KIND = {"goal": "goals", "own goal": "goals", "booking": "bookings", "sending off": "sendings off", "injury": "injuries"}


def field(rec, start, step=None):
    for o in rec["observations"]:
        if o["field"].startswith(start) and (step is None or o["step"] == step):
            return o["value"]
    return None


def scoreboard(text):
    """('DENMARK', 0, 'SWEDEN', 1) from rows 1 and 3 of the match screen (columns 13-27 the team, 29-30 the goals)."""
    rows = text.split("\n")

    def side(r):
        line = rows[r].ljust(40)
        return line[13:28].rstrip("-").strip(), int(line[29:31]) if line[29:31].strip().isdigit() else None
    a, b = side(1), side(3)
    return a[0], a[1], b[0], b[1]


def load(path):
    rec = json.loads(path.read_text())
    r = {"id": rec["run_id"], "arm": rec["arm"].split("-")[0], "status": rec["status"], "kind": rec["actions"]["args"][0]}
    args = rec["actions"]["args"]
    r["state"] = args[args.index("--state") + 1] if "--state" in args else None
    r["minute"] = args[args.index("--dos-time") + 1] if "--dos-time" in args else None
    if r["status"] != "completed":
        return r
    text = field(rec, "full time: text screen rows 0-24")
    r["screen"] = field(rec, "full time: text screen 80x25")
    r["score"] = scoreboard(text)
    r["seed"] = field(rec, "full time: word at DS:7B62").split()[0]
    r["score_bytes"] = tuple(int(x) for x in field(rec, "full time: score bytes").split())
    r["events"] = json.loads(field(rec, "events among them"))
    r["lines"] = json.loads(field(rec, "commentary lines of the match"))
    gaps = json.loads(field(rec, "commentary lines between successive reads"))
    r["gaps"], r["max_delta"] = gaps["gaps"], max(gaps["deltas"] or [0])
    r["keys"] = json.loads(field(rec, "keys sent from the key"))
    r["reads"] = field(rec, "match: savestate reads")
    r["stats"] = stats_screen(text)
    r["text"] = text
    counts = defaultdict(int)
    for kind, _, _ in r["events"]:
        if kind in KIND:
            counts[KIND[kind]] += 1
    r["disallowed"] = disallowed(r["lines"])
    r["commentary_goals"] = counts["goals"] - len(r["disallowed"])
    # goals: the score bytes. The commentary can miss a goal: `0791:1D4A` does not write a record equal
    # to the newest one (`0791:1C78`, seg_0791_03.asm:817-835, 849-855), so two goals by one player
    # with no line between are one line (a quick result's commentary has few lines between goals).
    counts["goals"] = sum(r["score_bytes"])
    r["counts"] = {m: counts[m] for m in MEASURES}
    return r


def stats_screen(text):
    """{'Bookings': (a, b), 'Red cards': (a, b)} from a full-time statistics screen (watched matches), else {}."""
    import re
    out = {}
    for row in text.split("\n"):
        for label in ("Bookings", "Red cards"):
            if label in row:
                out[label] = tuple(int(x) for x in re.findall(label + r"\s+(\d+)", row))
    return out


def disallowed(lines):
    """Goal lines (templates 38, 39) whose next commentary line is template 54 (`... is OFFSIDE`): the
    goal does not count. Read from the records: in every such case the score bytes and the scoreboard
    count the goal out (`Checks` below compares the three counts)."""
    return [a for a, b in zip(lines, lines[1:]) if a[1] in (38, 39) and b[1] == 54]


def short(events):
    return "; ".join(f"{k} {t} {x}" for k, t, x in events) or "none"


def same(a, b, lines=False):
    keys = ("score", "events", "seed") + (("lines",) if lines else ())
    return all(a[k] == b[k] for k in keys)


def perm_test(xs, ys, rng):
    obs = abs(statistics.fmean(xs) - statistics.fmean(ys))
    pool, n, hits = xs + ys, len(xs), 0
    for _ in range(PERMUTATIONS):
        rng.shuffle(pool)
        if abs(statistics.fmean(pool[:n]) - statistics.fmean(pool[n:])) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (PERMUTATIONS + 1)


def sign_flip(diffs, rng):
    obs = abs(sum(diffs))
    hits = 0
    for _ in range(PERMUTATIONS):
        if abs(sum(d if rng.random() < 0.5 else -d for d in diffs)) >= obs - 1e-12:
            hits += 1
    return (hits + 1) / (PERMUTATIONS + 1)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    runs_dir = Path(argv[0]) if argv else RUNS
    recs = [load(p) for p in sorted(runs_dir.glob("E004-r*.json"))]
    done = [r for r in recs if r["status"] == "completed"]
    aborted = [r for r in recs if r["status"] != "completed"]

    print("## Pairs: quick result (Enter+r) against watched match, one start state")
    print("| state | pair | quick run | watched run | quick score | watched score | quick DS:7B62 | watched DS:7B62 | identical |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    by_state = defaultdict(lambda: defaultdict(list))
    for r in done:
        if r["kind"] == "pairs":
            by_state[r["state"]][r["arm"]].append(r)
    pair_rows = []
    for st in sorted(by_state):
        q, w = by_state[st]["quick"], by_state[st]["watched"]
        for i, (a, b) in enumerate(zip(q, w), 1):
            ident = same(a, b)
            pair_rows.append((st, i, a, b, ident))
            sc = lambda r: f"{r['score'][0]} {r['score'][1]} {r['score'][2]} {r['score'][3]}"
            print(f"| {st} | {i} | {a['id']} | {b['id']} | {sc(a)} | {sc(b)} | {a['seed']} | {b['seed']} | {'yes' if ident else 'no'} |")
    print()
    print("Events per pair (kind, engine team 0/1, commentary line):")
    for st, i, a, b, _ in pair_rows:
        print(f"- {st} pair {i} quick {a['id']}: {short(a['events'])}")
        print(f"- {st} pair {i} watched {b['id']}: {short(b['events'])}")
    print(f"\npairs identical: {sum(p[4] for p in pair_rows)} of {len(pair_rows)}")

    print("\n## Replays: each run of an arm from one state against the first (score, events, all commentary lines, DS:7B62, full-time screen)")
    print("| state | arm | first | replays | identical to the first |")
    print("| --- | --- | --- | --- | --- |")
    for st in sorted(by_state):
        for arm in ("quick", "watched"):
            rs = by_state[st][arm]
            if not rs:
                continue
            first = rs[0]
            verdict = [f"{r['id']} {'yes' if same(first, r, lines=True) and first['screen'] == r['screen'] else 'no'}" for r in rs[1:]]
            print(f"| {st} | {arm} | {first['id']} | {len(rs) - 1} | {', '.join(verdict) or '-'} |")

    sample = [r for r in done if r["kind"] == "sample"]
    if sample:
        print("\n## Sample: fresh launch per DOS minute, events per match")
        arms = {a: [r for r in sample if r["arm"] == a] for a in ("quick", "watched")}
        mins = {a: sorted({r["minute"] for r in rs}) for a, rs in arms.items()}
        print(f"quick: {len(arms['quick'])} matches over {len(mins['quick'])} DOS minutes; watched: {len(arms['watched'])} over {len(mins['watched'])}")
        print("| measure | quick mean (sd) | watched mean (sd) | quick per-match counts 0/1/2/3/4+ | watched counts 0/1/2/3/4+ | permutation p (means) | paired sign-flip p (minutes in both) |")
        print("| --- | --- | --- | --- | --- | --- | --- | ")
        both = sorted(set(mins["quick"]) & set(mins["watched"]))
        qm = {r["minute"]: r for r in arms["quick"]}
        wm = {r["minute"]: r for r in arms["watched"]}
        for m in MEASURES:
            xs = [r["counts"][m] for r in arms["quick"]]
            ys = [r["counts"][m] for r in arms["watched"]]
            if not (xs and ys):
                continue
            hist = lambda v: "/".join(str(sum(1 for x in v if (x == k if k < 4 else x >= 4))) for k in range(5))
            p = perm_test(list(xs), list(ys), random.Random(SEED))
            ps = sign_flip([qm[t]["counts"][m] - wm[t]["counts"][m] for t in both], random.Random(SEED)) if both else float("nan")
            sd = lambda v: statistics.stdev(v) if len(v) > 1 else 0.0
            print(f"| {m} | {statistics.fmean(xs):.2f} ({sd(xs):.2f}) | {statistics.fmean(ys):.2f} ({sd(ys):.2f}) | {hist(xs)} | {hist(ys)} | {p:.4f} | {ps:.4f} (n={len(both)}) |")
        same_min = sum(1 for t in both if same(qm[t], wm[t]))
        print(f"\nminutes where the quick result and the watched match are identical (score, events, DS:7B62): {same_min} of {len(both)}")

    print("\n## Checks")
    print(f"records: {len(recs)}; completed {len(done)}; aborted {len(aborted)}" + "".join(f"\n- aborted {r['id']} ({r['kind']} {r['arm']} {r['state'] or r['minute']}): {r['status']}" for r in aborted))
    gaps = [(r["id"], g) for r in done for g in r["gaps"]]
    print(f"commentary gaps (lines possibly lost between reads, or an end marker among new lines): {len(gaps)}" + "".join(f"\n- {i}: {g}" for i, g in gaps))
    if done:
        print(f"max lines between two reads: quick {max([r['max_delta'] for r in done if r['arm'] == 'quick'] or [0])}, watched {max([r['max_delta'] for r in done if r['arm'] == 'watched'] or [0])} (ring of 200)")
    bad = [r["id"] for r in done if sorted(r["score_bytes"]) != sorted(x for x in (r["score"][1], r["score"][3]))]
    stat_bad = []
    n_stat = 0
    for r in done:
        if r["stats"].get("Bookings") and r["stats"].get("Red cards"):
            n_stat += 1
            if (sum(r["stats"]["Bookings"]) != r["counts"]["bookings"] or sum(r["stats"]["Red cards"]) != r["counts"]["sendings off"]):
                stat_bad.append(f"{r['id']} (screen {r['stats']}, commentary {r['counts']['bookings']} bookings, {r['counts']['sendings off']} sendings off)")
    print(f"bookings and red cards of the full-time statistics screen (watched) against the commentary: {n_stat} screens, disagree in: {', '.join(stat_bad) or 'none'}")
    dis = [(r["id"], x[3]) for r in done for x in r["disallowed"]]
    print(f"goal lines followed by an offside line (not counted as goals): {len(dis)}" + "".join(f"\n- {i}: {t}" for i, t in dis))
    print(f"score bytes DS:9B3C/9B3D against the scoreboard (as a set of two numbers): disagree in {', '.join(bad) or 'none'}")
    fewer = [f"{r['id']} ({r['commentary_goals']} lines, {sum(r['score_bytes'])} goals)" for r in done if r["commentary_goals"] != sum(r["score_bytes"])]
    print(f"goal lines (less those followed by an offside line) against the score bytes: differ in {', '.join(fewer) or 'none'}")


if __name__ == "__main__":
    main()
