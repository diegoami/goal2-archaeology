"""The check a goal2 session runs: is this the original's engine, run right, on this machine?

    python3 -m original_match.check [--image FILE.sav] [--cache .cache] [--family] [--json REPORT.json]

1. engine: E011-r0001's fixture (Denmark v country 19, calendar number 21, no input but the speed byte 0 at the
   captain prompt, as E011's starting keys left it) from the reference image must be the match E021 recorded
   from E011's DOSBox-X run (experiments/E021-m0-whole-match/out/20261011T201945897620Z-none-E011-r0001.json, its
   reads placed on E011's own): score, ticks, every main-RNG draw by its digest, the seed at the full-time board,
   the man of the match and the board screen's digest.
2. family (--family, about 100 s): E032's ten seeds written at the captain prompt must be E032's records
   (experiments/E032-match-engine-inventory/out/timing-delay20-*.jsonl): score, ticks, draws and their digest.
3. interactive: example.py's match (goal2's own lineup and tactics, a tactic change at a pause, a substitution
   at half time) run straight and saved and resumed at minute 60 must be identical to each other and to the
   digest this kit recorded (EXPECTED_INTERACTIVE): the same inputs and answers give the same match.
The expected values are digests and counts, no original bytes. Exit 0 when every check passes."""
import argparse
import hashlib
import json
import sys
import time

from . import Image, Match, Fixture, VERSION
from .assets import reference_image, REFERENCE
from . import example

EXPECTED_ENGINE = {"score": [1, 1], "ticks": 4149, "draws": 182188, "seed_at_board": 46625, "man_of_the_match": 127,
                   "draws_digest": "939f25379c56da7a13d32d4a8d3a5830b0f30eb4db9bb71f459e3b47bd494749",
                   "board_screen_sha256": "af83875517ff679aefaff91bb59d5461071c21c1674cd4258f50da7af3a2f295",
                   # the ring's 199 lines at the board (E021 `commentary` texts, oldest first, joined by newlines)
                   "commentary_last199_sha256": "0b749b4494f29e67250e73ef2d9f718e2484a5475d3b86bc3e15f7e89f12d877"}
EXPECTED_FAMILY = {   # seed: [score, ticks, draws, draws digest] (E032)
    0x0101: [[1, 0], 4279, 192967, "a365b543a2fd8cf85bfee434501dbe6efbfa7cd2ccf0921e18cfecf7f8469704"],
    0x1234: [[1, 1], 4146, 184109, "74b8eb805a4e391f2a0e4e213830b5c734d1b5086c75c682c5978b6403f9563e"],
    0x2345: [[0, 1], 4138, 187079, "fdd36353b12d04ce743c945f7f1161690403bbcdc51ed5ef4fb6cb7aedf65224"],
    0x2B7E: [[0, 2], 4029, 175773, "9c52581937efaeadc6b517fcf01f71d9e1d5c1afb647f833f31954aa09ce8c0e"],
    0x4C1D: [[1, 0], 4659, 210776, "062f3ec21511863a0ff66ba7988e44f908274a3500c0c60de6d2f8ba74455e1b"],
    0x6A33: [[0, 2], 4159, 184733, "e609a2ab96983daa3487ca71c254869482fbf576cde998b3cf5a61f58eaadf91"],
    0x8E05: [[1, 0], 4157, 186815, "139451d24fb36777d923c555e2f15ed093dade0fd66e41dd1a285b227a518c57"],
    0xA1F0: [[1, 0], 4281, 191805, "a0b3a43269fb60c1f7c1912dfc1b83afbaa0ed02abe60a3711a40edc83cce63b"],
    0xC3C3: [[2, 1], 4262, 184677, "4273d8ff21afa63b1451dc2ae5f6ffc48837eab6bbcccce387d6d0ad19727d8a"],
    0xE719: [[1, 0], 4240, 191629, "21f4cfca112e037de352c45767b898f67e01b31ff2db352e65c56fa377268b13"],
}
# example.py's match as this kit played it on the reference image (E033 out/check-*.json): a regression value,
# not independent evidence; a machine that gives another digest plays another match from the same inputs.
EXPECTED_INTERACTIVE = "0078fad9859d4b4083a88707785e2cf0a49e1b6cddfa48bfec5aa765590e592f"
REFERENCE_FIXTURE = Fixture(first=7, second=19, index=21)


