# A bounded validation and sensitivity design

Static reading has already answered many local questions. The next measurements should
corroborate a few consequential mechanisms and estimate a small, explicitly conditional effect.
They should not repeat the entire fidelity programme or rank every tactic/attribute.

This is a **proposed preregistration**, requiring accepted ES-R2 before execution and executable
T106/T107 task contracts afterward. The [design ledger](../../notes/engine-study/T105/T105a-v2.json)
and [calculator](../../notes/engine-study/T105/design.py) execute only source arithmetic. No
engine, direct original/port routine, UI key sequence or match ran in preparing it. Final seed
lists, inference and stopping/CPU limits belong to T105b and are required before launch.

## Questions, provenance and interventions

The direct-probe questions are whether the original and port exhibit the unusual small/zero
launch vectors and free-kick wall boundary/sign rules already read from source. The sensitivity
question is whether the effect of quick-pass setting2 differs between initial live-energy16
and32 in two fixed watched-friendly contexts. A source gate prediction does not fix the sign
of a full-match scoring effect.

Use published E006 asset `e0afff6751747233-e006-1000-r0001.sav`, releaseE006, savestate SHA256
`e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d` and uncompressed memory SHA256
`87400f6a866e0798f61a9f3ab3bfcaa322469fa6b238b0061f1b7ab2b6a3f979`. The source registry is
[image_sources.py](../../experiments/E036-match-port/image_sources.py). Verify both identities
and the registered original build before any call. Record full source/runner hashes; original
bytes and memory stay in the published asset/cache, not in this repository's new output.

The two match contexts are constructed `Fixture(7,19,index=21,kind=1)` and its reversal
`Fixture(19,7,index=21,kind=1)`, both managed7, on that same template/year. The first follows
F40's context; the reversal is an admitted synthetic API fixture. It changes host direction,
setup table cursor and side order. It is not a second observed natural fixture or proof of
side symmetry. Require distinct valid countries, index inside the calendar, friendlykind1,
coherent manager mapping and an available/legal starting XI; a failed preflight stops the
batch, rather than silently selecting another context.

Four arms cross **energy16/32** with **team tactic2 off/on**. Freeze all other choices and use
one common image per seed/context block:

1. Before Match construction, copy complete player/country record lists. For every nonzero
   managed squad identity, clear only own-tactic enable element6 (mask32), so tactic2 inherits
   the team. Preserve its low value bit and all other personal settings. Set only country7's
   current team element2 (mask2) for the selected arm; preserve the other bits and defaults.
2. Construct Match with these lists, managed7, the block's seed, record_draws=True,delay_byte=0,
   substitutions=None and default captain. Do not answer a nonexistent `pre_match` decision:
   the API's public menu decision contexts are half_time/pause/extra_time and eligible
   substitution notices, even though it recognises the pre-match screen internally.
3. At the **first F098 play entry**, after the kit's setup and optional captain-seed input,
   make one declared research intervention: for nonzero identities of country7's current
   20-player squad whose signed energy is positive, set player+E to16 or32. Leave energy0
   injuries, nonpositive width edges, status, form, fitness, ability, profile and roles untouched.
   This includes eligible bench players so a later replacement is still in the defined cohort.
4. Freeze AI setup across energy arms and read it back: lineup/current opponent tactics,
   captain/takers, pitch bindings/caches, foul-table bytes/cursor and main seed. Only declared
   intervention bytes may differ at that boundary. No manual full rebind, reroll or reseed follows.
   Direct energy readers then observe the new value; cached leadership/placement is held fixed.

This is a **synthetic live-energy intervention**, not a player condition naturally produced by
previous fixtures or a normal manager UI operation. A pre-construction energy edit is a different
experiment: opponentBD03/BD83 can react during setup. That alternative is deferred here.
The runner must prove the one-time edit occurs before the first sweep, including callback order,
not merely install a hook with the right name. Re-entry/load must not apply it a second time.

Setup2648 first seeds from fixture_index*(year+1), generates255 precomputed table bytes and
sets cursor8437 to the second country. Match's optional seed is written later at the managed
captain prompt; the no-managed path instead writes atF098. The late override does **not** rebuild
the table or undo AI choices. Pin index/year and record all random state. Equal initial main
seeds pair the treatment inputs, but conditional draws subsequently diverge.

## Selected direct probes

Use the original registered code and the full registered Python port on identical constructed
states, with **real nested callees**. Existing stubbing unit Rigs are useful references for
argument layout but cannot serve as original-backed observations. T106 must create and hash the
complete construction manifest before its first invocation: template, segment/pointers, stack,
side bases, clock/directions, player identities/availability, pitch bindings, destination/ball
fields, restart flags and source fingerprints. No unspecified fixture-dependent field may be
silently “fixed” after seeing an output.

For launch34C1, use ball(0,0), a valid nonkeeper holder slot2, receiver selector2, event argument6,
and the supplied target. This bypasses the conditional miscue branch and shot-duration branches.
Declare all byte edits, pitch identity and the actual far-call arguments from the listing.

| Case | Target | Expected velocity | Timer | Emitted event | Projected endpoint |
| --- | --- | --- | --- | --- | --- |
| Zero displacement | (0,0) | (0,−1) | 2 | 6 | (0,−2) |
| Small horizontal | (1,0) | (1,−1) | 2 | 6 | (2,−2) |
| Diagonal control | (7,14) | (1,2) | 7 | 7 | (7,14) |

The minimum timer and `step(0)=−1` explain the first two. The diagonal distinguishes division
by `abs(vx)+abs(vy)` from universal halving (which gives10 and endpoint10,20). These projections
are not actual ball arrivals; boundaries and contests can intervene later.

