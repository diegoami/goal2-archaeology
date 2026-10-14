"""E024: which computer-tactics branches (0791:C173 and its tree) the ten E010 quick-engine records reach.

    python3 -B experiments/E024-computer-managers/tally_tactics.py

Replays the second half of each E010 record with the seed-exact model (runtime/model/quick_engine.py,
`simulate`, F012: 10 of 10 exact, re-checked below by the score and the two seed words) from its
half-time savestate, and counts, by wrapping the model's own methods in this process (no source file
is edited, nothing is written to the guest), every call of:

  c173      per team and per branch of seg_0791_19.asm:997-1110 (managed skip; |d| < 2 -> BD83;
            |d| = 2 -> BF6B, ahead or behind; |d| > 2 ahead -> C0DF, behind -> C01A)
  bd83      the sub-branches (a) `t = 1, DS:80FC set, team 1 stronger` and (b) `own eleven stronger`
  c0df/c01a the once-per-stretch flag (DS:8334 / DS:8332) already set (return) or not (the 5 draws),
            and C01A's tail (the player in squad slot 9 has position 12 or 13: no back-four step;
            otherwise BEC7 + 230C)

What this cannot count: the match-start call of A3DE (B11F, 34E7, BD83) happens before the half-time
savestate, so only the second half is replayed. The result is the model's decisions, which equal the
original's wherever the model is seed-exact (checked on every record); it is not a hook on the guest.
The log goes to a new file out/tally-<UTC time>.log (never overwritten) and is echoed.
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
import quick_engine  # noqa: E402
import savestate  # noqa: E402

QM = quick_engine.QuickMatch
cnt = Counter()


def wrap(name, before=None):
    orig = getattr(QM, name)

    def inner(self, *a, **k):
        if before:
            before(self, *a, **k)
        return orig(self, *a, **k)
    setattr(QM, name, inner)


def pre_c173(self):
    d = quick_engine.s8((self.score[0] - self.score[1]) & 0xFF)
    ad = abs(d)
    cnt["c173 calls"] += 1
    for t in (0, 1):
        if self._country(self.teams[t])["managed"] > 0x80:
            cnt["c173 team skipped (managed)"] += 1
            continue
        ahead = self.score[t] > self.score[1 - t]
        if ad < 2:
            cnt["c173 |d|<2 -> BD83"] += 1
        elif ad == 2:
            cnt["c173 |d|=2 -> BF6B, team " + ("ahead (exclude)" if ahead else "behind (include)")] += 1
        elif ahead:
            cnt["c173 |d|>2 ahead -> C0DF"] += 1
        else:
            cnt["c173 |d|>2 behind -> C01A"] += 1


def pre_bd83(self, t):
    cnt["bd83 calls"] += 1
    if t == 1 and self.flag80fc and self.team_stronger(t):
        cnt["bd83 (a) t=1, DS:80FC set, team 1 stronger: element 1 included"] += 1
    if self.team_stronger(t):
        cnt["bd83 (b) own eleven stronger: rand(6) twice"] += 1
    else:
        cnt["bd83 own eleven not stronger: default only"] += 1


def pre_c0df(self, t):
    cnt["c0df " + ("flag DS:8334 already set: return" if self.once_8334[t] else "first time: 5 exclusions + element 6")] += 1


def pre_c01a(self, t):
    if self.once_8332[t]:
        cnt["c01a flag DS:8332 already set: return"] += 1
        return
    cnt["c01a first time: 5 inclusions + element 6"] += 1
    w = self._country(self.teams[t])["squad"][8]
    cnt["c01a tail: squad slot 9 position " + ("12/13: no back-four step" if self._player(w)[6] in {12, 13}
                                              else "other: BEC7 + 230C")] += 1


wrap("c173", pre_c173)
wrap("bd83", pre_bd83)
wrap("c0df", pre_c0df)
wrap("c01a", pre_c01a)
wrap("bf6b")

lines = []


def out(s):
    lines.append(s)
    print(s)


records = sorted((ROOT / "runs/E010").glob("E010-r*.json"))
good = 0
for p in records:
    record = json.loads(p.read_text())
    entry = next(o for o in record["outputs"] if o["name"].endswith("-halftime.sav"))
    state = savestate.Savestate(check_model.halftime_sav(entry))
    before = Counter(cnt)
    result = quick_engine.simulate(state)
    o_score, o_goals, o_seeds = check_model.originals(record)
    ok = (tuple(result["score"]) == o_score and result["seed_DS7B62"] == o_seeds["7B62"]
          and result["seed_DS8336"] == o_seeds["8336"])
    good += ok
    delta = {k: v - before.get(k, 0) for k, v in cnt.items() if v - before.get(k, 0)}
    out(f"{record['run_id']}: model {'= original' if ok else 'DIFFERS from original'} (score {tuple(result['score'])}); "
        f"half-time score from the state not stated; branches this record: {json.dumps(delta, sort_keys=True)}")
out(f"records exact: {good}/{len(records)}")
out("TOTAL over all records:")
for k in sorted(cnt):
    out(f"  {cnt[k]:4d}  {k}")
d = HERE / "out"
d.mkdir(exist_ok=True)
fn = d / f"tally-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
fn.write_text("\n".join(lines) + "\n")
print("log:", fn)
sys.exit(0 if good == len(records) else 1)
