#!/usr/bin/env python3
"""T59: on a real match, Match.save() at each decision: with a port's frame live (the substitution notice at a throw-in,
6E11 waiting on its call of 8062) it must refuse with MatchError; with none live it must save, and the match loaded from
that save must end as the straight one (score, ticks, draws digest). The straight match is the ported one, its record
compared with the reference elsewhere (compare-ports-*.txt).

    python3 -B experiments/E036-match-port/out/T59/save_under_port.py S/decisions-70"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
E036 = HERE.parents[1]
sys.path.insert(0, str(E036.parents[1] / "runtime"))
sys.path.insert(0, str(E036))
import families  # noqa: E402
import family  # noqa: E402


def drive(m, spec, saves):
    """Play to the end with the spec's policy, trying save() at each decision; returns (score, ticks, draws digest)."""
    from original_match.match import MatchError
    paused = set()
    if m.waiting is not None:          # a match loaded from a save made at a decision, before its answer
        if m.waiting["context"] in spec.policy.contexts:
            spec.policy.answer(m, m.waiting)
        else:
            m.answer()
    for ev in m.events():
        if ev.kind == "minute" and ev.minute in spec.policy.pause_at and ev.minute not in paused:
            paused.add(ev.minute)
            m.pause()
        if ev.kind == "decision":
            frames = m.port_frames()
            try:
                blob = m.save()
                saves.append(("saved", ev.minute, ev.data["context"], frames, blob))
            except MatchError as e:
                saves.append(("refused", ev.minute, ev.data["context"], frames, str(e).splitlines()[0]))
            if ev.data["context"] in spec.policy.contexts:
                spec.policy.answer(m, ev.data)
            else:
                m.answer()
    r = m.result()
    return r["score"], r["ticks"], r["draws_digest"]


def main(mid):
    from original_match import Image, Match, Fixture
    from original_match.assets import reference_image
    spec = {m.id: m for f in families.discover().values() for m in f.matches}[mid]
    image = Image.from_bytes(reference_image(family.DEFAULT_CACHE))
    first, second, index, kind = spec.fixture
    players = countries = None
    if spec.edits:
        players, countries = families.apply_edits(image.players(), image.countries(), spec.edits)
    m = Match(image, Fixture(first, second, index=index, kind=kind), managed=spec.managed, seed=spec.seed,
              record_draws=True, delay_byte=spec.delay_byte, substitutions=spec.substitutions, players=players,
              countries=countries, ports=["pilot", "restarts"])
    saves = []
    straight = drive(m, spec, saves)
    print(f"{mid} straight (ports pilot, restarts): score {straight[0]} ticks {straight[1]} draws {straight[2][:12]}...")
    ok = True
    for what, minute, context, frames, extra in saves:
        if what == "refused":
            good = bool(frames)
            print(f"minute {minute} {context}: save refused with MatchError ({extra}); frames live: {frames} "
                  f"{'as expected' if good else 'UNEXPECTED: no frame live'}")
        else:
            good = not frames
            if good:      # resume from the save: the rest of the match must be the straight one's
                rest = drive(Match.load(extra), spec, [])
                good = rest == straight
                print(f"minute {minute} {context}: saved with no frame live; resumed: score {rest[0]} ticks {rest[1]} "
                      f"{'equal to the straight match' if good else 'DIFFERS from the straight match'}")
            else:
                print(f"minute {minute} {context}: SAVED although frames were live: {frames}")
        ok = ok and good
    print("all as expected" if ok else "NOT as expected")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
