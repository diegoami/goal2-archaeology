#!/usr/bin/env python3
"""T60: the cost of a port's body on the kit's machine (the routine called as a Python function with the stack of its
entry, no emulator run, no hook dispatch): microseconds per call for the hot routines.

    python3 -B experiments/E036-match-port/out/T60/bench_ports.py [N]"""
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "runtime"))
sys.path.insert(0, str(HERE))
import fuzz  # noqa: E402
import generators  # noqa: E402
import generators_geometry  # noqa: E402
from original_match import port  # noqa: E402
from original_match.port.guest import PortFrame  # noqa: E402

HOT = [("runtime", "214B:0C57"), ("geometry", "0791:2996"), ("geometry", "0791:26D7"), ("geometry", "0791:2B51"),
       ("geometry", "0791:2CEC"), ("geometry", "0791:2C29"), ("geometry", "0791:2BB1"), ("geometry", "0791:2D10"),
       ("geometry", "0791:2C86"), ("geometry", "0791:278A"), ("runtime", "214B:06D0"), ("runtime", "214B:2031"),
       ("runtime", "23E4:0279"), ("runtime", "23E4:0294"), ("runtime", "23E4:0644"), ("runtime", "214B:0D56")]


def main(n=3000):
    img, memory = fuzz.setup(".cache/dl")
    for module, address in HOT:
        m, inst = fuzz.make_machine(img, memory, module)
        entry = port._module_registry(module).entries[address]
        rnd = random.Random(1)
        tr = fuzz.Trial(rnd)
        generators.GENERATORS[address](tr, img)
        for lin, d in tr.writes:
            m.write(lin, d)
        mem = inst.mem
        # the machine at the routine's entry, as fuzz.run_one sets it, then the body as a function
        cs = m.seg(int(address.split(":")[0], 16))
        layout = [0x0010] + ([cs] if entry.far else []) + [a & 0xFFFF for a in tr.args]
        sp = fuzz.SP0 - 2 * len(layout) - 8
        for i, w in enumerate(layout):
            m.write(fuzz.SS * 16 + sp + 2 * i, (w & 0xFFFF).to_bytes(2, "little"))
        for name, value in (("ss", fuzz.SS), ("ds", m.DS), ("sp", sp), ("bp", 0x1111), ("cs", cs)):
            m.set_reg(name, value)
        for name in ("ax", "bx", "cx", "dx", "si", "di"):
            m.set_reg(name, tr.regs.get(name, 0))
        t0 = time.perf_counter()
        for _ in range(n):
            m.set_reg("sp", sp)
            m.set_reg("bp", 0x1111)
            mem._entries.append((sp, entry.far))
            try:
                out = entry.fn(mem, None)
                if out is not None and hasattr(out, "send"):
                    try:
                        out.send(None)
                    except StopIteration:
                        pass
            finally:
                mem._entries.pop()
        dt = (time.perf_counter() - t0) / n * 1e6
        print(f"{address} {dt:6.1f} us per call")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3000)
