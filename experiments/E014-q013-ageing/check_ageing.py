#!/usr/bin/env python3
"""Check the E014 year-end captures against runtime/model/ageing.py (T28, Q013; Done-when 1).

    python3 experiments/E014-q013-ageing/check_ageing.py [--runs runs/E014]

For every consecutive capture pair of every E014 record (the start capture and each year end,
in capture order):

- the pair must span exactly ONE ageing: the stage path from the first capture's stage byte to
  the second's (+1 steps wrapped in [2, 8], 214B:1D6F) enters exactly one stage of the gate set
  {2, 3, 5, 7} (CS:81E8, seg_1771_12.asm:118/156-163); the derivation tables DS:6D25/DS:6DCD
  must be identical (F008's hazard);
- the same countries, each a COMPUTER country in both captures (+0x2E <= 0x80, 1771:0B77 —
  the retirement pass runs only there), each squad 20 nonzero, distinct player words, with
  exactly one captured record per squad word, and the same SET of words in both captures
  (7E80 re-creates in place, so no word joins or leaves);
- every squad player WORD of the first capture is one comparison, matched by identity (the
  word), never by name. 7F40's predicate is applied by the model to the AGED record
  (`ageing_value(...)['retires']`; 7FDF's first pass ages, its second tests,
  seg_1771_11.asm:1043/:1098). The year end's caps word is not captured; caps only grow for a
  computer-country player between year ends (the writers of +8 are 0791:B908 `inc`, the
  re-create's 7F09 and the managed offer path's 000E:5584), so a first-capture caps > 0 settles
  the caps clause; with caps 0 and the age clause open the outcome depends on whether a cap
  was won, and the second capture decides it:
  - predicate certainly 0 -> CONTINUING: +0, +2, +3, +5, +7, the surname and the initial
    unchanged, +1 = old + 1 (7E6F), +4 = compute_ability (32EB), +0x11 = 0 (7FD4), caps not
    smaller; (+6 is not compared: per-match repositioning, notes.md section 6);
  - predicate certainly 1 -> REPLACED by 7E80: every constraint of
    `ageing.recreate_constraints(old)` (+0/+7 carried into make_player, the zeroed bytes, the
    age/peak/profile draw ranges, +4 of its own bytes, one +3 per country), the surname kept
    (7E80 writes only the initial, 7F2D) — a continuing record never passes them when 7F40
    fires (the aged age is then above the re-create's age range; test_model_ageing pins it);
  - undecided (caps 0, the age clause open) -> continuing with caps > 0 in the second capture
    (a cap won: the clause closed), or replaced as above; continuing with caps 0 is a mismatch.
- a record that ends "completed" must carry at least one pair; an aborted record's pairs are
  checked like any other and the abort is reported. No record, or no comparison at all, is a
  failure, not a match.

Reports the observed +4 deltas of the continuing players (the `observed variance`: the spread
the creation draws of +2/+3 produce, reproduced from the records' own bytes, not from a seed).
Ends with `match: N/N`; exit 0 only when N > 0 and every comparison matched.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
import ageing as A  # noqa: E402

MANAGED_ABOVE = 0x80   # 1771:0B77: managed when the country's +0x2E > 0x80
SQUAD_SIZE = 20        # 7FDF: slots 1..0x14 (8015 cmp word ptr [bp - 2], 0x14)
CONTINUING_SAME = (A.COUNTRY, A.PEAK, A.RATING, A.PROFILE, A.CLUB_POSITION)


def captures(record):
    out = []
    for o in record["observations"]:
        f = o.get("field", "")
        if o.get("source") == "memory" and f.startswith("capture ") and ": the state bytes" in f:
            out.append((int(f.split()[1]), json.loads(o["value"])))
    return [c for _, c in sorted(out)]


def ageings_between(stage_before, stage_after):
    """The number of gate stages entered on the way from one stage byte to the other; None
    when either is not a stage of 214B:1D6F's range [2, 8]."""
    lo, hi = A.STAGE_RANGE
    if not (lo <= stage_before <= hi and lo <= stage_after <= hi):
        return None
    s, n, steps = stage_before, 0, 0
    while True:
        s = lo if s >= hi else s + 1          # 214B:1D6F(+0x3C, 2, 8, 1)
        steps += 1
        if s in A.AGEING_STAGES:
            n += 1
        if s == stage_after or steps > hi - lo + 1:
            return n


def caps_word(rec):
    return rec[A.CAPS] | (rec[A.CAPS + 1] << 8)


def with_caps(rec, caps):
    r = bytearray(rec)
    r[A.CAPS], r[A.CAPS + 1] = caps & 0xFF, (caps >> 8) & 0xFF
    return bytes(r)


