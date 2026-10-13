#!/usr/bin/env python3
"""T47: mutation check of the new tests, in memory (no tracked file is edited).

    python3 -B tests/mutations_t47.py

Each mutation replaces a text in the source of runtime/model/draws.py or experiments/E021-m0-whole-match/check.py,
compiles the mutated module in a CHILD process, puts it in sys.modules, and runs the test classes named for it;
the mutation is killed when a test fails. Prints one line per mutation and exits non-zero when one survives.
`EQUIVALENT` mutations are shown with the reason they cannot change behaviour (so no test can kill them)."""
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAWS = "runtime/model/draws.py"
CHECK = "experiments/E021-m0-whole-match/check.py"
ADAPTER = ["tests.test_emul_match.WrapperReaderTests"]
MODEL = ["tests.test_model_draws"]

# (name, file, old text, new text, tests that must fail)
MUTATIONS = [
    # --- the models, both wrappers separately (draws.py)
    ("06B1 n+1 in the draw", DRAWS, "recreate.draw(seed, n & 0xFFFF)                # 06BD-06C1", "recreate.draw(seed, (n + 1) & 0xFFFF)                # 06BD-06C1", MODEL),
    ("06D0 n+1 in the draw", DRAWS, "recreate.draw(seed, n & 0xFFFF)                # 06DC-06E0", "recreate.draw(seed, (n + 1) & 0xFFFF)                # 06DC-06E0", MODEL),
    ("06B1 n not masked to 16 bits", DRAWS, "recreate.draw(seed, n & 0xFFFF)                # 06BD-06C1", "recreate.draw(seed, n)                # 06BD-06C1", MODEL),
    ("06D0 n not masked to 16 bits", DRAWS, "recreate.draw(seed, n & 0xFFFF)                # 06DC-06E0", "recreate.draw(seed, n)                # 06DC-06E0", MODEL),
    ("06D0 compare to 2", DRAWS, "SUCCESS_DRAW = 1 ", "SUCCESS_DRAW = 2 ", MODEL),
    ("06D0 result inverted", DRAWS, "result = 1 if draw == SUCCESS_DRAW else 0", "result = 0 if draw == SUCCESS_DRAW else 1", MODEL),
    ("06D0 AH dropped", DRAWS, "(draw & 0xFF00) | result", "result", MODEL),
    ("06D0 AL = whole draw", DRAWS, "(draw & 0xFF00) | result", "draw | result", MODEL),
    ("06D0 AX high byte = draw low byte", DRAWS, "(draw & 0xFF00) | result", "((draw & 0xFF) << 8) | result", MODEL),
    ("06D0 seed not stepped", DRAWS, "return Wrapper(draw, new_seed, (draw", "return Wrapper(draw, seed, (draw", MODEL),
    ("06D0 DX = 0", DRAWS, "(draw & 0xFF00) | result, draw & 0xFFFF)", "(draw & 0xFF00) | result, 0)", MODEL),
    ("06D0 DX = draw + 1", DRAWS, "(draw & 0xFF00) | result, draw & 0xFFFF)", "(draw & 0xFF00) | result, (draw + 1) & 0xFFFF)", MODEL),
    ("06B1 seed not stepped", DRAWS, "return Wrapper(draw, new_seed, draw & 0xFFFF, draw & 0xFFFF)", "return Wrapper(draw, seed, draw & 0xFFFF, draw & 0xFFFF)", MODEL),
    ("06B1 DX = 0", DRAWS, "return Wrapper(draw, new_seed, draw & 0xFFFF, draw & 0xFFFF)", "return Wrapper(draw, new_seed, draw & 0xFFFF, 0)", MODEL),
    ("06B1 AX low byte only", DRAWS, "return Wrapper(draw, new_seed, draw & 0xFFFF, draw & 0xFFFF)", "return Wrapper(draw, new_seed, draw & 0xFF, draw & 0xFFFF)", MODEL),
    ("06B1 AX = draw + 1", DRAWS, "return Wrapper(draw, new_seed, draw & 0xFFFF, draw & 0xFFFF)", "return Wrapper(draw, new_seed, (draw + 1) & 0xFFFF, draw & 0xFFFF)", MODEL),
    ("06B1 draw field reported as n", DRAWS, "return Wrapper(draw, new_seed, draw & 0xFFFF, draw & 0xFFFF)", "return Wrapper(n, new_seed, draw & 0xFFFF, draw & 0xFFFF)", MODEL),
    # --- the adapter (check.py wrapper_reader)
    ("adapter: n from arg(1)", CHECK, "        n = g.arg(0)\n        seed_lin = g.far(0xA978)", "        n = g.arg(1)\n        seed_lin = g.far(0xA978)", ADAPTER),
    ("adapter: seed read from DS:7B62", CHECK, "seed_lin = g.far(0xA978)\n        seed = g.word_at(seed_lin)\n        honest", "seed_lin = g.DS * 16 + 0x7B62\n        seed = g.word_at(seed_lin)\n        honest", ADAPTER),
    ("adapter: seed write dropped (both)", CHECK, "        if falsifier != \"seed-write\":\n            g.put", "        if False:\n            g.put", ADAPTER),
    ("adapter: 06D0 writes the UNCHANGED seed (review R1)", CHECK, "g.put(seed_lin, r.seed.to_bytes(2, \"little\"))", "g.put(seed_lin, (r.seed if which else seed).to_bytes(2, \"little\"))", ADAPTER),
    ("adapter: 06B1 writes the UNCHANGED seed", CHECK, "g.put(seed_lin, r.seed.to_bytes(2, \"little\"))", "g.put(seed_lin, (seed if which else r.seed).to_bytes(2, \"little\"))", ADAPTER),
    ("adapter: seed written big-endian", CHECK, "g.put(seed_lin, r.seed.to_bytes(2, \"little\"))", "g.put(seed_lin, r.seed.to_bytes(2, \"big\"))", ADAPTER),
    ("adapter: seed written one word further", CHECK, "g.put(seed_lin, r.seed.to_bytes(2, \"little\"))", "g.put(seed_lin + 2, r.seed.to_bytes(2, \"little\"))", ADAPTER),
    ("adapter: seed written twice", CHECK, "g.put(seed_lin, r.seed.to_bytes(2, \"little\"))", "g.put(seed_lin, r.seed.to_bytes(2, \"little\")); g.put(seed_lin, r.seed.to_bytes(2, \"little\"))", ADAPTER),
    ("adapter: DX = 0", CHECK, "        g.set_reg(\"dx\", r.dx)\n    return fn\n\n\nHOOKS", "        g.set_reg(\"dx\", 0)\n    return fn\n\n\nHOOKS", ADAPTER),
    ("adapter: DX = AL only", CHECK, "        g.set_reg(\"dx\", r.dx)\n    return fn\n\n\nHOOKS", "        g.set_reg(\"dx\", r.dx & 0xFF)\n    return fn\n\n\nHOOKS", ADAPTER),
    ("adapter: AX masked to a byte", CHECK, "        g.set_reg(\"ax\", ax)\n        g.set_reg(\"dx\", r.dx)", "        g.set_reg(\"ax\", ax & 0xFF)\n        g.set_reg(\"dx\", r.dx)", ADAPTER),
    ("adapter: AX not set", CHECK, "        g.set_reg(\"ax\", ax)\n        g.set_reg(\"dx\", r.dx)", "        g.set_reg(\"dx\", r.dx)", ADAPTER),
    ("adapter: wrong model for 06D0 (06B1's)", CHECK, "model = draws.draw_06b1 if which else draws.draw_06d0", "model = draws.draw_06b1", ADAPTER),
    ("adapter: wrong model for 06B1 (06D0's)", CHECK, "model = draws.draw_06b1 if which else draws.draw_06d0", "model = draws.draw_06d0", ADAPTER),
    # falsifier behaviour
    ("falsifier n+1 not applied", CHECK, "r = model(seed, n + 1) if falsifier == \"n+1\" else honest", "r = honest", ADAPTER),
    ("falsifier n+1 adds 2", CHECK, "r = model(seed, n + 1) if falsifier == \"n+1\" else honest", "r = model(seed, n + 2) if falsifier == \"n+1\" else honest", ADAPTER),
    ("falsifier value+1 not applied", CHECK, "if falsifier == \"value+1\":\n            ax = (ax + 1) & 0xFFFF", "if False:\n            ax = (ax + 1) & 0xFFFF", ADAPTER),
    ("falsifier value+1 adds 2", CHECK, "ax = (ax + 1) & 0xFFFF", "ax = (ax + 2) & 0xFFFF", ADAPTER),
    ("falsifier inverted not applied", CHECK, "elif falsifier == \"inverted\":\n            ax ^= 1", "elif False:\n            ax ^= 1", ADAPTER),
    ("falsifier inverted flips AH too", CHECK, "ax ^= 1", "ax ^= 0x101", ADAPTER),
    ("falsifier seed-write keeps the write", CHECK, "if falsifier != \"seed-write\":", "if True:", ADAPTER),
    # tally counters and their conditions
    ("tally: n+1 changes -> always False (review R2)", CHECK, "model(seed, n + 1).draw != honest.draw", "False", ADAPTER),
    ("tally: n+1 changes -> always True", CHECK, "model(seed, n + 1).draw != honest.draw", "True", ADAPTER),
    ("tally: n+1 compares the seed", CHECK, "model(seed, n + 1).draw != honest.draw", "model(seed, n + 1).seed != honest.seed", ADAPTER),
    ("tally: n+1 uses the falsified run", CHECK, "model(seed, n + 1).draw != honest.draw", "model(seed, n + 1).draw != r.draw", ADAPTER),
    ("tally: calls not counted", CHECK, "            bump(\"calls\")\n", "", ADAPTER),
    ("tally: calls counted twice", CHECK, "            bump(\"calls\")\n", "            bump(\"calls\")\n            bump(\"calls\")\n", ADAPTER),
    ("tally: value+1 not counted", CHECK, "                bump(\"value+1 changes AX\")\n", "", ADAPTER),
    ("tally: draw is 1 -> draw is 2", CHECK, "honest.draw == 1)", "honest.draw == 2)", ADAPTER),
    ("tally: draw is 1 -> always", CHECK, "bump(\"draw is 1\", honest.draw == 1)", "bump(\"draw is 1\")", ADAPTER),
    ("tally: draw is 1 from the falsified run", CHECK, "honest.draw == 1)", "r.draw == 1)", ADAPTER),
    ("tally: inverted not counted", CHECK, "                bump(\"inverted changes AL\")\n", "", ADAPTER),
    ("tally: seed-write condition ==", CHECK, "honest.seed != seed)", "honest.seed == seed)", ADAPTER),
    ("tally: seed-write not counted", CHECK, "            bump(\"seed-write changes the seed\", honest.seed != seed)\n", "", ADAPTER),
    ("tally: 06B1 keys counted for 06D0", CHECK, "            if which:\n                bump(\"n+1", "            if True:\n                bump(\"n+1", ADAPTER),
]

