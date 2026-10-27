# Marking, takers and captain leadership

Marking has two distinct stages: an opponent identity can be assigned to a squad slot, then
an update decides whether to follow that opponent's adjusted coordinate. Zonal fallback,
availability, current energy and state can change the destination even with the same assignment.

The [source ledger](../../notes/engine-study/T101/T101b-v1.json) and
[worked calculations](../../notes/engine-study/T101/marking.py) cover eight positioning routines
and cite the assignment, leadership and sorting helpers across their boundaries. This is
proposed static interpretation, using the original named view followed by listings and port
comparison. No engine routine, synthetic fixture or new match is executed here. Structural
coverage checks cannot establish football meaning or natural visit frequency.

## Assignment and identity

Two similarly named tables serve different purposes:

| Storage | What the words hold | Main role |
| --- | --- | --- |
| `DS:9A3E + 40*side + 2*squad_slot` | Opponent **player identity**, or zero | Marking assignment; read by `0791:47C5`. |
| `DS:9976 + 10*side + 2*role`, role 1..5 | Own **player identity** | Captain, corner, penalty, free-kick and goal-kick takers. |

These are not live pitch-slot numbers. Helpers resolve the stored identity back to a current
slot when needed. The taker table's offset-zero byte also holds fixture-group context; it is
not a sixth taker. Historical names `pick_marker_by_skill` (`1FDD`) and `assign_marking_slots`
(`20E3`) are misleading: their table is the captain/taker table, not the opponent marking table.

The actual automatic marking assignment is `1771:3EF8`, with nested `1771:3E2F`.
For each side it builds role lists for outfield slots 2..11. Own sweepers, unavailable players
and players with status **element 7** set are excluded from automatic pairing. That is the
seventh set element (mask 0x40), not zero-based bit 7. The interface calls it Protect zone;
the important implementation effect is that such a player's existing marking word is retained.
Opponents already named by retained assignments are removed from the automatic candidate list.

The pairing passes prioritise opponent role ranges 12..13, 9..11, 5..8, 1, then 2..4.
Within a pass, `3E2F` visits four preference-table rows at `DS:0EE6+14*row`, and opposing
slots from 11 down to 2. It takes the first own role-list occurrence matching the preferred
role, clears both candidate entries and records the pairing. This is ordered table matching,
not a nearest-opponent search or an optimisation of marking skill. The final writer clears
unprotected assignments unless team tactic element 8 enables automatic man marking; slot 1
is cleared, and a role-1 sweeper in slot 2 has its assignment cleared before pairing.

Turning off automatic man marking does not remove all opponent-sensitive movement.
`47C5` can find a local fallback target when its assignment word is zero. It scans opposing
outfield slots 2..11 and retains each available in-zone candidate encountered, so the **last**
eligible slot wins. There is no distance comparison and no early break in that scan.
An existing assignment is resolved by player identity; if the identity no longer resolves to
an available opposing outfield player, the stale assignment is cleared.

`0791:2218` keeps squad words, saved-form bytes (`9B07`) and marking words together during
the surrounding `230C` sort. That caller separately swaps pitch records, remaps holder-related
selectors and rebinds the pitch data. Its tail calls `3EF8`, glyph refresh, `20E3`, then
`419C` to recompute posts. Sorting only the squad array would break these relationships.

## Following an opponent

`0791:4438` tests a rectangular zone around the home post: lateral difference must be below
four and directed longitudinal difference below nine. Outside state 9 it first adds
`DS:07BE+played_role` to the post's y byte. `44C1` instead uses the player's current position,
thresholds four and six, and excludes a holder or state-13 record. Edge differences 4, 9
and 6 fail; these are strict tests, not circular radii. Follow the direction operations on the
specified coordinate: the helper arguments and stored post/current point have different frames.

When `47C5` resolves a target, it copies that opponent's current coordinate into its caller's
local target word. It then rejects an opponent standing in that opponent's own half (`2C54`).
For a remaining target, the longitudinal displacement draw has bound:

```text
bound = 1 + max(0, opponent_feinting - own_marking) // 16
target_y = byte(target_y - marker_attack_direction * rand(bound))
```

The compared values are effective skills 8 and 5 through `278A`. Even bound one consumes a
draw and displaces by one. A skill difference of 15 leaves the bound at one; 16 raises it
to two. The result is a target adjustment, not a probability of winning possession.
The write changes the high byte of the copied local target word; preserve that overlap in
a readable translation, while giving the target a clear coordinate representation.

