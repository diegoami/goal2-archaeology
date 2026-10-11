# E020 notes: the static map of player +0xC, +0xD and +0xE inside a match (Q018, T36)

Static first (U32). Line numbers are physical lines of the instruction listings under
`static/goal-exe/code/` (file named per row), not decompiler lines. Behavioural corroboration is the
original binary run in Unicorn (E010's half-time image as code and data); no DOSBox-X run was taken
(see "Corroboration" below).

## 1. Method and limits

- **The inventory.** Every direct access to a player record's +0xC/+0xD/+0xE is the exhaustive scan of
  E017 (`experiments/E017-q015-energy/inventory.py`, re-run here: it prints the same routines; its
  classification of pitch, scorer, manager and runtime-object false positives is E017 `notes.md`
  "Reader/writer inventory" and is not repeated). A second grep for the other addressing forms
  (`[bx|si|bp + 0xc|0xd|0xe]` with any segment override) found only runtime-library objects
  (`seg_214B_02.asm`, `seg_23E4_01.asm`, `seg_2382_01.asm`: far pointers or unrelated bytes), no player
  access. Limit: a player record reached through a pointer computed some other way (an `add di, reg`
  with the offset in a register) would not show in either scan.
- **Engine membership.** `reach-001.txt` (from `reach.py`) is the call tree of each engine root from
  `static/goal-exe/calls.tsv`: `0791:D733` (quick) and `0791:9564` (watched sweep), with the pause
  screens `0791:9372`/`0791:ED8A` cut. Limit: `calls.tsv` has direct near and far calls only; an
  indirect call or a jump table is invisible. A routine "inside a tree" means some call chain reaches
  it, not that every match takes that chain.
- **Probes of the original.** `probe_original.py` runs the original `1771:377E` and `0791:278A` on
  literal records (records `strength-001`, `-002-fitness`, `contest-001`, `-002-events`,
  `-003-fitness`); `probe_halves.py` runs the original's whole quick second half on edited states
  (`half-*`). `check_condition.py` compares `runtime/model/condition.py` with all of them.
  `strength-001` and `contest-001` put their literal records at player words 3000..3171, which lie
  past the 3061-record array (`DS:A91B`, 0xEF24 bytes, `runtime/driver/players.py`) but below the
  word where `mul 0x14` wraps 16 bits (3277): the original read the bytes the probe wrote there.
  Later records use words inside the array (2800..2992).

## 2. Who reads +0xC (form), +0xD (fitness), +0xE (energy) in a match

`+0xC` is read signed (`cmp ... 0x20` is `jge`/`jl`, `cwde` sign-extends), `+0xE` is read signed
(`cmp byte ptr [+0xe], 1` with `jge`/`jle`, `cwde`). A player is "available" when signed `+0xE >= 1`
(`1771:3216`, `seg_1771_05.asm:201`), so +0xE of 0 (injury, F018) and 0x80..0xFF (negative) both make a
player unavailable.

### 2a. Quick engine (`0791:D733`)

| # | Routine | Lines | Field and arithmetic |
| --- | --- | --- | --- |
| Q1 | `1771:377E` strength | `seg_1771_05.asm:777` (calls 3216 first: 0 when unavailable), `:785` +0xE read, `:791` `add ax, 0xffc2`, `:795-801` +0xC `cmp 0x20 / jl`, `idiv 16`, `sub`, `:805-807` +0xC `cwde`, `add`, `:809-818` clamp 0..0x100, `:819-827` wrong foot halves | `v = (+4) + s8(+0xE) - 0x3E`; then `+0xC < 0x20 (signed)`: `v += s8(+0xC)`, else `v -= v idiv 16`; clamp to 0..0x100; halved when `3179` says the wrong foot. **Fitness +0xD is not read.** |
| Q2 | `1771:0BC4` line sums | `seg_1771_02.asm:187` (`call 0x377e` per squad word), `:189-192` (added when nonzero, plus the manager share) | called for BOTH sides at the start of every D733 (`seg_0791_21.asm:831,837`): the sums are recomputed from the live +0xC/+0xE each minute (F012). |
| Q3 | `0791:D733` energy loop | `seg_0791_21.asm:1165-1184` | every fifth minute (`831B mod 5 = 0`, `:1167`): signed `+0xE > 1` (`:1181 cmp byte ptr [+0xe],1`) decrements by 1 (`:1184`). Read and written; no +0xD. |
| Q4 | `0791:6443` goal, `0791:65FE` after-goal swing, via `0791:7CC5` | `seg_0791_13.asm:496` (+0xC read, `s8`), `:510` write, `:514` second read for the persisted copy | `+0xC := clamp(s8(+0xC) + delta, 1, 255)` (F012, F019/F020). Writes only; the read feeds the clamp. |
| Q5 | `0791:8062` substitutions | `seg_0791_13.asm:1019` (`cmp byte ptr [+0xe], 0` / `jle`) | a player is a candidate only when signed `+0xE > 0` (and the other tests of F012); `0791:C88D` `seg_0791_20.asm:687` (`cmp byte ptr [+0xe], 1 / jge`) takes the forced-removal path when `+0xE < 1`. No +0xC/+0xD. |
| Q6 | `0791:BD03` via `BD83` via `C173` | `seg_0791_19.asm:554,566` (`call far 1771:377E`) | after a goal the computer's tactics compare the two sides' 377E sums (F012): the same strengths, a second consumer. |
| Q7 | `0791:D5C1` foul roll (competitive fixtures only: `9A3D != 0`) | `seg_0791_21.asm:712` and `:720` (`call 0x1278a` at D688/D696), `:723` (`jb`) | `278A(side-a slot, 10)` against `278A(side-b slot, 3)` (unsigned compare): the watched blend below, read by the quick engine in a non-friendly match. **Not modelled** (`quick_engine.FoulPathNotModelled`); static reading only. |
| Q8 | `0791:9A32` half-time step | `seg_0791_16.asm:370` (+0xE read for the set test), `:378` (+0xE write) | `+0xE := +0xE + 2` when `+0xE` is in 1..30 (F018 s3). |

Not the same engine, same readers: `0791:D47E` (called only from `000E:6970`, `reach-001.txt`) runs
`0BC4` twice (`seg_0791_21.asm:507,514`) and `B19D(12)` (`:515-517`) - the one-shot result of a
fixture the owner does not play - so Q1/Q2 decide those results too (static reading; not run).

### 2b. Watched engine (`0791:9564`)

| # | Routine | Lines | Field and arithmetic |
| --- | --- | --- | --- |
| W1 | `0791:278A` skill of a pitch record, every skill read; callers `1FDD, 287C, 34C1, 3B15, 3EF8, 47C5, 5474, 5B36, 690C, 9ED3, D5C1` (`calls.tsv`; in the 9564 tree: all but `9ED3` and `D5C1`, `reach-001.txt`) | `seg_0791_04.asm:860-866` (form `cmp 0x20 / jge`, `inc`), `:872-880` (element `>= 0xC` adds 0x20, else `cwde` of +0xE added), `:885` (`3A06` skill), `:888-896` (pitch +0x13 halves), `:902-906` (`mul`, `xor dx,dx`, `div 0x100`), `:909-928` (keeper extra), `:929-936` (`+ value/16` for the home side) | `base = (s8(+0xC) < 0x20 ? s8(+0xC) + 1 : 0) + (element >= 0xC ? 0x20 : s8(+0xE))`; `skill = 3A06(...)` (halved when pitch+0x13); `value = ((base * skill) mod 65536) div 256 + skill div 4` (+ pitch+0x11 on the keeper gates, + value div 16 for the flagged side). `287C` turns it into `rand(value div 32 + 1)`. **Fitness +0xD is not read.** |
| W2 | `0791:2B7B` called by `4A28` | `seg_0791_05.asm:220` (+0xE read) | `random-is-one(0x21 - s8(+0xE))` (06D0): true with probability 1/(33 - E) when 33 - E >= 1; `4A28` (`seg_0791_08.asm:480-481`, the call and its test; `:496-500`, `4A5C jne 4A7B` then `call 4354`) goes to `4354` on a true. |
| W3 | `0791:4A28` marking | `seg_0791_08.asm:561` (`4B04`) | `rand(6) < s8(+0xE)` (`cmp ax,dx / jle`): the player follows a marking target only if E exceeds a 1..6 draw; at E <= 1 never (draw >= 1). |
| W4 | `0791:5049` | `seg_0791_09.asm:353` (`5311`) | `random-is-one(s8(+0xE) idiv 2)` (06D0) after a coin; true leads to `4E28` (its role is not examined here). |
| W5 | `0791:8AE9` update | `seg_0791_14.asm:1066` (`cmp [+0xe], 1`), `:1069` (`dec`) | counter > 180 and `DS:8325 != 0`: signed `+0xE > 1` decrements by 1 (F018). |
| W6 | `0791:7D56`, `7B77`, `6443`, `65FE` via `7CC5` | `seg_0791_13.asm:587` (+0xE := 0, the injury), `:496,510,514` | injury writes E := 0, then `7CC5(..., -2)`; the same +0xC writes as Q4. |
| W7 | `0791:8062`, `0791:C88D`, `0791:3216` | as Q5; `3216` lines as above | substitutions and availability. |
| W8 | `1771:377E` through `0791:BD03` only | `reach-001.txt` ROOT 9564: `377E <- BD03 <- BD83 <- C173 <- 65FE <- 67B6 <- 690C <- 83A2 <- 9564` | the watched engine takes the 377E strengths ONLY to compare the two sides after a goal (computer tactics). `1771:0BC4` is not in the 9564 tree. |

### 2c. Display only (reached through the pause or team screens, not match arithmetic)

`1771:13D0` (`seg_1771_02.asm:1046-1077`) adds `min(s8(+0xC), 0x20)` (`214B:0D1C`, `:1055-1056`) into
`DS:9B5A`, `+0xD` (only for signed `+0xE > 0`, `:1061-1063`) into `DS:9B5C`, `+0xE` into `DS:9B60` (`:1075-1077`); its only caller is
`1771:157D` (the team panel), called from `1771:1981`/`26B9`, and `1981` from `0791:ED8A` (the wait
screen of the half-time and pause menus) and `000E:7439`. `1771:42BC` (the player screen) and
`1771:2E20` (the injured colour) read them for bars and words. `reach-001.txt` shows `13D0` outside
both engines' arithmetic trees.

## 3. The claims F021 relies on

- **C1. Fitness (+0xD) is read by no match arithmetic.** In a match, the fitness byte is read only by
  `1771:13D0` (`seg_1771_02.asm:1061`, a team-panel total, display), `1771:42BC` (the player screen)
  and, outside a match, by the recovery/redraw routines and `0791:CB7D` (`seg_0791_20.asm:1031`, the
  after-match copy of +0xD to a positive +0xE), `1771:3558`/`3651`. Neither 377E (Q1) nor 278A (W1)
  reads it, which the original code confirms: `strength-002-fitness` and `contest-003-fitness` vary
  +0xD over 0, 1, 0x10, 0x20, 0x7F, 0x80, 0xFF and the original returns one value per (form, energy).
  Fitness reaches a match only as the energy it is copied to at the end of the previous one.
- **C2. Energy (+0xE) and form (+0xC) are read by the quick engine only through 377E (Q1), every
  minute; and by the watched engine through 278A (W1) in every skill read, plus the three
  energy-only gates W2-W4.**
- **C3. Team morale `DS:9B5A` reaches no match code.** `static/goal-exe/datarefs.tsv`: `DS:9B5A`,
  `DS:9B5C`, `DS:9B60` are referenced by `1771:13D0` and `1771:157D` only; a grep of every
  listing for `0x9b5a|0x9b5c|0x9b60` finds `seg_1771_02.asm:1012,1056,1090-1094` (13D0 writing) and
  `seg_1771_03.asm:246,303` (157D drawing it: `1733 mov di, [0x9b5a]` indexes the word table
  `DS:78A3` for the label, `17B8 mov ax, [0x9b5a]` scales it to the bar). `157D` is reached from the
  team screens (`1981 <- ED8A / 7439 / 26B9`), not from any arithmetic routine. F020's "display only"
  is confirmed.
- **C4. +0xC and +0xE are read signed** (Q1: `cmp ...,0x20 / jl`, `cwde`; W1: `jge`, `cwde`): form
  0x80..0xFF and energy 0x80..0xFF behave as negative numbers. The original confirms all of
  `strength-001`'s boundary rows (energy 0, 1, 2, 0x1F, 0x20, 0x3E, 0x7F, 0x80, 0xFF; form 0, 1,
  0x1F, 0x20, 0x21, 0x3F, 0x7F, 0x80, 0xFF).
