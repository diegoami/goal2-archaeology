#!/usr/bin/env python3
"""Check the whole-match harness against the E011 ground truth (T38 Done-when 1 and 2).

    python3 experiments/E021-m0-whole-match/check.py [--hook NAME]

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

--hook substitutes 214B:0688 (F004's RNG step) with a Python LCG and PROVES it side by side at
every call (runtime/emul/watched_match.py, `hook(prove=True)`): the original routine runs to its
return with every byte it writes recorded, the state is put back, the model runs on it, and the
two must write the same bytes in the same order and return the same registers; the first
difference stops the run with a ProofError naming the call, the address and the byte. The hooks: `f004` is F004's
`seed = seed * 0x7ABD + 0x1B0F`, returning 1 + (seed * n) >> 16; `f004-mult+1` and `f004-inc+1`
change the multiplier or the increment by +1; `f004+hidden-write` writes 0xDEAD to the seed and
restores it before each F004 step, `f004+raw-write` does the same with raw `mu.mem_write` calls,
`f004+831D-write` writes 0xDEAD to DS:831D and restores it, and `f004+inc+1-off-seed` steps with
increment + 1 only when the seed pointer is not DS:7B62 (the hook's falsifiers). A hooked run is also compared with
an unhooked run of the same state: every write of the seed word (value before and after, clock
reading) must be the original's, in order.
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
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import keeping  # noqa: E402

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


def hidden_write(step):
    """A falsifier (review R1): `step` preceded by a write of 0xDEAD to the seed word and its
    restore, so the step's results are F004's but the word takes a value the original never
    writes."""
    def fn(g):
        off, seg = g.arg(1), g.arg(2)
        seed = g.word(seg, off)
        g.set_word(seg, off, 0xDEAD)
        g.set_word(seg, off, seed)
        step(g)
    return fn


def trace_difference(reference, draws):
    """None when the two seed-write traces are identical, else the first differing index with
    both entries (a missing entry is None)."""
    for i, (a, b) in enumerate(zip(reference, draws)):
        if a != b:
            return i, a, b
    if len(reference) != len(draws):
        i = min(len(reference), len(draws))
        return i, reference[i] if i < len(reference) else None, draws[i] if i < len(draws) else None
    return None


def raw_write(step):
    """A falsifier (review round 2, R1): 0xDEAD written to the seed word and restored with raw
    Unicorn writes (`g.mu.mem_write`), then F004's step."""
    def fn(g):
        lin = g.arg(2) * 16 + g.arg(1)
        saved = g.mem(lin, 2)
        g.mu.mem_write(lin, b"\xad\xde")
        g.mu.mem_write(lin, saved)
        step(g)
    return fn


def clock_write(step):
    """A falsifier (review round 2, R2): 0xDEAD written to DS:831D (the sub-tick) and restored,
    then F004's step."""
    def fn(g):
        saved = g.rd(0x831D)
        g.set_word(g.DS, 0x831D, 0xDEAD)
        g.set_word(g.DS, 0x831D, saved)
        step(g)
    return fn


def off_seed_increment(step, wrong):
    """A falsifier (review round 2, R3): F004's step on DS:7B62, the wrong step (increment + 1)
    when the seed pointer is elsewhere (DS:8336, the speaker stream)."""
    def fn(g):
        on_main = g.arg(2) * 16 + g.arg(1) == g.DS * 16 + 0x7B62
        (step if on_main else wrong)(g)
    return fn


SKILL_READER = "0791:278A"
RECORD_SIZE = 20            # 2797 `mov dx, 0x14; mul dx` (the player array's stride)


def skill_reader(gate=None, product_plus=0):
    """0791:278A as a hook fn (M1a): reads the routine's inputs from the guest and decides its result
    with keeping.contest_trace. Far-called with `retf 6` (2879): stack args off (bp+6), seg (bp+8),
    element (bp+0xA) = arg(0), arg(1), arg(2). Reads: the pitch record's word +0xD (2793, the player
    index), +0x13 (27F1), +0x11 (2846), +6 (2852); the player record at the far pointer DS:A91B
    (279C) + 0x14 * index, bytes +0xC (27AB), +0xE (27D4), +4/+5/+7 (3A06, seg_1771_05.asm:3A06-3A7F,
    keeping.skill_value), the tables DS:6D25 and DS:6DCD (4096 bytes each: see below), DS:8327 (2833) and
    DS:80FC (2859). Results: AX = the value (2870-2873); DX is what the last `div` left (281C's
    remainder, or 2865's `value % 0x10` when the manager's share is added), which the proof compares
    (REGS_RETURNED). `gate` replaces keeping.KEEPER_EVENTS and `product_plus` adds to the value
    (the falsifiers)."""
    def fn(g):
        off, seg, element = g.arg(0), g.arg(1), g.arg(2)
        pitch = seg * 16 + off
        index = g.word_at(pitch + 0xD)
        rec = g.far(0xA91B) + RECORD_SIZE * index
        p = lambda i: g.mem(rec + i, 1)[0]
        pb = lambda i: g.mem(pitch + i, 1)[0]
        # the tables are indexed by record bytes (+7, +5): the original reads DS memory past the
        # documented 168 / 192 bytes (E011-r0001 call #77: +5 = 0x10, row 16 of DS:6DCD), so the
        # model gets the following bytes of the data segment too (12 * 255 + 255 < 4096)
        classes = g.mem(g.DS * 16 + 0x6D25, 4096)
        profiles = g.mem(g.DS * 16 + 0x6DCD, 4096)
        saved = keeping.KEEPER_EVENTS
        if gate is not None:
            keeping.KEEPER_EVENTS = gate
        try:
            value, dx = keeping.contest_trace(p(4), p(5), p(7), p(0xC), p(0xE), element, classes, profiles,
                                              pb(0x13), pb(0x11), g.rd(0x8327, 1), g.rd(0x80FC, 1), pb(6))
        finally:
            keeping.KEEPER_EVENTS = saved
        g.set_reg("ax", (value + product_plus) & 0xFFFF)
        g.set_reg("dx", dx)
    return fn


