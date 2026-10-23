#!/usr/bin/env python3
"""E036 (T57): the whole-match acceptance check over the families. Compares a candidate log with the reference of each
family, match by match, and FAILS CLOSED (E032's rules, PR 243, for these records).

    python3 -B experiments/E036-match-port/compare.py --family ALL --candidate <file.jsonl> [--reference <file.jsonl>]
        [--expect identical|differ] [--no-screen]

--family is ALL or comma-separated family names (families/*.json). The candidate must hold exactly the matches of
those families, each once. Each family names its reference (the unhooked kit over that family); --reference names
one log for all of them instead (a masked reference, say). The reference may hold more matches than the families
asked for.

Every record is validated before anything is compared, to its leaves, against records.py's grammar (strict JSON, closed
keys, whole-string patterns, ranges, the per-minute draws adding up to the count, the digests per 1 KiB of the exact
count each range has). A record that fails makes the log MALFORMED: it never counts as equal, nor as a difference.
Also MALFORMED: a match missing from the reference or the candidate, an unexpected or duplicated match, a record whose
spec digest is not the declared match's (another seed, edit, policy or policy code), a record of another image, two
masks (the reference's and the candidate's), a reference match that did not complete.

--expect identical (the default): every candidate match must be completed (no error, the full-time board reached, no
stray decision) and equal to its reference in every compared field: score, ticks, the draws (count, digest, one digest
per minute), the events, the board's statistics, bars, man of the match, final score and seed, the commentary's
template counts, the result's digest, the decisions, and after the post-match update the seed word and the digest of
every 1 KiB of DS and of every range. The first differing field is named, with the minute where the draws give one.
--expect differ (a falsifier caught): every candidate match must differ from its reference in one of those fields, or
be a match that did not complete (a falsifier that hangs or errors is caught as well); an identical match is NOT CAUGHT.
--no-screen with the new display profile leaves out the board screen digest and uses the independently proved byte
mask/reference; every DS block and every other compared field stays. Historical unprofiled --no-screen retains its
legacy screen-buffer block exclusions. The pitch background always stays. The display-profile producer also excludes
only full_time.data.screen_sha256 from the event digest, in both original references and candidates.

    python3 -B experiments/E036-match-port/compare.py --e032 --candidate <reference.jsonl>
prints, per seed, whether F40's ten E032 matches ('F40/e032-*') equal original_match.check's EXPECTED_FAMILY (score,
ticks, draws, draws digest): exit 0 when all ten do, 1 when one does not, 2 when one is missing or malformed.

Exit status: 0 when every expected match passes, 1 when one fails its expectation, 2 when the command or a log is
malformed or evidence is missing (never a pass)."""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import families  # noqa: E402
import records  # noqa: E402
import family as family_runner  # noqa: E402

ROOT = HERE.parents[1]
FIELDS = ("score", "ticks", "draws.count", "draws.digest", "draws.per_minute", "events", "board.statistics",
          "board.bars", "board.man_of_the_match", "board.final_score", "board.seed", "templates", "result_sha256",
          "decisions", "after.seed", "after.ds", "after.ranges", "board.screen_sha256")
SCREEN_FIELDS = ("board.screen_sha256",)


class Malformed(Exception):
    pass


def get(r, field):
    for part in field.split("."):
        r = r[part]
    return r


def completed(r):
    """None when the (validated) record is a completed match, else why not."""
    why = []
    if r["error"] is not None:
        why.append(f"error {r['error']!r}")
    if r["stopped_at_board"] is not True:
        why.append("did not stop at the full-time board")
    if r["strays"]:
        why.append(f"stray decisions {r['strays']!r}")
    return "; ".join(why) or None


def block_difference(a, b, label, skip=()):
    """The first 1 KiB block (not in `skip`) where two digest lists differ, as text, or None."""
    for k in range(max(len(a), len(b))):
        if k in skip:
            continue
        if k >= len(a) or k >= len(b) or a[k] != b[k]:
            return f"{label}+0x{k * records.BLOCK:04X}"
    return None


