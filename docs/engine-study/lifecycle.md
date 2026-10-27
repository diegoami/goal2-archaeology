# After the whistle: restoration, records and recovery

The end of the watched match is a boundary inside a larger fixture transaction. The summary,
live score, fixture record, player records and competition tables have different consumers and
update times. Treating `run_match` as the entire transaction loses important writes.

This proposed source interpretation covers [24 routines](../../notes/engine-study/T104/T104e-v1.json).
The [calculator](../../notes/engine-study/T104/postmatch.py) checks supplied arithmetic and
altered-rule alternatives without executing an original/port routine, UI interaction or match.
Existing F016/F018/F019/F020/F023/F027/F030 and T71/T72/T77 evidence keeps its own scope;
these explanations do not promote findings or fill the genuine-key gaps on #400.

## Post-match order and path boundaries

For a played fixture, `0791:F1F6` performs this sequence:

1. Set up the match and team menu. Save form for each nonzero squad word in slots1..20 to
   `9B07`; set the starting XI's performance to55.
2. Play `F098`, including extra time/shootout when applicable. Select man of match with
   `CAB0` **before** restoring form/energy. Snapshot when watched, show summary and refresh
   competition tables; offer summary saving on the watched route.
3. `CB7D` restores saved form. For signed-positive energy it copies current fitness to energy;
   zero injury energy remains zero. Thus ordinary live fatigue does not itself persist as the
   next fixture's energy.
4. Show updated groups for nonfriendly fixtures; reset tactics for unmanaged sides. Clear
   in-match/menu/replay flags. `D050` updates country records. `BA4E` updates each managed
   country's80-player pool. Set game continuation state.

The caller `000E:6CA7` then handles applicable manager confidence/news/sacking, **then calls
`B7FA`** for both squads, advances the fixture index and refreshes competition tables. The
`F1F6` routine itself ends before that outer tail. The kit's `Match._advance` explicitly calls
`B7FA` after `F1F6` and before `_finish`, so an ordinary **completed Match includes those
player updates**. It does not reproduce all of the outer router's news/sacking logic. A raw
caller that stops at `F1F6` alone has not applied all caps, result form, recovery or ban transitions. The parent [match-flow](match-flow.md)
chapter describes the entry-point distinction.

The silent `000E:6970` route calls `D47E` result generation, `B7FA`, `B602` scorer credit,
`D050`, then resets both sides' tactics. Consequently silent scorers receive their extra
`B364(+1)` **after** result-form clipping. Watched scorer events occur during play and have
separate live/saved-form handling. A kind-zero unplayed fixture takes `BB2F`, which does not
call `B7FA`. “Quick” watched-match mode `D733` and outer silent result `D47E` are distinct
processes even though they share aggregate contest formulas.

A managed pool player who is also selected can be touched by both `BA4E` and later `B7FA`.
Pool recovery/form jitter and status transitions precede the squad/result transitions.
Do not collapse them into a single update, assume every player is touched once, or infer a
full natural outcome from an isolated call. In particular repeated ban transitions can matter;
pool membership and exact caller order belong in a reproduction.

## What persists and what is restored

| State | Trigger and writes | Carry-over or limit |
| --- | --- | --- |
| Live form, player+C | Match events can update current form and sometimes saved9B07; CB7D restores the saved value | Opponent live boosts can disappear; result B364 later clamps each call1..32 |
| Energy/fitness, +E/+D | CB7D refills positive energy from fitness; later3558/3651 selects reroll/recovery | Injury zero survives CB7D; recovery can subsequently heal it |
| Caps word+8 | B7FA increments XI and bench players carrying status element3 | Every nonzero squad word is inspected; an unused bench player gets no cap |
| Career goals word+A | Normal6443 or silentB602 | Own goals/shootout goals have different exclusions; not a commentary count |
| Scorer byte+11 | B3B7 in eligible competitions; separate yearly reset | Top3 rows use strict count insertion; byte width remains relevant |
| Performance word+12 | XI starts55; substitute starts10055; commentary applies table deltas | Kept for summary/MOM, decoded differently from raw AI substitution comparison |
| Status+10 | B27F clears old suspension/red/current yellow; derives next suspension and carried booking | Availability uses status and energy; no numeric injury-duration byte here |
| Ability+4 and peak+2 | No new write in these postfixture routines | Do not describe recovery as ability growth; seasonal development is another path |
| Manager accumulator+2 | B6CC adds signed result delta, clamped−127..127 | Separate from manager ability+1 and later seasonal folding |

`CAB0` scans side0 then1, slots1..20. Bench slots need the substituted-off element3; it
skips performance0x7FFF. A **signed** value above5000 loses10000 before comparison. The
best starts at1 and replacement requires strict greater: XI95 beats a later bench10095
on their equal decoded95. A bench player without the participation bit is excluded even
with a high number. If every eligible value is<=1, this routine leaves the previous winner
word unchanged; natural incidence is not established here. It also does not explicitly
skip a zero squad word like CB7D does. Valid roster/dummy assumptions matter at raw edges.

[Scoring](scoring.md) and [shootouts](shootouts.md) explain why a penalty can affect performance
through commentary without increasing ordinary career goals. Man of match is selected after
that phase. A rewrite must preserve this order if it promises original behaviour.

## Recovery and availability