HOOKS = {"none": None, "f004": f004_step(), "f004+hidden-write": hidden_write(f004_step()),
         "f004+raw-write": raw_write(f004_step()), "f004+831D-write": clock_write(f004_step()),
         "f004+inc+1-off-seed": off_seed_increment(f004_step(), f004_step(inc=INC + 1)),
         "f004-mult+1": f004_step(mult=MULT + 1),
         "f004-inc+1": f004_step(inc=INC + 1)}


M1 = {"m1-278a": {}, "m1-278a+gate-0x18": {"gate": frozenset({0x18})},
      "m1-278a+product+1": {"product_plus": 1}}


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
    if hook_name in M1:             # M0's substitution and 278A's, each proved at every call
        m.hook(LCG_STEP, HOOKS["f004"], prove=True)
        m.hook(SKILL_READER, skill_reader(**M1[hook_name]), prove=True)
    elif HOOKS[hook_name] is not None:
        m.hook(LCG_STEP, HOOKS[hook_name], prove=True)
    for fn in inputs:
        fn(m)
    error = None
    t = time.time()
    try:
        m.run(timeout_s=600)
    except Exception as e:  # a void run: everything after it counts as missed
        error = f"{type(e).__name__}: {e}"
        m.final = m.state()
    return m, error, round(time.time() - t, 1)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs/E011"))
    ap.add_argument("--hook", choices=sorted(HOOKS) + sorted(M1), default="none")
    a = ap.parse_args(argv)
    records = sorted(Path(a.runs).glob("E011-r*.json"))
    n = ok = 0
    failed = []
    hooked = proved = reader_hooked = reader_proved = 0
    scratch = {}
    differences = []
    for p in records:
        record = json.loads(p.read_text())
        rid = record["run_id"]
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        data = asset(entry)
        m, error, secs = emulate(data, a.hook)
        trace = None
        if a.hook != "none":   # a substitution is right only if every seed write is the original's
            ref, ref_error, _ = emulate(data, "none")
            trace = "unhooked run void: " + ref_error if ref_error else trace_difference(ref.draws, m.draws)
        sets = m.tick_values()
        cps = reads(record)
        hit = sum(1 for mi, d, s in cps if s in sets.get((mi, d), ()))
        n += len(cps)
        ok += hit
        hooked += m.hook_counts.get(LCG_STEP, 0)
        proved += m.proved_calls.get(LCG_STEP, 0)
        per_record = m.hook_counts.get(SKILL_READER, 0)
        reader_hooked += per_record
        reader_proved += m.proved_calls.get(SKILL_READER, 0)
        if a.hook in M1:
            print(f"  {rid}: {SKILL_READER} calls {per_record}, proved {m.proved_calls.get(SKILL_READER, 0)}")
        for r, c in m.scratch_differences.get(LCG_STEP, {}).items():
            scratch[r] = scratch.get(r, 0) + c
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
            "every seed write equals the unhooked original's (hooked runs)": trace is None,
        }
        print(f"{rid}: start {entry['name']} (captain screen, seed 0x{m.start_state['7B62']:04x});"
              f" emulated {m.final['ticks']} clock ticks, {len(m.draws)} seed writes, {secs} s;"
              f" full time: minute {m.final['831F']} sub-tick {m.final['831D']}, seed 0x{m.final['7B62']:04x},"
              f" score {m.final['score']} (record {ft['score']}, seed 0x{ft['seed']:04x});"
              f" 000E strays: {m.strays or 'none'}; hook {a.hook}: {m.hook_counts or 'none'}", flush=True)
        if error:
            print(f"  VOID: {error}")
            failed.append(f"{rid}: {error}")
            if error.startswith("ProofError"):
                differences.append(f"{rid}: {error}")
        for name, good in checks.items():
            if not good:
                print(f"  FAIL: {name}" + (f": first difference {trace}" if name.startswith("every seed write") else ""))
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
    if a.hook != "none":
        print(f"hooked calls of {LCG_STEP}: {hooked}; proved side by side with no difference: {proved};"
              f" differences: {len(differences)}" + (f" (first: {differences[0]})" if differences else ""))
        if a.hook in M1:
            print(f"hooked calls of {SKILL_READER}: {reader_hooked}; proved side by side with no difference:"
                  f" {reader_proved}")
        print("uncompared-register differences (warnings, proved calls): "
              + ", ".join(f"{r} {c}" for r, c in scratch.items()))
    else:
        print("hooked calls: none (no hook)")
    print(f"match: {ok}/{n}")
    if n == 0:
        print("no reads: an empty set fails")
        return 1
    return 0 if ok == n and not failed else 1


if __name__ == "__main__":
    sys.exit(main())
