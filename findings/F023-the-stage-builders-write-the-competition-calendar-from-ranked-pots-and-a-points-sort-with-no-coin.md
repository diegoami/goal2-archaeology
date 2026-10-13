# F023 The five stage builders write the competition calendar from ranked pots and fixed tables; a group table is sorted on points (2-1-0), goal difference, goals scored, and no coin is drawn anywhere in the stage code

- **Status**: proposed
- **Question**: How are the continental championships and the World Cup built: who qualifies per stage and
  continent, how groups, the bracket, hosts and seeds are formed, how a group table is sorted, what the decider
  set is, and which years each stage belongs to? (Q030, Q031, `docs/backlog.md`; T49, pass one of the wide pass,
  `docs/wide-pass.md`)
- **Tests claims**: spec rows C-COMP-02, 04, 07, 08, 12, 14, 15, 16, 18, 19, 20, 24, 25 (`spec/competitions.md`);
  the verdict per row is the last section. F015's "`DS:693A` = {0x10}" (conflict, settled in Answer 9).
- **Experiment and runs**: E023 (`experiments/E023-competitions-structure/`): `dsbytes.py` reads the committed
  data-segment dumps, `tables.py` decodes the builders' tables (`tables.txt`), `counts.py` re-runs the builders'
  loops over those tables (`counts.txt`), `shuffle.py` computes the draw shuffle's distribution (`shuffle.txt`).
  **No run of GOAL.EXE was made** (Method). Hashes of the outputs are in `experiments/E023-competitions-structure/notes.md`.
