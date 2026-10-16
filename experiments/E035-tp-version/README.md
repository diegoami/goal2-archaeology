# E035: which Turbo Pascal built GOAL.EXE (issue 256)

Question: which Turbo Pascal compiler built `GOAL.EXE`, and is more worth doing (names for the runtime, library
signatures, Reko)?

## Answer

**Turbo Pascal 5.5.** Of six candidate compilers (4.0, 5.0, 5.5, 6.0, 7.0, 7.01), only 5.5's System unit reproduces
GOAL's System segment (`23E4`, 6,608 bytes, 2,969 instructions).

Method (static first, rule 22; the only runs are the compilers compiling our own probe, inside DOSBox-X):
compile `probes/t4.pas` (our program, touching most of System, Crt and Dos) with each candidate's `TPC.EXE` + `TURBO.TPL`
(`run_all.py`), cut the System segment out of each result (the target of the entry routine's first far call, up to the
data segment), and compare it with GOAL's by instruction skeleton (capstone; immediates, displacements and data offsets
masked, because the System variables sit at other data-segment offsets in GOAL).

| candidate | GOAL System instructions reproduced (blocks of 4 or more) | of the 88 System routines the project names, fully reproduced | Dos unit (235C) | Crt unit (2382) |
| --- | --- | --- | --- | --- |
| 4.0 | 79.1 % | 63 | 36 % | 99 % |
| 5.0 | 89.5 % | 79 | 99 % | 100 % |
| **5.5** | **99.7 %** (2,961 of 2,969) | **86** | 99 % | 100 % |
| 6.0 (6-11-1991) | 74.3 % | 59 | 99 % | 98 % |
| 7.0 | 57.8 % | 41 | 58 % | 92 % |
| 7.01 | 57.8 % | not tabulated (as 7.0) | 58 % | 92 % |

(`outputs/20261017a/`: `run.log` with sha256 of every image, compiler file and built exe and the per-routine table; `cover.*.txt`,
`gaps.*.txt`, `bytecmp.55.txt`, `startup`/`movecheck` lines in `run.log`, `t7.*.log`). The older `20261016*` folders are the same runs
before the generator stopped printing bytes; see `outputs/NOTE.md`.)

Structural clues, each checked against the candidates' own output:

- Start-up (`startup.py`, in `run.log`): the first 0xA0 bytes of the System segment have skeleton similarity 1.000 with 5.0
  and 5.5, 0.903 with 6.0, 0.851 with 7.0 and 7.01, 0.331 with 4.0. 6.0 stores `es:[2]`, a constant and CS in extra
  stores and lacks GOAL's `mov ax,es:[2]; sub ax,N`; 7.x adds two calls and a `mov es,[N]`; 4.0 has no vector-save loop.
- The table of saved interrupt vectors has **18** entries, identical to the table 5.0 and 5.5 compile; 6.0 and 7.x
  tables have 19, the extra entry being INT 21h (`startup.py`).
- The block-copy helper at `23E4:025D` (named `sys_move_025D` in the project; callers pass 4000 for a screen) is a plain
  `cld; rep movsb`. Probes show it is what the compiler calls for an array assignment `a := b` (`probes/t5.pas`: helper
  present, public Move absent); the public `Move` is another, overlap-safe routine (it uses `std`; `probes/t6.pas`: Move
  present, helper absent) that GOAL does not contain. So the original source wrote `screen := backup`-style
  assignments, not `Move` (`movecheck.py`, in `run.log`; the helper's offset differs per program because System is
  smart-linked, so no offset is claimed).
- 5.0 vs 5.5 (the two close ones): GetMem, FreeMem and heap allocation (`0329`, `0341`, `041D`), `Pos` (`06E3`) and the six-byte
  Real add, multiply and divide (`098F`, `0A52`, `0B57`) are not reproduced by 5.0 (0 to 76 % of each routine; the
  routine table in `run.log`) and fully by 5.5; `gaps.50.txt` has 17 stretches, the largest 191 instructions (403 bytes,
  inside the Real arithmetic). The 5.5 gaps (`gaps.55.txt`) are four stretches of 2, 3, 2 and 1 instructions (6, 6, 6 and 1
  bytes, 19 bytes in all): two (`118F`, `11DE`) are data containing data-segment offset words that decode as
  instructions, one is the two-instruction start of `Str(longint)` (`12FC`) that my probe laid out differently, one is a
  padding byte (`19CF`). `bytecmp.55.txt`: of the 2,961 matched instructions, 2,829 have identical bytes; the 132 others
  differ in a data-segment offset or a call displacement, in ten of them with the changed field inside the instruction
  (not at its end).
- No overlay manager or FBOV marker in GOAL (the game does not use overlays). That fits any version from 5.0 and says
  nothing about which.
- GOAL's Dos unit (235C) has `FindFirst`/`FindNext`, `Exec` and a `GetEnv`-like routine (the project's names). 4.0's Dos
  has no `GetEnv`: compiling the full probe with 4.0 stops at it with "Unknown identifier" (`t7.40.log`; 5.5 builds it,
  `t7.55.log`; `probes/t4_40.pas` leaves it and other calls out so that 4.0 can be compared at all). A point against 4.0,
  weaker than the System comparison.

