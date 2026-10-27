# Frozen sample, uncertainty and compute limits

This completes the proposed design in [experiment-design](experiment-design.md). It starts no
measurements: accepted ES-R2 and executable T106/T107 contracts are still required. The
[ledger](../../notes/engine-study/T105/T105b-v2.json) freezes every seed, arm order, witness and
cap. The [calculator](../../notes/engine-study/T105/budget.py) reads retained records and computes
sample/cost arithmetic only; it cannot construct or execute an engine.

## Frozen seed blocks and estimands

Use16 seeds per fixed context, sampled without replacement from0..65535 using separate
`random.Random(10520261027+i).sample(range(65536),16)` streams, i=0 forA and1 forB. The actual
lists below are frozen; no seed is replaced because of its outcome, failure or similarity.
Their realised sets are disjoint without resampling.

| Context | Main-seed words, in block order |
| --- | --- |
| A:7 v19,managed7 | 19516,45597,29364,29966,32093,25195,20121,5461,34317,21250,41924,11439,15368,7679,62584,62568 |
| B:19 v7,managed7 | 21433,28214,60620,19017,24009,22008,28455,32509,14616,11233,56722,59893,14753,12441,5270,45020 |

Each seed/context block contains four arms E16-Q0,E16-Q1,E32-Q0,E32-Q1 under the exact
intervention boundary in T105a. Run block1A,block1B,block2A,block2B…and within each block use
the ledger's fixed shuffled order (a separate `Random(10500000+2*block_index+context_index)`).
The schedule has **128 primary cells in32 blocks**. Four arms are potential outcomes of one
seed/context block, not four independent observations. Ticks, holders and commentary events
are not additional match replicates. ContextsA/B are fixed conditions, not two random draws
from a population of countries or venues.

One primary outcome is **Y=1 when managed country7 scores at least one retained fixture goal
in the watched friendly**, otherwise0. The block interaction is:

`I = (Y_E16Q1 − Y_E16Q0) − (Y_E32Q1 − Y_E32Q0)`.

It lies in[-2,2]. For outcomes[0,1,0,0],I=1; [1,0,0,1] gives−2; [1,1,1,1] gives0. Estimate each
context's mean over its16 blocks, then average those means with weights0.5/0.5. The estimand
is that equally weighted finite-main-seed effect for these two constructed contexts and the
specified synthetic energy intervention. It is not a natural fatigue effect, country-wide
win-rate recommendation, pure venue effect or new standalone-engine result.

Source reading predicts different **local action-gate** behaviour, not a directional scoring
interaction. Goals, shots, on-target, board possession, fouls/cards/injuries, opportunity counts,
actual signed energy and before/after player states are secondary descriptive outcomes. Report
them to explain what happened, without selecting a “best” tactic from them.

## Precision and multiplicity

Calculate I per block **before** calculating uncertainty. Separate marginal arm intervals
would discard the covariance that the paired design is intended to retain. Do not assume
common seeds keep later RNG draws synchronized; they only specify the four deterministic
potential trajectories from the declared starting boundary.

For a conservative finite-seed sampling interval, use the bounded range4 Hoeffding halfwidth
`4*sqrt(log(2/alpha)/(2*n))` for each context mean, with n=16 and alpha=0.025. Uniform sampling
without replacement permits the conservative bound; the union bound gives simultaneous
coverage of at least95% for both context means under that sampling model. Clip each interval
to[-2,2], then average the lower and upper endpoints for the aggregate estimand. This does not
require treating the two contexts as new independent football fixtures.

The halfwidth is **1.4802071873** before clipping: deliberately wide. Excluding zero in a
context needs an observed mean greater than1.4802: an integer block sum at least24 of its
maximum32 (or at most−24). For the equal-weight aggregate, the total over32blocks must be
at least48 of maximum64 (or at most−48). These are minimum observed exclusion thresholds,
not a power-guaranteed minimum true effect. Ordinary modest interactions will not be resolved.

A direct stratified aggregate Hoeffding bound could use all32 weighted block terms, giving
halfwidth `sqrt(log(40)/4)=0.9603227913`, and1476blocks/context for±0.1. That alternative is
recorded but **not adopted** here. The primary bound/caps/seeds remain unchanged. Before any
T107 execution, the owner must decide under#571 whether this very weak detection power is
worth the spending, whether to revise the design/bound, or to defer the batch. ES-R2 source
review acceptance alone is not that spending decision.
 A0.1 halfwidth with the
same conservative simultaneous construction needs **3506 blocks per context**, or **28048
four-arm match cells**. That calculation is a precision requirement, not a power guarantee
or permission to run them. The first bounded batch will probably be inconclusive about small
scoring interactions; an interval containing zero is not equivalence or proof that a setting
has no effect. A practical0.1 effect threshold cannot be excluded simply by this small sample.

State the model behind those intervals: randomness is the planned uniform selection of main
seed words within each fixed context. The actual sampler and engine are deterministic PRNGs;
this is a reproducible Monte Carlo design, not new physical randomness or a random sample of
football matches. Setup table/cursor state is fixed within context and its conditional paths
remain coupled. Publish the realised seed/block values and descriptive sample SD as well as
the conservative interval so a reviewer can assess those limits.

There is **one primary interaction**. The two contextual intervals share family alpha0.05;
the aggregate interval follows from their simultaneous event. No extra confirmatory p-values,
many-outcome significance search, best-setting selection or outcome-dependent sample extension.
Every secondary statistic/interaction is labelled exploratory. A later confirmation needs its
own preregistration and compute decision.

