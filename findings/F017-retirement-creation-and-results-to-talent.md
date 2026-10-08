# F017 Retirement, creation, and results -> talent

- **Status**: proposed
- **Question**: How do retirements happen, how are new players made, and do results feed
  new talent? (Q014, Q04.3-Q04.7, `docs/backlog.md`; T30)
- **Tests claims**: F007's byte map (`+3` = `country_rating(country) + 0x7F` at creation); F008's
  byte map and the +0..+0x13 layout; F016's yearly loop and the re-create 7E80's fixed bytes
  for the re-create; the help file's claim "replacements are better in a country whose points
  beat its expected points" (`GOAL.HLP` 196-205) — the chain is from prior-season results to
  a re-created player's `+3`, with a one-cycle lag for `+0x2B` (world rank, updated at stage 2
  entries) and same-cycle for `+0x2A` (continent rank, updated at stage 5 entries), both
  recomputes via `0177:63A4` running AFTER the year's ageing in `0177:8208` — `experiments/
  E016-q014-retirement/check_recreate.py` confirms 38/38 re-creates over runs/E014 (300/300
  comparisons).
- **Experiment and runs**: E016 (`experiments/E016-q014-retirement/`): the static map
  (`notes.md`) + `check_recreate.py` driving `runtime/model/recreate.py` over the
  already-committed E014 records (`runs/E014/E014-r00{01..06}.json`, 5 successful pairs, 38
  re-creates of the 3 computer countries). No new gameplay was needed: every byte the
  re-create writes is read from the listing and corroborated byte-for-byte by the E014
  records' 5 successful pairs.
- **Artifact**: set `goal2-67cf27d6`, variant none (the same E014 used — savestate bytes
  are not needed; the re-create's determinism is checked from the 20-byte record alone).
- **Max intervention**: I1 (memory read from savestates).
- **Tier reached**: V1 (a read-only rule from the listing, corroborated on the recorded years).
- **Confidence**: unreviewed. Static: every rule is read from `static/goal-exe/` (the named
  view first, then `code/` and `decompiled/`), with `calls.tsv`, `datarefs.tsv` and the
  initialised data image `data/ds_2581_01.hex` closing the reader/writer sets; claim-by-claim
  citations in `experiments/E016-q014-retirement/notes.md`. Behavioural: 38/38 re-creates of
  the E014 records' 5 successful pairs match `runtime/model/recreate.py`'s
  `recreate_constraints` and the `check_recreate.py` invariants; `tests/test_model_recreate.py`
  with literal-record fixtures and a mutation sweep.

## Answer (claim by claim)

- **A computer-country player retires when `(DS:0x110E[gk] < +1 AND caps_word(+8) == 0) OR
  (+1 > +2 + 5)`** — `0177:7F40` (seg_1771_11.asm:949-998), and only for a computer country
  and at the year end. `0177:0B77`'s `+0x2E > 0x80` flag (NOT MANAGED) gates `7FDF` to the
  retirement-test branch (the second pass, seg_1771_11.asm:1086-1107). `DS:0x110E = 1E 21`
  (data/ds_2581_01.hex:143) — 30 outfield, 33 goalkeeper; gk = `(+7 == 0)`. Both comparisons
  are STRICT (`7F78 jae`, `7F9D jg`). This is the F016 retirement test with a marker that
  ties it to the rank-reading re-create; before F017 the listed `+0x2A/+0x2B` were the
  candidates for which rank feeds the re-create; here we trace them.
- **A retiree is replaced by `0177:7E80(recreate_retired_player)` IN PLACE: `0177:96D3
  (make_player(1, old +7, old +0, player))` redraws `+5`, `+2`, `+3` (= country rating +
  0x7F, via `0177:10E7` country_rating), `+0xC` (morale), the player-tactics overrides,
  `+0xD/+0xE` (fitness/energy) and sets `+0x12/+0x13 = 0x7FFF`** (seg_1771_11.asm:870-947,
  notes section 2.1). Then 7E80 itself: two `214B:06B1(6)` draws at `:7EC7` and `:7ED1` give
  `+1 = DS:0x110C[gk] + rand(6) − rand(6)` (range DS:0x110C[gk] − 5 .. + 5, i.e. 20..30
  outfield, 23..33 goalkeeper — `DS:0x110C = 19 1C` per ds_2581_01.hex:143); a second
  `compute_ability` at `:7F01` (with the new `+1`) recomputes `+4`; zeros `+8/+9, +0xA/+0xB,
  +0x10` at `:7F09/:7F12/:7F19`; draws a new surname-initial byte from `0177:0000`
  at `:7F1F-:7F2D`; restores `+6` from the retiree's saved value at `:7F30-:7F36`.
  **The fixed bytes are 11** (10 in exact + `+4` from compute_ability): `+0, +7, +8, +9,
  +0xA, +0xB, +0x10, +0x11, +0x12, +0x13` are exact from the old + listings; `+1, +2, +5`
  fall in ranges; `+4 = compute_ability(+1, +2, +3)` of the new bytes; one `+3` per
  country per 7FDF call (`same_rating_per_country` invariant, check_ageing).
- **`0177:96D3(make_player)` (seg_1771_13.asm:1105-1201)** writes `+0` (country = argument
  at `:96F3`), `+7` (club_position = argument at `:96FC`), `+6 = +7` at `:9707`,
  `+5 = rand(0x10)` at `:9711-:971A`, `+1 = DS:0x118A[+7==0] − rand(7) + rand(7)` at
  `:9722-:9756` (28 ± 6 outfield, 31 ± 6 goalkeeper — `DS:0x118A = 1C 1F` per
  ds_2581_01.hex:147), `+2` via `0177:3291 (roll_peak_age)` (DS:0x0E80 = 1B 1E, +2 = base ±
  rand(3) − rand(3)), `+3 = country_rating(country) + 0x7F` when `param_1 != 0` at
  `:9764-:976B` (`country_rating` 0177:10E7 reads the country record's three rank bytes),
  `+4 = compute_ability` at `:979C`, `+0xC = rand(0x20)` at `:97A3-:97AB`, the player's
  tactics via `:97B3` (0177:3431), the fitness/energy via `:97BA` (0177:3558), and
  `+0x12/+0x13 = 0x7FFF` at `:97C0`. When `param_1 == 0` (the pool-player path
  `0177:9873 make_pool_player`), `+3 = country_rating + 0x7F − 10 − rand(10)` instead — a
  pool player has noise on `+3`; the re-create path does NOT.
- **The re-create's `+3` reads the COUNTRY RECORD's `+0x2A / +0x2B / +0x2C`** at the moment
  `0177:10E7(country_rating)` is called from `0177:96D3 :9768`. Neither 7E80, 96D3,
  roll_peak_age, 000E:54F0 nor 000E:7FDF write to the country record (verified by all
  writers of `[di + 0x2A..0x2C]`, only `0177:63A4 recompute_country_ranks` and a few
  helper scorers). So a re-create within one 7FDF call sees the SAME `+0x2A/+0x2B/+0x2C`
  (and therefore the same `+3`) — `same_rating_per_country` invariant, observed 19/19
  re-creates of one country in one 7FDF call across E014's 5 pairs (e.g. r0005 country 2
  had 4 re-creates in one call, all +3 = 0xC1).
- **`0177:63A4(recompute_country_ranks)` recomputes `+0x2A / +0x2B` from the points
  table** at every stage 2 (write `+0x2B`, world stage, `+0x40 = 0`) or stage 5 (write
  `+0x2A`, finals, `+0x40 = 1`) entry. Called from `0177:6730 (stage_qualifying)` at
  `:6762` (seg_1771_09.asm:1113) only when `[DS:A923]+0x38 > 0` (i.e. past the very first
  season). The new ranks are the sort order of `1771:602D` (world stage) or `0177:6103`
  (finals) over 128 countries; `0177:61F8` stabilises; loop assigns position 1..128
  to `+0x2B` (world) or `(position − 1) mod 32 + 1` to `+0x2A` (continent). The `+0x40 = (stage
  > 4)` discriminator is `0177:8208 stage_end`'s `:8280` write (seg_1771_12.asm:174).
  `0177:61F8` then `0177:63A4` writes a manager's score byte `[DS:A91F]+3*(0x80+m) + 1 =
  min(prior_score, country_rating)` at the loop's end (also notes section 4).
- **`0177:10E7 (country_rating)` formula**: `((5 − continent) * (33 − continent_rank) + (129 −
  world_rank)) / 2`, all in signed 16-bit (seg_1771_02.asm:697-738). The operand reads
  are at `:1104 (+0x2C)`, `:1116 (+0x2A)`, `:112A (+0x2B)` of the country record; the
  imul/12-bit arithmetic at `:1121-:1137`; the SIGNED idiv 2 at `:1139-:113D` (`cdq, mov
  cx, 2, idiv cx`); the result stored into `[bp − 2]` at `:1134` and returned in `ax`.
  Domain test: continent 0..4; continent_rank 1..32 (`(position-1) mod 32 + 1`); world_rank
  1..128. A healthier continent_rank lowers `(33 − continent_rank)` (smaller, so
  smaller product and smaller country_rating); a healthier world_rank lowers
  `(129 − world_rank)` (smaller, so smaller country_rating); both directions UPHOLD
  "better ranking ⇒ LARGER (better) rating", with a CAP at `((5-0)*(33-1) + 128)/2 = 144`
  for the world's best (`(cont=0, cr=1, wr=1)`). The CAVEAT is that `country_rating` does
  NOT use the country's tier / group (it has no separate input) — so a country and its
  tier-bound twins have DIFFERENT rank inputs but EACH rank is independent.
- **`0177:6730 (stage_qualifying)` runs AFTER `0177:8208 (stage_end) → 0177:80DA
  (yearly_ageing) → 0171:7FDF → 7E80`** (the play_round ordering at `000E:70B9`,
  seg_000E_09.asm:475-542: `:70E6 call 1771:8208` THEN `:70F4 call 1771:76B1`). So at the
  moment of re-create within a stage transition, the rank bytes are whatever the
  PRECEDING stage's recompute wrote (NOT the current stage's standings — those are not yet
  written). For a cycle N's `7FDF(1..128)` ageing (called from the stage 2/5 entrance of
  cycle N):
  - the world's previous `+0x2B` was set at the end of cycle N-1's stage 2 entry (i.e. from
    cycle N-1's world-qualifying standings);
  - the previous `+0x2A` was set at the end of cycle N-1's stage 5 entry (i.e. from cycle
    N-1's finals standings);
  - then the stage 2 entry of cycle N recomputes `+0x2B` (world-rank) using cycle N-1's
    overall results; only THEN is the cycle N `+0x2B` available for re-creates of stage 5.

  Net result for the same cycle N re-creates at stages 3, 5, 7, 8: BOTH `+0x2A` and
  `+0x2B` used by country_rating at re-create time are from the PRECEDING cycle's stage 5
  (for `+0x2A`) and cycle N-1's stage 2 (for `+0x2B`) — at minimum one cycle of lag for
  the world rank, AND `+0x2A` lags by at least one full cycle between consecutive
  recomputes.

  The HELP FILE's claim that better points produce better replacements is THUS TRUE: a
  re-created player's `+3` carries the country rating that was current at the moment of
  re-create, which reflects the PRIOR cycle's standings. Better prior standings ⇒ smaller
  world_rank ⇒ LARGER `country_rating` ⇒ LARGER `+3`. The timing makes the chain LAG the
  results by 1+ cycle for `+0x2B` and by 1+ cycle for `+0x2A` — the rebuild's year-end
  predictor therefore needs the cycle-N-1 final points table to write a cycle-N
  re-create's `+3`.
- **The retiree's MANAGED counterpart** uses `000E:54F0 (create_managed_replacement)`,
  reached from `000E:57E5 (offer_retire_player)` when the user accepts an offer: the same
  `make_player(1, retiree +7, country, new_player_index)` is called, with the age
  re-drawn from `DS:0x76[gk]` (a separate base table) instead of `DS:0x110C[gk]` (the
  re-create's base table) — `000E:54F0` then optionally overrides `+1` with
  `DS:0x76[gk] + rand(3)` when fewer than 20 of the squad+pool are below `DS:0x76[gk] + 4`
  (the young-squad heuristic at seg_000E_07.asm:705-707); `+3 = country_rating + 0x7F`
  remains identical to 7E80's path, so the chain is also YES here. OUT OF SCOPE per the
  brief's note (managed-retirement is the user / bot's offer path).
- **The PEAK AGE (`+2`)** and **the COUNTRY-RATING (`+3`) tie together** but in
  different cycles: `+2` is drawn ONCE at creation (`roll_peak_age` 0171:3291) and never
  moves (the 20-year and 28-year+ goalkeepers, F016). `+3` is read from the country record
  at creation. The FACT that `+2` and `+3` are both creation-only matters because the
  re-create happens AT the same instant the record is BORN — both bytes are set fresh by
  96D3 (or 7E80's follow-up). A continuing player's `+2` and `+3` never change.

## Method

Static first (rule 22): the entire chain — retirement test, re-create routine, every byte
it writes, the country record's rank recompute, the new ranks' timing — is read from
`static/goal-exe/` (the named view `static/goal-exe/named/seg_*.c` first, then `code/` and
`decompiled/`), with `calls.tsv` closing every callee set and the initialised data image
`static/goal-exe/data/ds_2581_01.hex` closing every constant. Claim-by-claim citations in
`experiments/E016-q014-retirement/notes.md`. No run was needed to discover the chain: every
byte the re-create writes is in the listing, the rank recompute is in the listing, the
country_rating formula is in the listing, the data image has the constant tables.

What static analysis could not give alone (and the runs corroborate):

- The 38 actual re-creates of the 5 successful E014 pairs, with their ages in
  `[20..30] ∪ [23..33]`, their peaks in `[25..29] ∪ [28..32]`, their profiles in `[1..16]`,
  and one `+3 = country_rating + 0x7F` per country per 7FDF call — `check_recreate.py`
  confirms `match: 300/300` with 38 re-creates detected. These are the only behaviour-side
  evidence the finding rests on; they confirm the BYTE-LEVEL invariants when paired with
  the static map.

What was the extent of corroboration (per the brief's "at most 4 runs, only where E014 and
static analysis cannot answer; runs/E016/"):

None. E014's 38 re-creates, paired with `check_recreate.py`'s byte-level check, cover the
run-side evidence this finding needs. The brief reserves E016 for chain corroboration that
static analysis cannot give; here, every byte is in the listing or the data image, and the
chains (country_rating's +0x2A/+0x2B reads, the rank recompute at stage 2/5) are
complete. Adding runs/E016 would be redundant.

The cache / no-run claim is verified by `experiments/E016-q014-retirement/check_recreate.py`
with `python3 tools/static/check_annotations.py` and `python3 -m unittest -v
tests.test_model_recreate` green; the `decompile.sh --annotations` reproduces
`static/goal-exe/named/` (covered by the regenerated `seg_*.c` files). The `notes.md`
section 4 is the chain walkthrough.
