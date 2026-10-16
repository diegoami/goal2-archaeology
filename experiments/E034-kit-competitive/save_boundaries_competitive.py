#!/usr/bin/env python3
"""E034: save() and Match.load() at every public event boundary of competitive fixtures, resumed = straight.

    python3 -B experiments/E034-kit-competitive/save_boundaries_competitive.py --log experiments/E034-kit-competitive/out/<new>.jsonl [--kit DIR]

E033's save_boundaries.py (its drive and try_save) on competitive scenarios: a straight run saves at the first
event of every kind it yields (extra_time, shootout and shootout_kick included), at every decision before its
answer and right after it (extra_time halves 1 and 2, shootout_order), and at the last event; each saved match is
loaded and played to its end with the same answers; its remaining events (kind, minute, score, data) and its
result (check.competitive_digest) must equal the straight run's. Scenarios: the knockout worked example (index 39,
budget 5, goal2's answers), kind 200 index 42 watched (penalties to sudden death), kind 200 index 9 as a quick
result from half time (24 kicks)."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E033-original-match-kit"))
import save_boundaries as E033  # noqa: E402

IMAGE = E033.IMAGE


def play_on(m, d):
    m.answer()


def quick_at_half_time(m, d):
    m.answer(quick=True) if d["context"] == "half_time" else m.answer()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--kit", default=str(ROOT / "runtime"))
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    sys.path.insert(0, a.kit)
    import original_match as kit
    from original_match import example
    from original_match.check import competitive_digest
    data = (ROOT / ".cache/dl" / f"{IMAGE[0][:16]}-{IMAGE[1]}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == IMAGE[0]
    img = kit.Image.from_savestate(data)
    ko = lambda m, d: example.knockout_answer(m, d, lambda *x: None)  # noqa: E731
    scenarios = [("knockout example (39, budget 5)", 39, 5, ko), ("kind 200, 42, watched", 42, None, play_on),
                 ("kind 200, 9, quick from half time", 9, None, quick_at_half_time)]
    failures = 0
    with open(log, "x") as out:
        for name, index, budget, policy in scenarios:
            t = time.time()

            def make():
                return kit.Match(img, kit.Fixture(7, 19, index=index, kind=200), managed=7, substitutions=budget)
            m = make()
            saves, first_kind = [], set()

            def on_event(i, ev, phase, m=m):
                if phase == "event" and (ev.kind not in first_kind or ev.kind in ("decision", "end")):
                    first_kind.add(ev.kind)
                    saves.append({"at": i, "kind": ev.kind, "phase": phase, "blob": E033.try_save(m)})
                elif phase == "answered":
                    saves.append({"at": i, "kind": "decision", "phase": phase, "blob": E033.try_save(m)})
            straight = E033.drive(m, policy, (), on_event)
            want = competitive_digest(m.result())
            rows = []
            for s in saves:
                row = {"at": s["at"], "kind": s["kind"], "phase": s["phase"]}
                if isinstance(s["blob"], str):
                    row["error"] = s["blob"]
                else:
                    try:
                        r = kit.Match.load(s["blob"])
                        rest = E033.drive(r, policy, (), start=s["at"] + 1)
                        row["events_equal"] = rest == straight[s["at"] + 1:]
                        row["result_equal"] = competitive_digest(r.result()) == want
                    except Exception as e:      # noqa: BLE001 - recorded, the scenario fails
                        row["error"] = f"{type(e).__name__}: {e}"
                rows.append(row)
            bad = [r for r in rows if r.get("error") or not (r.get("events_equal") and r.get("result_equal"))]
            failures += bool(bad)
            contexts = [json.loads(e)[3].get("context") for e in straight if json.loads(e)[0] == "decision"]
            rec = {"scenario": name, "pass": not bad, "events": len(straight), "boundaries": len(rows),
                   "kinds": sorted({r["kind"] for r in rows}), "decisions": contexts, "failures": bad, "rows": rows,
                   "wall_s": round(time.time() - t, 1)}
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{name:36s} {'PASS' if not bad else 'FAIL'} {rec['wall_s']:6.1f} s  {len(rows)} boundaries, kinds "
                  f"{rec['kinds']}, decisions {contexts}" + (f"\n    {json.dumps(bad)[:500]}" if bad else ""), flush=True)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
