# Restarts: awarding, placing, waiting and taking the ball

A restart changes the holder, ball position, player destinations, action states and readiness
flags. A displayed free kick can use different taker/placement mechanics depending on where
it was awarded. Players continue updating during a stoppage, even when the match clock is off.

The [26-routine ledger](../../notes/engine-study/T104/T104a-v1.json) pins the source reading;
[set_pieces.py](../../notes/engine-study/T104/set_pieces.py) reproduces supplied geometry and
state examples without engine execution. These are proposed interpretations for ES-R2. Existing
F013/F027/F028/F030 and T77 evidence is reused within its declared scope, not expanded into
new observations of genuine keys or complete matches.

## A restart is a phase transition

Most ordinary stoppage wrappers clear pending offside, check substitutions through `8062`,
select a taker and invoke `6BF1`. Their guards differ: throws, corners and the goal-kick-style
wrapper test `8326`; the ordinary free-kick and penalty wrappers have their own caller context.
Do not impose one universal mode guard merely because their names look similar.

`6BF1` installs the holder selector, advances past an unavailable selected outfielder, clears
`830C/830D`, sets play flag `8302` to one with ball timer zero, and puts all player records
in the specified state. That is a concrete example where `8302=1` is a phase gate, not a claim
that the ball is currently travelling. It computes spot `8315`, copies it into ball position
and taker destination, and sets the taker's countdown from a table byte plus ten, plus another
ten if the **current taker point** passes the attacking-zone predicate.

Raw set `CS:6BD1` requests a new snapshot for kinds 7..11. Actual snapshot/replay ordering
belongs to the [frame](match-flow.md). `6BF1` does not initialise every adjacent global or
reset `8323`; its caller and prior phase supply context. A convenient reset-all constructor
would change the original memory effects.

| Kind/state | Spot in signed world coordinates | Principal execution route |
| ---: | --- | --- |
| 7, throw | x=8*table_sign(ball_x), y=ball_y | `7069` / `6FEE`, throw to nearest selector |
| 8, goal-kick style | x=2*table_sign(ball_x), y=-33*direction | `7287` / `71E8`, wait area clear, then long ball |
| 9, corner | x=8*table_sign(ball_x), y=36*table_sign(ball_y) | `715A` / `70F6`, cross |
| 10, penalty | (0,28*direction) | `73BA` / `72F2`, run-up and event-3 shot |
| 11, ordinary free kick | Current ball point | `7621` / `74C2`, event-4 shot or pass |

Here table_sign is +1 only for a positive input; zero selects -1. Corner coordinates follow
the ball's signs rather than simply mirroring a fixed point by the taker's direction.

Kickoff uses separate state-1 placement `69BD`: home post plus `DS:0812[played_role]`, then
mirroring. The holding-side last slot and holder receive fixed overrides from `0822=(-2,-1)`
and `0820=(0,-1)`. Arrived nonholders become state zero and the holder state two in normal
mode. `6AAD` waits for the other required records, requests a snapshot, launches event six
toward mirrored `0824=(-2,0)`, sets all states to five and whistles.

At half end, `6AF7` uses exit `0642=(-8,0)`, terminal point `0644=(-9,0)` and distinct sentinel
`0640=(11,0)`. These are not interchangeable with origin `(0,0)` or with a logical unavailable
flag. Picture updates remain simulation-visible as the [movement chapter](movement.md) explains.

## Spot, taker and placement rules

`6D4E` uses a managed choice through `CC7B` or an automatic skill-based pick through `1FDD`.
The stored word is a player identity, resolved by `6B65` to the first squad slot 1..11; an
absent pick falls back to the side's nearest selector before `6BF1` starts placement.

| Award route | Taker policy / state | Important qualification |
| --- | --- | --- |
| Throw `6E11` | Opposite side's nearest, state 7 | It does not use a named corner/penalty/free-kick pick. |
| Corner `6E6E` | Opposite side, role 2, state 9 | Sets `830A`; explicit corners statistic via `6DEA`. |
| Penalty `6ECF` | Role 3, state 10 | Whistle/substitution check, penalty count and `8324` mode. |
| Ordinary free kick `6F3E` | Role 4 only if directed y>=18 and abs(x)<=4; otherwise nearest | The same displayed award does not always request the named free-kick taker. |
| Goal kick / own-area free kick `6F01` | Role 5, state 8 | Its flag changes text/free-kick count; the mechanics remain goal-kick style. |

`6FB6` chooses the own-area versus ordinary free-kick route. Thus an own-area free kick can
use the kicking-selected role-5 player, while a near-goal free kick can use the penalties-selected
role-4 player. The [leader/taker chapter](marking.md) gives the automatic skill selections.
`6DEA` submits text and separately increments the specified side/statistic byte; counting
visible lines alone does not replace those writes.

