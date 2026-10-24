#!/usr/bin/env python3
"""E036 (T59): where a ported run first differs from the reference: the minute, then the call.

    python3 -B experiments/E036-match-port/locate.py --family ALL --candidate <file.jsonl> --match <id>
        [--reference <file.jsonl>] [--out <new file>] [--cache DIR] [--time-limit S]

1. The first differing minute: the reference's and the candidate's per-minute draw digests (records.py
   `draws.per_minute`), the first row that differs; every draw before that row is identical. A candidate that did not
   complete has no draws recorded: its row is the first.
2. A re-run of the match with the candidate's ports (and variant), every call of a ported routine proved side by side
   with the original's (runtime/original_match/port/prove.py, E021's rule moved into the kit) from the first draw of
   that row on: the first call whose written bytes (in order, outside the routine's dead frame) or returned registers
   differ is named: the routine and its module, the call's number, where it was called from, the minute and the
   draw, and the byte or the register. If no proved call differs from that row on, the whole match is proved from its
   first draw (a port's difference may change memory before it changes a draw).

The script reads the two logs and writes nothing but --out (a new file; never a reference, never a log). A call whose
original reaches a site of the kit (a key read, the tick, an event's routine) is not proved but counted (prove.py), so
the summary says how many calls were proved and which were not.

Exit status: 0 a call located; 1 nothing located (the candidate equals the reference, or no proved call differs);
2 a refused command or a malformed log."""
import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE))
import compare  # noqa: E402
import families  # noqa: E402
import family  # noqa: E402

DEFAULT_TIME_LIMIT = 3600.0


class Refused(Exception):
    pass


def first_differing_row(ref, cand):
    """(row index, minute, draws before it) of the first per-minute draw row where the candidate differs, or None when
    every row is equal. A candidate without draws (it did not complete) differs at row 0."""
    rows_a = ref["draws"]["per_minute"]
    rows_b = (cand.get("draws") or {}).get("per_minute") if cand.get("draws") else None
    if rows_b is None:
        return 0, rows_a[0][0], 0
    before = 0
    for i in range(max(len(rows_a), len(rows_b))):
        a = rows_a[i] if i < len(rows_a) else None
        b = rows_b[i] if i < len(rows_b) else None
        if a != b:
            return i, (a or b)[0], before
        before += a[1]
    return None


def specs_of(cand):
    """The kit's port specs the candidate was run with."""
    variant = cand["variant"]
    names = [m for m in cand["ports"] if variant is None or m != variant.split(".")[0]]
    return names + ([variant] if variant else [])


def prove(image, spec, ports, from_draw, time_limit, say):
    """Re-run the match with its ports proved from draw `from_draw`; (ProofError or None, the proof's summary)."""
    from original_match import Match, Fixture
    from original_match.port.prove import ProofError
    players = countries = None
    if spec.edits:
        players, countries = families.apply_edits(image.players(), image.countries(), spec.edits)
    first, second, index, kind = spec.fixture
    m = Match(image, Fixture(first, second, index=index, kind=kind), managed=spec.managed, seed=spec.seed,
              record_draws=True, delay_byte=spec.delay_byte, substitutions=spec.substitutions, players=players,
              countries=countries, timeout_s=min(60, time_limit), ports=ports, prove=from_draw)
    t0 = time.time()
    try:
        family.play(m, spec, time.time() + time_limit)
        found = None
    except ProofError as e:
        found = e
    except Exception as e:          # the match stopped otherwise (an error of the port's, a time limit) before a
        say(f"the proved re-run stopped without a proof's difference: {family.clean_error(e)}")   # call differed
        found = None
    say(f"proved re-run from draw {from_draw}: {time.time() - t0:.0f} s; calls: " + "; ".join(
        f"{a} proved {s['proved']}" + (f", inside another proved call {s['nested']}" if s["nested"] else "")
        + (f", the kit's write listener calls compared {m.prover.listened[a]}" if m.prover.listened[a] else "")
        + (f", before the proof {s['before']}" if s["before"] else "")
        + (f", declared dead registers differing {s['dead']}" if s["dead"] else "")
        + (f", scratch registers differing {s['scratch']}" if s["scratch"] else "")
        for a, s in m.prover.summary().items()))
    return found


