#!/usr/bin/env python3
"""E033 (PR 251 review R3): every event's minute and score against the original's own writes, recorded by hooks this
script installs on the kit's machine, independent of the kit's event path.

    python3 -B experiments/E033-original-match-kit/stamps.py --log experiments/E033-original-match-kit/out/<new>.jsonl [--kit DIR]

--kit DIR imports original_match from DIR (default runtime/): a copy of an earlier commit's package shows the check
failing there. The script's own hooks, on the guest memory (Unicorn write hooks, called before each write lands):
- the commentary ring counter DS:80EE: each nonzero new value is one line (1D4A): (minute DS:831F, score);
- the score bytes DS:9B3C/9B3D: each +1 is a goal and each -1 a goal taken back (68B3), each at its own write,
  stamped (minute, the score after the write); except inside the quick engine: from its entry (code hook 0791:D733)
  to just after its commit (0791:DA5B) the bytes hold trial counts (static/goal-exe/named/seg_0791_11.c), so their
  writes are not goals, every stamp there carries the score saved at the entry, and the goals are the commit's
  bytes above that score, recorded at DA5B;
- the statistics STATS + 10t + 7, 8, 9 (bookings, red cards, injuries): each +1, (minute, score);
- substitutions left DS:9B3A + t (C5DC decrements it at C7DC; DS:9B38 is the action replay's copy): each -1 is a
  substitution, (minute, score);
- the minute word DS:831F: each change, (new minute, score);
- the board's key read (0791:0106 `call far 214B:08DD` at 0415): the half-time and full-time boards, (minute, score);
score, statistics, minute and substitution writes count from play_match's entry (0791:F098) to its return (F2E3),
as the set-up before it resets them. The kit's events of the same kinds must carry the same (minute, score), in the
same order, per kind and team: the check compares stamps, not counts. `order` (PR 251 review round 2, R2) compares
the whole stream across kinds: the kit's events of these kinds, in the order it yields them, must be the writes in
the order the original made them (kind, team, minute, score), the first board as half_time and the last as
full_time."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FAMILY = (0x0101, 0x1234, 0x2345, 0x2B7E, 0x4C1D, 0x6A33, 0x8E05, 0xA1F0, 0xC3C3, 0xE719)
IMAGE = ("e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d", "e006-1000-r0001.sav")


class Independent:
    """The original's writes, as this script sees them."""

    def __init__(self, m):
        from unicorn import UC_HOOK_MEM_WRITE, UC_HOOK_CODE
        self.m = m
        self.live = False
        self.quick = None               # the committed score while quick_match_engine runs (its entry to DA5B)
        self.log = {k: [] for k in ("commentary", "score", "booking", "sending_off", "injury", "substitution",
                                    "minute", "board")}
        self.order = []                 # every write above, of every kind, in the order the original made them
        ds = m.DS * 16
        uc = m.uc

        def word(off):
            return int.from_bytes(uc.mem_read(ds + off, 2), "little")

        def byte(off):
            return uc.mem_read(ds + off, 1)[0]

        def watch(off, size, fn):
            def hook(uc_, access, address, wsize, value, data):
                if address + wsize <= ds + off or address >= ds + off + size:
                    return
                old = bytes(uc_.mem_read(ds + off, size))
                new = bytearray(old)
                for i in range(wsize):
                    j = address + i - ds - off
                    if 0 <= j < size:
                        new[j] = (value >> (8 * i)) & 0xFF
                fn(old, bytes(new))
            uc.hook_add(UC_HOOK_MEM_WRITE, hook, begin=ds + off - 3, end=ds + off + size - 1)

        def score():
            return list(self.quick) if self.quick is not None else [byte(0x9B3C), byte(0x9B3D)]

        def add(kind, rec):
            self.log[kind].append(rec)
            self.order.append([kind] + rec)

        def line(old, new):
            if new != old and int.from_bytes(new, "little"):
                add("commentary", [word(0x831F)] + score())

        def score_write(old, new):
            if not self.live or self.quick is not None:     # the quick engine's trial counts: see quick_end
                return
            for t in (0, 1):
                d = (new[t] - old[t]) & 0xFF
                if d:
                    add("score", [t, word(0x831F), new[0], new[1], 1 if d < 0x80 else -1])

        def quick_start():              # quick_match_engine's entry: the score word it saves in [bp-2] (D75C)
            if self.live:
                self.quick = [byte(0x9B3C), byte(0x9B3D)]

        def quick_end():                # after its commit `mov [9B3C], ax` at DA58: the goals it committed
            if self.quick is None:
                return
            saved, self.quick = self.quick, None
            new = [byte(0x9B3C), byte(0x9B3D)]
            for t in (0, 1):
                for _ in range(new[t] - saved[t]):
                    add("score", [t, word(0x831F), new[0], new[1], 1])

        def cards(team):
            def f(old, new):
                if self.live:
                    for k, kind in enumerate(("booking", "sending_off", "injury")):
                        for _ in range(max(0, new[k] - old[k])):
                            add(kind, [team, word(0x831F)] + score())
            return f

        def subs(old, new):
            if self.live:
                for t in (0, 1):
                    if new[t] < old[t]:
                        add("substitution", [t, word(0x831F)] + score())

        def minute(old, new):
            if self.live and new != old:
                add("minute", [int.from_bytes(new, "little")] + score())

        watch(0x80EE, 2, line)
        watch(0x9B3C, 2, score_write)
        watch(0x7B7E + 7, 3, cards(0))
        watch(0x7B7E + 17, 3, cards(1))
        watch(0x9B3A, 2, subs)
        watch(0x831F, 2, minute)

        def code(address, fn):
            seg, off = address.split(":")
            lin = m.seg(int(seg, 16)) * 16 + int(off, 16)
            uc.hook_add(UC_HOOK_CODE, lambda *a: fn(), begin=lin, end=lin)
        code("0791:F098", lambda: setattr(self, "live", True))
        code("0791:F2E3", lambda: setattr(self, "live", False))
        code("0791:0415", lambda: add("board", [word(0x831F)] + score()))
        code("0791:D733", quick_start)
        code("0791:DA5B", quick_end)

    def expected(self):
        """Per kind the stamps the kit's events must carry, from the raw writes, and `order`: the writes of every
        kind in the original's order, as the kit's event stream must have them (a +1 of a score byte is a goal, a -1
        a goal taken back, each at its own write; the first board is half_time, the last full_time)."""
        out = {k: v for k, v in self.log.items() if k not in ("score", "board")}
        out["goal"] = [rec[:4] for rec in self.log["score"] if rec[4] > 0]
        out["goal_disallowed"] = [rec[:4] for rec in self.log["score"] if rec[4] < 0]
        out["half_time"], out["full_time"] = self.log["board"][:1], self.log["board"][-1:]
        boards = [i for i, rec in enumerate(self.order) if rec[0] == "board"]
        order = []
        for i, rec in enumerate(self.order):
            if rec[0] == "score":
                order.append(["goal" if rec[5] > 0 else "goal_disallowed"] + rec[1:5])
            elif rec[0] == "board":
                if i in (boards[0], boards[-1]):
                    order.append(["half_time" if i == boards[0] else "full_time"] + rec[1:])
            else:
                order.append(rec)
        out["order"] = order
        return out


