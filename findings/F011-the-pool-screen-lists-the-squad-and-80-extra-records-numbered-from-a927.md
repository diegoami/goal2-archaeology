# F011 The selection screen's pool is the 20 squad records plus 80 more numbered from A927, one block per manager, sorted by position

- **Status**: proposed
- **Question**: Which records does the pool (selection) screen list for a managed country, in what
  order, and how many? Where does each manager's 80 come from, and how many managers fit? What do
  `1771:26B9` and `1771:9873` do in this path? (G5 Q007, `docs/backlog.md`; T22)
- **Tests claims**: the backlog's Q007 (the pool lists 100 names, the squad's 20 = R012 and the other
  80 from the 500 unassigned names); bears on F007 (which made the 80 and numbered them 2561..2640),
  on R012 (the squad records) and R003/R004 (the names); on Q008 (when the squad may change, out of
  scope here); no spec row exists yet
- **Experiment and runs**: E009; one record, E009-r0001 (the managed country's pool screen, read from
  E006's published main-screen state of a new game)
- **Artifact**: set `goal2-67cf27d6`, variant none
- **Max intervention**: I2 (a savestate written at each read and one loaded at the start; the DOS
  clock of the session is not set; memory and text page read from the savestates, I1)
- **Tier reached**: V2
- **Confidence**: unreviewed (status `proposed`). Static: every claim below is read from the listing
  (`static/goal-exe/code/`), where the decompiled view hits a trust limit (the pool index array, the
  base table and the sort). Behavioural: the one record of E009 reads the pool index array `DS:A927`,
  the base table `DS:6D18`, the 80 pool records and the two records past them from the restored
  state, and matches the pool screen's names to `GOAL.DAT`. Claims marked "both" have both routes;
  a claim on one route says so.

## Answer

- **The selection screen has two views, not one 100-name list** (both). `0791:E44F` (`select_team_screen`,
  `seg_0791_22.asm:E44F`) is the SELECT TEAM screen. Its local word `[bp-5]` picks the view: 1 draws the
  squad view (`call 1771:4E22` at `:E4CD`), 2 draws the pool view (`call 0xe2e6` at `:E4D5`); Left/Right
  toggle it (`cmp al, 0xae`/`0xaf`, `:E6B8`–`:E6D4`). So the 100 names the backlog describes are 20 in the
  squad view plus 80 in the pool view. I put this at about 97% (E009-r0001 shows both screens; the toggle
  is the listing).
- **The squad view lists the 20 squad records** (both, corroborating F008). `1771:4E22` →
  `1771:4D8A` (`draw_squad_list`, `seg_1771_03.asm`) draws `draw_squad_row(0x41, row, country.squad[i-1])`
  for slots i = 1..11 (rows 3..13) and 12..20 (rows 15..23), then the card of `squad[DS:0C1B − 1]`
  (`1771:42BC`). The country record's first 20 words are the squad (R012, F007 `load_countries`), so the
  squad view lists player records `(c−1)·20+1 .. c·20` in the country record's order. About 97% (F008
  established the list; E009-r0001 reads Denmark's 20).
- **The pool view lists 80 records, in `DS:A927` order** (both). `0791:E2E6` (`draw_pool_view`,
  `seg_0791_22.asm:E2E6`) draws, for the 21 rows `top .. top+20` (`[DS:A923]+manager·2+0x52` to `+0x14`,
  `:E350`–`:E371`), the name of the player number at
  `A927[ DS:6D18 + 2·manager + row − 1 ]` (`mov ax, word ptr [di + 0x6d18]` `:E38B`, `les di, [0xa927]`
  `:E395`, `push word ptr es:[di]` `:E39B`, `call 1771:2F37` `:E3A5`), then the card of the selected pool
  player (`0791:DDCB`/`0791:DE51`/`1771:42BC`). The list scrolls 80 items, 21 visible
  (`push 0x50`, `push 0x15`, `call 214B:15B1` at `:E7CC`–`:E7D4`). So the pool view lists 80, not 100,
  records. About 95% (E009-r0001 lists the first 20 of them on the screen; 80 is the listing).
- **The 80 records are `0xA00 + index`, in `A927`, position-sorted** (both). `1771:98C4`
  (`make_managed_pool`, `seg_1771_14.asm:98C4`) makes them through `1771:9873` (`make_pool_player`):
  each call increments the caller's counter (`inc word ptr ss:[di − 2]`, `:9879`), stores the record
  number `counter + 0xA00` into `A927[counter]` (`:9898`), and draws the record with
  `make_player(flag 0, position, country, number)` (`:98BA`). The counter starts at
  `DS:6D18 + 2·manager − 1` (`:990D`–`:9912`), so manager m's 80 fill `A927[base .. base+79]`,
  `base = DS:6D18 + 2·manager`. The make order is positions 0..13 four times (`:993E`–`:9953`), one per
  squad slot 1..20 (`:9979`–`:99FB`, with the age redrawn and `1771:32EB`), then slots 6..9 again
  (`:9A0E`–`:9A36`). Then `sort_pool_by_position` (`1771:5532`, called at `:9A38`) sorts
  `A927[base .. base+79]` ascending by the position byte +6 (`1771:53E8` is the partition, pivot the
  middle element; equal positions may swap, so within a position the make order is not kept). About 95%
  (F007 reproduced the 80 records byte for byte; E009-r0001 reads the array and the records).
- **The 80's names are the names after record 2560** (both). A player's name is the initial at
  `[DS:9B70] + n` and the surname at `[DS:9B6C] + 11·n` (`1771:2E93`); those arrays are blocks 2 and 3 of
  `GOAL.DAT` (R003, R004: 3060 surnames and initials, the record index is the player number). Manager 1's
  80 are records 2561..2640, so their names are `GOAL.DAT`'s surnames 2561..2640. E009-r0001 matches the
  screen's names to them. About 95% (F002 established the blocks; E009 matches the names).
- **Each manager gets its own block of 80** (static). The base table at `DS:6D18` is initialised data
  (`ds_2581_03.hex`): `word[m]` for m = 1..6 is 1, 81, 161, 241, 321, 401, i.e. `80·(m−1)+1`. Manager m's
  pool is `A927[80·(m−1)+1 .. 80·(m−1)+80]` = records `2560 + 80·(m−1) + 1 .. 2560 + 80·m`: manager 1
  2561..2640, manager 2 2641..2720, …, manager 6 2961..3040. About 95% (the table is read at
  `:990D`, `:E38B`, `:5546`, `0791:DDCB`; one manager is run).
- **At most 6 managers, and the records allow exactly 6 full pools** (static). The new-game menu that
  sets the manager count (`1771:0021`, `seg_1771_01.asm:0021`) is a 6-item menu (`push 6`,
  `call 214B:1507` at `:00A0`–`:00A4`) and accepts the keys `1`..`6` (`cmp al, 0x31`/`0x36`,
  `:00A9`–`:00B4`), so 1..6 managers. 6 managers × 80 = 480 pool records (2561..3040); the player array
  holds 3061 records (F002 R013), 2560 squad plus 500 unassigned (2561..3060), so 6 full pools leave
  20 records (3041..3060) unused. About 95% (the menu is the listing; a second manager is not run).
- **`1771:26B9` and `1771:9873` in this path** (static). `1771:26B9` (`country_list_screen`) in mode 2
  is the country picker `1771:2D15` (`set_managed_countries`) runs per manager: on Enter with a country
  that is not already managed it stores that country into `DS:A91F + 3·(0x80 + manager)`
  (`cmp word ptr [bp+6], 2` `seg_1771_04.asm:2C38`; `is_managed` via `call 0xb77`, `214B:1765` refuses a
  managed one; the store `mov byte ptr es:[di], cl` at `:2C96`). It does not make the pool itself;
  `2D15` calls `make_managed_pool` after. `1771:9873` (`make_pool_player`) is `98C4`'s one-player
  helper: increment the counter, write `A927[counter] = counter + 0xA00`, draw the record (above).
  About 95% (the listing).

## Method

- **Static first** (owner rule U32). The question was answered from the listing. The named view
  (`static/goal-exe/named/`) has the routines typed, but the pool path's array indexing (the base table
  `DS:6D18`, the pool index array `DS:A927`, the sort) is a trust limit of the decompiled view (F009:
  struct typing on far pointers), so each claim above is read from `static/goal-exe/code/`
  (`seg_0791_22.asm` E44F/E2E6, `seg_1771_14.asm` 98C4/9873, `seg_1771_08.asm` 5532/53E8,
  `seg_1771_04.asm` 26B9, `seg_1771_01.asm` 0021) and the base table's bytes from
  `static/goal-exe/data/ds_2581_03.hex`. The listing answered everything except the values themselves
  (the base table's numbers, the pool records and the names are initialised or drawn data, not constants
  in the code), which the one run corroborates.
