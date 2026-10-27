# Independent reviews for the engine study

[designed: owner request, 2026-10-26] Define five mandatory review checkpoints and one conditional
prototype review for [programme #433](https://github.com/diegoami/goal2-archaeology/issues/433).
This extends the [engine study plan](engine-study-plan.md), using the existing
[milestone-review process](milestone-review.md). The programme's issue labels hold status.

## Review schedule

| Checkpoint / issue | Milestone | Entry work | Work protected by acceptance | Difficulty | Size / active effort | Complexity | Impact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [ES-R1](https://github.com/diegoami/goal2-archaeology/issues/454) | Foundations | T95–T100: engine/evidence inventory, player/team/fixture/transient-state dictionaries, skill/strength and contest formulas, tick/state/RNG flow. | T101's dependent pitch analysis and T108's arithmetic audit; later work inherits this gate through dependencies. | hard | M; 2–4 h | high | high |
| [ES-R2](https://github.com/diegoami/goal2-archaeology/issues/455) | Field behaviour and experimental design | T101–T105 and T108: positioning/motion, possession/scoring, tactics/AI, lifecycle, experiment preregistration and arithmetic/index audit. | T106 synthetic probes and T107's first bounded match batch. | hard | M; 2–4 h | high | high |
| [ES-R3](https://github.com/diegoami/goal2-archaeology/issues/456) | Empirical evidence and defect attribution | T106 and T109: selected original-backed probes and cross-module consistency audit; explicit owner deferral of T107 and its resulting inference gaps. | T110's architecture/rewrite assessment and completion of the empirical conclusions in T112 within the reviewed evidence scope. | hard | M; 2–4 h | high | high |
| [ES-R4](https://github.com/diegoami/goal2-archaeology/issues/457) | Rewrite feasibility and compatibility contract | T110: readable architecture alternatives, representative before/after pseudocode, compatibility requirements, costs and prototype proposal. | T111 additionally requires an explicit owner design decision; T112's final architecture recommendation requires ES-R4 acceptance. | hard | M; 2–4 h | high | high |
| [ES-R4P](https://github.com/diegoami/goal2-archaeology/issues/458) | Optional readable-rule prototype | T111 only, if the owner approves a prototype after ES-R4. | Publication/adoption of prototype conclusions. T112/T113 can complete without the prototype; if they include its results, those claims require this review or must remain explicitly unresolved. | hard | M; 2–4 h | high | medium |
| [ES-R5](https://github.com/diegoami/goal2-archaeology/issues/452) | Final guide and integrated conclusions | T112's assembled guide and the T113 review packet, with integrated spot-checks across all accepted earlier stages. | Completion of the study and promotion/delivery of its integrated conclusions. This is the existing T113/#452 review, not a second final-review task. | hard | M; 2–4 (already in T113) h | high | high |

T113 implements ES-R5; it is counted once. ES-R4P applies only to an approved T111 prototype.
T112/T113 can finish without T111, and cannot present unreviewed prototype results as established.

## Independence, activation and acceptance

These issues are **planned checkpoints**, not active milestone reviews. No candidate SHA, tag,
verdict or reviewer run is claimed. When a checkpoint's entry work is merged and its acceptance
artifacts exist, activate it under docs/milestone-review.md: populate the exact Milestone,
Candidate and Previous milestone fields, contributing PRs, green candidate CI/required checks,
claims with file:line, evidence hashes, owner decisions and the ready-to-paste reviewer prompt.
Allocate the real `m<n>-engine-study-...` tag then; ES-R identifiers are planning names, not tags.
The first baseline is the commit immediately preceding the study's implementation, pinned when
T95 starts. Later review packets name the preceding accepted checkpoint and the precise study
changes, including any intervening corrections or unrelated changes needing separate attribution.
The conditional ES-R4P states its ES-R4 baseline explicitly.

Once activated, the repository's normal fix-only-main, candidate recheck and tag rules apply.
Only the exact accepted SHA is tagged. Drafting a future chapter need not wait; dispatch or
publication that relies on a gated claim waits for its checkpoint. Dependencies below express
that constraint; they do not alter the repository's migration/delivery scheduling priority.

Use an independent Claude or Kimi reviewer who did not author the deliverables under review.
The owner selects the actual review model/settings at activation. The corrected
[main-session model policy](engine-study-models.md) assigns implementation and packet preparation
to Sol/high, with rare bounded Sol/xhigh help; neither a helper nor the author supplies the
independent verdict. The main session prepares
the packet, supplies evidence, handles fixes and relays findings in full; it does not substitute
its own implementation checks for the independent verdict. No reviewer is launched by this plan.

Each review examines all changes assigned to its scope, traces consequential claims to original
named/decompiled/listing sources and retained evidence, and spot-checks preceding invariants.
Prior receipts are reused; new probes/reruns require an explicit question and budget. Reproduce
or label unverified findings. Documentation/link/CI success does not establish football semantics.
The launcher, severities, mandatory candidate checks and review-round limit remain those of the
existing milestone process.

The reviewer posts one AGREE/BLOCK verdict with actual checked scope, limitations and findings:

- **MUST-FIX:** unsupported consequential claims, incorrect arithmetic/state interpretation,
  invalid controls or experimental inference, misattributed defects, missing consequential
  coverage or a compatibility contract that cannot justify the proposed design. These block
  dependent conclusions within this checkpoint's scope.
- **SHOULD:** useful improvements that do not invalidate the accepted claims; record their disposition.
- **OUT OF SCOPE / UNVERIFIED:** identify the evidence gap or issue; never present it as a
  reproduced defect. An acknowledged unknown need not block unless a dependent claim assumes it away.

Resolve and recheck MUST-FIX findings on the revised candidate, then obtain AGREE, tag that SHA
and close the checkpoint issue. Keep SHOULD and unrelated findings as explicit follow-ups.
Three BLOCK rounds escalate under the existing process. Existing claim-level independent review
requirements still apply; these checkpoints provide integrated review rather than postponing all
game-rule scrutiny to the end.

## Review packets

### ES-R1

**Foundations** — [review issue #454](https://github.com/diegoami/goal2-archaeology/issues/454).

**Entry:** All contributing task slices merged with source/evidence citations and required checks; inventory counts and unresolved buckets frozen for the candidate.

**Review:** Verify field/routine census completeness, signedness/ranges/lifetimes, branch arithmetic and independently calculated threshold examples. Trace an ordinary tick and distinguish watched, quick and unattended paths. Challenge claims of unused fields and unsupported evidence promotion.

**Exit:** The census is accounted for, consequential formula/flow claims are supported, and MUST-FIX errors are corrected and rechecked. Unknowns have explicit boundaries and issues rather than invented answers.

**Gate:** T101's dependent pitch analysis and T108's arithmetic audit; later work inherits this gate through dependencies.

### ES-R2

**Field behaviour and experimental design** — [review issue #455](https://github.com/diegoami/goal2-archaeology/issues/455).

**Entry:** ES-R1 accepted; contributing task slices merged; control/routine coverage, causal examples and the exact planned probe/batch budgets are committed before new measurements.

**Review:** Trace source-to-field mechanisms and hidden pitch occupancy/display effects; check control interactions, lifecycle persistence and arithmetic-candidate classifications. Challenge experimental hypotheses, independent expectations, falsifying controls, fixture reachability, seed/context design, precision, multiplicity, stopping rules and capped compute. Reuse T79 instead of duplicate fidelity work.

**Exit:** Mechanism coverage is complete or explicitly unresolved. The selected experiments can falsify their predictions within a justified budget, and no unresolved MUST-FIX flaw is used to launch them.

**Gate:** T106 synthetic probes and T107's first bounded match batch.

### ES-R3

**Empirical evidence and defect attribution** — [review issue #456](https://github.com/diegoami/goal2-archaeology/issues/456).

**Entry:** ES-R2 accepted; immutable raw records, actual budget receipts, source fingerprints, analysis scripts, deviations and candidate reproductions are committed.

[designed: owner decision, 2026-10-27; #571] T107's current scoring pilot is deferred until
T106 results inform a better design. ES-R3 reviews the completed T106/T109 evidence and the
explicit absence of match-effect results. This does not complete T107, approve a replacement
experiment, or permit scoring-effect/null-result claims. A revised proposal needs its own
precision, executable contracts and pre-execution review before spending. Later empirical
conclusions retain this gap; source-based architecture assessment can use only accepted evidence.

**Review:** Recompute selected summaries and literal expectations, inspect completion/refusal controls and limited held-out reruns where justified. Check effect intervals, null results, seed/context structure and RNG divergence. Separate original quirks, port defects, documentation/test defects and unresolved attribution; confirm minimal reproductions and no duplicate issue claims.

**Exit:** Published results reproduce from retained inputs, claims match their actual sample and scope, and every consequential discrepancy has a supported classification or an explicit evidence gap. MUST-FIX analysis/attribution errors are corrected and rechecked.

**Gate:** T110's architecture/rewrite assessment and completion of the empirical conclusions in T112.

### ES-R4

**Rewrite feasibility and compatibility contract** — [review issue #457](https://github.com/diegoami/goal2-archaeology/issues/457).

**Entry:** ES-R3 accepted; architecture assessment and cost assumptions committed, including source-pinned representative difficult routines and the proposed observable contract.

**Review:** Compare named memory views, extracted rules, explicit transitions and a full rewrite. Check numeric semantics, RNG consumption, occupancy/display dependencies, save/load/decision boundaries, event/API behaviour and downstream contract obligations. Challenge the validation cost, no-go option and whether the proposed slice tests a meaningful design risk.

**Exit:** The recommendation and its limits are defensible, any MUST-FIX contract gap is resolved, and the owner receives a concrete design choice. Reviewer AGREE is not owner approval to implement a prototype or change a backend.

**Gate:** T111 additionally requires an explicit owner design decision; T112's final architecture recommendation requires ES-R4 acceptance.

### ES-R4P

**Optional readable-rule prototype** — [review issue #458](https://github.com/diegoami/goal2-archaeology/issues/458).

**Entry:** ES-R4 accepted; explicit owner design choice and prototype contract recorded; isolated prototype, differential checks and controls committed.

**Review:** Independently check ordinary and boundary equivalence against original/accepted-reference behaviour, the failing control, timing methodology and evidence for readability. Look for shared expected/actual implementation, untested numeric/RNG behaviour and claims wider than the selected slice.

**Exit:** Prototype claims are supported on the declared slice and MUST-FIX flaws are corrected and rechecked. Decide separately whether to pursue a production rewrite. A rejected/deferred prototype can remain documented with no wider equivalence claim.

**Gate:** Publication/adoption of prototype conclusions. T112/T113 can complete without the prototype; if they include its results, those claims require this review or must remain explicitly unresolved.

### ES-R5

**Final guide and integrated conclusions** — [review issue #452](https://github.com/diegoami/goal2-archaeology/issues/452).

**Entry:** ES-R1–ES-R4 accepted; guide coverage checklist, reproducible summaries, known limits and prior finding dispositions committed. ES-R4P is needed only for prototype claims included as established results.

**Review:** Follow a complete attribute-to-pitch causal chain, inspect field/control/routine coverage and recheck selected calculations/results against primary evidence. Challenge omitted contexts, overstated certainty, contradictory chapters, defect dispositions and the final rewrite recommendation. Verify how each earlier MUST-FIX finding was resolved without routinely rerunning all experiments.

**Exit:** The guide's consequential claims are supported, coverage gaps and assumptions are visible, included prototype conclusions have the required evidence, and no MUST-FIX finding remains on the accepted candidate. The final verdict names actual scope and limitations.

**Gate:** Completion of the study and promotion/delivery of its integrated conclusions. This is the existing T113/#452 review, not a second final-review task.

## Cost and dependency changes

ES-R1–ES-R4 add **8–16 active hours** (four reviews at 2–4 hours). ES-R5's 2–4 hours were already
included in T113, so it is not added again. If T111 is approved, ES-R4P adds a further 2–4 hours
alongside the prototype's existing 2–4 hours. These are provisional first-pass estimates; findings,
fixes, further review rounds and additional compute can require re-estimation before execution.

The programme therefore becomes **41–82 mandatory active hours**, plus **4–8 hours for the optional
prototype and its review**, or **45–90 hours with that option**. CPU/runner time remains separately
capped in T105; this planning change starts no review or measurement.

The explicit new gates are ES-R1 → T101/T108; ES-R2 → T106/T107; ES-R3 → T110 and T112's empirical
conclusions; ES-R4 → T111 and T112's architecture conclusions; and ES-R5 → completion of the study.
If prototype conclusions are included, ES-R4P gates those conclusions. The owner's T107 deferral
keeps match-effect claims unresolved while ES-R3 can review the completed probe/integration scope.
Drafting and independent source reading can continue while claims await review.
