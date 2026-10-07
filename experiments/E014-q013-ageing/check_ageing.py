#!/usr/bin/env python3
"""Check the E014 year-end captures against runtime/model/ageing.py (T28, Q013; Done-when 1).

    python3 experiments/E014-q013-ageing/check_ageing.py [--runs runs/E014]

For every consecutive capture pair of every E014 record (the start capture and each year end, in
capture order), for every squad player of the 3 captured countries:

- a CONTINUING player (found in the next capture by surname+initial, the name `1771:2E93`
  prints, AND with the creation bytes +2/+3/+5 unchanged — a same draw): the yearly loop's
  writes must match — +1 = old +1 + 1 (mod 256, `7E6F`), +4 =
  compute_ability(new +1, +2, +3) (`1771:32EB`), +0x11 = 0 (`7FD4`) — and its untouched bytes
  +2, +3, +5, +7 must be unchanged (notes.md section 2; +6 is excluded: the per-match
  bookkeeping repositions national players, r0006). One comparison per player.
- a REPLACED player (the name is gone, or the creation bytes changed — the re-create `7E80`
  drew the same surname and initial, r0006 player 57): `1771:7F40`'s deterministic predicate on
  the OLD record must have fired (retirement_flag = 1), and the replacement must show the
  re-create's marks (caps +8 = 0, goals +0xA = 0, status +0x10 = 0, `7F09`-`7F19`). One
  comparison per player.
  The new bytes themselves are the RNG re-create of `1771:7E80` — Q014, not predicted.
- an UNEXPLAINED new name with no flagged retirement, a continuing player whose writes diverge,
  or a flagged player whose name survives: a mismatch, printed in full.

Also per pair: the derivation tables DS:6D25/DS:6DCD must be identical in both captures (F008's
hazard: the yearly path must not mutate them), and the observed year-over-year deltas of +4 are
reported (the `observed variance` — the spread the creation draws of +2/+3 produce, which the
model reproduces from the records' own bytes, not from a seed). Ends with `match: N/N`; exit 0
only when every comparison matched.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import ageing as A  # noqa: E402

INVARIANT = (0x02, 0x03, 0x05, 0x07)       # bytes the yearly loop never writes (notes.md §2);
# +6 (position) is excluded: the per-match bookkeeping repositions national players
# (0791:AD8F's substitution path sets position from the pitch slot and later restores
# club_position; 1771:4952's 'C' key and unmanage_country's bench copy are the other
# writers) — none of them is the yearly loop, but a year of matches may leave +6 moved
# (r0006: 7 players, e.g. 05 -> 08 and back). +2/+3/+5 are the creation bytes: for a
# name that continues they cannot change, so a change marks a same-name REPLACEMENT
# (r0006 player 57 'R Douwen': retired at 33 > peak 28 + 5, the re-create drew the same
# surname and initial; caps/goals/status zero, the 7E80 marks).
CREATION = (0x02, 0x03, 0x05)


def captures(record):
    out = []
    for o in record["observations"]:
        f = o.get("field", "")
        if o.get("source") == "memory" and f.startswith("capture ") and ": the state bytes" in f:
            out.append((int(f.split()[1]), json.loads(o["value"])))
    return [c for _, c in sorted(out)]


def by_name(cap):
    """{(country, surname_hex, initial_hex): (squad_word, record_bytes)} of one capture."""
    out = {}
    for c in cap["countries"]:
        for p in c["players"]:
            out[(c["n"], p["surname"], p["initial"])] = (p["w"], bytes.fromhex(p["rec"]))
    return out


def year_end_age(rec):
    return (rec[A.AGE] + 1) & 0xFF          # 7E6F increments before 7F40 tests (7FDF's two passes)


def peak_clause(rec):
    """7F40's second clause at the year end: age (after the increment) > peak + 5. Deterministic
    from the capture's own bytes — the loop writes neither +1's base nor +2 (notes.md §2)."""
    return 1 if year_end_age(rec) > rec[A.PEAK] + A.RETIRE_PEAK_MARGIN else 0


def caps_clause(rec, caps_word):
    """7F40's first clause: DS:110E[gk] < age AND the caps word == 0, with the age after the
    increment and the caps the year end saw (they only grow during a season, so a capture's
    caps > 0 excludes the clause, and caps == 0 leaves it open until the year-end value)."""
    gk = 1 if rec[A.CLUB_POSITION] == 0 else 0
    return 1 if A.RETIRE_LIMIT[gk] < year_end_age(rec) and caps_word == 0 else 0


def caps_word(rec):
    return rec[A.CAPS] | (rec[A.CAPS + 1] << 8)


def check_pair(before, after, mismatches):
    """Every comparison of one capture pair; returns the number of comparisons."""
    n = 0
    if before["tables"] != after["tables"]:
        mismatches.append(f"tables DS:6D25/DS:6DCD differ between the captures "
                          f"({before['when']} -> {after['when']})")
    b, a = by_name(before), by_name(after)
    for key, (w, rec) in sorted(b.items()):
        n += 1
        same_name = key in a
        if same_name and any(a[key][1][off] != rec[off] for off in CREATION):
            same_name = False          # the creation bytes changed: a same-name replacement
        if same_name:                   # a continuing player
            w2, new = a[key]
            pred = A.ageing_value(rec, 0, None, None, 0)
            for off, want in ((A.AGE, pred[A.AGE]), (A.ABILITY, pred[A.ABILITY]), (A.DEAD_BYTE, 0)):
                if new[off] != want:
                    mismatches.append(f"{key} (player {w}): +0x{off:02X} is {new[off]:02x}, predicted {want:02x}")
            for off in INVARIANT:
                if new[off] != rec[off]:
                    mismatches.append(f"{key} (player {w}): +0x{off:02X} changed {rec[off]:02x} -> {new[off]:02x}")
            if peak_clause(rec):
                mismatches.append(f"{key} (player {w}): the peak clause fired (year-end age "
                                  f"{year_end_age(rec)} > peak {rec[A.PEAK]} + 5) but the player continued")
            elif caps_clause(rec, caps_word(new)):
                mismatches.append(f"{key} (player {w}): the caps clause fired (year-end age "
                                  f"{year_end_age(rec)}, caps {caps_word(new)}) but the player continued")
        else:                                          # replaced: a clause must have fired
            if caps_word(rec) > 0 and not peak_clause(rec):
                mismatches.append(f"{key} (player {w}): the name is gone but no clause can have fired "
                                  f"(caps {caps_word(rec)} > 0, year-end age {year_end_age(rec)}, peak "
                                  f"{rec[A.PEAK]}; rec {rec.hex()})")
            elif caps_word(rec) == 0 and not peak_clause(rec):
                gk = 1 if rec[A.CLUB_POSITION] == 0 else 0
                if not A.RETIRE_LIMIT[gk] < year_end_age(rec):
                    mismatches.append(f"{key} (player {w}): the name is gone but retirement_flag cannot "
                                      f"have fired (rec {rec.hex()})")
    # every new name (or same-name replacement) must sit at the squad word of a replaced player
    gone = {key: (w, rec) for key, (w, rec) in b.items()
            if key not in a or any(a[key][1][off] != rec[off] for off in CREATION)}
    for key, (w, rec) in sorted(a.items()):
        if key in b and not any(rec[off] != b[key][1][off] for off in CREATION):
            continue          # a continuing player, checked above
        n += 1
        slot = [(k, ww, rr) for k, (ww, rr) in gone.items() if k[0] == key[0] and ww == w]
        if not slot:
            mismatches.append(f"{key} (player {w}): a new name with no replaced player at the same slot")
        else:
            if rec[A.CAPS] or rec[A.CAPS + 1] or rec[0x0A] or rec[0x0B] or rec[0x10]:
                mismatches.append(f"{key} (player {w}): the replacement does not show 7E80's marks "
                                  f"(caps/goals/status not zero: {rec.hex()})")
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs" / "E014"))
    a = ap.parse_args(argv)
    runs = sorted(Path(a.runs).glob("E014-r*.json"))
    total, mismatches, pairs, deltas = 0, [], 0, []
    for p in runs:
        record = json.loads(p.read_text())
        caps = captures(record)
        for before, after in zip(caps, caps[1:]):
            pairs += 1
            total += check_pair(before, after, mismatches)
            for c1, c2 in zip(before["countries"], after["countries"]):
                m1 = {(q["surname"], q["initial"]): q for q in c1["players"]}
                for q in c2["players"]:
                    k = (q["surname"], q["initial"])
                    if k in m1:
                        old = bytes.fromhex(m1[k]["rec"])
                        new = bytes.fromhex(q["rec"])
                        if any(new[off] != old[off] for off in CREATION):
                            continue      # a same-name replacement, not a year of ageing
                        deltas.append(new[A.ABILITY] - old[A.ABILITY])
    for m in mismatches:
        print("MISMATCH:", m)
    if deltas:
        hist = {}
        for d in deltas:
            hist[d] = hist.get(d, 0) + 1
        print(f"observed variance: {len(deltas)} continuing players, +4 deltas "
              f"{json.dumps({str(k): hist[k] for k in sorted(hist)})}")
    print(f"captures in {len(runs)} record(s), {pairs} consecutive pair(s)")
    print(f"match: {total - len(mismatches)}/{total}")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
