# F032 From the title's key read to the first manager menu, a new game opens, reads and closes GOAL.DAT and reads the DOS time, and makes no other interrupt; the title waits in 214B:08DD's read only after its animation

- **Status**: proposed
- **Question**: #367 (T82, a request from goal2 for its core, stage 3, G10): a savestate at the new-game screens with the CPU inside 214B:08DD's INT 16h key read; every interrupt other than that read between the title's load prompt and the first manager menu, with its call site and what it reads or writes; the key-read sites and caller frames of `title-load-prompt`, `title-player-count`, `country-select-name-entry` and `country-select`
- **Tests claims**: none (no `spec/` row); bears on F004 (the seed's DOS time read: where in the new-game path it happens) and on goal2's core (`goal2/core/runner.py` R1: a start state is one in 08DD's read)
- **Experiment and runs**: E038, `experiments/E038-new-game-keywait/` (`run.py`, `trace.py`, `summarise.py`, `notes.md`, `out/`); the run E038-r0001 (DOSBox-X, one new game, seven savestates kept) and the trace `out/trace-r0001.json` (the original's code under Unicorn from E038-r0001's title state, no record: an emulation of the listing's code, a static method)
- **Artifact**: set `goal2-67cf27d6` (the run); the listing of set `goal2-a949da2f`, packed GOAL.EXE sha256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664` (`static/goal-exe/README.md`)
- **Max intervention**: I3 (DOS date 10/04/2026 and time 10:00:00 set in the autoexec, read back; savestates written, I2; memory, registers and screens read from them, I1)
- **Tier reached**: V2 for the path traced (the listing, one DOSBox-X run, and a Unicorn run of the original's code that reaches the same end state)
- **Confidence**: unreviewed. Words as `docs/wide-pass.md`: **read** (the listing), **measured** (the record or the trace's log), **likely** (stated with what was searched).

## Answer

- **The states goal2 asked for exist, in the read** (measured): E038-r0001 kept one savestate per new-game screen, each but the name entry with the CPU at F000:CFA1–CFB1 (the BIOS's INT 16h wait) and exactly one frame of 08DD's `Intr` call above SS:SP. On the owner's Drive, folder root (as goal2 asked), and under `goal2-archaeology/E038/` with the record's names:

| screen | Drive (root) | record's name (`goal2-archaeology/E038/`) | sha256 | CPU | 08DD's return (the site) | callers (return addresses) |
| --- | --- | --- | --- | --- | --- | --- |
| `title-load-prompt` | `e038-r0001-title-keywait.sav` | `e038-title-load-prompt-r0001.sav` | `1c106cc3…` | F000:CFB0, SS:SP 3875:3FC6 | `1771:085F` | `0000:0029` (E038-r0001) |
| `title-player-count` | `e038-r0001-title-player-count.sav` | `e038-title-player-count-r0001.sav` | `6ad3920d…` | F000:CFA1 | `1771:0081` | `1771:08A8` (near), `0000:0029` (E038-r0001) |
| `country-select` | `e038-r0001-country-select.sav` | `e038-country-select-r0001.sav` | `586dbfcf…` | F000:CFA1 | `1771:28F5` | `1771:2D55`, `0000:003F` (E038-r0001) |
| `country-select-name-entry` | `e038-r0001-country-select-name-entry.sav` | `e038-country-select-name-entry-r0001.sav` | `879a5520…` | load+235C:004F (not in the read) | — (a polled screen) | — (E038-r0001) |
| `bulletin` ("APPOINT A NEW MANAGER", hit any key) | `e038-r0001-after-name-1.sav` | `e038-after-name-1-r0001.sav` | `3036081b…` | F000:CFAF | `000E:0629` | `000E:6964` (near), `0000:0078` (E038-r0001) |
| `bulletin` ("GROUPS ARE ANNOUNCED") | `e038-r0001-after-name-2.sav` | `e038-after-name-2-r0001.sav` | `8df96e01…` | F000:CFAE | `000E:0629` | `000E:6625` (near), `0000:00BE` (E038-r0001) |
| `manager-menu` | `e038-r0001-manager-menu.sav` | `e038-manager-menu-r0001.sav` | `4031771a…` | F000:CFB1 | `000E:75D1` | `0000:00CB` (E038-r0001) |

  (E038-r0001; the full sha256 and the frames are in the record.) goal2's core (`Core.start`, goal2 at its `main` of 2026-10-22) finds 08DD's entry in each read state and then stops only because its screen table has no entry for these sites; it refuses the name-entry state (no frame), as it should.
- **Why the checkpoints' `title.sav` are refused** (read; measured): the title `1771:080C` runs an animation (`1771:07B4` → `06F3`, nine rounds of 37 cells, each after a "key pressed?" poll `214B:0723`, each cell drawn by `214B:1EF1`, which waits in CRT `Delay` `214B:1E09`) before it calls 08DD at `1771:085A`. The checkpoints were taken during it (their CPU at load+214B:1E3E–1E44 is the delay loop). The read comes about 12 s after the title appears in a free-running DOSBox-X at `cycles=max` (T82's probe), 24.9 s in E038-r0001, whose savestate polls slow the guest. static:static/goal-exe/code/seg_1771_01.asm:887 static:static/goal-exe/code/seg_1771_01.asm:935 static:static/goal-exe/code/seg_214B_04.asm:98 (E038-r0001)
- **The interrupts from the title's read to the first manager menu** (measured in the trace, keys `n Enter Enter b o b Enter Enter Enter`, one manager, no saved game; E038-r0001's end matched): besides the key reads (INT 16h AH=0 through `Intr` at `214B:08FF` in 08DD) and the name entry's polls (INT 16h AH=1 through `Intr` at `214B:0735` in `0723`), exactly these, in this order (E038-r0001):

| # | when | interrupt | how it is reached (call site) | callers | reads | writes / returns |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | after `n` at the title, before the player count ("loading") | INT 21h AH=3Dh AL=02h, open | `MsDos` `235C:0000` from `214B:1ABE` (returns `214B:1AC3`) | `214B:1C1A` (near), `1771:014E`, `1771:0198` (near), `1771:08A5`, `0000:0029` | DS:DX = SS:3DB2, the ASCIIZ name `goal.dat` | AX = the handle (5 in the trace), CF clear (E038-r0001) |
| 2–11 | the same | INT 21h AH=3Fh, read (10 calls) | `MsDos` from `214B:1B81` (returns `214B:1B86`) | `1771:01A7`, `01B6`, `01C5`, `01D4`, `01E3`, `01F1`, `01FF`, `020D`, `021B`, `0229`; then `1771:08A5`, `0000:0029` | BX = 5; CX = 2064, 33671, 3061, 1755, 135, 387, 129, 129, 129, 2580 bytes, in file order from offset 0 to 44040 (the whole file) | the bytes to DS:DX: five heap blocks (far pointers the routine allocated), then DS:9D80, DS:9B7C, DS:9BFD, DS:9C7E, DS:9F03; AX = CX (E038-r0001) |
| 12 | the same | INT 21h AH=3Eh, close | `MsDos` from `214B:1A54` (returns `214B:1A59`) | `1771:022E`, `1771:08A5`, `0000:0029` | BX = 5 | CF clear (E038-r0001) |
| 13 | after Enter on the first bulletin ("APPOINT A NEW MANAGER"), before the second | INT 21h AH=2Ch, get time | the instruction `int 21h` at `23E4:11D9` in `23E4:11D7` (frameless, far) | `1771:67A8` (its return, in `1771:6730`), `1771:76C7` (near, in `1771:76B1`), `0000:0085` | — | CX → `DS:7B62` (hour·256+minute: the seed, F004), DX → `DS:7B64` (seconds·256+hundredths) (E038-r0001) |

  No INT 10h, no INT 21h AH=2Ah (the date), no other vector. (E038-r0001)
- **What serving these reproduces** (measured): the trace served exactly the rows above (the file from the verified release copy, the time 10:00:20.95 that E038-r0001's `DS:7B64` = `0x145F` shows DOS answered) and nothing else; at the manager menu its screen bytes, `DS:7B62` = `EE42`, `DS:7B64` = `145F`, the player array and the country array equal E038-r0001's manager-menu state byte for byte, and of conventional memory only the BIOS keyboard buffer, the tick count, the word DOS saves in the PSP at each INT 21h (`0813:002E`) and stack bytes below the read's SP differ. Each intermediate read's site, callers and screen equal the record's (`summarise.py`: 6 of 6). (E038-r0001)
- **The seed is the minute of the first bulletin's key** (measured; read): the time read (row 13) runs after the key that leaves the first bulletin, so a new game's seed is the DOS hour:minute at that key, not at the title; a replay that serves AH=2Ch with the same hour and minute gets the same game (F004: the seconds do not change the screen). The title state holds `DS:7B62` = 0, and the DOS year (2028 in the bulletin, from the date 10/04/2026) was already read before the title (no AH=2Ah after it). (E038-r0001) static:static/goal-exe/code/seg_23E4_02.asm:806
- **The key-read sites** (measured; read): `title-load-prompt` 08DD returns to `1771:085F`; `title-player-count` `1771:0081` (in `1771:0021`, `manager_count_menu`); `country-select` `1771:28F5` (in `1771:26B9`, the country browser, called from `1771:2D50` in `1771:2D15`); `country-select-name-entry` is a **polled** screen: the line editor `214B:1086` (called at `1771:0A1D`, return `1771:0A22`, from `1771:2E00`, return `1771:2E05`) calls the cursor loop `214B:0D90`, which polls `214B:0723` (return `214B:0DB9`) and reads the BIOS tick count `0040:006C` for the cursor's blink (a memory read, not an interrupt), and calls 08DD (return `214B:112B`) only when a poll says a key waits: once per letter and for Enter. Both bulletins read at `000E:0629` (in `000E:05F6`). The manager menu reads at `000E:75D1` (in `000E:7439`). (E038-r0001) static:static/goal-exe/code/seg_214B_02.asm:608 static:static/goal-exe/code/seg_214B_02.asm:972

## Method

- Static first (rule 22): the title `1771:080C`, the read `214B:08DD`, `Intr` `235C:000B` and `MsDos` `235C:0000`, the name entry `214B:0D90`/`1086`, `Randomize` `23E4:11D7`, and every `int` instruction and every `Intr`/`MsDos` call of the listing (`static/goal-exe/code/`, `calls.tsv`, `annotations/routines.tsv`). Static reading settled why the checkpoints are refused and where a read state can be taken, and gave the superset of interrupt sites; it could not by itself say which of them a new game reaches (the file routines `214B:1A36`–`1C86` serve every file the game opens) nor produce the savestate goal2 asked for, so one DOSBox-X run made the states, and the original's own code was run under Unicorn from one of them to list the interrupts the path makes.
- `Intr` (`235C:000B`, `seg_235C_01.asm:20`–`61`) reaches the handler without an `int` instruction: it pushes the flags and a return to `235C:0045`, loads the vector from `0:4n` and `retf`s into it. A Unicorn interrupt hook therefore sees only the `int` instructions (`23E4:11D9` here); `trace.py` also hooks `Intr`'s entry and serves the interrupt it asks for, writing the register record back and returning `retf 6`. static:static/goal-exe/code/seg_235C_01.asm:20
- E038-r0001: `run.py` at its `code_commit`; DOSBox-X 2024.03.01, `cycles=max` (`cycles=30000` crashed DOSBox-X at the first savestate in this cloud session, a scratch probe; `notes.md` §1); a state was kept at a screen only when its text was the expected one and, at a read, 08DD's frame was found above SS:SP (the same test as goal2's `read_entry`).
- The trace: `trace.py` from `e038-title-load-prompt-r0001.sav`, keys `6E 0D 0D 62 6F 62 0D 0D 0D` at 08DD's entry (as goal2's core answers), the poll `214B:0DB9` answered "a key waits" while keys remained, every other poll "no key" (none happened), time 10:00:20.95; any interrupt it did not serve would have stopped it (none did). Command line in `out/trace-r0001.json` (`argv`).

## Observations

- E038-r0001: launch, title after 2.5 s, the title's read kept at 27.4 s (44 polls), every later screen at the first poll after its key (0.6 s). DOS read back `10/04/2026 9:59:59`. `DS:7B62` at the seven states: `0000`, `0000`, `18BC`, — (name entry), `157F`, `EE42`, `EE42`; `DS:7B64` `0000` until the second bulletin, then `145F`. (E038-r0001)
- The trace's log `out/trace-r0001.json`: 7 reads with a key, 4 name-entry polls answered, 13 interrupts as the table, the stop at the manager menu's read with no key left; `compare` as in the Answer. (E038-r0001)

## Inferences

- **What goal2's core needs to serve for this path** (likely, from the table; E038-r0001): DOS open/read/close of `GOAL.DAT` (or the equivalent: the ten reads' bytes at their destinations, the handle in AX) and AH=2Ch with the hour and minute it wants as the seed; the two key routines it already answers; a "key waits" answer at the name entry's poll `214B:0DB9`. Nothing of video: the screens are written to the text page by the game's own code. Under Unicorn the tick count `0040:006C` does not move, so the name entry's cursor cell keeps one state; the key the editor reads restores it (`214B:0E1A`), so it does not reach the result.
- **Where an INT 10h would come from** (read; E038-r0001 makes none on this path): the program reaches the video BIOS only at start-up (`214B:206A` → `214B:0755` → CRT `TextMode` `2382:016D`, and the cursor hide `214B:0661`, `Intr` 10h at `214B:067F`), in the exit procedure `214B:136B` (`GotoXY` `2382:0215`), in CRT's own `Write` to `Output`, and in the DOS shell `214B:0813`, whose call in 08DD is dead code (`214B:0951`: `mov al, 0; or al, al; je`). goal2's INT 10h on "leaving the menu for a new game" is therefore likely the exit procedure (F10, quit) or a path this trace did not take; the site goal2's core reports would settle it. static:static/goal-exe/code/seg_214B_01.asm:866 static:static/goal-exe/code/seg_214B_02.asm:57

## Alternatives considered

- A state at the title taken without waiting (the checkpoints' way): refuted for goal2's use by the listing and the probe (the CPU is in `Delay`).
- The DOS time read at the title or at country selection: refuted; `DS:7B62` is `0000`, `18BC`, `157F` (draws from the start-up word, not the time) until the first bulletin's key, and the trace's only AH=2Ch is there. (E038-r0001)

## What this does not establish

- Other paths of a new game: `Y` at the title (loading a saved game: file search and other files), more than one manager, another difficulty or country choice. Not traced; the file routines `214B:1A36`–`1C86` are the same, the files and the AH values may not be.
- The handle number DOSBox-X gave (`5` in the trace): the run did not read it; the `FileRec` holding it was on the stack below the read's SP, among the bytes that differ.
- Timings in DOSBox-X beyond this one run and the probe.

## Where the evidence is

- Run record: `runs/E038/E038-r0001.json`. Savestates: the owner's Drive (table above; sha256 in the record's `outputs`).
- Trace: `experiments/E038-new-game-keywait/out/trace-r0001.json` and `.log`; check: `summarise.py`, `tests/test_e038_summarise.py`.
- Listing: `static/goal-exe/code/seg_1771_01.asm` (title), `seg_214B_02.asm` (08DD, 0D90, 1086), `seg_214B_03.asm` (file routines), `seg_235C_01.asm` (`Intr`, `MsDos`), `seg_23E4_02.asm` (`Randomize`).
