# Opposing contests, selection and quick goal attempts

The engine does not implement one universal success formula. A skill can alter a range, a
random-draw bound, a deterministic selection, an action gate or a composite contest. This chapter
maps the direct effective-skill readers and derives local probabilities with their assumptions.

The [source/numerical ledger](../../notes/engine-study/T99/contests-v1.json) records all examples,
exact fractions, draw counts, controls and source hashes. It enumerates arithmetic states,
not matches. Neither the percentages nor the caller map establishes visit frequency in play.

## What the original compares

The [current contest ledger](../../notes/engine-study/T99/contests-v2.json) contains
**11 callers / 24 call sites** of `0791:278A`.
Counts below are instruction sites, not dynamic executions. Full segment prefixes matter:
`0791:3EF8` is a ball-action routine, not `1771:3EF8`'s marking assignment.

| Caller | Static sites | Conditional local rule / interpretation |
| --- | ---: | --- |
| `0791:1FDD` | 2 | Strictly better skill replaces an eligible incumbent; selection, no outcome draw. |
| `0791:287C` | 1 | Single-player quantised skill gate, covered by T99a. |
| `0791:34C1` | 2 | Events 1/2: max(timer+5,U16(V+pitch_extra)//3); events 3/4: max(timer+5,V//3), without the extra pitch byte. Full continuation probability remains unresolved here. |
| `0791:3B15` | 1 | Kicking reach max(30,rand(V2//4)); still draws when the floor makes the result constant. |
| `0791:3EF8` | 1 | Two reach modes: heading V4/div 6/floor 20 or kicking V2/div 4/floor 30, selected by argument/table. |
| `0791:47C5` | 4 | Marking versus feinting comparison changes a random offset weight by a divided difference; not a binary duel. |
| `0791:5474` | 2 | Holder dribbling 10 or heading 4 draw first; challenger tackling 3 or heading 4, factor 4 only in the ground/2C54 geometry branch; strict signed word win. |
| `0791:5B36` | 6 | Ground duel: holder 10 vs keeper 1 plus conditional 1 INSIDE keeper bound; air duel: holder 4 vs doubled keeper 1. In-flight catch is a separate travel/penalty-threshold wide comparison. |
| `0791:690C` | 1 | Conditional finish on events 3/4: rand(selected holder skill) > rand(32), constant opponent draw first; flags/set predicates can bypass this contest. |
| `0791:9ED3` | 2 | Shootout taker ordering by element 12, including keeper; preserve loop/swap/tie behaviour, not a random chance. |
| `0791:D5C1` | 2 | Quick foul: unsigned deterministic own tackling 3 < other dribbling 10, tactic/chance gate then opposed hardness draws; not the quick goal-trial mechanism. |

The tackle table selects holder elements 10/4 and challenger elements 3/4 for ground/air contexts.
Its bound multiplier is 4 only when the ground branch's geometry predicate 2C54 holds, otherwise 1.
It multiplies the challenger bound, not the probability of a won tackle.

Two especially important distinctions:

- Ground keeper duel `5B36` uses `rand(keeping + delta)`, where delta is 0/1 from the local
  context. It does not add one to an already sampled roll. The air branch doubles the keeping
  bound and opposes heading rather than ground dribbling.
- In-flight catch is a different branch. After its mode/goal-strip gates, a nonzero timer gives
  `rand(keeping) > penalty_term + rand(U16(4*ball_travel))`. The threshold is added in the
  wider signed comparison after extending the draw. A zero timer skips that contest; subsequent
  deflection/save choice still has its own draw. The penalty term and preceding 1-in-3 gate
  occur only in the selected shootout path.

The finish in 690C is conditional on event/flag/set membership; other routes bypass it.
Outside shootout mode, the shot-through gate can read shooting 11 even for events 3/4, while
their launch/finish tables can read penalties 12. A set piece need not depend on just one skill.

### Non-binary uses and boundaries

Shot/header reach in `34C1` has two forms: events 1/2 use
`max(old_timer+5,U16(V+pitch_extra)//3)` (skill call at 368A); events 3/4 use
`max(old_timer+5,V//3)` (skill call at 36DA), without the extra pitch byte.
The listing at 3692..369F includes the byte load, word addition and division; the other
branch divides the returned skill directly. There is no opponent draw at either comparison.
A larger value only changes reach when the skill term wins that maximum and survives
division. Full continuation probability remains unresolved here.

Long reach can be `max(30,rand(V_kicking//4))`. If the bound is at most 30, the floor makes
the reach constant even though a draw is consumed. The heading variant uses divisor 6/floor 20.
Do not optimise away that call or infer that kicking has no other effect on the action.

Marking/feinting in 47C5 changes a divided offset weight; a difference 15 versus 16 can alter
that increment, but the rest of the position-bound calculation still matters. It is not a
binary marking-win percentage. The taker selector 1FDD retains an incumbent on equal values;
the actual 9ED3 sorting loops may reorder equal entries indirectly, so a generic stable sort
is not a fidelity proof.

Hardness/foul and precomputed discipline-table mechanisms are additional families, not hidden
278A calls. T99a and the [state dictionary](transient-state.md) identify their inputs; T104
will explain their full eligibility/cap/consequence paths.

## Local opposed probabilities

For independent ideal-uniform draws X in 1..A and Y in 1..B, with positive nonoverflowing bounds
and a strict X>Y comparison:

```text
P(X>Y) = sum(y=1..A, min(B,y-1)) / (A*B)
m = min(B,A-1)
numerator = m*(m+1)/2 + B*(A-1-m)
```

At equal bound 100 this is 0.495, not 0.5: ties lose. Factor 4 means changing a bound 100 to 400,
whose ideal chance against 100 is 0.87375, not four times 0.495. Keeper bound 101 against 100
gives 0.5; adding one to the sampled 100-roll instead would give 0.505.

There are three distinct models in the next table:

1. **Ideal uniform:** independent uniform integers over each bound.
2. **Independent quantised:** the actual one-draw bin counts from the 16-bit mapping, but
   independence is still assumed between draws.
3. **Serial LCG:** the specified source-order calls over all 65,536 uniformly distributed
   entry seeds, preserving signed comparison and conditional threshold arithmetic.

| Example | Own/opponent bounds | Ideal uniform | Independent quantised | Serial LCG | Winning entry seeds |
| --- | --- | ---: | ---: | ---: | --- |
| equal 100 | 100/100 | 0.495000000 | 0.494999997 | 0.490219116 | 32127/65536 |
| tackle-factor4 | 400/100 | 0.873750000 | 0.873744506 | 0.873748779 | 57262/65536 |
| ground-keeper-bound-plus1 | 101/100 | 0.500000000 | 0.499999622 | 0.501129150 | 32842/65536 |
| air-keeper-double | 200/100 | 0.747500000 | 0.747496337 | 0.747558594 | 48992/65536 |
| inflight-catch-offset50 | 100/200 + threshold 50 | 0.061250000 | 0.061251830 | 0.061141968 | 4007/65536 |
| finish-versus32 | 100/32 | 0.835000000 | 0.834992409 | 0.835037231 | 54725/65536 |
| zero-own-bound | 0/10 | 0.000000000 | 0.000000000 | 0.000000000 | 0/65536 |
| equal 1 | 1/1 | 0.000000000 | 0.000000000 | 0.000000000 | 0/65536 |
| synthetic-signed-bound40000 | 40000/100 | 0.817912500 | 0.817913228 | 0.817901611 | 53602/65536 |

The catch row adds 50 to the threshold after signed extension; the ground keeper row already
includes its one point inside bound 101. Bounds 40000 are a deliberate synthetic signed-word
example, not a natural player claim. Normal examples have nonnegative small draw values,
but crossing 0x8000 makes a signed compare differ greatly from unsigned host arithmetic.

The serial equal 100 result 0.490219116 differs from the independent-quantised 0.494999997:
bin quantisation alone does not explain the dependence. Other bounds have smaller differences.
This is a mathematical seed-law comparison, not evidence of the same bias at every reached
game call site.

Order and tie controls expose source-sensitive changes. Equal 100's reversed assignment changes
64,640 seed-level outcomes; its inclusive comparison changes 896. At equal bound 1, changing strict
greater to greater-or-equal changes all 65,536 outcomes. A zero bound still returns 1 and consumes
a step, rather than representing a zero-valued roll.

## Quick attempts and stream dependence

`0791:B19D` uses four line sums in keeper/defence/midfield/attack order. For one team's attempt,
it draws the opponent first, then the team, stopping on each signed own<=opponent:

```text
rand(own_mid) > rand(opponent_mid)
rand(own_attack) > rand(U16(2*opponent_defence))
rand(own_attack) > rand(opponent_keeper)
```

The displayed comparisons describe the operands, not evaluation order: **opponent's call comes
first** in each pair. One attempt consumes 2, 4 or 6 draws. Three wins add a trial goal.

Under the independent models one can multiply the three local win probabilities. For the actual
serial generator the branch-dependent stream must be followed. The following calculations fix
the line inputs and uniformly enumerate the entry seed of **one attempt**:

| Example | Ideal independent | Independent quantised | Serial LCG | Draw counts: number of entry seeds |
| --- | ---: | ---: | ---: | --- |
| equal-two-bounds | 0.015625000 | 0.015625000 | 0.015304565 | 2:49153, 4:12289, 6:4094 |
| F021-fit-v-tired | 0.069195982 | 0.069198116 | 0.069061279 | 2:24177, 4:35623, 6:5736 |
| F021-tired-v-fit | 0.019698276 | 0.019699857 | 0.019683838 | 2:41425, 4:22103, 6:2008 |

The F021 examples reuse the [earlier analytical line sums](../../findings/F021-energy-and-form-set-a-players-strength-fitness-is-never-read-in-a-match.md):
fit [242, 1022, 1045,433] versus tired [181,778,770,341], and the reverse.
They are declared inputs to this calculation, not newly measured lineups or win rates.
For the fit direction, the ideal product is about 0.069196 and the serial result 0.069061.

Later attempts need not start uniformly: their entry seed depends on how many draws earlier
attempts consumed. The exact one-attempt result is therefore not automatically the rate for
all attempts in a whole B19D call. Nor is it a final goal-per-minute probability.

The silent wrapper D47E uses trial counts as a result, with a possible extra decider. Quick
minute code D733 instead saves the committed score, computes scratch trials and postprocesses
them before committing at most one goal. Scratch B261 writes are not already visible goals.
Watch, quick and silent wrapper semantics must remain separate.

## Coverage and evidence limits

The checker verifies the ideal closed form against 64 small brute-force grids, quantised
marginal masses and the fixed serial examples. Reversed-order and inclusive-tie controls change
outcomes; variable-length attempts can also change their end seeds. All 11 direct callers and
their 24 sites are accounted for by the static call table and pinned source locations.

These are local source-derived models. The event 3/4 launch continuation, full positioning
weights, foul/discipline composition, eligibility and repeated in-flight opportunities are
not reduced to new whole-path odds here. They retain explicit source/context gaps for the
pitch/lifecycle chapters. Old E011 coverage in F022 concerns that fixture; it is not current
all-path coverage merely because later families include more cases.

No new original binary, half or match was executed. No original return/record parity is claimed
for the new probability examples. The entry-seed law, fixed bounds and comparison width are
part of each mathematical claim. A local duel win also need not equal a credited save or goal:
later branches, including foul/deflection/clearance logic, still determine the field result.

```bash
python3 -B notes/engine-study/foundations/check.py --task T99b
python3 -B notes/engine-study/T99/odds.py --contests --check
```
