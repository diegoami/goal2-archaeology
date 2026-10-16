#!/usr/bin/env python3
"""E033: which bytes of an image, beyond the teams, change the match? E011-r0001's watchstart (taken inside
run_match) as the image does not give E021's match for E011-r0001's own fixture, E006's main-screen images do
(templates-20261016.jsonl). Transplant regions from E006-r0005 (E011's own start state) into the watchstart image,
or clear them in E006-r0005, and run the engine check's fixture each time.

    python3 -B experiments/E033-original-match-kit/image_dependence.py --log experiments/E033-original-match-kit/out/<new>.jsonl

Regions: the stack below the entry frame (SS:0000..SS:3EC0, SS = load + 0x3052), the text page B800:0000 (4000
bytes) and the three screen buffers at the far pointers DS:7C1A, DS:7C1E, DS:7C22 (unit_0791_init 0791:F3F2:
4000 bytes each), the whole data segment DS:0000..FFFF minus the stack, and the low memory below the program."""
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

R5 = ("3789d8490d2b42d8a589fec2afeb51de0ace4b4c5d1e5e24ff232321874dd106", "e006-2100-r0005.sav")
WS = ("d68e48c734a742a63e707a8c451b9011ef03b452ebd91f239d86f875464e07a9", "E011-r0001-watchstart.sav")


def load(pair):
    sha, name = pair
    data = (ROOT / ".cache/dl" / f"{sha[:16]}-{name}").read_bytes()
    assert hashlib.sha256(data).hexdigest() == sha
    return Image.from_savestate(data)


def regions(img):
    ss = (img.load + 0x3052) * 16
    ds = img.DS * 16
    out = {"stack below the entry frame": (ss, 0x3EC0), "text page B800": (0xB8000, 4000)}
    for off in (0x7C1A, 0x7C1E, 0x7C22):
        out[f"screen buffer [DS:{off:04X}]"] = (img.far(off), 4000)
    return out


def play(img):
    m = Match(img, Fixture(7, 19, index=21), managed=7, record_draws=True, delay_byte=0)
    for ev in m.events():
        if ev.kind == "decision":
            m.answer()
    r = m.result()
    return {"score": r["score"], "ticks": r["ticks"], "equal": r["draws_digest"] == EXPECTED_ENGINE["draws_digest"]
            and r["board"]["screen_sha256"] == EXPECTED_ENGINE["board_screen_sha256"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    a = ap.parse_args()
    log = Path(a.log)
    if log.exists():
        sys.exit(f"refused: {log} exists")
    out = open(log, "x")
    r5, ws = load(R5), load(WS)
    assert r5.load == ws.load

    def emit(rec):
        out.write(json.dumps(rec) + "\n")
        out.flush()
        print(json.dumps(rec), flush=True)

    t = time.time()
    emit({"run": "baseline E006-r0005", **play(load(R5)), "s": round(time.time() - t, 1)})
    emit({"run": "baseline watchstart", **play(load(WS)), "s": round(time.time() - t, 1)})
    reg = regions(r5)
    for name, (base, n) in reg.items():
        img = load(WS)
        img.memory[base:base + n] = r5.memory[base:base + n]
        diff = sum(1 for x, y in zip(load(WS).memory[base:base + n], r5.memory[base:base + n]) if x != y)
        emit({"run": f"watchstart with E006-r0005's {name}", "bytes_differing": diff, **play(img),
              "s": round(time.time() - t, 1)})
    img = load(WS)
    for name, (base, n) in reg.items():
        img.memory[base:base + n] = r5.memory[base:base + n]
    emit({"run": "watchstart with all of them", **play(img), "s": round(time.time() - t, 1)})
    for name, (base, n) in reg.items():
        img = load(R5)
        img.memory[base:base + n] = bytes(n)
        emit({"run": f"E006-r0005 with {name} zeroed", **play(img), "s": round(time.time() - t, 1)})


if __name__ == "__main__":
    main()
