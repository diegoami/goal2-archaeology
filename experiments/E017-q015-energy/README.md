# E017 energy comparisons

Run `python3 experiments/E017-q015-energy/check_energy.py` from the repository
root. Comparisons use player words and all three final bytes, never player names.
Empty comparison sets fail.

## Superseded by, and why

The machine-readable declaration is `supersessions.json` in this directory.
The checker validates that both named records exist and that the successor is
not itself superseded, prints each superseded record and its reason, and checks
every comparison in all remaining records. Original captures remain unchanged.

| Record | Superseded by | Why |
| --- | --- | --- |
| `records/recovery-001.json` | `records/recovery-002.json` | Missing healing draw: 214B:06D0 calls 0688 directly, bypassing the initial 06B1 hook (`static/goal-exe/code/seg_214B_01.asm:913–935`). The repeat captures the draw at 0688 for the same cases. |