# the seed write of wrapper_reader is the only `g.put(seed_lin, r.seed...)` after this line (gate_reader has the same text earlier)
ANCHOR = 'if falsifier != "seed-write":\n            '
MUTATIONS = [(n, f, ANCHOR + o if o.startswith("g.put(seed_lin, r.seed") else o,
              ANCHOR + w if o.startswith("g.put(seed_lin, r.seed") else w, t) for n, f, o, w, t in MUTATIONS]

# Mutations no test can kill: the behaviour is identical.
EQUIVALENT = [
    ("tally: seed-write condition -> always True", "honest.seed != seed holds for every word: 0688's step w * 0x7ABD + 0x1B0F "
     "has no fixed point (w * 0x7ABC = -0x1B0F mod 65536 has no solution: 0x7ABC is even, 0x1B0F odd)"),
]


def child(index):
    name, path, old, new, tests = MUTATIONS[index]
    root = str(ROOT)
    for sub in ("runtime/model", "runtime/driver", "runtime/emul", "experiments/E021-m0-whole-match", "tests"):
        sys.path.insert(0, f"{root}/{sub}")
    sys.path.insert(0, root)
    source = (ROOT / path).read_text()
    assert source.count(old) >= 1, f"{name}: text not found"
    mutated = source.replace(old, new, 1)
    module_name = Path(path).stem
    if module_name == "check":
        import draws  # noqa: F401  (the real one, imported by check)
    module = types.ModuleType(module_name)
    module.__file__ = str(ROOT / path)
    sys.modules[module_name] = module
    exec(compile(mutated, str(ROOT / path), "exec"), module.__dict__)
    import unittest
    suite = unittest.defaultTestLoader.loadTestsFromNames(tests)
    result = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)      # 0: SURVIVED, 1: killed


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        child(int(sys.argv[2]))
    survived = 0
    for i, (name, path, old, new, tests) in enumerate(MUTATIONS):
        r = subprocess.run([sys.executable, "-B", __file__, "--child", str(i)], capture_output=True, text=True)
        killed = r.returncode == 1
        err = r.returncode not in (0, 1)
        print(("KILLED  " if killed else "ERROR   " if err else "SURVIVED"), name + (": " + r.stderr.strip().splitlines()[-1] if err else ""))
        survived += not killed
    for name, why in EQUIVALENT:
        print("EQUIVALENT", name, "-", why)
    print(f"{len(MUTATIONS)} mutations, {survived} not killed")
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
