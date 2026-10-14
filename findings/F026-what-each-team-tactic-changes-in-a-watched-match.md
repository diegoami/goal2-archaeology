# F026 What each team tactic changes in a watched match: the readers of `26D7`, and the measured effect of one flipped tactic at a time

- **Status**: proposed
- **Question**: Q024, Q025, Q026 (T52, pass one of the wide pass): which routines of the watched engine (`9564` and its callees) read each of the eight team tactics, what do they do with the answer, and how big is the effect on a whole watched match (goals, shots, possession-like counters, fouls, bookings)?
- **Tests claims**: C-TAC-05, C-TAC-06, C-TAC-13, C-TAC-14, C-TAC-16, C-TAC-17, C-TAC-18, C-TAC-19, C-TAC-21 (spec/tactics.md); table in the last section.
- **Experiment and runs**: E026, `experiments/E026-tactics-effect/` (`arm.py`, `queue.py`, `start_state.py`, `analyze.py`, `out/`). Every run is a whole watched match of the E021 harness from E011-r0001's watchstart savestate (Denmark, country 7, engine side 0, against country 19, engine side 1); no DOSBox-X run was taken.
- **Artifact**: set `goal2-a949da2f`; packed GOAL.EXE SHA-256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`.
- **Max intervention**: declared writes into the start state only (I3): the seed word `DS:7B62`, the +0x2D byte of country 7, the delay byte; no hook.
- **Tier reached**: static reading of every reader (V1); the measured table is V2 on one team pair.
- **Confidence**: unreviewed. Static rules are the listing's, cited by line; where a rule is only a reading of the decompiled C that the listing was not re-traced for, it says `read`. What a number in the depth tables means on the pitch (a row offset) is `inferred`.

## Answer

- Every watched-engine read of a team tactic is one of 18 `26D7` call sites in ten routines, or `1771:3EF8` for man to man. The tactics shape a match through three mechanisms: **line depth** (elements 1, 5, 6, 7 set the row offset `pitch +0xC` of each outfield player from tables `DS:07CB`/`DS:07DB`), **the holder's choices** (elements 1, 2, 3: how often he acts, whom he passes to, pass or dribble) and **fouls and marking** (elements 4 and 8).
- Per tactic (Uncertainty in docs/wide-pass.md's words):

| element | reading routines | what they change | measured effect (30 matches, one team pair) | uncertainty |
| --- | --- | --- | --- | --- |
| 1 position | `42CB` (line class), `4532`, `4A28`, `4E28` | push forward lowers the line class of a slot whose side holds the ball; makes wing-backs and wide midfielders dribble instead of pass; defenders follow the ball into the box | stay back: shots for -1.07 +-0.82, goals -0.33 +-0.43 | read (mechanism); measured (small) |
| 2 possession | `5049` | quick pass: the holder acts with chance about 1/2 per update; keep ball only 1/(energy div 2) | keep ball: "possession" bar -7.0 +-0.9 points | read; measured (bar's meaning unresolved) |
| 3 passing | `3111` | long: receiver at least 24 + draw (0..15) away; short: within 2 + draw | long: shots +1.27 +-1.12, on target +0.67 +-0.59 | read; measured (weak) |
| 4 tackling | `4DA9` (from `5513`, `5B36`) | go in hard makes the foul gate certain to roll (hardness against hardness) | avoid injury: own fouls -2.2 +-0.6, own bookings -0.5 +-0.3 | read; measured |
| 5 pitch | `4649`, `4B64` (depth `DS:07CB`), `4A28` (marking follow limit) | full pitch raises the defending depth target (10/5/0 with sag back, 45/25/5 with stand ground) and lets a marker follow into the opponent half | full pitch: shots +1.37 +-1.01 | read; measured |
| 6 defence | `4649`, `4B64`, `5729` | stand ground raises the defending depth target (15/10/2 half pitch); sag back sends a nearby defender at the ball | stand ground: shots +0.7 +-0.9, goals -0.30 +-0.44 | read; measured (not excluded) |
| 7 line | `4532`, `4B64` (attacking depth `DS:07DB`) | offside trap: class 2/3 players' advance target 50/35 instead of 45/25 and class 3 advances without the ball being 30 rows ahead | offside trap: free kicks for +3.4 +-1.0, shots +1.1 +-0.85 | read; measured; link to offside calls inferred |
| 8 marking | `1771:3EF8`, `3E2F` (pairing), `47C5` (destination) | man to man: each outfield slot gets an opponent by position preference tables `DS:0EF4`.., strikers first | zonal: no counter moves detectably | read; measured (no effect seen) |

- What the tables mean on the pitch (a positive offset is toward the opponent) is **inferred**. No effect on **goals** is detectable at 30 matches per arm (every interval contains zero); the large measured effects are on fouls and bookings (element 4), the offside-related free kicks (element 7) and the "possession" bar (element 2).

## Method: static first

Rule 22: the named view (`static/goal-exe/named/seg_0791_03.c`, `_04.c`, `_07.c`, `seg_1771_03.c`) was read first, the listing (`static/goal-exe/code/seg_0791_*.asm`) for the call sites and the data image (`static/goal-exe/data/ds_2581_0*.hex`) for the tables. Runs were made only for the question the listing cannot answer: how large is each effect.

All tactic reads in the watched engine go through `0791:26D7(pitch record, k)` (F010) or, for element 8, `1771:3EF8` directly. Direct byte reads of country +0x2D elsewhere in segment 0791 are the tactics screen (`EFDA`) and `26D7` itself (`seg_0791_04.asm:832`); `214B:0C57`'s other callers (`7EEF`, `8062`, `B27F`, ...) test status bits, not tactics (`calls.tsv`).

### The 18 call sites of `26D7` (watched engine), by element

The element is the `mov ax, k` before each call (script reading the listing; lines are `static/goal-exe/code/`):

| element | tactic (clear / set) | site (routine, return address, listing line) |
| --- | --- | --- |
| 1 position | stay back / push forward | `42CB` (`430E`, seg_0791_07.asm:723); `4532` (`45B4`, `45F6`, :1041, :1074); `4A28` (`4AC3`, seg_0791_08.asm:532); `4E28` (`4EF2`, `4F3C`, :1028, :1065) |
| 2 possession | keep ball / quick pass | `5049` (`52EB`, seg_0791_09.asm:339) |
| 3 passing | short / long | `3111` (`3121`, seg_0791_05.asm:990) |
| 4 tackling | avoid injury / go in hard | `4DA9` (`4DD8`, seg_0791_08.asm:900) |
| 5 pitch | half / full | `4649` (`4686`, :38); `4A28` (`4B17`, :571); `4B64` (`4CE8`, :786) |
| 6 defence | sag back / stand ground | `4649` (`466F`, :26); `4B64` (`4CD5`, :775); `5729` (`5793`, seg_0791_09.asm:883) |
| 7 line | play safe / offside trap | `4532` (`4558`, `4630`, seg_0791_07.asm:998, :1104); `4B64` (`4C78`, seg_0791_08.asm:727) |
| 8 marking | zonal / man to man | not through `26D7`: `1771:3EF8` tests country +0x2D element 8 directly (`seg_1771_03.c`, `set_marking_words`) |

(The quick engine's `D5C1` is the nineteenth site, `seg_0791_21.asm:732`, element 4; C-TAC-15.)

C-TAC-13's ten routines are exactly these, and its element lists are right; the finding adds the eighteen instructions and the structure below.

### The structure: tactics move players' row offsets and the holder's choices

`57AC` is the per-update decision of a pitch record in state 5 (called from `update_player` `8AE9`, `seg_0791_07.c`). With a goalkeeper holding the ball (`045D(DS:830B)` true, `DS:8302` clear) it calls `4B64`; otherwise it sets the destination (the ball, or `update_marking_destination` `4A28`), then `474D`. `4354` turns a destination into `pitch +8 = +0xA + +0xC` (home row plus row offset) and `+7 = +9 + +0xB` (`seg_0791_03.c` 1090-1131; so +9/+0xA are the home column/row and +0xB/+0xC the offsets; **inferred** from the arithmetic, annotated `likely`). Tactics 1, 5, 6, 7 act by setting and stepping the row offset `+0xC`:

- **Line class** `42CB`: 4 for the keeper (position 0); otherwise `DS:07BA[2*(position>4) + f]` = 3, 2, 2, 1, with f = 1 unless (position < 12 and (element 1 clear or the slot is not on the ball's side)). So push forward, for a slot whose side holds the ball, lowers the class by one (more advanced); positions 12-13 are always f = 1. (listing `seg_0791_07.asm` 42CB; data `DS:07BA` = `03 02 02 01 00 05`.)
- **Defending side** (slot not on the ball's side): `4B64` sets `+0xC := DS:07CB[8*e5 + 4*e6 + class]`, bounded by min(2*abs(ball y), 0x2a); `474D` then lowers `+0xC` by one per update through `4649` while `DS:07CB[...] < +0xC` and a position test holds (class 1: the player is 15 rows ahead of the ball; class 2: ahead of the ball; class 3: unless the ball is far ahead). The table (`DS:07CB`, 16 bytes `0E 00 00 00 | 00 0F 0A 02 | 00 0A 05 00 | 00 2D 19 05`) by element 5 (half 0 / full 1) and element 6 (sag back 0 / stand ground 1), classes 1..3:
  - half pitch, sag back: 0, 0, 0; half pitch, stand ground: 15, 10, 2; full pitch, sag back: 10, 5, 0; full pitch, stand ground: 45, 25, 5.
  So the "pressing depth" of the defending side grows with full pitch and, more, with stand ground, most for the most advanced class; sag back with half pitch leaves everyone at his home row. `read` (the table and the compare are the listing's; "row offset toward the opponent" for a positive value is **inferred**, the sign convention of `+0xA` per side was not traced).
- **Side with the ball**: `4B64` sets `+0xC := max(DS:07DB[4*e7 + class], 20)` (`DS:07DB` = `00 3C 2D 19 | 00 3C 32 23`), and `474D` raises `+0xC` by one per update through `4532` while `+0xC < DS:07DB[...]`: class 1 advances when the ball is ahead of the player or element 1 is set or a coin; class 2 when the ball is ahead or element 1 is set; class 3 when the ball is more than 30 rows ahead or **element 7 (offside trap) is set**. So element 7 makes the defenders (class 3) and, via the table, class 2/3 targets 5 and 10 rows deeper (0x32, 0x23 against 0x2D, 0x19) while the team holds the ball; no routine tests an offside condition on the opposite side with element 7. `track_offside_line` (`8CF5`) does not read it (`calls.tsv`: no `26D7` call). The only readers of element 7 are `4532` and `4B64`; the code does not test any offside condition against element 7, so its effect is this advance of the lines and whatever the offside call (`8CF5`) makes of it (measured below). `read`.
- **Element 1 elsewhere**: `4A28` (defending outfield branch, `DS:8325` set): the player follows the ball into the box when `in_own_goal_area` or (element 1 set and `40BC`); `4E28` (the holder's choice, below).
- **Element 5 in marking** `4A28`: after `choose_marking_target` (`47C5`) finds a target and a rand(6) is below his energy, a player with element 5 clear (half pitch) does not follow a target whose row times his attack direction is >= 0 (the target in the half this player attacks); with element 5 set he follows (`seg_0791_04.c` 171-228). `read`.
- **Element 6 in `5729`** (the go-to-the-ball gate in `57AC`): returns 1 for a defending slot that is not a keeper and not on the ball's side when `2EB8` (ball test) holds and (`2EF0` holds or element 6 is **clear**); so sag back sends a nearby defender at the ball, stand ground keeps him unless `2EF0`. What `2EB8`/`2EF0` test (a distance to the ball) was not decoded. `read`.

### Elements 2, 3, 4: what the holder does and fouls

- **Element 2** (`5049`, return `52EB`; `seg_0791_09.asm:323-356`, `seg_0791_04.c` 487-626): for the holder in mid-pitch (row times direction >= -0x14) the action `4E28` fires when (element 2 clear or coin) is false and `random_is_one(energy div 2)` fails -> no action; i.e. **quick pass: the holder acts with probability 1/2 + 1/(2*(E div 2)) each update; keep ball: only 1/(E div 2)** (E the signed energy byte +0xE; E of 20-30 gives 1/10-1/15). This is the strongest direct handle on how long the ball is held. `read`; the update rate of `5049` per tick was not counted.
- **Element 3** (`3111`, `seg_0791_03.c` 82-157): the pass receiver search keeps a team-mate whose Manhattan distance is below `DS:0778[0]` = 2 + draw(0..15) with element 3 clear, and above `DS:0778[1]` = 0x18 + draw with element 3 set (or when `2C54` holds and the passer is not a keeper); coin tie-breaks. So long passes ask for a receiver at least 24 + draw away, short ones within 2 + draw. `read`.
- **Element 4** (`4DA9`, called from `5513` after a lost challenge and from `5B36`): fires when `random_is_one(0x12 - hardness)` is true **or element 4 is set**, then returns 1 iff rand(1..hardness of the ball holder) < rand(1..hardness of the challenger); `5513` then draws a coin between `539F`'s foul line and `watched_substitution_sequence` `8206` (`seg_0791_04.c` 749-775). So go in hard turns the 1/(18 - hardness) chance of a foul-type outcome into certainty of the hardness comparison, with the chance depending only on the two hardness values. Bookings follow by `7EEF`/`798D` (F020) outside this finding. `read`.
- **`4E28`** (what a holder does once `5049`'s gate fires): far forward (row x direction >= 24 + draw, abs(x) > 3) `3DF6`; deep in his own end (row x direction < -8) or a draw of 1: `3323` (pass); else by position: 3, 4: pass if element 1 clear, dribble (`move_ball_to_slot`) if set; 7, 8: dribble if element 1 set and not random_is_one(3), else pass; 10, 11: dribble; 12, 13: pass with chance 1/4 (position 13) or 1/3 (position 12) (`DS:07E4` = 04, `07E5` = 03), else dribble; others pass. So element 1 (push forward) turns wing-backs and wide midfielders from passers into dribblers. `read`.

### Element 8, man to man (Q025)

`1771:3EF8` (`set_marking_words`, called from `230C`, both engines): for each side, slots 2..11 get a marking word `DS:9A3E + 0x28*side + 2*slot`: cleared unless the player has "Protect zone" (+0x10 bit 7); then, if the side's element 8 is set, the opponent's squad word chosen by `3E2F` (`seg_1771_03.c` 641-685, `seg_1771_06.asm:375-455`) or 0. The choice, newly read: own positions of slots 2..11 form a 10-character string (the sweeper, unavailable and Protect-zone players blank); the opponents' positions are an array. `3E2F` is called five times with the opponent position ranges (12..13), (9..11), (5..8), (1), (2..4), i.e. **strikers first, then the attacking midfield and wingers, the midfield, the opposing sweeper, the defenders**; for each call and each preference row r = 1..4, over opponent slots 11 down to 2 whose position q is in the range, it looks up the wanted own position `T[r][q]` (`DS:0EF4 + 14*(r-1) + q`; rows `0D 09 0C 0B 0A 06 05 04 03 02 04 03 02 02` / `0D 0D 0D 08 07 09 06 08 07 05 02 02 03 04` / `0D 0C 09 0D 0D 07 08 0B 0A 04 05 05 04 03` / `0D 0B 0A 09 09 08 07 05 05 03 08 07 05 05`) and, if the first own slot (lowest) with that position is still free, pairs them and removes both. Row 1 for a striker (q 13) is own position 2 (centre back), for q 12 position 2, for q 11 position 3 (left back), for q 10 position 4, for q 9 position 2, q 8 position 3, q 7 position 4, q 6 position 5, q 5 position 6, q 4 position 10, q 3 position 11, q 2 position 12 (a defender is marked by a winger/forward, last). `read` (the listing of `3E2F` and the table are read; the string-search arguments `23E4:06E3`/`075A` were taken to be Turbo Pascal `Pos` and `Chr`, **inferred**, and the construction of the pattern string in `3EF8`'s earlier part was read through the decompiler only).

The marking word is used in the watched engine by `choose_marking_target` `47C5` (`seg_0791_04.c` 89-165): with a nonzero word it finds the opponent's pitch slot, returns 0 when `2C54` holds for that slot, else sets the destination to his position, shifted by `rand(1..n)` rows against the marker's attack direction, with n = (target's feinting - marker's marking) div 16 + 1 when the target's feinting (element 8) exceeds the marker's marking (element 5), else 1. With a zero word (zonal) it looks for any eligible opponent through `4438`. Element 8 has no other reader. `read`.

Automatic assignment, refreshed at each `230C` call: when a team changes; overriding by hand clears the Protect-zone bit rule (C-TAC-19 is the help file's claim; the "clear to zonal at the end of the match" write was not looked for in this task).

### Which players the team byte reaches (the start state)

`out/start-state.json` (read from the savestate, no run): Denmark's squad has +0xF = 0x11 (positions 0, 1, 3, 4: element 1 override set), 0x32 / 0xB2 (the two centre backs, position 2: element 1 override clear, element 2 override set; the first also element 4 clear), 0x00 (midfield and attack) or 0x80 (element 4 override clear). So a **team** flip of element 1 reaches only the players without an element-1 override: positions 5 and up; a flip of element 2 reaches all but the centre backs; element 3 and elements 5-8 reach everyone; element 4 only those without the 0x80 bit. This limits what the arms below can show for elements 1, 2, 4 and is the reason the finding speaks of "the team byte", not "the tactic".

## Measured effects

### Design and budget

- **Pair and start**: E011-r0001's watchstart state: Denmark (country 7, engine side 0, managed, `+0x2D` = 0x8B: push forward, quick pass, go in hard, man to man; positions' override bytes above) against country 19 (side 1, unmanaged, `+0x2D` = 0xC7). The kick-off side was drawn before the saved state, so it is the same in all matches. One pair of teams and one kick-off side: the numbers below say nothing about other pairs.
- **Arms**: base (no change) and eight arms, each flipping **one element of Denmark's byte from the baseline value** (declared write `set_country_tactics`): e1 -> stay back, e2 -> keep ball, e3 -> long passes, e4 -> avoid injury, e5 -> full pitch, e6 -> stand ground, e7 -> offside trap, e8 -> zonal marking. So e1, e2, e4, e8 flip a set element to clear; e3, e5, e6, e7 a clear element to set. Nothing was changed on side 1. All arms use the same 30 seeds (`SEEDS[0..29]`, `DS:7B62` written into the start state, F004; `arm.py`: the first 30 of a fixed `random.Random(52026)` family).
- **N**: 30 matches per arm, 270 matches. Chosen from the CPU budget: the task allows about 8 h; measured on this shared machine (load average 17-24 for the whole batch) a match cost about 93 CPU-seconds (24,175 s over the 275 matches that logged `cpu_seconds`, plus 7 early ones without it), not the 31 s of an idle run, so 200 per arm for 9 arms was out of reach. The whole batch used about 6.9 CPU-hours (282 logged matches: 270 arm matches, one void, the 2 probe matches, and the repeated pairs below). At sd about 1.0-1.3 goals a match the interval on a goal difference is about +-0.7 (30 per arm, 95%); a difference under about 0.6 goals is not detectable, and the 16 arms the task file estimated (200 each) were not run. Arms not measured: the **reverse flip of each element** (only one direction per element), any **combination**, every **other team pair** and **a change during the match** (C-TAC-20 untested), and the opponent's tactics.
- **Outputs**: `out/<arm>-s<first>-<last>.jsonl` (one JSON line per match: score, the nine counters of the full-time board per side, the two bar words, scorers, draw-trace digest, declared writes, wall and CPU seconds), `out/analysis-20261013-final.md` (all 15 measures, every arm, unpaired and paired intervals), `out/start-state.json`, `out/final-tactics-e3-i0.json`. Counters are read raw from the full-time board's rows (E021 notes sec. 4); only the row labels are the listing's, so "possession" and "territory" are **the board's labels, not a decoded quantity** (`DS:80F6+2*side` counts, per ball phase, which half the ball is in; the update site of `DS:80F2` was not found by operand: `80F2`/`80F6` lie inside pitch record 0, `0x80E8`..`0x80FD`).
- **Reproduction**: seeds were run more than once in 10 (arm, seed) pairs in different logs (base 0-2, e5 0-1, e1 0-1 from the probe and `repro-e3-s0-4.jsonl`, 5 matches of arm e3); `analyze.py` refuses to run if a repeated pair differs in score or draw-trace digest, and it did not: the emulation repeats itself seed for seed, as F006 says. One match (e7, seed 54168, `e7-s0-9.jsonl`) ended in an **undeclared key wait** (`214B:08DD` from `214B:098A` at clock 86:15 — a prompt of the original that the harness does not answer, presumably the managed side's injury or sending-off substitution); it is left out (arm e7 has 29), and no other arm had one, so it is not a count of anything.
- **Does the byte survive?** `final_tactics.py` (arm e3, seed 0): side 0's `+0x2D` is 0x8F after the write and still 0x8F at full time (managed side not reset); side 1's stays 0xC7 in that match (`out/final-tactics-e3-i0.json`).
- **Intervals** are 95%, 1.96 standard errors of the difference (Welch), N = 30, so they are rough; the paired-by-seed figure is printed beside but the arms diverge as soon as the byte is read, so it brings little. No correction for 9 x 15 comparisons: about one in twenty of the intervals will miss zero by chance; read only the large ones.

### The table (differences to base; mean of base in the header; side 0 = Denmark, the arm's team)

Base means: goals for 1.27, goals against 1.00, shots for 3.63, shots against 3.47, on target for 2.07, free kicks for 2.93, fouls by us 2.77, bookings us 0.70, possession share 53.8%, territory share 47.8%.

| arm (flip) | N | goals for | goals against | shots for | shots against | on target for | free kicks for | fouls by us | bookings us | "possession" share (points) | "territory" share (points) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e1 stay back | 30 | -0.33 +-0.43 | +0.20 +-0.51 | **-1.07 +-0.82** | +0.30 +-0.90 | -0.37 +-0.53 | -0.13 +-0.88 | +0.53 +-0.91 | +0.37 +-0.46 | +1.7 +-0.9 | +0.6 +-3.1 |
| e2 keep ball | 30 | -0.10 +-0.52 | 0.00 +-0.58 | +0.07 +-1.02 | +0.20 +-0.95 | +0.03 +-0.72 | +0.27 +-0.99 | -0.30 +-0.82 | -0.20 +-0.39 | **-6.96 +-0.85** | -5.2 +-2.9 |
| e3 long passes | 30 | +0.37 +-0.49 | +0.10 +-0.53 | +1.27 +-1.12 | +0.40 +-0.84 | +0.67 +-0.59 | -0.03 +-0.85 | 0.00 +-0.83 | -0.17 +-0.40 | -1.06 +-1.11 | +0.9 +-3.1 |
| e4 avoid injury | 30 | +0.17 +-0.58 | +0.03 +-0.54 | +0.40 +-0.92 | -0.53 +-0.78 | +0.50 +-0.72 | -0.67 +-0.80 | **-2.23 +-0.57** | **-0.53 +-0.33** | +0.15 +-1.03 | -0.2 +-2.4 |
| e5 full pitch | 30 | +0.17 +-0.53 | -0.33 +-0.50 | **+1.37 +-1.01** | -0.33 +-0.81 | +0.73 +-0.69 | +0.20 +-0.91 | -0.30 +-0.77 | -0.07 +-0.40 | -0.21 +-0.99 | -0.5 +-2.6 |
| e6 stand ground | 30 | -0.30 +-0.44 | -0.07 +-0.51 | +0.70 +-0.93 | +0.20 +-0.85 | +0.27 +-0.57 | +0.43 +-0.95 | -0.03 +-0.85 | -0.07 +-0.42 | -1.07 +-0.95 | +0.1 +-2.7 |
| e7 offside trap | 29 | +0.11 +-0.46 | -0.14 +-0.49 | **+1.09 +-0.85** | -0.47 +-0.86 | **+0.73 +-0.61** | **+3.38 +-0.95** | -0.01 +-0.85 | +0.16 +-0.49 | -0.80 +-0.91 | +3.6 +-2.8 |
| e8 zonal marking | 30 | -0.17 +-0.42 | -0.30 +-0.51 | +0.07 +-0.85 | -0.10 +-0.85 | +0.03 +-0.53 | -0.27 +-0.91 | -0.13 +-0.74 | -0.23 +-0.38 | +0.24 +-0.91 | -1.9 +-2.9 |

Bold: an interval that excludes zero. Of the other measures (corners, fouls by them, bookings them, red cards, goal difference) no unpaired interval excludes zero (`out/analysis-20261013-final.md`); red cards are 0 to 4 in 30 matches.

What the numbers say, and no more:

- **No tactic's effect on goals is detectable** at N = 30 (every goals-for and goals-against interval contains zero; goal difference e1 -0.53 +-0.70, e5 +0.50 +-0.73 are the largest). A rebuild cannot take a goal effect from this; it can take the sizes of the other counters.
- **e4 (go in hard -> avoid injury, set to clear)** cuts the side's own fouls by 2.2 per match (2.77 -> 0.53) and bookings by 0.5 (0.70 -> 0.17), the one effect that is large against its interval beyond doubt; consistent with `4DA9` (element 4 removes the "always roll" branch). It also lowers opponents' fouls by 0.27 +-0.33 (not excluded). Its other counters do not move detectably.
- **e7 (offside trap on)** raises **free kicks for the side by 3.4 +-1.0 (2.9 -> 6.3)** with no change in fouls by either side, shots +1.1 +-0.85 and on target +0.7 +-0.6. Free kicks that are not fouls: the remaining source in the engine is the offside call (`8CF5 track_offside_line`, likely), so the reading is that a team that pushes its lines up (the `DS:07DB` rows, above) catches the opponent offside about three times more often. **Inferred**: no commentary of the offside calls was read, and the statistic row is labelled "Free kicks".
- **e2 (keep ball)** lowers the "possession" bar by 7.0 +-0.9 points and the "territory" bar by 5.2 +-2.9, with no detectable change in shots. The direction is the opposite of what the label suggests if the bar counted time with the ball (quick pass = fewer touches per ball), so **what the bar counts is unresolved**; the effect itself (the baseline's quick pass keeps the bar high) is measured.
- **e1 stay back** reduces shots by 1.1 +-0.8 and goals by 0.3 +-0.4 (not excluded); **e5 full pitch**, **e3 long passes** and **e6 stand ground** raise shots by +1.4 +-1.0, +1.3 +-1.1, +0.7 +-0.9 (e5 excluded, the others not).
- **e8 zonal marking** (man to man cleared): no counter moves detectably; "no effect larger than about 1 shot or 0.5 goals a match" is all this supports.
- Whole-match totals stay ordinary under every arm: 0.9-1.6 goals a side; red cards 0-0.14.

## Spec rows tested

| Row | Verdict | Deciding line |
| --- | --- | --- |
| C-TAC-05 | confirmed (match readers) | `26D7` is the reader at all 18 watched sites; direct reads only in the tactics screen (`seg_0791_04.asm:832`, `EFDA`) |
| C-TAC-06 | confirmed by the listing, still not run with an edited +0xF | the 18 sites above; the arms edit only +0x2D. The start state's +0xF show that team flips reach only players without an override (section "Which players the team byte reaches") |
| C-TAC-13 | confirmed and extended | ten routines = the table's sites; adds the 18 instructions and what each does (static section); `4532`/`4649`/`4B64`/`4A28`/`4E28`/`5049`/`3111`/`4DA9`/`5729`/`42CB` are no longer "not decoded" |
| C-TAC-14 | narrowed | `3E2F` read: pairing by position-preference tables `DS:0EF4`-`0F2B` in five range passes (12-13, 9-11, 5-8, 1, 2-4), first free own slot with the preferred position; `47C5` uses the word as a destination with a draw; "the word names the player marked" now `read`, not inferred |
| C-TAC-16 | not tested | no marking counterfactual on energy was run; E026 did not record energy |
| C-TAC-17 | narrowed from unknown to measured for 8 flips on one pair | the table of measured effects; goals not detectable at N = 30 (95% half-width 0.4-0.6 goals) |
| C-TAC-18 | partly confirmed | go in hard -> fouls and bookings (e4); offside trap -> more advanced lines and free kicks (e7); full pitch -> more shots (e5); sag back/stand ground and long passes only weakly (not excluded); quick pass retains more in the bar (e2). "Quick pass retains less" (help) is not what the bar shows, but the bar's meaning is unresolved |
| C-TAC-19 | partly confirmed | automatic pairing exists and skips the sweeper (position 1 is blanked in `3EF8`) and the keeper (slots 2..11 only) and Protect-zone players; manual override and the end-of-match clear not looked for |
| C-TAC-20 | untested | no mid-match change run |
| C-TAC-21 | partly confirmed | `4DA9` rolls the hardness (`player_hardness`, a function of player bytes +3 and +5 per the row) of both players; injuries/send-offs after the foul line (`7EEF`) not read in this task |
| new row proposed | line depth | the depth tables `DS:07BA`, `07CB`, `07DB`, the offset `pitch +0xC` and its steps (`474D`/`4532`/`4649`), read, uncertainty read; meaning of the sign inferred |
| new row proposed | holder's action rate | `5049`: element 2 set gives a coin on top of `random_is_one(energy div 2)`; read |
| new row proposed | pass distance | `3111`: `DS:0778` = 2 / 0x18 plus a draw 0..15 chosen by element 3; read |
| new row proposed | pass or dribble | `4E28` by position and element 1; read |
| new row proposed | foul gate | `4DA9`: `random_is_one(0x12 - hardness)` or element 4, then hardness draw; read |
| new row proposed | measured effects | e2 -7.0 points on the possession bar, e4 -2.2 own fouls / -0.5 own bookings, e7 +3.4 free kicks (N = 30, one pair, one kick-off side); measured |

## Limits

- One team pair, one kick-off side, one direction per element, 30 matches per arm: a rebuild should use the sizes of the large effects (fouls, free kicks, the bar) and treat the rest as `unknown` within the intervals above.
- The managed team's tactics are the arm; the opponent is the computer's, whose tactics react to goals (`C173`, F010) and whose own bytes are not part of the arm. Matches that stop at an undeclared key wait are excluded (1 of 271).
- Depth-table semantics (sign, units) and the counters' meaning are inferred; no per-tick position trace was taken, which would settle both and is the next step (an extra code hook in the harness, about a day).

