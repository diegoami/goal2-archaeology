# T124b1 evidence

[confirmed: F017/F023; `seg_1771_02.asm` 114B..11DE and
`seg_1771_09.asm` 5EE1..6616, read after the named view] The seven ports preserve
same-continent rank counting, unsigned descending quicksort (including equal and
self swaps), placement/group point ordering, old manager best ranks before new
country ranks, world-best **else** continent-best, signed score clamping, all128
manager record writes/resets and the real near/far return frames. Main's independent
`main_call_audit.py` maps all28 static calls, return PCs, argument counts and callee
cleanup, including recursive sort calls and PUSH CS near encodings of far calls.

Static reading determines the implementation; the differential runs corroborate
it. `prove.py` runs the focused direct edge calls and an unmodified original
play_round continuation from the T124t round3 checkpoint (hash4c1c7635...).
The checkpoint is already stage4, rounds1, cursor1353/count1361: the original
remaining final fixtures and stage end construct stage5, cursor1361/count2001,
year word1. The original outer76B1/6730 and year rollover remain original.

`natural-final.jsonl` compares the paired original and ported **completed round**:
all physical memory, all16 CPU registers, waiting key and complete ordered route
records are identical, in addition to the normal T59 checks. 63A4 is proved once;
114B, sort5EE1, bonus5FD1, continent bonuses6103 and group points61F8 are nested
within its proof. World bonuses602D are absent on this natural mode1 path.

`world-prepare-v4.jsonl` supplies a separate **declared synthetic world** case.
It starts the hash-verified original T124t round4 checkpoint, already stage5 with
its complete qualifying draw. Original6970 processes640 qualifying fixtures;
original76B1/7090 builds16 playoffs, 71B2 builds368 friendlies/finals, and74BE
builds8/4/2/2 knockout fixtures. All1040 results use the complete original6970
body, including D47E, B7FA, B602, D050, BC5D and pages. No result or group/rank
record is fabricated. Stage/round dispatch edits are individually recorded;
preparation bypasses managed-match UI routing and is not a natural played season.
Country ownership tags and manager count stay unchanged. Original A3DE/B11F and
BC5D/52CC may reorder squads, including managed squads; before/after hashes retain
those effects. Seven private intermediate checkpoints hold full memory, all16 CPU
registers and waiting key; their hashes/context are public, original bytes ignored.

The prepared world ends at stage8/rounds1/cursor=count2401/year1, with original-built
knockout start2385, third-place fixture2399 and final2400. `world-proof-v2.jsonl`
then compares actual play_round8→2 on the **same** prepared input: stage2/rounds1,
cursor1/count769/year2. World bonuses602D and4 nested placement bonuses are now
reached. All physical memory, all16 CPU registers, waiting key and ordered route
records are identical. Original80DA in this reference harness establishes no
sealed year-rollover implementation.

`synthetic-final.jsonl` declares27 direct calls:25 pass and2 required falsifiers
are caught. Each specifies base E006 state hash, mutated input-memory hash before
the declared call frame, real caller return address, target/arguments, source
hashes and per-routine proved/nested counts. It covers unsigned high points,
ties/self swaps, singleton ranges, both mode loops, stage2's table selector,
signed score extremes, both best-rank branches and explicit manager best values.
An extra flag255 edge intentionally aliases the points high byte: the original
bonus writes564, then its signed-flag counter increment makes820 (counter3).
This is a synthetic ABI edge, not a claim that a normal builder passes flag255.
Both required mutants are also caught on the natural completed-round input.

Tests: the exact final8 new Rankings tests fail on archived unchanged main953b57ee
with15 errors;23 focused new/preserved tests pass on the implementation. Only the
existing registry map and required variant CASES receive additive mechanical
updates in test_port_stages.py, preserving all old7 entries/14 variants/behavior
assertions. The full suite is left to CI. Annotation validation and regenerated
named view are included.

`baseline-v1`, `calibration-v1`, `ports-v1`, `*-v1/v2/v3` receipts retain calibration
history. Earlier host-only failures were the signed-flag overlap assertion,
public byte serialization, annotation basis syntax, and unsupported assumptions
that original silent updates leave squad ordering unchanged. World preparationv3 also used7016 as6970 returnPC; main caught the static frame mismatch (actual7014 CALL returns7017), corrected in world preparationv4. These calibration versions are not used
as final acceptance. `acceptance/index.json` identifies accepted source/receipts.
The proof contract remains standard T59: strict AX/DX/SP/BP/SS/DS/CS/IP and ordered
live/caller writes, dead frame/scratch handling as documented there. Whole-memory
and all-register equalities above are extra measurements for those completed
rounds, not stronger claims for every direct call.

Model: inherited Codex GPT-6 family, exact variant unavailable. No review is
started by this PR. No sealed full-season or year-rollover claim.


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
[T124d's index](../T124d/acceptance-v2/index.json); track the correction in
[issue673](https://github.com/diegoami/goal2-archaeology/issues/673).
