# E024 computer-managers - notes (T50, F024)

Append-only. Addresses are `segment:offset`; listings are `static/goal-exe/code/seg_*.asm`; the data image is `static/goal-exe/data/ds_2581_*.hex`. Run from the repository root. Every originals file under `out/` is kept as written; `out/SHA256SUMS-*.txt` records the hashes.

## 1. What was done, in order

1. Static reading (rule 22): the call table (`calls.tsv`) gave `A3DE` -> `B11F`, `34E7`, `BD83`; `B11F` calls `AC67` (x9), `AFA3`, `52CC`; `AFA3` calls `AAE8`, `AD8F`, `A9B8`; the nested helpers take the caller's `bp` as a static link. The task file's names `0791:1E8D`, `0791:C50C`, `0791:1EB5` are not lineup routines: `C5DC` calls `214B:1E8D` (speaker off), `C50C` (the substitution notice screen) and `0791:1EB5` (commentary); they belong to a substitution in a watched match.
2. `tables.py` printed the tables the lineup reads (`out/tables-1.log`): `DS:099A`, `DS:08D5`, the sets `DS:693A`, `695A`, `697A`, the string `DS:08CE`. The sets inside the code segment are read by hand from the listing: `CS:AD0F` = 60 00 -> {5, 6}; `AD2F` = 80 04 -> {7, 10}; `AD4F` = 00 09 -> {8, 11}; `AD6F` = 00 30 -> {12, 13}; `1771:3139` = 88 04 -> {3, 7, 10}; `1771:3159` = 10 09 -> {4, 8, 11} (element k at bit k mod 8 of byte k div 8).
3. `tally_tactics.py`: C173 branches over the ten E010 second halves (model, seed-exact): `out/tally-20261013T142733Z.log`.
4. `sample_silent.py`: `B19D(12)` sampled on the ten lineups: `out/silent-20261013T142848Z.log` (first script version), `silent-asis-…`, `silent-fresh-…`.
5. `diff_b11f.py`: the original `B11F` in Unicorn against a Python reading, on the ten half-time savestates and random patches. First run 5 scenarios per team (`diff-b11f-20261013T143317Z.log`, 43 of 120 flagged by my own sortedness check, which did not know that `52CC` marks the unavailable of a MANAGED country 0xE: the test teams include the managed one; the sets, `+6` bytes and `DS:99A2` matched in all 120); then 150 per team (`diff-b11f-20261013T143448Z.log`, the script before the falsifier option; 3020 cases, 0 differences); the final script `diff-b11f-main-…` (3020, 0) and the falsifiers `tie`, `first`, `noweaker`, `nofoot`.
6. `squad_writers.py`: heuristic scan for writers of squad words (`out/squad-writers-1.log`).

## 2. Decisions and surprises

- A name in the model (`QuickMatch`) is used for the player predicates (`unavailable`, `wrong_foot`, `player_strength`, `two_footed`, `foot_index`, the tables `t_formation`, `t_benchvalue`, `t_posstring`); a wrong table would show in neither side of the comparison. The original and the reading both read the tables from the same savestate; `tables.py` prints the same tables from the data image of the unpacked file (`tables-1.log`, which F024 quotes); `check_tables.py` compares the savestates' bytes of `DS:099A`, `08D5`, `08CE`, `693A`, `695A`, `697A` with the image: equal in 10 of 10 (`out/check-tables-1.log`).
- The compare does not check the ORDER inside each half: `52CC` sorts with the program's quicksort, whose order among equal `+6` is not reproduced. It is checked non-decreasing in `+6` (with `0xE` for the unavailable of a managed country).
- The perturbations: per player of the country, energy to 0 (injured) with probability 0.12, status element 8/6/3 with 0.06, energy 1..32 with 0.25, morale 1..40 with 0.3, ability +-40 with 0.3, `+6` of a starter random with 0.15, `+7` random with 0.08; seeded by record, team and scenario number.
- The Unicorn run needs no stub: `B11F` calls `214B:0018`, `214B:007B`, `23E4:075A`, `06E3`, `08DF` and `1771` routines, all in the image; the frame is the one `emu_full_loop.py` uses (SS 0x7000, SP 0x6FF0 here), the return goes to an address in the code segment that is never executed (`until`).
- `tally_tactics.py` counts what the model decides; for the guest this is the same wherever the model is seed-exact (10 of 10 re-checked in the run), but it is not a hook on the guest. The set-up call (`A3DE`, `BD83`) happens before the half-time savestate, so not counted.
- Not done: a run in the game of a silent fixture (no savestate reaches `000E:6970`: E014 notes that only the R quick-result path is run by its corroborating years); a count of `route_fixture`'s branches.

## 3. Open (for a later task)

- Which fixtures carry first byte `0xFE` (writers in the fixture builders), and what competition codes 8, 101, 103, 200, 201, 203 and the set `DS:693A` are (T49's competitions).
- A silent fixture's goals in the game against the model's 1.1 per match (needs a round of computer fixtures in a savestate).
- Which screens show a computer manager's name (callers of `000E:0ACB` in `000E:11D9`, `26F2`, `319B`, `3CC8`, `4A87`).
- `C0DF`, `C01A`, `BF6B` branch counts (no recorded state reaches them: a match with a 2+ goal difference after a goal).
