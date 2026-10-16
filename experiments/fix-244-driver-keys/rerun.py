#!/usr/bin/env python3
"""Re-run one earlier experiment's own script once on the fixed driver, writing its run records under
experiments/fix-244-driver-keys/out/rerun/<E>/ instead of runs/<E>/ (the originals are never touched,
and the numbering restarts: these are r0001... of this folder).

    python3 experiments/fix-244-driver-keys/rerun.py E003 d0 --runs 1 --dos-time 10:00:00 --dos-date 10/04/1993 --batch fix244
    python3 experiments/fix-244-driver-keys/rerun.py E006 games --times 10:00 --batch fix244

The experiment script is loaded unchanged and only its output folder (OUT, and E006's copy of E003's)
is replaced; its own clean-tree rule applies (commit before running)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = {"E003": "E003-q001-inputs", "E006": "E006-q004-skills"}


def load(exp):
    path = ROOT / "experiments" / SCRIPTS[exp] / "run.py"
    spec = importlib.util.spec_from_file_location(f"rerun_{exp}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    exp, argv = sys.argv[1], sys.argv[2:]
    mod = load(exp)
    out = HERE / "out" / "rerun" / exp
    mod.OUT = out
    if hasattr(mod, "e003"):  # E006 loads E003's script for its keys and helpers
        mod.e003.OUT = out
    return mod.main(argv)


if __name__ == "__main__":
    sys.exit(main())
