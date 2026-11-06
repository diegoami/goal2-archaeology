# T124b2 qualifying draw and calendar evidence

[confirmed: F023/F004/F017; named1771 parts4/5, raw1771_08 56E4..577E,
1771_09 6730..6B54 and23E4_02 11D7..11E3] Four routines are transcribed:
continent offset56E4, draw order56FF, complete qualifying builder6730 and the
reference seed service23E4:11D7. Static reading determines the loops, call frames,
word wrap, table offsets and effect order; the runs corroborate that transcription.
`call_audit.py`, adapted from main's B1 verifier, matches all17 static call sites,
near/far forms, return PCs, argument words and actual callee cleanup.

The complete eleven-routine T124b aggregate includes merged B1's ranking helpers.
`prove.py` installs those and the old fixture helpers, plus the REAL direct
callees0018/003C/007B/06B1,0B77,10E7 and display5C94/5CCB. No stub is installed.
The original outer76B1, stage_end and80DA remain original reference code.

`natural-draws-v3.jsonl` restores unmodified native T124t checkpoint3 (all16CPU
registers and waiting key included), finishes its remaining final fixtures and
executes actual play_round4→5. `world-draws-v3.jsonl` restores B1's corrected7017
synthetic world input f5610eca... from world-prepare-v4 (all original constructors
and1040 original6970 updates), and executes actual play_round8→2. The latter is
explicitly synthetic preparation, not a natural played world season. Original
rollover in either reference harness proves no sealed rollover implementation.

Both completed-round comparisons are exact for full physical memory, all16CPU
registers, waiting key, complete ordered route records and full country/manager/
group/calendar/game regions. Each whole6730 is proved once; B1 ranking routines
are nested. Natural mode1 appends640 fixtures; world mode0 appends768. Every
builder has actual06B1 entry/return observations:64calls at680D(bound8),64at682C
(bound8),32at68E2(bound4), retaining each seed before/after and actual choice in
order. Each natural/world site visits every possible choice1..8 or1..4. The first
pointer remains on the stack across the second shuffle draw, as in the listing.

`direct-draws-v3.jsonl` records16 declared direct calls:14 pass and2 required
mutants are caught. The two whole INITIAL-year builders use real registered
library implementations too, preserving003C's normally-scratch CX through56FF
into11D7. Entry/return observations explicitly compare incomingCX/DX with saved
7B62/7B64 and AH=2C (the native builder inputs give CX0/DX4/AX1→2C01); three
additional service edges cover nondefault register values. Reference Machine
swallows INT21: no DOS wall clock is observed and no host clock is invented.
The synthetic initial mode1 branch reuses native country/manager/order data and
valid constructor ABI; it is not claimed as a naturally reached stage5/year0.

The direct edges also cover offset word wrap, the129-byte mode0 copy including
its leading sentinel, unchanged bytes after it, and stable per-continent filtering
of a reversed world order while preserving incomingCX. Required mutants reverse
pot draw order or change a qualifying fixture's group argument. Both also fail on
the actual natural construction, retained in the final natural-mutant receipts.

The exact seven final Draw tests fail on archived unchanged prerequisite main
9f5cd1f6 with17errors. Draw+Rankings+preservedStages pass30tests in34.623s. The
source binding receipt proves the tested runtime/test files unchanged on final
source. Full suite is left to CI. Existing exact registry and variant maps receive
only additive entries (four new routines, two required mutants and the actual
6730return PC), preserving every old14routine/16variant entry and old behavior.

Calibration history stays immutable. Installing the ENTIRE existing entrypoints
module in a proof double-registers0688 while06B1 intentionally inlines that body's
implementation through R.invoke; Prover then expects an extra nested0688 return.
The failed whole-module setup is retained under calibration-v1. Final tests/proofs
select the same REAL06B1 entry and its real inlined0688 body, without registering
an additional inline-callee observer. This changes neither RNG implementation nor
Prover, and introduces no stub or exemption. The complete scalar/write/draw and
caller-frame oracles remain strict.

The proof contract remains standard T59: strict AX/DX/SP/BP/SS/DS/CS/IP and ordered
live/caller writes, with its existing dead-frame/scratch handling. Full-memory and
all-register equality are extra measurements for the two completed rounds only.
No new normalization, dead-result exemption, year-rollover port or full-season
completion claim is made. Final source/receipt hashes are in acceptance/index.json.
Model: inherited Codex GPT-6 family; exact variant unavailable.


## Evidence correction, 2026-11-06 — upstream #673

The historical B1 `world-prepare-v4` recipe called original6970 but omitted the
outer route's8757 finalization (which calls85F7 for playoff aggregates and sorts
group tables). Aggregate2401 was still255/0 with flag0 although its two completed
legs totaled5/3. Thus v4 and its derived world/bracket inputs were not faithful
completed-world inputs. The retained differential results still describe the
input actually measured; they **do not establish the completed-world validity
previously claimed**. This is an evidence-input defect, not an established
production-port mismatch. Continental naturalCP3 and initial-year seed proofs
that do not consume those world inputs are unaffected.

Replacement evidence is owned by [T124d](../T124d/README.md): fresh ORIGINAL
T124tCP4 play_round/RouteMatch/legal-eleven continuation, actual8757/85F7 after
complete calendars, all world constructors, real world finals and subsequent
8→2 whole-qualifying regression. New corrected synthetic controls explicitly
include actualouterRoute finalization after every calendar and remain labelled
synthetic. All eight aggregates, leg relationships, actual original85F7 output
and5C94 winner semantics are independently checked; no host scores/ranks/flags.

Historical runners, measured receipts and indexes remain immutable at their
recorded source-freeze heads. This factual README addition does not rewrite or
re-hash those old measurements. Current accepted replacement files/hashes are in
[T124d's index](../T124d/acceptance/index.json); track the correction in
[issue673](https://github.com/diegoami/goal2-archaeology/issues/673).
