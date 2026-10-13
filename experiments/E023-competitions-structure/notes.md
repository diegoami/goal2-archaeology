# E023 competitions structure (T49, F023)

Static reading of the five stage builders and the group-table sort, plus arithmetic over the data image. **No run of GOAL.EXE.**

| file | what | sha256 |
| --- | --- | --- |
| `dsbytes.py` | reads the committed data-segment hex dumps (`static/goal-exe/data/ds_2581_0*.hex`) | 3e733cfb5fec995ebc3b16613b6b35ae1efde8a1d942ee95de7778db19a9a40c |
| `tables.py` -> `tables.txt` | the sets `DS:0F3E`, `DS:693A`, the permutations, the 11 schedule rows, the friendlies tables | script 30ac13523825132dc2bd7c866172e757bd06c59301e32246486b9135f51e4707; output 39418be87dcf4e03651ec6888e34790db6e97b0137efdfefe3ff8ce65f9326a2 |
| `counts.py` -> `counts.txt` | re-runs the builders' loops (6730, 6B55, 6E59, 7090, 71B2, 74BE) over those tables: fixtures per stage and kind, per team, against `DS:6936` | script 1a6355f67dc3d3a9814b2c8b32862e715d45316e3ed546e0b26c201b2752349c; output ba3f212d0d3458be477a82a0b8d2f4d0c211a4704f63ad6b9df01b1ae5653c1d |
| `shuffle.py` -> `shuffle.txt` | exact distribution of the draw's weak shuffle (4 swaps of two uniform positions in a block of 8) | script 3381e24f5c577169d4a91b832d4cf4af44e9bd8f8f82f2f61cc4e430b14ad506; output 3fd08c24a247ff210b3e83794ba970c771c34851d0ab79cc2a1507d181ca3eb4 |

| `sets.py` -> `out/sets.txt` | every Pascal set cited (CS:81E8, 8737, 59B8, 7099; DS:0F3E, 693A), all 32 bytes decoded | script 827508afe83148f930e0ca696c3be72c75f78e839bdf8c8bb493df39492acd17; output ef878083f9223c618d136d3c6ff647c73ee67b28d477faa0f4fcd430318a201b |

Re-run: `python3 -B experiments/E023-competitions-structure/<script>.py > <output>` from the repository root; each takes under a second (no game, no network).
The outputs are not measurements of the game; they are deterministic functions of the committed dumps and the loops transcribed from the listing (the loop bounds and table offsets are cited in F023).

Cross-checks that came out exact: class 0 writes 1360 fixtures and the data image says class 1 starts at 1361 (`DS:6936`); class 1 writes 1040 and ends at 2400, below the eight aggregate records 2401..2408; every schedule row is a complete double round robin of 4 teams.
