#!/usr/bin/env python3
"""T59 (review round 1, R1): is a register's value at a point of GOAL.EXE ever read? A static liveness search over the
listing (static/goal-exe/code/*.asm), the evidence for a proof exception that a ported routine's AX or DX at one return
address is dead (port/prove.py RESULT_DEAD).

    python3 -B experiments/E036-match-port/out/T59/liveness.py --at 0791:8BB7 --reg ax --reg dx

From the point, every path is followed, its halves (al/ah, dl/dh) tracked separately: a half is dead on a path once an
instruction writes it before any reads it; the value is LIVE if some path reads a half that is still the point's.
Calls are followed into the callee (near, and far `call far SSSS:OOOO`) and back; a return with no call of the search's
own on the stack goes to the instruction after every call of the routine that holds it (static/goal-exe/routines.tsv
and the listings' calls), so the search climbs to the callers' callers. Conservative everywhere it cannot see: an
indirect call or jump, an `int`, a mnemonic whose register effects are not modelled, an address with no listing line,
or a search deeper than its limit count as a READ. So DEAD is a proof over the listing; LIVE may be a false alarm.
Prints DEAD or LIVE (with the path that reads) per register; exit 0 when every register asked is dead."""
import argparse
import bisect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CODE = ROOT / "static/goal-exe/code"
LINE = re.compile(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)\s*([a-z]\S*)\s*(.*)$")   # bytes upper case, mnemonic lower
HALVES = {"ax": {"al", "ah"}, "dx": {"dl", "dh"}, "eax": {"al", "ah"}, "edx": {"dl", "dh"},
          "al": {"al"}, "ah": {"ah"}, "dl": {"dl"}, "dh": {"dh"}}
WRITE_FIRST = {"mov", "lea", "les", "lds", "pop", "movzx", "movsx", "in"}
SAME_KILL = {"xor", "sub", "sbb"}
NO_REGS = {"nop", "clc", "stc", "cld", "std", "cli", "sti", "cmc", "push", "pushf", "popf", "leave", "enter", "wait",
           "les", "lds", "hlt"}
# Implicit register effects: (reads, writes) as halves; a byte (b) or word (w) form where they differ.
IMPLICIT = {
    "cwde": ({"al"}, {"ah"}),                    # 98: cbw in 16-bit code (the listing spells it cwde)
    "cdq": ({"ah"}, {"dl", "dh"}),               # 99: cwd
    "cbw": ({"al"}, {"ah"}), "cwd": ({"ah"}, {"dl", "dh"}),
    "lahf": (set(), {"ah"}), "sahf": ({"ah"}, set()),
    "xlatb": ({"al"}, {"al"}), "xlat": ({"al"}, {"al"}),
    "aam": ({"al"}, {"al", "ah"}), "aad": ({"al", "ah"}, {"al", "ah"}),
    "daa": ({"al"}, {"al"}), "das": ({"al"}, {"al"}), "aaa": ({"al", "ah"}, {"al", "ah"}),
    "aas": ({"al", "ah"}, {"al", "ah"}),
    "lodsb": (set(), {"al"}), "lodsw": (set(), {"al", "ah"}),
    "stosb": ({"al"}, set()), "stosw": ({"al", "ah"}, set()),
    "scasb": ({"al"}, set()), "scasw": ({"al", "ah"}, set()),
    "movsb": (set(), set()), "movsw": (set(), set()), "cmpsb": (set(), set()), "cmpsw": (set(), set()),
}
ALL = {"al", "ah", "dl", "dh"}


def seg_of(path):
    return path.stem.split("_")[1]


