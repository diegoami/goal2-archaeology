#!/usr/bin/env python3
"""E033: the kit on images taken inside a match (goal2's browser friendlies load E010 half-time savestates), and
the cost of yielding an event per tick.

    python3 -B experiments/E033-original-match-kit/templates.py --log experiments/E033-original-match-kit/out/<new>.jsonl

Runs (one JSON line each; images by SHA-256 from releases E010, E011, E006 in .cache/dl):
- watchstart: E011-r0001's watchstart (inside run_match, at the captain prompt) as the image, E011-r0001's fixture:
  the engine check must hold (the set-up redoes what the image's own run_match had done).
- e011-halftime: E011-r0001's half-time state as the image (its first half played: energy spent), the same
  fixture: the match must complete with no undeclared read; it need not equal the engine check.
- e010-halftime: E010-r0001's half-time state of a quick friendly (goal2's template), its own two countries and
  calendar number: the match must complete with decisions answered.
- ticks: the engine check's match from E006-r0001 with ticks=True against the default, CPU seconds."""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.check import EXPECTED_ENGINE  # noqa: E402

IMAGES = {
    "watchstart": "d68e48c734a742a63e707a8c451b9011ef03b452ebd91f239d86f875464e07a9:E011-r0001-watchstart.sav",
    "e011-halftime": "092f5f74bc5dc0c0f133709ca46be04122d3813a716c54fd23a686e9194ab9ff:E011-r0001-halftime.sav",
    "e010-halftime": None,    # its full SHA-256 is read from the cached file's name prefix and recorded
    "e006-r0001": "e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d:e006-1000-r0001.sav",
}


def image(key):
    if key == "e010-halftime":
        path = ROOT / ".cache/dl/e1dee7e2f5ad443e-E010-r0001-halftime.sav"
        data = path.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        if not sha.startswith("e1dee7e2f5ad443e"):
            sys.exit("E010-r0001 half-time: unexpected SHA-256")
        return Image.from_savestate(data), sha
    sha, name = IMAGES[key].split(":")
    data = (ROOT / ".cache/dl" / f"{sha[:16]}-{name}").read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        sys.exit(f"{name}: SHA-256 differs")
    return Image.from_savestate(data), sha


def play(img, fixture, managed, **kw):
    m = Match(img, fixture, managed=managed, **kw)
    kinds = {}
    t, c = time.time(), time.process_time()
    for ev in m.events():
        kinds[ev.kind] = kinds.get(ev.kind, 0) + 1
        if ev.kind == "decision":
            m.answer()
    r = m.result()
    return r, kinds, round(time.time() - t, 2), round(time.process_time() - c, 2)


def engine_equal(r):
    return {"score": r["score"] == EXPECTED_ENGINE["score"], "ticks": r["ticks"] == EXPECTED_ENGINE["ticks"],
            "draws_digest": r["draws_digest"] == EXPECTED_ENGINE["draws_digest"],
            "board": r["board"]["screen_sha256"] == EXPECTED_ENGINE["board_screen_sha256"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    out = open(log, "x")
    fix = Fixture(7, 19, index=21)

    def emit(rec):
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print(json.dumps(rec)[:300], flush=True)

    img, sha = image("watchstart")
    r, kinds, wall, cpu = play(img, fix, 7, record_draws=True, delay_byte=0)
    checks = engine_equal(r)
    emit({"run": "watchstart", "image_sha256": sha, "checks": checks, "pass": all(checks.values()), "kinds": kinds,
          "wall_s": wall, "cpu_s": cpu})
    img, sha = image("e011-halftime")
    r, kinds, wall, cpu = play(img, fix, 7, record_draws=True, delay_byte=0)
    emit({"run": "e011-halftime", "image_sha256": sha, "completed": r["board"] is not None, "score": r["score"],
          "ticks": r["ticks"], "equals_engine_check": engine_equal(r), "kinds": kinds, "wall_s": wall, "cpu_s": cpu})
    img, sha = image("e010-halftime")
    sides = [img.rd(0x9B34), img.rd(0x9B36)]
    human = img.managed_countries()
    r, kinds, wall, cpu = play(img, Fixture(sides[0], sides[1]), human[0] if human and human[0] in sides else sides[0])
    emit({"run": "e010-halftime", "image_sha256": sha, "sides": sides, "image_humans": human,
          "index": img.fixture_index(), "completed": r["board"] is not None, "score": r["score"], "ticks": r["ticks"],
          "kinds": kinds, "inputs": [i["what"] for i in r["inputs"]], "wall_s": wall, "cpu_s": cpu})
    img, sha = image("e006-r0001")
    for ticks in (False, True, False, True):
        r, kinds, wall, cpu = play(img, fix, 7, ticks=ticks)
        emit({"run": "ticks", "ticks_events": ticks, "events": sum(kinds.values()), "wall_s": wall, "cpu_s": cpu,
              "score": r["score"]})


if __name__ == "__main__":
    main()
