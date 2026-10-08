#!/usr/bin/env python3
"""Check every re-create in the E014 (and any E016) records against runtime/model/recreate.py
(T30, Q014; Done-when 1).

    python3 experiments/E016-q014-retirement/check_recreate.py [--runs runs/E014,runs/E016]

For every consecutive capture pair of every record, every squad player WORD of the first capture
is one comparison, matched by the word (the player's identity), never by name. 7F40's predicate
is applied to the AGED record (F016; the year end's caps word is not captured, so a first-capture
caps of 0 with the age clause open leaves the outcome undecided until the second capture):

- predicate certainly 0 -> the word must be CONTINUING (check_ageing.continuing_errors, F016);
- predicate certainly 1 -> the word must be a RE-CREATE: every part of
  `recreate.recreate_contract` a capture can show (below);
- undecided -> continuing with caps > 0 in the second capture (a cap was won), or a re-create
  as above; a record that is NEITHER is a mismatch.

The re-create contract checked (7E80 as notes.md section 3 maps it), on the record the second
capture holds at the word, the retiree being the first capture's record aged by 7FDF's first
pass (`ageing.aged_record`):
- exact: +0, +7, +8..+0xB = 0, +0x10 = 0, +0x11 = 0, +0x12/+0x13 = FF 7F;
- ranges: +1 in DS:110C[gk] +- 5, +2 in DS:0E80[gk] +- 2, +5 in 1..16, +0xC in 1..32, +0xD in
  14..32, +3 in 0x80..0xFF; +0xE = +0xD; +4 = compute_ability of the new +1/+2/+3;
- +0xF: the bits 1771:3431 sets are set and the bit it clears is clear (3431 read +6 = +7);
- the initial one of DS:0C38's 21 letters, the surname kept;
- one +3 for all re-creates of one country in one pair (country_rating reads the country
  record, which nothing in 80DA writes);
- EXACT, when the pair's countries are 1..k (80DA runs 7FDF for countries 1..128 in order and
  the ageing pass draws nothing, so country 1's first re-create makes the first draw of 80DA):
  the 16-bit RNG word at 80DA's entry is not captured, so every one of the 65536 values is
  tried; a value must reproduce every drawn byte (+1, +2, +5, +0xC, +0xD, +0xE, +4 and the
  initial) of every re-create of the pair, ten draws each, in country order and in the slot
  order of the second capture's squad. No value -> a mismatch; the number of values that
  do is printed.

Not checked, because a capture a year earlier cannot show them (recreate.NOT_IN_CAPTURES,
printed): +6 (the retiree's +6 at the instant), the +0xF bits 3431 leaves as they were, and +3
exactly (the country record is not captured).

Ends with `match: N/N` over the re-creates; exit 0 only when at least one re-create was compared
and every comparison of every word matched. No record, or no comparison, is a failure.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "model"))
sys.path.insert(0, str(ROOT / "experiments" / "E014-q013-ageing"))
import ageing as A              # noqa: E402 — F016: aged_record, compute_ability, the offsets
import recreate as R            # noqa: E402 — T30: the re-create's contract and its exact form
import check_ageing as C        # noqa: E402 — capture parsing, the continuing check (F016)

DRAWN = (A.AGE, A.PEAK, A.ABILITY, A.PROFILE, R.MORALE, R.FITNESS, R.ENERGY)
SEEDS = 0x10000                 # the RNG word is 16 bits (214B:0688)


def replacement_errors(rec, new, name_old, name_new):
    """Why `new` (the second capture's record, surname and initial as hex) cannot be 7E80's
    re-create of the first capture's `rec` ([] when it can be)."""
    inst = A.aged_record(rec)                    # the record as 7FDF's second pass sees it
    c = R.recreate_contract(inst)
    err = []
    for off, want in sorted(c["exact"].items()):
        if off not in R.NOT_IN_CAPTURES and new[off] != want:
            err.append(f"+0x{off:02X} is {new[off]:02x}, the re-create gives {want:02x}")
    for off, (lo, hi) in sorted(c["range"].items()):
        if not lo <= new[off] <= hi:
            err.append(f"+0x{off:02X} = {new[off]} outside the re-create's {lo}..{hi}")
    for off, other in sorted(c["same_as"].items()):
        if new[off] != new[other]:
            err.append(f"+0x{off:02X} = {new[off]} is not +0x{other:02X} = {new[other]}")
    seen = bytearray(new)
    seen[R.POSITION] = new[A.CLUB_POSITION]     # 3431 ran while +6 = +7 (970A); 7F36 came later
    must, clear = c["tactics"][1](seen)
    if new[R.TACTICS] & must != must or new[R.TACTICS] & clear:
        err.append(f"+0x0F = {new[R.TACTICS]:02x}: 3431 sets {must:02x} and clears {clear:02x}")
    if new[A.ABILITY] != A.compute_ability(new[A.AGE], new[A.PEAK], new[A.RATING]):
        err.append(f"+0x04 = {new[A.ABILITY]:02x} is not compute_ability of its own +1/+2/+3")
    ini = bytes.fromhex(name_new[1])
    if len(ini) != 1 or ini[0] not in c["initial"]:
        err.append(f"the initial {name_new[1]} is not one of DS:0C38's letters")
    if name_new[0] != name_old[0]:
        err.append(f"the surname changed {name_old[0]} -> {name_new[0]} (7E80 writes only the initial)")
    return err


def classify(rec, new, name_old, name_new):
    """('continuing' | 'recreate' | None, the reasons when None) for one word."""
    caps_lo = C.caps_word(rec)
    fire_lo = A.ageing_value(C.with_caps(rec, max(caps_lo, 1)), 0, None, None, 0)["retires"]
    fire_zero = A.ageing_value(C.with_caps(rec, 0), 0, None, None, 0)["retires"]
    decided = caps_lo > 0 or fire_lo == fire_zero
    cont = C.continuing_errors(rec, new, name_old, name_new)
    repl = replacement_errors(rec, new, name_old, name_new)
    if decided and not fire_lo:
        return ("continuing", []) if not cont else (None, ["retirement cannot fire, but: "
                                                           + "; ".join(cont)])
    if decided:
        return ("recreate", []) if not repl else (None, ["retirement fires, but not a re-create: "
                                                         + "; ".join(repl)])
    if not cont:
        if C.caps_word(new) == 0:
            return None, [f"continued with caps 0 at aged age {(rec[A.AGE] + 1) & 0xFF}: "
                          f"retirement fires"]
        return "continuing", []
    if not repl:
        return "recreate", []
    return None, [f"neither continuing ({'; '.join(cont)}) nor a re-create ({'; '.join(repl)})"]


def exact_seeds(seq):
    """The RNG words at 80DA's entry from which 7E80, applied to `seq` in order, reproduces
    every drawn byte and initial. seq: [(retiree aged, new record, initial byte)]."""
    hits = []
    for w0 in range(SEEDS):
        w, ok = w0, True
        for inst, new, ini in seq:
            got, gi, w = R.recreate(inst, new[A.RATING] - R.RATING_OFFSET, w)
            if gi != ini or any(got[o] != new[o] for o in DRAWN):
                ok = False
                break
        if ok:
            hits.append(w0)
    return hits


def check_pair(before, after, mismatches, notes, label=""):
    """(comparisons, re-creates matched, re-creates checked exactly) of one capture pair."""
    when = f"{label}{before.get('when')} -> {after.get('when')}"
    sb, sa = before["state"]["stage"], after["state"]["stage"]
    if C.ageings_between(sb, sa) != 1:
        mismatches.append(f"{when}: stage {sb} -> {sa} spans {C.ageings_between(sb, sa)} ageings, not 1")
    if before["tables"] != after["tables"]:
        mismatches.append(f"tables DS:6D25/DS:6DCD differ between the captures ({when})")
    nb = [c["n"] for c in before["countries"]]
    na = [c["n"] for c in after["countries"]]
    for side, ns in (("first", nb), ("second", na)):
        if len(ns) != C.COUNTRIES or len(set(ns)) != len(ns):
            mismatches.append(f"{when}: the {side} capture holds countries {ns}, "
                              f"not {C.COUNTRIES} distinct ones")
            return 0, 0, 0
    if nb != na:
        mismatches.append(f"{when}: the captured countries differ: {nb} -> {na}")
        return 0, 0, 0
    after_by_n = {c["n"]: c for c in after["countries"]}
    n, matched, seq = 0, 0, []
    for cb in sorted(before["countries"], key=lambda c: c["n"]):
        b = C.squad_map(cb, before.get("when"), mismatches)
        ca = after_by_n[cb["n"]]
        a = C.squad_map(ca, after.get("when"), mismatches)
        ratings, made = {}, []
        for w in sorted(b):
            n += 1
            rec, sur, ini = b[w]
            tag = f"country {cb['n']} player {w} ({when})"
            if w not in a:
                mismatches.append(f"{tag}: no record in the second capture")
                continue
            new, sur2, ini2 = a[w]
            kind, why = classify(rec, new, (sur, ini), (sur2, ini2))
            if kind is None:
                mismatches.append(f"{tag}: {'; '.join(why)} (rec {rec.hex()} -> {new.hex()})")
            elif kind == "recreate":
                matched += 1
                ratings.setdefault(new[A.RATING], []).append(w)
                made.append(w)
        if len(ratings) > 1:
            mismatches.append(f"country {cb['n']} ({when}): re-creates of one 7FDF call carry "
                              f"different +3 (country_rating + 0x7F): {ratings}")
        slot = {w: i for i, w in enumerate(ca.get("squad", []), 1)}
        for w in sorted(made, key=lambda x: slot.get(x, 99)):
            seq.append((A.aged_record(b[w][0]), a[w][0], bytes.fromhex(a[w][2])[0]))
    exact = 0
    if not seq:
        notes.append(f"{when}: no re-create in the pair")
    elif sorted(nb) != list(range(1, len(nb) + 1)):
        notes.append(f"{when}: countries {nb} are not 1..{len(nb)}: the exact check needs the "
                     f"first countries of 80DA's order; ranges only")
    else:
        hits = exact_seeds(seq)
        if not hits:
            mismatches.append(f"{when}: no RNG word at 80DA's entry reproduces the pair's "
                              f"{len(seq)} re-creates")
        else:
            exact = len(seq)
            notes.append(f"{when}: {len(seq)} re-creates reproduced exactly from the RNG word "
                         f"{', '.join(f'{h:#06x}' for h in hits[:4])} at 80DA's entry "
                         f"({len(hits)} of {SEEDS} words do)")
    return n, matched, exact


def check_runs(runs_by_dir):
    """(comparisons, mismatches, pairs, re-creates, exact, notes) over the record files."""
    total, mismatches, pairs, made, exact, notes = 0, [], 0, 0, 0, []
    if not any(runs_by_dir.values()):
        mismatches.append("no record found in any of the runs directories")
    for label, paths in runs_by_dir.items():
        if not paths:
            notes.append(f"{label}: no record")
        for p in paths:
            record = json.loads(Path(p).read_text())
            caps = C.captures(record)
            status = record.get("status", "")
            if len(caps) < 2:
                if status == "completed":
                    mismatches.append(f"{Path(p).name}: completed with {len(caps)} capture(s), no pair")
                else:
                    notes.append(f"{Path(p).name}: {len(caps)} capture(s), no pair ({status[:60]})")
            for i, (before, after) in enumerate(zip(caps, caps[1:])):
                pairs += 1
                k, m, e = check_pair(before, after, mismatches, notes,
                                     f"{Path(p).stem} captures {i}-{i + 1}: ")
                total, made, exact = total + k, made + m, exact + e
    if total == 0:
        mismatches.append("no comparison was made: nothing corroborated")
    elif made == 0:
        mismatches.append("no re-create was compared")
    return total, mismatches, pairs, made, exact, notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default="runs/E014,runs/E016",
                    help="comma-separated runs directories (default: runs/E014,runs/E016)")
    a = ap.parse_args(argv)
    runs_by_dir = {}
    for d in a.runs.split(","):
        path = Path(d.strip())
        if not path.is_absolute():
            path = ROOT / path
        runs_by_dir[d.strip()] = sorted(path.glob("E0*-r*.json"))
    total, mismatches, pairs, made, exact, notes = check_runs(runs_by_dir)
    for off, why in sorted(R.NOT_IN_CAPTURES.items()):
        print(f"not in captures: +0x{off:02X}: {why}")
    for m in notes:
        print("note:", m)
    for m in mismatches:
        print("MISMATCH:", m)
    print(f"comparisons: {total} squad words across {pairs} consecutive pair(s) of "
          f"{sum(len(v) for v in runs_by_dir.values())} record(s); {len(mismatches)} mismatch(es)")
    print(f"re-creates: {made}, of which {exact} reproduced exactly from a recovered RNG word")
    ok = not mismatches and made > 0
    print(f"match: {made if ok else max(made - len(mismatches), 0)}/{made}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