`B7FA` identifies participants as slots<=11 or status element3 on the bench. Participants
receive a cap, recovery with participating flag1 (or a reroll), and the fixture result delta.
A participating bench player also loses element3 and gets ordered `rand(2)` then `rand(2)`,
second minus first, as a separate clipped form call. Unused bench players instead get
`rand(4)` then `rand(2)`, second minus first, and recovery flag0. All nonzero squad players
then receive `B27F`, including unused or already suspended players.

The ban transition is explicit: clear old element8; red element6 sets element8 then clears6;
current yellow5 sets carried4 if absent, otherwise sets8 and clears4; finally clear5.
For raw statuses128,32,16,24,48 the outputs are0,128,8,128,136. A prior suspension normally
expires on an update, a red becomes a new one, and a second carried booking becomes one.
Those are **per-call** rules; the managed pool/squad overlap above prevents assuming one
call per calendar fixture for every identity.

`5A8F` chooses gradual3651 when the fixture kind belongs to `DS:0F3E`, or for a friendly
where the supplied country's continent differs from the fixture's second country. That
friendly comparison can hold for sideA on a cross-continent trip; for sideB it compares
itself and is false. Otherwise3558 rerolls fitness/energy.

For3558, age>peak+4 selects baseB13 instead of16. Managed players consume `rand(B+1)` first,
then `rand(3B)`, storing `B+second-first`; unmanaged players store `B+rand(2B)`. The routine
clamps signed fitness above32, **copies it to energy**, then clamps signed fitness below1.
Thus legal managed extreme B16, draws17 then1 gives **fitness1, energy0**, not1/1. This is
an original write-order candidate, not a newly established port defect or measured injury rate.

For3651, age>peak+3 selects maximum25 instead of32. Starting from signed fitness:

| Context | Ordered draws | Delta before clamps |
| --- | --- | --- |
| Energy exactly0 | rand2, rand8 | first−second |
| Nonzero energy, participant | rand2, rand8 | second−first |
| Nonzero energy, unused/pool | rand3, rand2 | second−first, then+1 if resulting fitness<16 |

A result below1 becomes1; otherwise it is capped by age. After writing fitness, signed-positive
old energy receives fitness automatically. Other energy requires `random-is-one(3)` to heal.
With fitness20, energy0 and draws1,8, fitness becomes13; energy remains0 on a failed coin or
becomes13 on success. With positive energy and participant flag, the same draws yield27/27.
With fitness15, positive energy, unused flag and draws3,1, the result is14/14. These are
supplied legal draw projections, not recorded recovery samples.

An annotated conditional sequence connects the layers: save form14; live form18/fitness20/
energy4/yellow16/caps3 at full time; choose MOM; CB7D gives form14/energy20; assume this
identity is outside the managed pool; outerB7FA adds a cap, participant recovery draws1,8
produce27/27, result delta+3 gives form17, and B27F turns yellow16 into carried8. Final:
**form17, fitness27, energy27, caps4, status8**. Pool membership or different fixture recovery
routing changes this sequence, so those conditions must travel with an experiment.

## Country and competition consumers

`B71C` starts with `(opponent_rating−own_rating)/32`, signed truncation toward zero. Country
rating10E7 is `((33−rank)*(5−continent)+129−order)/2`. A decisive fixture adds absolute
signed-goal margin for its winner or subtracts it for its loser. It then doubles when
`(winner==side)==(side==0 or fixture-kind-in-0F3E)`. Draws retain the rank term. `B364` clamps
each resulting form update1..32. For form31, +3 followed by−1 gives31; combining into+2 gives32.

`D050` uses fixture result+3 for season W/D/L and streaks, but stored goals for goals-for/against
and margins. A stored2–2 with shootout result0 counts a side0 win with two goals each; with
zero rank term, B71C's margin contribution remains0. Streak helpers increment/clear venue
and overall byte counters, then update maxima. Largest-result replacement uses>=margin,
so a later equal-margin fixture can replace an earlier record. Venue/host selection follows
the original helper calls, not an assumed interpretation of listing order.

`8757` rebuilds groups at stages2,3,5,7 and playoff aggregates at6. Stage7 has one continent;
stage3 has two groups. `59D8` selects the second table bank at stages3,4,7,8. Group82BD
recomputes from matching played fixture slots25..36, using goal comparisons for2/1/0 points,
then descending points, goal difference and goals scored. Equal keys have no fresh coin;
the original exchange sort need not be stable.

For equal two-leg aggregate totals,85F7 selects sideB when the second leg's first-side goals
are>=the first leg's first-side goals. Listing870A's `jae` catches equality before the later
parity-looking branch; that branch is unreachable. F023 already explains this help/code
inconsistency. This is not labelled a conventional away-goals rule without resolving venue.
Recomputation is safe to repeat because it rebuilds totals; it does not award points again.

Six model consistency examples and four worked sequences cover restoration, write order, substitute
rating decoding, all-squad bans, separate clips and the unreachable parity branch. Integrity
controls test coverage/source linkage, not natural incidence or causal average benefit.

Validation scope: legacy calculator labels called “controls” are model consistency examples,
not independently executed source/engine falsifiers. Some literal-only annotations do not
exercise a branch at all. See the [control-scope report](../../notes/engine-study/ES-R2/model-annotation-scope-v1.json);
[listing_guards.py](../../notes/engine-study/ES-R2/listing_guards.py) separately checks explicit
instructions and rejects altered-listing inputs. Neither establishes natural incidence.
