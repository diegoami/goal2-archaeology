# F019 Confidence is player +0xC; its result term compares the margin with country ranks

- **Status**: proposed
- **Question**: Q016 (Q05.4–Q05.6), T32.
- **Experiment and runs**: E018; E018-r0001 (defective) and E018-r0002
  (replacement), original-routine Unicorn probes, not complete DOSBox matches.
- **Artifact**: `goal2-67cf27d6`; input E011 half-time state SHA256
  `9820b47814dd96709b0844c7c970a208c4532de7dbf9f4d5e3ddbe597cbea8be`.
- **Confidence**: static-derived, unreviewed; B7FA's result and bench operations
  additionally checked against original guest execution (240 player words) for
  fixture kinds 1 and 2 only, neither of which is in the DS:0F3E set, so
  1771:5A03 returned false in every probed case. The 5A03-true doubling branch
  rests on the listing alone. No independent whole-match or human-sitting
  corroboration is claimed.

## Method

Static first: read the named B71C/B7FA/BA4E/BB2F, F1F6/CB7D,
000E:6970/6CA7 and 1771:5A03/5C60 views, then cross-check raw C and
assembly. Assembly settles the set-membership branch where C is misleading.
The complete direct +0xC and description-table reader/writer inventory is
in `experiments/E018-q016-confidence/notes.md`, with listing lines.
Static analysis establishes the arithmetic and routes but not concrete RNG
draws or the watched event sequence. The isolated B7FA probes corroborate
draw ordering, clipping and the rank-based term, not the complete fixture.
The first probe injected wrong offsets (squads at country +47, status at
player +7 instead of +0x10); its declared-input check fails both
`declared slot disagrees with injected squad` and `declared status disagrees
with injected +0x10` in all six cases. It is retained, printed and replaced,
never used as a successful comparison; no other check can set a record aside. Both start-state manifests
are under `evidence/E018/`. No further guest runs were taken on continuation.
The available E015 records describe one four-state scripted sitting, not
established before/after played-match pairs; none is used here (E015 README
lines 55–65). No missing watched event sequence has been invented.

## Answer and claim-by-claim basis

Paths below are relative to `static/goal-exe/`. Each claim is static-derived
unless its original-routine check is explicitly stated.

### Confidence and its storage

The help's result-relative player confidence is **player +0xC**, the byte
already called morale/form. B7FA passes its result term to B364, whose
player store is +0xC (`named/seg_0791_09.c:224–258`;
`named/seg_0791_08.c:1110–1127`). B364 adds a signed word to the signed
byte, with signed-word wrapping and a separate clamp to 1..32 on every
call (`code/seg_0791_18.asm:621` onward). It is not team morale (Q017).

The suspected DS:6ED4..6FF4 words are descriptions in the Pascal string
table rooted at 6EB4, with 16-byte strides, not expected-margin values
(`strings.tsv:1195–1212`). The player panel selects the morale string
using DS:78A3[min(+0xC,32)] (`named/seg_1771_03.c:881–892`). The notebook
enumerates every reference to the table root and finds no writer in those
routines; this is a listing sweep, not a guarantee against arbitrary memory
corruption. No numerical expected-margin array is established there.

### Expected margin and exact result term

For each side, country rating is signed IDIV 2 of
`(5 - continent) * (33 - continent_rank) + 129 - world_rank`, retaining
the instruction path's low word. Inputs are country +2C, +2A and +2B,
not selected players, skill ratings or the quick engine's line sums
(`code/seg_1771_02.asm:697–738`). B71C computes
`q = trunc_toward_zero((opponent_rating - own_rating) / 32)`
with signed-word subtraction (`code/seg_0791_18.asm:1012–1046`). Thus the
implicit expected own goal margin is `-q`; there is no separately stored
forecast at this call.

