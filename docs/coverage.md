# Coverage (the wide pass, pass one)

What the specification covers per knowledge-map area, what is missing, and where the findings disagree. Written by the main session from read-only agents' drafts of 2026-10-13 ([wide-pass.md](wide-pass.md)); the rows are in `spec/`, one file per area. The gaps are ranked cheapest first with the drafter's effort estimate (hours of agent work: read, run or hard), to choose pass-one tasks; sensitivity (pass two) is not yet measured. The statuses are in the spec files.

| Area | File |
| --- | --- |
| Countries, continents and their strength | [spec/countries.md](../spec/countries.md) |
| The player pool and the squad | [spec/pool.md](../spec/pool.md) |
| Player attributes and skills | [spec/attributes.md](../spec/attributes.md) |
| Ageing, peak age and new talent | [spec/ageing.md](../spec/ageing.md) |
| Fitness, energy, confidence and morale | [spec/fitness-morale.md](../spec/fitness-morale.md) |
| Team analysis and rankings | [spec/team-analysis.md](../spec/team-analysis.md) |
| Positions and formation | [spec/positions.md](../spec/positions.md) |
| Tactics | [spec/tactics.md](../spec/tactics.md) |
| The match engine | [spec/match-engine.md](../spec/match-engine.md) |
| Discipline, injuries and substitutions | [spec/discipline.md](../spec/discipline.md) |
| Competitions and fixtures | [spec/competitions.md](../spec/competitions.md) |
| Friendlies and tours | [spec/friendlies.md](../spec/friendlies.md) |
| Representation | [spec/representation.md](../spec/representation.md) |
| The other managers | [spec/other-managers.md](../spec/other-managers.md) |
| Sacking and the end of the game | [spec/end-of-game.md](../spec/end-of-game.md) |
| Several human players | [spec/multiple-humans.md](../spec/multiple-humans.md) |
| Data files and saves | [spec/data-files.md](../spec/data-files.md) |
| Customisation (ALTER.EXE) | [spec/customisation.md](../spec/customisation.md) |

## Per area: the gaps and the conflicts between findings

### Countries, continents and their strength

Rows: [spec/countries.md](../spec/countries.md).

**Coverage and gaps.**

Needs (knowledge map): the 128 teams, the 4 continents, how strength differs.
Established: teams and indices (CTY-01), continent and rank construction (CTY-02..04), the strength number and its start distribution (CTY-06..08), how it moves (CTY-09..11), default tactics (CTY-13, 14).

Gaps, cheapest first:

