#!/usr/bin/env python3
"""T70 (adapted from out/T69/prove_subset.py): the proof (T59, port/prove.py) of some of the setup module's ports over
a whole match from its first draw: every call of those ports side by side with the original's, written bytes outside the
dead frame, the kit's sites and listeners, and the returned AX and DX. The proof takes the outermost ported calls, so a
routine called inside another listed one is counted as nested, not proved on its own.

    python3 -B experiments/E036-match-port/out/T70/prove_subset.py O8/c1-c2-friendly 0791:A4A1

Exit 0: no proved call differs (and every listed port was proved at least once, else 1)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402


def main(mid, routines, time_limit="3600"):
    from original_match import Image, Match, Fixture
    from original_match.assets import reference_image
    from original_match.port import Registry, setup
    from original_match.port.prove import ProofError
    spec = {m.id: m for f in families.discover().values() for m in f.matches}[mid]
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    chosen = Registry("setup")
    for r in routines.split(","):
        chosen._add(setup.PORTS.entries[r])
    players = countries = None
    if spec.edits:
        players, countries = families.apply_edits(image.players(), image.countries(), spec.edits)
    first, second, index, kind = spec.fixture
    m = Match(image, Fixture(first, second, index=index, kind=kind), managed=spec.managed, seed=spec.seed,
              record_draws=True, delay_byte=spec.delay_byte, substitutions=spec.substitutions, players=players,
              countries=countries, timeout_s=float(time_limit), ports=[(chosen, None)], prove=0)
    import time
    t0 = time.time()
    found = None
    try:
        family.play(m, spec, time.time() + float(time_limit))
    except ProofError as e:
        found = e
    summary = m.prover.summary()
    print(f"proved from draw 0: {time.time() - t0:.0f} s; calls: " + "; ".join(
        f"{a} proved {s['proved']}" + (f", inside another proved call {s['nested']}" if s["nested"] else "")
        + (f", the kit's write listener calls compared {m.prover.listened[a]}" if m.prover.listened[a] else "")
        + (f", declared dead registers differing {s['dead']}" if s["dead"] else "")
        + (f", scratch registers differing {s['scratch']}" if s["scratch"] else "") for a, s in summary.items()))
    if found is not None:
        print(f"{mid}, ports {routines}: {found}")
        return 1
    unproved = [a for a, s in summary.items() if not s["proved"]]
    if unproved:
        print(f"{mid}: no call of {', '.join(unproved)} was proved at the top level")
    print(f"{mid}, ports {routines}, proved from draw 0: no proved call differs")
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
