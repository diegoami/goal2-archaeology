"""E024: the goal distribution of a silent computer-v-computer result (0791:D47E) on real line sums.

    python3 -B experiments/E024-computer-managers/sample_silent.py [N [fresh]]

`fresh` first sets energy := fitness (+0xE := +0xD) for every non-injured player of the two squads, a proxy for
the start of a fixture (0791:CB7D, F018) instead of the half-time energies the savestates hold.

D47E (seg_0791_21.asm:489-560) computes 0BC4 for both sides, then calls B19D(12) ONCE and takes its
two counts as the score (a tie in a competition code of the set at DS:693A adds B19D(4) and a coin,
not modelled here: friendlies are not in that set). This script takes the ten E010 half-time
savestates (the two teams of each record, with the lineups and conditions they hold there),
builds the model's line sums and calls the model's own `roll_quick_goals(12)` with N seeds per
record (seeds 1..N, a fresh LCG each), and prints per record and in all: mean goals per team, per
match, and the 0/1/2/3/4+ distribution of the match total.

It is a sample of the MODEL of B19D (seed-exact on the ten records for D733, F012), on states that
are half-time states of friendlies, not the line sums two computer countries would have at the
start of a fixture (everyone fresh); it answers whether the single-call count has the quick
engine's mean (1.32) or the watched engine's (1.98), not the exact silent mean of a competition.
Log: a new file out/silent-<UTC time>.log (never overwritten) and echoed.
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "runtime/driver"))
sys.path.insert(0, str(ROOT / "runtime/model"))
sys.path.insert(0, str(ROOT / "experiments/E010-q010-quick-engine"))
import check_model  # noqa: E402
import players  # noqa: E402
import quick_engine  # noqa: E402
import savestate  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
FRESH = len(sys.argv) > 2 and sys.argv[2] == "fresh"      # energy := fitness for non-injured players (see below)
lines = []


def out(s):
    lines.append(s)
    print(s, flush=True)


tot = Counter()
sum_team = [0, 0]
n_all = 0
for p in sorted((ROOT / "runs/E010").glob("E010-r*.json")):
    record = json.loads(p.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    state = savestate.Savestate(check_model.halftime_sav(entry))
    if FRESH:
        # a proxy for the start of a fixture: every non-injured player of the two squads gets energy := fitness
        # (+0xE := +0xD; 0791:CB7D does this before a played match, F018); injured (+0xE <= 0) stay as they are
        pa = players.far_pointer(state, players.PLAYERS_PTR)[2]
        ca = players.far_pointer(state, players.COUNTRIES_PTR)[2]
        mem = bytearray(state.mem)
        for team in (0, 1):
            cc = state.ds_word(0x9B34 + 2 * team)
            sqb = mem[savestate.MEM_BASE + ca + 0xBF * cc:savestate.MEM_BASE + ca + 0xBF * cc + 40]
            for i in range(20):
                w = int.from_bytes(sqb[2 * i:2 * i + 2], "little")
                b = savestate.MEM_BASE + pa + 20 * w
                if mem[b + 0xE] != 0 and mem[b + 0xE] < 128:
                    mem[b + 0xE] = mem[b + 0xD]
        state.mem = mem
    m = quick_engine.QuickMatch(state)
    dist = Counter()
    team = [0, 0]
    for seed in range(1, N + 1):
        m.rng = quick_engine.LCG(seed)
        f = m.roll_quick_goals(12)
        team[0] += f[0]
        team[1] += f[1]
        dist[min(f[0] + f[1], 4)] += 1
    sums = [m.line_sums(0, 0, m.teams[0]), m.line_sums(m.flag80fc, 1, m.teams[1])]
    out(f"{record['run_id']}: teams {m.teams} flag80fc {m.flag80fc} sums[gk,def,mid,att] {sums} "
        f"mean goals side0 {team[0] / N:.3f} side1 {team[1] / N:.3f} total {(team[0] + team[1]) / N:.3f} "
        f"dist 0/1/2/3/4+ {[dist[i] for i in range(5)]}")
    tot.update(dist)
    sum_team[0] += team[0]
    sum_team[1] += team[1]
    n_all += N
out(f"ALL {n_all} samples: mean goals per match {(sum_team[0] + sum_team[1]) / n_all:.3f} "
    f"(side0 {sum_team[0] / n_all:.3f}, side1 {sum_team[1] / n_all:.3f}); "
    f"dist 0/1/2/3/4+ per cent {[round(100 * tot[i] / n_all, 1) for i in range(5)]}")
out("reference: quick engine 1.32 (C-MATCH-27: 20/39/30/11/0 per 100), watched 1.98 (14/27/20/30/9)")
d = HERE / "out"
d.mkdir(exist_ok=True)
fn = d / f"silent-{'fresh' if FRESH else 'asis'}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines) + "\n")
print("log:", fn)
