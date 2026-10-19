#!/usr/bin/env python3
"""T60: where the memory of a ported match differs from the unhooked one at the end (the digests say only the 1 KiB block).

    python3 -B experiments/E036-match-port/out/T60/memdiff.py MATCH_ID PORTS [--variant M.NAME]

Runs the match twice (family.run_match, the kit's own routine) and prints the differing bytes as DS offsets (and as offsets
from SS:0 and from the final SP), the first 40 and the span."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402


def run(image, spec, ports):
    holder = {}
    rec = family.run_match(image, spec, ports=ports, watch=lambda m: holder.setdefault("m", m))
    m = holder["m"].m
    return rec, m.read(0, 0x110000), {r: m.reg(r) for r in ("ss", "sp", "bp", "ds")}, m


def main():
    mid, ports = sys.argv[1], [p for p in sys.argv[2].split(",") if p and p != "none"]
    if "--variant" in sys.argv:
        ports = [p for p in ports if p != sys.argv[sys.argv.index("--variant") + 1].split(".")[0]] + [sys.argv[sys.argv.index("--variant") + 1]]
    from original_match import Image
    from original_match.assets import reference_image
    spec = {m.id: m for f in families.discover().values() for m in f.matches}[mid]
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    ra, ma, regs_a, mach = run(image, spec, [])
    rb, mb, regs_b, _ = run(image, spec, ports)
    ds = mach.DS * 16
    print("final registers (unhooked / ported):", {k: (hex(regs_a[k]), hex(regs_b[k])) for k in regs_a})
    diffs = [i for i in range(len(ma)) if ma[i] != mb[i]]
    print(f"{len(diffs)} bytes differ")
    ssb = regs_a["ss"] * 16
    for i in diffs[:60]:
        print(f"linear 0x{i:05X} DS+0x{i - ds:X} SS+0x{i - ssb:X} (SP-relative {i - ssb - regs_a['sp']:+d}): "
              f"unhooked {ma[i]:02X}, ported {mb[i]:02X}")
    if diffs:
        print(f"span DS+0x{diffs[0] - ds:X} .. DS+0x{diffs[-1] - ds:X}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
