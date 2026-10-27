# Positioning: from a played role to a destination

A formation supplies the eleven players' home posts. Possession, tactical bits, state and
random draws then change the offsets used to construct destinations. Movement is a later
operation: choosing a destination does not guarantee that a player reaches it.

This chapter is a proposed explanation from the original named view and instruction listings,
checked against the port and existing F026/F028 evidence. The [source ledger](../../notes/engine-study/T101/T101a-v1.json)
pins every routine and table; [posts.py](../../notes/engine-study/T101/posts.py) reproduces the
worked arithmetic. It creates no Match and executes neither original nor port routines.
F028's historical original-code post comparisons remain their own evidence; these calculations
do not add observations of complete matches or establish how often a branch occurs.

## Posts and effective controls

Keep four things distinct:

| Quantity | Location | Meaning |
| --- | --- | --- |
| Played role | player `+6` | Chooses the base post; natural role `+7` is a separate attribute. |
| Pitch identity | pitch `+6` | Slot 1..22, used to select side/keeper and bind persistent records. |
| Home post | pitch `+9/+A` | Signed x/y in the team's own frame. |
| Destination | pitch `+7/+8` | A target coordinate after offsets and mirroring; it is not the player's current coordinate. |

As in [live-state conventions](transient-state.md), x is lateral and contributes to screen row;
y is longitudinal and contributes to screen column. Some historical annotations call them
column/row. Refer to byte offsets and the cell formula when translating those descriptions.

`0791:419C` visits each side's eleven slots and reads the post from `DS:079E + 2*played_role`.
There is no formation identifier in this operation. F028 describes formation labels and the
historical 52 starting role combinations separately; a label alone does not encode an engine
arrangement or tactical instruction.

| Played code | Base post (x,y) | Played code | Base post (x,y) |
| ---: | --- | ---: | --- |
| 0 | (0,-37) | 7 | (-5,-27) |
| 1 | (0,-36) | 8 | (5,-27) |
| 2 | (0,-35) | 9 | (0,-24) |
| 3 | (-6,-33) | 10 | (-7,-22) |
| 4 | (6,-33) | 11 | (7,-22) |
| 5 | (0,-31) | 12 | (0,-21) |
| 6 | (0,-28) | 13 | (0,-18) |

Adjacent identical posts are separated as they are assigned. If `abs(x)<=4`, the new post's x
increases by three and the previous post's x decreases by three. Otherwise the new x moves
three toward the centre and the previous **y** decreases by three. For two code-7 players,
the result is `(-5,-30),(-2,-27)`, not a symmetric lateral pair. Two code-2 players become
`(-3,-35),(3,-35)`; three become `(-3,-35),(3,-35),(0,-35)`. This is a sequential comparison
with the preceding, already adjusted post, not a general collision-resolution algorithm.

The routine initially reads a stack local before initialising the side loop. The first-slot
guard prevents that initial previous-slot value being dereferenced by the equal-post test;
do not infer an observed match defect from the decompiler's uninitialised-local appearance.

Effective tactics come through `0791:26D7`. For elements 1..4, the corresponding player's
override-enable bit (element k+4 of player `+F`) decides whether to use his own element k.
Otherwise the routine uses country `+2D` for the **bound pitch side's current country** in
`DS:9B34`; elements 5..8 are team settings. An enabled player override can explicitly be zero.
Setting a team option does not override that player's enabled personal choice.

`0791:42CB` selects a line class for depth-table indexing. A played goalkeeper gets class 4.
For everyone else it reads `[3,2,2,1]` at `DS:07BA`, indexed by
`2*(played_role>4)+flag`. For roles 1..11, flag is one only when effective element 1 is on
and this pitch slot belongs to the ball holder's side. Roles 12 and 13 always use flag one.
Thus possession plus push forward changes roles 1..4 from class 3 to 2, and roles 5..11
from class 2 to 1. Possession itself is the `2B51` comparison with the side of `DS:830B`;
the separate ball/play flag determines whether the ball is at feet or moving.

## Depth and destination updates

The depth offset is signed pitch `+C`; it is added to post y, rather than replacing it.
The three outfield classes read these exact table values:

| Situation / controls | Class 1 | Class 2 | Class 3 |
| --- | ---: | ---: | ---: |
| Attacking, ordinary line (e7=0) | 60 | 45 | 25 |
| Attacking, offside trap (e7=1) | 60 | 50 | 35 |
| Defending, half pitch / sag back (e5=0,e6=0) | 0 | 0 | 0 |
| Defending, half pitch / stand ground (0,1) | 15 | 10 | 2 |
| Defending, full pitch / sag back (1,0) | 10 | 5 | 0 |
| Defending, full pitch / stand ground (1,1) | 45 | 25 | 5 |

