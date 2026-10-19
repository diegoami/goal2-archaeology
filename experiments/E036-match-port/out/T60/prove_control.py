#!/usr/bin/env python3
"""T60: the proof's control for these ports: a match played with the ports proved from a given main-RNG draw on (every
call of a ported routine side by side with the original's, port/prove.py); it must raise no ProofError.

    python3 -B experiments/E036-match-port/out/T60/prove_control.py MATCH_ID PORTS [FROM_DRAW]

(T59's out/T59/prove_control.py proves from draw 0; a proved match costs several times an unproved one, and these ports
are called a million times in a match, so a window from a later draw is allowed.) Exit 0: no proved call differs."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402
import locate  # noqa: E402


def main(mid, ports, from_draw="0"):
    from original_match import Image
    from original_match.assets import reference_image
    spec = {m.id: m for f in families.discover().values() for m in f.matches}[mid]
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    found = locate.prove(image, spec, ports.split(","), int(from_draw), 36000, print)
    print(f"{mid}, ports {ports}, proved from draw {from_draw}: " + ("no proved call differs" if found is None else f"{found}"))
    return 0 if found is None else 1


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
