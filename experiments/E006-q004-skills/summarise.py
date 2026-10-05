#!/usr/bin/env python3
"""E006 summary (T15, Q004): the player array of each new game, field by field.

    python3 experiments/E006-q004-skills/summarise.py [--runs runs/E006] [--goal-dat .cache/goal2/GOAL.DAT]

Prints, per field of the 20-byte player record: whether it differs across DOS minutes and whether it
is equal within a minute; its range over all 3061 players; for a field that varies between players, the
correlation and least-squares line of its per-country mean (squads 1..128, n = 128) against each of
R007's three bytes and R008 (GOAL.DAT blocks `per_country_3` and `per_country_a`, F002), and against the
country rating `1771:10E7` computes from the country record. Then the seed word DS:7B62 of each game as
LCG steps from its DOS hour:minute (F004), and the static model of `1771:96D3` (draws of the LCG
`214B:0688` from the seed `1771:97CC` sets to the country number) against the observed bytes of players
1..2560. Records are read, never written. Exit 1 when no completed record is found.
"""
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import players as P  # noqa: E402

BLOCKS = ROOT / "static" / "goal-dat" / "blocks.tsv"
NAMED = list(range(1, P.SQUAD * P.SQUAD_COUNTRIES + 1))   # players named by a squad: 1..2560
FIELDS = list(range(P.PLAYER_SIZE))


# ---- the records -------------------------------------------------------------------------------
def load(runs):
    games = []
    for path in sorted(Path(runs).glob("E006-r*.json")):
        r = json.loads(path.read_text())
        if r["status"] != "completed":
            continue
        g = {"run": r["run_id"], "time": r["arm"].split("-")[-1]}
        for o in r["observations"]:
            f = o.get("field", "")
            if f.startswith("player array:"):
                g["players"] = bytes.fromhex(o["value"])
            elif f.startswith("country array:"):
                g["countries"] = bytes.fromhex(o["value"])
            elif f.startswith("main screen") and "DS:7B62" in f:
                g["seed"] = int(o["value"].split()[0], 16)
            elif f.startswith("players.check"):
                g["check"] = o["value"]
        games.append(g)
    return games


def field(array, p, off):
    return array[p * P.PLAYER_SIZE + off]


# ---- GOAL.DAT: R007, R008 (F002) ---------------------------------------------------------------
def goal_dat_blocks(blocks=BLOCKS):
    out = {}
    for line in Path(blocks).read_text().splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[1].startswith("0x"):
            out[parts[0]] = (int(parts[1], 16), int(parts[2]))
    return out


def per_country(dat, blocks=BLOCKS):
    """{'R007[0]': [..129], 'R007[1]', 'R007[2]', 'R008': [..129]}, index = country number."""
    b = goal_dat_blocks(blocks)
    o3, _ = b["per_country_3"]
    oa, _ = b["per_country_a"]
    out = {f"R007[{k}]": [dat[o3 + 3 * c + k] for c in range(P.N_COUNTRIES)] for k in range(3)}
    out["R008"] = [dat[oa + c] for c in range(P.N_COUNTRIES)]
    return out


def rating(countries, c):
    """1771:10E7 (seg_1771_02.asm:10ED-113D): ((5 - [+2C]) * (0x21 - [+2A]) + (0x81 - [+2B])) idiv 2."""
    r = P.record(countries, P.COUNTRY_SIZE, c)
    return ((5 - r[0x2C]) * (0x21 - r[0x2A]) + (0x81 - r[0x2B])) // 2


# ---- statistics ---------------------------------------------------------------------------------
def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    if sxx == 0 or syy == 0:
        return None, None, None
    slope = sxy / sxx
    return sxy / math.sqrt(sxx * syy), slope, my - slope * mx


# ---- the static model of 1771:96D3 at a new game ------------------------------------------------
class LCG:
    """214B:0688 (seg_214B_01.asm:880-889): seed = seed*0x7ABD + 0x1B0F (16 bits); returns
    ((seed*n) >> 16) + 1, i.e. 1..n."""

    def __init__(self, seed):
        self.seed = seed & 0xFFFF

    def draw(self, n):
        self.seed = (self.seed * 0x7ABD + 0x1B0F) & 0xFFFF
        return ((self.seed * n) >> 16) + 1


def lcg_steps(start, target, limit=200000):
    """How many LCG steps lead from start to target (None within limit)."""
    s = start & 0xFFFF
    for i in range(limit + 1):
        if s == target:
            return i
        s = (s * 0x7ABD + 0x1B0F) & 0xFFFF
    return None


