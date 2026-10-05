# static/goal-exe/decompiled/

Generated, never edited by hand: `bash tools/static/decompile.sh <released GOAL.EXE> static/goal-exe/decompiled` rewrites every file here byte for byte.

- Artifact: the released `GOAL.EXE` (packed sha256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`), unpacked by `tools/static/unlzexe.py` to sha256 `6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188` (checked by the tool; the unpacked file is never committed).
- Ghidra 12.1.4 (revision 8b6bbb857accdfa20dc5b2f5dea471178c2e9fbc), JDK 21.0.12.1, run headless with `-max-cpu 2`: the MZ loader, language `x86:LE:16:Real Mode` (compiler spec `default`), Ghidra's default auto-analysis options, the default decompiler options. Scripts: `tools/static/ghidra/GoalSetup.java` (before the analysis), `GoalDecompile.java` (after it); `tools/static/decompiled.py` writes these files.
- One function per routine of `../routines.tsv`, named `f_SSSS_OOOO` after its listing address, near or far by whether it returns with RETF. Ghidra's analysis may add functions; they are named the same way and marked in `index.tsv`.

## Addresses

Every heading, function name and label gives the listing address `SEGMENT:OFFSET` of `../code/`. Ghidra holds listing segment k (ascending) at its segment k×0x1000, so that each segment starts on a 64K boundary; at the listing's own segment numbers Ghidra's x86 language computes near call and jump targets wrongly (`GoalSetup.java` says why). Each heading also gives the Ghidra address. The map:

| listing | Ghidra |
| --- | --- |
| 0000 | 0000 |
| 000E | 1000 |
| 0791 | 2000 |
| 16D6 | 3000 |
| 1771 | 4000 |
| 2138 | 5000 |
| 2139 | 6000 |
| 214B | 7000 |
| 235C | 8000 |
| 2382 | 9000 |
| 23E4 | A000 |
| 2581 | B000 |

- `DS:9A3E` is offset 9A3E of the data segment 2581 (Ghidra's `DAT_b000_9a3e`, or `_DAT_b000_9a3e` for a wider access over smaller symbols).
- A segment number written in the code (a pushed segment, a far pointer's segment) is Ghidra's, from the table above: `0xb000` is the data segment 2581.
- A data address that Ghidra did not resolve stays a number, often signed: `*(char *)(i + -0x7f10)` is `DS:80F0 + i`.

What the decompiled view can be trusted for, and what not, was checked against the hand-traced claims of F002–F007: `findings/F009-*.md`.

## Counts

- Routines of `routines.tsv`: 726; decompiled 723, failed 3, no function 0.
- Functions Ghidra's analysis added (not in `routines.tsv`): 3: `23E4:00D1`, `23E4:0B50`, `23E4:13EF`.
- Not decompiled:
  - `0000:0000` (failed): Offset must be between 0x0 and 0x10ffef, got 0xffffffff instead!
  - `0791:1A04` (failed): Exception while decompiling 2000:1a04: ghidra.program.model.address.AddressOutOfBoundsException: Offset must be between 0x0 and 0x10ffef, got 0xb0002e8e instead!
  - `214B:05F0` (failed): Exception while decompiling 7000:05f0: ghidra.program.model.address.AddressOutOfBoundsException: Offset must be between 0x0 and 0x10ffef, got 0xb00079a4 instead!
- The scripts' own report: GOALSETUP moved 7 bytes back to segment 2138; GOALSETUP segments 12 relocations 1916; GOALSETUP routines 726 functions 726; GOALDECOMPILE functions 729 renamed 3 ok 726 failed 3.

| File | What |
| --- | --- |
| `index.tsv` | per function: listing address, decompiled or not, file and line of its heading, Ghidra address, found in `routines.tsv` or by Ghidra, why it failed |
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