def differences(a, b, no_screen=False, strict_display=False):
    """[(field, where)] for every compared field in which two completed records differ, in FIELDS order. `where` names
    the minute (draws), the 1 KiB block (memory) or the row that differs first, else ''."""
    out = []
    skip_blocks = set(records.SCREEN_DS_BLOCKS) if no_screen and not strict_display else set()
    for field in FIELDS:
        if no_screen and field in SCREEN_FIELDS:
            continue
        x, y = get(a, field), get(b, field)
        if field == "after.ds":
            where = block_difference(x, y, "DS", skip_blocks)
            if where:
                out.append((field, where))
        elif field == "after.ranges":
            for name in records.RANGES:
                where = block_difference(x[name], y[name], name)
                if where:
                    out.append((f"after.ranges.{name}", where))
        elif x != y:
            where = ""
            if field == "draws.per_minute":
                i = next((i for i in range(min(len(x), len(y))) if x[i] != y[i]), min(len(x), len(y)))
                row_x, row_y = (x[i] if i < len(x) else None), (y[i] if i < len(y) else None)
                minute = (row_x or row_y)[0]
                where = f"minute {minute} (reference {row_x and row_x[1]} draws, candidate {row_y and row_y[1]})"
            out.append((field, where))
    return out


def candidate_display_profile(candidate, no_screen):
    """Strict new profile for display ports or records over its mask; legacy behavior is retained.

    Owner decision 2026-10-23: new display records compare every DS block over the
    proved byte mask, while historical unprofiled --no-screen retains its behavior.
    """
    if not no_screen:
        return None
    required = any("display" in record.get("ports", ()) for record in candidate.values())
    masks = [record["mask"] for record in candidate.values()]
    if not required and not (any(masks) and family_runner.DISPLAY_PROFILE.exists()):
        return None
    try:
        profile = family_runner.read_display_profile()
    except family_runner.Refused as exc:
        raise Malformed(str(exc)) from exc
    matching = [mask == profile["mask"] for mask in masks]
    if required and not all(matching):
        raise Malformed("candidate mask differs from the declared display profile")
    return profile if all(matching) else None


def describe(diff):
    """The first differing field (with its minute or block), the minute where the draws first differ when that is not
    the first field, and the other differing fields."""
    first = f"first at {diff[0][0]}" + (f" ({diff[0][1]})" if diff[0][1] else "")
    draws = next((w for f, w in diff if f == "draws.per_minute"), None)
    rest = [f for f, _ in diff[1:] if f != "draws.per_minute" or diff[0][0] == "draws.per_minute"]
    text = first
    if draws and diff[0][0] != "draws.per_minute":
        text += f"; the draws first differ at {draws}"
    if rest:
        text += f"; also {', '.join(rest[:6])}" + (f" and {len(rest) - 6} more" if len(rest) > 6 else "")
    return text


def check(ref, cand, expected, expect="identical", no_screen=False, image_sha256=None, strict_display=False):
    """(lines, passed) for the matches of `expected` ({id: spec digest}); ref and cand are {id: record}. Raises Malformed
    on a missing or unexpected match, a record that is not the declared match's, an incomplete reference, two masks."""
    missing_ref = sorted(set(expected) - set(ref))
    missing = sorted(set(expected) - set(cand))
    unexpected = sorted(set(cand) - set(expected))
    if missing_ref or missing or unexpected:
        raise Malformed("match family mismatch: " + "; ".join(
            f"{what}: {', '.join(lst[:8])}" + (f" and {len(lst) - 8} more" if len(lst) > 8 else "") for what, lst in (
                ("missing from the reference", missing_ref), ("missing from the candidate", missing),
                ("unexpected in the candidate", unexpected)) if lst))
    for what, log in (("reference", ref), ("candidate", cand)):
        for mid in expected:
            r = log[mid]
            if r["spec_sha256"] != expected[mid]:
                raise Malformed(f"{what} {mid}: its spec digest is not the declared match's (another seed, edit, "
                                "fixture, policy or policy code)")
            if image_sha256 is not None and r["image_sha256"] != image_sha256:
                raise Malformed(f"{what} {mid}: it was played from another image than {image_sha256[:8]}...")
    for mid in expected:
        why = completed(ref[mid])
        if why:
            raise Malformed(f"reference {mid} is not a completed match ({why})")
        if "ports" in ref[mid]:                 # T59: the reference is the unhooked kit, never a ported run
            raise Malformed(f"reference {mid} was run with ports ({ref[mid]['ports']}): a reference is the unhooked kit")
        if ref[mid]["mask"] != cand[mid]["mask"]:
            raise Malformed(f"{mid}: the reference was taken over mask {ref[mid]['mask']}, the candidate over "
                            f"{cand[mid]['mask']}")
    lines, passed = [], 0
    for mid in expected:
        a, b = ref[mid], cand[mid]
        bad = completed(b)
        diff = differences(a, b, no_screen, strict_display) if not bad else []
        head = (f"{mid}: score {a['score']} ticks {a['ticks']} draws {a['draws']['count']} "
                f"cpu {a['cpu_s']} s -> {b['cpu_s']} s; ")
        if expect == "identical":
            ok = not bad and not diff
            verdict = "identical" if ok else f"NOT COMPLETED ({bad})" if bad else "DIFFER: " + describe(diff)
        else:
            ok = bool(bad or diff)
            verdict = (f"caught: not completed ({bad})" if bad else
                       "caught: " + describe(diff) if diff else "NOT CAUGHT: identical")
        passed += ok
        lines.append(head + verdict + ("" if ok else ": FAIL"))
    lines.append(f"{len(expected)} matches expected {expect}, {passed} pass, {len(expected) - passed} fail")
    return lines, passed == len(expected)