Other players matter. Throw state `7069` gives a nearby receiver a target using signed half
ball x, two coins and a directed rand(4) y lead; others use ordinary destination logic.
Corner state `715A` also delegates other players to that logic. Goal-kick state `7287` sends
outfielders out of the holder's area; `717F` scans the 22 records, excluding keeper slots and
holder, before permitting the next phase. A taker can wait because of another player's location.

Free-kick state `7621` can form a wall when the defending/forward-kick/spot guards hold.
The raw set selects relative squad slots **7..11**, not played-role or skill codes. Near/far
anchors and per-slot offsets determine their destinations; other defenders use ordinary
destination updates with longitudinal spacing and lateral avoidance. Reordering the eleven
can therefore change wall membership even without changing a marking rating.

## Ready, wait and execute

Throw and corner takers (`6FEE`/`70F6`) count down only when at their destination. A positive
timer decreases; an update entering with zero sets the ready flag `8323`, clears play flag
`8302`, submits the ready line and handles the marker message. A **later** ready update launches
the throw/cross and sets all records to state five. These are eligible player updates, not
fixed seconds or game minutes. The final all-state-five write can overwrite a child wrapper's
state-13 chase write; local callee effects are not always the caller's final state.

Goal-kick taker `71E8` has another sequence: reach the spot, wait for area clearance, target
the goal-line-side position and mark ready, then use `3B15`. A record reaching the wrong
intermediate point is redirected to the spot with selectors adjusted. Penalty `72F2` instead
waits for the required state-zero players, sets a directed run-up y=24 and normal/shootout
ready text, then calls event-three shot and returns everyone to state five. `73BA` supplies
mode/side/keeper-specific waiting destinations and makes arrived waiting records state zero.

Free-kick taker `74C2` requires the opposing keeper at abs(y)=37 before its ready action.
It saves played role, temporarily writes **code 1**, consumes a coin and tests `2F28`, restores
the original role, then passes or calls event-four `3C3F`. Code one is the sweeper role;
keeper is zero. The old annotation calling one a keeper is wrong. This temporary context
lowers the attacking-zone longitudinal threshold without permanently changing the player.

The event-four shot uses shooting skill for `3C3F`'s first quality gate and penalties skill
for launch duration/conditional finishing. The role is restored before those calls. A cleanup
must preserve the predicate context and restoration order rather than turning the temporary
write into a real position change or re-binding cached placement halfway through it.

## Worked paths and evidence limits

For a corner at ball `(8,39)`, chosen taker current point `(0,25)`, role five, direction +1
and supplied table byte three, setup chooses spot `(8,36)` and countdown 23. The attacking-zone
test reads the taker's **current point**; incorrectly testing the new corner spot would give
13. Walking to the spot does not decrement that timer in the corner handler. A short timer-two
example shows the four eligible updates: decrement to one, decrement to zero, ready, then cross.
Readying on the decrement-to-zero update is one call too early.

For an ordinary free kick at `(0,20)`, original role 13 fails its usual attacking-zone threshold,
but temporary role one passes. With keeper/readiness/coin conditions satisfied, the restored
player shoots event four. At y=12, role one fails while keeper code zero would pass; treating
the annotation's word keeper as code zero changes the actual decision.

The wall has a further source-derived candidate quirk. Under the defending/forward/slot
guards, spot `(0,25)` gives relative slots 7..11 targets `(2,30),(1,30),(0,30),(-1,30),(-2,30)`.
At spot `(0,26)` the far branch instead gives `(-3,-28)` through `(-3,-24)`. Instructions
`7772–779F` select the opposite sign of spot y, and the later destination stores have no extra
mirror. The port agrees. Natural free-kick reachability/frequency and complete-match effects
remain unestablished; silently normalising the sign would change original behaviour.

The script checks spot signs, snapshot kinds, kickoff tables, readiness and role thresholds,
wall-set membership and this near/far transition. Five alternate interpretations differ within the authored model; this is not an independent listing check.
These projections do not demonstrate a genuine managed taker prompt or a complete original
call-frame comparison. T77's exact/READ classifications and the genuine-key gaps on
[#400](https://github.com/diegoami/goal2-archaeology/issues/400) remain explicit. No new private
input collection or original/port probe was run here; selected corroboration requires the
T105 design and accepted ES-R2 gate.

Validation scope: legacy calculator labels called “controls” are model consistency examples,
not independently executed source/engine falsifiers. Some literal-only annotations do not
exercise a branch at all. See the [control-scope report](../../notes/engine-study/ES-R2/model-annotation-scope-v1.json);
[listing_guards.py](../../notes/engine-study/ES-R2/listing_guards.py) separately checks explicit
instructions and rejects altered-listing inputs. Neither establishes natural incidence.
