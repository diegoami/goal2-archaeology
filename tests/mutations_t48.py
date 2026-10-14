#!/usr/bin/env python3
"""T48: mutation check of the new tests, in memory (no tracked file is edited).

    python3 -B tests/mutations_t48.py

Each mutation replaces a text in the source of runtime/model/longs.py or experiments/E021-m0-whole-match/check.py,
compiles the mutated module in a CHILD process (one process per mutation), puts it in sys.modules, and runs the test
classes named for it; the mutation is killed when a test fails. A text that is absent, or a mutation that does not change
the source, is an ERROR (never counted as killed). Prints one line per mutation and exits non-zero when one survives.
`EQUIVALENT` mutations are shown with the reason they cannot change behaviour (so no test can kill them)."""
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LONGS = "runtime/model/longs.py"
CHECK = "experiments/E021-m0-whole-match/check.py"
ADAPTER = ["tests.test_emul_match.LongReaderTests", "tests.test_emul_match.LongProofTests"]
MODEL = ["tests.test_model_longs"]
KILLED, SURVIVED, ERROR = 3, 0, 4         # child exit codes

# (name, file, old text, new text, tests that must fail)
MUTATIONS = [
    # --- flags (longs.py): every term of each flag
    ("flags: CF term dropped", LONGS, "(CF if carry else 0)", "0", MODEL),
    ("flags: PF inverted", LONGS, "count(\"1\") % 2 == 0", "count(\"1\") % 2 == 1", MODEL),
    ("flags: PF of the whole word", LONGS, "bin(result & 0xFF)", "bin(result & 0xFFFF)", MODEL),
    ("flags: AF term dropped", LONGS, "(AF if aux else 0)", "0", MODEL),
    ("flags: ZF term dropped", LONGS, "(ZF if result == 0 else 0)", "0", MODEL),
    ("flags: SF term dropped", LONGS, "(SF if result & 0x8000 else 0)", "0", MODEL),
    ("flags: SF tests bit 14", LONGS, "(SF if result & 0x8000 else 0)", "(SF if result & 0x4000 else 0)", MODEL),
    ("flags: OF term dropped", LONGS, "(OF if overflow else 0)", "0", MODEL),
    ("sub flags: borrow x <= y", LONGS, "x < y,", "x <= y,", MODEL),
    ("sub flags: borrow x > y", LONGS, "x < y,", "x > y,", MODEL),
    ("sub flags: OF uses (x ^ y) only", LONGS, "(x ^ y) & (x ^ r) & 0x8000, (x ^ y ^ r) & 0x10)\n\n\ndef add16", "(x ^ y) & 0x8000, (x ^ y ^ r) & 0x10)\n\n\ndef add16", MODEL),
    ("sub flags: AF mask 0x08", LONGS, "(x ^ y ^ r) & 0x10)\n\n\ndef add16", "(x ^ y ^ r) & 0x08)\n\n\ndef add16", MODEL),
    ("add flags: carry x + y >= 0xFFFF", LONGS, "x + y > 0xFFFF", "x + y >= 0xFFFF", MODEL),
    ("add flags: carry dropped", LONGS, "x + y > 0xFFFF", "False", MODEL),
    ("add flags: OF as for a subtraction", LONGS, "~(x ^ y) & (x ^ r) & 0x8000", "(x ^ y) & (x ^ r) & 0x8000", MODEL),
    ("add flags: AF mask 0x08", LONGS, "~(x ^ y) & (x ^ r) & 0x8000, (x ^ y ^ r) & 0x10)", "~(x ^ y) & (x ^ r) & 0x8000, (x ^ y ^ r) & 0x08)", MODEL),
    # --- 214B:0D56 (longs.py max_0d56): each decision
    ("0D56: high words compared unsigned (jg/jl)", LONGS, "a_wins = s16(a_hi) > s16(b_hi)", "a_wins = a_hi > b_hi", MODEL),
    ("0D56: high words compared as less-than", LONGS, "a_wins = s16(a_hi) > s16(b_hi)", "a_wins = s16(a_hi) < s16(b_hi)", MODEL),
    ("0D56: low words compared SIGNED (jbe -> jle)", LONGS, "a_wins = a_lo > b_lo ", "a_wins = s16(a_lo) > s16(b_lo) ", MODEL),
    ("0D56: low words compared as less-than", LONGS, "a_wins = a_lo > b_lo ", "a_wins = a_lo < b_lo ", MODEL),
    ("0D56: equal high words go to the high compare", LONGS, "    if a_hi != b_hi:", "    if a_hi >= b_hi:", MODEL),
    ("0D56: low compare also when the high words differ", LONGS, "    if a_hi != b_hi:", "    if False:", MODEL),
    ("0D56: flags of the high compare always", LONGS, "flags = sub16_flags(a_lo, b_lo) ", "flags = sub16_flags(a_hi, b_hi) ", MODEL),
    ("0D56: flags of the low compare always", LONGS, "flags = sub16_flags(a_hi, b_hi) ", "flags = sub16_flags(a_lo, b_lo) ", MODEL),
    ("0D56: high compare flags with swapped operands", LONGS, "flags = sub16_flags(a_hi, b_hi) ", "flags = sub16_flags(b_hi, a_hi) ", MODEL),
    ("0D56: low compare flags with swapped operands", LONGS, "flags = sub16_flags(a_lo, b_lo) ", "flags = sub16_flags(b_lo, a_lo) ", MODEL),
    ("0D56: winner swapped", LONGS, "(a_lo, a_hi) if a_wins else (b_lo, b_hi)", "(b_lo, b_hi) if a_wins else (a_lo, a_hi)", MODEL),
    ("0D56: ES = the low word", LONGS, "return Max(lo, hi, hi, flags)", "return Max(lo, hi, lo, flags)", MODEL),
    ("0D56: DX = the low word", LONGS, "return Max(lo, hi, hi, flags)", "return Max(lo, lo, hi, flags)", MODEL),
    ("0D56: AX = the high word", LONGS, "return Max(lo, hi, hi, flags)", "return Max(hi, hi, hi, flags)", MODEL),
    ("0D56: flags dropped", LONGS, "return Max(lo, hi, hi, flags)", "return Max(lo, hi, hi, 0)", MODEL),
    # --- 23E4:0279 (longs.py mul_0279): each register, each term
    ("0279: SI = DX", LONGS, "si, di = ax, dx", "si, di = dx, ax", MODEL),
    ("0279: the low product uses BX", LONGS, "low = ax * cx", "low = ax * bx", MODEL),
    ("0279: the low product uses DX", LONGS, "low = ax * cx", "low = dx * cx", MODEL),
    ("0279: the carry (high word of the low product) dropped", LONGS, "partial = ((low >> 16) + bx_out) & 0xFFFF", "partial = bx_out & 0xFFFF", MODEL),
    ("0279: the carry taken from bit 15", LONGS, "(low >> 16)", "(low >> 15)", MODEL),
    ("0279: the mul bx term uses CX", LONGS, "bx_out = (si * bx) & 0xFFFF", "bx_out = (si * cx) & 0xFFFF", MODEL),
    ("0279: the mul bx term uses DI", LONGS, "bx_out = (si * bx) & 0xFFFF", "bx_out = (di * bx) & 0xFFFF", MODEL),
    ("0279: the mul bx term not masked", LONGS, "bx_out = (si * bx) & 0xFFFF", "bx_out = si * bx", MODEL),
    ("0279: the mul bx term dropped from DX", LONGS, "partial = ((low >> 16) + bx_out) & 0xFFFF", "partial = (low >> 16) & 0xFFFF", MODEL),
    ("0279: the mul cx term uses BX", LONGS, "cx_out = (di * cx) & 0xFFFF", "cx_out = (di * bx) & 0xFFFF", MODEL),
    ("0279: the mul cx term uses SI", LONGS, "cx_out = (di * cx) & 0xFFFF", "cx_out = (si * cx) & 0xFFFF", MODEL),
    ("0279: the mul cx term not masked", LONGS, "cx_out = (di * cx) & 0xFFFF", "cx_out = di * cx", MODEL),
    ("0279: the mul cx term dropped from DX", LONGS, "dx_out = (partial + cx_out) & 0xFFFF", "dx_out = partial & 0xFFFF", MODEL),
    ("0279: DX not masked after the last add", LONGS, "dx_out = (partial + cx_out) & 0xFFFF", "dx_out = partial + cx_out", MODEL),
    ("0279: partial not masked (first add's carry kept)", LONGS, "partial = ((low >> 16) + bx_out) & 0xFFFF", "partial = (low >> 16) + bx_out", MODEL),
    ("0279: AX not masked", LONGS, "return Mul(low & 0xFFFF,", "return Mul(low,", MODEL),
    ("0279: flags of the first add", LONGS, "add16_flags(partial, cx_out))", "add16_flags(low >> 16, bx_out))", MODEL),
    ("0279: flags of the result", LONGS, "add16_flags(partial, cx_out))", "add16_flags(dx_out, 0))", MODEL),
    ("0279: BX and CX swapped in the result", LONGS, "return Mul(low & 0xFFFF, dx_out, bx_out, cx_out,", "return Mul(low & 0xFFFF, dx_out, cx_out, bx_out,", MODEL),
    ("0279: SI and DI swapped in the result", LONGS, "cx_out, si, di,", "cx_out, di, si,", MODEL),
    # --- the 0D56 adapter (check.py long_max_reader)
    ("max adapter: b taken from arg(1), arg(0) (low/high swapped)", CHECK, "b, a = (g.arg(0), g.arg(1)), (g.arg(2), g.arg(3))", "b, a = (g.arg(1), g.arg(0)), (g.arg(2), g.arg(3))", ADAPTER),
    ("max adapter: a low/high swapped", CHECK, "b, a = (g.arg(0), g.arg(1)), (g.arg(2), g.arg(3))", "b, a = (g.arg(0), g.arg(1)), (g.arg(3), g.arg(2))", ADAPTER),
    ("max adapter: a and b swapped", CHECK, "b, a = (g.arg(0), g.arg(1)), (g.arg(2), g.arg(3))", "a, b = (g.arg(0), g.arg(1)), (g.arg(2), g.arg(3))", ADAPTER),
    ("max adapter: model called with b, a", CHECK, "honest = longs.max_0d56(*a, *b)", "honest = longs.max_0d56(*b, *a)", ADAPTER),
    ("max adapter: ES = AX", CHECK, "g.set_reg(\"es\", honest.dx)", "g.set_reg(\"es\", honest.ax)", ADAPTER),
    ("max adapter: ES not set", CHECK, "        g.set_reg(\"es\", honest.dx)\n        merge_flags(g, honest.flags)", "        merge_flags(g, honest.flags)", ADAPTER),
    ("max adapter: flags not merged", CHECK, "        g.set_reg(\"es\", honest.dx)\n        merge_flags(g, honest.flags)", "        g.set_reg(\"es\", honest.dx)", ADAPTER),
    ("max adapter: AX and DX swapped", CHECK, "        g.set_reg(\"ax\", ax)\n        g.set_reg(\"dx\", dx)\n        g.set_reg(\"es\"", "        g.set_reg(\"ax\", dx)\n        g.set_reg(\"dx\", ax)\n        g.set_reg(\"es\"", ADAPTER),
    ("merge_flags: other bits cleared", CHECK, "(g.reg(\"flags\") & ~longs.ARITH) | arith", "arith", ADAPTER),
    ("merge_flags: arithmetic bits not cleared", CHECK, "(g.reg(\"flags\") & ~longs.ARITH) | arith", "g.reg(\"flags\") | arith", ADAPTER),
    ("merge_flags: whole word replaced by the guest's", CHECK, "(g.reg(\"flags\") & ~longs.ARITH) | arith", "g.reg(\"flags\") & ~longs.ARITH", ADAPTER),
    ("min: returns the winner", CHECK, "return b if (honest.ax, honest.dx) == a else a", "return a if (honest.ax, honest.dx) == a else b", ADAPTER),
    ("min: returns b always", CHECK, "return b if (honest.ax, honest.dx) == a else a", "return b", ADAPTER),
    ("min: not applied", CHECK, "    if variant == \"min\":\n        return b if", "    if False:\n        return b if", ADAPTER),
    ("tie-a: applied to every call", CHECK, "if variant == \"tie-a\" and a == b:", "if variant == \"tie-a\":", ADAPTER),
    ("tie-a: applied to a's high word equal", CHECK, "if variant == \"tie-a\" and a == b:", "if variant == \"tie-a\" and a[1] == b[1]:", ADAPTER),
    ("lowword-signed: unsigned compare", CHECK, "return a if longs.s16(a[0]) > longs.s16(b[0]) else b", "return a if a[0] > b[0] else b", ADAPTER),
    ("lowword-signed: reversed compare", CHECK, "return a if longs.s16(a[0]) > longs.s16(b[0]) else b", "return a if longs.s16(a[0]) < longs.s16(b[0]) else b", ADAPTER),
    ("lowword-signed: applied when the high words differ", CHECK, "if variant == \"lowword-signed\" and a[1] == b[1]:", "if variant == \"lowword-signed\":", ADAPTER),
    ("lowword-signed: tally uses min", CHECK, "max_variant(honest, a, b, \"lowword-signed\") != (honest.ax, honest.dx))", "max_variant(honest, a, b, \"min\") != (honest.ax, honest.dx))", ADAPTER),
    ("lowword-signed: tally not counted", CHECK, "            bump(\"lowword-signed changes the result\", max_variant(honest, a, b, \"lowword-signed\") != (honest.ax, honest.dx))\n", "", ADAPTER),
    ("falsifier min not passed to the registers", CHECK, "ax, dx = max_variant(honest, a, b, falsifier)", "ax, dx = max_variant(honest, a, b, None)", ADAPTER),
    ("max tally: calls not counted", CHECK, "            bump(\"calls\")\n            bump(\"high words", "            bump(\"high words", ADAPTER),
    ("max tally: high words differ -> a > b", CHECK, "a[1] != b[1])", "a[1] > b[1])", ADAPTER),
    ("max tally: high words differ -> low words", CHECK, "a[1] != b[1])", "a[0] != b[0])", ADAPTER),
    ("max tally: a wins counts ties", CHECK, "== a and a != b)", "== a)", ADAPTER),
    ("max tally: b wins counts ties", CHECK, "== b and a != b)", "== b)", ADAPTER),
    ("max tally: b wins compares to a", CHECK, "bump(\"b wins\", (honest.ax, honest.dx) == b and a != b)", "bump(\"b wins\", (honest.ax, honest.dx) == a and a != b)", ADAPTER),
    ("max tally: ties compare the high words", CHECK, "bump(\"ties (a == b)\", a == b)", "bump(\"ties (a == b)\", a[1] == b[1])", ADAPTER),
    ("max tally: min changes -> equal", CHECK, "max_variant(honest, a, b, \"min\") != (honest.ax, honest.dx))", "max_variant(honest, a, b, \"min\") == (honest.ax, honest.dx))", ADAPTER),
    ("max tally: min changes -> always", CHECK, "bump(\"min changes the result\", max_variant(honest, a, b, \"min\") != (honest.ax, honest.dx))", "bump(\"min changes the result\")", ADAPTER),
    ("max tally: tie-a changes -> uses min", CHECK, "max_variant(honest, a, b, \"tie-a\") != (honest.ax, honest.dx))", "max_variant(honest, a, b, \"min\") != (honest.ax, honest.dx))", ADAPTER),
    ("max tally: tie-a changes -> always", CHECK, "bump(\"tie-a changes the result\", max_variant(honest, a, b, \"tie-a\") != (honest.ax, honest.dx))", "bump(\"tie-a changes the result\")", ADAPTER),
    # --- the 0279 adapter (check.py long_mul_reader)
    ("mul adapter: BX and CX operands swapped", CHECK, "ax, dx, bx, cx = g.reg(\"ax\"), g.reg(\"dx\"), g.reg(\"bx\"), g.reg(\"cx\")", "ax, dx, cx, bx = g.reg(\"ax\"), g.reg(\"dx\"), g.reg(\"bx\"), g.reg(\"cx\")", ADAPTER),
    ("mul adapter: AX and DX operands swapped", CHECK, "ax, dx, bx, cx = g.reg(\"ax\"), g.reg(\"dx\"), g.reg(\"bx\"), g.reg(\"cx\")", "dx, ax, bx, cx = g.reg(\"ax\"), g.reg(\"dx\"), g.reg(\"bx\"), g.reg(\"cx\")", ADAPTER),
    ("mul adapter: AX not set", CHECK, "        g.set_reg(\"ax\", out_ax)\n", "", ADAPTER),
    ("mul adapter: DX not set", CHECK, "        g.set_reg(\"dx\", out_dx)\n", "", ADAPTER),
    ("mul adapter: BX not set", CHECK, "        g.set_reg(\"bx\", r.bx)\n", "", ADAPTER),
    ("mul adapter: CX not set", CHECK, "        g.set_reg(\"cx\", r.cx)\n", "", ADAPTER),
    ("mul adapter: DI not set", CHECK, "        g.set_reg(\"di\", r.di)\n", "", ADAPTER),
    ("mul adapter: SI = DI", CHECK, "g.set_reg(\"si\", r.si)", "g.set_reg(\"si\", r.di)", ADAPTER),
    ("mul adapter: scratch falsifier always", CHECK, "        if falsifier != \"scratch\":\n            g.set_reg(\"si\", r.si)", "        if True:\n            pass", ADAPTER),
    ("mul adapter: scratch falsifier never", CHECK, "        if falsifier != \"scratch\":\n            g.set_reg(\"si\", r.si)", "        if True:\n            g.set_reg(\"si\", r.si)", ADAPTER),
    ("mul adapter: flags not merged", CHECK, "        g.set_reg(\"di\", r.di)\n        merge_flags(g, r.flags)", "        g.set_reg(\"di\", r.di)", ADAPTER),
    ("product+1: no carry into DX", CHECK, "(r.dx + (r.ax == 0xFFFF)) & 0xFFFF", "r.dx", ADAPTER),
    ("product+1: carry always", CHECK, "(r.dx + (r.ax == 0xFFFF)) & 0xFFFF", "(r.dx + 1) & 0xFFFF", ADAPTER),
    ("product+1: adds 2", CHECK, "out_ax, out_dx = (r.ax + 1) & 0xFFFF,", "out_ax, out_dx = (r.ax + 2) & 0xFFFF,", ADAPTER),
    ("product+1: not applied", CHECK, "if falsifier == \"product+1\":", "if False:", ADAPTER),
    ("no-cross-term: drops the other term", CHECK, "out_dx = (r.dx - r.bx) & 0xFFFF", "out_dx = (r.dx - r.cx) & 0xFFFF", ADAPTER),
    ("no-cross-term: not applied", CHECK, "elif falsifier == \"no-cross-term\":", "elif False:", ADAPTER),
    ("no-cross-term: DX unmasked", CHECK, "out_dx = (r.dx - r.bx) & 0xFFFF", "out_dx = r.dx - r.bx", ADAPTER),
    ("mul tally: calls not counted", CHECK, "            bump(\"calls\")\n            bump(\"DX operand", "            bump(\"DX operand", ADAPTER),
    ("mul tally: DX operand condition dropped", CHECK, "bump(\"DX operand (a high word) non-zero\", dx)", "bump(\"DX operand (a high word) non-zero\")", ADAPTER),
    ("mul tally: DX operand -> AX", CHECK, "bump(\"DX operand (a high word) non-zero\", dx)", "bump(\"DX operand (a high word) non-zero\", ax)", ADAPTER),
    ("mul tally: BX operand -> CX", CHECK, "bump(\"BX operand (b high word) non-zero\", bx)", "bump(\"BX operand (b high word) non-zero\", cx)", ADAPTER),
    ("mul tally: mul bx term -> mul cx term", CHECK, "= no-cross-term changes DX\", r.bx)", "= no-cross-term changes DX\", r.cx)", ADAPTER),
    ("mul tally: mul bx term -> operand BX", CHECK, "= no-cross-term changes DX\", r.bx)", "= no-cross-term changes DX\", bx)", ADAPTER),
    ("mul tally: mul cx term -> mul bx term", CHECK, "non-zero\", r.cx)", "non-zero\", r.bx)", ADAPTER),
    ("mul tally: carry -> AX * BX", CHECK, "(ax * cx) >> 16)", "(ax * bx) >> 16)", ADAPTER),
    ("mul tally: carry -> low word", CHECK, "(ax * cx) >> 16)", "(ax * cx) & 0xFFFF)", ADAPTER),
    ("mul tally: product+1 not counted", CHECK, "            bump(\"product+1 changes the result\")\n", "", ADAPTER),
    ("mul tally: SI differs -> equal", CHECK, "g.reg(\"si\") != ax)", "g.reg(\"si\") == ax)", ADAPTER),
    ("mul tally: SI differs -> always", CHECK, "bump(\"SI differs at entry = the scratch falsifier shows\", g.reg(\"si\") != ax)", "bump(\"SI differs at entry = the scratch falsifier shows\")", ADAPTER),
    ("mul tally: SI compared with DX", CHECK, "g.reg(\"si\") != ax)", "g.reg(\"si\") != dx)", ADAPTER),
]

