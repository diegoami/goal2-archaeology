# static/goal-exe/named/

The named view: the decompiled `GOAL.EXE` of `../decompiled/` with the annotations of `../annotations/` applied: routine names, the `player` and `country` records typed on the array pointers, global names and types. Generated, never edited by hand:

```sh
bash tools/static/decompile.sh --annotations static/goal-exe/annotations <released GOAL.EXE> static/goal-exe/named
```

rewrites every file here byte for byte (the same Ghidra run as `../decompiled/`, with `tools/static/ghidra/GoalAnnotate.java` before `GoalDecompile.java` and `tools/static/named.py` as the writer; `tools/static/check_annotations.py` must pass first). Ghidra 12.1.4 (revision 8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc), JDK 21.0.12.1.

- Names are claims. Each annotated heading gives a second line: the purpose, the confidence (`established` for a finding's claim, `likely`, `guess`) and the basis (a finding, or the lines read). A routine nobody has read keeps its `f_SSSS_OOOO` name.
- Each heading keeps the listing address and the raw name `f_SSSS_OOOO`, so a line here maps to `../decompiled/` and `../code/`. Addresses read as in `../decompiled/README.md`.
- `../decompiled/` stays the raw baseline (F009). Where the two differ on what the code does, the listing decides: struct typing on far pointers is a trust limit of F009.
- To add or correct a name: edit `../annotations/`, run the checker, regenerate this directory (`docs/process.md`, "The named view").

## Coverage

| segment | named | routines |
| --- | --- | --- |
| 0000 | 1 | 1 |
| 000E | 2 | 58 |
| 0791 | 47 | 283 |
| 16D6 | 0 | 26 |
| 1771 | 46 | 154 |
| 2138 (run-time library) | 1 | 1 |
| 2139 (run-time library) | 1 | 1 |
| 214B (run-time library) | 85 | 85 |
| 235C (run-time library) | 12 | 12 |
| 2382 (run-time library) | 17 | 17 |
| 23E4 (run-time library) | 88 | 88 |

- The scripts' own report: GOALSETUP moved 7 bytes back to segment 2138; GOALSETUP segments 12 relocations 1916; GOALSETUP routines 726 functions 726; GOALANNOTATE records 2 fields 22 globals 5 routines 300; GOALDECOMPILE functions 729 renamed 3 ok 726 failed 3.

| File | What |
| --- | --- |
| `index.tsv` | per function: listing address, annotated name and confidence (the basis is in the heading and in `../annotations/routines.tsv`), decompiled or not, file and line of its heading, Ghidra address, found in `routines.tsv` or by Ghidra, why it failed |
| `seg_000E_01.c` | code segment 000E, part 1 |
| `seg_000E_02.c` | code segment 000E, part 2 |
| `seg_000E_03.c` | code segment 000E, part 3 |
| `seg_000E_04.c` | code segment 000E, part 4 |
| `seg_000E_05.c` | code segment 000E, part 5 |
| `seg_0791_01.c` | code segment 0791, part 1 |
| `seg_0791_02.c` | code segment 0791, part 2 |
| `seg_0791_03.c` | code segment 0791, part 3 |
| `seg_0791_04.c` | code segment 0791, part 4 |
| `seg_0791_05.c` | code segment 0791, part 5 |
| `seg_0791_06.c` | code segment 0791, part 6 |
| `seg_0791_07.c` | code segment 0791, part 7 |
| `seg_0791_08.c` | code segment 0791, part 8 |
| `seg_0791_09.c` | code segment 0791, part 9 |
| `seg_0791_10.c` | code segment 0791, part 10 |
| `seg_16D6_01.c` | code segment 16D6, part 1 |
| `seg_1771_01.c` | code segment 1771, part 1 |
| `seg_1771_02.c` | code segment 1771, part 2 |
| `seg_1771_03.c` | code segment 1771, part 3 |
| `seg_1771_04.c` | code segment 1771, part 4 |
| `seg_1771_05.c` | code segment 1771, part 5 |
| `seg_1771_06.c` | code segment 1771, part 6 |
| `seg_2138_01.c` | code segment 2138, part 1 |
| `seg_2139_01.c` | code segment 2139, part 1 |
| `seg_214B_01.c` | code segment 214B, part 1 |
| `seg_214B_02.c` | code segment 214B, part 2 |
| `seg_235C_01.c` | code segment 235C, part 1 |
| `seg_2382_01.c` | code segment 2382, part 1 |
| `seg_23E4_01.c` | code segment 23E4, part 1 |
| `seg_23E4_02.c` | code segment 23E4, part 2 |
| `seg_23E4_03.c` | code segment 23E4, part 3 |
