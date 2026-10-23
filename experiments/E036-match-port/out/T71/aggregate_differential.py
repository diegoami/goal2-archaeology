"""T71: stage-six aggregate port against the original, including its dead frame.

ALL never enters 85F7. These deterministic synthetic pairs run the actual original's
routine and its port from the same released image and random stack bytes. No original
bytes are emitted; the comparison includes every memory byte and AX/DX.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments/E036-match-port/out/T60"))
import fuzz

img, memory = fuzz.setup(ROOT / ".cache/dl")
original, _ = fuzz.make_machine(img, memory, None)
ported, inst = fuzz.make_machine(img, memory, "postmatch")
rng = random.Random(710085)
pairs = [(4, 0, 1, 0), (0, 4, 1, 0), (1, 1, 2, 2), (2, 2, 1, 1), (1, 1, 1, 1)]
pairs += [tuple(rng.randrange(10) for _ in range(4)) for _ in range(45)]
failed = 0
for trial, goals in enumerate(pairs):
    output = []
    garbage = bytes(rng.randrange(256) for _ in range(0x2000))
    for m in (original, ported):
        m.write(0, memory)
        m.write(0x90000, bytes(0x10000))
        m.write(0xA0000 + fuzz.SP0 - 0x2000, garbage)
        def word(lin, value):
            m.write(lin, value.to_bytes(2, "little"))
        word(m.DS * 16 + 0xA923, 0x100)
        word(m.DS * 16 + 0xA925, 0x9000)
        word(m.DS * 16 + 0xA92B, 0x200)
        word(m.DS * 16 + 0xA92D, 0x9000)
        word(0x90100 + 0x26, 2)
        word(0x90100 + 0x2C, 1)
        m.write(0x90200, bytes([goals[0], goals[1], 6, 0, 1, 0, 2, 0,
                                  goals[2], goals[3], 6, 0, 2, 0, 1, 0]))
        sp, reason = fuzz.run_one(m, False, "1771:85F7", [], {"ax": 0xBEEF, "dx": 0x1234}, 10)
        output.append((fuzz.final(m), bytes(m._uc.mem_read(0, fuzz.MEM_SIZE)), sp))
    (a, ma, sp), (b, mb, _) = output
    differences, scratch = fuzz.compare(a, b, ma, mb, sp, False)
    if differences:
        failed += 1
        print(trial, goals, differences)
print(f"85F7: {len(pairs)} synthetic pairs, {failed} differing (all memory, dead stack frame included, AX/DX)")
sys.exit(bool(failed))
