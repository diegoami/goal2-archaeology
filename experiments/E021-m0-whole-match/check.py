#!/usr/bin/env python3
"""Check the whole-match harness against the E011 ground truth (T38 Done-when 1 and 2).

    python3 experiments/E021-m0-whole-match/check.py [--hook none|f004|f004-mult+1|f004-inc+1]

For each E011 record: take its watchstart savestate (the captain screen before the kick-off; the
release E011 asset named by sha256, downloaded into .cache/dl/ when missing), emulate the whole
match with runtime/emul/watched_match.py to the full-time board, and check EVERY mid-play read of the
record (both halves; the record's "ground-truth trajectory" observation, none excluded) against the
emulated trajectory tick-exactly: the read's (DS:831F, DS:831D) names the clock reading, and its
DS:7B62 must be one of the values the seed word takes under that reading (E011 notes.md §6, F013).
Also: the full-time score equals the record's, the 000E skip log is empty, the keys delivered are
exactly the declared ones, and the seed word and the text screen (4000 bytes, sha256) at the board
equal the record's "full time" read. Ends with `match: N/N` (N = the records' reads) and the
hooked-call count; exits non-zero on an empty set, any miss or any failed check.

--hook substitutes 214B:0688 (F004's RNG step) with a Python LCG: `f004` is F004's
`seed = seed * 0x7ABD + 0x1B0F`, returning 1 + (seed * n) >> 16; `f004-mult+1` and `f004-inc+1`
change the multiplier or the increment by +1 (the hook's falsifiers).
Each emulated run's outputs (without the draw list, whose count and sha256 they carry) are written
to a new file under experiments/E021-m0-whole-match/out/ (never overwritten)."""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
import driver  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
DL = ROOT / ".cache/dl"
LCG_STEP = "214B:0688"
MULT, INC = 0x7ABD, 0x1B0F          # F004 (seg_214B_01.asm:881, :883)


def f004_step(mult=MULT, inc=INC):
    """F004's step as a hook fn: stack (far call) n at +4, the seed's far pointer at +6/+8;
    the new seed is stored, AX = DX = 1 + (new * n) >> 16 (seg_214B_01.asm:873-894)."""
    def fn(g):
        n, off, seg = g.arg(0), g.arg(1), g.arg(2)
        new = (g.word(seg, off) * mult + inc) & 0xFFFF
        g.set_word(seg, off, new)
        r = (((new * n) >> 16) + 1) & 0xFFFF
        g.set_reg("ax", r)
        g.set_reg("dx", r)
    return fn


HOOKS = {"none": None, "f004": f004_step(), "f004-mult+1": f004_step(mult=MULT + 1),
         "f004-inc+1": f004_step(inc=INC + 1)}


def asset(entry, release="E011"):
    """A record output's bytes, by its sha256 (downloaded from the release when not cached)."""
    name = f"{entry['sha256'][:16]}-{entry['name']}"
    path = DL / name
    if not path.is_file():
        DL.mkdir(parents=True, exist_ok=True)
        subprocess.run(["gh", "release", "download", release, "--repo", "diegoami/goal2-archaeology",
                        "--pattern", name, "--dir", str(DL)], check=True)
    data = path.read_bytes()
    if driver.sha256(data) != entry["sha256"]:
        raise SystemExit(f"{path}: sha256 does not match the record's {entry['sha256']}")
    return data


def observation(record, prefix):
    return next(o["value"] for o in record["observations"] if o.get("field", "").startswith(prefix))


def reads(record):
    """Every mid-play read of the record: [(minute, sub-tick, seed)], in read order."""
    return [tuple(p) for p in json.loads(observation(record, "ground-truth trajectory"))]


def full_time(record):
    clock = observation(record, "full time: clock").split()
    return {"seed": int(clock[4]), "score": [int(x) for x in observation(record, "full time: score bytes").split()],
            "screen_sha256": observation(record, "full time: text screen 80x25, chars+attributes")}


def draws_digest(draws):
    return hashlib.sha256("\n".join("%d %d %04x %04x" % d for d in draws).encode()).hexdigest()


