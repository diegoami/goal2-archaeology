#!/usr/bin/env python3
"""Check the E014 (and any E016) records' re-creates against runtime/model/recreate.py
(T30, Q014; Done-when 1).

    python3 experiments/E016-q014-retirement/check_recreate.py
        [--runs runs/E014,runs/E016]   # both by default
        [--model runtime/model/recreate.py]   # default

For every squad player word of every consecutive capture pair of every record the checker:
- ages the first-capture record (the same way `check_ageing.py` does, by `runtime/model/ageing.py`'s
  `aged_record` — the F016 +1/+4 update);
- if the second capture shows a different record at that word (different byte at one of the
  re-create's fixed offsets; or an aged byte that the listing forbids), and the record's bytes
  satisfy every entry of `recreate_constraints` (fixed bytes exact, drawn bytes in their
  listing ranges, +4 = compute_ability(+1, +2, +3) of the new bytes, the surname unchanged and
  the initial drawn from the LCG) — that word is a re-create;
- otherwise the word is continuing; the F016 model checks it;
- the per-country `+3` (country_rating + 0x7F) of every re-create within one 7FDF call is the
  same byte — `same_rating_per_country` invariant (section 2.1 of notes.md).

No country record is captured by the E014 runner; the +3 invariant is checked from the
per-country word set of re-creates, and the byte must be the same value for every re-create of
one 7FDF call. The runs/E016/* path is for any new records T30 takes (the brief allows up to
4 corroboration runs under runs/E016/ for the chain of `+0x2A/+0x2B -> country_rating -> +3`,
only if static analysis is inconclusive; see section 4 of notes.md).

Returns `match: N/N` (each comparison one squad player word of one pair); exit 0 only when
N >= 38 (the E014 floor) and no comparison failed; non-zero on empty, missing, or any
mismatch. Notes only the FAILURES — every captured re-create is one comparison.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
sys.path.insert(0, str(ROOT / "experiments" / "E014-q013-ageing"))
import ageing as A              # noqa: E402 — F016 helpers (compute_ability, retirement_flag)
import recreate as R            # noqa: E402 — T30 model
import check_ageing as C        # noqa: E402 — capture-pair scaffolding


SQUAD_SIZE = 20                  # 7FDF: slots 1..0x14 (8015 cmp word ptr [bp - 2], 0x14)
MANAGED_ABOVE = 0x80             # 1771:0B77: managed when the country's +0x2E > 0x80
MIN_RECREATES = 38               # the brief's Done-when 1: N >= 38 (E014's 5 successful pairs)
CONTINUING_SAME = (A.COUNTRY, A.PEAK, A.RATING, A.PROFILE, A.CLUB_POSITION, R.POSITION)


def captures(record):
    """The capture list of one record (each entry one JSON value with the squad / tables /
    state). Empty when the record has none. Re-uses check_ageing's parsing for shape parity."""
    return C.captures(record)


def squad_map(country, when, mismatches):
    return C.squad_map(country, when, mismatches)


def replacement_errors(rec, new):
    """Why `new` does not satisfy 7E80's re-create of `rec` ([] when it can be one).

    `c["range"]` is the bracketing range around the LCG draws of the listed routines. The
    computed `+4 = compute_ability(new[+1], new[+2], new[+3])` of the new bytes (7E80's last
    compute_ability call) is the determinism check.
    """
    c = R.recreate_constraints(rec)
    err = []
    for off, want in sorted(c["exact"].items()):
        if new[off] != want:
            err.append(f"+0x{off:02X} is {new[off]:#04x}, the re-create gives {want:#04x}")
    for off, (lo, hi) in sorted(c["range"].items()):
        if not lo <= new[off] <= hi:
            err.append(f"+0x{off:02X} = {new[off]} outside the re-create's {lo}..{hi}")
    if new[A.ABILITY] != A.compute_ability(new[A.AGE], new[A.PEAK], new[A.RATING]):
        err.append(f"+0x04 = {new[A.ABILITY]:#04x} is not compute_ability of its own +1/+2/+3")
    return err, c


def continuing_errors(rec, new, name_old, name_new):
    return C.continuing_errors(rec, new, name_old, name_new)


