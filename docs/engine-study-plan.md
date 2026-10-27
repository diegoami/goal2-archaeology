# Engine anatomy, behaviour and readability study

[designed: owner, 2026-10-26] The owner approved the proposed ten-area study and requested
difficulty, size, complexity and impact ratings. This is the versioned plan and backlog, tracked
by [programme #433](https://github.com/diegoami/goal2-archaeology/issues/433).
GitHub issues and labels hold work status.

## Purpose and boundaries

Explain the engine to a programmer and to someone exploring football behaviour: how its code,
attributes, tactical controls and state changes produce what happens on the field. Corroborate
selected uncertainties with experiments, investigate inconsistencies, and assess whether a more
readable implementation is practical. The principal result is a source-backed guide, reference
dictionary and exploration atlas, rather than a replacement engine.

The routines' translation is distinct from standalone execution and packaging. T78 (#289),
T79 (#290) and T80 (#291) keep their existing contracts; T79 supplies the broad fidelity sheet.
This programme neither restarts the port sequence nor replaces the goal2 delivery contract (#427).
Static analysis and original-backed probes can use the validated existing kit. Measurements on a
new standalone path require its accepted fidelity evidence first.

Approval covers planning and recording the backlog. Research execution is selected separately;
a readable prototype also requires the explicit design decision in T110/T111. Fixes to faithful
original quirks and production/default-backend changes are separate decisions. Planning this study
does not change CLAUDE.md rule 23's scheduling priority.

## Ratings and cost assumptions

Each issue has four independent labels and a rationale in its brief:

| Dimension | Values | Meaning |
| --- | --- | --- |
| Difficulty | easy / hard | Indexing/transcription versus inference about rules, numerical behaviour, experiments or architecture. New game-rule claims are hard under CLAUDE.md rule 21. |
| Size | S / M / L / XL | S = 0.5–1 active hour; M = 2–4; L = 4–8; XL = more than 8 and therefore a programme. Estimates are provisional work budgets, not delivery promises. |
| Complexity | low / medium / high | Local work; several interacting concepts; or tightly coupled state, arithmetic, RNG, phase transitions and compatibility. |
| Impact | low / medium / high | The L/M/H importance rubric of docs/wide-pass.md: detail/rare path; shapes play; or changes results, state/eligibility or an essential programme prerequisite. |

Difficulty is not size, complexity is not elapsed time, and high impact is not scheduling priority.
The [wide-pass cost/importance rules](wide-pass.md) still decide which unknowns merit measurement.
The size estimate excludes CPU/runner time and owner waiting. T105 sets an explicit compute cap
before any new batch; an expensive or low-value question can remain an assumption or an evidence gap.

The nineteen work packages originally totalled 33–66 mandatory active hours (including the final
T113 review), plus 2–4 for an optional prototype. The [independent review schedule](engine-study-reviews.md)
adds four earlier mandatory reviews (8–16 hours) and one conditional prototype review (2–4 hours).
The revised programme is **41–82 mandatory active hours**, plus **4–8 hours for the optional
prototype and its review**, or **45–90 hours including that option**. These provisional first-pass
ranges exclude findings/fixes, repeat review rounds and compute; re-estimate those before execution.
Reuse of findings may lower the work; gaps found by T95 may raise it. No match count or runner budget
is authorised by this estimate.

## Ten areas and independently tracked packages

1. **Inventory and evidence**: [T95](tasks/T95.md).
2. **Attribute dictionary**: [T96](tasks/T96.md), [T97](tasks/T97.md).
3. **Analytical examples**: [T98](tasks/T98.md), [T99](tasks/T99.md).
4. **Pitch behaviour**: [T100](tasks/T100.md), [T101](tasks/T101.md), [T102](tasks/T102.md).
5. **Tactics and lifecycle**: [T103](tasks/T103.md), [T104](tasks/T104.md).
6. **Experiment design**: [T105](tasks/T105.md).
7. **Bounded measurements**: [T106](tasks/T106.md), [T107](tasks/T107.md).
8. **Defect investigation**: [T108](tasks/T108.md), [T109](tasks/T109.md).
9. **Readable rewrite**: [T110](tasks/T110.md), [T111](tasks/T111.md).
10. **Guide and independent review**: [T112](tasks/T112.md), [T113](tasks/T113.md).

| Package | Issue | Deliverable | Difficulty | Size / active effort | Complexity | Impact | Depends on |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [T95](tasks/T95.md) | [#434](https://github.com/diegoami/goal2-archaeology/issues/434) | Engine inventory and evidence map | easy | S; 0.5–1 h | medium | high | planning merge |
| [T96](tasks/T96.md) | [#435](https://github.com/diegoami/goal2-archaeology/issues/435) | Player attribute dictionary | hard | M; 2–4 h | medium | high | T95 |
| [T97](tasks/T97.md) | [#436](https://github.com/diegoami/goal2-archaeology/issues/436) | Team, fixture and transient match-state dictionary | hard | M; 2–4 h | high | high | T95 |
| [T98](tasks/T98.md) | [#437](https://github.com/diegoami/goal2-archaeology/issues/437) | Attribute formulas and worked player examples | hard | M; 2–4 h | high | high | T96, T97 |
| [T99](tasks/T99.md) | [#438](https://github.com/diegoami/goal2-archaeology/issues/438) | Contest probabilities and decision thresholds | hard | M; 2–4 h | high | high | T98 |
| [T100](tasks/T100.md) | [#439](https://github.com/diegoami/goal2-archaeology/issues/439) | Match tick, state transitions and random-number flow | hard | S; 0.5–1 h | high | high | T95, T97 |
| [T101](tasks/T101.md) | [#440](https://github.com/diegoami/goal2-archaeology/issues/440) | Pitch positioning, marking and movement anatomy | hard | M; 2–4 h | high | high | T97, T100; [ES-R1](engine-study-reviews.md#es-r1) accepted |
| [T102](tasks/T102.md) | [#441](https://github.com/diegoami/goal2-archaeology/issues/441) | Possession, ball actions and scoring anatomy | hard | M; 2–4 h | high | high | T99, T100, T101 |
| [T103](tasks/T103.md) | [#442](https://github.com/diegoami/goal2-archaeology/issues/442) | Tactics, formation choices and computer-manager behaviour | hard | M; 2–4 h | high | medium | T96, T97, T101, T102 |
| [T104](tasks/T104.md) | [#443](https://github.com/diegoami/goal2-archaeology/issues/443) | Restarts, discipline, substitutions and post-match effects | hard | M; 2–4 h | high | high | T96, T97, T100, T102 |
| [T105](tasks/T105.md) | [#444](https://github.com/diegoami/goal2-archaeology/issues/444) | Preregister bounded experiments and synthetic scenarios | hard | M; 2–4 h | high | high | T98, T99, T101, T102, T103, T104 |
| [T106](tasks/T106.md) | [#445](https://github.com/diegoami/goal2-archaeology/issues/445) | Validate isolated mechanisms with synthetic probes | hard | M; 2–4 h | medium | high | T105; [ES-R2](engine-study-reviews.md#es-r2) accepted |
| [T107](tasks/T107.md) | [#446](https://github.com/diegoami/goal2-archaeology/issues/446) | Run the first bounded match sensitivity batch | hard | M; 2–4 h + capped compute | high | medium | T105, T106; [ES-R2](engine-study-reviews.md#es-r2) accepted |
| [T108](tasks/T108.md) | [#447](https://github.com/diegoami/goal2-archaeology/issues/447) | Audit arithmetic, boundaries and record indexing | hard | M; 2–4 h | high | high | T96, T97, T98, T99; [ES-R1](engine-study-reviews.md#es-r1) accepted |
| [T109](tasks/T109.md) | [#448](https://github.com/diegoami/goal2-archaeology/issues/448) | Audit cross-module consistency and execution paths | hard | M; 2–4 h | high | high | T100, T101, T102, T103, T104, T106 |
| [T110](tasks/T110.md) | [#449](https://github.com/diegoami/goal2-archaeology/issues/449) | Readable-engine architecture and rewrite decision | hard | M; 2–4 h | high | high | T95, T98, T99, T100, T101, T102, T103, T104, T108, T109; [ES-R3](engine-study-reviews.md#es-r3) accepted |
| [T111](tasks/T111.md) | [#450](https://github.com/diegoami/goal2-archaeology/issues/450) | Conditional readable-rule prototype | hard | M; 2–4 h; re-estimate after T110 | high | medium | T110; [ES-R4](engine-study-reviews.md#es-r4) accepted |
| [T112](tasks/T112.md) | [#451](https://github.com/diegoami/goal2-archaeology/issues/451) | Assemble the engine guide and exploration atlas | hard | M; 2–4 h | medium | high | T95, T96, T97, T98, T99, T100, T101, T102, T103, T104, T106, T107, T108, T109, T110; [ES-R3](engine-study-reviews.md#es-r3) accepted, [ES-R4](engine-study-reviews.md#es-r4) accepted |
| [T113](tasks/T113.md) | [#452](https://github.com/diegoami/goal2-archaeology/issues/452) | Independent milestone review of the engine study | hard | M; 2–4 h | high | high | T112 |

Dependencies express research needs, not permission to run several tasks in this checkout.
T111 is optional and is not a dependency of T112 or T113. If its conclusions are included as
established results, they require ES-R4P acceptance.

## Foundation execution slices

[designed: main session, 2026-10-26, owner-authorised execution through ES-R1] T95's census
pins engine sources to `08beac2e9d43faf766e445e924da096b8a99d748`; the first study implementation
baseline is `2c8f02a46601dd50977b72d227d11d1884eba310`. Execute the M packages as
[T96a](tasks/T96a.md)/[T96b](tasks/T96b.md), [T97a](tasks/T97a.md)/[T97b](tasks/T97b.md),
[T98a](tasks/T98a.md)/[T98b](tasks/T98b.md), [T99a](tasks/T99a.md)/[T99b](tasks/T99b.md),
then T100, one independently mergeable PR per slice. Source/document integrity checks are
structural; numerical comparisons and independent source reading support the actual claims.
Stop after ES-R1's foundation deliverables merge and provide the candidate-pinned review prompt;
do not launch the reviewer or begin ES-R2-gated pitch work in this execution run.

## Main-session implementation and targeted help

[designed: owner correction, 2026-10-26] Do all implementation and analysis in the main session
on `gpt-6.1-sol` at `high`. Sparingly use a separate `gpt-6.1-sol` / `xhigh` agent for only the
hardest, narrowly scoped subproblems after working them at high. No task automatically requires
delegation or extra-high effort. The [main-session model policy](engine-study-models.md) supersedes
the previous per-task model assignments, mandatory implementer spawning and Claude implementation
alternatives. Astra is excluded; xhigh is the Codex effort ceiling.

Independent milestone reviews remain Claude or Kimi reviews with model/settings selected at
activation. T113's packet preparation and fixes use the main session at Sol/high; its reviewer
supplies the independent verdict. Existing readiness, source/evidence, budget and milestone gates
continue to apply.

## Dispatch and milestones

These files are **planning briefs**, not a set of ready implementation contracts. This is
intentional: exhaustive field/routine counts and the cheapest validation cases come from T95,
so inventing those counts or executable checks now would create false acceptance criteria.

Before marking any package ready, the main session pins its scope, owned artifacts and exact
Done-when commands, checks that each fails on pre-task main and passes on a mock fix, and records
the contract change through the normal repository process. **Every M/L package is split before
dispatch into independently mergeable slices of about one hour**, using suffixes such as T96a,
T96b. Each slice has its own issue, ownership, evidence and measurable completion criterion.
The package issue remains their parent. Even an S package is split if inspection shows it is too large.
Task-specific acceptance outcomes below must survive that decomposition.

Five mandatory independent reviews and one conditional prototype review are defined in
[engine-study-reviews.md](engine-study-reviews.md), with entry work, exact review scope, exit criteria
and dependent-work gates. T113 implements the final ES-R5 review; it is counted once. These are
planned checkpoints, activated under the existing milestone process only when a candidate is ready.
No review or experiment is launched by defining them.

1. **Inventory:** T95 accounts for the current engine/evidence universe and records counts and gaps.
   Use it to refine estimates and schedule the first static chapter.
2. **Mechanisms:** T96–T104 provide complete field/control/routine coverage or explicit unresolved
   entries, causal explanations and source-pinned worked examples. New rule findings receive
   independent strong-model review before spec promotion.
3. **Validation:** T105 fixes questions, controls and budgets; T106 corroborates cheap isolated
   predictions; T107 publishes only the first bounded match batch. Additional batches require
   their own scoped follow-ups. Reuse accepted T79 results rather than duplicating fidelity runs.
4. **Audit and design:** T108/T109 classify suspected defects; T110 recommends rewrite options.
   The owner then decides whether T111's isolated prototype is useful.
5. **Guide:** T112 assembles the guide; T113 independently challenges its evidence, completeness,
   experiments and design recommendation. Relay the review in full; track all unresolved findings.

## How the investigation works

- Read the named original first, then decompiled/listing sources, the port and existing findings.
  Preserve evidence levels: port parity or repetition does not promote an unreviewed claim.
- For each attribute/control, trace storage and displayed value through derived values, decision
  branches and state writes to visible events and lasting consequences. Separate direct,
  indirect, context-dependent and no-identified effects.
- Use ordinary, threshold and counterintuitive worked inputs. Preserve signedness, wrapping,
  truncation, caps, strict comparisons and exact random-draw order.
- Treat pitch characters/occupancy, referee/offside markers, display side effects and save/decision
  continuations as potential gameplay dependencies until traced.
- Compare watched, quick and unattended paths explicitly; one is not an experimental substitute
  for another. Distinguish local probabilities from whole-match effects.
- Synthetic fixtures declare provenance, every edit, legal/reachable status and the question they
  answer. Original-backed differential checks and port-only exploration carry different claims.
- Equal starting seeds do not keep subsequent draws aligned after branch divergence. Match batches
  report independent seed/context structure, effect sizes, intervals, failures and exploratory
  versus confirmatory results; repeated looks and multiple comparisons follow the pinned design.
- Every measurement has a tracked, immutable task-owned output path, pinned sources, completion
  checks and an independent expected value or falsifying control. Push per batch and per repository
  timing rules; heavy jobs use tools/heavy.sh. No long campaign starts from an uncapped outline.
- Candidate defects get a minimal reproduction and a classification: original quirk, port defect,
  documentation/test defect, unsupported suspicion or unresolved. A surprising rule is not
  automatically a bug, and lack of a caught mutant may expose an observation blind spot.
- Preserve existing issue ownership: #227 offside, #375 uncaught A2E6 falsifier, #412 listing edges,
  #416 display frontier, #394 DOS return-frame proof and #400 original-key inputs are leads and
  evidence gaps, not presumed new defects. Link or narrow them before filing duplicates.
- Keep research code in probes/prototypes and new static findings in the annotation/named-view
  workflow. Only the main session promotes reviewed claims into spec. Downstream delivery uses
  docs/process.md §14; this programme does not modify goal2.

## Readability decision

T110 compares named memory views/helpers, extracted pure rules, explicit state transitions and a
full semantic rewrite. It must show representative before/after pseudocode and validation costs,
including alternatives that stop short of a full rewrite. Preserve observable football behaviour,
RNG consumption, numeric semantics, occupancy and save/load/API compatibility as appropriate to
the chosen contract. State deliberately changed semantics explicitly for the owner's decision.

T111 tests a chosen narrow slice only after that decision; ordinary/boundary differential checks
and a failing control must establish its claimed equivalence. A local success is not whole-engine
proof. The final guide and review can finish without this optional experiment.

## Field-behaviour execution slices

[designed: owner resume, 2026-10-27] ES-R1 is accepted at `m5-engine-study-foundations`. Continue in the main session toward ES-R2, then stop with its candidate-pinned reviewer prompt. T101 runs as [T101a](tasks/T101a.md), [T101b](tasks/T101b.md) and [T101c](tasks/T101c.md), with independently mergeable chapters and source-derived examples. The [readiness receipt](../notes/engine-study/T101/readiness-v1.json) checks contract structure only. New original/port probes and match batches remain gated by accepted ES-R2 and T105 budgets; this continuation does not activate them.

T108 follows T101 as [T108a](tasks/T108a.md)/[T108b](tasks/T108b.md), before the remaining ball/tactics work: T101 exposed captain-cache and marking interpretations that need qualification before experimental predictions use them. This is a bounded audit of nine named candidates, not permission to repair the original or run new probes. [Readiness](../notes/engine-study/T108/readiness-v1.json) pins the structural checks.

T102 runs as [T102a](tasks/T102a.md), [T102b](tasks/T102b.md) and [T102c](tasks/T102c.md), covering55 ball/contest/duel and deferred motion entries. [Readiness](../notes/engine-study/T102/readiness-v1.json) binds the exact census disposition and structural controls. These chapters explain selection through visible/persistent consequences while leaving restart management to T104 and new engine executions to the accepted ES-R2/T105 gate.