| # | Gap | Rows | Effort | Backlog |
| --- | --- |
| 1 | Membership list of the 4 x 32 with names; Concacaf/Oceania placement | CTY-03, 21 | 0.5 h read | Q005 |
| 2 | Rating of all 128 countries as a table (a rebuild constant table) and Germany's place | CTY-18 | 0.5 h read | Q005 |
| 3 | R007 meaning (readers of `DS:832E..8331`) | CTY-15 | 1 h read | Q005 |
| 4 | Points weights: k, the four placement tiers | CTY-10 | 1 h read | Q020 |
| 5 | Manager byte and `B6CC` delta | CTY-11 | 1 h read | Q020/Q035 |
| 6 | Fields above +0x2F of the country record | CTY-05 | 1-2 h read | Q005 |
| 7 | Rank/rating change observed after a full cycle (behavioural half of CTY-09) | CTY-09 | 2 h run | Q020 |
| 8 | Survival of a managed team's tactics over several matches | CTY-14 | 2 h run | Q005 |
| 9 | Results by continent and rating gap (the bot's choice of country) | CTY-16, 17, 19 | hard (needs sim) | Q006, Q028 |

**Conflicts and doubts (not resolved).**

- No finding contradicts another in this area. Note: F007/F008/F010/F011/F012/F015/F016 cite set `goal2-67cf27d6`, F014/F017/F018/F021 cite `goal2-a949da2f`; `known.json` says the first is the successor of the second with the same ten files, so no content conflict, only a scope word.
- F007's "about 85%" for the naming of +0x2A..+0x2C as continent/rank/world rank rests on two screens; C-CTY-02 is nonetheless `corroborated` because the rating fit over 128 countries is exact (the names do not change the numbers).

---

### The player pool and the squad

Rows: [spec/pool.md](../spec/pool.md).

**Coverage and gaps.**

Needs: the pool of 100, the squad of 20, when the squad may change.
Established: squad 20 (POOL-01), the arrays (POOL-02), exact creation of all 2560 + 80 (POOL-03/04), the two screens (POOL-06), selection order (POOL-09), who is selectable (POOL-08).

Gaps, cheapest first:

| # | Gap | Rows | Effort | Backlog |
| --- | --- |
| 1 | `EA09`/`3216` eligibility predicate as a rule | POOL-08 | 1 h read | Q008 |
| 2 | Why `26B9` calls `97CC`; effect on "identical games" | POOL-12 | 1 h read | Q007 |
| 3 | Substitution rule (`E022`, `C88D`) and its limits | POOL-15 | 1 h read | Q008/Q034 |
| 4 | A run corroborating when a squad change is refused (`DBFA`, finals/tours; read in F031) | POOL-13 | 1 h run | Q008 |
| 5 | Assistant selection rule | POOL-14 | 3-4 h read (hard) | Q008 |
| 6 | 2..6 managers: second block, base table, pools | POOL-04/05 | 2 h run | Q007 |
| 7 | Pool improvement over cycles | POOL-17 | 3 h run | Q014 |
| 8 | Which routine makes the one LCG draw between `9A40` and `98C4` | POOL-04 | 1 h read | Q007 |

**Conflicts and doubts (not resolved).**

- F007 says the squad-slot copies of `98C4` have age "18..22"; F017 (`DS:118C` = 0x11, 0x14 + rand(3)) and the listing give 18..20 for outfield and 21..23 for goalkeepers. Minor wording inconsistency, not resolved here.
- Help "pool of the 100 best players in your country" is narrowed by F007/F011 (C-POOL-07): not a conflict between findings, but the help claim is not what the code builds.
- F011 calls the 80 "numbered from A927" (index array) and F007 "players 2561..2640": consistent (record number = counter + 0xA00), noted for readers.

---

### Player attributes and skills

Rows: [spec/attributes.md](../spec/attributes.md).

**Coverage and gaps.**

Needs: the 12 skills, fitness, energy, hardness, age, caps, confidence, position, leadership, height, foot, performance.
Established: record layout and display of every item (ATTR-01..04, 07..13, 15, 17, 18), engine skill value (ATTR-05, 06, 14).

Gaps, cheapest first:

| # | Gap | Rows | Effort | Backlog |
| --- | --- |
| 1 | Position names 5..13 and what each position code means for the line sums | ATTR-11 | 0.5 h read | Q021 |
| 2 | Writers of caps/goals words | ATTR-19 | 1 h read | Q009 |
| 3 | Flank test of the wrong foot (`3179`) | ATTR-10 | 1 h read | Q022 |
| 4 | Captain proposal routine | ATTR-24 | 1-2 h read | Q009 |
| 5 | Agility in a tackle; hardness in a tackle/foul | ATTR-21..23 | 2-4 h read | Q010 |
| 6 | Marking / feinting / heading contests | ATTR-25 | 2-3 h read | Q010/Q025 |
| 7 | Mid-season status/card screens | ATTR-18 | 1 h run | Q033 |
| 8 | Sensitivity: how much each of ATTR-05, 14 moves results | ATTR-05, 14 | pass two | Q010, Q018 |

**Conflicts and doubts (not resolved).**

- **+3 is "potential" in F007 (70%) and "rating" r in F016 (peak value of +4)**: not a conflict of facts (both say the maximum of +4), but F008 found +3 used elsewhere as noise (hardness low bit, leadership (+3 - +5) mod 8). So +3 is overloaded; a rebuild must keep the byte, not only the idea.
- F008 says +0x11 is not read by the screen; F016 says it is the per-year goal count of the top-scorer table; F017 item 4 says the re-create "keeps +0x11" while F016 says the re-create has +0x11 zero. Resolution possible (7FD4 clears +0x11 for every player before 7E80), but the two statements read differently.
- F008 reads +0xD and +0xE as equal in all 80 new-game players, so only the listing separates them; F018 later separates them by distinct writers and consumers. Consistent, but the claim "fitness is +0xD" is static only (no run edits +0xD alone).
- F018, F021 and parts of F016's check use Unicorn emulation of the original code, not DOSBox-X; I treated that as a static-adjacent method in the Findings column. If the main session counts it as behavioural, C-ATTR-05, 13, 14 are corroborated by F015/F018 + F021 and a static finding.

---

### Ageing, peak age and new talent

Rows: [spec/ageing.md](../spec/ageing.md).

**Coverage and gaps.**

Needs: how skills grow and decline, how results feed the pool.
Established: gate (AGE-01), order (AGE-02), the rule (AGE-03, 04, 05), retirement and re-create for computer countries (AGE-08, 09), results to ranks to replacements (AGE-10).

Gaps, cheapest first:

| # | Gap | Rows | Effort | Backlog |
| --- | --- |
| 1 | Check `DS:0076`/`DS:0078` bytes against the data image | AGE-13 | 0.1 h read | Q014 |
| 2 | Churn per country per year from the model over 128 squads | AGE-18 | 1 h read/run | Q014 |
| 3 | Gate timing vs displayed years (four gates, year word at 2 and 5) | AGE-01 | 1 h run | Q013 |
| 4 | Managed path in a run: retirements one per fixture, pool aging | AGE-02, 12 | 2 h run | Q014 |
| 5 | Rank and replacement ceiling after a full cycle (behavioural half) | AGE-10, 17 | 2-3 h run | Q014 |
| 6 | "Better than expected" (help's mechanism), strong vs weak country | AGE-11 | 3 h run | Q014 |
| 7 | Retirement age histogram over 2 cycles | AGE-16 | 3 h run | Q013 |

**Conflicts and doubts (not resolved).**

- **Ageing cadence**: F016 says players age "once per displayed year" and also that a 4-year cycle has four ageings while the year word increments only at stages 2 and 5 (twice per cycle). Both cannot mean the same "year"; one of the two statements is loose. Not resolved here (C-AGE-01).
- F007 calls +2 "peak age, about 70%" and +3 "potential, about 70%"; F016 derives +2 and +3 from the ageing rule (supported), which raises both. F008 still says +3 is "not shown" and noise-like in two displays (see ATTR).
- F017 item 4 vs F016: whether the re-create "keeps" +0x11 (F017) or has it zero (F016); the unconditional clear by `7FD4` before the re-create explains both.
- All of F016's behavioural evidence is one start state, three computer countries, the R-quick-result path, five year-end pairs; F017's re-create checks reuse the same records, so F016 and F017 are not two independent confirmations (C-AGE-08 is therefore `supported`, not `corroborated`).

### Fitness, energy, confidence and morale

Rows: [spec/fitness-morale.md](../spec/fitness-morale.md).

**Coverage and gaps.**

What the rebuild and the bot need (knowledge-map: "how each changes during and between matches"): the size of every change in fitness, energy, confidence and team morale, and their effect on play.

Established (ids): record layout and display C-FIT-01; starting values C-FIT-02; energy loss in a match C-FIT-03, C-FIT-04, C-FIT-06, C-FIT-07; energy and fitness after a match C-FIT-08, C-FIT-09, C-FIT-11; what the engines read C-FIT-12 to C-FIT-14, C-FIT-16; effect size (quick engine) C-FIT-15; confidence after a match C-FIT-18 to C-FIT-22; events C-FIT-23; team morale C-FIT-27. Backlog Q015-Q018 are answered in substance by F018-F021 (the backlog rows still say "not placed": update them).

Gaps, cheapest first (effort in hours; read = listing only, run = a short measurement, hard = new model):

| Rank | Gap | Row | Backlog | Effort |
| --- | --- |
| 1 | Fixture-kind map (which kinds are friendly, league, qualifier, final) and whether a friendly result is applied | C-FIT-21, C-FIT-25 | Q016, Q017 | read 1 |
| 2 | What `DS:5A8F` tests and how often recovery runs (days, fixtures); needed for any energy/fitness trajectory and injury length | C-FIT-10, C-FIT-11 | Q015 | read 1 |
| 3 | Half-start step: first-half use of 9A32 | C-FIT-06 | Q015 | read 1 |
| 4 | Tabulate recorded activity counters by position | C-FIT-05 | Q015 | read 1 |
| 5 | Unicorn runs of CB7D, 7CC5, 13D0, BA4E, BB2F, kind-3 B7FA to move rows from `read` to `exact` | C-FIT-08, -21, -22, -23, -27 | Q015-Q017 | run 1 each (about 6 in all) |
| 6 | Booking and confidence (help says damage; listing says no write) | C-FIT-24 | Q017 | read 1 (confirm inventory) |
| 7 | Other five team-panel averages (fitness, hardness, energy, age, caps) | C-TEAM-09 | Q017/Q019 | read 1 |
| 8 | Substitution, man-marking energy effect measured on the watched engine | C-FIT-07, C-FIT-04 | Q015 | run 3 |
| 9 | Watched-engine size of the energy and form effect; first half of the quick engine | C-FIT-17, C-FIT-15 | Q018 | hard 6 |

**Conflicts and doubts (not resolved).**

1. F019 (clamp 1..32 in B364) against F020 (7CC5 clamps 1..255, panel reads s8): F020 reconciles them as two writers, but then a live +0xC can exceed 0x7F and read negative (panel sum, 377E form term, 278A). Neither finding says whether any play reaches 128. Not a contradiction; flagged for sensitivity.
2. F018 (watched: decrement per >180 active updates; quick: per 5-minute step) and the help ("direct proportion to activity"): F018 itself says the quick rule has no activity term. Not a conflict between findings, but the help claim is true for one engine only.
3. F019 and F020 both state the 7CC5/B364 mix as "static-derived"; F019 says a distinct abandoned-match rule is not established, F020 says the friendly kind is not established; same gap, no conflict.
4. F012 calls the line sums keeper/defence/midfield/attack "High confidence"; F010 says the same naming is "inferred, about 75%". Confidence labels differ for the same statement (affects C-TEAM-06).
5. F021 notes a defect in `runtime/model/keeping.py` (keeper-extra event value 0x18 vs the set {3,4}); F015 is the finding that introduced it. Outside A05; flagged.
6. The backlog still lists Q015-Q018 as "Not placed" while F018-F021 are merged.

---------------------------------------------------------------------------------------------------

### Team analysis and rankings

Rows: [spec/team-analysis.md](../spec/team-analysis.md).

**Coverage and gaps.**

Needs (knowledge-map): team skills from the eleven and the formation; how rankings are set. Established: the rating and the ranks' sources and update (C-TEAM-01 to C-TEAM-05), the engine's four line sums with their routing (C-TEAM-06), their use for results (C-TEAM-08), performance deltas (C-TEAM-10), morale aggregate (C-FIT-27).

Gaps, cheapest first:

| Rank | Gap | Row | Backlog | Effort |
| --- | --- |
| 1 | The team-info panel's four skills and five averages (what the screen shows, scale, rounding) | C-TEAM-07, C-TEAM-09 | Q019 | read 2.5 |
| 2 | Ranking place-to-bonus map and sort tie-break (800/600/400/200 mapping, 5EE1) | C-TEAM-03 | Q020 | read 1.5 |
| 3 | Manager bonus 0AA7 per manager (needed to reproduce the line sums for a given country) | C-TEAM-06 | Q019, Q035 | read 1.5 |
| 4 | BD03 team comparison; team performance rating; history screen | C-TEAM-13, C-TEAM-11, C-TEAM-12 | Q019, Q035 | read 4 |
| 5 | Initial ranks per DOS date (how the year changes the start) | C-TEAM-02 | Q001, Q020 | read 1 |
| 6 | Rank change moves replacements' +3 (end-to-end) and computer results vs quick results | C-TEAM-05, C-TEAM-08 | Q014, Q020, Q032 | run 6 |

**Conflicts and doubts (not resolved).**

1. F010 and F012 disagree in confidence on the naming of the four line sums (inferred 75% vs high); behavioural team-info screens were not read (no finding), so the identity with the displayed team skills rests on the template words only.
2. F012 describes M as "idiv 8, +0x10"; F010 says the added amount per tactic element is "0AA7(country) div 8". Whether M already contains the +0x10 and the division is ambiguous across the two texts; the main session should read 0AA7 before using the value as a parameter.
3. The backlog (Q020) says the ranking writers are "Not placed"; F017 places them (63A4). Backlog row is stale.

---------------------------------------------------------------------------------------------------

### Positions and formation

Rows: [spec/positions.md](../spec/positions.md).

**Coverage and gaps.**

Needs (knowledge-map): the 14 positions and how a formation places players. Established: the 14 codes and glyphs (C-POS-01), initial positions (C-POS-02), order (C-POS-03), position-to-skill (C-POS-04), height/foot (C-POS-05, C-POS-06), quick-engine routing and overrides (C-POS-07, C-POS-08), marking display (C-POS-09), substitution picker (C-POS-10).

Gaps, cheapest first:

| Rank | Gap | Row | Backlog | Effort |
| --- | --- |
| 1 | Position counts per country (formations as derived from block 10) and per-position counts of the pool | C-POS-02, C-POS-13, C-POS-12 | Q023, Q021 | read 1.5 |
| 2 | Class table rows per position vs help text; print height/foot tables into the finding | C-POS-14, C-POS-05 | Q021 | read 2 |
| 3 | Foot test 3179 (which positions, which foot) | C-POS-06 | Q022 | read 1 |
| 4 | Sweeper and marking assignment loop in the engine | C-POS-09 | Q025, Q023 | read 1.5 |
| 5 | `DS:099A` formation/role table for substitution | C-POS-10 | Q008, Q034 | read 1 |
| 6 | Out-of-position effect in the watched engine (callers of +6 in 0791) | C-POS-11 | Q021 | read 2, run 2 |
| 7 | Start coordinates per position / sweeper drift | C-POS-12 | Q023 | run 3, hard if modelled |
| 8 | Formation label shown on the team-info screen | C-POS-12 | Q019, Q023 | read 1 |

**Conflicts and doubts (not resolved).**

1. F008 says +7 (not +6) feeds skills, foot and height "by the listing" (static only, since +6 = +7 in all 80 new-game players); F012/F010 route strength by +6. If the two bytes were never different in any record, the +6/+7 split is unobserved behaviourally. Not a conflict but the key position claim (C-POS-04, C-POS-11) is static only.
2. F002 R011 says "bytes 0..10 and 11..19 each non-decreasing in 123 of 128 records" and "that slots 0..10 are the first eleven is not established"; F010 (52CC) and F002 BC5D (slots 1..11) treat slots 1..11 as the eleven. Consistent with each other; F002's caution is stronger.
3. The backlog (Q021, Q023) lists the position-to-line table as not placed; F010/F012 give it.

### Tactics

Rows: [spec/tactics.md](../spec/tactics.md).

**Coverage and gaps.**

What a rebuild needs: the 8 team tactics and their per-player overrides as state; their effect on match results; computer teams' reset and reaction rules; man-marking. What a competent bot needs: which tactics help against which opponents, and how much (that is the item with no number).

Established (row ids): representation and display: C-TAC-01..05, C-TAC-22. Per-player override derivation: C-TAC-07. Computer teams: C-TAC-10..12. Quick-engine effect (friendlies): C-TAC-08, C-TAC-09 (exact in the model, one managed country tested). Watched call sites only: C-TAC-13, C-TAC-14.

Gaps, cheapest first:

| # | Gap | Rows | Q | Effort |
| --- | --- |
| 1 | Screen labels of elements 5-7; R008 for 128 countries tabulated | C-TAC-02, C-TAC-04 | Q005, Q024 | read, 0.5-1 h each |
| 2 | Quick-engine magnitude of each element 1/5/6 as a goal-probability shift for typical M (the model is exact, so vary it) | C-TAC-08 | Q024 | read/run, 1-2 h |
| 3 | What the stat counters `DS:7B7E/82/83` print | C-TAC-09 | Q029 | read, 1 h |
| 4 | Which `C173` branches the records reached; managed-team persistence over two matches | C-TAC-10, C-TAC-12 | Q035 | run, 1-2 h each |
| 5 | Competitive quick result: `D5C1` -> `7EEF` (bookings, injuries, sending off) never run or modelled | C-TAC-15, C-TAC-21 | Q033, Q026 | run 3 h + hard read 8 h |
| 6 | Watched-engine effect of each tactic (sizes) | C-TAC-17 | Q024, Q026 | run: 30 h CPU, 2 h work, after a hand-off of seeds; the harness is built |
| 7 | Man-marking assignment (`3E2F`, early `3EF8`), manual override clear, conflict precedence | C-TAC-14, C-TAC-19 | Q025 | hard read, 4-6 h |
| 8 | Read the ten `26D7` call sites (outcomes, not just that they read) | C-TAC-13 | Q024 | hard read, about 15 h |

Biggest holes: row C-TAC-17. No tactic's effect on a watched match is quantified, and a bot cannot choose tactics without it. The quick engine is the only place the effect is exact, and it is only the attack/defence shift of elements 1/5/6 (a managed team's tactics in a friendly).

**Conflicts and doubts (not resolved).**

- F010 says the quick engine's "element k of the line sums" mapping k = 0..3 to keeper/defence/midfield/attack is inferred at about 75%; F021 prints the four sums as (keeper, defence, midfield, attack) and F012 uses mid/def/atk/gk by name in B19D; the mapping is consistent but nowhere proved by a test other than the model being seed-exact.
- The named view `static/goal-exe/named/seg_0791_02.c` still comments the keeper gate as "event code 0x18"; T40 and F015's text say the set `CS:276A` has members {3, 4} (byte 0x18 = bits 3 and 4). A stale comment, not a finding conflict.
- F010's statement of "about 70%" for managed-team persistence is the weakest claim a bot relies on (C-TAC-12).

---

### The match engine

Rows: [spec/match-engine.md](../spec/match-engine.md).

**Coverage and gaps.**

What the rebuild needs from A09: a result engine for every fixture type (quick for computer fixtures, a full watched simulation for the managed team's matches, since a bot plays them), home advantage, goals/own goals/offside, clock and injury time. What a bot needs: how a result depends on strengths, tactics, energy/form, and how much it is worth to change a lineup or tactics.

Established (row ids):
- Engine identity, RNG, determinism: C-MATCH-01..05.
- Quick engine, friendly, second half, seed-exact: C-MATCH-06..14, C-MATCH-17; its inputs: C-MATCH-10, C-MATCH-11, C-MATCH-15, C-MATCH-16. Computer-v-computer result read: C-MATCH-31.
- Watched engine skeleton, clock, draw volume: C-MATCH-18..21 and C-MATCH-22; skill reader: C-MATCH-23; contests read: C-MATCH-24..26; ratings: C-MATCH-29.
- Measured rates: C-MATCH-27, C-MATCH-28.

Gaps, cheapest first (Q numbers are backlog questions):

| # | Gap | Row | Q | Effort |
| --- | --- |
| 1 | F012 energy minutes prose vs model (6 vs 10 minutes); manager byte M table; `DS:066B` budgets | C-MATCH-14, C-MATCH-10, C-MATCH-17 | Q027, Q034 | read, 0.3-1 h each |
| 2 | Closed-form attempt probability and goal-count distribution of `B19D` from the sums | C-MATCH-09 | Q029 | read/analysis, 1-2 h |
| 3 | Identity of `DS:80FC` and the home/away slot assignment; home advantage size | C-MATCH-32, C-MATCH-33 | Q028 | read 2-3 h, then run 3 h |
| 4 | Computer-v-computer result: run `D47E` on 200 pairs and compare with the quick sample | C-MATCH-31 | Q032 | run, 2 h |
| 5 | Own goal and offside rates (counts from records and harness); injury time (search clock writers) | C-MATCH-28, C-MATCH-34 | Q029, Q027 | run/read, 2-3 h each |
| 6 | The first half of a quick match (start from the watchstart state) and extra time | C-MATCH-06, C-MATCH-12 | Q027 | run, 4 h |
| 7 | A second and third watched match: widen E011 from one match to coverage of events 3/4, the `5B36` duel, offside | C-MATCH-35, C-MATCH-20 | Q010, Q027 | run, 3 h |
| 8 | Competitive quick result: `D5C1` -> `7EEF`, cards, injuries, send-offs; and the watched foul path | C-MATCH-30, C-TAC-15 | Q033, Q026 | hard read 6-8 h |
| 9 | `8AE9` state handlers, `8889` movement, formation start positions (not placed), `83A2` | C-MATCH-19 | Q023, Q010 | hard, 10-20 h |
| 10 | Set pieces (corner, free kick, throw-in, goal kick, penalty), the shoot-out `A10A`, takers | C-MATCH-24, C-MATCH-34 | Q012, Q010 | hard, 10-15 h |
| 11 | Watched effects of tactics, energy and form on a whole match (needs a rough simulator or the harness at scale) | C-TAC-17, C-MATCH-15 | Q024, Q018 | run: 30 h CPU for 16 arms |

Watched-engine routines by status (from T42-T47 and E021; 98 of 98 checkpoints on E011-r0001 and r0002; calls per record from `t47-m2-draws.log`):

| Routine | What | Status | Detail |
| --- | --- |
| `214B:0688` | LCG step | exact | 74,686 calls per record proved |
| `214B:06B1`, `214B:06D0` | draw wrappers | exact | 73,533 and 37,025 calls; 52 mutations all killed (T47) |
| `0791:278A` | skill reader | exact | 37,096 calls per record |
| `1771:377E` | strength | exact | 88 calls per record; 376 literal records |
| `0791:287C` | contest gate | exact | 545 calls |
| `214B:0D56`, `23E4:0279` | long max, 32-bit multiply | untouched (reach log only) | the task is T48 (its label shows its state); 8,544 and 26,726 entries; 0D56's high-word branches never taken in E011 |
| `0791:9564` and its tree (`8AE9`, `8889`, `83A2`, `2FB1`, `59B3`, `6188`) | the sweep, movement | read (names and order); not modelled | F013, F018 |
| `34C1`, `3C3F`, `539F`, `5565`, `5474`, `5B36`, `5F8A`, `384C`, `3B15`, `3EF8` | the contests | read | F022 |
| `8CF5`, `9119`, `970C`, `98C4`, `9A32`, `983F` | offside line, referee draw, clock, half time | read | F013 |
| `1FDD`, `47C5`, `20E3`, `230C` | selection sites | read (F022 lists them); not modelled | M3 |
| `7EEF`, `798D`, `7B77`, `7D56`, `5B36`'s duel, `690C`, `9ED3`, `A10A` | fouls, cards, injuries, shoot-out | untouched | not reached by E011 |
| `D733` and everything it reaches (`0BC4`, `B19D`, `C173`, `65FE`, `8062`) | quick engine | exact in a Python model (second half, friendlies) | not hooked into the Unicorn match |

Biggest unmodelled parts of a whole watched match: movement and positions (`8889`, `8AE9`, the unplaced formation start positions, Q023); the event routines that make commentary (`5F8A` branches, set pieces, offside `90C5`); the foul path (bookings, send-offs, injuries); the keeper duel and the shoot-out; the substitution animation `8206`; extra time. The 98 of 98 result means the harness reproduces the original on one match; it does not mean those routines are understood. A rebuild that wants more than the quick engine's score needs gaps 7-10.

**Conflicts and doubts (not resolved).**

1. F012 vs F018 and the model: F012's prose says the quick energy loop runs in minutes 66, 71, 76, 81, 86 and 91 (six); the model (`quick_engine.py:801`, `831B % 5 == 0`) and F018 imply the second half runs it at 831B = 45, 40, ... 0, that is minutes 46, 51, ... 91 (ten). F012 also states 831B = 91 - 831F.
2. F013: "about 0x25 loop iterations per minute" (0x24 reload, 37 iterations) versus F013's own count of 2077 ticks per half over 46 minutes (about 45 per minute) and 4149 ticks per match in F022. Either tick counts something other than 970C iterations or the 0x24 reload is stepped by something other than 1.
3. F004 says menus waiting for a key draw nothing (the seed did not move across keys 1, 2 and 4 of d3) while F012 states `000E:045D` (crowd animation, 1000-1500 draws per call) runs from key waits `04F5`/`0572`. Both can hold if the waits differ; the finding on key timing (C-MATCH-04) leaves the draws before `r` unexplained.
4. F005 says the quick routine produced no bookings, sendings off or injuries in 120 matches and that the help file says `R` lists them; F012/F021 explain why: `D5C1` runs only when `DS:9A3D` != 0 (a competition). So F005's zero rates are friendlies only. A competitive quick result was never run (rows C-MATCH-27 and C-MATCH-30).
5. F012 gives `DS:0x7920[7C39 != 0 ? 0 : 1]` as the form delta index in `6443`; F020 says `DS:0x7920[side_of_credit]`. Same effect for a normal goal, different for an own goal; not checked.
6. F015's text carries two inline corrections (the table-byte elements 2, 4, 12 became 2, 4, 11, 12 by T42; the keeper set is {3, 4}, not 0x18 as an old model had it, T40). The named view comment still says 0x18.
7. T43's header lists 37,641 calls of `278A` per record and the T47 log 37,096; T47 explains that inner calls of proved originals do not fire hooks. Not a conflict, but a reader should use the log numbers.

### Discipline, injuries and substitutions

Rows: [spec/discipline.md](../spec/discipline.md).

**Coverage and gaps.**

What a faithful rebuild needs from A10: the foul generator per engine, the card state machine and bans, the
injury process (rate, who, how long), the substitution rules for human and computer sides, and the numbers
that tie them to confidence, performance and the pool; a competent bot needs the sizes: which squad to field
(unavailable players), how often players are lost, substitution limits (5 and 2), the effect of "go in hard"
on bookings and injuries.

Established: the quick engine's lack of events in friendlies (C-DISC-01), the watched rates (C-DISC-02), the
outline of the foul tree (C-DISC-04, C-DISC-05, C-DISC-07 to C-DISC-09), confidence and performance effects
(C-DISC-14, C-DISC-16 to C-DISC-19), the friendly quick substitution rule and budget (C-DISC-20, C-DISC-22).

Gaps, cheapest to fill first (hours: read / run / hard):
1. Review the drafter's readings C-DISC-10, C-DISC-12, C-DISC-25 as one finding (ban rules, caps, injury time):
   read, 3 h. Q033, Q027.
2. Confirm the budget 2 and the refusal messages with one competition run, C-DISC-21 and C-DISC-24: run, 2 h. Q034, Q008.
3. Count the foul table's draw1 and draw2 frequencies and instrument `D5C1`, C-DISC-05: read/run, 1-2 h. Q033.
4. Injury duration measured, C-DISC-13: run, 3-4 h. Q033, Q017.
5. Foul frequency in the watched engine and the chain from a challenge to `7EEF` (C-DISC-06): read, 3 h; then a run, 4 h. Q033, Q026.
6. The watched engine's computer substitution rule (C-DISC-23): read, 3-4 h. Q034, Q035.
7. A non-friendly quick result sample (C-DISC-01, C-DISC-04): run, 3-5 h; this also gives the `R` rates for qualifying and finals matches. Q033, Q029.
8. Effect of tactic 4 and hardness on the rates (C-DISC-27): hard, 10-15 h. Q024, Q026.
9. Carry-over at year change (C-DISC-28): read, 1 h. Q033.

Conflicts between findings (not resolved).
- F005 says it was not established whether `D733` can produce a booking, sending off or injury; F012 (later) says `D5C1` is not run in a friendly and traces it for other kinds. Not a contradiction, but F005's "Whether D733 can produce one at all" is answered only for kind 1.
- F015 writes the shoot-out decider set `DS:693A` as `{0x10}`; the data bytes at 0x693A are `10 FF x24 0F` (see COMP, C-COMP-07), the same shape as `DS:0F3E`. Affects C-COMP, not DISC.
- F012 cites its question as Q010 and the foul path as Q012; in `docs/backlog.md` Q010 is the contests and Q012 keeping and penalties, and the foul path is Q033. A labelling mismatch only.
- F020 (static: no booking writer of confidence) against `GOAL.HLP` 342-350 (bookings damage confidence): C-DISC-15 keeps both.

---

### Competitions and fixtures

Rows: [spec/competitions.md](../spec/competitions.md).

**Coverage and gaps.**

A faithful rebuild of A11 needs the whole fixture generator: the stage sequence, the groups, the order and
schedule of rounds, the knockout brackets, tie-breaks, hosts, seeding, and the rating inputs; a competent bot
needs to know when its matches come, what each stage is worth to the ranking (it feeds talent, F017), and the
tie-break and extra-time rules.

Established: the cycle (C-COMP-01), kind names (C-COMP-03), the two kind sets (C-COMP-05), the shoot-out gate
(C-COMP-06), the match routing and silent results (C-COMP-10), ranking points and rank writes (C-COMP-09) and
top scorers (C-COMP-26).

Gaps, cheapest to fill first:
1. Decoder checks of the sets and the start stage (C-COMP-02, C-COMP-07): read, 1 h. Q030.
2. Review C-COMP-08, C-COMP-24, C-COMP-25 (silent decision and the fixture record): read, 3 h. Q032.
3. Read the five stage builders `6B55`, `6E59`, `7090`, `71B2`, `74BE` for structure, counts qualifying, brackets (C-COMP-04, 12, 14, 15, 16): read, 4-6 h. Q030.
4. Group table sort, points per win, coin toss (C-COMP-18, C-COMP-19): read, 2-3 h. Q031.
5. Host selection and seeding (C-COMP-20): read `000E:60CB`, `6B55`, `71B2`: read, 3-4 h. Q031.
6. Extra time length and clock (C-COMP-17): read, 3 h. Q027.
7. Home advantage and host (C-COMP-21): run, 8+ h (hard). Q028.
8. The computer-vs-computer score distribution (C-COMP-11): run, 3 h. Q032.
9. Shoot-out watched (C-COMP-06): run, 4-5 h (a knockout savestate is needed). Q012.

Conflicts between findings (not resolved).
- F015: `DS:693A` = `{0x10}`. The data bytes read `10 FF x24 0F` (C-COMP-07). Also F019 and F020 both say "which kind is a friendly is not established"; F012 treats kind 1 as a friendly (`DS:9A3D`, `A4A1`) and `580B` names it. Not a contradiction: different strengths of evidence.
- F012 and F016 name artifact set `goal2-67cf27d6`; F005 says the same ten files as `goal2-a949da2f`; F007 and F014 use `a949da2f`. Scope only.
- `docs/backlog.md` Q020 says the writers of the ranking bytes are "not placed"; F017 places them (`63A4`, `61F8`, `5E3A`). The backlog row is out of date, not a finding conflict.

---

### Friendlies and tours

Rows: [spec/friendlies.md](../spec/friendlies.md).

**Coverage and gaps.**

A faithful rebuild needs friendly generation (count, partners, dates), the cancel and rearrange actions and
their limits, tours, and the differences in friendlies' rules (5 substitutions, no doubled result term, no
manager-rating update). A competent bot needs: how to cancel a friendly, whether it is worth it (squad rest
versus confidence), and the squad-lock rules on tours and in finals.

Established: kind 1 for friendlies, the budget of 5, the absence of foul events in the quick result of a
friendly (C-DISC-01), friendlies outside `DS:0F3E` (C-COMP-05, C-FRI-07), tours and the squad lock (C-FRI-01,
C-FRI-10, C-FRI-11, F031; read, not run).

Gaps, cheapest to fill first:
1. Confirm the friendly counts per country at a new game (C-FRI-04, C-FRI-12): a savestate read, 2 h. Placeholder Q12.1-Q12.4 (no Qxxx yet).
2. Cancel and rearrange in a run, with the refusal rule (C-FRI-02, C-FRI-05, C-FRI-06): run, 2-3 h. Q12.2 (no Qxxx).
3. Grep checks for friendly exclusions (C-FRI-08, C-FRI-09): read, 1 h. Q014, Q017.
4. A run corroborating the tours F031 read from the listing (C-FRI-10, C-FRI-11): the squad screen and an odd-position country's fixture list at stage 7: run, 2 h, Q008.
5. A comparison of confidence and morale after a friendly vs a qualifier (C-FRI-07): run, 3 h. Q016, Q017.

Conflicts between findings (not resolved): none specific to A12. F019 and F020 (friendly not established) against
F012 (kind 1 = friendly in `A4A1`) is the same note as in COMP.

### Representation

Rows: [spec/representation.md](../spec/representation.md).

**Coverage and gaps.**

Cited by findings: R001-R013 (F002 defines; F007 R007-R011, R013; F008 R008; F010 R008, R011; F011 R003, R004, R012, R013; F012 R008). Each has a row. R014-R024 are structures used by many findings without ids; they are mine to propose, so the main session may renumber. Nothing in this table is refuted.

Gaps, cheapest first (estimates are mine):
1. R024 key codes (1 h, no backlog Q).
2. R016 byte 0 and the human slots (1 h, Q007/Q008 context).
3. R007 role (2 h; help file P118 names strips; A17 and the bot's display need nothing more).
4. R021 and R020 formats (2-3 h; Q16.3).
5. R019 untyped blocks `[A92B]`, `[A92F]`, `[A933]`, `[A937]`, `[A93B]`, `DS:9CFF` (2-4 h; Q16.1; needed only for a loader of original saves, not for the rebuild's own saves).
6. R015 and R017 field-by-field (3 h each).

Conflicts. (1) F002 treats `Y.HIL` as a probable saved goal; F001 says only that it is the same size as a match summary. Not a contradiction, but R021 stays `hypothesis`. (2) F007's age range of the managed 80 (18..36) and F008's screen range (22..34) are different populations, no conflict. (3) F002 calls block 6 "display colours" (inferred); F007 shows no player-value routine reads it; compatible.

### The other managers

Rows: [spec/other-managers.md](../spec/other-managers.md).

**Coverage and gaps.**

Needs. The bot needs to predict an opponent's tactics and lineup, which determine the match against it. The rebuild needs the computer's decisions in every match (tactics, substitutions, lineup), the squad dynamics of the 127 other countries, and the manager rating.

Established: tactics (default, relative-strength adjustment, score reaction) and substitution scan in the quick engine, with the managed-team exception; squad dynamics (ageing gate, in-place re-creation); the manager rating term in strength.

Gaps, cheapest first:
1. C-MGR-12 engine identity of unseen results: 1-2 h, Q032.
2. C-MGR-13 manager name display: 1 h, help Q13.3.
3. C-MGR-14 marking update on opponent change: 2 h, help Q13.2 (Q025 is the marking question).
4. C-MGR-03/04 branch coverage in the existing replays: 2 h each, no new Q (inside Q035).
5. C-MGR-05 survival of a human's edit across matches: 2 h static or two quick matches.
6. C-MGR-11 `B6CC` deltas (manager rating after results): 3 h, new question.
7. C-MGR-08 lineup choice of a computer team: 4 h, Q035. This is the one that moves bot results most; it is also the least certain.

Conflicts between findings: none found. Note F010 says BD83's include is a random tactic from elements 1..6 and F012 says the same; F012's "5 per team in a friendly" for the budget and the help file's "2 in competition" (GOAL.HLP 254-259) are different fixtures, not a conflict.

### Sacking and the end of the game

Rows: [spec/end-of-game.md](../spec/end-of-game.md).

**Coverage and gaps.**

Needs. The bot needs: can it be sacked, and what to avoid (a floor on performance). The rebuild needs: whether play stops, and what dismissal does (the rebuild can shortcut with "never sacked" if the trigger is rare in idle play).

Established: the build saves; the stage counter wraps; the dismissal release routine's effects.

Gaps, cheapest first:
1. C-END-03 the shareware routine: 1-2 h (help Q14.1; the file here is registered, so low value).
2. C-END-08 a year limit: 2 h.
3. C-END-06 trigger of `01FA`: 1-2 h.
4. C-END-04 stage vs year display: 2 h.
5. C-END-05 sacking criterion: 3-4 h (help Q14.2; backlog placeholder "Sacking and the end of the game": `000E:5E6C`, `DS:19E8`). Highest value for the bot.

Conflicts: none found. F016's "four ageings per cycle but the year word advances at two stages" is a puzzle in one finding, not a conflict.

### Several human players

Rows: [spec/multiple-humans.md](../spec/multiple-humans.md).

**Coverage and gaps.**

Needs. The rebuild needs the count, the picks and the per-human state (the 80 pools, the manager record); the bot needs none of it (idle play = one human).

Gaps, cheapest first:
1. C-MULTI-06 name dialogue: 1 h.
2. C-MULTI-04 the RNG for m >= 2: 2-3 h.
3. C-MULTI-08 human vs human fixtures: 3 h.
4. C-MULTI-07 turn order: 3-4 h (help Q15.1; backlog placeholder "Several human players": `DS:1B1C`, `1771:09A0`).

Conflicts: none. Note the help file's "pool of 100" (GOAL.HLP 196-205; backlog Q007 tested "100") is 20 squad + 80 pool (F011), which narrows the help file rather than conflicting with it.

### Data files and saves

Rows: [spec/data-files.md](../spec/data-files.md).

### Customisation (ALTER.EXE)

Rows: [spec/customisation.md](../spec/customisation.md).

**Coverage and gaps.**

Needs. The rebuild needs only to read a `GOAL.DAT` (R001-R013) and accept names, strips and rankings from it (U20's databases). A writer for G-M6 (the plan's customisation milestone) needs the editor's rules. The bot needs nothing.

Established: the file layout (Representation above), the help file's feature list, the ranking-to-strength chain.

Gaps, cheapest first:
1. C-ALT-07 in-game rename persistence: 2 h.
2. C-ALT-06 length of an ALTER-written file: 1 h if a sample exists, otherwise folds into ALTER's listing.
3. C-ALT-02/04/08 ALTER's own code: 4-6 h, with a small change to `tools/static/listing.py`; help Q17.1-Q17.5; backlog placeholder "Customisation (ALTER.EXE)" (Q17.1-Q17.5).

Conflicts: none found. R007's role as strips (F002 inferred) and the help file's "team strips" agree but are not independently shown.

