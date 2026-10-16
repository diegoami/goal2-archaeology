#!/usr/bin/env python3
"""E034: the stamps check of E033 (stamps.py) on competitive fixtures, with the hooks extra time and the shoot-out
need, installed by this script on the kit's machine, independent of the kit's event path.

    python3 -B experiments/E034-kit-competitive/stamps_competitive.py --log experiments/E034-kit-competitive/out/<new>.jsonl [--kit DIR]

E033's Independent (its write hooks on the commentary counter, the score bytes, the statistics, the substitutions
left, the minute word, the board's key read, the quick engine) plus:
- code hook 0791:9B15 (9B0C's `mov word [831F], 0x59`): extra time begins, (0x59, score); the minute write it makes
  next is not a `minute` event but this one (the clock set back for extra time, F098 named seg_0791_12.c);
- code hook 0791:A10A (penalty_shootout's entry): the shoot-out begins, (minute, score); from here to play_match's
  return a +1 of a score byte is a kick that went in, stamped at its write (minute, the score after it), with the
  team whose byte rose;
- code hooks 0791:A006 (play_shootout_kick's entry) and A1EF (its return in A10A): a kick between them with no
  score write is a miss, stamped at A1EF (minute, score), with the side that kicked as A006 left it in DS:8319
  (`DS:8319 = -side`, named seg_0791_08.c), not as the kit reads it (A10A's frame);
so the kit's `extra_time`, `shootout` and `shootout_kick` events are compared too, per kind (and team for kicks) and
in the whole stream (`order`). Scenarios: the knockout worked example (example.play_knockout's answers, budget
5), kind 200 fixtures from the reference image that go to extra time and penalties watched (index 42: sudden death)
and as quick results (index 9: 24 kicks, the takers' rotation past 11 and sudden death; 53), one decided in extra
time (30), goal2 managing the second side (19, index 42 quick: penalties), a qualifier (kind 2, index 21: no extra
time, the competition table after it) and the friendly reference.
--kit DIR imports original_match from DIR (default runtime/)."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E033-original-match-kit"))
import stamps as E033  # noqa: E402

IMAGE = E033.IMAGE


class Competitive(E033.Independent):
    def __init__(self, m):
        super().__init__(m)
        from unicorn import UC_HOOK_CODE
        ds, uc = m.DS * 16, m.uc
        self.shootout_from = None       # the index in self.order of the shoot-out's start
        self.kick_score = None

        def word(off):
            return int.from_bytes(uc.mem_read(ds + off, 2), "little")

        def score():
            return [uc.mem_read(ds + 0x9B3C, 1)[0], uc.mem_read(ds + 0x9B3D, 1)[0]]

        def code(address, fn):
            seg, off = address.split(":")
            lin = m.seg(int(seg, 16)) * 16 + int(off, 16)
            uc.hook_add(UC_HOOK_CODE, lambda *a: fn(), begin=lin, end=lin)

        def extra_time():
            self.order.append(["extra_time", 0x59] + score())

        def shootout():
            self.shootout_from = len(self.order)
            self.order.append(["shootout", word(0x831F)] + score())

        def kick():
            self.kick_score = score()

        def kicked():
            if score() == self.kick_score:
                side = (-uc.mem_read(ds + 0x8319, 1)[0]) & 0xFF
                self.order.append(["miss", side, word(0x831F)] + score())
            self.kick_score = None
        code("0791:9B15", extra_time)
        code("0791:A10A", shootout)
        code("0791:A006", kick)
        code("0791:A1EF", kicked)

    def expected(self):
        boards = [i for i, rec in enumerate(self.order) if rec[0] == "board"]
        order, skip_minute = [], False
        for i, rec in enumerate(self.order):
            kind = rec[0]
            if kind == "minute" and skip_minute:
                skip_minute = False
                if rec[1] != 0x59:
                    raise AssertionError(f"the write after 9B15 is minute {rec[1]}")
                continue
            if kind == "extra_time":
                skip_minute = True
                order.append(rec)
            elif kind == "score":
                shoot = self.shootout_from is not None and i > self.shootout_from
                if shoot and rec[5] < 0:
                    raise AssertionError("a score byte went down in the shoot-out")
                order.append(["shootout_kick" if shoot else "goal" if rec[5] > 0 else "goal_disallowed"] + rec[1:5])
            elif kind == "miss":
                order.append(["shootout_kick"] + rec[1:])
            elif kind == "board":
                if i in (boards[0], boards[-1]):
                    order.append(["half_time" if i == boards[0] else "full_time"] + rec[1:])
            else:
                order.append(rec)
        out = {k: [] for k in ORDERED}
        for rec in order:
            out[rec[0]].append(rec[1:])
        out["order"] = order
        return out


ORDERED = E033.ORDERED + ("extra_time", "shootout", "shootout_kick")
TEAMED = ("goal", "goal_disallowed", "booking", "sending_off", "injury", "substitution", "shootout_kick")


def kit_stamps(events):
    out = {k: [] for k in ORDERED}
    out["order"] = []
    for kind, minute, score, data in events:
        if kind in ORDERED:
            team = [data["team"]] if kind in TEAMED else []
            out[kind].append(team + [minute] + list(score))
            out["order"].append([kind] + team + [minute] + list(score))
    return out


def play_on(m, d):
    m.answer()


def quick_at_half_time(m, d):
    m.answer(quick=True) if d["context"] == "half_time" else m.answer()


def run(kit, img, index, kind, policy, budget=None, managed=7):
    m = kit.Match(img, kit.Fixture(7, 19, index=index, kind=kind), managed=managed, substitutions=budget)
    ind = Competitive(m.m)
    events = []
    for ev in m.events():
        events.append((ev.kind, ev.minute, ev.score, ev.data))
        if ev.kind == "decision":
            policy(m, ev.data)
    return ind.expected(), kit_stamps(events), m.result()


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
    data = (ROOT / ".cache/dl" / f"{IMAGE[0][:16]}-{IMAGE[1]}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == IMAGE[0]
    img = kit.Image.from_savestate(data)
    ko = lambda m, d: example.knockout_answer(m, d, lambda *x: None)  # noqa: E731
    scenarios = [("knockout example (39, budget 5)", dict(index=39, kind=200, policy=ko, budget=5)),
                 ("kind 200, 42: penalties, sudden death", dict(index=42, kind=200, policy=play_on)),
                 ("kind 200, 30: decided in extra time", dict(index=30, kind=200, policy=play_on)),
                 ("kind 200, 9, quick: 24 kicks", dict(index=9, kind=200, policy=quick_at_half_time)),
                 ("kind 200, 53, quick: penalties", dict(index=53, kind=200, policy=quick_at_half_time)),
                 ("kind 200, 42, quick, goal2 manages 19", dict(index=42, kind=200, policy=quick_at_half_time,
                                                                managed=19)),
                 ("kind 2, 21: a qualifier", dict(index=21, kind=2, policy=play_on)),
                 ("friendly, 21 (the reference)", dict(index=21, kind=1, policy=play_on))]
    bad = 0
    with open(log, "x") as out:
        for name, kw in scenarios:
            t = time.time()
            want, got, r = run(kit, img, **kw)
            mismatch = {}
            for k in sorted(set(want) | set(got)):
                w, g = want.get(k, []), got.get(k, [])
                if w != g:
                    first = next((i for i, (x, y) in enumerate(zip(w, g)) if x != y), min(len(w), len(g)))
                    mismatch[k] = {"writes": len(w), "events": len(g), "first_difference": first,
                                   "write": w[first] if first < len(w) else None,
                                   "event": g[first] if first < len(g) else None,
                                   "differing": sum(1 for x, y in zip(w, g) if x != y) + abs(len(w) - len(g))}
            counts = {k: len(v) for k, v in want.items() if k != "order"}
            so = r["shootout"]
            rec = {"scenario": name, "kit": a.kit, "pass": not mismatch, "counts": counts, "mismatch": mismatch,
                   "result": {"score": r["score"], "score_90": r["score_90"], "shootout": so and so["score"],
                              "kicks": so and len(so["kicks"]), "winner": r["winner"], "budget": r["substitution_budget"]},
                   "wall_s": round(time.time() - t, 1)}
            bad += bool(mismatch)
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{name:40s} {'PASS' if not mismatch else 'FAIL'} {rec['wall_s']:5.1f} s  {rec['result']}"
                  + (f"\n    {json.dumps(mismatch)[:600]}" if mismatch else ""), flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
