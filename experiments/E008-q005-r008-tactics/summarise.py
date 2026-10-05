#!/usr/bin/env python3
"""E008 (T19, Q005): the continental order of the rating, the readers of country +0x2D and player +0xF,
and the quick-result arms.

    python3 experiments/E008-q005-r008-tactics/summarise.py [--goal-dat .cache/goal2/GOAL.DAT]

1. The rating `1771:10E7` per country (F007) from GOAL.DAT alone: `1771:9A40` sets +0x2B to the
   country's position in block 8 (DS:9BFD + k, k = 1..128), and +0x2C = (i - 1) div 32 + 1, +0x2A =
   (i - 1) mod 32 + 1 from its position i in block 9 (DS:9C7E + i) (seg_1771_06.c:85-99). Per
   continent (+0x2C): mean, minimum and maximum, next to E006's measured mean of player field +3
   minus 0x7F over the continent's squad players (runs/E006, the first completed record: F007 found
   all 12 identical).
2. The static reader table (readers.py).
3. If runs/E008 exists: per start state and arm, the score bytes DS:9B3C/DS:9B3D and the seed words.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(HERE))
import players as P  # noqa: E402
import readers  # noqa: E402

BLOCKS = ROOT / "static" / "goal-dat" / "blocks.tsv"
# DS:690A.. (static/goal-exe/strings.tsv): EUROPEAN, AMERICAN, AFRICAN, ASIAN; GOAL.HLP 166-170
# numbers the continents 1 Europe, 2 America, 3 Africa, 4 Asia.
CONTINENTS = {1: "Europe", 2: "America", 3: "Africa", 4: "Asia"}
HELP_ORDER = [1, 2, 3, 4]  # GOAL.HLP 171-173: Europe > America > Africa > Asia
RATING_OFFSET = 0x7F  # F007: field +3 = rating + 0x7F for squad players (1771:96D3, flag 1)


def blocks(path=BLOCKS):
    out = {}
    for line in Path(path).read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1].startswith("0x"):
            out[parts[0]] = int(parts[1], 16)
    return out


def ranks(dat, path=BLOCKS):
    """{country: (+0x2A, +0x2B, +0x2C)} as 1771:9A40 sets them from blocks 8 and 9."""
    b = blocks(path)
    o8, o9 = b["per_country_b"], b["per_country_c"]
    world, cont = {}, {}
    for k in range(1, P.SQUAD_COUNTRIES + 1):
        world[dat[o8 + k]] = k
        c = dat[o9 + k]
        cont[c] = ((k - 1) % 32 + 1, (k - 1) // 32 + 1)
    if sorted(world) != list(range(1, P.SQUAD_COUNTRIES + 1)) or sorted(cont) != sorted(world):
        raise ValueError("blocks 8 and 9 are not each a permutation of countries 1..128")
    return {c: (cont[c][0], world[c], cont[c][1]) for c in world}


def rating(r2a, r2b, r2c):
    """1771:10E7 (F007): ((5 - [+2C]) * (0x21 - [+2A]) + (0x81 - [+2B])) idiv 2 (all positive here)."""
    return ((5 - r2c) * (0x21 - r2a) + (0x81 - r2b)) // 2


def e006_plus3(runs=ROOT / "runs" / "E006"):
    """(run id, {country: mean of player field +3 over its squad players 1..2560}) from E006's first completed record."""
    for path in sorted(Path(runs).glob("E006-r*.json")):
        r = json.loads(path.read_text())
        if r["status"] != "completed":
            continue
        arr = next(bytes.fromhex(o["value"]) for o in r["observations"] if o.get("field", "").startswith("player array:"))
        sums = {}
        for p in range(1, P.SQUAD * P.SQUAD_COUNTRIES + 1):
            rec = arr[p * P.PLAYER_SIZE:(p + 1) * P.PLAYER_SIZE]
            sums.setdefault(rec[0], []).append(rec[3])
        return r["run_id"], {c: sum(v) / len(v) for c, v in sums.items()}
    return None, {}


def continent_table(dat):
    rk = ranks(dat)
    rat = {c: rating(*rk[c]) for c in rk}
    run, plus3 = e006_plus3()
    rows = []
    for k, name in CONTINENTS.items():
        cs = [c for c in rk if rk[c][2] == k]
        v = [rat[c] for c in cs]
        m = [plus3[c] - RATING_OFFSET for c in cs if c in plus3]
        rows.append({"continent": k, "name": name, "n": len(cs), "mean": sum(v) / len(v), "min": min(v), "max": max(v),
                     "e006_mean": sum(m) / len(m) if m else None})
    return rows, run


def order_holds(rows):
    means = {r["continent"]: r["mean"] for r in rows}
    return all(means[a] > means[b] for a, b in zip(HELP_ORDER, HELP_ORDER[1:]))


def runs_table(runs=ROOT / "runs" / "E008"):
    out = []
    for path in sorted(Path(runs).glob("E008-r*.json")):
        r = json.loads(path.read_text())
        row = {"run": r["run_id"], "state": r["start_state"]["id"], "arm": r["arm"], "status": r["status"]}
        for o in r["observations"]:
            f = o.get("field", "")
            for key in ("full time: score", "full time: seed", "edit:"):
                if f.startswith(key):
                    row[key] = o["value"]
        out.append(row)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--goal-dat", default=str(ROOT / ".cache" / "goal2" / "GOAL.DAT"))
    a = ap.parse_args(argv)
    dat = Path(a.goal_dat).read_bytes()
    rows, run = continent_table(dat)
    print("1. Rating 1771:10E7 per continent, from GOAL.DAT blocks 8 and 9 (128 countries),"
          f" next to E006's measured mean of field +3 minus 0x7F ({run})")
    print(f"{'continent':<12}{'n':>4}{'mean':>9}{'min':>6}{'max':>6}{'E006 +3-7F':>12}")
    for r in rows:
        e = f"{r['e006_mean']:.3f}" if r["e006_mean"] is not None else "-"
        print(f"{r['continent']} {r['name']:<10}{r['n']:>4}{r['mean']:>9.3f}{r['min']:>6}{r['max']:>6}{e:>12}")
    print(f"help file order Europe > America > Africa > Asia holds for the means: {order_holds(rows)}")
    print()
    print("2. Routines that access country +0x2D or player +0xF (listing filter, readers.py), reached from the engines' direct calls")
    for r, inw, inq, where in readers.table():
        print(f"{r}  watched 0791:9564: {'yes' if inw else 'no ':<3}  quick 0791:D733: {'yes' if inq else 'no ':<3}  {where}")
    print()
    rt = runs_table()
    if rt:
        print("3. Quick results per start state and arm: score bytes DS:9B3C, DS:9B3D and seed words")
        for r in rt:
            print(f"{r['run']} {r['state']} {r['arm']:<10} {r['status']:<10} edit: {r.get('edit:', '-')} | score: {r.get('full time: score', '-')} | seed: {r.get('full time: seed', '-')}")
    else:
        print("3. No runs under runs/E008.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
