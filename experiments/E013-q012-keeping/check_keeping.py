#!/usr/bin/env python3
"""Check every E013 record against the predictor `runtime/model/keeping.py` (T27, Q012).

    python3 experiments/E013-q012-keeping/check_keeping.py

Cases per record, each counted once towards `match: N/N`:
1. the predicted keeper's keeping value — the value the model derives from the record bytes and
   the tables the run read at the half-time stall equals the prediction stored in the record
   (the runner computes it from the same bytes; a disagreement means the model and the runner
   disagree, i.e. two readings of the listing diverge);
2. the predicted save count — against the same start state's E012 baseline: the edited run's
   first half must be the baseline's first half (determinism, F005/F013), and then
   - a keeper edited to +4 = 0x00 keeps with value 0, so the second half's `saved by` count is
     strictly below the baseline's (the model's `keeper_save_predictions`);
   - any other edit predicts the second half's line log differs from the baseline's (every
     contest the edited player enters draws differently);
3. the non-keeper prediction — the outfield edit's effect: the second half is not the baseline
   replay (an event count changed), and every `saved by` line still names a player of the
   conceding side (the read is open to any challenger, F015).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import keeping  # noqa: E402

RUNS = ROOT / "runs"
SAVE, GOAL = 29, 38


def fields(record):
    out = {}
    for o in record["observations"]:
        out.setdefault(o.get("field", ""), o["value"])
    return out


def line_log(f):
    for k, v in f.items():
        if "commentary line log" in k:
            return json.loads(v)
    raise KeyError("commentary line log")


def halftime_extent(f):
    for k, v in f.items():
        if "lines seen (the first half's extent)" in k:
            return int(v)
    raise KeyError("first-half extent")


def edit_desc(f):
    for k, v in f.items():
        if k.startswith("the I3 edit"):
            return json.loads(v)
    raise KeyError("the I3 edit observation")


def halftime_sides_tables(f):
    for k, v in f.items():
        if k.startswith("half-time team-screen stall (before the edit)"):
            return json.loads(v)
    raise KeyError("the half-time stall observation")


def baseline_for(start_id):
    """The E012 record of the same start state (the unedited baseline; its r0002/r0003 are
    replays of r0001 — any of them serves)."""
    for p in sorted((RUNS / "E012").glob("E012-r*.json")):
        d = json.loads(p.read_text())
        if d["status"] == "completed" and d["start_state"]["id"] == start_id:
            return d
    raise SystemExit(f"no completed E012 record of start state {start_id}: the baseline is missing")


def check(record_path):
    d = json.loads(record_path.read_text())
    f = fields(d)
    cases, notes = [], []

    # 1. the predicted keeping value
    desc = edit_desc(f)
    ht = halftime_sides_tables(f)
    cls, prof = ht["tables"]["class"], ht["tables"]["profile"]
    side = next(s for s in ht["sides"] if s["side"] == desc["side"])
    rec = side["squadword1" if desc["who"] == "keeper" else "squadword2"]["record"]
    for tag, b4 in (("before", desc["old"]), ("after", desc["new"])):
        want = keeping.skill_value(b4, rec[5], rec[7], 1, cls, prof)
        cases.append((f"keeping value {tag} the edit (player {desc['player']}, +4 {b4}, +5 {rec[5]}, +7 {rec[7]})",
                      want == desc[tag]["keeping"], f"model {want}, record {desc[tag]['keeping']}"))
    if desc["who"] == "keeper" and desc["new"] == 0x00:
        cases.append(("the low edit floors the keeper's keeping at 0", desc["after"]["keeping"] == 0,
                      f"{desc['after']['keeping']}"))

    # 2/3. the second half against the same start state's E012 baseline
    base = baseline_for(d["start_state"]["id"])
    bf = fields(base)
    blog, bht = line_log(bf), halftime_extent(bf)
    log, ht_n = line_log(f), halftime_extent(f)
    first_ok = log[:ht_n] == blog[:bht]
    cases.append(("the first half is the baseline's (determinism; only the second half is edited)",
                  first_ok and ht_n == bht, f"{ht_n} lines vs the baseline's {bht}"))
    second, bsecond = log[ht_n:], blog[bht:]
    saves = [l for l in second if l[1] == SAVE]
    bsaves = [l for l in bsecond if l[1] == SAVE]
    if desc["who"] == "keeper" and desc["new"] == 0x00:
        p = keeping.keeper_save_predictions(len(bsaves), desc["new"])
        ok = len(saves) <= p["saves_at_most"]
        cases.append((f"the predicted save count: at most {p['saves_at_most']} (baseline {len(bsaves)})",
                      ok, f"{len(saves)} saves: {[l[2] for l in saves]} vs baseline {len(bsaves)}"))
    else:
        p = keeping.keeper_save_predictions(len(bsaves), desc["new"]) if desc["who"] == "keeper" \
            else keeping.outfield_edit_predictions()
        ok = second != bsecond
        cases.append(("the predicted changed second half (every contest the edited player enters draws differently)",
                      ok, f"second halves differ: {ok}"))
    if desc["who"] == "outfield":
        p = keeping.outfield_edit_predictions()
        counts = (len(second), sum(1 for l in second if l[1] == GOAL), len(saves))
        bcounts = (len(bsecond), sum(1 for l in bsecond if l[1] == GOAL), len(bsaves))
        cases.append(("the non-keeper's +4 edit changes watched event counts (no stored keeping exists to edit)",
                      counts != bcounts, f"lines/goals/saves {counts} vs baseline {bcounts}"))

    # every save names a player of the conceding side (the team byte of the save line)
    squads = {s["side"]: set(s["squad"]) for s in ht["sides"]}
    bad = [l for l in saves if l[2] not in squads[l[4]]]
    cases.append(("every `saved by` line names a squad player of the conceding side", not bad, f"{bad}"))
    notes.append(f"saves name players {[l[2] for l in saves]}; keepers of the sides are "
                 f"{[s['squadword1']['player'] for s in ht['sides']]}")
    return cases, notes


def main():
    paths = sorted((RUNS / "E013").glob("E013-r*.json"))
    if not paths:
        raise SystemExit("no E013 records under runs/E013")
    total = passed = 0
    for p in paths:
        d = json.loads(p.read_text())
        if d["status"] != "completed":
            print(f"{p.stem}: {d['status']} — skipped (not a completed record)")
            continue
        cases, notes = check(p)
        print(p.stem)
        for name, ok, detail in cases:
            total += 1
            passed += ok
            print(f"  [{'ok' if ok else 'FAIL'}] {name}: {detail}")
        for n in notes:
            print(f"    - {n}")
    print(f"match: {passed}/{total}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
