#!/usr/bin/env python3
"""T60: each ported routine against the original on random inputs (the evidence behind "exact" for the branches the
families do not reach, and a first check for the ones they do).

For each trial the same memory (the reference image plus random bytes in a scratch segment and the routine's own tables)
and the same registers and stack arguments are given to two machines: one runs the original's code from the routine's entry
to its return, the other the port in its place (runtime/original_match/port). Compared at the return: AX, BX, CX, DX, SI, DI,
BP, SP, DS, ES, SS, CS:IP and the direction flag (a difference in BX, CX, SI, DI, ES is "scratch", the proof's term, and
is counted apart; any other difference fails), the arithmetic flags when --flags, and every byte of guest memory but the
callee's dead stack frame (below the return SP). The original's bytes are read at run time from the image (.cache/dl,
verified by hash, rule 18); nothing of them is written to the tree.

    python3 -B experiments/E036-match-port/out/T60/fuzz.py --module runtime [--routine 214B:0000] [--n 200] [--seed 1]
"""
import argparse
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from original_match import Image, port                                       # noqa: E402
from original_match.assets import reference_image                           # noqa: E402
from original_match.machine import Machine, MEM_SIZE                        # noqa: E402

DATA = 0x9000                      # a scratch segment of random bytes (linear 0x90000)
SS, SP0 = 0xA000, 0xF000           # the stack
SCRATCH_REGS = ("bx", "cx", "si", "di", "es")
STRICT_REGS = ("ax", "dx", "bp", "sp", "ds", "ss", "cs", "eip")
ARITH = 0x8D5
DF = 0x400


class Trial:
    """What one trial gives both machines: stack words (arg 0 first), memory writes, register overrides."""

    def __init__(self, rnd):
        self.rnd = rnd
        self.args = []
        self.writes = []            # (linear, bytes)
        self.regs = {}
        self.note = ""

    def ptr(self, off=None, span=0x200):
        off = self.rnd.randrange(0x100, 0x1800 - span) if off is None else off
        return off, DATA

    def random_bytes(self, linear, n):
        self.writes.append((linear, bytes(self.rnd.randrange(256) for _ in range(n))))

    def poke(self, linear, data):
        self.writes.append((linear, bytes(data)))


def setup(image_cache):
    img = Image.from_bytes(reference_image(image_cache))
    memory = bytes(img.memory[:MEM_SIZE]).ljust(MEM_SIZE, b"\0")
    return img, memory


def make_machine(img, memory, module, variant=None):
    m = Machine(bytearray(memory), img.load)
    inst = port.install(m, [f"{module}.{variant}" if variant else module]) if module else None
    return m, inst


def run_one(m, entry_far, target, args, regs, timeout=10):
    """Start the routine at target ('SSSS:OOOO') with the stack words `args` (arg 0 nearest the return address) and the
    registers `regs`, and run to its return. A far routine returns to a scratch segment, a near one to its own."""
    m.stop_reason = None
    tseg, toff = target.split(":")
    cs = m.seg(int(tseg, 16))
    ret_cs, ret_ip = (0x9F00, 0x0010) if entry_far else (cs, 0x0010)
    layout = [ret_ip] + ([ret_cs] if entry_far else []) + [a & 0xFFFF for a in args]    # from the stack pointer up
    sp = SP0 - 2 * len(layout) - 8
    for i, w in enumerate(layout):
        m.write(SS * 16 + sp + 2 * i, (w & 0xFFFF).to_bytes(2, "little"))
    for name, value in (("ss", SS), ("ds", m.DS), ("es", regs.get("es", m.DS)), ("sp", sp), ("bp", regs.get("bp", 0)),
                        ("eflags", regs.get("eflags", 0x202)), ("cs", cs), ("eip", int(toff, 16))):
        m.set_reg(name, value)
    for name in ("ax", "bx", "cx", "dx", "si", "di"):
        m.set_reg(name, regs.get(name, 0))
    reason = m.run(ret_cs * 16 + ret_ip, timeout_s=timeout, fresh=True)
    return sp, reason


def final(m):
    return {r: m.reg(r) for r in ("ax", "bx", "cx", "dx", "si", "di", "bp", "sp", "ds", "es", "ss", "cs", "eip", "eflags")}


STACK_DETAIL = False
IGNORE_FRAME = False        # --ignore-frame: leave the callee's dead stack frame out of the memory comparison (T60's first rule)


