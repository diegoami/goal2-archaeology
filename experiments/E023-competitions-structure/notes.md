# E023 competitions structure (T49, F023)

Static reading of the five stage builders and the group-table sort, plus arithmetic over the data image. **No run of GOAL.EXE.**

| file | what | sha256 |
| --- | --- | --- |
| `dsbytes.py` | reads the committed data-segment hex dumps (`static/goal-exe/data/ds_2581_0*.hex`) | 3e733cfb5fec995ebc3b16613b6b35ae1efde8a1d942ee95de7778db19a9a40c |
| `tables.py` -> `tables.txt` | the sets `DS:0F3E`, `DS:693A`, the permutations, the 11 schedule rows, the friendlies tables | script de9093995d079c7fef3bf6f2dd6df3a6fb92d35078952c297146fedf43dc854e; output 09f3db6844405b578ec60615c6f548a395c13914ac2b68c44ce85b8b9b26b8bf |
| `counts.py` -> `counts.txt` | re-runs the builders' loops (6730, 6B55, 6E59, 7090, 71B2, 74BE) over those tables: fixtures per stage and kind, per team, against `DS:6936` | script 1a6355f67dc3d3a9814b2c8b32862e715d45316e3ed546e0b26c201b2752349c; output ba3f212d0d3458be477a82a0b8d2f4d0c211a4704f63ad6b9df01b1ae5653c1d |
| `shuffle.py` -> `shuffle.txt` | exact distribution of the draw's weak shuffle (4 swaps of two uniform positions in a block of 8) | script 3381e24f5c577169d4a91b832d4cf4af44e9bd8f8f82f2f61cc4e430b14ad506; output 3fd08c24a247ff210b3e83794ba970c771c34851d0ab79cc2a1507d181ca3eb4 |

Re-run: `python3 -B experiments/E023-competitions-structure/<script>.py > <output>` from the repository root; each takes under a second (no game, no network).
The outputs are not measurements of the game; they are deterministic functions of the committed dumps and the loops transcribed from the listing (the loop bounds and table offsets are cited in F023).

Cross-checks that came out exact: class 0 writes 1360 fixtures and the data image says class 1 starts at 1361 (`DS:6936`); class 1 writes 1040 and ends at 2400, below the eight aggregate records 2401..2408; every schedule row is a complete double round robin of 4 teams.