For wall7621, choose genuine side/slot bindings but edited restart geometry, defending records
in relative slots7..11, the corresponding holder direction and satisfied wall predicates.
For positive direction, side1 holder slot2 and side0 defenders18..22 fit the standard bases;
for negative direction, side0 holder13 and side1 defenders7..11. Record the actual clock/base
bytes that make those directions true. Each row needs **five target invocations per backend**.

| Spot / holder direction | Expected targets for relative7..11 |
| --- | --- |
| (0,25), +1 | (2,30),(1,30),(0,30),(−1,30),(−2,30) |
| (0,26), +1 | (−3,−28),(−3,−27),(−3,−26),(−3,−25),(−3,−24) |
| (0,−26), −1 | (−3,28),(−3,29),(−3,30),(−3,31),(−3,32) |

Check the other-side predicate, `holder_direction*spot_y>0`, `abs(y)−abs(x)>10` and relative-slot
membership; include a negative guard witness outside the wall set. Direct target writes are
not followed by a normalising mirror. The far cases test the original quirk; they do not establish
its natural incidence.36 ordinary oracle/port target calls are needed across these six cases,
plus the explicitly capped setup, negative controls, mutants and repeats in T105b.

Literal expected values come from independent listing arithmetic, pinned in T102b/T104a and
this design, rather than running the same implementation to make both expected and actual.
Require normal return, stack/SP cleanup and complete target fields. Compare the port's memory/
ABI projection under the existing strict contract; label caller-unobserved/dead bytes separately
rather than silently masking a mismatch. A wrong-rule candidate is a falsifying control, not
another oracle. Preserve a failure before investigating it; do not repair original quirks.

## The four-arm match design

The batch runs **watched original code in the existing Unicorn-backed kit**. It is not a new
standalone path or a port-only sensitivity campaign. PlayOn policy uses answer() at the declared
half_time/substitution decisions, retaining original substitution budget and default choices.
No voluntary tactical/role changes, quick toggle, pauses, reloads or private input collection.
Unexpected/refused contexts and watchdog failures remain data; no new seed replaces them.
Friendlykind1 prevents extra time/shootouts, keeping the first batch bounded.

Source prediction: at5049's mid-pitch holder gate, keep-ball calls random-is-one(E/2). Quick-pass
first tries a coin, then that draw only on failure. Under an ideal independent-draw approximation,
E16 gives1/8 versus9/16 and E32 gives1/16 versus17/32. The actual finite LCG is slightly correlated:
for all65536 starting words, source enumeration gives off/on counts **8192/36866** at16 and
**4096/34815** at32. Quick's increment is28674 versus30719, respectively. This is **source-only
arithmetic at a fixed gate**, not an experiment or a claim about the distribution of seeds at
naturally reached opportunities. During a full match, fatigue changes E and the intervention
also changes skill/contests, possession and which opportunities occur. No directional full-match
goal/win-rate prediction is asserted.

T105b freezes the sample and primary estimand, not a search for a setting that wins. Instrument
intermediate gate opportunities/actions and record goals,shots,on-target,board possession bars,
fouls/cards/injuries and player energy/status before recovery and after the completed Match.
The original result is authoritative for this scenario. Existing T77 strict74-match comparisons
retain their narrower scope. **T79/#290 is still blocked and has no700-match sheet or A700
artifacts**; reuse it when delivered. A full port sensitivity run would be separately costed,
and any new standalone measurements wait for that path's accepted fidelity evidence.

## Instrumentation, controls and deferrals

A passive native observer can count52DD (entry to the tactic2 opportunity),5326 (action taken)
and532C (shared exit). A completion is counted **only when52DD was observed earlier in
that same5049 activation**, not on every532C hit. Assign an activation identifier at5049
entry together with SS/BP; a reused frame starts a new activation. Clear pending state on
completion and every return/abort. The keeper50FB,51AB,shot/header528F and deep-field52DB
routes also reach532C but do not open an opportunity; ignore all four. Associate only
normal-phase managed pending activations, resolving the actual
pitch pointer/identity and signed energy. Ignore deep-field actions entering other branches.
A denominator is an opportunity after prior gates, not every tick or every holder update.
It changes under treatment, so an action fraction is a descriptive conditional outcome and
cannot alone isolate a local probability effect. Preserve raw counts, actual E and phase;
zero opportunities are explicitly undefined, not replaced by0 or dropped without disclosure.

Use the family records' board and draw/event digests, and a richer additive record for observer
counts and intervention readbacks. Do not confuse attempted/provisional goals with retained
fixture goals, PK tally with fixture result, or commentary count with player stats. Match._advance
explicitly runsB7FA afterF1F6 before finishing; record pre-recovery full-time and post-update
states separately. It does not reproduce every outer-router news/sacking action.

Controls must include exact input-difference/readback checks, common-setup invariants across
energy arms, literal probe expectations, altered-rule rejection and non-wall guard; no-op edits
must preserve the baseline. Fixed repeats with/without the passive observer must reproduce all
unaffected result/draw/full-state projections. The active energy edit remains in both witnesses.
No additional RNG call may be introduced merely to sample/label an observation. Probe completion,
valid ABI and actually reached instrumentation are acceptance checks, not claims that a helper
“was exercised” because a mock returned a value.

Defer large attribute/formation rankings, alternate tactical interactions, natural rare-wall or
map-depletion rates, partial shootout cursor cases, the unused shot-coin probe and expensive
all-port match sensitivity. Their source answers/issues remain explicit. The first experiment
is not a licence for a broad campaign, original-bug fixes or production-default changes.
