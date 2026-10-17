#!/usr/bin/env python3
"""T59 (review round 1): the control of the proof: the ports as they are (no variant) proved over a whole match from
its first draw must raise no ProofError, every call of a ported routine proved (the decisions under 6E11 included).

    python3 -B experiments/E036-match-port/out/T59/prove_control.py S/decisions-70 pilot,restarts"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402
import locate  # noqa: E402


def main(mid, ports):
    from original_match import Image
    from original_match.assets import reference_image
    spec = {m.id: m for f in families.discover().values() for m in f.matches}[mid]
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    found = locate.prove(image, spec, ports.split(","), 0, 3600, print)
    print(f"{mid}, ports {ports}, proved from draw 0: " + ("no proved call differs" if found is None else f"{found}"))
    return 0 if found is None else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