# Initialised data of GOAL.EXE (static/goal-exe/data/ds_2581_01.hex rows 0E80 and 1180), indexed by
# 1 for a goalkeeper (position byte 0) and 0 otherwise.
AGE_BASE = {0: 0x1C, 1: 0x1F}    # DS:118A, DS:118B  (field +1)
PEAK_BASE = {0: 0x1B, 1: 0x1E}   # DS:0E80, DS:0E81  (field +2)
FIT_BASE = {0: 0x10, 1: 0x0D}    # DS:0E82, DS:0E83  (field +0xD), indexed by "+1 > +2 + 4"
SET_A = {0, 1, 3, 4}             # the set constant at 1771:3411 (byte 0x1B)


def model_player(rng, country, pos, rate, flag=1, managed=False):
    """The 20 bytes 1771:96D3 (seg_1771_13.asm:96D3-97C9) writes, given the RNG state; bytes it does not
    write (+8..+0xB, +0x10, +0x11) are 0 here and are left out of the comparison."""
    r = bytearray(P.PLAYER_SIZE)
    r[0] = country
    r[7] = r[6] = pos
    r[5] = rng.draw(16)
    a = rng.draw(7)
    b = rng.draw(7)
    gk = 1 if pos == 0 else 0
    r[1] = (AGE_BASE[gk] - b + a) & 0xFF
    a = rng.draw(3)                                   # 1771:3291
    b = rng.draw(3)
    r[2] = (PEAK_BASE[gk] + b - a) & 0xFF
    if flag:
        r[3] = (rate + 0x7F) & 0xFF
    else:
        d = rng.draw(10)
        r[3] = (rate + 0x7F - 10 - d) & 0xFF
    age, peak, pot = r[1], r[2], r[3]                 # 1771:32EB
    if peak <= age <= peak + 3:
        r[4] = pot
    else:
        k = 16 - (age - (peak + 3)) if age > peak + 3 else 16 - (peak - age) // 2
        r[4] = ((pot * k) // 16) & 0xFF
    r[0xC] = rng.draw(32)
    if (r[5] - (r[3] & 1)) & 0xFF < 4:                # 1771:3431 -> 1771:2FFB, 1771:33CD
        r[0xF] |= 0x80
        r[0xF] &= ~0x08 & 0xFF
    if r[6] in SET_A:
        r[0xF] |= 0x10 | 0x01
    elif r[6] == 2:
        if r[5] < 0x0E:
            r[0xF] |= 0x10
        r[0xF] |= 0x20 | 0x02
    t = FIT_BASE[1 if age > peak + 4 else 0]          # 1771:3558
    if managed:                                       # 1771:0B77 true: [+2E] > 0x80
        a = rng.draw(t + 1)
        b = rng.draw(3 * t)
        v = t + b - a
    else:
        v = t + rng.draw(2 * t)
    v = min(v, 0x20)
    r[0xE] = v & 0xFF
    r[0xD] = max(v, 1) & 0xFF
    r[0x12:0x14] = (0x7FFF).to_bytes(2, "little")
    return bytes(r)


MODELLED = [0, 1, 2, 3, 4, 5, 6, 7, 0xC, 0xD, 0xE, 0xF, 0x12, 0x13]


def model_squads(countries, squad_bytes, last=P.SQUAD_COUNTRIES):
    """Players 1..2560 as 1771:97CC builds them: seed := country (97E6-97ED), then 96D3 for slots
    1..20 with the position byte DS:9F03 + 20*country + slot - 1. squad_bytes: GOAL.DAT block squad_20."""
    out = {}
    rng = None
    for c in range(1, last + 1):
        rng = LCG(c)
        rate = rating(countries, c)
        for slot in range(1, P.SQUAD + 1):
            out[(c - 1) * P.SQUAD + slot] = model_player(rng, c, squad_bytes[20 * c + slot - 1], rate)
    return out, rng.seed


YOUTH_AGE = {0: 0x11, 1: 0x14}   # DS:118C, DS:118D (row 1180 of ds_2581_01.hex)


def model_extra(seed, country, squad_positions, rate):
    """The 80 players 1771:98C4 (seg_1771_14.asm:9934-9A2F) makes for a managed country through 1771:9873
    (96D3 with flag 0; 1771:0B77 true): positions 0..13 four times each; one per squad slot 1..20 with
    the slot's position, then its age redrawn as DS:118C[gk] + rand(3) and +4 recomputed (1771:32EB);
    then slots 6..9 again. seed: the LCG word when 98C4 starts."""
    rng = LCG(seed)
    out = []
    for pos in range(14):
        for _ in range(4):
            out.append(model_player(rng, country, pos, rate, flag=0, managed=True))
    for slot in range(1, 21):
        r = bytearray(model_player(rng, country, squad_positions[slot - 1], rate, flag=0, managed=True))
        r[1] = (YOUTH_AGE[1 if r[7] == 0 else 0] + rng.draw(3)) & 0xFF
        age, peak, pot = r[1], r[2], r[3]
        if peak <= age <= peak + 3:
            r[4] = pot
        else:
            k = 16 - (age - (peak + 3)) if age > peak + 3 else 16 - (peak - age) // 2
            r[4] = ((pot * k) // 16) & 0xFF
        out.append(bytes(r))
    for slot in range(6, 10):
        out.append(model_player(rng, country, squad_positions[slot - 1], rate, flag=0, managed=True))
    return out


def find_extra_seed(observed, country, squad_positions, rate):
    """The seeds (0..0xFFFF) from which model_extra reproduces the observed 80 records exactly on the
    modelled bytes; the first record filters the candidates."""
    want0 = observed[0]
    hits = []
    for s in range(0x10000):
        first = model_player(LCG(s), country, 0, rate, flag=0, managed=True)
        if any(first[f] != want0[f] for f in MODELLED):
            continue
        if all(m[f] == o[f] for m, o in zip(model_extra(s, country, squad_positions, rate), observed) for f in MODELLED):
            hits.append(s)
    return hits


# ---- the report ---------------------------------------------------------------------------------
def summary(games, dat):
    lines = []
    pr = lines.append
    times = [g["time"] for g in games]
    pr(f"E006: {len(games)} completed new games; DOS minutes {', '.join(sorted(set(times)))} "
       f"({len(set(times))} distinct; repeated: {', '.join(t for t in sorted(set(times)) if times.count(t) > 1) or 'none'})")
    pr("players.check per record: " + ", ".join(f"{g['run']} {g['check']}" for g in games))
    pr("")
    pr("DS:7B62 at the main screen, as LCG steps from hour*256+minute (F004):")
    for g in games:
        hh, mm = int(g["time"][:2]), int(g["time"][2:4])
        pr(f"  {g['run']} {g['time'][:2]}:{g['time'][2:4]}  0x{g['seed']:04x}  steps {lcg_steps(hh * 256 + mm, g['seed'])}")
    pr("")
    ref = games[0]
    groups = {}
    for g in games:
        groups.setdefault(g["time"], []).append(g)
    every = range(P.N_PLAYERS)
    across = [g for g in games if g["time"] != ref["time"]]
    pr("Per field of the 20-byte record at [DS:A91B] (players 0..3060; 'named' = players 1..2560 of squads 1..128):")
    pr("  field  across minutes                    within a minute            range all 3061   range named")
    varying = []
    for f in FIELDS:
        diff_players = sorted({p for g in games for p in every if field(g["players"], p, f) != field(ref["players"], p, f)})
        diff_minutes = sorted({p for g in across for p in every if field(g["players"], p, f) != field(ref["players"], p, f)})
        within = all(field(g["players"], p, f) == field(grp[0]["players"], p, f) for grp in groups.values() for g in grp for p in every)
        vals = [field(g["players"], p, f) for g in games for p in every]
        named = [field(g["players"], p, f) for g in games for p in NAMED]
        acr = "equal in all" if not diff_minutes else f"differs: {len(diff_minutes)} players (first {diff_minutes[:4]})"
        pr(f"  +0x{f:02X}  {acr:<33} {'equal' if within else 'NOT equal':<26} {min(vals):>3}..{max(vals):<3}         {min(named):>3}..{max(named):<3}")
        if not diff_players and len(set(named)) > 1:
            varying.append(f)
    w = [int.from_bytes(g["players"][p * 20 + 0x12:p * 20 + 0x14], "little") for g in games for p in NAMED]
    pr(f"  +0x12 as a word: named players {min(w)}..{max(w)}")
    cdiff = sorted({(c, o) for g in games for c in range(P.N_COUNTRIES) for o in range(P.COUNTRY_SIZE)
                    if g["countries"][c * P.COUNTRY_SIZE + o] != ref["countries"][c * P.COUNTRY_SIZE + o]})
    pr(f"Country array at [DS:A917] (129 records of 0xBF bytes): (country, offset) pairs differing between any two games: {len(cdiff)}"
       + (f", first {cdiff[:6]}" if cdiff else ""))
    pr("")
    r = per_country(dat)
    r8 = [P.record(ref["countries"], P.COUNTRY_SIZE, c)[0x2D] for c in range(1, P.SQUAD_COUNTRIES + 1)]
    pr(f"R008 (GOAL.DAT) equals country field +0x2D for countries 1..128: {r8 == r['R008'][1:P.SQUAD_COUNTRIES + 1]}")
    preds = dict(r)
    preds["rating 10E7"] = [0] + [rating(ref["countries"], c) for c in range(1, P.SQUAD_COUNTRIES + 1)]
    pr("Per-country mean (squads 1..128, n = 128) of each field that varies between players, against R007, R008 and the rating:")
    pr("  field  " + "  ".join(f"{k:>26}" for k in preds))
    for f in varying:
        means = [sum(field(ref["players"], p, f) for p in range((c - 1) * 20 + 1, c * 20 + 1)) / 20 for c in range(1, 129)]
        cells = []
        for k, xs in preds.items():
            rr, slope, icept = pearson(xs[1:129], means)
            cells.append("r      n/a (constant)" if rr is None else f"r {rr:+.3f} y={slope:+.3f}x{icept:+.1f}")
        pr(f"  +0x{f:02X}  " + "  ".join(f"{c:>26}" for c in cells))
    pr("")
    b = goal_dat_blocks()
    so, ss = b["squad_20"]
    model, end_seed = model_squads(ref["countries"], dat[so:so + ss])
    pr("Static model of 1771:96D3 from seed = country (1771:97CC), against every game, players 1..2560:")
    for f in MODELLED:
        hits = sum(model[p][f] == field(g["players"], p, f) for g in games for p in NAMED)
        total = len(games) * len(NAMED)
        miss = sorted({p for g in games for p in NAMED if model[p][f] != field(g["players"], p, f)})
        pr(f"  +0x{f:02X}  {hits}/{total} equal" + (f"; differing players {miss[:8]}{' ...' if len(miss) > 8 else ''}" if miss else ""))
    pr("")
    pr("Players 2561..3060 (not named by a squad):")
    for g in games:
        nz = [p for p in range(P.SQUAD * P.SQUAD_COUNTRIES + 1, P.N_PLAYERS) if any(g["players"][p * 20:p * 20 + 20])]
        managed = [c for c in range(1, P.N_COUNTRIES) if P.record(g["countries"], P.COUNTRY_SIZE, c)[0x2E] > 0x80]
        pr(f"  {g['run']}: {len(nz)} non-zero records ({nz[0] if nz else '-'}..{nz[-1] if nz else '-'}), countries in byte 0 "
           f"{sorted({field(g['players'], p, 0) for p in nz})}; managed countries (+0x2E > 0x80) {managed}")
    managed = [c for c in range(1, P.N_COUNTRIES) if P.record(ref["countries"], P.COUNTRY_SIZE, c)[0x2E] > 0x80]
    for c in managed:
        nums = [p for p in range(2561, P.N_PLAYERS) if field(ref["players"], p, 0) == c]
        observed = [ref["players"][p * 20:p * 20 + 20] for p in nums]
        if len(observed) != 80:
            pr(f"  country {c}: {len(observed)} records, not the 80 of 1771:98C4; not modelled")
            continue
        seeds = find_extra_seed(observed, c, dat[so + 20 * c:so + 20 * c + 20], rating(ref["countries"], c))
        steps = [lcg_steps(end_seed, s) for s in seeds]
        pr(f"  model of 1771:98C4 for country {c} (players {nums[0]}..{nums[-1]}), modelled bytes of all 80 equal from LCG seed(s) "
           f"{[f'0x{s:04x}' for s in seeds]}; LCG steps from the word left by the last squad (country 128, 0x{end_seed:04x}): {steps}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", default=str(ROOT / "runs" / "E006"))
    ap.add_argument("--goal-dat", default=str(ROOT / ".cache" / "goal2" / "GOAL.DAT"),
                    help="the verified release copy (bash setup/goal2-runtime.sh)")
    a = ap.parse_args(argv)
    games = load(a.runs)
    if not games:
        print("no completed E006 record")
        return 1
    print(summary(games, Path(a.goal_dat).read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
