"""Count, in E011's recorded watched matches run unhooked, the contest sites of T45 (M2a) and the branches
each one takes.

    python3 experiments/E022-m2a-contests/probe.py

Nothing is substituted and nothing is written to the guest: every hook is a code hook at an instruction
of the listing (static/goal-exe/code/seg_0791_*.asm) that only reads registers and memory. Per record
(E011-r0001, E011-r0002) it prints, for each contest site of T45's Scope 1:

  - the site's call count, by the return address of the call (the Evidence's counts) and, from the
    arguments on the stack at the callee's entry, the element the site passed (the table values are
    the run's, not the data image's);
  - the branch counts: each `label` is the listing line the hook sits on (its text is printed from
    the listing, and a hook on a line that is not an instruction start of the listing stops the run);
  - the gates of the sites E011 does not reach (their hooks print 0 when the gate holds).

A falsifier of M2b can stop only on a branch these matches take (docs/lessons.md L105). The log is
written to a new file out/probe-<UTC time>.log (never overwritten) and echoed.
"""
import json
import re
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

# --- the Evidence's counts (T45 task file): 278A's calls by return address, per record ---------
EXPECTED_CALLS = {"288E": 545, "368D": 7, "3B35": 3, "3F4B": 5, "54A1": 120, "54F2": 120, "5D69": 13}
# the sites E011 does not reach, by return address of the call: 0 expected (Scope 3)
UNREACHED_CALLS = {"36DD": "34C1 second call (36DA)", "5BC7": "5B36 duel, air (5BC4)", "5BDB": "5B36 duel, air (5BD8)",
                   "5C09": "5B36 duel, ground (5C06)", "5C1D": "5B36 duel, ground (5C1A)",
                   "696B": "690C (6968)", "9F6D": "9ED3 (9F6A)", "9FA2": "9ED3 (9F9F)"}
# the selection sites, classified only (Scope 2)
SELECTION_CALLS = {"20A3": "1FDD incumbent", "20B0": "1FDD candidate", "494D": "47C5 marker el.5", "496A": "47C5 cand. el.8",
                   "4980": "47C5 marker el.5 (again)", "499D": "47C5 cand. el.8 (again)"}

# --- the 287C call sites: the return address of each call is the `or al, al` the hook reads -------
S287C = {"3725": "34C1 (call 3722)", "39FC": "384C (call 39F9)", "3C89": "3C3F (call 3C86)", "5401": "539F (call 53FE)",
         "560F": "5565 (call 560C)", "6003": "5F8A (call 6000)", "6071": "5F8A (call 606E)", "60A8": "5F8A (call 60A5)",
         "611C": "5F8A (call 6119)"}

# --- routines whose entry arguments are tallied: (entry, name, arg words after the far return address) ---
# a near call from the same segment pushes cs first, so the frame is the far one in every case here.