def locate(ref, cand, spec, image, time_limit=DEFAULT_TIME_LIMIT, say=print):
    """Say where `cand` first differs from `ref`; returns True when a call was located."""
    if "ports" not in cand:
        raise Refused(f"{cand['id']}: the candidate was run without ports: there is no ported call to prove")
    if "ports" in ref:
        raise Refused(f"{ref['id']}: the reference was run with ports: a reference is the unhooked kit")
    why = compare.completed(cand)
    diff = compare.differences(ref, cand) if not why else []
    if not why and not diff:
        say(f"{cand['id']}: identical to the reference: nothing to locate")
        return False
    say(f"{cand['id']}: ports {cand['ports']}, variant {cand['variant']}; "
        + (f"not completed ({why})" if why else "differs: " + compare.describe(diff)))
    row = first_differing_row(ref, cand)
    if row is None:
        say("the draws are identical row by row: the proof starts at the first draw")
        row = (0, ref["draws"]["per_minute"][0][0], 0)
    index, minute, before = row
    say(f"first differing minute: {minute} (per-minute row {index}; {before} identical draws before it)")
    ports = specs_of(cand)
    found = prove(image, spec, ports, before, time_limit, say)
    if found is None and before > 0:
        say("no proved call differs from that row on: the whole match is proved")
        found = prove(image, spec, ports, 0, time_limit, say)
    if found is None:
        say("NOT LOCATED: no proved call differs")
        return False
    say(f"LOCATED: {found}")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--family", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--match", required=True)
    ap.add_argument("--reference")
    ap.add_argument("--out")
    ap.add_argument("--cache", default=family.DEFAULT_CACHE)
    ap.add_argument("--time-limit", type=float, default=DEFAULT_TIME_LIMIT)
    a = ap.parse_args(argv)
    lines = []

    def say(line):
        print(line, flush=True)
        lines.append(line)
    try:
        if a.out and Path(a.out).exists():
            raise Refused(f"{a.out} exists (an output is never overwritten)")
        chosen = families.select(a.family, families.discover())
        specs = {m.id: (fam, m) for fam in chosen for m in fam.matches}
        if a.match not in specs:
            raise Refused(f"--match {a.match!r} is not a match of --family {a.family}")
        fam, spec = specs[a.match]
        ref_path = Path(a.reference or fam.reference)
        ref_log = compare.load(ref_path if ref_path.is_absolute() else ROOT / ref_path)
        cand_log = compare.load(a.candidate)
        for what, log in (("reference", ref_log), ("candidate", cand_log)):
            if a.match not in log:
                raise Refused(f"{a.match} is not in the {what}")
            r = log[a.match]
            if r["spec_sha256"] != spec.sha256 or r["image_sha256"] != spec.image_sha256:
                raise Refused(f"the {what}'s {a.match} is not the declared match on the declared image")
        ref, cand = ref_log[a.match], cand_log[a.match]
        if compare.completed(ref):
            raise Refused(f"the reference's {a.match} is not a completed match")
        if ref["mask"] != cand["mask"]:
            raise Refused(f"{a.match}: the reference and the candidate were taken over different masks")
        from original_match import Image
        from original_match.assets import reference_image
        image = Image.from_bytes(reference_image(a.cache))
        ok = locate(ref, cand, spec, image, a.time_limit, say)
    except (Refused, families.FamilyError, compare.Malformed) as e:
        print(f"refused: {e}")
        return 2
    if a.out:
        with open(a.out, "x") as f:
            f.write("\n".join(lines) + "\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