# Mutations no test can kill: the behaviour is identical.
EQUIVALENT = [
    ("0D56: the high compare `>` -> `>=`", "a_wins = s16(a_hi) > s16(b_hi) is only evaluated when a_hi != b_hi, so >= and > agree"),
    ("0D56: the low compare `>` -> `>=` (jbe -> jb)", "evaluated with equal high words; equal low words then mean a == b as longs, and returning a or b gives "
     "the same AX, DX, ES, and the flags come from the same compare: the only call it changes is a tie, which has one result"),
    ("sub flags: the result not masked to 16 bits (`r = x - y`)", "Python integers are two's complement of unbounded width: "
     "`result & 0xFF`, `result & 0x8000`, `result == 0` and the xor terms give the same bits for a negative r as for r & 0xFFFF"),
    ("0279: add16_flags(cx_out, partial) (operands swapped)", "an addition is commutative: carry, overflow, auxiliary carry, sign, zero and parity "
     "of x + y are the same for y + x"),
    ("tie-a: `return a` -> `return b`","the branch runs only when a == b"),
    ("0D56: tie-a (the task's falsifier m2-longs+0d56-tie-a)", "a tie is a == b: a and b are the same long, so the falsifier changes no register; "
     "check.py's tally 'tie-a changes the result' counts 0 (the m2-longs run prints it) and test_tie_a_is_not_stopped_it_changes_no_register pins it"),
]


