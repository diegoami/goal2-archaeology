# Recommendation: improve readability at proven boundaries

Yes: the engine can be organized more readably. The strongest near-term route is named views
over shared storage, followed by small numerical extractions whose machine-effect adapters
remain explicit and independently checked. A full domain rewrite is technically plausible,
but this study has not established a complete replacement contract or proof strategy for it.

The [compatibility contract](rewrite-contract.md) and [four worked sketches](rewrite-options.md)
make the risks concrete. Their [T110c ledger](../../notes/engine-study/T110/T110c-v1.json) and
[cost producer](../../notes/engine-study/T110/recommendation.py) retain assumptions and exact
source/support hashes. These are design recommendations for the owner, not production changes,
measured productivity, a prototype result or an approved budget.

## Recommendation and owner choices

1. **Prefer incremental memory views/helpers** while retaining the existing boundary contract.
   Reuse Rec/Mem rather than replacing shared storage with copied objects. Name known fields,
   preserve opaque bytes and keep cache, identity and write-site semantics visible.
2. **Make pure-rule extraction conditional on one meaningful experiment.** The first candidate
   is the strength arithmetic block after availability and before placement. A clear numerical
   helper is useful only if its adapter preserves the relevant machine effects without making
   the overall explanation harder.
3. **Defer a broad explicit-state replacement.** Phases are useful vocabulary, but pending
   decisions, nested calls, queues and checkpoint reconstruction require a complete state model.
   Account separately for any later accepted T78c work; do not assume it at this m7 baseline.
4. **No-go now for substituting a full semantic rewrite under the existing fidelity contract.**
   This is a scheduling/contract recommendation, not a proof of impossibility. Removing DOS
   representation requires an owner compatibility decision, consumer audit and new proof work.

The owner can approve a bounded prototype after ES-R4, prefer view-only follow-up, or defer
implementation and finish the guide. Independent AGREE on this assessment is not that design
decision. T111 is optional; T112/T113 can finish without prototype results.

## Cost model and exclusions

All figures below are **active engineering hours under explicit, uncalibrated work-unit
assumptions**. They are arithmetic planning scenarios, not measured developer/model throughput,
confidence intervals or delivery guarantees. Source membership supports the work allocation;
it does not validate a per-unit rate. Do not convert these numbers directly into elapsed days,
model tokens, money or a match CPU budget.

The four scopes differ: three record families, four selected numerical blocks, a phase/decision/
checkpoint redesign, or an initial full rewrite attempt. They are **not equal-feature bids**.
Do not rank them just by totals or add the four totals as one mandatory roadmap.

| Option / designed scope | Implementation hours | Validation hours | Total hours | All rates doubled |
| --- | ---: | ---: | ---: | ---: |
| memory-views | 14–28 | 15–30 | 29–58 | 58–116 |
| pure-rules | 16–32 | 20–40 | 36–72 | 72–144 |
| explicit-transitions | 66–132 | 92–184 | 158–316 | 316–632 |
| semantic-rewrite | 376–752 | 568–1136 | 944–1888 | 1888–3776 |

Doubling both implementation and validation rates is a stress scenario, not an upper bound.
Unknown field semantics, a missing oracle, representation decisions or a required continuation
proof can make work exceed these ranges. A smaller chosen subset can reduce it. No production
allocation is approved by publishing the arithmetic.

**Excluded and unpriced:** the live-Core bridge #427 (natural caller frames, complete write sets,
outer news/confidence ordering and safe original continuation), sealed records-only delivery,
T79's independent fidelity sheet/campaign, new genuine-key collection, exhaustive-input proof,
and any deliberate rule change. Fresh-career delivery does not make a bridge unnecessary;
old-career migration is not part of the current owner requirement. Later accepted delivery
may change the work estimate and needs a new version, not a changed historical ledger.

CPU/runner duration remains unknown and unbudgeted. T106's6.6CPU seconds for selected direct
probes do not predict whole-match or prototype validation cost. Existing full CI is a separate
verification workload. Any future engine execution needs its own exact contract and cap.

## Four cost plans

### memory-views

**Disposition:** recommend. Recommend incremental named views over existing storage/helpers; preserve the current boundary contract.

**Scope:** Three record families (player, country, pitch), shared accessor naming and two representative integration boundaries; not all unknown fields or the live-Core bridge.

