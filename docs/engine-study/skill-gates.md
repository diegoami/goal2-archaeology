# Random draws and single-player skill gates

An effective skill value is an input to a caller, not a probability by itself. Some callers
make a discrete gate, some compare opposing draws, and some select a player or alter reach
without a binary contest. This chapter covers the random primitive and local gates; T99b maps
the opposed and deterministic families.

The [analytical ledger](../../notes/engine-study/T99/gates-v1.json) enumerates integer states,
not matches. All exact probabilities below assume a **uniform distribution over the 65,536
entry seeds**. A call reached after earlier game events need not have that seed distribution.

## The random stream and its scope

The original `214B:0688`, wrapped by `06B1`, computes:

```text
new_seed = U16(seed * 0x7ABD + 0x1B0F)
draw = ((new_seed * U16(n)) >> 16) + 1
```

The source-derived recurrence visits all65,536 states before returning to seed0. That period
does not make successive draws independent. The seed step is independent of n, and every call
advances it—even n=1 or n=0. At seed0 both those bounds return1 and leave seed6927.
Replacing a constant-result draw with no call changes later behaviour.

For positive n, the encoded word ranges1..n. For **n=0 it returns1**, rather than throwing
a host random-library range error. Comparison signedness is a separate caller decision.
`06D0(n)` returns true when the draw equals1; `06FA` does that with n=2.

The finite mapping is only approximately uniform when n does not divide65536. Under the stated
entry-seed law:

```text
count(draw == 1) = ceil(65536/n)     for n > 0
P(draw == 1) = that_count / 65536
P(draw == 1) = 1                   for n == 0
```

For n=3, the first bin has21,846 states. The usual 1/3 expression is an ideal-uniform
approximation; the exact first-bin probability is21846/65536. These small quantisation
differences are distinct from dependence between consecutive draws.

A different bound can leave the seed chain identical if call count/order stay unchanged.
Once a decision changes the later calls, the paths can diverge. One edited match at one seed is
therefore neither a general effect estimate nor proof that an attribute is unused when nothing
visible changes.

## Skill gate thresholds

`0791:287C` calls the effective reader278A, sets `n = V // 32 + 1`, calls06D0 and
**returns1 when the draw is not1**. The direction matters: the is-one helper itself returns
the opposite Boolean.

| Effective V | n | Passing entry states | Exact local pass probability | Ideal-uniform expression |
| ---: | ---: | --- | ---: | --- |
| 0 | 1 | 0/65536 | 0.000000000 | 0 |
| 1 | 1 | 0/65536 | 0.000000000 | 0 |
| 31 | 1 | 0/65536 | 0.000000000 | 0 |
| 32 | 2 | 32768/65536 | 0.500000000 | 1/2 |
| 33 | 2 | 32768/65536 | 0.500000000 | 1/2 |
| 63 | 2 | 32768/65536 | 0.500000000 | 1/2 |
| 64 | 3 | 43690/65536 | 0.666656494 | 2/3 |
| 95 | 3 | 43690/65536 | 0.666656494 | 2/3 |
| 96 | 4 | 49152/65536 | 0.750000000 | 3/4 |
| 127 | 4 | 49152/65536 | 0.750000000 | 3/4 |
| 128 | 5 | 52428/65536 | 0.799987793 | 4/5 |
| 255 | 8 | 57344/65536 | 0.875000000 | 7/8 |
| 256 | 9 | 58254/65536 | 0.888885498 | 8/9 |
| 65535 | 2048 | 65504/65536 | 0.999511719 | 2047/2048 |

The last row is a synthetic word endpoint, not a claim that ordinary players attain that value.
Values0..31 all fail this predicate, yet still consume a draw. Values32..63 share one threshold;
64..95 share another. Improving a value within a bucket need not change this gate, while crossing
a boundary can change it sharply.

For the [worked skill example](attribute-formulas.md), V72 gives n3, while the form32 value54
gives n2. That is a local gate difference conditional on calling287C, not a match win-rate claim.

Callers assign meaning to the Boolean. In the launch/miscue route it changes ball travel;
elsewhere it controls a challenge, reception, heading or a shot branch. Some geometry/state
conditions skip the call and continue along a branch automatically. Do not apply this gate's
probability to every action merely because the action uses the same skill.

## Other local gates and selection boundaries

Energy has several different uses, including two chance forms with opposite numeric trends:

- `2B7B` calls is-one with `U16(33-I8(energy))`.
- A branch in holder decision `5049` calls is-one with
  `U16(trunc_div(I8(energy),2))`, after its other conditions.

| Energy byte | 2B7B bound | Exact is-one | 5049 energy bound | Exact is-one |
| --- | ---: | ---: | ---: | ---: |
| 1 | 32 | 0.031250000 | 0 | 1.000000000 |
| 16 | 17 | 0.058837891 | 8 | 0.125000000 |
| 31 | 2 | 0.500000000 | 15 | 0.066680908 |
| 32 | 1 | 1.000000000 | 16 | 0.062500000 |
| 33 (synthetic) | 0 | 1.000000000 | 16 | 0.062500000 |
| 34 (synthetic) | 65535 | 0.000030518 | 17 | 0.058837891 |

These are different decision branches, not competing estimates of a generic energy-success
probability. The synthetic rows explain zero/wrapped bounds; ordinary play's energy range and
availability restrictions still apply.

Watched foul gate `4DA9` first makes the chance test with bound
`18-u8(hardness)`; only if it fails does it test the effective go-in-hard tactic. With ordinary
hardness0..16 the bound is18..2. A second opposed hardness comparison is still needed.
An enabled tactic does not justify skipping the earlier chance draw in a faithful rewrite.

Deterministic selectors must be separated too. `1FDD` replaces an incumbent on a strictly
better skill; `9ED3` ranks shoot-out takers using penalty skill. Their actual scan/swap order,
eligibility and initial state determine ties. They are not random wins, and an arbitrary stable
sort is not automatically the original algorithm. T99b accounts for every direct278A caller.

Set conventions also depend on the helper: the byte-set tactic/status helpers use element k
at bit k-1; the compiler's 256-element membership helper tests bit e for an enum value e.
Thus a CS set byte0x18 denotes event members3 and4, not event24 or status elements3/4.

## Validation and limits

The analytical checker enumerates all65,536 entry seeds for twelve selected bounds and fourteen
skill-threshold examples, and verifies the closed first-bin counts. It also verifies the full
recurrence period. Controls expose a missing +1 in the gate denominator, an inverted Boolean
and skipped degenerate draws. Source locations/hashes include the original RNG wrappers and
gate readers; no new original routine or match was executed.

These exact statements concern the declared seed law and local formulas. They do not establish
the frequency of visiting a gate, independent consecutive draws, uniform entry seeds after
conditioning, natural reachability of synthetic byte cases or a whole-match outcome effect.
The precomputed foul table and its index are additional state, as explained in
[live-state boundaries](transient-state.md).

```bash
python3 -B notes/engine-study/foundations/check.py --task T99a
python3 -B notes/engine-study/T99/odds.py --gates --check
```