ORDERED = ("commentary", "goal", "goal_disallowed", "booking", "sending_off", "injury", "substitution", "minute",
           "half_time", "full_time")


def kit_stamps(events):
    out = {k: [] for k in ORDERED}
    out["order"] = []
    for kind, minute, score, data in events:
        if kind in ORDERED:
            team = [data["team"]] if kind in ("goal", "goal_disallowed", "booking", "sending_off", "injury",
                                              "substitution") else []
            out[kind].append(team + [minute] + list(score))
            out["order"].append([kind] + team + [minute] + list(score))
    return out


def run(kit, img, seed=None, policy=None, pause_at=(), go_in_hard=False):
    countries = None
    if go_in_hard:                      # Denmark's tactic element 4 set: more fouls, cards (F026)
        countries = img.countries()
        rec = bytearray(countries[7])
        rec[0x2D] |= 1 << 3
        countries[7] = bytes(rec)
    m = kit.Match(img, kit.Fixture(7, 19, index=21), managed=7, seed=seed, countries=countries)
    ind = Independent(m.m)
    events, paused = [], set()
    for ev in m.events():
        events.append((ev.kind, ev.minute, ev.score, ev.data))
        if ev.kind == "minute" and ev.minute in pause_at and ev.minute not in paused:
            paused.add(ev.minute)
            m.pause()
        if ev.kind == "decision":
            (policy or (lambda m, d: m.answer()))(m, ev.data)
    return ind.expected(), kit_stamps(events)


