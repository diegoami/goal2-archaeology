# F016 Skills rise to a five-age maximum around the peak age and fall after it — a continuing player's yearly update writes only +1/+4/+0x11, deterministically; the peak age never moves after creation

- **Status**: proposed
- **Question**: How do skills change with age, and what is a player's peak age? (Q013, Q04.1,
  Q04.2, `docs/backlog.md`; T28)
- **Tests claims**: F008's inference that +2 is the peak age (the loop reads it every year and
  never writes it for a continuing player — the inference is now derived from the ageing path
  itself); F008's byte map (+1 age, +4 ability) and its "+0x11 not read by the screen's
  routines" (it stands for the screen; the program reads +0x11 in the top-scorer table,
  `0791:B3B7`); F015's derivation (one input, +4, changes, so all twelve skills scale together);
  the backlog's hypothesis ("skills rise each year to a peak age that differs between players
  and fall afterwards", GOAL.HLP 327-332) — corroborated with the exact rule: the maximum is a
  plateau of five ages, p−1..p+3, not one year.
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
  Behavioural: the E014 records' consecutive capture pairs, `match: 300/300` by
  `check_ageing.py`.

## Answer

- **When**: the players age once per displayed year, at the year-end settling — `000E:70B9`
  (play_round) calls `1771:8208` when a stage's fixtures are exhausted; `8208` wraps the stage
  byte `[A923]+0x3C` +1 into [2,8] (`214B:1D6F`, static:static/goal-exe/code/seg_1771_12.asm:143) and calls the ageing
  `1771:80DA` only when the NEW stage is in the set `CS:81E8` = 0xAC = {2, 3, 5, 7}
  (seg_1771_12.asm:118, :156-163). One 4-year cycle = stages 2..8 = four ageings; the year word
  `+0x38` increments only for the set {2, 5} (`CS:80BA` = 0x24, seg_1771_11.asm:1115).
- **Who, in which order**: `1771:80DA` loops the 128 countries (static:static/goal-exe/code/seg_1771_12.asm:17);
  `1771:7FDF` per country first ages all 20 squad players (`7FB1` → `7E4A`, the call at
  seg_1771_11.asm:1043), and for a MANAGED country also the manager's 80 pool players
  (`DS:6D18[+0x2E − 0x80]`, indices `[A927]`, :1050-1085); only then, for a COMPUTER country,
  a second pass runs the retirement test `1771:7F40` per squad player (:1086-1099, the call at
  :1098) — on the record the first pass has aged — and re-creates retirees with `1771:7E80`
  (:1106).
