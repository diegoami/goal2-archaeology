# F009 Ghidra's decompiled view of GOAL.EXE, at the listing's addresses, agrees with nine of ten hand-traced claims; it loses a delay loop that polls the BIOS tick, and it hides far-pointer segments and results returned in flags or registers

- **Status**: proposed
- **Question**: Does Ghidra's decompiled view of `GOAL.EXE` say what the code does, so that later tasks may read it in place of the capstone listing, and where does it not? (T18, G3; F002 named Ghidra as the missing static tool)
- **Tests claims**: none (no spec row); checks the static claims of F004, F005 and F007 listed under Observations
- **Experiment and runs**: none. Static analysis only; the artifact was never run. No `runs/` or `evidence/` record exists for this finding.
- **Artifact**: set `goal2-67cf27d6`, `GOAL.EXE` (packed sha256 `a6928b0bb7cda0303ac8daf8690efc56ef1792dddaccb5c6f3d85af1f68d3664`, the same file as in `goal2-a949da2f`), variant: none
- **Max intervention**: I1 (static analysis, `vocabulary/interventions.md`)
- **Tier reached**: V0 (nothing was run; every claim is about the decompiler's output and the listing, which a reviewer can re-derive with the commands under Reproduction)
- **Confidence**: unreviewed (status `proposed`) — static route only (Ghidra 12.1.4's decompiler against the capstone listing of F002); 10 of 10 hand-traced claims checked, 9 agree, 1 disagrees; the address mapping is tested (`tests/static/test_decompile.py`, which fails when the mapping is broken)

## Verdict

Yes, for reading the logic of ordinary Pascal routines: in `static/goal-exe/decompiled/` every routine sits under its listing address, and nine of the ten hand-traced claims read directly from it, formulas included. No, as a replacement for the listing in several places, and there the listing decides:
- where a routine waits on memory that changes by itself (the BIOS tick);
- where a far pointer's segment matters;
- where argument order matters;
- where a callee passes a result back in a flag or register its prototype does not declare. Ghidra then shows an unassigned input such as `in_CF`, as in 12 functions of the run-time segment 23E4 (O5).

## Answer

- `tools/static/decompile.sh`, given the released `GOAL.EXE` and an output directory, puts each routine of `routines.tsv` under its listing `SEGMENT:OFFSET`, run after run byte-identical; 723 of 726 routines decompile, 3 fail with a Ghidra exception, and Ghidra adds 3 functions of its own (`23E4:00D1`, `23E4:0B50`, `23E4:13EF`). `static:static/goal-exe/decompiled/README.md`
- Ghidra's x86 language gets real-mode near call and jump targets wrong unless each segment starts on a 64K linear boundary, so the tool places listing segment k at Ghidra segment k×0x1000 and remaps the relocations; at the listing's own segment numbers, the near call `1771:9810` (displacement wrapping to `10E7`) and the near calls across linear 0x10000 in segment 0791 go to wrong addresses (O1). `static:tools/static/ghidra/GoalSetup.java:13`
- Against the hand-traced claims (O2): F005's three agree (the tick loop `0791:97D0` calls `D733` when `DS:9A3E` is set, else `9564`; `A4A1` is the per-match set-up). `static:static/goal-exe/decompiled/seg_0791_06.c:1047`
- F007's four agree, including `1771:10E7`'s formula, which reads almost verbatim, and `1771:32EB`'s three branches with the 16-bit product. `static:static/goal-exe/decompiled/seg_1771_01.c:848`
- F004's LCG `214B:0688` (`seed·0x7ABD + 0x1B0F`, result 1..n) agrees. `static:static/goal-exe/decompiled/seg_214B_01.c:559`
- F004's delay calibration `214B:1DA7` **disagrees**: the decompiled view is an empty infinite loop with three blocks removed as unreachable, and no store to `DS:A9FF`; the listing counts loop passes during one BIOS tick, divides by 55 and stores the count at `DS:A9FF`. The decompiler treats the tick word `0000:046C` as ordinary memory, so a loop that waits for it to change never ends. `static:static/goal-exe/decompiled/seg_214B_02.c:364`

## Method

- Tool: `tools/static/decompile.sh` (this task). It unpacks `GOAL.EXE` with `tools/static/unlzexe.py` and checks the unpacked sha256 `6fd8c5ef…`. It then imports the result with Ghidra 12.1.4's MZ loader (language `x86:LE:16:Real Mode`, compiler spec `default`) in a throw-away project, headless, `-max-cpu 2`.
- `tools/static/ghidra/GoalSetup.java`, before the analysis, does four things:
  - it undoes the loader's `adjustSegmentStarts` heuristic, which had moved `2138:0000`'s 7 bytes into segment 1771;
  - it places listing segment k at Ghidra segment k×0x1000 (table in the output README; 2581 → B000) and rewrites all 1916 relocated segment words through that table;
  - it sets CS per segment and DS to the data segment;
  - it makes one function per routine of `routines.tsv`, named `f_SSSS_OOOO`, `__stdcall16far` when its body returns with RETF, else `__stdcall16near`.
- Ghidra's default auto-analysis then runs, and `GoalDecompile.java` decompiles every function with the default options. `tools/static/decompiled.py` writes Ghidra's addresses back in the listing's numbering (`DAT_b000_9a3e` → `DS:9A3E`; memory outside `GOAL.EXE`, such as the BIOS data area, → `ABS_0046C`) and splits the output per segment under 40,000 bytes per file.
- Reproducibility: runs give byte-identical output (`diff -r` prints nothing), equal to the committed `static/goal-exe/decompiled/`.
  - Once, in the rework, Ghidra's decompiler process died mid-run ("Decompiler process died" at `1771:602D`, which every other run decompiles), and that run's output differed.
  - `GoalDecompile.java` now retries a failed function up to 3 times, each with a fresh decompiler process.
  - The 3 genuine failures fail the same way on every attempt, so retries cannot change the output.
  - Three further runs were identical to each other and to the committed output.
- The check: for each claim under Evidence of T18, I read the decompiled function at the address `index.tsv` gives and compared it with the claim and with the listing lines the claim cites. I did not tune the scripts to the claims. The one change made after reading output (the 64K placement) came from a wrong call target that the listing contradicts (`f_1771_97CC` calling `func_0x000387f7` where the listing has `call 10E7`), before the table was drawn up.

## Observations

**O1. Address mapping.** `ia.sinc` (Ghidra 12.1.4, x86) defines `rel16` as `((inst_next >> 16) << 16) | ((inst_next + simm16) & 0xFFFF)` on the linear address. In a run with the loader's own layout (listing segment + 0x1000), `1771:97CC` decompiled with a call to `func_0x000387f7(0x2771,param_1)` for the listing's `9810 E8 D4 78 call 10E7`. That run left 2 routines without a function and made 810 functions in all; with the 64K placement, all 726 routines become functions and the total is 729. `tests/static/test_decompile.py` checks seven routines' names and first bytes at their listing addresses, the wrapping call, the calls across linear 0x10000, a far call and a relocated word. Run against a copy of `GoalSetup.java` that keeps the listing's segment numbers, the wrapping-call, 64K-crossing, relocated-word and DS tests fail. Without the relocation remap, the far-call and relocated-word tests fail. Without the `2138` fix-up, the probe of `2138:0000` fails.

**O2. The hand-traced claims** (each "agree" means the decompiled lines say the same as the claim and as the listing lines it cites):

| # | Claim (source) | Decompiled lines | Result |
| --- | --- | --- | --- |
| 1 | `0791:97D0` calls `0791:D733` when `DS:9A3E` is set (F005) | `seg_0791_06.c:1047` `if (DS:9A3E == '\0') {`, `:1067`–`1068` `else { f_0791_D733(); }` | agree |
| 2 | … else `0791:9564` (F005) | `seg_0791_06.c:1047`–`1061`: in the `DS:9A3E == 0` arm, the replay handling (`0C65`, `15B9`), then `f_0791_9564();`, then `8CF5` and `9119` only if `DS:9A3E` is still 0 (`:1062`–`1064`), as F005 traced | agree |
| 3 | `0791:A4A1` is the per-match set-up (F005) | `seg_0791_07.c:292` `DS:7C3A = 0` (commentary counter), `:296` `f_214B_0018(0xff,0x4b0,0x7c3e,0xb000)` (the ring filled with 0xFF), `:303` `DS:831A = f_214B_06FA()` (kick-off draw), `:346`–`350` `DS:9A3E`, `DS:9A3F`, `DS:7C38` cleared; `0791:F1F6` calls it (`seg_0791_09.c:1040`) before `F098` (`:1065`) | agree |
| 4 | `1771:97CC` writes the country number into the seed word, through the far pointer `DS:A978` (F007) | `seg_1771_05.c:1292` `*DS:A978 = param_1;` | agree. Neither view shows statically that the pointer targets `DS:7B62` (F007 takes that from F004); the decompiled line hides that `DS:A978` is a far pointer |
| 5 | … before calling `1771:96D3`, 20 times (F007) | `seg_1771_05.c:1297`–`1303`: `local_4` 1..0x14, each `f_1771_96D3(1, <block-10 byte>, param_1, …)`, after `:1292` | agree (arguments shown in reverse Pascal order: F007's `96D3(player, c, position, 1)`) |
| 6 | `1771:10E7` = `((5 − [+0x2C]) · (0x21 − [+0x2A]) + (0x81 − [+0x2B])) idiv 2` (F007) | `seg_1771_01.c:848`–`849` `return (int)((0x81 - [+0x2b]) + (0x21 - [+0x2a]) * (5 - [+0x2c])) / 2;` over the record `DS:A917 + c·0xBF` (`:847`) | agree |
| 7 | `1771:32EB` computes +4 from +1, +2, +3 (F007) | `seg_1771_02.c:878`–`891`: +4 = +3 unless `+1 < +2` or `+2+3 < +1`; then k = 16 − (+1 − (+2+3)), or 16 − ((+2 − +1) / 2) signed; +4 = low byte of `(+3·k & 0xFFFF) / 16` (the listing's `mul`, `xor dx, dx`, `div cx`, `seg_1771_05.asm:361`–`366`) | agree |
| 8 | `214B:0688` is the LCG `seed·0x7ABD + 0x1B0F` (F004) | `seg_214B_01.c:559`–`560` `uVar1 = *param_2 * 0x7abd + 0x1b0f; *param_2 = uVar1;` | agree |
| 9 | … returning 1..n (F004) | `seg_214B_01.c:561` `return (int)((ulong)uVar1 * (ulong)param_1 >> 0x10) + 1;` (high word of seed·n, plus 1) | agree |
| 10 | `214B:1DA7` calibrates a delay into `DS:A9FF` (F004) | `seg_214B_02.c:357`–`366`: three "Removing unreachable block" warnings (`214B:1DCE`, `1DD9`, `1DEF`) and `do { } while( true );`; no read of the tick, no division, no store | **disagree**: the listing (`seg_214B_04.asm:44`–`69`) waits for `0:046C` to change, counts passes until it changes again, divides by 0x37 through `23E4:0294` and stores the dword at `DS:A9FF` |

**O3. Counts** (`static/goal-exe/decompiled/README.md`, `index.tsv`): 726 routines in `routines.tsv`; 723 decompiled; 3 failed, each with `AddressOutOfBoundsException` (`0000:0000`, the entry, "got 0xffffffff"; `0791:1A04`, "got 0xb0002e8e"; `214B:05F0`, "got 0xb00079a4"); 0 without a function; 3 functions Ghidra's analysis added. 31 files of C, the largest 39,914 bytes.

**O4. What the decompiled view showed wrong or hid, besides claim 10** (examples, not a census):
- *Far pointers.* An `ES`-based access through a far pointer reads as a near access to the pointer's offset. In `214B:0D90` the cursor's cell in the video buffer is `*(uint *)(iVar3 + …)` with `iVar3 = (int)DS:A96A` (`seg_214B_01.c:1011`–`1021`), and the segment from `DS:A96A + 2` is dropped. In `1771:10E7`, `uVar2 = (ulong)DS:A917 >> 0x10` is computed and never used (`seg_1771_01.c:846`). `214B:0688` takes a near `uint *` (`seg_214B_01.c:554`), while its callers pass `DS:A978` as offset and segment (`:572`, `:584`, `:596`).
- *Argument order.* Turbo Pascal pushes arguments left to right; Ghidra's prototypes list them right to left. `FillChar(DS:7C3E, 0x4B0, 0xFF)` reads `f_214B_0018(0xff,0x4b0,0x7c3e,0xb000)` (`seg_0791_07.c:296`; listing `seg_0791_17.asm:273`–`280`).
- *Segment numbers* in the code are Ghidra's (`0xb000` is the data segment 2581). An indexed data address may stay a signed number: `*(undefined1 *)(local_5 + -0x7f10)` is `DS:80F0[i]` (`seg_0791_07.c:320`, in `A4A1`).
- *Pascal strings and sets* have no types. A string is `&DS:XXXX` (look it up in `strings.tsv`), and a set is a byte array handled by run-time calls, e.g. `f_214B_0018(0,0x20,local_26,unaff_SS)` clearing a 32-byte set in `0791:D733` (`seg_0791_08.c:1161`).
- *Nested procedures* receive the parent's frame as `&stack0xfffe` (`f_0791_F098(&stack0xfffe)`, `seg_0791_09.c:1065`); what the parent's locals are is not shown.
- *Reads of the BIOS tick that are not a loop's only exit survive*: `214B:0D90` blinks on `ABS_0046C / 3` (`seg_214B_01.c:1017`), and `0791:F3F2` stores the tick into `DS:8336` (`seg_0791_09.c:1136`), as F004 and F005 traced.

**O5. Flags and registers passed back across calls** (review R1 on PR #54). Turbo Pascal's run-time routines return success in the carry flag and results in registers outside any prototype Ghidra knows. The caller's use then reads as an unassigned input:
- `23E4:0341` (`seg_23E4_01.c:421`–`427`) calls `f_23E4_04D8()` and branches on `in_CF`. The listing calls `04D8` at `034D` and branches on the carry it returns at `0350` (`jb 0x355`, `seg_23E4_01.asm:381`–`382`), and `04D8` sets carry on its failure path (`050E stc`, `:587`).
- `23E4:0329` (`seg_23E4_01.c:404`–`411`) branches on `in_CF` and returns `in_CX` after `f_23E4_041D()`. The listing branches on `041D`'s carry (`0332 jb`) and returns `041D`'s CX:BX as AX:DX (`0334 mov ax, cx`, `0336 mov dx, bx`; `:366`–`369`). The decompiled `0341` also shows no parameters, while the listing reads its arguments through `bx = sp` (`:377`–`380`).
- The procedure-variable call at `23E4:0484` (`lcall [0x7b4e]`) reads `(*DS:7B4E)(0xa000,in_AX)` (`seg_23E4_01.c:571`). It keeps the indirect call but not its prototype: the far-pointer and argument-order limits of O4 apply.

The count, per segment, of functions reading an unassigned input (`python3 tools/static/ghidra/count_inputs.py static/goal-exe/decompiled`). "After a call" means the first read follows a call in the body:

| Segment | Functions | Flag input | … after a call | Register input | … after a call |
| --- | --- | --- | --- | --- | --- |
| 000E | 58 | 0 | 0 | 0 | 0 |
| 0791 | 282 | 0 | 0 | 7 | 2 |
| 16D6 | 26 | 0 | 0 | 3 | 1 |
| 1771 | 154 | 0 | 0 | 2 | 1 |
| 2138, 2139 | 2 | 0 | 0 | 0 | 0 |
| 214B | 84 | 0 | 0 | 2 | 2 |
| 235C | 12 | 1 | 0 | 4 | 3 |
| 2382 | 17 | 0 | 0 | 4 | 1 |
| 23E4 | 91 | 12 | 12 | 37 | 11 |
| all | 726 | 13 | 12 | 59 | 21 |

All 12 flag reads after a call are in 23E4, the run-time library: `0329`, `0341`, `0C93`, `0CA5`, `0CC5`, `16BE`, `1703`, `173B`, `1828`, `1868`, `1899`, `18FA`. Game segments 000E–1771 have none. Of the 10 register reads after a call outside 23E4, I checked three:
- in `0791:2BB1` (`seg_0791_02.c:629`) and `0791:92FC` (`seg_0791_06.c:772`), `in_AX` is the don't-care high byte of a byte argument passed in AX, not a returned value;
- in `1771:5A38` (`seg_1771_03.c:1255`) Ghidra assigns its `in_AX`.

The other 7 were not checked. A further 844 uses of `unaff_SS` are the stack segment of far pointers to locals, which is harmless.

No Ghidra option or per-routine override was added. A carry-flag return cannot be declared in a Ghidra prototype without custom storage on each run-time routine, and the cases are confined to the run-time library, which F004–F007 never cite. So this is documented rather than patched.

## Inferences

- The decompiled view can be read in place of the listing for some things, in a function that reads no unassigned flag or register input (`in_CF`, `in_ZF`, `in_AX`, …; O5) and is not a hardware wait. Those things are: control flow on values the function itself computes or loads, which call targets are taken (near, far and `push cs; call near`), arithmetic on bytes and words, and `DS:XXXX` data. About 85% that a later claim read there holds in the listing, from 9 of 9 such claims here and the mapping tests. `static:static/goal-exe/decompiled/seg_1771_02.c:878`
- It cannot be trusted, without the listing, for: loops on memory changed by interrupts or hardware (`ABS_xxxxx`); far-pointer segments; argument order against the Pascal source; the 3 failed routines; signed data offsets. A claim resting on any of these cites the listing. `static:static/goal-exe/decompiled/seg_214B_02.c:364`
- Nor for results passed back across a call in a flag or a register outside the callee's prototype. Every flag or register input (`in_CF`, `in_AX`, …) read after a call may be such a result, and 33 functions show one (12 flag, 21 register; O5). In segment 23E4, the run-time library, the branch or return there is wrong as written: `23E4:0341` tests `in_CF` where the listing tests the carry `04D8` returns. `static:static/goal-exe/decompiled/seg_23E4_01.c:422`

## Alternatives considered

1. *The 9 agreements are the decompiler copying the listing's bias.* Both views decode the same bytes, but with different tools: capstone and Ghidra's SLEIGH. The claims were traced by hand from capstone; the decompiled view was not tuned to them, and it disagreed where it is wrong (claim 10), so it is not just echoing them. Partly excluded: a shared decoding error in both tools would not show.
2. *The mapping is right for the tested routines only.* The 726 routines' names come from one rule (`toGhidra`), and all 726 got functions. Tested at 7 addresses in 5 segments, the wrapping call and the 64K crossings. Not excluded for every address, but a wrong rule would show at the tested ones.

## What this does not establish

- That a routine absent from the ten claims decompiles right: the rate of 9 in 10 is from a small sample chosen by what was traced, not at random.
- Whether a volatile range for the BIOS data area (0000:0400–04FF) would make `214B:1DA7` decompile right. It was not tried, so that the table reflects the default analysis.
- Jump tables (`case` statements), which neither this check nor the claims visited.
- Whether the 7 unchecked register reads after a call outside 23E4 (O5) are returned values, and whether a flag or register result Ghidra models silently, with no `in_` name, occurs anywhere. The count finds only what Ghidra names.

## Where the evidence is

`static/goal-exe/decompiled/` (the output, `README.md`, `index.tsv`), `static/goal-exe/code/` (the listing), `tools/static/decompile.sh` and `tools/static/ghidra/`; no run records, no evidence bundle.

## Reproduction

`python3 tools/fetch_artifact.py goal2-67cf27d6`, then `bash tools/static/decompile.sh .cache/artifacts/goal2-67cf27d6/GOAL.EXE /tmp/out` twice and `diff -r /tmp/out static/goal-exe/decompiled` (prints nothing). Ghidra 12.1.4 and a JDK 21 as in `docs/environment.md`. The mapping tests are `python3 -m unittest discover -s tests/static`.
