"""T72: unreached B6CC against actual original on deterministic signed/clamp/wrap cases.

Both machines start from the same released image, synthetic manager byte and random
stack residue. Compare all memory including the dead frame and returned AX/DX.
Only counts/differences are emitted, never original bytes.
"""
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "experiments/E036-match-port/out/T60"))
import fuzz

img, memory = fuzz.setup(ROOT / ".cache/dl")
original, _ = fuzz.make_machine(img, memory, None)
ported, inst = fuzz.make_machine(img, memory, "update")
rng = random.Random(7200)
cases = [(b, d) for b in (0, 1, 127, 128, 129, 255) for d in (-32768, -200, -1, 0, 1, 200, 32767)]
cases += [(rng.randrange(256), rng.randrange(65536)) for _ in range(58)]
failed = 0
for trial, (before, delta) in enumerate(cases):
    output = []
    garbage = bytes(rng.randrange(256) for _ in range(0x2000))
    for m in (original, ported):
        m.write(0, memory)
        m.write(0x90000, bytes(0x10000))
        m.write(0xA0000 + fuzz.SP0 - 0x2000, garbage)
        m.write(m.DS * 16 + 0xA91F, (0x200).to_bytes(2, 'little') + (0x9000).to_bytes(2, 'little'))
        m.write(0x90200 + 3 * 130 + 2, bytes([before]))
        sp, reason = fuzz.run_one(m, True, "0791:B6CC", [delta, 130], {"ax": 0xBEEF, "dx": 0x1234}, 10)
        output.append((fuzz.final(m), bytes(m._uc.mem_read(0, fuzz.MEM_SIZE)), sp))
    (a, ma, sp), (b, mb, _) = output
    differences, scratch = fuzz.compare(a, b, ma, mb, sp, False)
    if differences:
        failed += 1
        print(trial, before, delta, differences)
print(f"B6CC: {len(cases)} cases, {failed} differing (all memory, dead stack frame included, AX/DX)")
sys.exit(bool(failed))