def write_out(label, run_id, payload):
    OUT.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = OUT / f"{stamp}-{label}-{run_id}.json"
    with open(path, "x") as f:                       # never overwrite
        json.dump(payload, f, indent=1)
    return path


def emulate(data, hook_name, inputs=()):
    m = WatchedMatch(data)
    if HOOKS[hook_name] is not None:
        m.hook(LCG_STEP, HOOKS[hook_name])
    for fn in inputs:
        fn(m)
    error = None
    t = time.time()
    try:
        m.run()
    except Exception as e:  # a void run: everything after it counts as missed
        error = f"{type(e).__name__}: {e}"
        m.final = m.state()
    return m, error, round(time.time() - t, 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs/E011"))
    ap.add_argument("--hook", choices=sorted(HOOKS), default="none")
    a = ap.parse_args(argv)
    records = sorted(Path(a.runs).glob("E011-r*.json"))
    n = ok = 0
    failed = []
    hooked = 0
    for p in records:
        record = json.loads(p.read_text())
        rid = record["run_id"]
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        m, error, secs = emulate(asset(entry), a.hook)
        sets = m.tick_values()
        cps = reads(record)
        hit = sum(1 for mi, d, s in cps if s in sets.get((mi, d), ()))
        n += len(cps)
        ok += hit
        hooked += m.hook_counts.get(LCG_STEP, 0)
        ft = full_time(record)
        out = m.outputs() if m.stopped_at_board else {"final": m.final, "key_log": m.key_log, "strays": m.strays,
                                                      "hook_counts": m.hook_counts, "inputs": m.inputs}
        screen_sha = out.get("board_screen_sha256")
        checks = {
            "full-time score equals the record's": m.final["score"] == ft["score"],
            "the 000E skip log is empty": not m.strays,
            "keys: the three declared screens, Enter each": [k[0].split(" (")[0] for k in m.key_log]
            == ["captain screen", "half-time board", "team screen"],
            "stopped at the full-time board's key wait": m.stopped_at_board,
            "seed at the board equals the record's full-time read": m.final["7B62"] == ft["seed"],
            "board screen sha256 equals the record's full-time screen": screen_sha == ft["screen_sha256"],
        }
        print(f"{rid}: start {entry['name']} (captain screen, seed 0x{m.start_state['7B62']:04x});"
              f" emulated {m.final['ticks']} clock ticks, {len(m.draws)} seed writes, {secs} s;"
              f" full time: minute {m.final['831F']} sub-tick {m.final['831D']}, seed 0x{m.final['7B62']:04x},"
              f" score {m.final['score']} (record {ft['score']}, seed 0x{ft['seed']:04x});"
              f" 000E strays: {m.strays or 'none'}; hook {a.hook}: {m.hook_counts or 'none'}", flush=True)
        if error:
            print(f"  VOID: {error}")
            failed.append(f"{rid}: {error}")
        for name, good in checks.items():
            if not good:
                print(f"  FAIL: {name}")
                failed.append(f"{rid}: {name}")
        for mi, d, s in cps:
            if s not in sets.get((mi, d), ()):
                print(f"  MISS: read at minute {mi} sub-tick {d} seed 0x{s:04x} is not on the emulated"
                      f" trajectory ({len(sets.get((mi, d), ()))} values under that clock reading)")
        print(f"  {rid}: reads {hit}/{len(cps)}")
        out.update({"run_id": rid, "hook": a.hook, "start_state": {"name": entry["name"], "sha256": entry["sha256"]},
                    "reads_matched": hit, "reads": len(cps), "checks": checks, "error": error, "seconds": secs,
                    "draws_count": len(m.draws), "draws_sha256": draws_digest(m.draws)})
        out.pop("draws", None)
        print(f"  outputs: {write_out(a.hook, rid, out).relative_to(ROOT)}")
    print(f"hooked calls of {LCG_STEP}: {hooked}" if a.hook != "none" else "hooked calls: none (no hook)")
    print(f"match: {ok}/{n}")
    if n == 0:
        print("no reads: an empty set fails")
        return 1
    return 0 if ok == n and not failed else 1


if __name__ == "__main__":
    sys.exit(main())