If fixture +3 is 2, it is a **draw**: the term remains q, which may be
nonzero. Otherwise add the absolute difference of the signed score bytes
for the winner, subtract it for the loser (`code/seg_0791_18.asm:1047–1070`;
margin helper `code/seg_1771_08.asm:1047` onward). The winner byte governs
this branch, including a shoot-out winner; equal score bytes do not by
themselves take the draw branch (literal test: 1-1 with winner byte 0, ratings
100 vs 164, gives 4, not the draw's 2). Then, only for a non-draw, double the
word if `(winner == side) == (side == 0 or 1771:5A03(fixture))`
(`code/seg_0791_18.asm:1071–1109`). 5A03 tests fixture +2 in DS:0F3E
(`code/seg_1771_08.asm:762–787`), the fixture-kind set predicate,
not a strength calculation. The retained DS:0F3E bytes (`98 ff`x24 `0f`,
then zeros) hold kinds 3, 4, 7 and 8..203; kinds 0, 1, 2, 5, 6 and 204..255
are outside it. Which kind is a friendly is **not established** by these
lines. The model takes the observed classification; it does not replace it
with a guessed friendly/competition flag.

**Help claim: yes for the sign, no for the size.** The term's **sign**
follows the margin minus the expected margin `-q`: before doubling the term
is `q + margin` for the winner and `q - margin` for the loser, and doubling
keeps the sign. Its **size is not monotonic** in the margin, because the
doubling applies only when `(winner == side) == (side == 0 or 5A03)`
(`code/seg_0791_18.asm:1071–1109`): a narrow win can score worse than a
draw, and a narrow loss better than a draw. With ratings 128 vs 1 (q = -3 for the strong
side, +3 for the weak), non-special kind: the strong side 0 gets -4 for a
win by 1, -3 for a draw and -4 for a loss by 1; the weak side 1 gets +4 for
a loss by 1, +3 for a draw and +4 for a win by 1 (literal tests of
`result_delta`; the non-special branch matched the guest in all probed
cases). The expected margin comes from country ranks, not current squad
strength, and the byte is also moved by clipping and by other ordered writes
and draws, so the help's claim is not a complete before/after rule. The
help's wording alone does not establish a different forecast.

### Participation and draws (original-routine checked)

B7FA ignores zero squad words. Slots 1..11 and bench status-bit-3
participants receive the result term. Participating bench then receives
`draw(2) - draw(2)`; the first draw is subtracted. Unused bench receives
`draw(2) - draw(4)` instead of the result term
(`named/seg_0791_09.c:219–279`; `code/seg_0791_19.asm:137–187`).
Each B364 call clips independently, so a substitute on 32 with positive
result and a later -1 ends on 31, not 32. Literal boundary tests visit this
edge. `participant_values` returns exact possible bytes or a singleton
given the two actual bounded draws. These are draws, not fixed constants.

### Routes and other ordered writes

On the silent-result route, 000E:6970 calls D47E, B7FA, B602 and D050
in that order (`named/seg_000E_05.c:392–406`). B602 adds +1 per selected
scorer after result clipping (`named/seg_0791_09.c:96–116`).
On the watched/managed route, F1F6 saves +0xC, plays, and restores through
CB7D before pool updates (`named/seg_0791_11.c:632–649,674–700`). BA4E
gives each managed-pool word independent `draw(4)-draw(4)`
(`named/seg_0791_09.c:297–312`), before the caller's B7FA result update
(`named/seg_000E_05.c:605–640`). Overlapping pool/squad words receive both.

Restoration does **not** imply every in-match change disappears. 7CC5
clamps live signed +0xC plus delta to 1..255, and its nonzero flag writes
min(32,signed new live) to DS:9B07 (`named/seg_0791_06.c:610–625`).
The scorer call uses flag one; ordinary team-wide goal reactions use zero
(`named/seg_0791_05.c:543–545,628–643`). Therefore score and kickoff
confidence alone do not determine a watched player's saved confidence:
event order matters. `match_form` models the write given that order.

BB2F's unplayed branch applies `draw(2)-draw(4)`, never B71C
(`named/seg_0791_09.c:340–361`; router `named/seg_000E_05.c:605–612`).
This is the listing's unplayed route; a distinct abandoned-match confidence
rule is **not established** by these lines. The result updater is shared
by routed fixtures, with the explicit kind predicate above; arranging a
friendly's separate effect, injuries/cards and team morale are outside
this finding.

## Reproduction and limits

`python3 experiments/E018-q016-confidence/check_confidence.py` checks by
player word, prints the defective record's failed declared-input checks,
and reports `match: 240/240 (480 incl. run observations)`: 240 distinct
player/case comparisons, repeated once in the formal run observations.
Empty sets, a record declared defective whose declared check passes in any
case, any other check failure and a kept mismatch fail closed. The tests use
literal inputs and expected bytes. `mutation_sweep.py` (`mutations-006.log`)
shifts every numeric constant of the model and the checker by +1 and -1,
applies 19 behaviour mutants and deletes every `raise` of both files, in
place: 70/70 killed (`mutations-005.log`, before the last tests: 66/70).
Earlier logs remain under E018.

This does not claim a whole-match simulator, full watched corroboration,
an exact RNG-free prediction for bench/pool players, or an established
abandonment/friendly-arrangement rule. Those limits cannot be removed by
matching the isolated B7FA routine.
