# Cross-module consistency: what is a rule, a contradiction or still unknown?

The integration audit establishes no new production gameplay defect. The proposed role-label
contradiction was a false positive: role titles and automatic selection skills describe different
things. The audit preserves several original quirks and path differences, and
keeps continuation/coverage questions open. Source-based conclusions remain proposed until
ES-R3 review. The [nine-group register](../../notes/engine-study/T109/T109b-v3.json),
[reproducer](../../notes/engine-study/T109/integration.py) and
[boundary audit](audit-boundaries.md) state exact evidence and limits.

## Candidate register

| Area | Bounded result | Disposition / next evidence |
| --- | --- | --- |
| Cache and reset lifetimes | Captain-derived pitch cache is separate from live player attributes; managed pool/squad overlap can apply recovery/status updates twice. | Original quirk conditional on membership; [#546](https://github.com/diegoami/goal2-archaeology/issues/546) retains incidence/membership questions. |
| Side and identity bindings | Team tactics use the pitch side's country; own player IDs, squad indices and pitch slots are different domains. | Existing annotation defect [#553](https://github.com/diegoami/goal2-archaeology/issues/553), not a new runtime discrepancy. |
| Occupancy and pictures | Character plus attribute and draw order can affect whether a player moves. | Intentional source path; a boolean occupancy grid loses behavior. |
| Score, events and statistics | A provisional goal can be rolled back before scorer recording; goal history, career goals and shootout result have separate lifetimes. | Intentional path distinctions; final score cannot reconstruct every event. |
| Watched, quick and silent modes | They execute different routines, random draws and commit paths. | Intentional path distinctions; same seed does not make mode switching an equivalent run. |
| Save/load boundary | Live Python frames need recorded reconstruction; menus and proved matches have explicit restrictions. | Source contract known; universal natural continuation coverage unproved. |
| Manager/taker continuation | Role 4 is the free-kick taker, automatically selected by penalties skill; role 5 is the goal-kick taker, selected by kicking. | The old skill wording was correct; [#603](https://github.com/diegoami/goal2-archaeology/issues/603) retracts the false positive #599. Real checkpoint gaps remain [#400](https://github.com/diegoami/goal2-archaeology/issues/400). |
| Old offside reports | Line tracking, pending player, notification and adjudication are separate operations. | [#227](https://github.com/diegoami/goal2-archaeology/issues/227) needs the exact old continuation for incident attribution. |
| Surviving proof/coverage gaps | An uncaught mutant, omitted unit edges, displaced DOS return and unvisited display bodies have distinct limitations. | Existing issues stay open; no blanket dead-store or state-free classification. |

## Source contradictions and bounded examples

**Role names and selection skills are different quantities.** The original Pascal strings at
`DS:0A29+11*role` read CAPTAIN, CORNER, PENALTY, FREE KICK and GOAL KICK for roles 1..5.
The award callers agree: `6ECF` passes role 3, near-goal `6F3E` role 4, and `6F01` role 5.
The automatic selectors also read `DS:0764+role`: roles 2..5 map to skill elements 7,12,12,2.
Thus role 4 (free kick) is selected using penalties, element 12; role 5 (goal kick) uses kicking,
element 2. Role 3 (penalty) also uses element 12. `20E3` and the automatic `6D4E` branch pass
the mapped element to `1FDD`, which compares effective skill and retains the first equal best
available candidate. Its start-slot rule includes the keeper for role 5, excluding him for 2..4.
These criteria describe automatic selection, not a restriction on the managed manual choice.

The old paragraph's “penalties-selected role-4” and “kicking-selected role-5” were accurate.
I mistakenly treated those skill descriptions as role names under #599. The revised paragraph
now gives both the role and skill explicitly. [Review #603](https://github.com/diegoami/goal2-archaeology/issues/603)
withdraws that false positive; it does not identify an original or port selection bug.
The checker now reads both tables and guards their actual consumers. Four altered skill-byte
negatives and prose negatives reject omitted skill descriptions and the prior title-only edit.
The three title negatives still test titles alone; none is an executed engine mutant.
Historical v1/v2 ledgers remain unchanged and superseded; no player selection or input checkpoint changes.

**A cached field is not a continuously evaluated formula.** `20E3` adds twice captain leadership
to each side's eleven pitch `+11` bytes. Later readers include gated `278A` skill and direct
event-1/2 launch duration. Changing persistent context is not proof that an existing cache has
been recomputed. Likewise, `CB7D` restores temporary form and copies fitness to energy before
later post-match updates. The order is part of the rule. The managed-pool pass and later squad
pass can reach the same identity twice; a status transition that clears a suspension on one
call need not leave that same state after another. This is conditional source reasoning, not
a measured frequency of double updates. [Lifecycle](lifecycle.md) retains the detailed route.

**Side aliases can conceal a wrong description.** On coherent fixtures, looking up a player's
country and looking up the pitch side's country often agree. `26D7` actually calls `2974` and
uses `9B34/36`; a mismatched synthetic identity can distinguish them. That changes the
interpretation of a raw probe, not evidence that ordinary fixtures are inconsistent.
The annotation correction is already [#553](https://github.com/diegoami/goal2-archaeology/issues/553).
`2BB1` separately subtracts eleven for slots 12..22. A player ID is never interchangeable
with either domain merely because a stored example has a small value.

**The displayed picture can be simulation input.** For an ordinary live outfielder, `86D0`
reads the picture at `7C16`; attribute 0x0D bypasses the character-blocking test. The same
character can therefore permit or block a move depending on its attribute. `8537` and `8E24`
have different restoration rules, including a full-glyph equality guard for the latter.
Extracting a renderer safely would require retaining the simulation-visible cells and order.
This does not classify every display body as necessary or every omitted body as harmless.

**Different counters answer different questions.** `67B6` increments the provisional score
at `685C`. In normal mode, pending offside leads to the decrement at `68B3`, then `82EB`,
before normal scorer routine `6443`. The goal list saturates at eleven rows, while accepted
player/score totals have separate storage. In competition processing, fixture result controls
W/D/L while stored goals supply GF/GA; shootout result and working tally are distinct again.
These source paths explain why a commentary line or temporary increment is not an accepted
career goal. They do not reconstruct the exact old E015 incident from a final score alone.

**Modes are distinct engines/paths.** Quick `D733`, watched sweeps and silent result handling
have different computation and random consumption. `6337` adds three watched target draws
for a nonkeeper holder, and the quick branch omits those three; keeper transfer is separate.
The incomplete old annotation is already [#531](https://github.com/diegoami/goal2-archaeology/issues/531).
An identical initial seed only defines a coupling before the paths diverge. It is not evidence
that later draws refer to the same events. No cross-mode score experiment was performed here.

## Remaining gaps and review scope

For the original backend, the source supports a concrete save/load protocol: `Match.save` rejects an active menu,
a proved match, or live port frames without replay origin; version 4 can retain recorded
reconstruction data and `load` checks the recovered state. Guest memory and one RNG word
are insufficient on their own. Separately merged T78b at 2ec0fff4 adds explicit engine selection
and refuses port-backend checkpoints in that assembly slice. The original backend remains the
default. The two changed primary runtime sources are explicitly pinned to that commit; this is
not acceptance of standalone checkpoint delivery. Original action replay is another mechanism. Existing
tests/evidence retain their declared scope; this study adds no genuine manager checkpoint or
standalone sealed-delivery result. The independent delivery session owns that latter work.

The [issue snapshot](../../notes/engine-study/T109/issues-v1.json) captures twenty live issue
records as context; it is not a new execution or a replacement for current labels. Keep:

- [#375](https://github.com/diegoami/goal2-archaeology/issues/375): the initial pitch-direction
  mutation survived O8; a later overwrite is not a complete earlier-read/alias proof.
- [#412](https://github.com/diegoami/goal2-archaeology/issues/412): missing focused unit edges,
  despite source agreement and passing families.
- [#394](https://github.com/diegoami/goal2-archaeology/issues/394): direct proof prediction for
  displaced DOS return frames; successful runner tests are a different mechanism.
- [#416](https://github.com/diegoami/goal2-archaeology/issues/416): unvisited display boundaries;
  zero historical entries do not prove general removability.
- [#591](https://github.com/diegoami/goal2-archaeology/issues/591): retained bare-launch stack
  difference, with global liveness/isolated attribution unresolved.
- [#400](https://github.com/diegoami/goal2-archaeology/issues/400) and
  [#544](https://github.com/diegoami/goal2-archaeology/issues/544): actual manager-key checkpoints
  and partial/fallback order reachability remain separate gaps.

`C718` clears persistent-player tactics after binding `A91B`; it does not clear pitch direction
just because both fields have offset `+F`. That distinction guards against a tempting false
explanation of #375. Older annotation/helper issues likewise retain their own scope and
immutable evidence; this register does not silently close them.

T107's scoring pilot is deferred by the owner under
[#571](https://github.com/diegoami/goal2-archaeology/issues/571). T106 establishes selected
single-call mechanisms, not scoring effects, natural incidence or a null result. A revised
proposal must identify whether it needs branch/reachability observations or score-effect
estimation, then justify its precision and spending before execution. ES-R3 reviews the
completed probe/integration scope with that absence explicit. It does not approve a new
batch, establish whole-engine equivalence or authorise a rewrite/default change.
