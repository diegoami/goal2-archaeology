# What the bounded engine probes establish

The original and Python port agree on all six selected geometry cases. This includes two
counterintuitive original rules: a zero-displacement launch still moves downward, and a free
kick at y=26 selects a wall formula with destinations on the opposite side of halfway.
These are proposed corroborations pending independent ES-R3 review, not balance corrections.

The [integrated report](../../notes/engine-study/T106/report-v1.json) and
[reproducer](../../notes/engine-study/T106/analysis.py) account for 48 completed calls:
36 ordinary original/port invocations, four guard calls, two energy controls, two real
reverse-x port variants and four fixed repeats. There were no failed calls or unclosed
reservations. Total measured parent/child CPU was 6.632043 seconds and active wall time
6.572569 seconds, within the global 60-call/600-CPU/900-wall limits. The unused twelve
invocations are a ceiling reserve, not a new campaign. Report generation executes no engine.

## Literal predictions and observations

| Original and port input | Observed result in both |
| --- | --- |
| Launch target (0,0), holder at (0,0) | Velocity (0,-1), duration 2, event 6, projected point (0,-2) |
| Launch target (1,0) | Velocity (1,-1), duration 2, event 6, projected point (2,-2) |
| Launch target (7,14) | Velocity (1,2), duration 7, event 7, projected point (7,14) |
| Free kick (0,25), holder direction +1 | Relative slots 7..11 target (2,30),(1,30),(0,30),(-1,30),(-2,30) |
| Free kick (0,26), holder direction +1 | Relative slots 7..11 target (-3,-28),(-3,-27),(-3,-26),(-3,-25),(-3,-24) |
| Free kick (0,-26), holder direction -1 | Relative slots 7..11 target (-3,28),(-3,29),(-3,30),(-3,31),(-3,32) |

The launch duration calculation is not universal halving. Its signed byte steps give -1 for
a zero component, and its duration has a minimum of two. A projected point is a calculation,
not an observed future arrival: movement, boundaries and contests can intervene.

The wall boundary is strict: abs(y)<26 uses the near formula. The far formula directly writes
its coordinates without a final normalising mirror. The negative-side case preserves x=-3;
mirroring both axes would change the original rule. These observations reproduce the literal
expectations committed in [T105a-v2](../../notes/engine-study/T105/T105a-v2.json).

## What the controls actually test

Energy 16 versus 32 leaves zero-launch geometry unchanged on this branch in both backends.
The actual registered reverse-x variant changes the horizontal velocity for both selected
nonzero launches. Four fixed repeats reproduce all captured registers and full memory for
their respective backend. These checks are bounded observations, not attribute rankings.

An outside-wall relative slot 6 and a holder facing away from the positive kick spot both
execute the real `0791:4B64` fallback, in native code and in the production port. Their
destinations are respectively (-3,33) and (-1,-31), with state 11 unchanged. Those guard pairs
agree on full memory and the declared return ABI. No helper supplies canned answers.

The wrong zero-idle, universal-halving, near/far-boundary, far-sign and both-axes-mirroring
alternatives are rejected by original observations. These are observation-backed hypotheses,
not five executed engine mutations. Separate software/data negatives reject missing
completion, altered input hashes, mismatched reservations, invented observations and the
slice validator's missing/false-exact cases. They test record integrity, not football rules.

## Equality has several distinct meanings

| Comparison across the 18 ordinary original/port pairs | Matches |
| --- | --- |
| Selected geometry/event/state fields | 18/18 |
| Declared return ABI, including direction flag | 18/18 |
| Every memory byte | 15/18, all wall pairs |
| Every captured register, including arithmetic flags | 3/18, all launch pairs |
| Every memory byte and every captured register together | 0/18 |

All three launch pairs differ in fifteen memory bytes below the returned stack pointer,
at SS:3EDE,3EE0..3EE2,3EE4,3EE6..3EEF (entry SP=3F00, returned SP=3F0C).
The production T73 sound stub `214B:1EA1` is reached; the native arm executes the original
muted sound/delay body. This is consistent with callee-frame residue, but is not an isolated
causal proof. [Follow-up #591](https://github.com/diegoami/goal2-archaeology/issues/591)
asks the integration audit to classify caller liveness and the documented sound boundary.
No byte is masked and no full-state equivalence is claimed.

All fifteen wall baseline pairs match full memory and the declared ABI but differ in EFLAGS.
For example, near slot 18 returns flags 0x246 natively and 0x293 in the port. Arithmetic flags
are scratch under the existing port contract; direction flag is compared. The slice ledger's
`exact` disposition means memory plus declared ABI, not all-register equality. Whether an
actual caller observes a difference belongs to the T109 consistency audit. No sound/display
stub is reached in the wall slice.

## Construction, provenance and limits

The hash-verified published E006 image supplies genuine country/player bindings. The probes
deliberately construct all 22 live records, positions, destination/state fields, energy,
clock/direction context, muted sound calibration and a far-call stack. Each patch, prior-byte
hash, full input-memory hash and register set appears in the committed manifests. There is no
match setup call, instruction patch or production-engine modification. Source producers and
complete manifests were committed and pushed before execution. Original memory/code bytes
are not published; derived records contain hashes, observations, traces and differing offsets.

The native arm has no port replacements. The port arm uses actual registered production
callees, refuses unregistered fallback and guards against native instruction execution.
Entry/return hooks and inline helpers are identified separately; hook events are not evidence
that native instructions ran in the port arm. All measured records and old report versions
remain immutable. Slice reports pin historical source commits and their own budget snapshots,
so later standalone work cannot silently replace the measured implementation.

Synthetic direct calls establish neither natural incidence nor match-level scoring impact.
They do not resolve [zero-target reachability #529](https://github.com/diegoami/goal2-archaeology/issues/529)
or [far-wall incidence #540](https://github.com/diegoami/goal2-archaeology/issues/540).
No new full match was run. The owner deferred T107's weak scoring pilot under
[#571](https://github.com/diegoami/goal2-archaeology/issues/571). A revised proposal should
separate a mechanism/reachability question from scoring-effect estimation, justify its
sampling precision before spending, and retain independent review. These probes alone
provide no scoring effect, confidence interval or null result.
