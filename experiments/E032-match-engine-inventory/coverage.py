#!/usr/bin/env python3
"""E032 (the match-engine plan): what a whole watched match of the original executes, by routine.

    python3 -B experiments/E032-match-engine-inventory/coverage.py --seed 0xC0DE --out experiments/E032-match-engine-inventory/out/<new file>.json [--fast-delay]

Runs one whole watched match of the ORIGINAL code in the E021 harness (runtime/emul/watched_match.py,
no substitution hook) from E011-r0001's watchstart savestate (sha256 verified by check.asset), with
the main seed DS:7B62 written (a declared input, as E026's arms do). Adds two observers and nothing
else:
- a basic-block hook over the code image (paragraphs 0000..2581 of the load): per block start, the
  executions and the block's size, split by phase: "match" from the first clock tick (0791:970C entry)
  to F098's return (0791:F2E3), "outside" otherwise (the captain screen's tail, the boards);
- a memory-write hook over the text page (B800:0000..0FA0) and the off-screen page the game draws to
  ([DS:A96A], when it is elsewhere): per writing routine, the bytes written.
Each block is attributed to the routine whose start (static/goal-exe/routines.tsv) is the nearest at or
below it in its segment. The output is one JSON file (refused if it exists): per routine, the
executions, executed instructions (block executions x instructions per block, counted by capstone on the
guest bytes), distinct code bytes reached against the routine's size, the phase split, video writes, the
annotation's name, and the run's score, ticks, draws and wall seconds.

--fast-delay additionally writes the delay calibration dword DS:A9FF/AA01 := 1 (a declared input). F006
(C-MATCH-02) says delays only count passes against it, so a match must not change: compare the score and
the draws digest with a run without it."""
import argparse
import bisect
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "E021-m0-whole-match"))
sys.path.insert(0, str(ROOT / "runtime" / "emul"))
from check import asset, draws_digest  # noqa: E402
from watched_match import WatchedMatch, SCREEN_PTR  # noqa: E402
from unicorn import UC_HOOK_BLOCK, UC_HOOK_MEM_WRITE  # noqa: E402
from unicorn import x86_const as X  # noqa: E402
import capstone  # noqa: E402

RECORD = ROOT / "runs/E011/E011-r0001.json"
DS_PARAGRAPH = 0x2581


def routines():
    starts, info = [], {}
    for line in (ROOT / "static/goal-exe/routines.tsv").read_text().splitlines():
        if line.startswith(";") or line.startswith("segment"):
            continue
        f = line.split("\t")
        seg, off = (int(x, 16) for x in f[0].split(":"))
        img = seg * 16 + off
        starts.append(img)
        info[img] = {"address": f[0], "size": int(f[1]), "instructions": int(f[2])}
    names = {}
    for line in (ROOT / "static/goal-exe/annotations/routines.tsv").read_text().splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 4:
            names[f[0]] = (f[1], f[3])
    starts.sort()
    return starts, info, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fast-delay", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refused: {out} exists")
    record = json.loads(RECORD.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    data = asset(entry)          # bytes, sha256-verified against the record
    m = WatchedMatch(data)
    m.set_seed(a.seed)
    if a.fast_delay:
        m.write_input("delay calibration dword DS:A9FF/AA01", m.DS * 16 + 0xA9FF, (1).to_bytes(4, "little"))
    base = m.load * 16
    code_end = (m.load + DS_PARAGRAPH) * 16
    blocks = {}      # linear -> [size, n_match, n_outside]

    def on_block(uc, address, size, data):
        b = blocks.get(address)
        if b is None:
            b = blocks[address] = [size, 0, 0]
        if m.tick_marks and m.full_time is None:
            b[1] += 1
        else:
            b[2] += 1

    m.mu.hook_add(UC_HOOK_BLOCK, on_block, begin=base, end=code_end)
    video = {}       # linear pc -> bytes written
    pages = [(0xB8000, 0xB8000 + 4000)]
    off_screen = m.far(SCREEN_PTR)
    if not (0xB8000 <= off_screen < 0xB8000 + 4000):
        pages.append((off_screen, off_screen + 4000))

    def on_video(uc, access, address, size, value, data):
        pc = m.reg("cs") * 16 + m.reg("ip")
        video[pc] = video.get(pc, 0) + size

    for lo, hi in pages:
        m.mu.hook_add(UC_HOOK_MEM_WRITE, on_video, begin=lo, end=hi - 1)
    t = time.time()
    error = None
    try:
        m.run(timeout_s=3600)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    secs = round(time.time() - t, 1)

    starts, info, names = routines()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_16)
    per = {}

    def owner(img):
        i = bisect.bisect_right(starts, img) - 1
        return starts[i] if i >= 0 else None

    for lin, (size, nm, no) in blocks.items():
        img = lin - base
        r = owner(img)
        if r is None:
            continue
        p = per.setdefault(r, {"blocks": 0, "exec_match": 0, "exec_outside": 0, "instr_match": 0,
                               "instr_outside": 0, "bytes_reached": 0, "video_bytes": 0})
        n_ins = len(list(md.disasm(bytes(m.mem(lin, size)), 0)))
        p["blocks"] += 1
        p["exec_match"] += nm
        p["exec_outside"] += no
        p["instr_match"] += nm * n_ins
        p["instr_outside"] += no * n_ins
        p["bytes_reached"] += size     # blocks can overlap after a jump into a block; an upper bound
    for pc, nbytes in video.items():
        r = owner(pc - base)
        if r is not None and r in per:
            per[r]["video_bytes"] += nbytes
    rows = []
    for r, p in sorted(per.items()):
        i = info[r]
        nm = names.get(i["address"], ("", ""))
        rows.append({"address": i["address"], "name": nm[0], "confidence": nm[1], "size": i["size"],
                     "instructions_static": i["instructions"], **p})
    outs = {"final": m.state(), "error": error, "seconds": secs, "seed": a.seed, "fast_delay": a.fast_delay,
            "score": m.state()["score"], "ticks": len(m.tick_marks), "draws": len(m.draws),
            "draws_digest": draws_digest(m.draws), "strays": list(m.strays), "inputs": m.inputs,
            "stopped_at_board": m.stopped_at_board, "video_pages": [[hex(lo), hex(hi)] for lo, hi in pages],
            "statistics_raw": m.statistics() if not error else None,
            "start_record": "E011-r0001", "watchstart_sha256": entry["sha256"], "routines": rows}
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "x") as f:
        json.dump(outs, f, indent=1)
    print(json.dumps({k: outs[k] for k in ("seed", "fast_delay", "score", "ticks", "draws", "draws_digest",
                                           "seconds", "error", "strays", "stopped_at_board")}))


if __name__ == "__main__":
    main()