def result_digest(r):
    """A digest of what a match produced: score, events, the board, the commentary, the squads and the seed."""
    keep = {k: r[k] for k in ("score", "half_time_score", "goals", "bookings", "sendings_off", "injuries",
                              "substitutions", "man_of_the_match", "ticks", "seed_after", "squads_after")}
    keep["board"] = {k: r["board"][k] for k in ("statistics", "bars", "screen_sha256")}
    keep["commentary"] = [c["text"] for c in r["commentary"]]
    return hashlib.sha256(json.dumps(keep, sort_keys=True).encode()).hexdigest()


def engine(image):
    m = Match(image, REFERENCE_FIXTURE, managed=7, record_draws=True, delay_byte=0)
    for _ in m.events():
        pass
    r = m.result()
    lines = "\n".join(c["text"] for c in r["commentary"][-199:])
    got = {"score": r["score"], "ticks": r["ticks"], "draws": r["draws"], "seed_at_board": r["board"]["seed"],
           "man_of_the_match": r["man_of_the_match"], "draws_digest": r["draws_digest"],
           "board_screen_sha256": r["board"]["screen_sha256"],
           "commentary_last199_sha256": hashlib.sha256(lines.encode()).hexdigest()}
    return got == EXPECTED_ENGINE, {k: (got[k], EXPECTED_ENGINE[k]) for k in got if got[k] != EXPECTED_ENGINE[k]}


def family(image):
    bad = {}
    for seed, want in EXPECTED_FAMILY.items():
        m = Match(image, REFERENCE_FIXTURE, managed=7, record_draws=True, delay_byte=0, seed=seed)
        for _ in m.events():
            pass
        r = m.result()
        got = [r["score"], r["ticks"], r["draws"], r["draws_digest"]]
        if got != want:
            bad[f"0x{seed:04X}"] = {"got": got[:3], "want": want[:3], "digest_equal": got[3] == want[3]}
    return not bad, bad


def interactive(image):
    straight = result_digest(example.play(image, quiet=True, resume_at=None))
    resumed = result_digest(example.play(image, quiet=True, resume_at=60))
    ok = straight == resumed and (EXPECTED_INTERACTIVE is None or straight == EXPECTED_INTERACTIVE)
    return ok, {"straight": straight, "resumed": resumed, "expected": EXPECTED_INTERACTIVE}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--image", help="a savestate or Memory component (default: the reference, fetched by hash)")
    ap.add_argument("--cache", default=".cache")
    ap.add_argument("--family", action="store_true")
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    data = open(a.image, "rb").read() if a.image else reference_image(a.cache)
    image = Image.from_bytes(data)
    report = {"kit": VERSION, "image_sha256": hashlib.sha256(data).hexdigest(), "reference": REFERENCE, "checks": {}}
    steps = [("engine", engine), ("interactive", interactive)] + ([("family", family)] if a.family else [])
    for name, fn in steps:
        t0, c0 = time.time(), time.process_time()
        ok, detail = fn(image)
        report["checks"][name] = {"pass": ok, "detail": detail, "wall_s": round(time.time() - t0, 1),
                                  "cpu_s": round(time.process_time() - c0, 1)}
        print(f"{name:12s} {'PASS' if ok else 'FAIL'}  {report['checks'][name]['wall_s']} s  {detail if not ok or name == 'interactive' else ''}")
    if a.json:
        with open(a.json, "x") as f:
            json.dump(report, f, indent=1)
    sys.exit(0 if all(c["pass"] for c in report["checks"].values()) else 1)


if __name__ == "__main__":
    main()