- **The run corroborates.** E009: a fresh DOSBox-X launch, E006's published main-screen savestate of a
  new game (E006-r0001, release E006) restored with Host+L, then Esc (exit the country list to the main
  menu `000E:7439`), Space (the SELECT TEAM screen `0791:E44F`, squad view), Left (the pool view
  `0791:E2E6`). Each screen is read; from the restored state's savestate the run reads the pool index
  array `DS:A927` (481 words), the base table `DS:6D18` (8 words), the name arrays `[DS:9B6C]`/`[DS:9B70]`,
  the 80 pool records (2561..2640) and the two records past them (2641, 2642). One record per run.
- Machine and tools: as F007 (Ubuntu 24.04 in WSL2, DOSBox-X 2024.03.01, Xvfb, `cycles=30000`); driver
  `runtime/driver/driver.py`, `players.py` (names), runner `experiments/E009-q007-squad-pool/run.py`,
  analysis `experiments/E009-q007-squad-pool/summarise.py`.

## Observations

- `summarise.py` (E009-r0001, the one record): `DS:A927[0]` is 0, `DS:A927[1..80]` is exactly the set
  {2561..2640}, and `DS:A927[81..480]` is all zero; `DS:6D18` words 1..6 are 1, 81, 161, 241, 321, 401.