`0791:4A28` first considers whether the player is on the holding side:

- On that side, `2B7B` can trigger a home-derived target reset. Its bound is
  `33-signed_energy`; for ordinary energy 1..32 the ideal isolated success is 1/bound.
  A role-1 player with the ball no more than ten ahead also resets. Failure can leave the
  existing destination in place.
- On the defending side it first installs a [home-derived destination](positioning.md),
  consuming that routine's jitter draw when applicable. A keeper may replace it with the
  ball coordinate under live-clock/area and push-forward conditions.
- A defending outfielder asks `47C5` for a target. The copy is suppressed when live activity
  is off and the target is the current holder. Otherwise it consumes `rand(6)` and requires
  **signed energy > draw**. Finally, with half-pitch e5=0, adjusted target y times marker
  direction must be negative. Full-pitch e5=1 bypasses that final guard.

Energy one never passes this six-draw comparison; energy two passes only draw one; energy
six passes draws 1..5; energy seven passes all six. These are accepted draw values, not match
success percentages. In particular a rejected copy may still have consumed the post jitter,
displacement and energy draws, changing later random results.

There is a qualification to the apparent full-pitch effect. For opposed directions, an
opponent outside its own half has `target_y*marker_direction<=0`. After a positive,
nonwrapping displacement it is strictly negative. Under those assumptions the half-pitch
guard already passes, so bypassing it cannot change this copy. This is a T108 audit candidate,
not a claim that element 5 has no effect: its depth-table effect is independent, and wrapping
or unusual contexts need separate analysis. Older descriptions that infer an extra following
benefit solely from this guard need that qualification.

## Leaders and worked examples

`0791:1F3C` chooses the available first-eleven player with the greatest derived leadership.
Strict replacement preserves the first tie. For normal nonnegative `rating-profile`,
`1771:30D9` takes the remainder modulo eight, halving it below age 21. Rating 72/profile 4
therefore gives leadership two at age 20 and four at age 21. The listing uses signed remainder
then unsigned division: negative edited differences require a separate arithmetic audit rather
than substituting Python `%`. If all eleven are unavailable, `1F3C` returns an uninitialised
winner local; natural reachability of that case is unresolved.

`0791:1FDD` chooses takers by effective skill, retaining the first equal best candidate.
Roles 2..5 use elements 7, 12, 12 and 2. The static start-slot rule excludes the keeper for
roles 2..4 but includes slot 1 for role 5. The stored result is the player's identity.
Availability and gated/derived skill can change the selected taker without changing the squad.

`20E3` automatically refreshes captain/takers for unmanaged sides. A managed side before
the in-match-menu context refreshes takers while preserving the captain; after that context,
an unavailable captain or one outside the eleven can trigger the captain prompt. These are
separate branches, not a blanket “computer side only” routine.

After those branches, **both sides' eleven pitch records receive twice their captain's
leadership**, added to cached byte `+11`. `A260` initially supplies manager bonus plus 32;
that initial value is not the whole later cache. Starting at 56, leadership four gives 64.
`278A` gates its effective-skill addition by element/event. `34C1` independently adds the raw
byte again on events1/2 for ball duration, so its influence is broader than the skill gate
but remains different from a flat bonus to every skill.
Binding resets and captain application order matter; calling the additive step twice is not
equivalent to rebinding once. A byte-edge calculation, 250+14 becoming 8, illustrates storage
width only and is not evidence that a natural match produces that cache value.

For a local marking sequence, assume `4A28` resolves an eligible opponent at `(2,-2)`, marker
direction +1, marking 48 and opponent feinting 81. Post fallback is installed first. The
displacement bound is three; supplied draw three yields `(2,-5)`. With live activity on,
energy six and energy draw five, the energy test passes and the half-pitch sign test passes,
so the destination becomes `(2,-5)`. Change the energy draw to six and the copy fails: the
post-derived target remains. Other target selection and earlier play-state gates remain
declared prerequisites, not observations from a full fixture.

The calculation script checks strict zone/energy edges, skill-difference thresholds, tied
selection and captain cache arithmetic, rejecting four altered interpretations. A rewrite can
use distinct types/names for opponent identity, taker identity, resolved pitch slot and target
coordinate. Keep assignment order, fallback scan order, byte writes and conditional draws;
cleaner names alone must not change those decisions.