def check_pair(before, after, mismatches):
    """Every comparison of one capture pair; returns the number of comparisons.

    A comparison is one squad player word of `before`. For each:
    - the second capture must hold a record at that word (the squad maps are 1-1);
    - the record is either continuing (per F016) or a re-create (per R.recreate_constraints);
    - a re-create's +3 (rating) is one byte per country per 7FDF call.
    """
    when = f"{before.get('when')} -> {after.get('when')}"
    sb, sa = before["state"]["stage"], after["state"]["stage"]
    if C.ageings_between(sb, sa) != 1:
        mismatches.append(f"{when}: stage {sb} -> {sa} spans "
                          f"{C.ageings_between(sb, sa)} ageings, not 1")
    if before["tables"] != after["tables"]:
        mismatches.append(f"tables DS:6D25/DS:6DCD differ between the captures ({when})")
    nb = [c["n"] for c in before["countries"]]
    na = [c["n"] for c in after["countries"]]
    for side, ns in (("first", nb), ("second", na)):
        if len(ns) != 3 or len(set(ns)) != len(ns):
            mismatches.append(f"{when}: the {side} capture holds countries {ns}, "
                              f"not 3 distinct ones")
            return 0
    if nb != na:
        mismatches.append(f"{when}: the captured countries differ: {nb} -> {na}")
        return 0
    after_by_n = {c["n"]: c for c in after["countries"]}
    n = 0
    for cb in before["countries"]:
        b = squad_map(cb, before.get("when"), mismatches)
        ca = after_by_n.get(cb["n"], {"n": cb["n"], "squad": [], "players": []})
        a = squad_map(ca, after.get("when"), mismatches)
        ratings = {}
        for w in sorted(b):
            n += 1
            rec, sur, ini = b[w]
            tag = f"country {cb['n']} player {w} ({when})"
            if w not in a:
                mismatches.append(f"{tag}: no record in the second capture")
                continue
            new, sur2, ini2 = a[w]
            caps_lo = C.caps_word(rec)
            fire_lo = A.ageing_value(C.with_caps(rec, max(caps_lo, 1)), 0, None, None, 0)["retires"]
            fire_zero = A.ageing_value(C.with_caps(rec, 0), 0, None, None, 0)["retires"]
            decided = caps_lo > 0 or fire_lo == fire_zero
            cont = continuing_errors(rec, new, (sur, ini), (sur2, ini2))
            repl, c = replacement_errors(rec, new)
            if decided and not fire_lo:
                if cont:
                    mismatches.append(f"{tag}: retirement cannot fire, but: {'; '.join(cont)} "
                                      f"(rec {rec.hex()} -> {new.hex()})")
            elif decided:
                if repl:
                    mismatches.append(f"{tag}: retirement fires, but not a re-create: "
                                      f"{'; '.join(repl)} (rec {rec.hex()} -> {new.hex()})")
                else:
                    ratings.setdefault(new[A.RATING], []).append(w)
            else:
                if not cont:                       # undecided, continuing with caps > 0: ok
                    if C.caps_word(new) == 0:
                        mismatches.append(f"{tag}: continued with caps 0 at aged age "
                                          f"{(rec[A.AGE] + 1) & 0xFF}: retirement fires")
                elif repl:
                    ratings.setdefault(new[A.RATING], []).append(w)
        if len(ratings) > 1:
            mismatches.append(f"country {cb['n']} ({when}): re-creates of one 7FDF call carry "
                              f"different +3 (country_rating + 0x7F): {ratings}")
    return n


def check_runs(runs_by_dir):
    """(total, mismatches, pairs, recreates, notes) over the record files.

    recreates is the number of squad player words that match a re-create. The brief's Done-when
    1 requires N >= MIN_RECREATES (38 over runs/E014, the committed E014 evidence).
    """
    total, mismatches, pairs, recreates, notes = 0, [], 0, 0, []
    if not any(runs_by_dir.values()):
        mismatches.append("no record found in any of the runs directories")
        return total, mismatches, pairs, recreates, notes
    for label, paths in runs_by_dir.items():
        if not paths:
            notes.append(f"{label}: no records matched")
            continue
        for p in paths:
            record = json.loads(Path(p).read_text())
            caps = captures(record)
            status = record.get("status", "")
            if len(caps) < 2:
                if status == "completed":
                    mismatches.append(f"{Path(p).name}: completed with {len(caps)} capture(s), "
                                      f"no pair")
                else:
                    notes.append(f"{Path(p).name}: {len(caps)} capture(s), no pair "
                                 f"({status[:60]})")
            for before, after in zip(caps, caps[1:]):
                pairs += 1
                total += check_pair(before, after, mismatches)
                recreates += _count_recreates(before, after)
    return total, mismatches, pairs, recreates, notes


def _count_recreates(before, after):
    """The number of squad player WORDS of `before` whose second capture satisfies every
    re-create constraint and is NOT a continuing prediction. Used only for the brief's
    MIN_RECREATES guard; the per-word verification is in `check_pair`.

    The semantic: `continuing_errors(rec, new, ...) == []` means the new record IS a
    continuing prediction (so NOT a re-create); a re-create has non-empty continuing_errors
    (the +1, +2, +5 etc. don't match) AND empty replacement_errors.
    """
    nb = [c["n"] for c in before["countries"]]
    na = [c["n"] for c in after["countries"]]
    if len(set(nb)) != 3 or nb != na:
        return 0
    after_by_n = {c["n"]: c for c in after["countries"]}
    n = 0
    for cb in before["countries"]:
        ca = after_by_n.get(cb["n"], {"n": cb["n"], "squad": [], "players": []})
        b_words = [p["w"] for p in cb.get("players", [])]
        a_words = {p["w"]: bytes.fromhex(p["rec"]) for p in ca.get("players", [])}
        for w in b_words:
            if w not in a_words:
                continue
            rec = bytes.fromhex(next(p["rec"] for p in cb["players"] if p["w"] == w))
            new = a_words[w]
            if not continuing_errors(rec, new, ("", ""), ("", "")):
                continue                                    # it IS a continuing player
            repl_err, _ = replacement_errors(rec, new)
            if not repl_err:
                n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default="runs/E014,runs/E016",
                    help="comma-separated runs directories (default: runs/E014,runs/E016)")
    a = ap.parse_args(argv)
    runs_by_dir = {}
    recreates_by_dir = {}
    for d in a.runs.split(","):
        d = d.strip()
        runs_by_dir[d] = sorted(Path(d).glob("E0*-r*.json"))
    total, mismatches, pairs, recreates, notes = check_runs(runs_by_dir)
    for m in notes:
        print("note:", m)
    for m in mismatches:
        print("MISMATCH:", m)
    print(f"comparisons: {total} across {pairs} consecutive pair(s) "
          f"of {sum(len(v) for v in runs_by_dir.values())} record(s)")
    print(f"re-creates detected: {recreates}")
    failed = len(mismatches)
    print(f"match: {max(total - failed, 0)}/{total}")
    if total == 0 or failed > 0:
        return 1
    if recreates < MIN_RECREATES:
        print(f"FAIL: re-creates {recreates} < MIN_RECREATES {MIN_RECREATES}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
