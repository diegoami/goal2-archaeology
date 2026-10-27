# Engine anatomy: reading and evidence map

Start here to follow a manager choice or player field into what happens on the pitch. The
chapters connect original source, formulas, live state, control interactions and explicit
unknowns. The final empirical guide and rewrite recommendation are later programme work;
this index is not a claim that those stages have finished.

The [programme](../engine-study-plan.md), [live epic #433](https://github.com/diegoami/goal2-archaeology/issues/433)
and [review #455](https://github.com/diegoami/goal2-archaeology/issues/455) hold scope and status.
Foundations were independently accepted at `m5-engine-study-foundations`; later field/design
interpretations remain proposed until their exact ES-R2 candidate is accepted. Source-derived
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
| Which suspected defects remain? | [Arithmetic audit](audit-arithmetic.md), [record/evidence audit](audit-records.md), and linked live follow-up issues |
| What should be measured next, and at what cost? | [Experiment design](experiment-design.md), [frozen sample and budget](experiment-budget.md) |
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

## Reproduce the current source checks

From this checkout with Python3.12:

```bash
tools/heavy.sh ES-R2-source -- python3.12 -B notes/engine-study/ES-R2/verify.py
```

The [receipt directory](../../notes/engine-study/ES-R2/) (`source-checks-v1.json`) records41 commands:
18 calculators,18 completeness/source/control checks, current transient-state/restore checks,
links and diff whitespace. It also audits201 distinct scoped routine entries,60 worked examples,
nine arithmetic/index candidate groups,100 calculation controls and preservation of prior raw
study outputs. These are coverage and calculation counts, not201 independently proven game rules
or100 executed engine mutants. Full CI on the exact review candidate is recorded on #455.

Original raw listings and runtime/original_match remain unchanged from the accepted foundation.
New ledgers pin the later `a42c2cbe91300c8ee261b82fa993e665ed3f3325` snapshot, which includes
intervening T114–T116 annotation changes. Older foundation generators deliberately reject drift
from their earlier pin; reproduce those receipts at the accepted m5 checkout instead of weakening
them against today's named index. New corrections preserve earlier JSON/TXT evidence as separate
versions. The verification tool refuses to overwrite a receipt path.

## Boundaries before further work

No new study original/port probe or match campaign has been run for these field chapters.
Required full CI may execute existing emulator regressions; that is separate from new research
corroboration. The preregistration proposes six direct-case comparisons and a small four-arm
sensitivity batch with strict caps and likely inconclusive small-effect intervals. It does not
authorise execution until accepted ES-R2 and subsequent executable T106/T107 contracts.

T79's broad700-match fidelity sheet is still pending at this design pass; existing T77 exact
comparison receipts have a narrower scope. Standalone delivery proceeds independently in the
goal session's clone. Original-bug fixes, production defaults and a readable-engine prototype
remain separate decisions. The rewrite assessment waits for the empirical/consistency stage
and ES-R3; the optional prototype additionally needs the owner's explicit decision and review.