def load():
    code = {}                  # (seg, off) -> (mnemonic, operands, next offset, text)
    for f in sorted(CODE.glob("*.asm")):
        seg = seg_of(f)
        prev = None
        for line in f.read_text().splitlines():
            m = LINE.match(line)
            if not m:
                continue
            off = int(m.group(1), 16)
            size = len(m.group(2).split())
            mn, ops = m.group(3), m.group(4).strip()
            if mn in ("rep", "repe", "repne", "repz", "repnz", "lock") and ops:
                mn, _, ops = ops.partition(" ")
            code[(seg, off)] = (mn, ops, off + size, line.strip())
    starts = {}
    for line in (ROOT / "static/goal-exe/routines.tsv").read_text().splitlines():
        first = line.split("\t")[0]
        if line.startswith(";") or not re.fullmatch(r"[0-9A-F]{4}:[0-9A-F]{4}", first):
            continue
        s, o = first.split(":")
        starts.setdefault(s, []).append(int(o, 16))
    for s in starts:
        starts[s].sort()
    callers = {}               # routine (seg, off) -> [(seg, off of the instruction after the call)]
    for (seg, off), (mn, ops, nxt, _) in code.items():
        t = target(seg, mn, ops)
        if mn.startswith("call") and t is not None:
            callers.setdefault(t, []).append((seg, nxt))
    return code, starts, callers


def target(seg, mn, ops):
    m = re.fullmatch(r"far ([0-9A-F]{4}):([0-9A-F]{4})", ops)
    if m:
        return m.group(1), int(m.group(2), 16)
    m = re.fullmatch(r"0x([0-9a-f]+)", ops)
    if m:
        return seg, int(m.group(1), 16) & 0xFFFF       # a near target wraps in its segment (`call 0x10425`)
    return None


def routine_of(starts, seg, off):
    lst = starts.get(seg, [])
    i = bisect.bisect_right(lst, off) - 1
    return (seg, lst[i]) if i >= 0 else None


def regs_in(text):
    out = set()
    for tok in re.findall(r"\b(e?[ad]x|[ad][lh])\b", text):
        out |= HALVES[tok]
    return out


def effects(mn, ops):
    """(reads, writes) halves of al/ah/dl/dh, or None when not modelled."""
    if mn in IMPLICIT:
        return IMPLICIT[mn]
    parts = [p.strip() for p in split_ops(ops)]
    if mn in ("mul", "imul", "div", "idiv") and len(parts) == 1:
        byte = "byte" in parts[0] or re.fullmatch(r"[a-d][lh]", parts[0])
        src = regs_in(parts[0])
        if mn in ("mul", "imul"):
            return ({"al"} | src, {"al", "ah"}) if byte else ({"al", "ah"} | src, {"al", "ah", "dl", "dh"})
        return ({"al", "ah"} | src, {"al", "ah"}) if byte else (ALL | src, ALL)
    if mn == "imul":                                     # two or three operands: dest := src * ...
        return (regs_in(" ".join(parts[1:])), regs_in(parts[0]) if not parts[0].count("[") else set())
    if mn in ("in",):
        return (regs_in(parts[1]) if len(parts) > 1 else set(), regs_in(parts[0]))
    if mn == "out":
        return (regs_in(ops), set())
    if mn.startswith("int") or mn in ("into",):
        return None
    if mn in NO_REGS and not regs_in(ops):
        return (set(), set())
    if mn in ("push",):
        return (regs_in(ops), set())
    if not parts or parts == [""]:
        return (set(), set()) if mn in NO_REGS or mn.startswith(("ret", "j", "loop")) else None
    dest, rest = parts[0], " ".join(parts[1:])
    dest_regs = regs_in(dest) if "[" not in dest else set()
    mem_regs = regs_in(dest) if "[" in dest else set()
    if mn in WRITE_FIRST:
        return (regs_in(rest) | mem_regs, dest_regs)
    if mn in SAME_KILL and len(parts) == 2 and parts[0] == parts[1]:
        return (set(), dest_regs)
    if mn == "xchg":
        return (regs_in(ops), regs_in(ops))
    return (regs_in(ops), dest_regs)                     # read-modify-write, compares, tests, shifts


def split_ops(ops):
    out, depth, cur = [], 0, ""
    for ch in ops:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + [cur] if cur or out else []


