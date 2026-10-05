#!/usr/bin/env python3
"""E009 (T22, Q007): check the pool screen and the pool data against the static claims of F011.

    python3 experiments/E009-q007-squad-pool/summarise.py

Reads the records of runs/E009 and checks, per record:
  - DS:A927 (the pool index array): word 0 is 0, words 1..80 are exactly the set 2561..2640 (the 80
    pool records the managed country's 1771:98C4 makes), words 81..480 are 0;
  - DS:6D18 (the per-manager base table): words 1..6 are 1, 81, 161, 241, 321, 401;
  - the 80 pool records 2561..2640 hold the managed country (Denmark, 7) in byte 0, and the two
    records just past the pool (2641, 2642) are all zero;
  - the pool view's list shows the names of DS:A927[1..20] (the first 20 of the position-sorted pool),
    i.e. the names 1771:2E93 builds for records 2561..2640;
  - the squad view's list shows the names of the managed country's 20 squad records (121..140, Denmark).
Each line prints what was found; anything that contradicts a claim prints a FAIL line and the run
exits 1."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import players  # noqa: E402

RUNS = ROOT / "runs" / "E009"
N_POOL = 80
POOL_FIRST = 0xA00
DENMARK = 7  # the managed country of E006-r0001 (F007); its squad is records 121..140


def obs(record, field_prefix):
    return [o for o in record["observations"] if o.get("field", "").startswith(field_prefix)]


def words_obs(record):
    for o in record["observations"]:
        if "DS:A927 (the pool index array" in o.get("field", ""):
            return json.loads(o["value"])
    raise SystemExit("no DS:A927 observation in the record")


def base_obs(record):
    for o in record["observations"]:
        if "the per-manager pool base table" in o.get("field", ""):
            raw = bytes.fromhex(o["value"])
            return [int.from_bytes(raw[2 * i:2 * i + 2], "little") for i in range(len(raw) // 2)]
    raise SystemExit("no DS:6D18 observation in the record")


def names_obs(record):
    surnames = initials = None
    for o in record["observations"]:
        if "bytes of surnames" in o.get("field", ""):
            surnames = bytes.fromhex(o["value"])
        if "bytes of initials" in o.get("field", ""):
            initials = bytes.fromhex(o["value"])
    if surnames is None or initials is None:
        raise SystemExit("no name-array observation in the record")
    return surnames, initials


def records_obs(record):
    out = {}
    for o in record["observations"]:
        f = o.get("field", "")
        if "bytes of player record " in f:
            n = int(f.split("record ")[1].split(" ")[0])
            out[n] = bytes.fromhex(o["value"])
    return out


def screen_text(record, prefix):
    for o in record["observations"]:
        if o.get("field", "").startswith(prefix) and "text screen rows" in o.get("field", ""):
            return o["value"]
    raise SystemExit(f"no {prefix} screen observation in the record")


def screen_has(text, names):
    return all(n in text for n in names)


def pool_ok(words):
    """DS:A927[0] is 0, DS:A927[1..80] is exactly the set 2561..2640, DS:A927[81..480] all 0."""
    pool = words[1:N_POOL + 1]
    return (words[0] == 0 and sorted(pool) == list(range(POOL_FIRST + 1, POOL_FIRST + N_POOL + 1))
            and all(w == 0 for w in words[N_POOL + 1:]))


def base_ok(base):
    """DS:6D18 words 1..6 are the six managers' bases 1, 81, 161, 241, 321, 401 (80*(m-1)+1)."""
    return base[1:7] == [1, 81, 161, 241, 321, 401]


def pool_records_ok(recs20):
    """The 80 pool records hold country 7 (Denmark) in byte 0; records 2641, 2642 are all zero."""
    countries = [recs20.get(n, b"")[0] if len(recs20.get(n, b"")) else None
                 for n in range(POOL_FIRST + 1, POOL_FIRST + N_POOL + 1)]
    ok_country = all(c == DENMARK for c in countries)
    past = [recs20.get(n, b"") for n in (POOL_FIRST + N_POOL + 1, POOL_FIRST + N_POOL + 2)]
    ok_past = all(b == b"\x00" * 20 for b in past)
    return ok_country, ok_past


def positions_sorted_ok(recs20, words):
    """The pool records' position (+6) in A927 order is non-decreasing (sort_pool_by_position)."""
    nums = words[1:N_POOL + 1]
    positions = [recs20[n][6] for n in nums]
    return positions == sorted(positions)


def main():
    recs = sorted(RUNS.glob("E009-r*.json"))
    if not recs:
        print("no E009 records")
        return 1
    problems = 0
    for p in recs:
        rec = json.loads(p.read_text())
        if rec["status"] != "completed":
            print(f"{p.name}: status {rec['status']}, skipped")
            problems += 1
            continue
        words = words_obs(rec)
        base = base_obs(rec)
        surnames, initials = names_obs(rec)
        recs20 = records_obs(rec)

        # 1. the pool index array
        ok_pool = pool_ok(words)
        print(f"{p.name}: DS:A927[0]={words[0]} DS:A927[1..80] is {{2561..2640}}={ok_pool} "
              f"DS:A927[81..480] all zero={all(w == 0 for w in words[N_POOL + 1:])}")

        # 2. the base table
        ok_base = base_ok(base)
        print(f"{p.name}: DS:6D18 words 1..6 = {base[1:7]} (want 1,81,161,241,321,401)={ok_base}")

        # 3. the pool records' country byte (Denmark = 7) and the two records past the pool
        ok_country, ok_past = pool_records_ok(recs20)
        print(f"{p.name}: pool records 2561..2640 country byte = 7 = {ok_country}; "
              f"records 2641,2642 all zero = {ok_past}")

        # 3b. the pool is position-sorted
        ok_sorted = positions_sorted_ok(recs20, words)
        print(f"{p.name}: pool positions in A927 order non-decreasing = {ok_sorted}")

        # 4. the pool view lists the first 20 of the position-sorted pool
        pool_screen = screen_text(rec, "SELECT TEAM, pool view")
        pool_first20 = [players.full_name(surnames, initials, n) for n in words[1:21]]
        ok_pool_screen = screen_has(pool_screen, pool_first20)
        print(f"{p.name}: pool view lists DS:A927[1..20] names = {ok_pool_screen} "
              f"(first 3: {pool_first20[:3]})")

        # 5. the squad view lists Denmark's 20 squad records (121..140)
        squad_screen = screen_text(rec, "SELECT TEAM, squad view")
        squad_names = [players.full_name(surnames, initials, n) for n in range((DENMARK - 1) * 20 + 1, DENMARK * 20 + 1)]
        ok_squad_screen = screen_has(squad_screen, squad_names)
        print(f"{p.name}: squad view lists Denmark's 20 squad records 121..140 = {ok_squad_screen} "
              f"(first 3: {squad_names[:3]})")

        for label, ok in [("pool array", ok_pool), ("base table", ok_base), ("pool country", ok_country),
                          ("past pool zero", ok_past), ("pool sorted", ok_sorted),
                          ("pool screen", ok_pool_screen), ("squad screen", ok_squad_screen)]:
            if not ok:
                print(f"{p.name}: FAIL {label}")
                problems += 1

    print(f"{len(recs)} record(s); {problems} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