def squad_map(country, when, mismatches):
    """{word: (rec, surname, initial)} of one captured country, with the coverage checks."""
    tag = f"country {country.get('n')} ({when})"
    squad = country.get("squad", [])
    if len(squad) != SQUAD_SIZE or 0 in squad or len(set(squad)) != len(squad):
        mismatches.append(f"{tag}: the squad is not {SQUAD_SIZE} distinct nonzero words: {squad}")
    words = [p["w"] for p in country.get("players", [])]
    if sorted(words) != sorted(set(squad)) or len(words) != len(set(words)):
        mismatches.append(f"{tag}: the captured records {sorted(words)} are not the squad "
                          f"{sorted(squad)}, one each")
    if country.get("manager_byte", 0) > MANAGED_ABOVE:
        mismatches.append(f"{tag}: a managed country (+0x2E = {country['manager_byte']:#x}): "
                          f"no retirement pass, not a computer country")
    out = {}
    for p in country.get("players", []):
        rec = bytes.fromhex(p["rec"])
        if len(rec) != 20:
            mismatches.append(f"{tag}: player {p['w']}'s record is {len(rec)} bytes")
            continue
        out[p["w"]] = (rec, p["surname"], p["initial"])
    return out


def continuing_errors(rec, new, name_old, name_new):
    """Why `new` is not the continuing prediction from `rec` ([] when it is)."""
    pred = A.ageing_value(rec, 0, None, None, 0)
    err = []
    for off in (A.AGE, A.ABILITY, A.SCORER_COUNT):
        if new[off] != pred[off]:
            err.append(f"+0x{off:02X} is {new[off]:02x}, predicted {pred[off]:02x}")
    for off in CONTINUING_SAME:
        if new[off] != rec[off]:
            err.append(f"+0x{off:02X} changed {rec[off]:02x} -> {new[off]:02x}")
    if caps_word(new) < caps_word(rec):
        err.append(f"caps fell {caps_word(rec)} -> {caps_word(new)}")
    if name_new != name_old:
        err.append(f"the name changed {name_old} -> {name_new}")
    return err


def replacement_errors(rec, new, name_old, name_new):
    """Why `new` is not a 7E80 re-create of `rec` ([] when it can be one)."""
    c = A.recreate_constraints(rec)
    err = []
    for off, want in sorted(c["exact"].items()):
        if new[off] != want:
            err.append(f"+0x{off:02X} is {new[off]:02x}, the re-create gives {want:02x}")
    for off, (lo, hi) in sorted(c["range"].items()):
        if not lo <= new[off] <= hi:
            err.append(f"+0x{off:02X} = {new[off]} outside the re-create's {lo}..{hi}")
    if new[A.ABILITY] != A.compute_ability(new[A.AGE], new[A.PEAK], new[A.RATING]):
        err.append(f"+0x04 = {new[A.ABILITY]:02x} is not compute_ability of its own +1/+2/+3")
    if name_new[0] != name_old[0]:
        err.append(f"the surname changed {name_old[0]} -> {name_new[0]} (7E80 writes only the initial)")
    # A continuing record cannot pass these when 7F40 fires: the caps clause needs an aged age
    # above DS:110E[gk] = DS:110C[gk] + 5, the peak clause one above p + 5 with p >= DS:0E80[gk]
    # - 2 = DS:110C[gk] (roll_peak_age's range) — both above the re-create's age range
    # (test_model_ageing.CheckerTests.test_retiree_never_passes_as_recreate visits the edge).
    return err


