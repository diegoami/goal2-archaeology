"""T61: each ported routine of port/attributes.py run against the original's, on the same synthetic state, and the whole of
guest memory and the registers compared after the return (the dead stack frames included, which the proof mode leaves out:
the families' memory digests cover the stack, so a port must leave the stack bytes the original leaves).

    python3 -B experiments/E036-match-port/out/T61/diffcheck.py [--routines 1771:3216,...] [--cases N] [--seed S]
                                                               [--out FILE] [--variant NAME]

The state is the reference image (E006-r0001, fetched by hash into .cache/dl) with random edits of the arrays the
routines read (players, countries, managers, the two teams' words and the marking words), random arguments and random
entry registers; case k of a routine is made from (seed, routine, k) alone. For each case the original's routine and the
port (all of port/attributes.py installed, so its routines call each other's ports as the port does in a match) run from
the same state; the result is the AX, DX, SP, BP, CS, IP, DS, SS of the proof's REGS_RETURNED (compared), the scratch
registers (counted), and every byte of the 1.1 MiB of guest memory (compared). No byte of the original is written out."""
import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image, port  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
from original_match.machine import Machine, MEM_SIZE  # noqa: E402
from original_match.port import attributes  # noqa: E402

SS_PARA, SP_TOP = 0xAD1, 0x3F00     # the stack: SS = DS + 0xAD1 (the match's SS, 0x3875 over DS 0x2DA4), SP below its top 0x4000
END = "0791:0000"                   # the return address of every call: never executed
RETURNED = ("ax", "dx", "sp", "bp", "cs", "ip", "ds", "ss")
SCRATCH = ("bx", "cx", "si", "di", "es")
SCRATCH_AREA = 0xF000               # DS:F000.. is free: a destination string for 0E6C and 2E93, a fixture for 5A03


class Routine:
    def __init__(self, address, ret, make_args, near=False):
        self.address, self.ret, self.make_args, self.near = address, ret, make_args, near


def rand_player(r):
    b = bytearray(r.randrange(256) for _ in range(0x14))
    if r.random() < 0.9:
        b[6] = r.randrange(0, 15)
    if r.random() < 0.9:
        b[7] = r.randrange(0, 15)
    if r.random() < 0.3:
        b[5] = r.randrange(0, 31)
        b[2] = 30 - b[5]
    if r.random() < 0.5:
        b[0xE] = r.choice((0, 1, 2, 0x7F, 0x80, 0xFF, r.randrange(256)))
    if r.random() < 0.5:
        b[0xC] = r.choice((0, 0x1F, 0x20, 0x21, 0x7F, 0x80, 0xFF, r.randrange(256)))
    if r.random() < 0.5:
        b[1] = r.choice((0, 0x14, 0x15, 0x16, r.randrange(256)))
    if r.random() < 0.4:
        b[0x10] = r.choice((0, 0x04, 0x20, 0x80, 0xA4, r.randrange(256)))
    if r.random() < 0.4:
        b[0xF] = r.choice((0, 0xFF, r.randrange(256)))
    return bytes(b)