Opportunity action fractions require special care: prior gates and opportunity counts change
under treatment. Report numerator, denominator and actual E distribution; zero denominators
remain undefined. Such fractions describe a treatment-dependent set of opportunities and do
not by themselves verify the fixed-energy local probability or establish a direct causal path.
The original/port microprobes answer their own literal mechanism questions separately.

## Compute caps and stopping

| Work | Maximum attempts | CPU cap | Active runner wall cap | Per invocation / match | Workers |
| --- | --- | --- | --- | --- | --- |
| T106 selected probes | 60 top-level invocations including setup,negative/mutation controls and repeats | 600s | 900s | 5CPU s /10wall s | 1 |
| T107 sensitivity | 128 primary matches +4 fixed witnesses =132 total attempts | 3600s | 5400s | 45CPU s /60wall s | 1 |
| Combined new work | Both caps apply separately | **4200s (70min)** | **6300s (105min)** | No additional all-port full matches | 1 |

The ordinary microfrontier already needs36 target invocations (three launch calls and fifteen
wall-record calls per backend). The remaining24 are a ceiling for construction/setup and
controls/repeats, not an invitation to expand the frontier. Full nested real callees count
against CPU/wall watchdogs. No whole match is needed to initialise a synthetic direct-call
fixture. If a safe construction cannot fit, stop and revise the contract before running it.

Use tools/heavy.sh, one owned worker, with child-process CPU accounting and hard watchdogs.
Account for initialisation, failed/refused/timed-out attempts and repeats, not just successful
matches. Active wall time begins after obtaining the slot; queue delay is logged separately.
No unattended batch outside those caps, no hidden workers and no broad original or port sweep.
An interrupted attempt consumes budget and gets an immutable output; it does not grant a retry.

Retained data justifies this scale, while qualifying the extrapolation:

| Retained source | N | Median CPU/match | Maximum CPU/match | Median wall/match |
| --- | --- | --- | --- | --- |
| T57/reference.jsonl,unhooked kit2 | 62 | 14.4s | 21.072s | 13.51s |
| T57/trial-all-20261017.jsonl,unhooked kit2 | 62 | 15.4025s | 28.708s | See ledger |
| T57/rerun.jsonl,unhooked kit2 | 62 | 11.888s | 17.619s | See ledger |
| T77/all-actions-1-40090586451/all-actions-1.jsonl,all ports | 74 | 1549.8785s | 2851.377s | 1385.6715s |

For reference.jsonl alone,132 matches at its median cost1900.8CPU s (31.68min), or
2781.504CPU s (46.36min) at its maximum. Across **all three** retained unhooked runs the maxima
range17.619..28.708s; the largest gives3789.456s (63.16min), exceeding the3600s cap. F40-only
maxima are19.360/19.363/15.558s, but the side-reversed context is not an observed F40 case.
All three original timing runs used kit2; the current design reads kit4, and there is no
retained matched unhooked kit4 timing baseline. **The outcome-blind calibration stop is
the binding feasibility gate**, not the favourable reference run. These are projections from retained data,
**not fresh benchmarks**. Hosts, profiles, scenarios and contention differ. The much larger
all-port timings justify avoiding a duplicate full-port sensitivity campaign; they do not prove
an intrinsic universal speed ratio. T77's strict74-match evidence is reused within its actual
scope; pending T79's700-match sheet is not claimed to exist.

The **first eight primary matches**, block1A/B, also provide a runtime calibration and count
inside128. Examine timing/completion/readback diagnostics without adapting to outcome values.
If `132*max(first8_cpu_s)>3600`, stop before launching more cells and report that the budget
cannot support the preregistered batch. Also stop on a source/input mismatch, invalid boundary,
unreached required observer, noninterference failure, an unexpected/refused decision that cannot
be answered by the fixed policy, or any hard cap. Never switch to quick mode or another engine
to finish. No interim effect-based extension or stopping-for-significance.

## Completion, reproducibility and delivery

The four witness reruns are fixed now: the first seed of each context (A19516,B21433), arms
E16-Q0 andE32-Q1, with the **passive observer disabled** and the active intervention unchanged.
Compare with their scheduled primary counterparts for input identity, final results, RNG/event
digests and strict relevant memory/ABI projections. Only the observer's separate log can differ.
These runs are not new effect samples. Preserve a mismatch as a failure; do not retune keys,
seed, phase or record schema until it disappears.

A primary result needs exactly128 unique complete cells, all32 four-arm blocks and the four
witnesses, with no input/source mismatch, missing outcome or silently ignored failure. Check
friendly result/fixture goals against the kit's phase-aware result, full-time completion,
expected decisions, the actual energy/own-bit intervention and the native opportunity observer.
Record zero opportunities and all pre-/post-recovery observations explicitly. Do not infer that
an event template is a shot, goal or player statistic without its actual write consumer.

If a runtime/validity stop prevents completion, publish the attempts, reason, budget spent,
completed-cell/block counts and raw descriptive outcomes. **Do not publish the full planned
primary estimate/interval from complete survivors, impute missing outcomes as zero, replace
seeds or claim equivalence.** Failure can depend on treatment/trajectory, so dropping it would
change the design. A follow-up can preregister a missingness-bound analysis or revised feasible
batch; it does not alter the old records.

Before first measurement, T106/T107 still need independently mergeable executable contracts,
source hashes, immutable input manifests, input/observation/completion negative controls and
failing-baseline/passing-implementation checks. Then accepted ES-R2 is required. Every attempt
gets a new exclusive output under its owned notes directory; commit/push each batch and within
the repository's evidence cadence. Save actual cumulative CPU/runner time and all refusals.
Publish N, fixed estimand, effect/interval, secondary descriptive outcomes, observed RNG divergence,
limits and deviations before considering more runs. ES-R3 independently reviews the results.