Attacking indices are `DS:07DB + 4*e7 + class`; defending indices are
`DS:07CB + 8*e5 + 4*e6 + class`. These are byte values and depth limits, not percentages,
metres, speed ratings or promises that the entire team will occupy that line.

`0791:474D` takes an incremental route. A record on the holding side uses `4532` to add zero
or one to depth. Roles 0..4 additionally require the ball to be ahead; if that fails they use
the defending route. Everyone else uses `4649` to subtract zero or one. The strict table
comparison is necessary but insufficient:

| Routine / class | Additional predicate for a one-cell change |
| --- | --- |
| `4532`, class 1 | Ball ahead, or e1 on, or a coin succeeds; coin drawn only if the first two fail. |
| `4532`, class 2 | Ball ahead or e1 on. |
| `4532`, class 3 | Ball more than 30 ahead or e7 on. |
| `4649`, class 1 | Player more than 15 ahead of the ball. |
| `4649`, class 2 | Player ahead of the ball. |
| `4649`, class 3 | Ball is not more than 10 ahead, or squad slot is 2, or played role is 1. |

Advancement requires `depth<limit`; retreat requires `depth>limit`. A player can stop short
of a table value when the geometry predicate fails. On the defending route, squad slot 2
also gets lateral offset `+B=-post_x`, tending to centre its destination when used.

`0791:4B64` can reset depth instead. Keeper slots go directly to their mirrored post. In its
ordinary outfield branch, a player on the holding side gets `max(20,attack_limit)`; being more
than 40 ahead of the ball replaces that by `-attack_direction`. A defending player gets the
defending table value clamped to `[0,min(2*abs(ball_y),42)]`. A class-1 full-pitch/stand-ground
limit of 45 therefore resets to only 20 when `abs(ball_y)=10`.

State 9, or state 11 with `ball_y*direction>20`, uses a separate reset: on the holding side,
roles in code-set `CS:4B44` ({1,3,4,5}) use `abs(post_y)+draw_table_byte()`; others use
`38-post_y-draw_table_byte()`. The other side uses `-38-post_y+draw_table_byte()`.
Then `4A28` chooses whether a home-derived or marking destination is installed. The
draw-table helper itself consumes randomness; do not replace these branches with an average
offset while claiming the same future random stream.

`0791:4354` constructs a home-derived destination. Normal outfield lateral jitter is
`rand(5)-3`, giving -2..2. Role 13 outside state 9 uses `rand(15)-8`, giving -7..7; in state 9
it uses the ordinary range. A played goalkeeper starts with zero jitter and consumes no
draw here. If depth is below two, subtract `trunc(post_x/2)` from the lateral offset. Add
offsets to the home post, store each byte, then `2C86` multiplies **both** coordinates by
attack direction. It performs no coordinate clamp. The retained 4354 annotation contains an
older contradictory “clamps” sentence; the listing is authoritative.

## Worked sequences and limits

Consider a defending role-7 record in state 5, direction +1, post `(-5,-27)`, depth 26,
full pitch and stand ground. Its class is 2 and retreat limit 25. Assume `57AC` reaches
`4A28`, no marking target is accepted, the normal lateral draw is 3, and the player is ahead
of the ball. These are declared local branch conditions, not a measured complete fixture.

1. `4A28` calls `4354`: jitter zero gives destination `(-5,-1)` using depth 26.
2. `57AC` then calls `474D`: the strict retreat test passes, so stored depth becomes 25.
3. At a second eligible update with the same stated conditions, the destination becomes
   `(-5,-2)` and depth stays 25. Actual motion and occupancy may prevent reaching either point.

The destination is constructed **before** that update's depth step on this route. Reversing
the order gives a different first target. Other branches can reset depth or target the ball;
this sequence must not be presented as a universal update order for every state.

A separate controlled comparison holds class 2, depth 45 and its advancement predicate
fixed. With ordinary line e7=0, depth stays 45. With e7=1, limit becomes 50 and depth becomes
46. The control named offside trap acts here through depth and an advancement predicate;
these instructions do not switch offside detection on or off. Match frequency and score impact
require the later experiment design and accepted probes.

Signed division also matters. At post `(-5,-27)`, depth zero and draw 3, centring subtracts
`trunc(-5/2)=-2`, giving offset +2 and own-frame target `(-3,-27)`. Direction -1 mirrors it
to `(3,27)`. Python floor division would give `(2,27)`, an observable one-cell error in a rewrite.
The script rejects that control, an inclusive-limit control, step-before-target order, and
symmetric separation of wide duplicate posts.

For a readable rewrite, home post, target offsets and world destination deserve separate
names. Preserve when each is recomputed, byte stores, signed truncation, random draw branches
and both-axis mirroring. Those seams make local functions easier to explain; they do not yet
justify replacing the match architecture or changing tactical behaviour.