def search(code, starts, callers, seg, off, halves, limit=200000, max_stack=24, climbed=None):
    """None when every path writes each half before reading it, else (reason, path). climbed: a set the routines
    returned from to their listed callers are added to (the search relies on their callers being all listed)."""
    seen = set()
    work = [((seg, off), frozenset(halves), (), ())]
    steps = 0
    while work:
        (s, o), live, stack, path = work.pop()
        key = ((s, o), live, stack)
        if key in seen:
            continue
        seen.add(key)
        steps += 1
        if steps > limit:
            return ("the search's limit", path)
        ins = code.get((s, o))
        if ins is None:
            return (f"no listing line at {s}:{o:04X}", path)
        mn, ops, nxt, text = ins
        path2 = (path + (text,))[-12:]
        if mn.startswith("ret") or mn == "iret":
            if stack:
                work.append((stack[-1], live, stack[:-1], path2))
            else:
                r = routine_of(starts, s, o)
                ups = callers.get(r, [])
                if not ups:
                    return (f"a return from {r[0]}:{r[1]:04X}, which has no listed caller", path2)
                if climbed is not None:
                    climbed.add(f"{r[0]}:{r[1]:04X}")
                for up in ups:
                    work.append((up, live, (), path2))
            continue
        if mn.startswith("call"):
            t = target(s, mn, ops)
            if t is None:
                return (f"an indirect call at {s}:{o:04X}", path2)
            if len(stack) >= max_stack:
                return ("the call depth limit", path2)
            work.append((t, live, stack + ((s, nxt),), path2))
            continue
        eff = effects(mn, ops)
        if eff is None:
            return (f"an unmodelled instruction: {text}", path2)
        reads, writes = eff
        if reads & live:
            return ("a read", path2)
        live2 = live - writes
        if not live2:
            continue
        if mn == "jmp":
            t = target(s, mn, ops)
            if t is None:
                return (f"an indirect jump at {s}:{o:04X}", path2)
            work.append((t, live2, stack, path2))
            continue
        if mn.startswith(("j", "loop")):
            t = target(s, mn, ops)
            if t is None:
                return (f"an indirect jump at {s}:{o:04X}", path2)
            work.append((t, live2, stack, path2))
        work.append(((s, nxt), live2, stack, path2))
    return None


# The search's controls (`--controls`): points whose answer the listing shows at a glance (seg_0791_12.asm,
# seg_0791_05.asm). A read in the same routine, a read after a return in the caller, and a write before any read.
CONTROLS = (("0791:6E26", "ax", "LIVE", "6E26 or al, al reads 2996's result"),
            ("0791:2BF9", "dx", "LIVE", "2BF9 cmp dx, bx"),
            ("0791:2A9F", "ax", "LIVE", "2A6D's result, read by its caller 2AA3 at 2AC6 push ax (after the return)"),
            ("0791:2C13", "dx", "DEAD", "2C13 pop dx writes DX before 2C14 reads DL"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--at")
    ap.add_argument("--reg", action="append", choices=("ax", "dx"))
    ap.add_argument("--controls", action="store_true")
    a = ap.parse_args(argv)
    code, starts, callers = load()
    if a.controls:
        ok = True
        for at, reg, want, why in CONTROLS:
            s, o = at.split(":")
            got = "DEAD" if search(code, starts, callers, s, int(o, 16), HALVES[reg]) is None else "LIVE"
            ok = ok and got == want
            print(f"{reg.upper()} at {at}: {got} (expected {want}: {why})")
        print("controls " + ("all as expected" if ok else "NOT as expected"))
        return 0 if ok else 1
    seg, off = a.at.split(":")
    ok = True
    for reg in a.reg:
        climbed = set()
        found = search(code, starts, callers, seg, int(off, 16), HALVES[reg], climbed=climbed)
        if found is None:
            print(f"{reg.upper()} at {a.at}: DEAD on every path (each half written before it is read); returns followed "
                  f"to every listed caller: {', '.join(sorted(climbed)) or 'none'}")
        else:
            ok = False
            print(f"{reg.upper()} at {a.at}: LIVE or not shown dead: {found[0]}; the path's last instructions:")
            for t in found[1]:
                print("    " + t)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
