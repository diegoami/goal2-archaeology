#!/usr/bin/env python3
"""T60: what a ported call costs inside a running guest, framework included: a small guest program calls 214B:0C57 100
times (push 3, push 5, call far) and is run N/100 times, on the original and on the port; the difference per call is the
port's.

    python3 -B experiments/E036-match-port/out/T60/bench_loop.py [N]"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "runtime"))
sys.path.insert(0, str(HERE))
import fuzz  # noqa: E402


def main(n=20000):
    img, memory = fuzz.setup(".cache/dl")
    for module in (None, "runtime"):
        m, inst = fuzz.make_machine(img, memory, module)
        seg = 0x9E00
        target_seg = m.seg(0x214B)
        unit = bytes([0xB8, 3, 0, 0x50, 0xB8, 5, 0, 0x50, 0x9A, 0x57, 0x0C, target_seg & 0xFF, target_seg >> 8])
        code = unit * 100 + bytes([0x90])               # the routine clobbers CX: unrolled, and the program run again
        m.write(seg * 16, code)
        t0 = time.perf_counter()
        for _ in range(n // 100):
            for name, value in (("cs", seg), ("eip", 0), ("ss", fuzz.SS), ("sp", fuzz.SP0), ("ds", m.DS), ("bp", 0)):
                m.set_reg(name, value)
            m.run(seg * 16 + len(code) - 1, timeout_s=300, fresh=True)
        dt = time.perf_counter() - t0
        print(f"{'port' if module else 'original'}: {dt / n * 1e6:.1f} us per call ({n} calls)")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20000)
