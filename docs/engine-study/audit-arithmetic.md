# Arithmetic audit: quirks, wrong inferences and surviving edge questions

The first audit does not reproduce a port arithmetic defect. It identifies two original
arithmetic quirks, qualifies a previously inferred tactic benefit, and rejects a suspected
off-by-one interpretation by reading the instructions. These are bounded conclusions about
four named candidates, not a clean bill of health for the whole engine.

The [candidate ledger](../../notes/engine-study/T108/T108a-v1.json) pins primary sources,
minimal inputs, expected/actual source behaviour, dispositions and reachability limits.
[arithmetic.py](../../notes/engine-study/T108/arithmetic.py) reproduces local arithmetic and
controls using the existing T98 source-derived projections. It executes no original or port
routine and does not supply a new observed match. All attributions remain proposed pending
independent ES-R2 review.

## What counts as a defect

| Candidate | Disposition | What is established here |
| --- | --- | --- |
| Form 31 to 32 | Original quirk | Both skill and strength take a different signed branch at 32. A continuous “higher is better” assumption is false. |
| Negative ceiling-profile leadership | Original quirk on a representable input | Signed remainder followed by unsigned halving produces a large word. Natural reachability remains unestablished. |
| Half-pitch following benefit | Documentation/inference defect under stated conditions | An earlier target rejection already guarantees the later sign guard for on-pitch targets. Full pitch still affects depth. |
| Equality/strict threshold suspicion | Unsupported suspicion of a port bug | Original instructions and port agree at the examined offside-target and activity edges. |

An original quirk is something a faithful rewrite must preserve. It does not imply an
author-intended bug or authorise changing game balance. A source calculation is also distinct
from an original-versus-port execution comparison. Where a new execution would settle an open
question, its design and cost belong to T105/T106, after the ES-R2 gate.

## Arithmetic candidates

**Form is not a continuous numeric scale across 32.** In `0791:278A`, signed form below 32
contributes `form+1` to the condition word; at or above 32 it contributes zero. At ability
180/profile 8/natural role 2, element 3, energy 32, no placement penalty or venue share, the
worked effective skill is 72 for form 31 and 54 for form 32. This element does not add the
cached extra, so captain/manager context does not explain the drop.

`1771:377E` has its own branch: below 32 it adds signed form; otherwise it subtracts a
sixteenth of the signed intermediate, using division toward zero. At ability 225/energy 32,
without placement halving, strength is 226 at form 31 and 183 at form 32. These outcomes
agree with the rules already documented in the foundations. They do not establish that a
real player's form just increased, or that 32 should mean “one point better.” The branch's
meaning and its storage representation must be preserved before imposing a modern rating scale.

Changing the cutoff to 33 in the effective-skill calculation gives 73 instead of 54 at the
same form-32 edge. The control is rejected. Repairing the apparent discontinuity would change
original behaviour; it is not a readability-only transformation.

**Leadership mixes signed and unsigned arithmetic.** `1771:30D9` reads unsigned creation
ceiling/rating at player `+3` and profile at `+5`, subtracts them, uses signed `IDIV 8`, then
retains the remainder word. If age is below 21 it uses unsigned `DIV 2` on that word.
Normal nonnegative differences produce the familiar 0..7, or halved 0..3, values.

For the representable input ceiling 0/profile 1, signed remainder is -1, stored as 0xFFFF.
At age 20 unsigned division produces 0x7FFF (32767); at age 21 the result remains 0xFFFF
(65535). Python `(-1)%8//2` instead gives three. That is a change of the original rule,
not a safe simplification. Twice either returned value has low byte 0xFE, which can affect
the captain cache addition as a wrapped byte rather than as a natural 0..14 bonus.

The audit has not established a creation/lifecycle path with ceiling below profile. Do not
report this as a naturally occurring super-captain, a confirmed crash, or a port discrepancy.
The existing attributes port preserves the instruction arithmetic. The all-unavailable
leader-selection return is a separate record/control-flow question.

## A redundant guard under stated bounds

The [marking chapter](marking.md) exposed an apparent contradiction in older wording:
`4A28` lets full-pitch tactic e5 bypass a sign guard, but `47C5` first rejects an opponent
standing in its own half. A bypass alone does not prove an additional following benefit.

Let marker attack direction be d, opponent direction -d, and y the opponent's unadjusted
world coordinate. Surviving `2C54` in `47C5` requires `y*(-d)>=0`, hence `y*d<=0`.
The target's y is then displaced by `-d*r`, with positive draw r. If that byte store does not
wrap, the target used by the later guard obeys:

```text
adjusted_y*d = y*d - r < 0
```

That is precisely the condition the half-pitch e5=0 branch needs. Full pitch's bypass cannot
change this copy decision under these assumptions.

The no-wrap premise can be bounded rather than guessed. Derived skill is a low-word product
divided by 32, so it is at most 2047. In `278A`, the condition product's divided low word is
at most 255 and the quarter term at most 511. Marking/feinting elements 5/8 do not receive
the cached extra in the fixed tables. Their pre-venue value is therefore at most 766, and
the optional one-sixteenth share raises that bound to 813. The displacement bound is at
most `1+813//16=51`.

For an on-pitch accepted target with `abs(y)<=37`, the adjusted magnitude is at most 88,
inside signed-byte range. The script checks all 3,876 direction/accepted-coordinate/draw
combinations in this conservative envelope. This is an arithmetic proof over an
overapproximation, not 3,876 engine calls or observed legal fixtures.

Two controls expose the premises. Remove the initial target-own-half rejection and y=10,
d=+1, r=1 leaves adjusted y=9, which fails the half-pitch guard. Permit an off-pitch y=-128
and r=1, and the stored byte wraps to +127. The audit does not claim that an available target
with either context is naturally encountered; such reachability remains open.

Consequently a tactic experiment must not predict an extra on-pitch following benefit from
this bypass alone. Element 5 still changes the defending depth table and can change complete
matches through that independent route. The older F026 following explanation needs this
qualification; [follow-up #514](https://github.com/diegoami/goal2-archaeology/issues/514)
tracks the cross-chapter correction and remaining contexts.

## Edges, negatives and remaining risks

At `8970/8972` in `8889`, an absolute target equal to the opposing line reaches the restriction
because `jl` skips only a smaller value. With all other gates eligible, target y=20,
line y=20 and direction +1 gives restricted target 19. A `>` interpretation leaves 20 and
differs in the authored model. The independent listing check is documented below. The decompiler can misattribute flags across the set-membership call that follows;
use the instruction comparison and branch, which the port matches.

At the `8AE9` expenditure tail, activity 180 does not spend energy and 181 can. The increment
precedes that test, as the [movement chapter](movement.md) explains. The current strict
comparison is faithful; changing it to inclusive would spend on the earlier edge.

No new port failure is established by these examined negatives. The remaining register/index
audit covers short analytical table windows, cache ownership, historical test blind spots and
the uncaught A2E6 mutation. This audit does not cover every signed expression, malformed record,
alias, frame or original-only continuation. Preserving those explicit boundaries is necessary
for a rewrite cost estimate that can be assessed against the actual evidence.

Validation scope: legacy calculator labels called “controls” are model consistency examples,
not independently executed source/engine falsifiers. Some literal-only annotations do not
exercise a branch at all. See the [control-scope report](../../notes/engine-study/ES-R2/model-annotation-scope-v1.json);
[listing_guards.py](../../notes/engine-study/ES-R2/listing_guards.py) separately checks explicit
instructions and rejects altered-listing inputs. Neither establishes natural incidence.