What could not be settled, and why:

- Whether a later build of 5.5 (the set here has one) would also match: not testable with the material at hand.
- The compiler switches ({$S}, {$R}, {$N}, {$G}) of GOAL's own code: not compared (only the runtime was).
- Only the System, Crt and Dos units were compared; GOAL's own units (`0791`, `000E`, `1771`, `214B` ...) are the author's
  and say nothing about the compiler except through its code generation, which a rebuilt Pascal source could test
  (see Recommendation).
- The 0.3 % of the System segment not reproduced (8 instructions) is data and one two-instruction fragment, see above.

## Is it worth more?

What the answer already buys (at the cost of this experiment; no run of the original game was needed):

- The System unit's 88 routines are already named in `static/goal-exe/annotations/routines.tsv`, Crt (2382) and Dos (235C)
  too; no routine in `23E4`, `2382` or `235C` is unnamed. A set of names from signatures would add nothing there.
- The runtime's semantics can be taken from a documented compiler: six-byte `Real`, `Str`/`Val`/`Pos`/`Copy`, the
  longint and set helpers (`0279`, `0294`, `08DF`...) are TP 5.5's (byte-identical shape). The game's own random numbers
  come from its LCG at `214B:0688` (`x*31421+0x1B0F`, per the project's annotations), not from a System routine I
  compared. The remaining engine work is the game's own code; reading it does not need more runtime naming.
- **A compile-and-diff oracle exists.** `TPC.EXE` 5.5 runs in DOSBox-X in about a second (`dbx.py`, 1.5 s for six
  compilers), so a port's Pascal-level transcription of a routine can be compiled and its bytes compared with the
  original's (the ZZT precedent). That is the one capability this opens; it costs per routine and is worth using only
  where a decompilation is in doubt (the 16-bit overflow and `Real` rounding cases), not as a general step.

Recommendation: stop here for naming. Do not build FLIRT or Function ID signatures: the only code they could name is
the runtime, which is named, and a signature database from six compiler variants would be a build step with no reader.

## Reko (0.12.5, tried)

`reko/excerpts.md`. Reko 0.12.5 (Windows `CmdLine` zip) runs on Linux with the .NET 8 runtime unpacked into a scratch
directory (no install), detects MZ real mode on its own, has an LZEXE unpacker built in and decompiled the whole 185 KB
image in 66 s. Compared with the project's Ghidra view on three routines (`Pos` `23E4:06E3`, the LCG `214B:0688`, the
Real multiply `23E4:0A52`):

- Adds: register-argument routines get real signatures (Reko inferred `dx, bx, si, di` inputs and `ax, dx, bx` outputs for the
  Real multiply, where Ghidra shows `void` and a bare `undefined4`), list of callers per procedure, 32-bit arithmetic idioms
  folded (`ax * 31421 + 0x1B0F`).
- Costs: one procedure failed (`fn0800_00E2`), anonymous `Eq_NNN` types, a wrong string-scan loop in `Pos`
  (the compare reads after the increment), flag tests turned into `< 0x00` nonsense in the Real multiply, 20 MB of output
  that mostly repeats Ghidra's, no segment model for BIOS accesses. Its output does not use the project's names, so each
  use is a manual cross-read.
- Verdict: not worth adopting. It could be used as a second opinion on register-argument runtime routines, which are
  already named and match 5.5's. The setup is not recorded as a project requirement (downloaded to a scratch directory;
  re-do from this section if wanted).

## Assumptions

- The skeleton comparison is a fair stand-in for a byte comparison: the masked fields are exactly those that move with
  the data layout (checked by `bytecmp.py`: of 2,961 matched instructions, the 132 that differ in bytes differ only in
  the fields the skeleton masks: a data offset, an immediate or a call displacement).
- The System unit in a compiled EXE is the smart-linked subset the program uses, so a candidate can only be compared on
  the routines my probe links (`probes/t4.pas` was written to link most of System; 86 of 88 routines are reproduced by
  5.5; routines the probe did not link would show as a gap for every candidate alike, and the 5.0-versus-5.5 gaps
  are in routines the probe does link).
- The floppy images are what they claim to be (WinWorldPC); their hashes are in `outputs/20261017a/run.log`.

## Files

- `fat12.py`, `dbx.py`, `sysseg.py`, `cover.py`, `gaps.py`, `bytecmp.py`, `routines.py`, `units.py`, `startup.py`, `movecheck.py`, `pick.py` (one match from a glob, or an error), `selfcheck.py`
  (proves that rule fires on two matches), `hexscan.py` (counts hex runs of more than 8 bytes in the tracked files), `run_all.py`: tools
  (`run_all.py SCRATCH OUT` redoes everything; it reads the keep directory's images and the released `GOAL.EXE`).
- `probes/`: our Pascal test programs.
- `outputs/20261016a/` (first run), `20261016b/` (with the Dos/Crt probes), `20261016c/` (with the Move probes) and
  `20261017a/` (the run the table cites; the generator no longer prints bytes). The four agree on the System numbers.
  Older folders: byte columns removed, see `outputs/NOTE.md`.
- `reko/excerpts.md`: Reko excerpts. No Borland file and no GOAL file is committed, and no output carries bytes of GOAL (offset, length and sha256 instead).