- **C5. In both engines the form term stops helping at 0x20.** Quick: `v + s8(+0xC)` below 0x20, then
  `v - v idiv 16` from 0x20. Watched: `s8(+0xC) + 1` below 0x20, then 0. The best form is therefore
  0x1F, not the clamp's 0x20 (`0791:B364` clamps a result/bench/pool change to 1..32, F019).
- **C6. The keeper-extra gate of 278A is the set `{3, 4}` of `DS:8327`, not the value 0x18**
  (`seg_0791_04.asm:843` holds the set bytes `18 00 ...`; `probe_event_gate.py` /
  `event-gate-001.log`: the original adds pitch+0x11 for `DS:8327` = 3 and 4 only). `keeping.py`'s
  `KEEPING_EVENT = 0x18` names the set's byte; `condition.contest` passes the membership instead.
  This is a T27 (F015) defect outside this task; reported.

## 4. Corroboration

- Original `377E` on 193 literal records and original `278A` on 209 literal records, model and original
  equal on all (`check_condition.py`, `match:` line in `check-001.log`).
- Original quick second half on equal-skill states edited by player word, 16 seeds in two scenarios
  (`half-*` records), model and original equal on score, final seed and number of draws.
- No DOSBox-X run was taken: the engines' arithmetic was answerable statically and by running the
  original's own code, which is what a DOSBox-X run of the same edited bytes would execute; the
  behavioural step a DOSBox-X run adds (the game's own loading and display path around the same
  routines) was judged not worth a run from the budget of six.
