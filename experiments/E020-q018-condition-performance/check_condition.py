#!/usr/bin/env python3
"""Compare runtime/model/condition.py with every E020 record (Done-when 1).

    python3 experiments/E020-q018-condition-performance/check_condition.py [records-dir]

Three kinds of comparison, all keyed by PLAYER WORD (or, for a half, by the edits' player words and
the seed), never by name:
  strength/1  1771:377E of a literal 20-byte record, from the original code (probe_original.py)
  contest/1   0791:278A of a literal record, from the original code
  half/1      the original's whole second half on a half-time state edited by player word
              (probe_halves.py), against the quick-engine model on the same bytes: final score,
              final main seed, number of draws
Every record under records/ is read; a duplicate player word inside one file, an unknown schema, a
record without comparisons, and an empty set all fail. A mismatch prints MISS and the run ends
non-zero. Ends with `match: N/N`."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common  # noqa: E402
from common import ROOT  # noqa: E402
sys.path.insert(0, str(ROOT))
from runtime.model import condition, quick_engine  # noqa: E402
import savestate  # noqa: E402


def check_strength(rec):
    ft, fi = bytes.fromhex(rec["foot_table_DS_0E60"]), bytes.fromhex(rec["foot_index_DS_0E7C"])
    seen, good, total = set(), 0, 0
    for c in rec["comparisons"]:
        if c["player_word"] in seen:
            raise ValueError(f"duplicate player word {c['player_word']}")
        seen.add(c["player_word"])
        got = condition.strength(c["player_word"], bytes.fromhex(c["record"]), ft, fi)
        total += 1
        good += got == c["strength"]
        if got != c["strength"]:
            print(f"MISS strength player word {c['player_word']}: model {got}, original {c['strength']}")
    return good, total


def check_contest(rec):
    ct, pt = bytes.fromhex(rec["class_table_DS_6D25"]), bytes.fromhex(rec["profile_table_DS_6DCD"])
    seen, good, total = set(), 0, 0
    for c in rec["comparisons"]:
        if c["player_word"] in seen:
            raise ValueError(f"duplicate player word {c['player_word']}")
        seen.add(c["player_word"])
        got = condition.contest(bytes.fromhex(c["record"]), c["element"], ct, pt,
                                event=c["event_code_8327"], pitch_13=c["pitch_13"],
                                pitch_11=c["pitch_11"], flag_80fc=c["flag_80fc"],
                                pitch_6=c["pitch_6"])
        total += 1
        good += got == c["contest"]
        if got != c["contest"]:
            print(f"MISS contest player word {c['player_word']}: model {got}, original {c['contest']}")
    return good, total


def check_half(rec):
    data = common.load_state()
    if rec["source_sha256"] != common.STATE_SHA256:
        raise ValueError("record names another source state")
    words = [e["player_word"] for e in rec["edits"] if "player_word" in e and e["offset"] == 0xC]
    if len(words) != len(set(words)) or not words:
        raise ValueError("the edits must set each player word's form exactly once")
    edited = common.apply_edits(data, rec["edits"])
    seen, good, total = set(), 0, 0
    for c in rec["comparisons"]:
        if c["seed"] in seen:
            raise ValueError(f"duplicate seed {c['seed']}")
        seen.add(c["seed"])
        state = savestate.Savestate(common.apply_edits(edited, [common.seed_edit(c["seed"])]))
        match = quick_engine.QuickMatch(state)
        result = match.run()
        got = (list(result["score"]), result["seed_DS7B62"], result["draws"])
        want = (c["score"], c["final_seed"], c["draws"])
        total += 1
        good += got == want
        if got != want:
            print(f"MISS half {rec['scenario']} seed {c['seed']}: model {got}, original {want}")
    return good, total


CHECKS = {"E020-strength/1": check_strength, "E020-contest/1": check_contest,
          "E020-half/1": check_half}


def main():
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "records"
    files = sorted(folder.glob("*.json"))
    good = total = 0
    for path in files:
        rec = json.loads(path.read_text())
        check = CHECKS.get(rec.get("schema"))
        if check is None:
            raise SystemExit(f"{path.name}: unknown schema {rec.get('schema')!r}")
        if not rec.get("comparisons"):
            raise SystemExit(f"{path.name}: no comparisons")
        g, t = check(rec)
        print(f"{path.name}: {g}/{t}")
        good, total = good + g, total + t
    if not total:
        raise SystemExit("no comparisons: an empty set fails")
    print(f"match: {good}/{total}")
    return int(good != total)


if __name__ == "__main__":
    raise SystemExit(main())