- **A continuing player's yearly writes are exactly {+1, +4, +0x11}**: +1 (age) incremented by
  `7E6F` (`inc byte ptr es:[di + 1]`, static:static/goal-exe/code/seg_1771_11.asm:861, wrapping at 255), +4 (ability)
  written only by `compute_ability` `1771:32EB` (seg_1771_05.asm:312/366), +0x11 cleared
  unconditionally by `7FD4` (:1015). +0x11 is the player's goal count for the top-scorers
  tables: `0791:B3B7` increments it per goal (`B3EC`, seg_0791_18.asm:677) and reads it into or
  against the table at `[DS:A93F]` (`B446`, `B53B`, `B5E4`; :712/:814/:881); those five are
  the only accesses of a player record's +0x11 in the listing (the other `[di + 0x11]` lines are
  the 22-byte pitch record; notes.md section 2), so the yearly clear makes the count a per-year
  one. **+2 (peak), +3 (rating), +5, +7 never move for a continuing player** (+2's only writer
  is `roll_peak_age` `1771:3291`, called only from `make_player` `1771:96D3` — creation, which
  the yearly loop reaches only through the re-create 7E80; calls.tsv); so the task's "+5
  profile / +7 club position?" is answered: untouched. +6 (position) is written outside the
  yearly loop only (the substitution bookkeeping `0791:AD8F`, the player screen's 'C' key
  `1771:4952`, unmanage_country's bench copy `000E:0290`), but a year of matches may leave it
  moved (r0006: 7 of 211 continuing players, 05 → 08 and back) — so the corroborated invariant
  set is +0/+2/+3/+5/+7, and +6 is per-match bookkeeping. The engines' derived skills
  (`1771:3A06`, F015) therefore change by the +4 ratio alone: all twelve skills scale by
  (new +4 + 1)/(old +4 + 1) under the integer division.
- **The peak-age rule** (`compute_ability` `1771:32EB`, static:static/goal-exe/code/seg_1771_05.asm:283; a = +1 after the
  increment, p = +2, r = +3): the copy branch `p ≤ a ≤ p + 3` stores r (`333A`, :296-312);
  above it k = a − (p + 3) (:337-347); below it k = (p − a) idiv 2, signed (`33A7`, :348-361);
  then the stored byte is **AL, the low byte of ((r · (0x10 − k)) mod 65536) div 16**, the
  factor a 16-bit word (`3386`/`33AE`), the high product discarded (`33B9 xor dx, dx`), the
  divide unsigned (`33BE`), `33C3 mov es:[di + 4], al` (:362-366). So:
  - **the maximum r holds for five ages, p−1..p+3** — the copy branch gives four of them
    (p..p+3), and at p−1 the below branch's k = 1 idiv 2 = 0 gives r · 16 div 16 = r. E014
    shows it (r0005 country 1 word 6: p = 29, r = 0xA1, 0x96 at 27, 0xA1 at 28); (static:static/goal-exe/code/seg_1771_05.asm:283)
  - **before it** the ability rises by one step of r/16 every two years (15r/16 at p−3 and
    p−2, 14r/16 at p−5 and p−4, …); (static:static/goal-exe/code/seg_1771_05.asm:283)
  - **after it** it falls by one step of r/16 per year (15r/16 at p+4, …) to 0 at p+19 (k = 16); (static:static/goal-exe/code/seg_1771_05.asm:283)
  - **past p+19 the stored byte wraps** (k ≥ 17: the factor word is 0x10000 − (k − 16), and AL
    keeps the low byte of the quotient — a = 47, p = 27, r = 240 gives 4081 = 0x0FF1, stored
    0xF1), so the fall is monotone only to p+19. A computer-country player is retired long
    before (a > p + 5, below); only a managed country's player, never tested at the year end,
    could reach it, and no E014 record does.
  The peak differs between players only through the creation draw: `roll_peak_age` draws
  `+2 = DS:0E80[gk] + rand(3) − rand(3)` (25..29 outfield, 28..32 goalkeeper,
  `DS:0E80 = 1B 1E`, data/ds_2581_01.hex:123). (static:static/goal-exe/code/seg_1771_05.asm:283)
- **Retirement (context, Q014)**: for computer countries `1771:7F40` retires the AGED record when
  `(DS:110E[gk] < a AND caps word +8 == 0) OR a > p + 5`, both comparisons strict (`7F78 jae`,
  `7F9D jg`; 30 outfield / 33 goalkeeper, `DS:110E = 1E 21`, data/ds_2581_01.hex:143) —
  deterministic. So a player of 32 with peak 27 retires at this year end (aged 33 > 32). The
  re-create `7E80` draws +1, +2, +5, morale, fitness/energy and the initial; the listing fixes
  the rest — +0/+7 carried into make_player, caps/goals/status/+0x11 zero, performance 0x7FFF,
  +1 within DS:110C[gk] ± 5, +2 within DS:0E80[gk] ± 2, +4 of its own bytes, one +3
  (country_rating + 0x7F) per country — and `check_ageing.py` checks those on every re-create. (static:static/goal-exe/code/seg_1771_11.asm:951)

## Inferences

- **The continuing-player update draws no random number; the yearly path does** (the hazard's
  "differ by year" wording): the continuing update's callee closure — `7FB1` → `7E4A` →
  `32EB`, and the test `7F40` — calls no RNG entry point (calls.tsv; `214B:06B1` and
  `1771:0000` are not among their callees), so a continuing player's new +1/+4/+0x11, and the
  retirement decision, are a pure function of the record (and the year end's caps word). The
  re-create in the same `7FDF` call is random: `7E80` calls `214B:06B1` twice for the age
  (`7EC7`, `7ED1`), `make_player` (`7EC0`) and `1771:0000` for the initial (`7F1F`). The
  variance between continuing players is the creation draw of +2/+3, which the model reproduces
  from the records' own bytes (check_ageing's `observed variance` histogram: of 262 continuing
  players, 149 held their +4, the rest moved by 10..15 — r/16-sized steps of their ratings). (static:static/goal-exe/code/seg_214B_01.asm:898)

## Method

Static first (rule 22): the loop, its gate, its two-pass order, the write set, the +0x11 access
inventory and the peak rule were all read from `static/goal-exe/` — the named view, then
`code/` and `decompiled/` — with `calls.tsv` closing every callee set (the RNG claim for the
continuing update and +2's writer set rest on it); no run was needed to find the loop or the
rule. What static analysis could not give: the confirmation that the real game's year end
agrees byte-for-byte with the read rule over the recorded countries — the four stalled rounds
and the pre-match stall (below) meant no corroborated pair existed until E014-r0005. The runs
corroborate: every consecutive capture pair of every E014 record is compared against
`runtime/model/ageing.py` by `check_ageing.py` (`match: 300/300` over the 5 pairs of
r0005-r0006, each spanning exactly one ageing stage): every squad player word of the three
computer countries is one comparison, by identity — 262 continuing players with their
+1/+4/+0x11 as predicted and +0/+2/+3/+5/+7 and the name unchanged; 38 re-created where the
retirement predicate on the aged record fires (or, with caps 0 and the age clause open, where
no cap was won), each satisfying 7E80's fixed bytes; the tables unchanged (F008's hazard). The
four aborted records (r0001-r0004, one capture each) carry no pair and are reported, not
counted. Every match of every corroborating year ran through the R quick-result path (the
captain screen's Enter+r, F005's quick engine; all other fixtures refused at `0791:E80D` and
simulated) — the ageing runs in the stage settling, which that path still traverses (notes.md
§8); the stage transitions and settling screen occurred at every recorded year end. The factor
wrap past p+19 is static only (pinned by `tests/test_model_ageing.py`): no recorded player
reaches it.

Two run-side discoveries, both read statically after the runs exposed them (notes.md §7): the
pre-match team screen `0791:ED8A` silently refuses ` play ` while `0791:EA09` returns 0 (one
ineligible player among the first eleven — the r0002-r0004 stalls), and the recovery is the
assistant's recommended 20 (`0791:DC7E`, the Ins key of the SELECT TEAM screen, GOAL.HLP P58).
Both are annotation rows now, as is `0791:B3B7` (`update_top_scorers`), the reader of +0x11.
