#!/usr/bin/env python3
"""E033: every decision path of runtime/original_match, each with its checks, one JSON line per scenario.

    python3 -B experiments/E033-original-match-kit/paths.py --log experiments/E033-original-match-kit/out/<new>.jsonl

The image is E006-r0001 (release E006, by SHA-256: goal2's own), the fixture Denmark (7) v country 19 at calendar
number 21 (E011-r0001's), managed 7, unless a scenario says otherwise. A scenario's `pass` is the conjunction of
its named checks; the script exits 1 when one fails."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, Match, Fixture, MatchError  # noqa: E402
from original_match.check import EXPECTED_ENGINE, result_digest  # noqa: E402

IMAGE = ("e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d", "e006-1000-r0001.sav")
FIX = Fixture(7, 19, index=21)


def load():
    sha, name = IMAGE
    data = (ROOT / ".cache" / "dl" / f"{sha[:16]}-{name}").read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        sys.exit("the image's SHA-256 differs")
    return Image.from_savestate(data)


def run(img, on_minute=None, on_decision=None, fixture=FIX, **kw):
    """Play a match; on_minute(m, minute) and on_decision(m, data) act; returns (result, events)."""
    m = Match(img, fixture, **({"managed": 7} | kw))
    events = []
    for ev in m.events():
        if ev.kind not in ("commentary", "minute", "tick"):
            events.append({"kind": ev.kind, "minute": ev.minute, "score": list(ev.score),
                           "data": {k: v for k, v in ev.data.items() if k not in ("positions", "eleven", "bench")}})
        if ev.kind == "minute" and on_minute:
            on_minute(m, ev.minute)
        if ev.kind == "decision":
            (on_decision or (lambda m, d: m.answer()))(m, ev.data)
    return m.result(), events


def pause_at(minute):
    done = []

    def f(m, at):
        if at == minute and not done:
            done.append(1)
            m.pause()
    return f


def engine_checks(r):
    return {"draws_digest": r["draws_digest"] == EXPECTED_ENGINE["draws_digest"], "score": r["score"] == EXPECTED_ENGINE["score"],
            "ticks": r["ticks"] == EXPECTED_ENGINE["ticks"], "board": r["board"]["screen_sha256"] == EXPECTED_ENGINE["board_screen_sha256"]}


def s_pause_without_change(img):
    r, ev = run(img, pause_at(10), record_draws=True, delay_byte=0)
    return engine_checks(r) | {"one_pause": sum(e["kind"] == "decision" and e["data"]["context"] == "pause" for e in ev) == 1}, ev


def s_speed_byte_kept(img):
    r, ev = run(img, record_draws=True)        # the speed byte left as the image holds it (1)
    return engine_checks(r), ev


def s_tactics_at_pause(img):
    def dec(m, d):
        m.answer(tactics={4: False} if d["context"] == "pause" else None)
    r, ev = run(img, pause_at(10), dec)
    t = [e for e in ev if e["kind"] == "tactics"]
    return {"tactics_event": len(t) == 1 and t[0]["data"]["byte"] == 0x83, "match_changed": r["score"] != [1, 1]}, ev


def s_half_time_substitution(img):
    def dec(m, d):
        if d["context"] == "half_time":
            m.answer(substitutions=[(130, 134)])
        else:
            m.answer()
    r, ev = run(img, None, dec)
    subs = [s for s in r["substitutions"] if s["team"] == 0]
    return {"made_at_46": [(s["off"], s["on"], s["minute"]) for s in subs][:1] == [(130, 134, 46)],
            "squad_after": r["squads_after"]["7"].index(134) < 11}, ev


def s_request_then_notice(img):
    def dec(m, d):
        if d["context"] == "pause":
            m.answer(substitutions=[(d["eleven"][10], d["bench"][7])])
        else:
            m.answer()
    r, ev = run(img, pause_at(20), dec)
    req = [e for e in ev if e["kind"] == "substitution_requested"]
    notice = [e for e in ev if e["kind"] == "decision" and e["data"]["context"] == "substitution"]
    subs = [s for s in r["substitutions"] if s["team"] == 0]
    return {"requested_at_pause": len(req) == 1, "offered_at_a_stoppage": len(notice) >= 1 and notice[0]["minute"] > 20,
            "made_by_default_answer": len(subs) == 1 and subs[0]["minute"] == notice[0]["minute"]}, ev


def s_refused_eleven(img):
    seen = []

    def dec(m, d):
        if d["context"] == "half_time" and not d.get("refused"):
            m.answer(substitutions=[(d["eleven"][9], 132)])        # 132: the reserve keeper (position 0)
        elif d["context"] == "half_time":
            seen.append(d["refused"])
            m.answer(substitutions=[(121, 133)])                  # take the keeper off: one keeper again
        else:
            m.answer()
    r, ev = run(img, None, dec)
    return {"refusal_offered_back": len(seen) == 1 and "goalkeeper" in seen[0].lower(),
            "match_completed": r["score"] is not None}, ev


def s_players(img):
    def dec(m, d):
        if d["context"] == "pause":
            pos = dict(d["positions"])
            m.answer(positions={126: (pos[126] + 2) % 14}, marking={124: 370}, own_tactics={128: {1: True, 2: False}})
        else:
            m.answer()
    r, ev = run(img, pause_at(15), dec)
    pos = [e for e in ev if e["kind"] == "position"]
    own = {e["data"]["player"]: e["data"] for e in ev if e["kind"] == "player_tactics"}
    return {"position": len(pos) == 1 and pos[0]["data"]["position"] == 6,
            "marking": own.get(124, {}).get("marking") == 370,
            "own_set": own.get(128, {}).get("own_set", 0) & 0x33 == 0x31,
            "no_refusal": not any(e["kind"] == "refused" for e in ev)}, ev


def s_quick_and_speed(img):
    def dec(m, d):
        m.answer(speed=3, quick=True) if d["context"] == "pause" else m.answer()
    r, ev = run(img, pause_at(30), dec)
    return {"quick_engine_ran": r["ticks"] < 3000, "completed": r["board"] is not None}, ev


def s_captain(img):
    six = Match(img, FIX, managed=7)._squad(7)[5]
    m = Match(img, FIX, managed=7, captain=six)
    for ev in m.events():
        if ev.kind == "minute":
            break
    return {"captain_word": m.m.rd(0x9978) == six}, []


def s_save_resume(img):
    def dec(m, d):
        m.answer(tactics={6: True})
    a, _ = run(img, None, dec, record_draws=True)
    m = Match(img, FIX, managed=7, record_draws=True)
    blob = blob2 = None
    for ev in m.events():
        if ev.kind == "minute" and ev.minute == 30:
            blob = m.save()
            break
    m2 = Match.load(blob)
    for ev in m2.events():
        if ev.kind == "decision":
            blob2 = m2.save()
            break
    m3 = Match.load(blob2)
    waiting = m3.waiting["context"]
    m3.answer(tactics={6: True})
    for ev in m3.events():
        if ev.kind == "decision":
            m3.answer(tactics={6: True})
    b = m3.result()
    return {"waiting_after_load": waiting == "half_time", "identical": result_digest(a) == result_digest(b)
            and a["draws_digest"] == b["draws_digest"], "sizes": [len(blob), len(blob2)]}, []


def s_other_country(img):
    r, ev = run(img, None, None, managed=19)
    d = [e for e in ev if e["kind"] == "decision"]
    return {"released_7": any("release country 7" in i["what"] for i in r["inputs"]),
            "decides_for_19": bool(d) and d[0]["data"]["tactics"] == 0xC7}, ev


def s_injury_notice(img):
    first = []

    def dec(m, d):
        if d["context"] == "substitution" and d["injured"] and not first:
            first.append(d)
            m.answer(substitutions=[(d["injured"][0], d["bench"][1])])
        else:
            m.answer()
    r, ev = run(img, None, dec, seed=70)
    subs = [s for s in r["substitutions"] if s["team"] == 0]
    return {"injury_offered": bool(first) and first[0]["injured"] == [128],
            "replaced": bool(subs) and subs[0]["off"] == 128}, ev


SCENARIOS = [s_pause_without_change, s_speed_byte_kept, s_tactics_at_pause, s_half_time_substitution,
             s_request_then_notice, s_refused_eleven, s_players, s_quick_and_speed, s_captain, s_save_resume,
             s_other_country, s_injury_notice]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--only")
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    img = load()
    failed = 0
    with open(log, "x") as out:
        for s in SCENARIOS:
            if a.only and s.__name__ not in a.only.split(","):
                continue
            t, c = time.time(), time.process_time()
            try:
                checks, events = s(img)
                error = None
            except (MatchError, ValueError, RuntimeError) as e:
                checks, events, error = {}, [], f"{type(e).__name__}: {e}"
            ok = error is None and all(v for k, v in checks.items() if k != "sizes")
            failed += not ok
            rec = {"scenario": s.__name__, "pass": ok, "checks": checks, "error": error, "events": events,
                   "wall_s": round(time.time() - t, 1), "cpu_s": round(time.process_time() - c, 1)}
            out.write(json.dumps(rec) + "\n")
            out.flush()
            print(f"{s.__name__:28s} {'PASS' if ok else 'FAIL'} {rec['wall_s']:6.1f} s  {checks if not ok or 'sizes' in checks else ''} {error or ''}", flush=True)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