def child(index):
    name, path, old, new, tests = MUTATIONS[index]
    root = str(ROOT)
    for sub in ("runtime/model", "runtime/driver", "runtime/emul", "experiments/E021-m0-whole-match", "tests"):
        sys.path.insert(0, f"{root}/{sub}")
    sys.path.insert(0, root)
    source = (ROOT / path).read_text()
    if source.count(old) < 1 or old == new:
        print(f"{name}: text not found or unchanged")
        sys.exit(ERROR)
    mutated = source.replace(old, new, 1)
    module_name = Path(path).stem
    if module_name == "check":
        import longs  # noqa: F401  (the real one, imported by check)
    module = types.ModuleType(module_name)
    module.__file__ = str(ROOT / path)
    sys.modules[module_name] = module
    exec(compile(mutated, str(ROOT / path), "exec"), module.__dict__)
    import unittest
    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
    result = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(suite)
    sys.exit(SURVIVED if result.wasSuccessful() else KILLED)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        child(int(sys.argv[2]))
    not_killed = 0
    for i, (name, path, old, new, tests) in enumerate(MUTATIONS):
        r = subprocess.run([sys.executable, "-B", __file__, "--child", str(i)], capture_output=True, text=True)
        label = {KILLED: "KILLED  ", SURVIVED: "SURVIVED"}.get(r.returncode, "ERROR   ")
        detail = "" if r.returncode in (KILLED, SURVIVED) else ": " + ((r.stdout + r.stderr).strip().splitlines() or ["?"])[-1]
        print(label, name + detail, flush=True)
        not_killed += r.returncode != KILLED
    for name, why in EQUIVALENT:
        print("EQUIVALENT", name, "-", why)
    print(f"{len(MUTATIONS)} mutations, {not_killed} not killed")
    return 1 if not_killed else 0


if __name__ == "__main__":
    sys.exit(main())
