# Engine anatomy: reading and evidence map

Start here to follow a manager choice or player field into what happens on the pitch. The
chapters connect original source, formulas, live state, control interactions and explicit
unknowns. The final empirical guide and rewrite recommendation are later programme work;
this index is not a claim that those stages have finished.

The [bounded probe report](micro-probes.md) records the six selected original/port geometry cases,
controls and separate field/ABI/memory/register comparisons. It makes no match-effect claim.

The [programme](../engine-study-plan.md), [live epic #433](https://github.com/diegoami/goal2-archaeology/issues/433)
and [review #456](https://github.com/diegoami/goal2-archaeology/issues/456) hold scope and status.
Foundations were independently accepted at `m5-engine-study-foundations`; field/design work at
`m6-engine-study-field-behaviour` (55d7a479). New probe/integration interpretations require ES-R3.
Source-derived
examples and hashes do not establish natural frequency, net tactical benefit or genuine key coverage.

## Follow a question

| Question | Read |
| --- | --- |
| What do the stored attributes mean? | [Player fields](player-fields.md), [derived traits](player-derived.md), [team/fixture fields](match-fields.md), [transient state](transient-state.md) |
| How do form, energy, ability, placement and leadership change effective values? | [Attribute formulas](attribute-formulas.md), [strength](strength-formulas.md), [skill gates](skill-gates.md), [contest formulas](contest-formulas.md) |
| What runs in a tick and consumes randomness? | [Match flow](match-flow.md); distinguish watched,quick,silent and the Match API boundary |
| Why does a player stand there, follow somebody or fail to move? | [Positioning](positioning.md), [marking](marking.md), [movement and occupancy](movement.md) |
| How are passes, shots, tackles,saves and goals resolved? | [Possession](possession.md), [ball play](ball-play.md), [scoring](scoring.md) |
| What do manager controls and the AI actually change? | [Tactics/control matrix](tactics.md), [lineup selection](lineup-policy.md), [computer policy](computer-policy.md) |
| What happens at a restart, sanction, substitution or shootout? | [Restarts](restarts.md), [discipline](discipline.md), [substitutions](substitutions.md), [shootouts](shootouts.md) |
| What persists into the next fixture? | [Lifecycle](lifecycle.md), including saved form,energy,recovery,bans and managed pool/squad overlap |
| Which suspected defects remain? | [Arithmetic audit](audit-arithmetic.md), [record/evidence audit](audit-records.md), [caller boundaries](audit-boundaries.md), [integration register](audit-integration.md), and linked live issues |
| What did the probes establish? | [Micro-probes](micro-probes.md): six geometry cases, controls and explicit state differences |
| What should be measured next, and at what cost? | Historical [design](experiment-design.md)/[budget](experiment-budget.md), then the owner-deferred [T107 revision proposal](t107-revision-proposal.md) |
| What is the full inventory and existing evidence scope? | [Inventory](inventory.md), then its source/evidence census |

For a first reading, use match flow → attributes/strength → positioning/marking/movement →
possession/ball/scoring → tactics/AI → lifecycle. Each chapter links a machine-readable ledger
and the script reproducing its worked source calculations. Those scripts do not execute the
faithful port to generate their own expected football result.

## Results that change how to read the engine

A few mechanisms explain many surprising outcomes:

- Form32 is a branch boundary, and live energy is distinct from fitness. A field edit at the
  wrong phase may be restored or leave a cached value unchanged.
- Line/depth targets, displayed occupancy and movement are coupled. A target is not an immediate
  position change, and the character/attribute buffer can block a move or trigger extra draws.
- A pass setting changes a candidate preference with fallback. A local random-opportunity gate
  does not establish a full-match benefit; equal initial seeds do not preserve later draw alignment.
- Team tactics1..4 can be shadowed by three-state personal overrides. A formation label is derived
  from available played roles; it is not a selected formation ID.
- Prematch bench selection and in-match replacement use different role maps. Several AI choices
  prefer an ordered or first/last candidate rather than the strongest player overall.
- Provisional goals, retained fixture goals, result bytes, shootout working tally, player goals
  and commentary performance are different representations. Read the phase and actual consumer.
- Post-match restoration and subsequent recovery are separate. A completed Match includes B7FA;
  a direct F1F6 call alone does not. Pool and squad updates can touch one identity more than once.

The source also contains quirks worth preserving until the owner chooses otherwise: degenerate
launch vectors, far free-kick wall signs, signed/byte edges, a zero-energy reroll write order
and greedy lineup-map depletion. They are not automatically port bugs or proof that ordinary
play reaches them. Existing annotation/test gaps and unresolved mutation coverage have explicit
issues rather than invented explanations.

## Reproduce the source and probe checks

For current probe/integration source, data and software checks with Python 3.12:

```bash
tools/heavy.sh ES-R3-source -- python3.12 -B notes/engine-study/ES-R3/verify.py
```

This audits six cases, 48 completed research calls, thirteen integration/boundary candidates,
55 literal instruction guards, separate selection-table/prose negatives and unchanged historical outputs. It executes no new engine
routine or match. The [ES-R3 receipt directory](../../notes/engine-study/ES-R3/) records checks;
required full CI is separate. Do not rerun measured batches merely to regenerate a report.

The accepted ES-R2 matrix must run in a clean checkout at its exact accepted commit,
55d7a479a7288ea044ceaa315eaff87e2077fdb6, not on newer standalone runtime sources:

```bash
tools/heavy.sh ES-R2-source -- python3.12 -B notes/engine-study/ES-R2/verify.py
```

The [receipt directory](../../notes/engine-study/ES-R2/) (`source-checks-v2.json`;v1 is historical) records 43 commands:
18 calculators,18 completeness/source/control checks, current transient-state/restore checks,
links and committed-range whitespace. It also audits 201 distinct scoped routine entries,61 worked examples,
nine arithmetic/index candidate groups,100 legacy model annotations and preservation of prior raw
study outputs. These are coverage and calculation counts, not 201 independently proven game rules
or 100 source/engine falsifiers. The matrix also runs 25 literal instruction expectations and
25 altered-listing negatives, the annotation classifier, and a committed-whitespace negative
control. The whitespace guard excludes generated index.tsv and immutable raw .log outputs. Full CI on the exact review candidate is recorded on #455. The annotation count does not
prove 100 independent falsifiers: [control_scope.py](../../notes/engine-study/ES-R2/control_scope.py)
classifies these labels as model consistency examples. Literal-only examples can pass even
when a source branch is omitted. Listing-bound checks are separately reported by
[listing_guards.py](../../notes/engine-study/ES-R2/listing_guards.py).

Original raw listings remain unchanged from the accepted foundation. Independently merged
T78 runtime additions are separately pinned and reported; the study fixes change no
production engine semantics.
Most field ledgers pin the later `a42c2cbe91300c8ee261b82fa993e665ed3f3325` snapshot, which includes
intervening T114–T116 annotation changes; current T97v5 pins c5945810 to include the
intervening API-overview source. Older foundation generators deliberately reject drift
from their earlier pin; reproduce those receipts at the accepted m5 checkout instead of weakening
them against today's named index. New corrections preserve earlier JSON/TXT evidence as separate
versions. The verification tool refuses to overwrite a receipt path.

## Boundaries before further work

T106's bounded direct probes are reported separately from the source-only field chapters.
Required full CI may execute existing emulator regressions; that is a separate verification
workload. No new research full match was run. The owner deferred the old T107 scoring pilot;
the revision proposal needs a concrete design and pre-execution gates before any spending.

T79's broad700-match fidelity sheet is still pending at this design pass; existing T77 exact
comparison receipts have a narrower scope. Standalone delivery proceeds independently in the
goal session's clone. Original-bug fixes, production defaults and a readable-engine prototype
remain separate decisions. The rewrite assessment waits for the empirical/consistency stage
and ES-R3; the optional prototype additionally needs the owner's explicit decision and review.
