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

(See the sections below; the measured table is in "Measured effects".)

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

`57AC` is the per-update decision of a pitch record in state 5 (called from `update_player` `8AE9`, `seg_0791_07.c`). With the ball in flight (`045D(DS:830B)` true, `DS:8302` clear) it calls `4B64`; otherwise it sets the destination (the ball, or `update_marking_destination` `4A28`), then `474D`. `4354` turns a destination into `pitch +8 = +0xA + +0xC` (home row plus row offset) and `+7 = +9 + +0xB` (`seg_0791_03.c` 1090-1131; so +9/+0xA are the home column/row and +0xB/+0xC the offsets; **inferred** from the arithmetic, annotated `likely`). Tactics 1, 5, 6, 7 act by setting and stepping the row offset `+0xC`:

- **Line class** `42CB`: 4 for the keeper (position 0); otherwise `DS:07BA[2*(position>4) + f]` = 3, 2, 2, 1, with f = 1 unless (position < 12 and (element 1 clear or the slot is not on the ball's side)). So push forward, for a slot whose side holds the ball, lowers the class by one (more advanced); positions 12-13 are always f = 1. (listing `seg_0791_07.asm` 42CB; data `DS:07BA` = `03 02 02 01 00 05`.)
- **Defending side** (slot not on the ball's side): `4B64` sets `+0xC := DS:07CB[8*e5 + 4*e6 + class]`, bounded by min(2*abs(ball y), 0x2a); `474D` then lowers `+0xC` by one per update through `4649` while `DS:07CB[...] < +0xC` and a position test holds (class 1: the player is 15 rows ahead of the ball; class 2: ahead of the ball; class 3: unless the ball is far ahead). The table (`DS:07CB`, 16 bytes `0E 00 00 00 | 00 0F 0A 02 | 00 0A 05 00 | 00 2D 19 05`) by element 5 (half 0 / full 1) and element 6 (sag back 0 / stand ground 1), classes 1..3:
  - half pitch, sag back: 0, 0, 0; half pitch, stand ground: 15, 10, 2; full pitch, sag back: 10, 5, 0; full pitch, stand ground: 45, 25, 5.
  So the "pressing depth" of the defending side grows with full pitch and, more, with stand ground, most for the most advanced class; sag back with half pitch leaves everyone at his home row. `read` (the table and the compare are the listing's; "row offset toward the opponent" for a positive value is **inferred**, the sign convention of `+0xA` per side was not traced).
- **Side with the ball**: `4B64` sets `+0xC := max(DS:07DB[4*e7 + class], 20)` (`DS:07DB` = `00 3C 2D 19 | 00 3C 32 23`), and `474D` raises `+0xC` by one per update through `4532` while `+0xC < DS:07DB[...]`: class 1 advances when the ball is ahead of the player or element 1 is set or a coin; class 2 when the ball is ahead or element 1 is set; class 3 when the ball is more than 30 rows ahead or **element 7 (offside trap) is set**. So element 7 makes the defenders (class 3) and, via the table, class 2/3 targets 5 and 10 rows deeper (0x32, 0x23 against 0x2D, 0x19) while the team holds the ball; no routine tests an offside condition on the opposite side with element 7. `track_offside_line` (`8CF5`) does not read it (`calls.tsv`: no `26D7` call). **There is no code in the watched engine that makes element 7 "trap" an attacker: its only effect is this advance of the lines.** `read`.
- **Element 1 elsewhere**: `4A28` (defending outfield branch, `DS:8325` set): the player follows the ball into the box when `in_own_goal_area` or (element 1 set and `40BC`); `4E28` (the holder's choice, below).
- **Element 5 in marking** `4A28`: after `choose_marking_target` (`47C5`) finds a target and a rand(6) is below his energy, a player with element 5 clear (half pitch) does not follow a target whose row times his attack direction is >= 0 (the target in the half this player attacks); with element 5 set he follows (`seg_0791_04.c` 171-228). `read`.
- **Element 6 in `5729`** (the go-to-the-ball gate in `57AC`): returns 1 for a defending slot that is not a keeper and not on the ball's side when `2EB8` (ball test) holds and (`2EF0` holds or element 6 is **clear**); so sag back sends a nearby defender at the ball, stand ground keeps him unless `2EF0`. What `2EB8`/`2EF0` test (a distance to the ball) was not decoded. `read`.

### Elements 2, 3, 4: what the holder does and fouls

- **Element 2** (`5049`, return `52EB`; `seg_0791_09.asm:323-356`, `seg_0791_04.c` 487-626): for the holder in mid-pitch (row times direction >= -0x14) the action `4E28` fires when (element 2 clear or coin) is false and `random_is_one(energy div 2)` fails -> no action; i.e. **quick pass: the holder acts with probability 1/2 + 1/(2*(E div 2)) each update; keep ball: only 1/(E div 2)** (E the signed energy byte +0xE; E of 20-30 gives 1/10-1/15). This is the strongest direct handle on how long the ball is held. `read`; the update rate of `5049` per tick was not counted.
- **Element 3** (`3111`, `seg_0791_03.c` 82-157): the pass receiver search keeps a team-mate whose Manhattan distance is below `DS:0778[0]` = 2 + draw(0..15) with element 3 clear, and above `DS:0778[1]` = 0x18 + draw with element 3 set (or when `2C54` holds and the passer is not a keeper); coin tie-breaks. So long passes ask for a receiver at least 24 + draw away, short ones within 2 + draw. `read`.
- **Element 4** (`4DA9`, called from `5513` after a lost challenge and from `5B36`): fires when `random_is_one(0x12 - hardness)` is true **or element 4 is set**, then returns 1 iff rand(1..hardness of the ball holder) < rand(1..hardness of the challenger); `5513` then draws a coin between `539F`'s foul line and `watched_substitution_sequence` `8206` (`seg_0791_04.c` 749-775). So go in hard turns the 1/(18 - hardness) chance of a foul-type outcome into certainty of the hardness comparison, with the chance depending only on the two hardness values. Bookings follow by `7EEF`/`798D` (F020) outside this finding. `read`.
- **`4E28`** (what a holder does once `5049`'s gate fires): far forward (row x direction >= 24 + draw, abs(x) > 3) `3DF6`; deep in his own end (row x direction < -8) or a draw of 1: `3323` (pass); else by position: 3, 4: pass if element 1 clear, dribble (`move_ball_to_slot`) if set; 7, 8: dribble if element 1 set and not random_is_one(3), else pass; 10, 11: dribble; 12, 13: pass with chance 1/`DS:07E4[position == 12]`, else dribble; others pass. So element 1 (push forward) turns wing-backs and wide midfielders from passers into dribblers. `read`.

### Element 8, man to man (Q025)

`1771:3EF8` (`set_marking_words`, called from `230C`, both engines): for each side, slots 2..11 get a marking word `DS:9A3E + 0x28*side + 2*slot`: cleared unless the player has "Protect zone" (+0x10 bit 7); then, if the side's element 8 is set, the opponent's squad word chosen by `3E2F` (`seg_1771_03.c` 641-685, `seg_1771_06.asm:375-455`) or 0. The choice, newly read: own positions of slots 2..11 form a 10-character string (the sweeper, unavailable and Protect-zone players blank); the opponents' positions are an array. `3E2F` is called five times with the opponent position ranges (12..13), (9..11), (5..8), (1), (2..4), i.e. **strikers first, then the attacking midfield and wingers, the midfield, the opposing sweeper, the defenders**; for each call and each preference row r = 1..4, over opponent slots 11 down to 2 whose position q is in the range, it looks up the wanted own position `T[r][q]` (`DS:0EF4 + 14*(r-1) + q`; rows `0D 09 0C 0B 0A 06 05 04 03 02 04 03 02 02` / `0D 0D 0D 08 07 09 06 08 07 05 02 02 03 04` / `0D 0C 09 0D 0D 07 08 0B 0A 04 05 05 04 03` / `0D 0B 0A 09 09 08 07 05 05 03 08 07 05 05`) and, if the first own slot (lowest) with that position is still free, pairs them and removes both. Row 1 for a striker (q 13) is own position 2 (centre back), for q 12 position 2, for q 11 position 3 (left back), for q 10 position 4, for q 9 position 2, q 8 position 3, q 7 position 4, q 6 position 5, q 5 position 6, q 4 position 10, q 3 position 11, q 2 position 12 (a defender is marked by a winger/forward, last). `read` (the listing of `3E2F` and the table are read; the string-search arguments `23E4:06E3`/`075A` were taken to be Turbo Pascal `Pos` and `Chr`, **inferred**, and the construction of the pattern string in `3EF8`'s earlier part was read through the decompiler only).

The marking word is used in the watched engine by `choose_marking_target` `47C5` (`seg_0791_04.c` 89-165): with a nonzero word it finds the opponent's pitch slot, returns 0 when `2C54` holds for that slot, else sets the destination to his position, shifted by `rand(1..n)` rows against the marker's attack direction, with n = (target's feinting - marker's marking) div 16 + 1 when the target's feinting (element 8) exceeds the marker's marking (element 5), else 1. With a zero word (zonal) it looks for any eligible opponent through `4438`. Element 8 has no other reader. `read`.

Automatic assignment, refreshed at each `230C` call: when a team changes; overriding by hand clears the Protect-zone bit rule (C-TAC-19 is the help file's claim; the "clear to zonal at the end of the match" write was not looked for in this task).

### Which players the team byte reaches (the start state)

`out/start-state.json` (read from the savestate, no run): Denmark's squad has +0xF = 0x11 (positions 0, 1, 3, 4: element 1 override set), 0x32 / 0xB2 (the two centre backs, position 2: element 1 override clear, element 2 override set; the first also element 4 clear), 0x00 (midfield and attack) or 0x80 (element 4 override clear). So a **team** flip of element 1 reaches only the players without an element-1 override: positions 5 and up; a flip of element 2 reaches all but the centre backs; element 3 and elements 5-8 reach everyone; element 4 only those without the 0x80 bit. This limits what the arms below can show for elements 1, 2, 4 and is the reason the finding speaks of "the team byte", not "the tactic".

## Measured effects

(MEASURED-SECTION-PLACEHOLDER)

## Spec rows tested

(TABLE-PLACEHOLDER)
