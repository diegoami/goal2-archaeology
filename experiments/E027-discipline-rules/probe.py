"""Count, in E011's two recorded watched matches run unhooked, the discipline and substitution routines of T53.

    python3 experiments/E027-discipline-rules/probe.py

Nothing is substituted. Every hook is a code hook at an instruction start of the listing
(static/goal-exe/code/seg_0791_*.asm) that only reads registers and memory. The one declared input is
WatchedMatch.run()'s own (the delay byte [DS:A923]+0x3F := 0, E021's standard; no discipline routine reads it).

Per record (E011-r0001, E011-r0002) it prints
  - the start state: DS:9A3D (fixture kind != 1), DS:9A3E (quick flag), DS:9B3A[0..1] (substitution budgets after A4A1),
    DS:8437 and the 255-byte draw table DS:8337+1..255 with the frequencies of 7EEF's two tests
    (draw1 < 4 and draw2 == 1) over the table, as the table stands when 7EEF is first entered;
  - the entries of 7A43, 7EEF, 798D, 7B77, 7D56, 8206, 8062, C88D, C5DC, D5C1, 5B36, 5513, 5474, 539F, with callers
    where a routine has several;
  - for each 7EEF entry the two table bytes it will read (DS:8437 and the next index, wrapping 255 -> 1);
  - for each 7A43 entry the side and the counters DS:7B86/7B87 of that side;
  - for each C88D entry the arguments (flag, side, slot) and DS:9B3A[side] before it;
  - the match-end counters DS:7B7E+side*10+k, DS:9B3A, DS:8321.
The log is written to a new file out/probe-<UTC time>.log (never overwritten) and echoed.
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/E021-m0-whole-match"))
from check import asset  # noqa: E402
from watched_match import WatchedMatch  # noqa: E402
from unicorn import UC_HOOK_CODE  # noqa: E402

CODE = ROOT / "static/goal-exe/code"
SEG = "0791"

ENTRIES = ["7A43", "7EEF", "798D", "7B77", "7D56", "8206", "8062", "C88D", "C5DC", "D5C1", "5B36", "5513", "5474",
           "539F", "7B24", "261A", "2648",
           # the foul funnel: 4DA9 (would this player foul), its two exits, 8206's early exit and its two endings
           "4DA9", "4DDF", "4E16", "4E1A", "824A", "824D", "82DD", "82E2",
           # 8062's substitution test passed (81B1), and the dead-ball routines that call 8062
           "81B1", "61EC", "6E11", "6E6E", "6ECF", "6F01", "6F3E", "983F"]
CALLERS_OF = {"8062", "7EEF", "8206", "C88D", "5B36"}

TABLE = 0x8337     # DS:8337 + index (1..255), 261A: mov al, [di - 0x7cc9]
INDEX = 0x8437
STATS = 0x7B7E     # DS:7B7E + side*10 + k

OUT = HERE / "out"


def listing_line(addr):
    """The listing line of an instruction start (a hook on anything else stops the run)."""
    pat = f"{addr}  "
    for f in sorted(CODE.glob(f"seg_{SEG}_*.asm")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if line.startswith(pat):
                return f"{f.name}:{n}: {line.strip()}"
    raise SystemExit(f"{SEG}:{addr} is not an instruction start of the listing")


def main():
    # `probe.py --seeds N FIRST`: E011-r0001's start state under N seeds (DS:7B62 := seed, a declared input)
    seeds = None
    if len(sys.argv) == 4 and sys.argv[1] == "--seeds":
        seeds = list(range(int(sys.argv[3]), int(sys.argv[3]) + int(sys.argv[2])))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    OUT.mkdir(exist_ok=True)
    log = OUT / (f"probe-seeds-{stamp}.log" if seeds else f"probe-{stamp}.log")
    lines = []

    def say(s=""):
        print(s, flush=True)
        lines.append(s)
        with open(log, "a") as f:     # appended per line: a killed run leaves what it printed
            f.write(s + "\n")

    say("E027 probe: " + stamp)
    for a in ENTRIES:
        say(f"  hook {SEG}:{a}  {listing_line(a)}")
    jobs = [(p, None) for p in sorted((ROOT / "runs/E011").glob("E011-r*.json"))]
    if seeds:
        jobs = [(ROOT / "runs/E011/E011-r0001.json", sd) for sd in seeds]
    for p, seed in jobs:
        record = json.loads(p.read_text())
        entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
        m = WatchedMatch(asset(entry))
        if seed is not None:
            m.set_seed(seed)
        say(f"\n=== {record['run_id']} seed {seed} (watchstart savestate sha256 {entry['sha256']})")
        say(f"start: DS:9A3D={m.rd(0x9A3D, 1)} DS:9A3E={m.rd(0x9A3E, 1)} DS:9B3A={m.rd(0x9B3A, 1)},{m.rd(0x9B3B, 1)} "
            f"DS:8437={m.rd(INDEX)} DS:8321={m.rd(0x8321)} DS:7B84..87[side0]={list(m.mem(m.DS*16+0x7B84, 4))}")
        counts = Counter()
        callers = {a: Counter() for a in CALLERS_OF}
        seven = []        # (draw1, draw2) at each 7EEF entry
        a43 = []          # (side, 7B86, 7B87) per 7A43 entry
        c88 = []          # (flag, side, slot, budget_before)
        first_table = {}

        def tbl():
            return m.mem(m.DS * 16 + TABLE, 256)

        def stack(off):
            ss = m.reg("ss") * 16
            return int.from_bytes(m.mu.mem_read(ss + m.reg("sp") + off, 2), "little")

        def at(a):
            def fn(uc, addr, size, data):
                counts[a] += 1
                if a in CALLERS_OF:
                    callers[a][f"{m.reg('cs') - m.load:04X}:{stack(0):04X}"] += 1
                if a == "7EEF":
                    t = tbl()
                    if "t" not in first_table:
                        first_table["t"] = t
                    i = m.rd(INDEX)
                    j = 1 if i == 0xFF else i + 1
                    seven.append((t[i], t[j]))
                if a == "7A43":
                    side = stack(2) & 0xFF
                    a43.append((side, m.rd(0x7B86 + side * 10, 1), m.rd(0x7B87 + side * 10, 1)))
                if a == "C88D":
                    # near call: [sp]=ret ip, +2 flag, +4 side, +6 slot, then the country far pointer (7D56 pushes it first)
                    flag, side, slot = stack(2) & 0xFF, stack(4) & 0xFF, stack(6)
                    c88.append((flag, side, slot, m.rd(0x9B3A + side, 1)))
            return fn

        for a in ENTRIES:
            lin = m.lin(f"{SEG}:{a}")
            m.mu.hook_add(UC_HOOK_CODE, at(a), begin=lin, end=lin)
        m.run(timeout_s=3000)
        say(f"run: ticks {m.final['ticks']}, score {m.final['score']}, 831F {m.final['831F']}")
        for a in ENTRIES:
            say(f"  {SEG}:{a} entered {counts[a]}")
            for k, c in sorted(callers.get(a, {}).items()):
                say(f"      from {k}: {c}")
        t = first_table.get("t") or tbl()
        body = t[1:256]
        d1 = sum(1 for b in body if b < 4)
        d2 = sum(1 for b in body if b == 1)
        hist = Counter(body)
        say(f"draw table DS:8337+1..255 (255 bytes): value histogram {dict(sorted(hist.items()))}")
        say(f"  draw1 < 4: {d1}/255 = {d1/255:.4f}; draw2 == 1: {d2}/255 = {d2/255:.4f}")
        say(f"7EEF entries (draw1, draw2): {seven}")
        say(f"7A43 entries (side, DS:7B86, DS:7B87): {a43}")
        say(f"C88D entries (flag, side, slot, budget before): {c88}")
        say(f"end: DS:9B3A={m.rd(0x9B3A, 1)},{m.rd(0x9B3B, 1)} DS:8321={m.rd(0x8321)}")
        for side in (0, 1):
            say(f"  stats side {side} (DS:7B7E+{side*10}+k, k=0..9): {list(m.mem(m.DS*16+STATS+side*10, 10))}")
    print(f"\nlog: {log}")


if __name__ == "__main__":
    main()