def make_state(image_bytes, load, r):
    """A Machine on the reference image with random edits of the records the routines read."""
    memory = bytearray(image_bytes)
    ds = (load + 0x2581) * 16

    def far(off):
        return int.from_bytes(memory[ds + off + 2:ds + off + 4], "little") * 16 + int.from_bytes(memory[ds + off:ds + off + 2], "little")
    players, countries, managers = far(0xA91B), far(0xA917), far(0xA91F)
    for n in r.sample(range(0, 3061), 400):
        memory[players + 0x14 * n:players + 0x14 * n + 0x14] = rand_player(r)
    for c in range(0, 129):
        rec = bytearray(memory[countries + 0xBF * c:countries + 0xBF * c + 0xBF])
        for k in range(20):
            rec[2 * k:2 * k + 2] = (0 if r.random() < 0.1 else r.randrange(0, 3061)).to_bytes(2, "little")
        rec[0x2D] = r.randrange(256)
        rec[0x2E] = r.choice((c & 0xFF, 0x80, 0x81, 0x85, r.randrange(256)))
        rec[0x2C] = r.randrange(0, 16)
        memory[countries + 0xBF * c:countries + 0xBF * c + 0xBF] = rec
    for k in range(3 * 0x90):
        memory[managers + k] = r.randrange(256)
    teams = r.sample(range(1, 129), 2)
    memory[ds + 0x9B34:ds + 0x9B38] = teams[0].to_bytes(2, "little") + teams[1].to_bytes(2, "little")
    for k in range(0x9A3E, 0x9A3E + 0x50):
        memory[ds + k] = r.randrange(256)
    for k in range(SCRATCH_AREA, SCRATCH_AREA + 0x100):
        memory[ds + k] = r.randrange(256)
    return memory


def player_arg(r):
    return r.choice((0, 1, 3060, r.randrange(0, 3061), r.randrange(0, 3061), r.randrange(0, 3061)))


def country_arg(r):
    return r.choice((1, 128, 0, r.randrange(1, 129), r.randrange(1, 129), r.randrange(1, 129)))


def routines():
    p, c = player_arg, country_arg
    R = [
        Routine("1771:0AA7", "retf 2", lambda r: [c(r)]),
        Routine("1771:0B77", "retf 2", lambda r: [c(r)]),
        Routine("1771:0E24", "ret 2", lambda r: [c(r)], near=True),
        Routine("1771:0E6C", "retf 2", lambda r: [-1, SCRATCH_AREA, c(r)]),
        Routine("1771:2E20", "retf 4", lambda r: [p(r), r.randrange(0, 15)]),
        Routine("1771:2E93", "retf 2", lambda r: [-1, SCRATCH_AREA, p(r)]),
        Routine("1771:2FAD", "retf 2", lambda r: [p(r)]),
        Routine("1771:2FFB", "retf 2", lambda r: [p(r)]),
        Routine("1771:3041", "retf 2", lambda r: [p(r)]),
        Routine("1771:3088", "retf 2", lambda r: [p(r)]),
        Routine("1771:30D9", "retf 2", lambda r: [p(r)]),
        Routine("1771:3179", "retf 2", lambda r: [p(r)]),
        Routine("1771:3216", "retf 2", lambda r: [p(r)]),
        Routine("1771:33CD", "retf 2", lambda r: [p(r)]),
        Routine("1771:3431", "retf 2", lambda r: [p(r)]),
        Routine("1771:34E7", "retf 2", lambda r: [c(r)]),
        Routine("1771:377E", "retf 2", lambda r: [p(r)]),
        Routine("1771:3A06", "retf 4", lambda r: [p(r), r.randrange(1, 13)]),
        Routine("1771:3A82", "retf 4", lambda r: [p(r) if r.random() < 0.3 else 0, c(r)]),
        Routine("1771:3EF8", "retf", lambda r: []),
        Routine("1771:5A03", "retf 4", lambda r: [-1, SCRATCH_AREA + 0x80 - 2]),
    ]
    return {x.address: x for x in R}


def call_routine(machine, rt, args, regs, variant_specs):
    """Run rt on the machine with args pushed (the last nearest the return address) and the registers as given."""
    if variant_specs:
        port.install(machine, variant_specs)
    ds = machine.DS
    sp = SP_TOP
    rseg, roff = END.split(":")
    if rt.near:
        rseg = rt.address.split(":")[0]     # a near return stays in the routine's segment
    end = machine.lin(f"{rseg}:{roff}")
    words = [int(roff, 16)] + ([machine.seg(int(rseg, 16))] if not rt.near else []) + [machine.DS if a == -1 else a for a in reversed(args)]
    for i, w in enumerate(words):
        machine.write((ds + SS_PARA) * 16 + ((sp + 2 * i) & 0xFFFF), (w & 0xFFFF).to_bytes(2, "little"))
    tseg, toff = rt.address.split(":")
    for name, value in (("ss", ds + SS_PARA), ("sp", sp), ("ds", ds), ("es", ds), ("cs", machine.seg(int(tseg, 16))),
                        ("eip", int(toff, 16))):
        machine.set_reg(name, value)
    for name, value in regs.items():
        machine.set_reg(name, value)
    machine.run(end, timeout_s=60, fresh=True)
    return {r: machine.reg(r) for r in RETURNED + SCRATCH}, machine.read(0, MEM_SIZE)


