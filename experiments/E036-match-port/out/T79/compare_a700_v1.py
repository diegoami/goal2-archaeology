"""T79 M4: compare.py's own comparison of A700's port arm with its oracle arm.

    PYTHONPATH=runtime python3 -B experiments/E036-match-port/out/T79/compare_a700_v1.py \
        experiments/E036-match-port/out/T79/oracle.jsonl experiments/E036-match-port/out/T79/port.jsonl [--subset]

--subset (Done-when 3's reruns): compare only the matches the candidate holds, every one of them, so
a 20-match rerun is checked against its arm's or the other arm's records.

Why not `compare.py --family A700 --no-screen` itself: the port's records name the `display` port, so
compare.py applies the strict display profile (owner, 2026-10-23), whose reference is one bound file
(families/display/profile.json) holding the 75 admitted matches, not A700; extending that file is
its own reviewed step (#419's). This calls the same `compare.check` with the arguments compare.py
passes under that profile (no_screen=True, strict_display=True, the declared images, mask []), and
takes the reference from A700's own oracle arm (the unhooked kit, mask [], as the bound file). A match
not completed in the oracle arm cannot be a reference (check refuses it); each is left out by name,
listed, and must be not completed in the port arm too, with the same error.
Exit 0 when every compared match is identical, 1 otherwise, 2 for a malformed input.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "experiments/E036-match-port"), str(ROOT)]
import compare  # noqa: E402
import families  # noqa: E402
import records  # noqa: E402


def main(oracle_path, port_path, *flags):
    ref, cand = compare.load(Path(oracle_path)), compare.load(Path(port_path))
    family = families.select("A700", families.discover())[0]
    expected = family.expected()
    if "--subset" in flags:
        expected = {mid: d for mid, d in expected.items() if mid in cand}
        ref = {mid: r for mid, r in ref.items() if mid in expected}
        print(f"subset: {len(expected)} matches")
    left = sorted(mid for mid in expected if mid in ref and not records.is_completed(ref[mid]))
    if not expected:
        print("MALFORMED: no match to compare");return 2
    for mid in left:
        if mid not in cand or records.is_completed(cand[mid]) or cand[mid]["error"] != ref[mid]["error"]:
            print(f"MALFORMED: {mid} is not completed in the oracle arm but is in the port arm, or with another error")
            return 2
        print(f"left out: {mid}: not completed in either arm ({ref[mid]['error']})")
    for mid in left:
        del expected[mid], ref[mid], cand[mid]
    profile = compare.candidate_display_profile(cand, True)
    print(f"strict display profile applied: {profile is not None}; mask {profile['mask'] if profile else None}")
    images = {m.id: m.image_sha256 for m in family.matches if m.id in expected}
    lines, ok = compare.check(ref, cand, expected, "identical", True, images, strict_display=profile is not None)
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main(*sys.argv[1:]))
    except compare.Malformed as e:
        print(f"MALFORMED: {e}")
        sys.exit(2)