def load(path):
    """{id: record} of a log. Strict (records.read_log); an id twice is malformed."""
    try:
        recs = records.read_log(path)
    except records.SchemaError as e:
        raise Malformed(str(e))
    out = {}
    for r in recs:
        if r["id"] in out:
            raise Malformed(f"{path}: {r['id']} appears twice")
        out[r["id"]] = r
    return out


def e032(log, declared):
    """(lines, ok): the ten matches 'F40/e032-<seed>' of the log against check.py's EXPECTED_FAMILY, per seed. Raises
    Malformed when one is missing, is not the declared match or did not complete."""
    from original_match.check import EXPECTED_FAMILY
    lines, ok = [], True
    for seed, (score, ticks, draws, digest) in sorted(EXPECTED_FAMILY.items()):
        mid = f"F40/e032-{seed:04x}"
        if mid not in log or mid not in declared:
            raise Malformed(f"{mid} is missing from the log or not a declared match")
        spec = declared[mid]
        if spec.seed != seed or log[mid]["spec_sha256"] != spec.sha256:
            raise Malformed(f"{mid}: not the declared match with seed 0x{seed:04x}")
        why = completed(log[mid])
        if why:
            raise Malformed(f"{mid} is not a completed match ({why})")
        r = log[mid]
        got = [r["score"], r["ticks"], r["draws"]["count"], r["draws"]["digest"]]
        want = [score, ticks, draws, digest]
        equal = got == want
        ok = ok and equal
        lines.append(f"seed 0x{seed:04X}: score {got[0]} ticks {got[1]} draws {got[2]} digest {got[3][:8]}... "
                     + ("equal to check.py's EXPECTED_FAMILY" if equal else
                        f"DIFFERS from EXPECTED_FAMILY (score {score} ticks {ticks} draws {draws} digest {digest[:8]}...): FAIL"))
    lines.append(f"{len(EXPECTED_FAMILY)} E032 seeds, {'all equal' if ok else 'NOT all equal'}")
    return lines, ok


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--family")
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--e032", action="store_true")
    ap.add_argument("--reference")
    ap.add_argument("--expect", choices=("identical", "differ"), default="identical")
    ap.add_argument("--no-screen", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.e032 != (a.family is None) or (a.e032 and (a.reference or a.no_screen or a.expect != "identical")):
            raise Malformed("give --family (a comparison), or --e032 alone with --candidate (the E032 seeds' check)")
        try:
            declared = families.discover()
            chosen = families.select(a.family, declared) if not a.e032 else []
        except families.FamilyError as e:
            raise Malformed(str(e))
        if a.e032:
            lines, ok = e032(load(a.candidate), {m.id: m for fam in declared.values() for m in fam.matches})
            print("\n".join(lines))
            return 0 if ok else 1
        cand = load(a.candidate)
        profile = candidate_display_profile(cand, a.no_screen)
        if profile and a.reference is not None:
            supplied = Path(a.reference)
            supplied = supplied if supplied.is_absolute() else ROOT / supplied
            bound = Path(profile["reference"])
            bound = bound if bound.is_absolute() else ROOT / bound
            if supplied.resolve() != bound.resolve():
                raise Malformed("--reference differs from the declared display profile reference")
        groups = {}
        for fam in chosen:
            groups.setdefault(a.reference or (profile["reference"] if profile else fam.reference), []).append(fam)
        ref, expected = {}, {}
        for path, fams in groups.items():
            log = load(Path(path) if Path(path).is_absolute() else ROOT / path)
            for fam in fams:
                for mid, digest in fam.expected().items():
                    expected[mid] = digest
                    if mid in log:
                        ref[mid] = log[mid]
        lines, ok = check(ref, cand, expected, a.expect, a.no_screen, families.image_sha256(), strict_display=profile is not None)
    except Malformed as e:
        print(f"MALFORMED: {e}")
        return 2
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
