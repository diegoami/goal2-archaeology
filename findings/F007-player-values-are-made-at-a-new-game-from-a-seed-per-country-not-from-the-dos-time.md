# F007 A new game makes every player's values from a fixed seed per country and the country's ranks, not from the DOS time: all 3061 player records are identical across DOS minutes

- **Status**: proposed
- **Question**: Where and how are player skills and attributes made, given that `GOAL.DAT` holds none (F002 R013), and does a new game's seed change them? (G5 Q004, `docs/backlog.md`; T15)
- **Tests claims**: R013 (where the values come from); bears on R007, R008, R009, R010, R011, on Q005 (country strength), Q007 (the 80 players beyond the squad) and Q009–Q016 (what the fields mean); no spec row exists yet
- **Experiment and runs**: E006; E006-r0001 … E006-r0012 (12 new games: DOS 10:00 three times, r0001, r0011, r0012; 10:01 r0002, 10:02 r0003, 13:37 r0004, 21:00 r0005, 23:58 r0006, 00:00 r0007, 06:30 r0008, 12:00 r0009, 17:45 r0010; all on 10/04/2026)
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Max intervention**: I3 (the DOS date and time set in the autoexec before GOAL runs, verified by DOS's read-back, in all 12; savestates written, I2; memory read from them, I1)
- **Tier reached**: V2
- **Confidence**: unreviewed (status `proposed`). Behavioural: 12 of 12 games give byte-identical player and country arrays over 10 DOS minutes, while `DS:7B62` follows the minute in all 12. Static: `1771:97CC` stores the country number into the LCG's seed word before drawing that country's players. Both routes agree on every claim marked "both" below, so those claims would be corroborated once reviewed. A claim on one route says so.

## Answer

- **The DOS time does not change any player value** (both routes). In 12 new games over 10 DOS minutes, every byte of the 0xEF24-byte player array at `[DS:A91B]` and of the 0x603F-byte country array at `[DS:A917]` is the same across minutes and within a minute (E006-r0001 … r0012; `summarise.py`, the field table and "Country array … 0"). Over the same 12 games `DS:7B62` reads LCG^162(hour·256+minute): ten distinct values, and the same one three times at 10:00, as F004 found. Static: `1771:97CC` writes the country number into the seed word through the far pointer `DS:A978` (`seg_1771_14.asm:18`–`20`: `mov ax, [bp+6]; les di, [0xa978]; mov es:[di], ax`) before its 20 calls of `1771:96D3` (`:65`). The DOS time reaches `DS:7B62` later, through `1771:76B1` → `1771:6730` → `23E4:11D7` (`seg_0000_01.asm:52`; `seg_1771_09.asm:1138`; F004). The main program calls `1771:9B85` (the players) and `1771:2D15` (the managed country) before that (`seg_0000_01.asm:24`–`25`). The backlog's prediction for Q004 ("two new games with different seeds give … different skills") is refuted. I put this at about 95%; the limits are a single DOS date and one managed country (below).
- **What makes players 1..2560** (both routes): at a new game `1771:9B85` → `1771:9A40` → `1771:97CC(c)` for c = 1..128 (`seg_1771_14.asm:393`, `:374`). It seeds the LCG `214B:0688` with c and calls `1771:96D3(player, c, position, 1)` for slots 1..20. The position is GOAL.DAT block 10 (R011) byte `20c + slot − 1` (`:59`–`:65`). A model of `96D3` and its callees, from the listing alone (`summarise.py` `model_player`), gives every byte it writes for all 2560 players in all 12 games: 30720 of 30720 per field, for fields +0..+7, +0xC..+0xF and +0x12..+0x13 (E006-r0001 … r0012; `summarise.py`, "Static model"). The per-field writers are in the table below.
- **What makes players 2561..2640** (both routes): with F001's keys the managed country is country 7 (Denmark; country field +0x2E = 0x81 = 0x80 + manager 1, written by `1771:2D15`, `seg_1771_04.asm:840`). For it `1771:98C4` (called by `2D15`, `:878`) makes 80 more players through `1771:9873` → `96D3(…, 0)` (`seg_1771_14.asm:146`–`253`). It makes positions 0..13 four times each (56 players), then one per squad slot 1..20, with the age redrawn as `DS:118C[gk] + rand(3)` and +4 recomputed (`:189`–`226`), then slots 6..9 again (`:249`). The model reproduces all 80 records' modelled bytes from exactly one 16-bit seed, `0xf5db`, in every game. That seed is one LCG step past the word the last squad (country 128) leaves, so exactly one draw falls between `9A40` and `98C4`. Which routine makes that draw is not established. Players 2641..3060 are all zero at the main screen (E006-r0001 … r0012).
- **What "country strength" means here** (both routes): field +3 is `rating(c) + 0x7F` for every squad player of country c. `rating` is `1771:10E7`, `((5 − [+0x2C]) · (0x21 − [+0x2A]) + (0x81 − [+0x2B])) idiv 2` over the country record (`seg_1771_02.asm:710`–`733`). Behaviourally the per-country mean of +3 against that rating fits y = x + 127.0 with r = +1.000, and the mean of +4 fits y = 0.962x + 120.2 with r = +0.995 (n = 128). Against R007's three bytes |r| ≤ 0.126 for +3 and ≤ 0.123 for +4; against R008, r = +0.066 and +0.068. No routine in the player path reads R008 (`DS:9B7C`, country +0x2D) or R007 (`DS:9D80`): not `96D3`, `3291`, `32EB`, `2FFB`, `3431`, `33CD`, `3558`, `0B77` or `10E7` (their listings, `seg_1771_13.asm:1107`–`1198`, `seg_1771_05.asm:243`–`629`, `seg_1771_04.asm:1100`–`1126`, `seg_1771_02.asm:98`–`733`). So the backlog's "scaled by a per-country value (R007 or R008)" is refuted for the values a new game makes. The country fields the rating reads are ranks: `9A40` stores a country's position in block 8 (R009) at +0x2B. Its position i in block 9 (R010) gives +0x2C = (i−1) div 32 + 1 and +0x2A = (i−1) mod 32 + 1 (F002 O5). The record bytes fit +0x2B as the world rank, +0x2C as the continent and +0x2A as the rank within it. Denmark reads world 29, continent 1, rank 1, as F004's main screen shows "World 29, Europe 1". Germany reads 1, 1, 2, as F004's E003-r0043 shows "World 1, Europe 2". The four continents of 32 are led by Denmark, Argentina, Ivory Coast and Japan. I'd put the naming at about 85%: two screens agree, and the other 126 countries are not checked against a screen.

### The 20-byte player record after a new game

| Field | Written by, from | Range (named; managed) | What it is |
| --- | --- | --- | --- |
| +0x00 | the country argument (`seg_1771_13.asm:1117`–`1119`) | 1..128; 7 (E006-r0001 … r0012) | the country (F002 O5; `players.check` uses it) |
| +0x01 | `DS:118A[gk] − b + a`, with a then b = rand(7) (`:1132`–`1156`; `DS:118A` = 0x1C, 0x1F, `ds_2581_01.hex` row 1180). In `98C4`'s slot loop it is overwritten by `DS:118C[gk] + rand(3)` (0x11, 0x14; `seg_1771_14.asm:201`–`219`) | 22..37; 18..36 (E006-r0001 … r0012) | inferred to be the age, about 75%: years-like values, keepers 3 older, and `98C4`'s squad-slot players aged 18..22 |
| +0x02 | `1771:3291`: `DS:0E80[gk] + b − a`, with a then b = rand(3) (`seg_1771_05.asm:253`–`277`; 0x1B, 0x1E) | 25..32; 25..32 (E006-r0001 … r0012) | inferred to be the peak age, about 70%: +4 is +3 unreduced exactly when +1 is between +2 and +2+3 (next rows) |
| +0x03 | flag 1: `rating(c) + 0x7F` (`seg_1771_13.asm:1163`–`1166`; `10E7`). Flag 0 (`98C4`): `rating(c) + 0x7F − 10 − rand(10)` (`:1169`–`1181`) | 128..253; 221..230 (E006-r0001 … r0012) | a ceiling set by the country's ranks (the Answer). Inferred to be the player's potential ability, about 70% |
| +0x04 | `1771:32EB` from +1, +2, +3. +3 when +2 ≤ +1 ≤ +2+3 (unsigned, `seg_1771_05.asm:297`–`312`). Otherwise `(+3 · k) div 16`, with k = 16 − (+1 − (+2+3)) when +1 > +2+3 (`:328`–`340`) and k = 16 − ((+2 − +1) idiv 2) when +1 < +2 (`:354`–`357`); the low byte (`:361`–`366`) | 88..253; 154..230 (E006-r0001 … r0012) | +3 reduced by distance from the peak. `1771:377E` ("a player's value", F002 map) reads it, so it is inferred to be current ability, about 75% |
| +0x05 | rand(16) (`seg_1771_13.asm:1127`–`1131`) | 1..16; 1..16 (E006-r0001 … r0012) | not established. `2FFB` returns +5 − (+3 and 1) (`seg_1771_04.asm:1113`–`1126`), and +0x0F depends on it |
| +0x06, +0x07 | the position argument: +7, then +6 = +7 (`seg_1771_13.asm:1120`–`1126`) | 0..13; 0..13 (E006-r0001 … r0012) | the position code (R011; F002 O5) |
| +0x08 … +0x0B | not written by the player path | 0 in all (E006-r0001 … r0012) | not established |
| +0x0C | rand(32) (`:1188`–`1190`) | 1..32; 1..32 (E006-r0001 … r0012) | not established. `377E` reads it (F002 map) |
| +0x0D, +0x0E | `1771:3558`: T = `DS:0E82[+1 > +2 + 4]` (0x10, 0x0D; `seg_1771_05.asm:550`, `:569`). If the country is managed (`1771:0B77`: +0x2E > 0x80, `seg_1771_02.asm:108`), v = T + b − a with a = rand(T+1), b = rand(3T) (`:573`–`594`). Otherwise v = T + rand(2T) (`:604`–`613`). Then v is capped at 0x20 (signed compare, `:616`–`619`). +0x0E = v, +0x0D = max(v, 1) (`:624`–`629`) | 14..32; 3..32 (E006-r0001 … r0012) | not established. `1771:3216` reports a player unavailable when +0x0E < 1 (F002 map `377E`, `3216`) |
| +0x0F | `1771:3431` (bit k−1 for Pascal set element k, `214B:0C79`/`0CA1`, `seg_214B_02.asm:450`–`472`). Bit 7 is set and bit 3 cleared when `2FFB` < 4 (`1771:33CD`, `seg_1771_05.asm:384`–`397`, `:419`–`420`). Bits 0 and 4 are set when the position is in {0,1,3,4}, the set constant byte 0x1B at `1771:3411` (`:402`, `:429`–`447`; `23E4:08DF` tests membership, `seg_23E4_01.asm:1065`). Position 2 sets bits 1 and 5, plus bit 4 when +5 < 14 (`seg_1771_05.asm:451`–`477`) | 0..178; 0..178 (E006-r0001 … r0012) | flags, meaning not established |
| +0x10, +0x11 | not written by the player path | 0 in all (E006-r0001 … r0012) | not established. `3216` tests +0x10 against 3, 6 and 8 |
| +0x12 (word) | 0x7FFF (`seg_1771_13.asm:1198`) | 32767; 32767 (E006-r0001 … r0012) | not established |

## Notes on the player record table

Writers are `1771:96D3` and its callees unless the row names another. The gk index is 1 when the position byte is 0 (the goalkeeper; F002 O5 position names) and 0 otherwise. `rand(n)` is `214B:06B1` (1..n, `seg_214B_01.asm:880`–`906`). Draws happen in the table's order, per player. Ranges are over all 12 games. "Named" means players 1..2560, and "managed" means 2561..2640. Every row's writer is from the listing, and the model reproduces it on every named and managed player in E006-r0001 … r0012, unless it says "not written".

## Method

- Machine and tools: as F004 and F005 (Ubuntu 24.04 in WSL2, DOSBox-X 2024.03.01, Xvfb; each record's `runtime.fingerprint`), `cycles=30000`, `svga_s3`, memsize 16. Driver `runtime/driver/driver.py`, array reader `runtime/driver/players.py`, runner `experiments/E006-q004-skills/run.py` (sha256 in each record's `actions`), `code_commit` `c1edac2` in all 12. The records' `actions.args` name a `--dos-time` option that `run.py` does not accept. What each run actually ran is in E006 README amendment 1, which also shows the measurements are unaffected.
- Each record is a fresh launch at the DOS time given on 10/04/2026 (I3; DOS's read-back in the record), then F001's keys `n Enter Enter b o b Enter Enter Enter Enter`, each followed by a settle poll, to the main screen, then Host+S. The savestate is kept and published (below).
- Read from the main-screen savestate: the far pointers `DS:A91B` (`4E5B:000D` in all 12) and `DS:A917` (`4857:000E`), followed in guest memory. The arrays are 0xEF24 and 0x603F bytes, the allocations of `2139:0000` (F002 map). They are located on known values before use (`players.check`, "ok" in all 12): country c (1..128) names players (c−1)·20+1 … c·20 in its first 20 words (`1771:9A40`), and each of them holds c in byte 0 (`96D3`).
- Analysis is `summarise.py`. It does the field-by-field comparison across and within minutes and the ranges. It fits the Pearson r and least-squares line of per-country means (squads 1..128, n = 128) against R007's bytes and R008, read from `GOAL.DAT` through `static/goal-dat/blocks.tsv`, and against the rating `10E7`. It also runs the static model: an LCG seeded with c per country, the draws of `96D3` in listing order, the tables from `ds_2581_01.hex`, and a search of the 65536 seeds for `98C4`'s 80 players.
- Static sources: `static/goal-exe/code/` of unpacked `GOAL.EXE` sha256 `6fd8c5ef…` (`static/goal-exe/README.md`).

## Observations

- `summarise.py` output, abridged:
  - per field +0x00 … +0x13: "equal in all" across minutes and "equal" within 10:00 (three games), for all 3061 players;
  - the country array: 0 (country, offset) pairs differ between any two games;
  - `DS:7B62` at the main screen is 162 LCG steps from hour·256+minute in 12 of 12 (`0xee42` at 10:00 ×3, `0xb24b`, `0x7654`, `0x5e8f`, `0x5142`, `0xcd4c`, `0x9442`, `0xc350`, `0x0042`, `0xa2d7`);
  - the static model gives 30720 of 30720 equal for each modelled field of players 1..2560;
  - for `98C4`, seed `0xf5db` is the only one; the last squad leaves `0x18bc`, one step before it;
  - players 2561..2640 are non-zero, country 7, in 12 of 12, and 2641..3060 are zero;
  - R008 equals country field +0x2D for countries 1..128.
- Per-country means against the inputs (n = 128; r and fitted line), for the fields whose values vary between players:

| Field | R007[0] | R007[1] | R007[2] | R008 | rating `10E7` |
| --- | --- | --- | --- | --- | --- |
| +0x01 | −0.159 | +0.038 | −0.093 | −0.078 | −0.011 |
| +0x02 | +0.252 | −0.236 | +0.200 | +0.031 | +0.027 |
| +0x03 | −0.010 | −0.013 | −0.126 | +0.066 | +1.000, y = 1.000x + 127.0 |
| +0x04 | +0.000 | −0.019 | −0.123 | +0.068 | +0.995, y = 0.962x + 120.2 |
| +0x05 | +0.083 | −0.078 | −0.088 | +0.200 | +0.008 |
| +0x0C | −0.038 | +0.022 | +0.020 | +0.005 | +0.004 |
| +0x0D, +0x0E | +0.118 | −0.080 | +0.072 | +0.049 | −0.091 |
| +0x0F | −0.002 | +0.016 | +0.119 | −0.182 | −0.056 |

  The fields +0x00, +0x06 and +0x07 (country and position) are printed too and are not values.
- Player 1 (country 1) in E006-r0001 reads `01 20 1e a1 a1 0a 00 00 00 00 00 00 08 20 20 11 00 00 ff 7f`. Its country record bytes +0x28 … +0x2F read `1c 50 1c 50 01 f7 01 04`, so the rating is ((5−1)(33−28) + (129−80)) div 2 = 34 = 0xA1 − 0x7F.

## Inferences

- Player values are a function of `GOAL.DAT` (positions R011, ranks R009 and R010) and of which country is managed; no clock or seed input enters them. The basis is the identity across minutes (E006-r0001 … r0012) together with the reseed by country (Answer). A rebuild can make every new game's players with the model of `summarise.py`, given which countries are managed and the one draw before `98C4` (not established; reproduced here by its result, the seed `0xf5db`, for one managed country).
- The "draw" exists, but its seed is fixed: a field equal in every game is still a draw of `214B:0688`. It is drawn at the new game (`9B85` runs on the main program's not-load path only, `seg_0000_01.asm:18`–`24`; `9B85` and `9A40` have one caller each, `calls.tsv`), not at start-up. A loaded game takes the arrays from its file (`1771:027B`, F002 map). All 12 runs (E006-r0001 … r0012) are new games, so none of them observes start-up or a load.

## Alternatives considered

1. *The values are drawn from the time seed but the 12 minutes happen to collide.* Excluded: `DS:7B62` takes ten different values over the ten minutes (Observations), and the model from seed = country reproduces every byte.
2. *The values are fixed data read from a file and the model fits by chance.* Excluded: `GOAL.DAT` holds no such bytes (F002 R013), and the model reproduces 30720 of 30720 per field from 16-bit draws.
3. *Something after the new game, such as the 162 time-seeded draws before the main screen, rewrites some fields.* Excluded for the main screen: the model of the new-game writers matches every modelled byte there. What happens after the main screen (matches, seasons) is out of scope.
4. *The managed country changes other countries' players.* Not tested behaviourally (one managed country); statically `98C4` writes only new player numbers from `[A927]`.

## What this does not establish

- Another DOS date: all 12 are 10/04/2026. Statically the player path reads no date; `9B85` uses `DS:A9FD` (the year) for `[A923]`+0x3A only. That is one route.
- Another managed country, or several managers: statically that country gets +0x2E > 0x80, the 80 players of `98C4`, and draws through `3558`'s managed branch. The 80 records would differ because the managed rating and squad differ. This is one route, not run.
- Which routine draws the one LCG step between `9A40` and `98C4`, and whether its count depends on keys in `1771:26B9`'s selection screens. With F001's keys it is one draw in 12 of 12.
- When `26B9` regenerates two countries with `97CC` (`seg_1771_04.asm:675`, `:683`), and when the other callers of `96D3` (`000E:54F0`, `1771:7E80`) run: careers and ageing (Q013–Q016).
- What +0x05, +0x08 … +0x0B, +0x0C, +0x0D/+0x0E, +0x0F and +0x10 … +0x13 mean in play (Q009–Q012), and how the screens show them (Q009).

## Where the evidence is

- `evidence/E006/E006-r0001.manifest.json` … `E006-r0012.manifest.json`: the main-screen savestate of each game (`e006-HHMM-r<nnnn>.sav`, class `save`). They are assets of release `E006` of this private repository, named `<sha256[:16]>-<name>`, and each record's `outputs` names its own.

## Reproduction

```
bash setup/goal2-runtime.sh
python3 experiments/E006-q004-skills/run.py games --times 10:00,10:01,10:02,13:37,21:00,23:58,00:00,06:30,12:00,17:45,10:00,10:00 --batch b1
python3 experiments/E006-q004-skills/summarise.py
python3 tools/verify_evidence.py E006
```
