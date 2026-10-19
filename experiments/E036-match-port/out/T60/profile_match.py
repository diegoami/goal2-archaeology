#!/usr/bin/env python3
"""T60: where a ported match spends its time (cProfile over family.run_match).

    python3 -B experiments/E036-match-port/out/T60/profile_match.py MATCH_ID PORTS [TOP]"""
import cProfile
import pstats
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402


def main(mid, ports, top="40"):
    from original_match import Image
    from original_match.assets import reference_image
    spec = {m.id: m for f in families.discover().values() for m in f.matches}[mid]
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    pr = cProfile.Profile()
    pr.enable()
    rec = family.run_match(image, spec, ports=[p for p in ports.split(",") if p != "none"], time_limit=3000)
    pr.disable()
    print(mid, "error:", rec["error"], "cpu", rec["cpu_s"], "calls", sum(rec.get("port_calls", {}).values()))
    st = pstats.Stats(pr)
    st.sort_stats("tottime").print_stats(int(top))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
