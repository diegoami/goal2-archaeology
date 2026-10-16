#!/usr/bin/env python3
"""E033 (PR 251 review R2): save() and Match.load() at every public event boundary, resumed = straight.

    python3 -B experiments/E033-original-match-kit/save_boundaries.py --log experiments/E033-original-match-kit/out/<new>.jsonl [--kit DIR]

Per scenario, a straight run saves at each boundary and plays on: the first event of every kind the run yields,
every decision before it is answered and again right after the answer, and the last event. Each saved match is then
loaded and played to its end with the same answers; its remaining events (kind, minute, score, data) and its result
(check.result_digest) must equal the straight run's. Scenarios: two fixtures (Denmark v 19 at 21 and at 40; and
goal2 managing country 19), a second seed and seeds with an injury and with sendings off, a pause with every kind of
answer and a refused eleven, a quick result, `tick` events. --kit DIR imports original_match from DIR."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = ("e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d", "e006-1000-r0001.sav")


def play_on(m, d):
    m.answer()


def everything(m, d):
    """A pause answered with every kind of answer and a substitution asked for; half time refused, then made."""
    if d["context"] == "pause" and d["minute"] < 40:
        pos = dict(d["positions"])
        other = m._squad(19 if m.opts["managed"] == 7 else 7)[:11]
        m.answer(tactics={4: not bool(d["tactics"] >> 3 & 1)}, positions={d["eleven"][5]: (pos[d["eleven"][5]] + 2) % 14},
                 marking={d["eleven"][3]: other[9], d["eleven"][0]: other[8]},   # the keeper: no marking row, refused
                 own_tactics={d["eleven"][7]: {1: True}}, substitutions=[(d["eleven"][10], d["bench"][7])])
    elif d["context"] == "half_time" and not d.get("refused"):
        keeper = next(w for w, p in d["positions"] if p == 0 and w in d["bench"])
        m.answer(substitutions=[(d["eleven"][9], keeper)])            # a second keeper: refused
    elif d["context"] == "half_time":
        outfield = next(w for w, p in d["positions"] if p != 0 and w in d["bench"])
        m.answer(substitutions=[(d["eleven"][0], outfield)])          # the first keeper off: accepted
    else:
        m.answer()


def injured(m, d):
    if d["context"] == "substitution" and d["injured"]:
        m.answer(substitutions=[(d["injured"][0], d["bench"][1])])
    else:
        m.answer()


def quick(m, d):
    m.answer(quick=True, speed=3) if d["context"] == "pause" else m.answer()


SCENARIOS = [
    ("Denmark v 19 at 21", {}, (), play_on),
    ("Denmark v 19 at 40, seed 0xE719", {"index": 40, "seed": 0xE719}, (), play_on),
    ("goal2 manages 19, at 21", {"managed": 19}, (), play_on),
    ("seed 70: an injury, its notice answered", {"seed": 70}, (), injured),
    ("go in hard, seed 4: sendings off", {"seed": 4, "go_in_hard": True}, (), play_on),
    ("every answer at a pause, a refused eleven", {}, (15, 60), everything),
    ("a quick result, tick events", {"ticks": True}, (30,), quick),
]


def make(kit, img, kw):
    kw = dict(kw)
    index = kw.pop("index", 21)
    if kw.pop("go_in_hard", False):
        countries = img.countries()
        rec = bytearray(countries[7])
        rec[0x2D] |= 1 << 3
        countries[7] = bytes(rec)
        kw["countries"] = countries
    return kit.Match(img, kit.Fixture(7, 19, index=index), **({"managed": 7} | kw))


def ev_record(ev):
    return json.dumps([ev.kind, ev.minute, list(ev.score), ev.data], sort_keys=True, default=str)


def drive(m, policy, pause_at, on_event=None, start=0):
    """Play m to its end; returns the event records. on_event(i, ev, phase) may save ('event', 'answered')."""
    out, paused = [], set()
    i = start
    if m.waiting is not None:                       # loaded at a decision not yet answered
        policy(m, m.waiting | {"minute": m.minute})
        if on_event:
            on_event(i - 1, None, "answered")
    for ev in m.events():
        out.append(ev_record(ev))
        if ev.kind == "minute" and ev.minute in pause_at and ev.minute not in paused:
            paused.add(ev.minute)
            m.pause()                               # the client's reaction first: a save below holds it
        if on_event:
            on_event(i, ev, "event")
        if ev.kind == "decision":
            policy(m, ev.data | {"minute": ev.minute})
            if on_event:
                on_event(i, ev, "answered")
        i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--kit", default=str(ROOT / "runtime"))
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    sys.path.insert(0, a.kit)
    sys.path.insert(1, str(ROOT / "runtime"))
    import original_match as kit
    from original_match.check import result_digest
    data = (ROOT / ".cache/dl" / f"{IMAGE[0][:16]}-{IMAGE[1]}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == IMAGE[0]
    img = kit.Image.from_savestate(data)
    failures = 0
    with open(log, "x") as out:
        for name, kw, pause_at, policy in SCENARIOS:
            t = time.time()
            m = make(kit, img, kw)
            saves, first_kind = [], set()

            def on_event(i, ev, phase, m=m):
                if phase == "event" and (ev.kind not in first_kind or ev.kind in ("decision", "end")):
                    first_kind.add(ev.kind)
                    saves.append({"at": i, "kind": ev.kind, "phase": phase, "blob": try_save(m)})
                elif phase == "answered":
                    saves.append({"at": i, "kind": "decision", "phase": phase, "blob": try_save(m)})
            straight = drive(m, policy, pause_at, on_event)
            want = result_digest(m.result())
            rows = []
            for s in saves:
                row = {"at": s["at"], "kind": s["kind"], "phase": s["phase"]}
                if isinstance(s["blob"], str):
                    row["error"] = s["blob"]
                else:
                    try:
                        r = kit.Match.load(s["blob"])
                        rest = drive(r, policy, pause_at, start=s["at"] + 1)
                        row["events_equal"] = rest == straight[s["at"] + 1:]
                        row["result_equal"] = result_digest(r.result()) == want
                    except Exception as e:      # noqa: BLE001 - recorded, the scenario fails
                        row["error"] = f"{type(e).__name__}: {e}"
                rows.append(row)
            bad = [r for r in rows if r.get("error") or not (r.get("events_equal") and r.get("result_equal"))]
            failures += bool(bad)
            rec = {"scenario": name, "pass": not bad, "events": len(straight), "boundaries": len(rows),
                   "kinds": sorted({r["kind"] for r in rows}), "failures": bad, "rows": rows,
                   "wall_s": round(time.time() - t, 1)}
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{name:42s} {'PASS' if not bad else 'FAIL'} {rec['wall_s']:6.1f} s  {len(rows)} boundaries over "
                  f"{len(rec['kinds'])} kinds {rec['kinds']}" + (f"\n    {json.dumps(bad)[:500]}" if bad else ""), flush=True)
    sys.exit(1 if failures else 0)


def try_save(m):
    try:
        return m.save()
    except Exception as e:                      # noqa: BLE001 - a refused save is a failure of the boundary
        return f"{type(e).__name__}: {e}"


if __name__ == "__main__":
    main()
