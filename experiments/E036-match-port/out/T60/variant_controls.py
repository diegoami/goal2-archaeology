#!/usr/bin/env python3
"""T60: the fuzz's control. Each variant (falsifier) of a port is run against the original on the routine it changes: the
fuzz must find a difference (fuzz.py exits 1 and says where), or the fuzz could not see a wrong port.

    python3 -B experiments/E036-match-port/out/T60/variant_controls.py [--n 300]
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTROLS = [("geometry", "0791:278A", "skill-no-halving"), ("geometry", "0791:278A", "keeper-gate-off"),
            ("geometry", "0791:2D10", "ahead-inclusive"), ("geometry", "0791:2C54", "own-half-zero"),
            ("geometry", "0791:2B7B", "energy-gate-32"), ("geometry", "0791:2E82", "penalty-strip-4"),
            ("geometry", "0791:2BB1", "slot-side-12"),
            ("runtime", "214B:1C86", "wrap-high-inclusive"), ("runtime", "214B:2000", "clamp-high-uses-lo"),
            ("runtime", "214B:0D56", "max-unsigned-high"), ("runtime", "214B:0D1C", "min-unsigned-high"),
            ("runtime", "214B:0C57", "bit-shift-1")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", default="300")
    a = ap.parse_args()
    bad = 0
    for module, routine, variant in CONTROLS:
        p = subprocess.run([sys.executable, "-u", "-B", str(HERE / "fuzz.py"), "--module", module, "--routine", routine,
                            "--variant", variant, "--n", a.n, "--timeout", "2"], capture_output=True, text=True)
        last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-200:]
        found = p.returncode == 1
        print(f"{module}.{variant} on {routine}: {'differs from the original (as a falsifier must)' if found else 'NO DIFFERENCE FOUND'}"
              f" | {last[:150]}")
        bad += 0 if found else 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