# --- branch hooks: address -> short label (the listing line is printed beside it) ---------------
BRANCHES = {
    "34C1 (kick/launch: the 368D site)": [
        ("362C", "event 6 upgraded to 7 (8300 > 0x14)"), ("3655", "event 6 upgraded to 8 (45D and 2EB8 true)"),
        ("3670", "event in the set at 3481 (1, 2): the 278A site 368D"),
        ("36B0", "not in 3481: test the set at 34A1 (3, 4)"), ("36C0", "event in 34A1 (3, 4): the 278A site 36DA"),
        ("36F3", "event not in 1..4: the 287C site at 3722 follows the event-8, 8300 and 830B gates"),
        ("3676", "368D site: 8300 before"), ("36AA", "368D site: 8300 after (max of 8300+5 and (skill+pitch+0x11)/3)"),
        ("36F9", "event 8: skip"), ("3703", "8300 <= 1: skip"), ("370F", "830B == 830C: skip"),
        ("3712", "287C site set up"), ("3729", "287C returned non-zero: skip"), ("372C", "287C returned 0: the miscue path"),
        ("3742", "miscue: 045D(slot) true: skip"), ("3745", "miscue: coin"), ("3755", "miscue: halve branch (timer -= rand(timer/2))"),
        ("376B", "miscue: direction branch"), ("379D", "direction: 82FC != 0"), ("3772", "direction: 82FC == 0"),
        ("37AB", "82FE magnitude 1: cleared"), ("37B2", "82FE re-rolled"), ("37C2", "common tail"),
    ],
    "384C (pass to a slot: 287C at 39FC)": [
        ("39EF", "2DCA false: 287C(pitch, 10) is called"), ("3A00", "287C non-zero"), ("3A0F", "|bp-2| > 8: 82FC := 0"),
        ("3A16", "|bp-2| <= 8: 82FE adjusted"), ("3A2F", "tail"),
    ],
    "3C3F (shot/header: 287C at 3C89)": [
        ("3C47", "entry"), ("3C63", "8324 == 0 path"), ("3C8D", "287C returned 0: 06D0(4)"), ("3C9A", "06D0 false: 29B3"),
        ("3CA1", "80FB := 0"), ("3CA5", "80FB := 1"),
    ],
    "539F (the tackle's aftermath: 287C at 5401)": [
        ("53E3", "8303 == 0: coin"), ("53EC", "coin 0: 287C(holder, 3)"), ("5405", "win path (869F, template 0x0E)"),
        ("541E", "lose path: 8303 test"), ("5451", "5E41 and templates 0x0E, 0x21"),
    ],
    "5565 (challenge: 287C at 560F)": [
        ("55FE", "287C(pitch, 3) called"), ("5616", "result := 1 (from 287C non-zero at 5611, or from 55FC's jle when the product is <= 0)"),
        ("5675", "2B28 emitted, 5474 next"), ("5679", "after 5474"),
    ],
    "5F8A (loose-ball reaction: 287C at 6003, 6071, 60A8, 611C)": [
        ("5FE1", "8303 test"), ("5FF2", "8303 set, near: 287C(pitch, 4)"), ("6007", "that 287C non-zero"),
        ("601C", "2EB8 true: 408E"), ("602B", "2EB8 false"), ("6040", "2EF0 true: 3EDF"), ("604F", "2EF0 false: 5F06"),
        ("6060", "8303 clear, far: 287C(pitch, 3)"), ("6075", "that 287C non-zero: 5F06"), ("607C", "8303 clear, near"),
        ("6097", "2F28 true: 287C(pitch, 9)"), ("60AC", "that 287C non-zero"), ("60CC", "06D0 true: 3EC5"),
        ("60F1", "to the 8300 test"), ("6120", "contest passed or 8300 == 0"),
    ],
    "5474 (tackle roll: 54A1 and 54F2)": [
        ("54C4", "multiplier index 0 (8303 == 0 and 2C54 true)"), ("54C8", "multiplier index 1"), ("5500", "challenger roll > holder roll: 539F, result 1"),
        ("550A", "tail (result 0 when 5500 was not taken)"),
    ],
    "3B15 (long ball: 3B35)": [("3B4A", "after max(0x1E, rand(skill/4))")],
    "3EF8 (cross/long kick: 3F4B)": [("3F5E", "after max(floor, rand(skill/divisor))"), ("3F8E", "after 34C1")],
    "5B36 (keeper: 5D69; the duel 5BC4-5C1E)": [
        ("5B4A", "8325 == 0 and 8324 == 0: return"), ("5B4D", "past the first gate"), ("5B5A", "2B51 true: bail 5E25"),
        ("5B5D", "past 2B51"), ("5B6C", "8302 != 0: the flight block 5C88"), ("5B6F", "8302 == 0: the duel (5BC4-5C1E)"),
        ("5C8F", "8324 != 0: element := 1"), ("5C96", "8324 == 0: element from DS:07FE"), ("5CD3", "8324 != 0, 06D0(3) false: return"),
        ("5CD8", "8324 != 0, 06D0(3) true"), ("5D0F", "[bp-6] set"), ("5D22", "2EB8 false: 3FAD(9)"), ("5D32", "2EB8 true"),
        ("5D39", "8300 != 0: the 5D69 contest"), ("5D78", "contest lost (high word)"), ("5D7F", "contest lost (low word)"),
        ("5D82", "past the contest (won, or 8300 == 0)"), ("5D99", "8326 == 0 and event in 5B16 (1..4): 2996 and 3C20 (a statistics count)"),
        ("5DAE", "rand(4) = 1: reverse"), ("5DE9", "rand(4) = 2: sideways"), ("5E1F", "rand(4) = 3, 4: 5A8E"),
        ("5E25", "bail (2B51)"),
    ],
    "690C (penalty contest: call 6968)": [
        ("6912", "entry"), ("6919", "8327 > 4: 6755"), ("691F", "8327 <= 4"), ("692D", "7C39 == 0 and 80FB == 0"),
        ("693D", "8327 in 68EC (3, 4): the 278A site"), ("6976", "67B6"), ("697C", "6755"),
    ],
}

