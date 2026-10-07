# F016 Skills rise into a four-age peak band and fall after it — the yearly loop writes only +1/+4/+0x11, deterministically; the peak age never moves after creation

- **Status**: proposed
- **Question**: How do skills change with age, and what is a player's peak age? (Q013, Q04.1,
  Q04.2, `docs/backlog.md`; T28)
- **Tests claims**: F008's inference that +2 is the peak age (the loop reads it every year and
  never writes it — the inference is now derived from the ageing path itself); F008's byte map
  (+1 age, +4 ability); F015's derivation (one input, +4, changes, so all twelve skills scale
  together); the backlog's hypothesis ("skills rise each year to a peak age that differs between
  players and fall afterwards", GOAL.HLP 327-332) — corroborated with the exact rule: the peak
  is a band of four ages, not one year.
- **Experiment and runs**: E014 (`experiments/E014-q013-ageing/`): auto-played years from E006's
  published main-screen start state of a new game, capturing at every year end (the settling on
  entry to a stage in {2,3,5,7}) the player records of the first 3 computer countries, both
  derivation tables and the state bytes from one savestate per capture. Runs
  `runs/E014/E014-r00{01..06}.json`; the corroborating pairs are checked by
  `experiments/E014-q013-ageing/check_ageing.py`.
- **Artifact**: set `goal2-67cf27d6`, variant none (E006's published start state, adopted).
- **Max intervention**: I1 (memory read from savestates) and I2 (savestates written at every
  read and staged as start states). No memory edit.
- **Tier reached**: V1 (a read-only rule from the listing, corroborated on the recorded years).
- **Confidence**: unreviewed (status `proposed`). Static: every rule is read from
  `static/goal-exe/` (the named view first, then `code/` and `decompiled/`), with `calls.tsv`
  closing the callee sets; claim-by-claim citations in `experiments/E014-q013-ageing/notes.md`.
  Behavioural: the E014 records' consecutive capture pairs, `match: N/N` by `check_ageing.py`
  (the PR body carries the run).

## Answer

- **When**: the players age once per displayed year, at the year-end settling — `000E:70B9`
  (play_round) calls `1771:8208` when a stage's fixtures are exhausted; `8208` wraps the stage
  byte `[A923]+0x3C` +1 into [2,8] (`214B:1D6F`, seg_1771_12.asm:143-155) and calls the ageing
  `1771:80DA` only when the NEW stage is in the set `CS:81E8` = 0xAC = {2, 3, 5, 7}
  (seg_1771_12.asm:118, :156-163). One 4-year cycle = stages 2..8 = four ageings; the year word
  `+0x38` increments only for the set {2, 5} (`CS:80BA` = 0x24, seg_1771_11.asm:1115).
- **Who**: `1771:80DA` loops the 128 countries (seg_1771_12.asm:17-30); `1771:7FDF` per country
  ages the 20 squad players (`7FB1` → `7E4A`), and for a MANAGED country also the manager's 80
  pool players (`DS:6D18[+0x2E − 0x80]`, indices `[A927]`, :1050-1085); a COMPUTER country then
  runs the retirement test `1771:7F40` per squad player (:1086-1099) and re-creates retirees
  `1771:7E80` (Q014's territory).
- **The yearly writes on a continuing player are exactly {+1, +4, +0x11}**: +1 (age) incremented
  by `7E6F` (`inc byte ptr es:[di + 1]`, seg_1771_11.asm:861, wrapping at 255), +4 (ability)
  written only by `compute_ability` `1771:32EB` (seg_1771_05.asm:312/366), +0x11 cleared
  unconditionally by `7FD4` (:1015 — the byte's only writer in the whole program, and no reader).
  **+2 (peak), +3 (rating), +5, +6, +7 never move in the yearly loop** (+2's only writer is
  `roll_peak_age` `1771:3291`, called only from `make_player` `1771:96D3` — creation, calls.tsv);
  so the task's "+5 profile / +7 club position?" is answered: untouched. The engines' derived
  skills (`1771:3A06`, F015) therefore change by the +4 ratio alone: all twelve skills scale by
  (new +4 + 1)/(old +4 + 1) under the integer division.
- **The peak-age rule** (`compute_ability` `1771:32EB`, seg_1771_05.asm:283-370; a = +1, p = +2,
  r = +3): inside the band `p ≤ a ≤ p + 3` the ability is the ceiling **r** (:296-312); above it
  k = a − (p + 3) (:337-347); below it k = (p − a) div 2 signed (:348-361); then
  `+4 = ((r · (16 − k)) mod 65536) div 16` (:362-366, the high product discarded at `33B9`).
  So a player's skill **rises by r/16 per two years before the band, sits at r for the four ages
  p..p+3, and falls by r/16 per year after it** — the peak is a four-age band, and it differs
  between players only through the creation draw: `roll_peak_age` draws
  `+2 = DS:0E80[gk] + rand(3) − rand(3)` (25..29 outfield, 28..32 goalkeeper,
  `DS:0E80 = 1B 1E`, data/ds_2581_01.hex:123).
- **No randomness in the yearly path** (the hazard's "differ by year" wording): `calls.tsv`
  shows `8208/80DA/7FDF/7FB1/7E4A/32EB/7F40` call no RNG routine; the ageing of a continuing
  player is a pure function of its record. The variance between players is the creation draw of
  +2/+3, which the model reproduces from the records' own bytes (check_ageing's
  `observed_variance` histogram: the recorded years' +4 deltas are 0 inside the band and
  ±r/16-shaped steps outside it).
- **Retirement (context, Q014)**: for computer countries `1771:7F40` retires when
  `(DS:110E[gk] < a AND caps word +8 == 0) OR a > p + 5` (30 outfield / 33 goalkeeper,
  `DS:110E = 1E 21`, data/ds_2581_01.hex:143) — deterministic; the re-create `7E80` is all RNG
  and is not predicted (the model flags such players `retires`).

## Method

Static first (rule 22): the loop, its gate, the write set and the peak rule were all read from
`static/goal-exe/` — the named view, then `code/` and `decompiled/` — with `calls.tsv` closing
every callee set (the RNG-absence claim and +2's writer set rest on it); no run was needed to
find the loop or the rule. What static analysis could not give: the confirmation that the real
game's year end agrees byte-for-byte with the read rule over the recorded countries — the four
previous stalled rounds and the pre-match stall (below) meant no corroborated pair existed until
E014-r0005. The runs corroborate: each consecutive capture pair of every E014 record is compared
against `runtime/model/ageing.py` by `check_ageing.py` (`match: N/N`), including the untouched
bytes +2/+3/+5/+6/+7, the tables' constancy (F008's hazard), the retirement predicate (every
replaced player flagged, no unflagged player replaced) and the replacements' `7E80` marks. Every
match of every corroborating year ran through the R quick-result path (the captain screen's
Enter+r, F005's quick engine; all other fixtures refused at `0791:E80D` and simulated) — the
ageing runs in the stage settling, which that path still traverses (notes.md §8); the stage
transitions and settling screen occurred at every recorded year end.

Two run-side discoveries, both read statically after the runs exposed them (notes.md §7): the
pre-match team screen `0791:ED8A` silently refuses ` play ` while `0791:EA09` returns 0 (one
ineligible player among the first eleven — the r0002-r0004 stalls), and the recovery is the
assistant's recommended 20 (`0791:DC7E`, the Ins key of the SELECT TEAM screen, GOAL.HLP P58).
Both are annotation rows now.
