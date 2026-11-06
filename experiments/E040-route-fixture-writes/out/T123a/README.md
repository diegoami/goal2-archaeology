# T123a speaker-on ABI evidence

Method: read named `seg_214B_02.c` speaker-on first, then raw decompilation and
`code/seg_214B_04.asm` 1E75–1E8C. Twelve instructions determine the frame, mute
branch, AL-only update and CMP/OR flags. Static analysis cannot establish the
reference machine's unhandled IN61 value; original-backed controls corroborate
it directly at 1E85, after IN and before OR. T73's speaker return receipt agrees.
The original OUT instructions remain omitted by the accepted T123 design; this
leaf implements no hardware audio or sound assets.

`baseline-v1` and `calibration-v2` are immutable calibrations, not acceptance.
The latter records both new final tests failing against the original stub
(169 failures), restores the saved implementation, and retains early annotation
schema/proof-root errors with their successful corrections. Named regeneration
completed via the prescribed Ghidra command; its output changes only the relevant
speaker-on heading. Acceptance receipts name an exact subsequently frozen commit.

Inputs: mute bytes 0,1,3,FF; AX1234,AB00,00FF; flags 0202,0203,0206,0242,0282,0A02,
0ED7; distinct high register words, BP6789, SS:A000, entry SP EFF4. Far return
frames target 9F00:0010 and same-CS:0010 (the push-CS/near-call form). The routine
always retf with zero argument cleanup, so final SP is EFF8 and BP6789 remains
in the dead frame at EFF2. Every original comparison includes all machine REGS,
all EFLAGS bits and complete memory, including live game/RNG and dead frame.
The denial subprocess positively refuses Unicorn imports and EXE reads before
28 real registered PortMachine calls; it checks explicit AX/AH/flags/stack/PC
and a hand-derived complete memory image. No new stub or fallback is installed.

Falsifiers execute the actual registered function source with one expression
changed in memory, without editing files: enabled-al-loss retains incoming AL
instead of 03h; mute-condition-inverted runs the enabled body on nonzero mute.
The original-backed tests catch both (42 and168 failing controls respectively).

Model: inherited Codex GPT-6 family, exact variant unavailable. Full-suite and
CI gate are left to CI; no local full suite/gate was run. Main owns merge.