- The 80 pool records 2561..2640 hold country 7 (Denmark) in byte 0; records 2641 and 2642 are all zero.
- The pool view lists the names of `DS:A927[1..20]` (first three: B Gathergood, O Dyke, T Barrow), and
  the positions (+6) of `A927[1..80]` in `A927` order are non-decreasing — the pool is position-sorted
  (`sorted ascending: True`), 6 goalkeepers first.
- The squad view lists Denmark's 20 squad records 121..140 (first three: P Schmeichel, L Olsen, T Piechnik).

## Inferences

- A rebuild's pool for manager m is the country's 20 squad records (the country record's first 20 words,
  R012) plus the 80 records `2560 + 80·(m−1) + 1 .. 2560 + 80·m`, listed in the pool view in the order
  `A927` holds after `sort_pool_by_position` (ascending by position +6). The names are `GOAL.DAT`'s
  surnames/initials at the same record numbers.
- The "100 names" of the backlog are two screens, not one list: 20 in the squad view, 80 in the pool view.

## Alternatives considered

1. *The pool view lists 100 names at once.* Refuted: the list scroll is 80 items (`0x50`), and the pool
   view reads only `A927` (the 80), never the country record's squad.
2. *The 80 come from other countries' squads.* Refuted: `make_managed_pool` makes fresh records numbered
   `0xA00 + counter` (2561..2640 for manager 1), distinct from all 2560 squad records (F007, F002 R012).
3. *The pool is in make order, not sorted.* Refuted: `sort_pool_by_position` sorts by +6 before the screen.

## What this does not establish

- When the squad may change and how the pool's exchange/edit works (`0791:DEA6`, `0791:E022`,
  `0791:DC7E`, `0791:DDCB`'s use beyond the card) — Q008.
- A second manager run: the base table and the 6-manager limit are static only (one manager is run).
- The order of players of the same position (the quicksort is not stable; the make order within a
  position is not guaranteed to survive).

## Where the evidence is

- `runs/E009/E009-r0001.json`; the start state is E006-r0001's (`evidence/E006/E006-r0001.manifest.json`,
  release E006).

## Reproduction

```
bash setup/goal2-runtime.sh
python3 experiments/E009-q007-squad-pool/run.py adopt --from E006-r0001
python3 experiments/E009-q007-squad-pool/run.py pool --state e006-1000-r0001 --batch b1
python3 experiments/E009-q007-squad-pool/summarise.py
python3 tools/verify_evidence.py E006
```