# the entry tallies: routine -> (arg names after pitch far pointer at +4; read as words from the stack)
def parse_listing():
    """address -> instruction text, for every instruction line of the 0791 listing files."""
    text = {}
    rx = re.compile(r"^([0-9A-F]{4})  (?:[0-9A-F]{2} )+\s+(.*)$")
    for p in sorted(CODE.glob(f"seg_{SEG}_*.asm")):
        for line in p.read_text().splitlines():
            m = rx.match(line)
            if m:
                text.setdefault(m.group(1), (p.name, m.group(2).strip()))
    return text


def signed16(w):
    return w - 0x10000 if w & 0x8000 else w


def run_record(path, listing, out):
    record = json.loads(path.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-watchstart.sav"))
    m = WatchedMatch(asset(entry))
    ds = m.DS * 16

    def stack(k):                       # the k-th word above SS:SP
        return m.stack_word(2 * k)

    calls278 = Counter()                # (return IP) -> count
    elem278 = Counter()                 # (return IP, element) -> count
    calls287 = Counter()                # (return IP, element) -> count
    res287_el = Counter()               # (return IP, element, result) -> count
    res287 = Counter()                  # (return IP, AL != 0) -> count
    ev34 = Counter()                    # (return IP, event) -> count
    enter = {}                          # routine -> Counter of key tuples
    hits = Counter()                    # branch address -> count
    state = {}

    def hook(off, fn):
        lin = m.lin(f"{SEG}:{off}")
        m.mu.hook_add(UC_HOOK_CODE, fn, begin=lin, end=lin)

    def need(off):
        if off not in listing:
            raise SystemExit(f"hook {off} is not an instruction start of the listing")

    # 278A entry: [sp] = return IP, [sp+2] = CS, [sp+4:+6] = pitch far pointer, [sp+8] = element
    def e278(uc, addr, size, data):
        ip, element = stack(0), stack(4)
        calls278[f"{ip:04X}"] += 1
        elem278[(f"{ip:04X}", element)] += 1
    hook("278A", e278)

    def e287(uc, addr, size, data):
        calls287[(f"{stack(0):04X}", stack(4))] += 1
        state["last287"] = stack(4)
    hook("287C", e287)

    def e34c1(uc, addr, size, data):    # args: [sp+4:+6] pitch, [sp+8] event, [sp+10] target word
        ev34[(f"{stack(0):04X}", stack(4))] += 1
    hook("34C1", e34c1)

    def tally(routine, keyfn):
        enter[routine] = Counter()

        def fn(uc, addr, size, data):
            enter[routine][keyfn()] += 1
        hook(routine, fn)

    byte = lambda off: m.rd(off, 1)
    tally("5B36", lambda: (f"ret {stack(0):04X}", f"8302={byte(0x8302)}", f"8324={byte(0x8324)}", f"8325={byte(0x8325)}", f"8326={byte(0x8326)}", f"8327={byte(0x8327)}"))
    tally("5474", lambda: (f"8303={byte(0x8303)}", f"8327={byte(0x8327)}"))
    tally("690C", lambda: (f"8327={byte(0x8327)}", f"7C39={byte(0x7C39)}", f"80FB={byte(0x80FB)}"))
    tally("3C3F", lambda: (f"ret {stack(0):04X}", f"event={stack(4)}"))
    def b_of_3ef8():
        state["3ef8_b"] = 1 if stack(4) == 9 else 0      # 3F09 cmp [bp+0xA], 9 -> [bp-3]
        return (f"ret {stack(0):04X}", f"param={stack(4)}")
    tally("3EF8", b_of_3ef8)
    tally("3B15", lambda: (f"ret {stack(0):04X}",))

    # the result of every 287C call: AL at the `or al, al` the call returns to
    for off in S287C:
        need(off)

        def r(uc, addr, size, data, off=off):
            res287[(off, "non-zero" if m.reg("eax") & 0xFF else "zero")] += 1
            res287_el[(off, state["last287"], "non-zero" if m.reg("eax") & 0xFF else "zero")] += 1
        hook(off, r)

    # branch hooks; two of them also read values (368D site: 8300 before and after)
    for group, items in BRANCHES.items():
        for off, label in items:
            need(off)

            def fn(uc, addr, size, data, off=off):
                hits[off] += 1
                if off == "3676":
                    state["8300_before"] = m.rd(0x8300)
                elif off == "36AA":
                    after = m.reg("eax") & 0xFFFF
                    key = ("368D: 8300 = 8300 + 5 (kept)" if after == (state["8300_before"] + 5) & 0xFFFF
                           else "368D: 8300 raised by the skill term")
                    hits[key] += 1
                elif off == "3B4A":
                    hits["3B35: result = 0x1E (floor)" if (m.reg("eax") & 0xFFFF) == 0x1E else "3B35: result > 0x1E (rolled)"] += 1
                elif off == "3F5E":
                    hits["3F4B: floor applied" if (m.reg("eax") & 0xFFFF) == m.rd(0x79C + state["3ef8_b"], 1) else "3F4B: rolled above the floor"] += 1
            hook(off, fn)

    m.run(timeout_s=1800)
    w = lambda s="": out.append(s)
    w(f"{record['run_id']}: ticks {m.final['ticks']}, score {m.final['score']}")
    w("  -- 278A calls by return address (run-time CS = image 0791)")
    for ret, n in EXPECTED_CALLS.items():
        w(f"  {ret}: {calls278[ret]} (expected {n}) {'OK' if calls278[ret] == n else 'MISMATCH'}")
    for ret, label in UNREACHED_CALLS.items():
        w(f"  {ret}: {calls278[ret]}  [unreached site: {label}]")
    for ret, label in SELECTION_CALLS.items():
        w(f"  {ret}: {calls278[ret]}  [selection site: {label}]")
    w("  -- elements passed to 278A per Scope-1 return address (ret: element x count)")
    for ret in EXPECTED_CALLS:
        w(f"  {ret}: " + ", ".join(f"{e}x{n}" for (r, e), n in sorted(elem278.items()) if r == ret))
    for ret in SELECTION_CALLS:
        w(f"  {ret}: " + ", ".join(f"{e}x{n}" for (r, e), n in sorted(elem278.items()) if r == ret))
    w("  -- 287C: calls by return address and element; result = AL at the return address")
    for ret, label in S287C.items():
        els = ", ".join(f"{e}x{n}" for (r, e), n in sorted(calls287.items()) if r == ret)
        w(f"  {ret} [{label}]: elements {els}; AL non-zero {res287[(ret, 'non-zero')]}, zero {res287[(ret, 'zero')]}")
    for (ret, el, res), n in sorted(res287_el.items()):
        w(f"  {ret} element {el}: AL {res} x {n}")
    w(f"  287C calls in all: {sum(calls287.values())}")
    w("  -- 34C1 entries by return address and event code (the event is the argument at bp+0xA)")
    for (ret, ev), n in sorted(ev34.items()):
        w(f"  ret {ret}, event {ev}: {n}")
    w("  -- routine entries by state (the globals read at the entry)")
    for routine, c in enter.items():
        for key, n in sorted(c.items()):
            w(f"  {routine} {' '.join(key)}: {n}")
    w("  -- branches (address: count; the listing line)")
    for group, items in BRANCHES.items():
        w(f"  {group}")
        for off, label in items:
            fname, text = listing[off]
            w(f"    {off} {hits[off]:6d}  {label}   [{fname}: {text}]")
    for key in sorted(k for k in hits if not re.fullmatch(r"[0-9A-F]{4}", k)):
        w(f"    {key}: {hits[key]}")
    ok = all(calls278[r] == n for r, n in EXPECTED_CALLS.items())
    return ok


def main():
    listing = parse_listing()
    out = []
    ok = True
    for p in sorted((ROOT / "runs/E011").glob("E011-r*.json")):
        ok &= run_record(p, listing, out)
        print(f"{p.name} done", flush=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = HERE / "out" / f"probe-{stamp}.log"
    target.parent.mkdir(exist_ok=True)
    with open(target, "x") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))
    print(f"log: {target.relative_to(ROOT)}")
    if not ok:
        raise SystemExit("a Scope-1 call count differs from the Evidence")


if __name__ == "__main__":
    main()
