#!/usr/bin/env python3
"""Check every E013 record against the predictor `runtime/model/keeping.py` (T27, Q012).

    python3 experiments/E013-q012-keeping/check_keeping.py

Cases per record, each counted once towards `match: N/N`:
1. the predicted keeper's keeping value — the value the model derives from the record bytes and
   the tables the run read at the half-time stall equals the prediction stored in the record
   (the runner computes it from the same bytes; a disagreement means the model and the runner
   disagree, i.e. two readings of the listing diverge);
2. the predicted save count — R2 fix: a STATE-DEPENDENT derivation, not an observed-outcome
   flag. The edited half-time savestate is downloaded from release E013 (the evidence bundle)
   and re-emulated by `runtime/emul/watched.py`; the save count is the number of writes of
   `0791:5A8E` (the `write_save_line` routine, template 0x1D = 29) the engine reaches in the
   second half. The predicted count must equal the record's count. For BOTH the LOW edit
   (`+4 = 0x00`) and the HIGH edit (`+4 = 0xFF`), the count is the emulated count: the
   round-3 review reproduced a path where zero-keeping still records saves via
   `5C44 → 4DA9 → 06FA → 5C69 → 5A8E`, so no analytical shortcut applies;
3. the predicted non-keeper-no-change — R2 fix: state-dependent, not unconditional. The
   edited half-time savestate is re-emulated; the predictor returns the edited (saves,
   goals) tuple and the check verifies (a) equality with the baseline's (saves, goals)
   and (b) the full line log equals the baseline's (every commentary event — saves,
   goals, bookings, injuries, own goals, etc. — must match; any other template change
   fails the check).

Every `saved by` line is checked to name a player of the conceding side (the read is open to
any challenger, F015).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
import keeping  # noqa: E402

RUNS = ROOT / "runs"
SAVE, GOAL = 29, 38
EVIDENCE = ROOT / "evidence" / "E013"
DL = ROOT / ".cache" / "E013"


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
        if "commentary lines seen" in k and "extent" in k:
            return int(v)
    raise KeyError("first-half extent")


def edit_desc(f):
    for k, v in f.items():
        if k.startswith("the I3 edit") or "the I3 edit" in k[:40]:
            return json.loads(v)
    raise KeyError("the I3 edit observation")


def halftime_sides_tables(f):
    for k, v in f.items():
        if k.startswith("half-time team-screen stall (before the edit)"):
            return json.loads(v)
    raise KeyError("the half-time stall observation")


def manifest_for(run_id):
    """The evidence manifest for an E013 run (the edited half-time savestate is its only
    file; the manifest records sha256 and size)."""
    p = EVIDENCE / f"{run_id}.manifest.json"
    if not p.is_file():
        raise SystemExit(f"{p}: no manifest; the evidence bundle for {run_id} is not on disk")
    return json.loads(p.read_text())


def fetch_evidence_asset(asset, sha256, size):
    """Download the half-time-edit savestate from release E013 (by exact asset name) and
    verify by sha256."""
    DL.mkdir(parents=True, exist_ok=True)
    path = DL / asset
    if not path.is_file():
        subprocess.run(
            ["gh", "release", "download", "E013", "--repo", "diegoami/goal2-archaeology",
             "--pattern", asset, "--dir", str(DL), "--clobber"],
            check=True,
        )
    data = path.read_bytes()
    import hashlib
    if len(data) != size or hashlib.sha256(data).hexdigest() != sha256:
        raise SystemExit(f"{path}: downloaded asset fails sha256/size check; the release is corrupt or the asset name is wrong")
    return data


def emulated_save_count(savestate_bytes):
    """R2 fix: a state-dependent derivation. Run the second half via the existing watch-engine
    emulator (runtime/emul/watched.py) and count 0791:5A8E writes (`write_save_line`,
    template 0x1D = 29, the `saved by` line). Returns the count; raises on a stray (the
    000E wait-family skip is wrong, the run is void)."""
    from watched import WatchedHalf
    half = WatchedHalf(savestate_bytes).run()
    if half.strays:
        raise SystemExit(f"000E wait family ran during emulation: {half.strays}; the skip is wrong, the run is void")
    return half.save_calls


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

    # 2. the second half against the same start state's E012 baseline
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

    # The half-time-edit savestate (the run's evidence asset) is what the emulated predictor
    # runs over: the edit is in place at the half-time stall, so the emulator's count is the
    # prediction the second half should match.
    manifest = manifest_for(d["run_id"])
    asset = manifest["files"][0]
    savestate_bytes = fetch_evidence_asset(asset["asset"], asset["sha256"], asset["bytes"])
    emu_count = emulated_save_count(savestate_bytes)
    notes.append(f"emulated save count for {d['run_id']}: {emu_count} (5A8E reaches in 0791:983F..98C0)")

    if desc["who"] == "keeper":
        # The count is state-dependent (the round-3 review showed an analytical shortcut for
        # edited_keeping == 0 misses the fallback path 5C44 → 4DA9 → 06FA → 5C69; we always
        # emulate). The emulated count is the truth; the record's count must match it.
        p = keeping.keeper_save_predictions(savestate_bytes, desc["new"], edited_keeping=desc["after"]["keeping"])
        cases.append((f"the predicted save count (emulated) equals the record's second-half saves",
                      p["saves_count"] == len(saves), f"emulated {p['saves_count']}, record {len(saves)}"))

    if desc["who"] == "outfield":
        p = keeping.outfield_edit_predictions(savestate_bytes, desc["new"],
                                              desc["before"]["keeping"], desc["after"]["keeping"])
        cases.append(("the predicted save count (emulated) equals the record's second-half saves",
                      p["saves_count"] == len(saves), f"emulated {p['saves_count']}, record {len(saves)}"))
        # R3 fix: the checker's non-keeper prediction CONSUMES the predictor's `event_counts`
        # and asserts equality with the baseline's event counts. The metric is
        # (saves, goals) — both the emulator and the record carry these in the same units.
        # (ticks is the clock reaches, not commentary events; line log != line count of
        # accepted entries; only saves/goals compare like-for-like.)
        # R6 fix: the LINE LOG itself is the gate too — every commentary event must match
        # the baseline line-for-line, not just saves/goals. A change to another template
        # (booking/injury/etc.) without a save/goal change now fails the check.
        counts = (len(second), sum(1 for l in second if l[1] == GOAL), len(saves))
        bcounts = (len(bsecond), sum(1 for l in bsecond if l[1] == GOAL), len(bsaves))
        pred_counts = (p["saves_count"], p["goal_count"])
        base_sav_goal = (len(bsaves), sum(1 for l in bsecond if l[1] == GOAL))
        cases.append(("the predicted non-keeper effect: predictor's (saves, goals) == baseline "
                      "(no comparison flipped)",
                      pred_counts == base_sav_goal,
                      f"predictor {pred_counts} vs baseline {base_sav_goal}"))
        # R6 follow-up: the line log equality is a GATE, not a diagnostic. Any template
        # other than saves/goals (e.g. booking, injury) must also match.
        first_diff = None
        for i, (a, b) in enumerate(zip(second, bsecond)):
            if a != b:
                first_diff = (i, a, b)
                break
        if first_diff is None and len(second) != len(bsecond):
            first_diff = (min(len(second), len(bsecond)),
                          second[-1] if second else None,
                          bsecond[-1] if bsecond else None)
        cases.append(("the predicted non-keeper effect: every commentary event matches the "
                      "baseline (line log equality)",
                      second == bsecond,
                      f"{len(second)} lines vs {len(bsecond)}; first diff: {first_diff}"))

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