- **Artifact**: set `goal2-a949da2f`, the unpacked `GOAL.EXE` listing (`static/goal-exe/`).
- **Max intervention**: none (static reading and arithmetic over the listing's tables).
- **Tier reached**: V1 for the rules (read from the listing; no behavioural corroboration of any of them).
- **Notation**: uncertainty words are `docs/wide-pass.md`'s (**read** = from the listing, not run). Addresses `SSSS:OOOO`
  are the listing's, `DS:XXXX` the data segment; `asm` = `static/goal-exe/code/`. "Side A" is a fixture record's word
  at +4, "side B" the word at +6 (Answer 1).
- **Confidence**: unreviewed (status `proposed`). Every rule below is `read`: the listing's, with its addresses, the
  decompiled view agreeing (named view, `seg_1771_05.c`, `seg_1771_07.c`); none was run against the original. Two
  independent consistency checks passed (Answer 1): the fixture counts of the builders sum to exactly the block sizes
  the data image holds (`DS:6936`), and every table decoded is a complete schedule.

## Answer

### 1. The shared structures the builders write

- **Fixture record, 8 bytes**, number `n` (1-based) at `DS:A92B + 8n - 8`, written only by `1771:5D94(group, kind, A, B)`
  (asm seg_1771_09.asm:63-122): +0 = `0xFF` (unplayed), or `0xFE` when either country's byte +0x2E is above `0x80`
  (a managed country, `5DFB`-`5E1E`); +1 = group (0 when the fixture belongs to no group table); +2 = kind;
  +4 = side A, +6 = side B (country words). **+3 is not written by the builder** (it is the result, set when the
  match is played; 82BD reads +0 and +1 as the two scores). The same call appends the fixture's number to each country's
  list of 36 words at `DS:A92F + 0x48 * country` (`1771:5D02`, the list shifts down one word, the newest is last)
  and raises the country byte +0x3B to the kind if lower. `[A923]+0x28` is the **next free number**
  (incremented at the end of 5D94, `5E30`), `[A923]+0x26` the next number to play (`000E:6CA7`, named seg_000E_05.c:514-694;
  it plays the record at `DS:A92B + 8*[+0x26] - 8`, then increments).
  Numbers 1..2400 are fixtures, **2401..2408 are eight synthetic play-off aggregate records** (7090, 85F7), and
  the sentinel `0xFF` of `init_new_game` sits at number 2409 (`A92B+0x4B40`).
  (static:static/goal-exe/code/seg_1771_09.asm:63)
- **Numbering by class.** A class is `[A923]+0x40` = 0 for stages 2-4 and 1 for stages 5-8
  (`stage_end`, F016). 6730 sets `[+0x28] = [+0x26] = word DS:6936[class]` = **1 and 1361** (`tables.txt`; asm 67C9).
  Class 0 therefore owns fixtures 1..1360, class 1 owns 1361..2400.
  (static:static/goal-exe/code/seg_1771_12.asm:121) (static:experiments/E023-competitions-structure/tables.txt)
- **Group tables** at `DS:A933` (`0x1C00` bytes; 6730 clears `0xE00` of them at a stage 2 or 5 build, asm 67D0-67E9).
  Address of a slot: `A933 + class*0xE00 + table*0x700 + continent*0x1C0 + group*0x38 + slot*8 - 0x200`
  (continent c = 1 Europe, 2 America, 3 Africa, 4 Asia: the names at `DS:6E92 + 8c`, ds_2581_03.hex rows 6E80-6EA0,
  and `load_countries` assigns `continent = (position-1)/32 + 1`, named seg_1771_07.c:213-262); group g = 1..8; slot s = 1..4;
  `table` 0 = the **A table** (qualifying groups), 1 = the **B table** (the finals groups of the continental championship
  (class 0) and of the World Cup (class 1, continent 1)). A slot is 8 bytes: country word, then wins (+2), draws (+3),
  losses (+4), goals for (+5), goals against (+6), points (+7) (82BD, asm 82D6-8476); after the 4 slots of a group
  come 12 words holding the fixture numbers by round (the round list): **relative to the start of slot 1 they are at `+0x20 + 2(round-1)`, i.e. `+0x20..+0x37`, the last word at `+0x36`** (6730 writes `first-slot base + 2*round + 0x1E`, round 1..12, asm seg_1771_09.asm:1466-1472, named seg_1771_05.c:334; 6B55 and 71B2 write rounds 1..6 the same way, `6617` reads them); the group stride is 0x38, so the list ends where the next group's slot 1 begins (the formula above is relative to a notional slot 0, where the words are `+0x28..+0x3F`).
  (static:static/goal-exe/code/seg_1771_12.asm:205) (static:static/goal-exe/data/ds_2581_03.hex)
- **State bytes of `[DS:A923]` the builders use**: +0 managers, +1 current manager, +2+m group of manager m
  (`5E99(v)` sets all managers' to v), +0x26/+0x28 fixture pointers (above), +0x2A first fixture of the
  last-16 round, +0x2C first fixture of the play-offs, **+0x2E, +0x30, +0x32, +0x34 the hosts of continents 1..4**, +0x36
  the World Cup host, +0x38 year word, +0x3C stage, +0x3D rounds left in the stage (`stage_end`: 1, except 2 at stage 4 and 4 at stage 8), +0x40 class.
  (static:static/goal-exe/code/seg_1771_09.asm:162)
- **The 128-byte order table** `DS:9D00..9D7F` (`DS:9CFF + i`): 4 blocks of 32, continent c at `32(c-1)+1..32c`,
  each block is **4 pots of 8** in rank order. `1771:56FF` fills it before every stage 2 or 5 build: at stage 2 (class 0) it copies
  the continental order array `DS:9C7E` (128 bytes, four continent blocks); at stage 5 (class 1) it takes the world order array
  `DS:9BFD` and keeps, for c = 1..4, the countries of continent c in world order (named seg_1771_04.c:618-660).
  The two arrays are the ones `63A4` sorts by points (F017); `load_countries` fills them at a new game from `GOAL.DAT`
  (named seg_1771_07.c:213-262). **Order of events** (6730, asm seg_1771_09.asm:1109-1113): 56FF copies first, `63A4` recomputes after, so a draw uses the arrays as the
  *previous* recompute left them: stage 2 the continental order of the last stage 5, stage 5 the world order of the last stage 2, and
  in the first cycle the file's initial order.
  (static:static/goal-exe/code/seg_1771_08.asm:446)
- **Count check.** Re-running the builders' loops over the decoded tables (`counts.txt`) writes **1360** fixtures in class 0
  and **1040** in class 1; `DS:6936 = {1, 1361}` makes class 0 exactly 1360 and 2400 - 1360 = 1040. The data image and the loops agree to the unit.
  (static:experiments/E023-competitions-structure/counts.txt)

### 2. Stage dispatch and years (`1771:76B1`, `8208`)

- `run_stage` sends stage 2 and 5 to `6730`, 3 to `6B55`, 4 to `6E59`, 6 to `7090`, 7 to `71B2`, 8 to `74BE`. It is
  called once at a new game (`0000:0080`) and then by `play_round` (`000E:70B9`, asm 70E6-70F4)
  each time `stage_end` has run, i.e. each time `[+0x26] == [+0x28]` (all fixtures played). `stage_end` counts `+0x3D` down
  and moves the stage only at 0; so a stage with several rounds (4 and 8) is **built round by round**: 6E59 and 74BE branch on `+0x3D`.
  (static:static/goal-exe/code/seg_1771_11.asm:6) (static:static/goal-exe/code/seg_0000_01.asm:52) (static:static/goal-exe/code/seg_000E_09.asm:492)
- The ageing/year gate is the set `CS:81E8` = {2, 3, 5, 7} (bytes `AC`, F016): a new playing year starts on entry to
  each, so **year 1 = stage 2, year 2 = stages 3-4, year 3 = stages 5-6, year 4 = stages 7-8**, and the year word (+0x38) increments at 2 and 5
  (F016), twice per cycle. The tables are recomputed after every played fixture by `1771:8757` (called from `000E:6CA7`, asm 7004 and 7069) when the
  stage is in `CS:8737` = {2, 3, 5, 7}.
  (static:static/goal-exe/code/seg_1771_12.asm:118) (static:static/goal-exe/code/seg_1771_12.asm:682) (static:static/goal-exe/code/seg_000E_09.asm:400)

| stage | year | builder | class | competitive kind and count | friendlies (kind 1) | listing |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 1 | 6730 | 0 | 2: 384 (12 rounds x 4 continents x 8 groups) | 384 | static:static/goal-exe/code/seg_1771_09.asm:1092 |
| 3 | 2 | 6B55 | 0 | 3: 48 (6 rounds x 2 groups x 4 continents) | 528 | static:static/goal-exe/code/seg_1771_10.asm:6 |
| 4 | 2 | 6E59 | 0 | 101 (0x65) x 8, then 102 x 4 and 103 x 4 | 0 | static:static/goal-exe/code/seg_1771_10.asm:324 |
| 5 | 3 | 6730 | 1 | 5: 384 | 256 | static:static/goal-exe/code/seg_1771_09.asm:1092 |
| 6 | 3 | 7090 | 1 | 6: 16 (4 two-leg pairs in each of Africa and Asia) | 0 | static:static/goal-exe/code/seg_1771_10.asm:553 |
| 7 | 4 | 71B2 | 1 | 7: 48 (6 rounds x 8 groups) | 320 | static:static/goal-exe/code/seg_1771_10.asm:671 |
| 8 | 4 | 74BE | 1 | 8 x 8, 200 x 4, 201 x 2, 202, 203 | 0 | static:static/goal-exe/code/seg_1771_10.asm:987 |

### 3. Stage 2 and stage 5: the qualifying groups (`1771:6730`, asm seg_1771_09.asm:1092-1529)

- **Inputs**: the order table after 56FF (1); the points of the countries (year word 0: every country's points := `5 - continent`
  and `sys_get_time` seeds the RNG, asm 6767-67A8, F004/F017; otherwise `63A4` recomputes the ranks); the state.
  (static:static/goal-exe/code/seg_1771_09.asm:1113)
- **Resets**: the 6 bytes at `[A923]+0x14`; fixture pointers to `DS:6936[class]`; the class's `0xE00` bytes of group tables; all managers' group := 1 (`5E99(1)`);
  the hosts (class 0: `+0x2E..+0x34` := 0, class 1: `+0x36` := 0, asm 685C-6891); the top-scorer tables (class 0: `0x180` bytes at `[A93F]`,
  four continents of `0x60`; class 1: `0x60` at `+0x180`, the World Cup's; asm 6891-68C5).
  (static:static/goal-exe/code/seg_1771_09.asm:1168) (static:static/goal-exe/code/seg_1771_09.asm:1215)
- **The draw** (asm 67FA-6855 and 68C5-69AD). *Seeding:* for each of the 16 blocks of 8 positions (continent c, pot a = ranks
  8(a-1)+1..8a of the continent in the order table) the builder swaps two uniformly drawn positions of the block (`214B:06B1(8)` twice, `214B:007B`) **4 times**; then
  position p of pot a goes to **group p**, in the slot `DS:0F71 + 4r + a` of a random row r = 1..4 (`214B:06B1(4)`, one row per group) of the four permutations at `DS:0F76`:
  (1 2 3 4), (2 3 4 1), (3 4 2 1), (4 1 2 3). Exactly one team of each pot sits in each of the 8 groups of the continent: **8 groups of 4, one team per pot, pot a = the
  8(a-1)+1-th to 8a-th ranked team of the continent**. *Weak shuffle (computed, `shuffle.txt`):* 4 swaps of two uniform positions leave a team in its own position with probability
  **0.402** (a uniform shuffle would give 0.125) and in each other group 0.085, so the top team of a pot is in group 1 about 40% of the time, the second in group 2, and so on.
  *Slot:* pot 1 and pot 2 take each slot 1..4 with probability 1/4; pot 3 takes slot 2 with probability 1/2, slots 3 and 4 1/4 each, never slot 1; pot 4 takes slot 1 with probability 1/2, slots 3 and 4 1/4 each, never slot 2.
  (static:static/goal-exe/code/seg_1771_09.asm:1177) (static:experiments/E023-competitions-structure/shuffle.txt)
- **The group fixtures** (asm 6AB3-6B2D, the call at `6B2D`): for round e = 1..12, continent c = 1..4, group g = 1..8, in this order,
  `5D94(g, stage, slot a, slot b)` with the pair `(a, b)` = bytes `DS:0F54 + 0x18(g+c) + 2e` and `+1`, i.e. the rows of the table at `0F86..108D`, one row per `g + c` = 2..12, each a
  **permutation of the 12 ordered pairs of 4 teams** (a double round robin, one match per group per round; `tables.txt` checks all 11 rows). Each team plays 6 group matches; the group number
  in the record is g, the kind is the stage byte (2 or 5). No ranking points are added at creation (the `5E3A` bonus is not used here).
  (static:static/goal-exe/code/seg_1771_09.asm:1510) (static:experiments/E023-competitions-structure/tables.txt)
- **Friendlies** (asm 6A0C-6AB0): in round e, when `e < DS:1106[class == 0]` = 7 (stage 2) or 5 (stage 5) and `DS:1087 + 6g + e` = t is non-zero,
  four friendlies `5D94(0, 1, slot a of group t, slot a of group g)`, a = 1..4 (inter-group, same continent). The table has 3 non-zero entries per group in rounds 1-6: **384** friendlies at stage 2, **256** at stage 5 (rounds 1-4: 2 per group).
  A team plays 6 group matches and 6 friendlies at stage 2 (**12 fixtures**, the exact size of the 12-entry window of the table sort, 8) and 6 + 4 = 10 at stage 5 (`counts.txt`).
  (static:static/goal-exe/code/seg_1771_09.asm:1391) (static:experiments/E023-competitions-structure/counts.txt)
- **After**: the managed countries' group fixtures are turned to `0xFE` by `1771:6617(0)` (asm 6B4E; it reads each manager's group in `[A923]+2+m` and the round list of the group):
  all 12 fixtures of a managed country's group become watchable, not only its own.
  (static:static/goal-exe/code/seg_1771_09.asm:973)
- **Outputs**: the A table of the class with 32 groups (continent x group) of 4, the round lists, 768 or 640 fixtures.
  (static:static/goal-exe/code/seg_1771_09.asm:1525)
- **Dates and matchdays**: none. A fixture has no date; the order of play is the fixture number, i.e. round-major, then continent, then group; a "matchday" is the run of fixtures between two fixtures of managed countries (`route_fixture` returns after a managed fixture, F010).
  (static:static/goal-exe/named/seg_000E_05.c:512)

### 4. Stage 3: the continental finals groups (`1771:6B55`, asm seg_1771_10.asm:6-323)

- **Inputs**: the A table of class 0 sorted by `8757` after every stage 2 fixture (slot 1 = group winner, 2 = runner-up, ...), see 8.
  (static:static/goal-exe/code/seg_1771_10.asm:6)
- **Host** (asm 6B75-6BA4): for each continent c, a group `rand(8)` (`214B:06B1`) and **its winner (slot 1) is the host of the continent**: `[A923]+0x2C+2c`.
  (static:static/goal-exe/code/seg_1771_10.asm:24)
- **Finals groups** (asm 6BAD-6C8B): `B[c][g][perm(a)] = A[c][2a - (g odd)][(g+1)/2]`, g = 1..8, a = 1..4, one random permutation row per (c, g):
  B group 1 = the winners of the odd qualifying groups 1,3,5,7; B2 = the winners of 2,4,6,8; B3/B4 = the runners-up of the odd/even groups; B5/B6 thirds; B7/B8 fourths.
  **Only B1 and B2 play the finals** (the 8 qualifiers of a continent, `g < 3`: the manager's group `[A923]+2+m` is set only for g < 3, `6C73`); B3..B8 take part in friendlies only.
  (static:static/goal-exe/code/seg_1771_10.asm:47) (static:static/goal-exe/code/seg_1771_10.asm:123)
- **Fixtures**, for round e = 1..12, c, g (asm 6CEE-6E34: friendlies 6D07-6D6C and 6E31, group fixtures through `5E3A` at 6DEB): `e < 7`: the friendlies of the stage-2 kind through the table `DS:1087` among B groups (4 per entry; **384**);
  `e >= 7` with m = e - 6 = 1..6: for g < 3 `5E3A(host, g, 3, ...)` (kind 3, **48** fixtures: single round robin of 4, the pairs of `DS:10BC + 2m` = (1,2) (3,4) (1,3) (2,4) (1,4) (2,3)); for g >= 3 the same pairs as friendlies (**144**).
  `5E3A` puts the host, when it is one of the two teams, as side B (it swaps the default order when the default A operand is the host) and adds 200 ranking points to both teams (F017). All 128 countries play 9 fixtures at this stage (`counts.txt`).
  (static:static/goal-exe/code/seg_1771_10.asm:174) (static:experiments/E023-competitions-structure/counts.txt)
- **Output**: B1 and B2 of each continent, tables recomputed after each fixture, 576 fixtures; `6617(1)` marks the managed countries' finals group.
  (static:static/goal-exe/code/seg_1771_10.asm:320)
- **Qualifiers per continent**: 8 (the group winners of stage 2). To the semi-finals: winner and runner-up of B1 and B2 (4).
  (static:static/goal-exe/code/seg_1771_10.asm:39)

### 5. Stage 4: the continental knockout (`1771:6E59`, asm seg_1771_10.asm:324-485)

- **Inputs**: `+0x3D` (2 or 1), the sorted B1 and B2 of each continent (slots 1 and 2), the continent's host.
  (static:static/goal-exe/code/seg_1771_10.asm:324)
- `+0x3D == 2` (asm 6E8E-6F18): **semi-finals** `SF1 = winner of B1 v runner-up of B2`, `SF2 = winner of B2 v runner-up of B1`, kind **0x65 (101)**, both through `5E3A`; the pairing names above do not give the side order. Pre-swap arguments of `5D94` (A, B): **SF1 = (runner-up of B2, winner of B1)** and **SF2 = (runner-up of B1, winner of B2)**, because the builder pushes the winner first and `5E3A`'s non-swap path forwards the second push as A; `5E3A` swaps A and B when its default A operand is the host (+200 points); the two fixture numbers are stored at `DS:A933 + 0x1C0*c + 0x56C` and `+0x56E` (asm 6E99-6EE2; these fall in the B1 group's round-list words 7 and 8, `+0x20 + 2(round-1)` from slot 1 at `A933 + 0x1C0*c + 0x540`, which stage 3 leaves unused as it writes only rounds 1..6).
  (static:static/goal-exe/code/seg_1771_10.asm:345)
  (static:static/goal-exe/code/seg_1771_10.asm:356)
  (static:static/goal-exe/code/seg_1771_09.asm:137)
- `+0x3D == 1` (asm 6F1B-6FDB): **third place** kind **0x66 (102)** = the losers of the two semi-finals (`5CCB`), **final** kind **0x67 (103)** = the winners (`5C94`); numbers stored at `+0x570`, `+0x572`.
  (static:static/goal-exe/code/seg_1771_10.asm:405)
- 4 continents x (2 + 2) = 16 fixtures. There is **no tie-break in the builder**: the semi-final and final winners come from the played match's byte +3, decided by extra time and the shoot-out (kinds 101..103 are in the decider set, 9).
  (static:static/goal-exe/code/seg_1771_10.asm:485)

### 6. Stage 6: the African and Asian play-offs (`1771:7090`, asm seg_1771_10.asm:553-670; `85F7`, seg_1771_12.asm:557-683)

- **Inputs**: the class-1 A table, sorted after stage 5: for c = 3 (Africa) and 4 (Asia), slot 1 (the 8 group winners).
  (static:static/goal-exe/code/seg_1771_10.asm:553)
- **Pairs** (asm 70AE-7115): `[A923]+0x2C := [+0x28]`; for c = 3, 4 and g = 1..4: **leg 1 = side A winner(group 9-g), side B winner(group g); leg 2 = A winner(g), B winner(9-g)**, kind 6, group 0, `5D94` directly (no bonus). 4 pairs per continent: (1 v 8), (2 v 7), (3 v 6), (4 v 5) of the group winners: **16 fixtures, 4 qualifiers each**. After each leg 1 the record is copied to the aggregate record number `0x961 + k` (k = pair index 0..7, asm 7119-7161) and `6FEB` turns the fixtures to `0xFE` for managers of the same continent as the fixture's country.
  (static:static/goal-exe/code/seg_1771_10.asm:589) (static:static/goal-exe/code/seg_1771_10.asm:637)
- **The tie rule** (85F7, run by `8757` at stage 6 after every fixture): when both legs are played (`rec[0] < 0xFE`), aggregate +0 = leg2 B goals + leg1 A goals (A's total), +1 = leg1 B goals + leg2 A goals (B's total, B = winner(g)); aggregate +3 = 1 (B qualifies) iff **B's total is larger, or the totals are equal and leg 2's A goals >= leg 1's A goals** (`86F0 ja`, `8707 jae`); otherwise A. In leg-score terms: with equal totals, B (winner(g)) goes through iff the first-listed side's score in leg 2 (B's team) is at least the first-listed side's score in leg 1 (A's team); whether the first-listed side is the home side is not established here, so this is not called a home- or away-goals rule. **The listing contains a coin-shaped branch** (`8714`-`871D`: B's country word `& 1`) **but it is unreachable**: `8707 jae` takes the jump on equality before it. So the aggregate is **never a coin**, contrary to the help file (`GOAL.HLP` 293-300).
  (static:static/goal-exe/code/seg_1771_12.asm:650) (static:static/goal-exe/code/seg_1771_12.asm:658) (static:static/goal-exe/code/seg_1771_12.asm:787)
- **Outputs**: the 8 aggregate records (winner = `5C94`), read by 71B2.
  (static:static/goal-exe/code/seg_1771_12.asm:557)

### 7. Stage 7: the World Cup finals groups (`1771:71B2`, asm seg_1771_10.asm:671-986)

- **Inputs**: the class-1 A table (sorted after stage 5), the 8 aggregate records (6), the order table of this class (world order by continent, 1).
  (static:static/goal-exe/code/seg_1771_10.asm:671)
- **Host** (asm 71C5-71FA): `[A923]+0x36 := A[c][g][1]` with c = `rand(2)` (1 or 2), g = `rand(8)`: **the winner of a random qualifying group of Europe or America**. Africa, Asia, runners-up and play-off winners never host.
  (static:static/goal-exe/code/seg_1771_10.asm:681)
- **The 32 finalists, 8 groups of 4** (asm 71FA-72D0): for g = 1..8, a random row of the permutations of `DS:0F72` decides the slots: slot `p1` = **Europe winner of group g** (`A[1][g][1]`), `p2` = **Europe runner-up of group 9-g** (`A[1][9-g][2]`), `p3` = **America winner of group g** (`A[2][g][1]`), `p4` = **the winner of play-off number g** (`5C94` of aggregate `0x960+g`: g <= 4 Africa, g >= 5 Asia). That gives 16 + 8 + 4 + 4 = 32. Managers' groups are noted in `[A923]+2+m` (asm 7317).
  **There is no ranking input and no random draw other than the slot permutation**: the World Cup groups follow from the qualifying groups' indices.
  (static:static/goal-exe/code/seg_1771_10.asm:720) (static:static/goal-exe/code/seg_1771_10.asm:737) (static:static/goal-exe/code/seg_1771_10.asm:753)
- **Group fixtures** (asm 7420-74AB): for round m = 1..6 and group g: `5E3A(host, g, 7, pair m of DS:10BC)` (kind 7, +200 points each): **48 fixtures**, a single round robin (1,2) (3,4) (1,3) (2,4) (1,4) (2,3).
  (static:static/goal-exe/code/seg_1771_10.asm:976)
- **Friendlies for everyone** (asm 7336-741D): 256 from three tables (positions of the order table: `DS:10C6`, `DS:10D5`) plus 64 consecutive pairs (order positions 2i-1 v 2i): **320**, so every one of the 128 countries gets 5 friendlies; a finalist plays 8 fixtures this stage.
  (static:static/goal-exe/code/seg_1771_10.asm:890) (static:experiments/E023-competitions-structure/counts.txt)
- **Output**: groups of 4 with the finalists, recomputed after every fixture (`8757`, one continent index, 8 groups); `6617(1)` marks managed groups.
  (static:static/goal-exe/code/seg_1771_10.asm:983)

### 8. The table sort, points and ties (`1771:8757`, `82BD`, asm seg_1771_12.asm:205-556 and 685-779)

- `8757` runs for stages in `CS:8737` = {2, 3, 5, 7}: continents 1..`DS:1110[stage == 7]` (= 4, or 1 at stage 7), groups 1..`DS:1112[stage == 3]` (= 8, or 2 at stage 3); table 0 (A) or 1 (B): `1771:59D8` tests the stage against `CS:59B8` = {3, 4, 7, 8} (bytes `98 01 00 ...`, all 32 decoded by `sets.py`, `out/sets.txt`; byte 1 bit 0 is stage 8) and adds `0x700` for members; since `8757` itself only runs for {2, 3, 5, 7}, stages 3 and 7 sort the B table, 2 and 5 the A table (4 and 8 never reach the sort; 60CB's use of 59D8 is likewise limited to the announced stages {2, 3, 5, 7}).
  (static:static/goal-exe/code/seg_1771_12.asm:685) (static:static/goal-exe/code/seg_1771_08.asm:735)
- **`82BD` rebuilds a group from scratch** (asm 82D6-8476): the 6 bytes (+2..+7) of each slot are zeroed; then for the **last 12 words of the country's fixture list** (`DS:A92F + 0x48 country`, entries 25..36) each non-zero number whose record has **kind == the stage byte** and **+0 < 0xFE (played)** is added:
  win -> +2 (wins) and **2 points**, draw (`rec[1] == rec[0]`) -> +3 and **1 point**, loss -> +4 and 0; +5 += own goals, +6 += goals against, +7 += points (asm 8322-8464). **Points are 2-1-0** (not stated by the help file). The window holds 12 entries, which the stage 2 count (12) fills exactly.
  (static:static/goal-exe/code/seg_1771_12.asm:221) (static:static/goal-exe/code/seg_1771_12.asm:318) (static:static/goal-exe/code/seg_1771_12.asm:345)
- **Sort** (asm 8476-85F1): an exchange sort: for i = 1..3, j = i+1..4, the slots swap (`214B:007B`, 8 bytes) iff `pts[j] > pts[i]`, or equal points and `GD[j] > GD[i]` (GD = GF - GA as a signed 16-bit difference), or equal GD and `GF[j] > GF[i]` (`84B4`, `8536`, `85B2`). **There is no further key and no random call**: the equal slots keep the order they have (the exchange sort is not stable: a later slot can pass an equal one only by swapping with a third, so equal teams may end in the opposite order).
  The help file's "finally a coin" is not in the code: **segment 1771 contains no call of the coin `214B:06FA`** (no occurrence in `asm/seg_1771_*.asm`). The only randomness in the tie is the slot permutation of the draw (3) which fixes the starting order.
  (static:static/goal-exe/code/seg_1771_12.asm:420) (static:static/goal-exe/code/seg_1771_12.asm:474) (static:static/goal-exe/code/seg_1771_12.asm:525)
- The table is re-sorted in place after every fixture; slots 1..2 of each group at the end of the stage are read by the next builder (6B55 slot 1 .. 4, 6E59 slots 1-2, 7090 slot 1, 71B2 slots 1-2, 74BE slots 1-2).
  (static:static/goal-exe/code/seg_1771_10.asm:59)

### 9. Hosts, the bracket, the decider set and the start stage

- **Hosts**: continental = the winner of a uniformly random qualifying group of that continent (4); World Cup = the winner of a random qualifying group of Europe or America (7). Hosts are chosen **at the build of the finals stage, after qualifying**, from the qualifiers (help: P54); there are no exemptions (the draw has no input but the groups' results). `000E:60CB` announces the host: it is called by `play_round` (seg_000E_09.asm:534) when the stage is in `CS:7099` = {2, 3, 5, 7} (set at seg_000E_09.asm:471, test :502), and reads `[A923]+0x40` (seg_000E_08.asm:33), then `[A923]+0x36` at class 1 (:36) or `[A923]+0x2C + 2*continent` at class 0 (:41-43). Only this host read was checked; the rest of the routine (news text, group and opponent lines) was skimmed in the named view, not audited.
  Host fixtures put the host as side B (`5E3A`: `if (param_4 == host) swap`): which side is the home side on the pitch is not read here.
  (static:static/goal-exe/named/seg_000E_05.c:4) (static:static/goal-exe/code/seg_1771_09.asm:123)
- **Last 16** (`74BE`, `+0x3D == 4`, asm 74DF-7537): for i = 1..8, **winner of group i v runner-up of group 9-i** (default operands before the host swap: side A the runner-up, side B the winner; if the runner-up is the host, `5E3A` swaps them, so the record is then A = the group winner, B = the runner-up/host; seg_1771_09.asm:127-141, called with the host at seg_1771_10.asm:1028-1029), kind 8: A-H, B-G, C-F, D-E, E-D, F-C, G-B, H-A. `[A923]+0x2A := [+0x28]` first.
  **Quarter-finals** (`+0x3D == 3`, kind 200): for i = 1..4 the winners of last-16 fixtures 2i-1 and 2i: (A-H v B-G), (C-F v D-E), (E-D v F-C), (G-B v H-A) (default operands before the host swap: A the second fixture's winner, B the first's; the same `5E3A` swap applies when the A operand is the host, call with the host at seg_1771_10.asm:1075-1076). The same default-order-with-host-exception holds for every fixture written through `5E3A` (stage 3 kind 3, stage 4, stage 7, stage 8), and not for the directly written ones (stages 2, 5, 6, friendlies); the pairings themselves do not depend on it.
  **Semi-finals** (`+0x3D == 2`, kind 0xC9 = 201): winners of quarter-finals (1, 2) and (3, 4). **Third place** (kind 0xCA = 202): the two semi-final losers; **final** (kind 0xCB = 203): the winners (`+0x3D == 1`).
  The captions at `2581:2EFF..32E0` list the same last-16 pairs in the same order; the block `2581:3724..382E` (A H B G C F D E) is consistent with the first two quarter-finals' groups (an inference from string order; those strings were not traced to the screen routine).
  **Line of each branch of 74BE** (seg_1771_10.asm): entry 987; host `[+0x36]` read 996; `+0x3D == 4` test 1000, `[+0x2A]` := `[+0x28]` 1003-1007, loop with the two operand pushes 1016 and 1023, kind 8 push 1024-1025, host push 1028, `5E3A` call 1029, loop test 1030-1031, jump out 1032; `== 3` test 1034, quarter-final loop from 1041 (kind 200); `== 2` test 1081 (kind 0xC9); `== 1` test 1128, third place (0xCA) call 1163, final (0xCB) call 1195.
  (static:static/goal-exe/code/seg_1771_10.asm:1000) (static:static/goal-exe/code/seg_1771_10.asm:1034) (static:static/goal-exe/code/seg_1771_10.asm:1081) (static:static/goal-exe/code/seg_1771_10.asm:1128) (static:static/goal-exe/strings.tsv:867)
- **The decider set `DS:693A`** (C-COMP-07): the 32 bytes at `DS:693A..6959` are `10 FF x24 0F 00 x6` (ds_2581_03.hex; `tables.txt`). `23E4:08DF` tests element e as bit `e & 7` of byte `e >> 3` of the set (asm seg_23E4_01.asm:1052-1068, no bound check, so the set is exactly 32 bytes): `0x10` is bit 4 of byte 0 = element 4; `FF x24` = 8..199; `0F` = 200..203. **The set is {4, 8..203}**, the same shape as `DS:0F3E` = {3, 4, 7, 8..203} (`98` -> 3, 4, 7). F015's "{0x10}" takes the first byte for the set's value; it is the set's element 4. Used at `0791:A405` and `0791:1382` (sets `DS:7C36`, the shoot-out gate) and at `0791:B176` (silent results' extra time, `B15F`).
  The kinds the builders write are 1, 2, 3, 5, 6, 7 (never in the set), 8, 101..103, 200..203 (all in it); **kind 4 is never written**. So extra time and the shoot-out exist for the continental semi-finals, third place and final and for every World Cup knockout match, and for nothing else.
  (static:static/goal-exe/code/seg_23E4_01.asm:1052) (static:static/goal-exe/code/seg_0791_17.asm:179) (static:static/goal-exe/code/seg_0791_18.asm:397) (static:static/goal-exe/code/seg_0791_02.asm:1080)
- **Start stage** (C-COMP-02): `init_new_game` (`1771:9B85`, asm seg_1771_14.asm:391-427): year `[+0x3A] = DS:A9FD + 1`, incremented again if odd; `[+0x38] = 0`; class `[+0x40] = ([+0x3A] mod 4 == 2)`; stage `[+0x3C] = DS:118E[class]`; `DS:118E` = `02 05` (ds_2581_01.hex row 1180). So **a new game starts at stage 2 when the start year is a multiple of 4 and at stage 5 when it is 2 mod 4** (the first stage built is then 6730, class 0 or 1).
  (static:static/goal-exe/code/seg_1771_14.asm:391) (static:static/goal-exe/code/seg_1771_14.asm:427) (static:static/goal-exe/data/ds_2581_01.hex)

## Method

Static first (CLAUDE.md rule 22), never run. Read in this order: the named view (`seg_1771_05.c`, `seg_1771_07.c`, `seg_1771_04.c`, `seg_000E_05.c`, `seg_0791_10.c`), then
the raw listing for every site cited (the decompiled view agreed with the listing on every branch and offset checked; one difference: the decompiled `85F7` shows the coin term
`bVar1 == bVar2 && odd` as a live disjunct, and the listing shows no path reaches it; argument order of the calls was read from the pushes). Tables were read from the committed
data-segment dumps by `dsbytes.py` (a Pascal set is 32 bytes; element e is bit `e & 7` of byte `e >> 3`, listing `23E4:08DF`), and the builders' loops were re-run over them (`counts.py`) to count the fixtures,
check each schedule row is a double round robin, and compare the totals with `DS:6936`. The draw shuffle's distribution (`shuffle.py`) is exact enumeration of the loop at 6804-6846, assuming `214B:06B1` is uniform.
Why no run: nothing asked here needs the game, the rules are branches and tables, and the cheap check (the counts against the data image) came out exact. A run of one new game and of the fixture list at each stage would corroborate the pairings and the first-cycle behaviour; not made.

## Observations

1. `DS:6936` = `01 00 51 05` -> 1 and 1361; the loops write 1360 (class 0) and 1040 (class 1) fixtures (`counts.txt`).
2. All 11 schedule rows of `DS:0F86..108D` are complete double round robins of 4 teams (`tables.txt`).
3. `DS:693A` = `10 FF x24 0F 00 x6`; `DS:0F3E` = `98 FF x24 0F 00 x6` (`tables.txt`).
4. `DS:118E` = `02 05`. `DS:1106` = `05 07`, `DS:1110` = `04 01`, `DS:1112` = `08 02`, `DS:1104` = `0C 06`.
5. 4 swaps of two uniform positions: P(stays) = 0.4019 = 1/8 + 7/8 x (3/4)^4 (`shuffle.txt`).
6. Segment 1771 has no call of `214B:06FA`.

## Inferences

- Pot formation as "the 8 best of the continent by the order table" rests on the order table being the arrays `63A4` sorts by points (F017); the first-cycle order is `GOAL.DAT`'s (F007), not read here.
  (static:static/goal-exe/code/seg_1771_08.asm:446)
- That group slot 1 is the winner depends on `8757` having run after the last fixture of the stage: `route_fixture` calls it after every fixture and at the end of the list (`000E:6CA7`), read, not seen.
  (static:static/goal-exe/code/seg_000E_09.asm:400)
- "Side B is the host" is the record order; whether B is the home side on screen is not established.
  (static:static/goal-exe/code/seg_1771_09.asm:123)

## Alternatives considered

- The coin-shaped branch in 85F7 could be a compiler artefact of `(a > b) or ((a = b) and (c <= d))`; the listing's `jae` at 8707 is what runs, and the branch below it cannot be entered.
- A non-stable exchange sort could be intended as a coin; the code draws no random value, so the starting order (the slot permutation) is the only chance in the tie.

## What this does not establish

- Nothing was run: the pairings, the unreachable coin and the 2-1-0 points are `read`. A fixture-list transcription of a new game and of the play-offs would corroborate.
- The initial order arrays `DS:9BFD`/`9C7E` (from `GOAL.DAT`) and the draw's `214B:06B1` uniformity.
- The friendlies' pairing tables `DS:10C6`/`10D5` are decoded as a function of the loop indices, not interpreted as football (which continents meet).
- Extra time's length and the shoot-out itself (C-COMP-17); the top-scorer table layout (`DS:A93F`); who the home side is (C-COMP-21); `000E:60CB`'s news text beyond the host and group lines.
- `[A923]+0x14` (6 bytes cleared at each 6730 build): purpose not read.

## Where the evidence is

`experiments/E023-competitions-structure/` (scripts and outputs, hashes in `notes.md`); `static/goal-exe/code/seg_1771_09.asm`, `seg_1771_10.asm`, `seg_1771_12.asm`, `seg_1771_08.asm`, `seg_1771_14.asm`, `seg_23E4_01.asm`, `seg_0791_17.asm`, `seg_0791_18.asm`, `seg_0791_02.asm`; `static/goal-exe/data/ds_2581_01.hex`, `ds_2581_03.hex`; `static/goal-exe/named/seg_1771_05.c`, `seg_1771_07.c`; `static/goal-exe/strings.tsv`.

## Verdict per spec row

| Row | Verdict | Deciding line | Uncertainty |
| --- | --- | --- | --- |
| C-COMP-02 | confirmed | `seg_1771_14.asm:391-427` (year, parity, `DS:118E[class]`), `DS:118E` = `02 05` | read |
| C-COMP-04 | confirmed; narrowed for stage 3 | `run_stage` (seg_1771_11.asm:6-49) and the kinds written by each builder; gate `CS:81E8` = {2, 3, 5, 7}. Only B1/B2 play kind 3 at stage 3; stage 4 plays the semi-finals, third place and final | read |
| C-COMP-07 | confirmed, and F015 corrected | bytes `10 FF x24 0F` and `23E4:08DF` (seg_23E4_01.asm:1052-1068): the set is {4, 8..203}; kind 4 never written | read (the bytes exact) |
| C-COMP-08 | narrowed: gate and call structure confirmed, the rest not re-read | read in this task: `D47E` (seg_0791_21.asm:489-570) makes 12 attempts (`D4BA`-`D4BE`), sets the winner byte 2 when level else side B iff its score is higher (`D4D3`-`D4FB`), asks `B15F` (`D504`; seg_0791_18.asm:385-410: kind in `DS:693A` and level), then 4 more attempts (`D50B`-`D50F`) and, if still level, the coin `214B:06FA` into byte +3 (`D52A`-`D532`); the calls in `D47E` include no shoot-out routine. So the gate is {4, 8..203} = kinds 101..103, 8, 200..203 in practice. NOT re-read: that 12 + 4 = 16 equals `DS:0A8A[1]` (F012), `roll_quick_goals`' internals, and the callers after `D47E` in `6970` | read |
| C-COMP-12 | confirmed | 6730 pairs (double round robin of 4, 12 matches per group), 6B55 A->B (winners to B1/B2, single round robin), 6E59 (semi-finals, third place, final); 32 per continent (`load_countries`) | read |
| C-COMP-14 | confirmed; the play-off tie rule refuted | 71B2 7208-7336 (Europe 16, America 8, play-off winners 4 + 4); 7090 (4 pairs per continent); 85F7 `8707 jae` | read |
| C-COMP-15 | confirmed, with the bracket | 71B2 (48 kind-7 fixtures, `DS:10BC`), 74BE 74DF-76AA (slots 1-2, kinds 8, 200, 201, 202, 203) | read |
| C-COMP-16 | confirmed for the last 16; the quarter-final reading narrowed | `74BE` pairs winner i v runner-up 9-i (A-H ... H-A); quarter-finals pair last-16 fixtures (1,2) (3,4) (5,6) (7,8). The strings at `2581:3311..` were not decoded and are not used; block `3724..382E` is only consistent with that reading (string order, not traced) | read for the pairing; inferred for the labels |
| C-COMP-18 | first three keys confirmed; the coin refuted | `82BD` 8476-85F1 (points, GD, GF); no `214B:06FA` in segment 1771; play-off aggregate decided by total then by the leg-2 v leg-1 first-side scores (no coin: the parity branch is unreachable, `85F7` 86F0-8723; the help file's coin is not what the listing does) | read |
| C-COMP-19 | resolved: 2-1-0 | `82BD` 8322-8464 (`shl 1` + draw flag, +7 += points) | read |
| C-COMP-20 | narrowed; rules found | hosts: `6B55` 6B75-6BA4, `71B2` 71C5-71FA; seeding: pots of 8 in the order table, weak shuffle (P(stay) 0.40), World Cup groups from qualifying indices without ranking input; `60CB` announces only | read; draw odds computed |
| C-COMP-24 | confirmed; +3 and the numbering added | `5D94` (seg_1771_09.asm:63-122), `5D02` (:6-62); records 1..2400 + aggregates 2401..2408 | read |
| C-COMP-25 | confirmed; counts and corrections | 384 + 384 (stage 2), 384 + 256 (stage 5); the pair table starts at `DS:0F86` (not `0F54`, whose bytes belong to the set `0F3E`'s tail and strings); no dates; per-team fixtures 12 and 10 | read |

New rows proposed: **C-COMP-29** the group table sort (2-1-0 points, GD, GF, exchange sort, no coin; 82BD); **C-COMP-30** the stage-6 aggregate rule (total, then leg-2 v leg-1 first-side scores; unreachable coin; 85F7);
**C-COMP-31** the draw (pots of 8 by order table, weak shuffle, slot permutations; 6730); **C-COMP-32** the finals-group formation (6B55 A->B, 71B2 composition); **C-COMP-33** the host rules; **C-COMP-34** the fixture counts and numbering (1360 / 1040, aggregates 2401..2408).