def decisions(m, d):
    if d["context"] == "pause" and d["eleven"]:
        m.answer(tactics={4: not bool(d["tactics"] >> 3 & 1)}, substitutions=[(d["eleven"][10], d["bench"][7])])
    elif d["context"] == "half_time" and not d.get("refused"):
        m.answer(substitutions=[(d["eleven"][9], d["bench"][1])])
    elif d["context"] == "substitution" and d["injured"]:
        m.answer(substitutions=[(d["injured"][0], d["bench"][2])])
    else:
        m.answer()


def quick(speed, then=None, at=0):
    """Answer a pause from minute `at` on with the quick result (R) at `speed`; other decisions with `then` (or
    play on)."""
    def policy(m, d):
        if d["context"] == "pause" and m.minute >= at:
            m.answer(quick=True, speed=speed)
        else:
            (then or (lambda m, d: m.answer()))(m, d)
    return policy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--kit", default=str(ROOT / "runtime"))
    ap.add_argument("--quick", action="store_true", help="the reference fixture and two seeds only")
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    sys.path.insert(0, a.kit)
    import original_match as kit
    data = (ROOT / ".cache/dl" / f"{IMAGE[0][:16]}-{IMAGE[1]}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == IMAGE[0]
    img = kit.Image.from_savestate(data)
    scenarios = [("reference", {})] + [(f"seed 0x{s:04X}", {"seed": s}) for s in (FAMILY[:2] if a.quick else FAMILY)]
    scenarios += [("decisions, seed 70", {"seed": 70, "policy": decisions, "pause_at": (20, 60)}),
                  ("seed 70 (an injury)", {"seed": 70}),
                  ("go in hard, seed 4 (sendings off)", {"seed": 4, "go_in_hard": True}),
                  ("quick from minute 30 (R1)", {"policy": quick(3), "pause_at": (30,)}),
                  ("quick from minute 1, speed 0", {"policy": quick(0), "pause_at": (1,)}),
                  ("decisions then quick at 60, seed 70", {"seed": 70, "policy": quick(5, then=decisions, at=60),
                                                           "pause_at": (20, 60)})]
    bad = 0
    with open(log, "x") as out:
        for name, kw in scenarios:
            t = time.time()
            want, got = run(kit, img, **kw)
            mismatch = {}
            for kind in sorted(set(want) | set(got)):
                w, g = want.get(kind, []), got.get(kind, [])
                if w != g:
                    first = next((i for i, (x, y) in enumerate(zip(w, g)) if x != y), min(len(w), len(g)))
                    mismatch[kind] = {"writes": len(w), "events": len(g), "first_difference": first,
                                      "write": w[first] if first < len(w) else None,
                                      "event": g[first] if first < len(g) else None,
                                      "differing": sum(1 for x, y in zip(w, g) if x != y) + abs(len(w) - len(g))}
            counts = {k: len(v) for k, v in want.items()}
            rec = {"scenario": name, "kit": a.kit, "pass": not mismatch, "counts": counts, "mismatch": mismatch,
                   "wall_s": round(time.time() - t, 1)}
            bad += bool(mismatch)
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{name:20s} {'PASS' if not mismatch else 'FAIL'} {rec['wall_s']:5.1f} s  writes {counts}"
                  + (f"\n    {json.dumps(mismatch)[:600]}" if mismatch else ""), flush=True)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