def case(image, rt, seed, k, variant_specs=None):
    """One case: the result of the original and of the port on the same state (None, None, "" when they agree)."""
    r = random.Random(f"{seed}/{rt.address}/{k}")
    memory = make_state(image.memory, image.load, r)
    args = rt.make_args(r)
    regs = {n: r.randrange(0x10000) for n in ("ax", "bx", "cx", "dx", "si", "di", "bp")}
    out = []
    for specs in (None, variant_specs or [(attributes.PORTS, None)]):
        m = Machine(bytearray(memory), image.load)
        out.append(call_routine(m, rt, args, regs, specs))
    (ro, mo), (rp, mp) = out
    problems = []
    for name in RETURNED:
        if ro[name] != rp[name]:
            problems.append(f"{name.upper()}: original 0x{ro[name]:04X}, port 0x{rp[name]:04X}")
    scratch = [n for n in SCRATCH if ro[n] != rp[n]]
    if mo != mp:
        ds = image.load + 0x2581
        diffs = [i for i in range(len(mo)) if mo[i] != mp[i]] if len(mo) < 1 << 24 else []
        shown = []
        for i in diffs[:6]:
            ss = (ds + SS_PARA) * 16
            if ss <= i < ss + 0x10000:
                where = f"SS:{i - ss:04X} (entry SP {SP_TOP:04X}: bp{i - ss - (SP_TOP - 2):+#x})"
            elif ds * 16 <= i < ds * 16 + 0x10000:
                where = f"DS:{i - ds * 16:04X}"
            else:
                where = f"linear 0x{i:05X}"
            shown.append(f"{where} original 0x{mo[i]:02X} port 0x{mp[i]:02X}")
        problems.append(f"memory differs at {len(diffs)} bytes: " + "; ".join(shown))
    return args, regs, problems, scratch


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--routines")
    ap.add_argument("--cases", type=int, default=50)
    ap.add_argument("--seed", default="T61")
    ap.add_argument("--first", type=int, default=0)
    ap.add_argument("--variant")
    ap.add_argument("--out")
    ap.add_argument("--cache", default=".cache/dl")
    a = ap.parse_args(argv)
    image = Image.from_bytes(reference_image(a.cache))
    table = routines()
    names = a.routines.split(",") if a.routines else sorted(table)
    specs = [("attributes." + a.variant) if a.variant else "attributes"]
    loaded = port.load(specs)
    total = bad = 0
    log = open(a.out, "x") if a.out else None
    for name in names:
        rt = table[name]
        nbad = 0
        scratch_cases = 0
        for k in range(a.first, a.first + a.cases):
            args, regs, problems, scratch = case(image, rt, a.seed, k, loaded)
            total += 1
            scratch_cases += bool(scratch)
            if problems:
                bad += 1
                nbad += 1
                line = {"routine": name, "case": k, "args": args, "problems": problems}
                if nbad <= 3:
                    print(json.dumps(line))
                if log:
                    log.write(json.dumps(line) + "\n")
        print(f"{name}: {a.cases} cases, {nbad} differ (scratch registers differ in {scratch_cases})", flush=True)
        if log:
            log.write(json.dumps({"routine": name, "cases": a.cases, "differ": nbad, "scratch_cases": scratch_cases}) + "\n")
            log.flush()
    print(f"{total} cases, {bad} differ")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