| Activity | Units | Hours per unit | Basis |
| --- | ---: | ---: | --- |
| implementation | 3 | 4–8 | Name one shared-storage record family |
| implementation | 1 | 2–4 | Shared accessor/schema integration |
| validation | 3 | 3–6 | Alias/wrapping/reserved-byte/write-site audit per family |
| validation | 2 | 3–6 | Two representative integration boundaries; more consumers add cost |

**Assumptions:** Three families are a designed rollout scope, not a measured count of independent implementations. Reuse Rec/Mem; no copied replacement storage, cache refresh or reordered writer effects. Rates are uncalibrated active-hour inputs for planning, not measured productivity.

**Dependencies:** Accepted field meanings/opaque bytes; Aliasing/wrapping and write-site audit; Boundary regression infrastructure.

### pure-rules

**Disposition:** conditional. Conditionally extract numerical blocks behind explicit ABI/effect adapters after one meaningful prototype.

**Scope:** Four candidate numerical blocks:377E strength,3A06 derived skill,278A effective-skill arithmetic,34C1 geometry arithmetic. Whole routines are not claimed pure.

| Activity | Units | Hours per unit | Basis |
| --- | ---: | ---: | --- |
| implementation | 4 | 3–6 | One candidate numerical block plus its adapter |
| implementation | 1 | 4–8 | Shared input/trace/helper infrastructure |
| validation | 4 | 4–8 | Per-block retained/original/accepted-port boundary and negative controls |
| validation | 1 | 4–8 | Shared integration and independent review fixes |

**Assumptions:** Four blocks are selected work scope, not a purity census or all numeric engine code. Existing wrappers/calls/sites remain until an adapter passes exact boundary checks. No extrapolation of T106's small-call timings into match performance.

**Dependencies:** Independent numerical oracles and targeted boundary witnesses; Adapter preserving intermediate/register/frame effects; Original/accepted-port comparison harness.

### explicit-transitions

**Disposition:** defer. Defer broad state-representation replacement until pending decisions and checkpoint obligations have a complete model.

**Scope:** Four designed phase workgroups (setup,run_match,player_update,terminal), six public decision contexts, three checkpoint workgroups (ordinary,pending/refused,queued). Counts are planning groups, not measured states.

| Activity | Units | Hours per unit | Basis |
| --- | ---: | ---: | --- |
| implementation | 4 | 6–12 | Designed phase workgroup |
| implementation | 6 | 4–8 | Public decision context with refusal/default path |
| implementation | 3 | 6–12 | Checkpoint workgroup |
| validation | 4 | 8–16 | Phase boundary/order evidence |
| validation | 6 | 6–12 | Decision/refusal/continuation evidence |
| validation | 3 | 8–16 | Checkpoint queue/frame/RNG evidence |

**Assumptions:** Context count follows the six documented public decision kinds; extra-time halves/refusal subpaths still need separate cases. At m7 plain-port checkpoints are refused; this option does not take credit for later independent T78c work. Nested generator/caller state may force redesign; a phase enum alone is insufficient.

**Dependencies:** Complete continuation/state representation; Exact event/answer/refusal order; Pending frame/queue/RNG checkpoint proof; Reassessment against later accepted delivery if any.

### semantic-rewrite

**Disposition:** no-go-now. No-go now for substituting a full domain rewrite under the present fidelity contract; technical feasibility is not disproved.

**Scope:** Initial rewrite/validation attempt across all23m7 registry modules plus six cross-module workgroups. Not a complete release estimate, exhaustive proof or live-Core bridge/sealed delivery.

| Activity | Units | Hours per unit | Basis |
| --- | ---: | ---: | --- |
| implementation | 10 | 12–24 | Numeric/policy registry-module group |
| implementation | 10 | 16–32 | State/effect/lifecycle registry-module group |
| implementation | 3 | 16–32 | Interaction/assembly registry-module group |
| implementation | 6 | 8–16 | Cross-module workgroup |
| validation | 10 | 16–32 | Numeric/policy module original-oracle evidence |
| validation | 10 | 24–48 | State/effect/lifecycle module evidence |
| validation | 3 | 24–48 | Interaction/assembly module evidence |
| validation | 6 | 16–32 | RNG/events/decisions/checkpoints/modes/post-tail integration evidence |

**Assumptions:** Partition actual modules into10numeric/policy,10state/effect/lifecycle and3interaction/assembly groups; rates intentionally differ. Per-module effort varies widely; module count is a work-allocation input, not a complexity metric. Unresolved oracle/coverage/representation obligations can exceed every range here; no confidence bound is claimed. A public-API-only representation contract would need explicit owner adoption; it is not assumed.