def compare(a, b, mem_a, mem_b, sp_entry, flags):
    problems, scratch = [], []
    for r in STRICT_REGS:
        key = "eip" if r == "eip" else r
        if (a[key] & 0xFFFF) != (b[key] & 0xFFFF):
            problems.append(f"{r.upper()}: original {a[key] & 0xFFFF:04X}, port {b[key] & 0xFFFF:04X}")
    for r in SCRATCH_REGS:
        if (a[r] & 0xFFFF) != (b[r] & 0xFFFF):
            scratch.append(r)
    if (a["eflags"] ^ b["eflags"]) & DF:
        problems.append(f"DF: original {bool(a['eflags'] & DF)}, port {bool(b['eflags'] & DF)}")
    if flags and (a["eflags"] ^ b["eflags"]) & ARITH:
        problems.append(f"flags: original {a['eflags'] & ARITH:03X}, port {b['eflags'] & ARITH:03X}")
    if mem_a != mem_b:
        lo = SS * 16 + (a["sp"] - 0x1800)             # the callee's dead stack frame: below its return SP
        hi = SS * 16 + a["sp"]
        if not IGNORE_FRAME:                         # the digests of DS include the stack's residue: compare it too
            lo = hi = 0
        diffs = []
        n = len(mem_a)
        # find differing bytes quickly by blocks
        step = 4096
        for base in range(0, n, step):
            if mem_a[base:base + step] != mem_b[base:base + step]:
                for i in range(base, min(base + step, n)):
                    if mem_a[i] != mem_b[i] and not lo <= i < hi:
                        diffs.append(i)
        if diffs:
            rel = [d - (SS * 16 + sp_entry) for d in diffs]
            where = "stack, entry SP%+d.." % rel[0] if all(abs(r) < 0x2100 for r in rel) else "linear 0x%05X" % diffs[0]
            problems.append("memory: %d bytes differ, first at %s (original %02X, port %02X)"
                            % (len(diffs), where, mem_a[diffs[0]], mem_b[diffs[0]]))
            if STACK_DETAIL:
                problems.append("diff offsets from the entry SP: " + " ".join("%+d" % r for r in rel[:40]))
    return problems, scratch


def fuzz(module, routines, n, seed, flags, cache, verbose, variant=None, timeout=3):
    import generators_geometry  # noqa: F401  (registers the geometry generators)
    from generators import GENERATORS
    img, memory = setup(cache)
    mo, _ = make_machine(img, memory, None)
    mp, inst = make_machine(img, memory, module, variant)
    registry = port._module_registry(module)
    total_fail = 0
    for address in routines:
        entry = registry.entries[address]
        gen = GENERATORS.get(address)
        if gen is None:
            print(f"{address}: no generator")
            total_fail += 1
            continue
        rnd = random.Random(f"{seed}/{address}")
        seg_c = address.split(":")[0]
        fails, errors, scratch_counts, t0 = 0, 0, {}, time.time()
        for t in range(n):
            tr = Trial(rnd)
            gen(tr, img)
            garbage = bytes(rnd.randrange(1, 256) for _ in range(0x2000))
            outs = []
            for m in (mo, mp):
                m.write(0, memory)
                m.write(DATA * 16, bytes(0x10000))
                m.write(SS * 16 + SP0 - 0x2000, garbage)        # old stack bytes: the dead frames overwrite them or not
                for linear, data in tr.writes:
                    m.write(linear, data)
                regs = dict(tr.regs)
                try:
                    sp, reason = run_one(m, entry.far, address, tr.args, regs, timeout)
                    outs.append((final(m), bytes(m._uc.mem_read(0, MEM_SIZE)), sp, None))
                except Exception as e:          # a guest error: the same on both is not a difference
                    outs.append((None, None, None, f"{type(e).__name__}: {str(e)[:100]}"))
            (fa, ma, spa, ea), (fb, mb, spb, eb) = outs
            if ea or eb:
                if (ea is None) != (eb is None) or (ea and not (ea.split(":")[0] == eb.split(":")[0])):
                    fails += 1
                    print(f"{address} trial {t}: original {ea}, port {eb} {tr.note}")
                else:
                    errors += 1
                continue
            problems, scratch = compare(fa, fb, ma, mb, spa, flags)
            for r in scratch:
                scratch_counts[r] = scratch_counts.get(r, 0) + 1
            if problems:
                fails += 1
                if fails <= 5 or verbose:
                    print(f"{address} trial {t}: " + "; ".join(problems) + f" {tr.note} args={[hex(a) for a in tr.args]}")
        total_fail += 1 if fails else 0
        print(f"{address}: {n} trials ({errors} ended in the same guest error), {fails} differ, scratch registers differing: {scratch_counts or 'none'} "
              f"({time.time() - t0:.1f} s)")
    return total_fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", required=True)
    ap.add_argument("--routine")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", default="1")
    ap.add_argument("--flags", action="store_true")
    ap.add_argument("--variant", help="run the port's variant (it must DIFFER from the original: a control)")
    ap.add_argument("--cache", default=".cache/dl")
    ap.add_argument("--timeout", type=float, default=3, help="seconds a run may take before it counts as a guest error")
    ap.add_argument("--ignore-frame", action="store_true")
    ap.add_argument("--stack-detail", action="store_true")
    ap.add_argument("-v", action="store_true")
    a = ap.parse_args()
    global IGNORE_FRAME, STACK_DETAIL
    IGNORE_FRAME, STACK_DETAIL = a.ignore_frame, a.stack_detail
    registry = port._module_registry(a.module)
    routines = [a.routine] if a.routine else sorted(registry.entries)
    return 1 if fuzz(a.module, routines, a.n, a.seed, a.flags, a.cache, a.v, a.variant, a.timeout) else 0


if __name__ == "__main__":
    sys.exit(main())