def check_pair(before, after, mismatches):
    """Every comparison of one capture pair; returns the number of comparisons (one per squad
    player word of `before`). Each mismatch is appended to `mismatches`."""
    when = f"{before.get('when')} -> {after.get('when')}"
    sb, sa = before["state"]["stage"], after["state"]["stage"]
    if ageings_between(sb, sa) != 1:
        mismatches.append(f"{when}: stage {sb} -> {sa} spans {ageings_between(sb, sa)} ageings, not 1")
    if before["tables"] != after["tables"]:
        mismatches.append(f"tables DS:6D25/DS:6DCD differ between the captures ({when})")
    nb = [c["n"] for c in before["countries"]]
    na = [c["n"] for c in after["countries"]]
    if nb != na or not nb:
        mismatches.append(f"{when}: the captured countries differ or are empty: {nb} -> {na}")
    after_by_n = {c["n"]: c for c in after["countries"]}
    n = 0
    for cb in before["countries"]:
        b = squad_map(cb, before.get("when"), mismatches)
        ca = after_by_n.get(cb["n"], {"n": cb["n"], "squad": [], "players": []})
        a = squad_map(ca, after.get("when"), mismatches)
        if set(b) != set(a):
            mismatches.append(f"country {cb['n']} ({when}): the squad words differ: gone "
                              f"{sorted(set(b) - set(a))}, new {sorted(set(a) - set(b))}")
        ratings = {}
        for w in sorted(b):
            n += 1
            rec, sur, ini = b[w]
            tag = f"country {cb['n']} player {w} ({when})"
            if w not in a:
                mismatches.append(f"{tag}: no record in the second capture")
                continue
            new, sur2, ini2 = a[w]
            caps_lo = caps_word(rec)
            fire_lo = A.ageing_value(with_caps(rec, max(caps_lo, 1)), 0, None, None, 0)["retires"]
            fire_zero = A.ageing_value(with_caps(rec, 0), 0, None, None, 0)["retires"]
            decided = caps_lo > 0 or fire_lo == fire_zero
            cont = continuing_errors(rec, new, (sur, ini), (sur2, ini2))
            repl = replacement_errors(rec, new, (sur, ini), (sur2, ini2))
            if decided and not fire_lo:
                if cont:
                    mismatches.append(f"{tag}: retirement cannot fire, but: {'; '.join(cont)} "
                                      f"(rec {rec.hex()} -> {new.hex()})")
            elif decided:
                if repl:
                    mismatches.append(f"{tag}: retirement fires, but not a re-create: {'; '.join(repl)} "
                                      f"(rec {rec.hex()} -> {new.hex()})")
                else:
                    ratings.setdefault(new[A.RATING], []).append(w)
            elif not cont:                       # undecided, continuing
                if caps_word(new) == 0:
                    mismatches.append(f"{tag}: continued with caps 0 at year-end age "
                                      f"{(rec[A.AGE] + 1) & 0xFF}: retirement fires (rec {rec.hex()})")
            elif repl:
                mismatches.append(f"{tag}: neither continuing ({'; '.join(cont)}) nor a re-create "
                                  f"({'; '.join(repl)}) (rec {rec.hex()} -> {new.hex()})")
            else:
                ratings.setdefault(new[A.RATING], []).append(w)
        if len(ratings) > 1:
            mismatches.append(f"country {cb['n']} ({when}): re-creates of one 7FDF call carry "
                              f"different +3 (country_rating + 0x7F): {ratings}")
    return n


def check_runs(paths):
    """(total comparisons, mismatches, pairs, deltas, notes) over the record files."""
    total, mismatches, pairs, deltas, notes = 0, [], 0, [], []
    if not paths:
        mismatches.append("no E014 record found")
    for p in paths:
        record = json.loads(Path(p).read_text())
        caps = captures(record)
        status = record.get("status", "")
        if len(caps) < 2:
            if status == "completed":
                mismatches.append(f"{Path(p).name}: completed with {len(caps)} capture(s), no pair")
            else:
                notes.append(f"{Path(p).name}: {len(caps)} capture(s), no pair ({status[:60]})")
        for before, after in zip(caps, caps[1:]):
            pairs += 1
            total += check_pair(before, after, mismatches)
            for c1, c2 in zip(before["countries"], after["countries"]):
                m2 = {q["w"]: bytes.fromhex(q["rec"]) for q in c2["players"]}
                for q in c1["players"]:
                    old, new = bytes.fromhex(q["rec"]), m2.get(q["w"])
                    if new is not None and all(new[o] == old[o] for o in CONTINUING_SAME) \
                            and new[A.AGE] == (old[A.AGE] + 1) & 0xFF:
                        deltas.append(new[A.ABILITY] - old[A.ABILITY])
    if total == 0:
        mismatches.append("no comparison was made: nothing corroborated")
    return total, mismatches, pairs, deltas, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs" / "E014"))
    a = ap.parse_args(argv)
    runs = sorted(Path(a.runs).glob("E014-r*.json"))
    total, mismatches, pairs, deltas, notes = check_runs(runs)
    for m in notes:
        print("aborted:", m)
    for m in mismatches:
        print("MISMATCH:", m)
    if deltas:
        hist = {}
        for d in deltas:
            hist[d] = hist.get(d, 0) + 1
        print(f"observed variance: {len(deltas)} continuing players, +4 deltas "
              f"{json.dumps({str(k): hist[k] for k in sorted(hist)})}")
    print(f"captures in {len(runs)} record(s), {pairs} consecutive pair(s)")
    failed = len(mismatches)
    print(f"match: {max(total - failed, 0)}/{total}")
    return 0 if total > 0 and not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