**Dependencies:** Owner compatibility decision and consumer audit; Independent numeric/RNG/occupancy replacements; Rare-path and genuine-key oracle coverage; Whole API/record/continuation proof; Separate #427,T79,T80 delivery decisions.

For the full-rewrite allocation the actual23modules are partitioned without overlap:
numeric/policy = attributes, contests, duels, geometry, positioning, quick, rare, runtime, selection, real;
state/effect/lifecycle = ball, discipline, frame, motion, pilot, postmatch, restarts, setup, takers, update;
interaction/assembly = display, menus, entrypoints.
The six additional integration workgroups are RNG streams, events, decisions, checkpoints,
modes and post-tail behavior. These are workgroups, not proof cases or independent experiments.
The allocation explicitly includes validation and cross-module work; it is not439routines
times one assumed implementation cost.

## Smallest meaningful prototype

### prototype

**Proposal only; not authorised or implemented.** Extract the after-availability numerical
block of377E while retaining the original query order, placement query, frame/register and
write/site effects in the adapter. This tests whether a readable pure rule can coexist with
the existing machine boundary, rather than merely demonstrating a shorter scalar formula.

A scalar result alone is insufficient. The adapter may need intermediate words, quotient/
remainder or branch information; retaining explicit existing operations may be necessary.
If this requires duplicating most plumbing or worsens the explanation, stop and recommend
views instead. Do not remove effects because a sampled numeric corpus does not notice them.

Provisional **6–12 active hours** for this known narrow prototype, subject to a later executable
contract:1–2numerical block,1–2adapter,2–4selected oracle/negative cases,2–4boundary/readability
assessment and review fixes. This re-estimates the earlier T111 outline; it is not approval.
The four-block rollout above includes additional heterogeneous blocks/shared infrastructure
and wider validation, not four automatic copies of a successful first experiment.

**Independent evidence:** reuse the376retained numerical returns only for their recorded
projection; compare complete observed wrapper state/effects against the unchanged accepted
port and independent original behavior under its disclosed contract. The new helper must
not generate both expected and actual outcomes. Record any baseline discrepancy separately;
a new unexplained difference blocks success, and existing #591 limits are not a fresh mask.

**Actual future failing controls required:** cutoff33 with a form32 witness; clamp after
placement with the retained clamp-before-placement witness; a correct scalar coupled to a
wrong adapter word/register/site, with a demonstrated sensitive boundary witness. These are
proposed tests, not executed T110 mutants. If the witness is unavailable, the later contract
is not ready; do not credit an uncaught change as harmless.

**Readability questions for an independent reader:** locate the signed form32 rule and finite
operations; distinguish unavailable from available-zero strength; identify placement/query
ordering and adapter effects; assess whether trace/wrapper complexity defeats the benefit.
Pre-register the comparison method and report limitations. Fewer lines or a renamed function
alone is not the success criterion, and no speed improvement is claimed without a matched,
preregistered measurement.

**Stop conditions:** unexplained state/trace difference; only scalar parity available; unknown
required ABI effects; adapter duplication defeats the intended clarity; missing independent
oracle/sensitive negative; exceeded separately approved CPU/runner cap. Keep failures and stop,
rather than repeatedly changing scope or thresholds after seeing results.

**Owner decisions before T111:** compatibility target, approve/defer the prototype and effort,
then exact input/oracle/control scope and CPU/runner cap through executable readiness. ES-R4
reviews this proposal and its estimates; ES-R4P reviews any later actual prototype. Neither
this recommendation nor reviewer AGREE changes a production backend or authorises T107 matches.

## Validation and review boundary

The producer recomputes every work-unit sum and doubled-rate scenario and verifies that the
23module partition matches the frozen T110a inventory. Schema controls reject omitted
decisions/limits/sources, mock evidence and an altered cost sum. Those checks establish
consistency, not calibrated productivity, architectural correctness or implementation parity.

Preserve T110b-v1's historical incorrect movement sketch and v2's correction; structural
validation alone did not certify effect order. Reuse accepted m7 source/evidence with all
known gaps. No runtime/static/spec changes, prototype or new research engine call occur in T110.
The next action is author-independent ES-R4 review of the exact candidate, with the owner
receiving the concrete choices above. The deferred T107 proposal remains separate.
