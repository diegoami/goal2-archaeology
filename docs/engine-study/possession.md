# Possession: who considers the ball, and what the holder chooses

A pass involves several decisions: who is eligible, which teammate is preferred, whether the
holder acts now, where the ball is aimed, whether the launch miscues, and who reaches it later.
A single passing rating or a single “pass success” roll cannot describe that pipeline.

This proposed source explanation covers sixteen routines in the
[ledger](../../notes/engine-study/T102/T102a-v2.json). The
[worked calculations](../../notes/engine-study/T102/receivers.py) use supplied branch inputs
and draws; they execute no engine routine or complete fixture. Original named sources were
read alongside instruction listings and the port. Existing F022/F026 observations retain
their own scope; none of the examples adds a natural-frequency estimate.

## Who is considered

`DS:830B` identifies the current holder/kicker slot. While the ball is moving it can still
name the previous kicker, so that byte alone does not establish possession at feet.
`2C29` additionally requires the ball/play flag `8302` to be clear. `830C` is a selected
receiver/challenger selector whose meaning depends on phase, not another player record.

`0791:2FB1` scans outfield slots 2..11 of each side, excluding unavailable players, the holder
and state-13 records. It stores the nearest by Manhattan distance in `8311[side]` and the
nearest strictly goal-side of the ball in `830F[side]`. The two minima start at 100 and replace
only on a smaller distance, so the first equal candidate wins. These selectors feed later
chasing/reaction branches; they do not directly award possession or include the keeper.
`30EA` supplies the side-base mapping for relative squad-slot loops.

`0791:3111` chooses a pass receiver. Its long mode is enabled by effective tactic element 3,
or by being in the player's own half while not a keeper. Thus turning that tactic off does
not guarantee short mode everywhere. The initial cutoff is `2+table_byte` for short mode,
`24+table_byte` for long mode.

The first pass visits teammates from squad slot 11 down to 2. A candidate must be available,
not the passer, not in state 13, and not more than ten cells behind the ball according to
`2D10(candidate,10)`. It then compares Manhattan distance from the passer:

| Mode | Distance condition | Effect of accepting a candidate |
| --- | --- | --- |
| Short | distance <= current cutoff | Replace cutoff by that distance, so later candidates must be at least as close. |
| Long | distance > current cutoff | Replace cutoff by that distance, so later candidates must be farther away. |

The first accepted candidate needs no coin. A later distance-qualified replacement needs
a successful coin, so the chosen receiver is not necessarily the closest/farthest eligible
player. If nobody is accepted, an ascending fallback over slots 2..11 returns the **last**
available non-passer. That fallback does not retain the distance, state-13 or ahead-of-ball
filters. Long mode is therefore a preference, not an absolute distance guarantee.

Cross selection is different. `0791:3D38` scans the holding side's outfielders upward and
returns the first available non-passer in the opposing goal strip whose played role belongs
to the raw `CS:3D18` set: **codes 2 and 12**. It does not choose by nearest distance, directly
read height, or accept every forward role. Availability, position conversion and geometry
can therefore affect crossing targets indirectly. The set-membership branch must be read
from the listing; decompiler flags around it are misleading.

## Holder choices and two random sources

State-5 updater `57AC` tries its branches in order: offside action, holder-at-feet opportunity
(`5049`), selected receiver destination (`533B`), challenge/duel, then other ball/marking target
decisions and depth stepping. An earlier accepted branch suppresses the later decisions.
The special keeper-holder route can replace ordinary target updates with `4B64`.
The pending-offside notification `56D9` itself always returns low-byte zero; it does not end
that chain. [Resolution](scoring.md) distinguishes notification from adjudication.

Two sources of variation need separate accounting:

| Reader | State consumed now | Consequence of an extra call |
| --- | --- | --- |
| `261A` draw-table byte | Next of 255 precomputed bytes, value 0..15; `8437` wraps 255 to 1. | Changes the later table position, including foul/action decisions using that table. It does **not** advance the main seed at this call. |
| `06B1` / coin / random-is-one | Shared main LCG word, with the actual call's bound. | Changes subsequent main draws; conditional calls need their original order. |

Setup fills the table using main draws, but reading it later is not another main draw.
Pairing matches only by initial main seed cannot remove divergence in either consumer sequence.

`0791:5049` first requires the holder at feet and updates depth/target. A keeper heads toward
its throw position and can use `3BEE` once at the longitudinal throw boundary. An outfielder
gets geometry/state-dependent shot, header and deep-clearance opportunities before the
ordinary pass/dribble branch. The opposite keeper being in state 13 (`500C`) can affect
those choices. The goalkeeper's state matters as well as its keeping skill.

Outside those earlier branches, `5049` calls `4E28` when effective element 2 and a coin permit
it, or on `random_is_one(trunc(signed_energy/2))`. In that isolated fallback, lower positive
energy gives a smaller bound: energy 8 asks for draw one out of four, while energy 32 asks
for one out of sixteen. This is a local action-opportunity rule, not evidence that tired
players are better overall. Energy simultaneously changes effective skills and other gates,
and the conditional entry seeds need not be uniformly distributed.

`0791:4E28` then chooses among crossing, passing and self-directed dribbling:

| Earlier condition / played role | Choice after reaching this stage |
| --- | --- |
| Directed y > 24+first table byte, abs(x)>3 | Cross immediately; no second table read. Equality does not qualify. |
| Directed y < -8 | Pass; the second table read is skipped. |
| Otherwise second table byte is one | Pass. |
| Roles 3/4 | Push-forward element 1 on: dribble; off: pass. |
| Roles 7/8 | Push forward can dribble, with a random-is-one(3) exception that passes. |
| Roles 10/11 | Dribble after the earlier conditions fail. |
| Roles 12/13 | Pass on random-is-one(3/4) respectively; otherwise dribble. |
| Other roles | Pass. |

Thus the same push-forward control affects both positional depth and ball choice. An extra
cross/forced-pass branch can also change which table/main draws occur, before any accuracy roll.

## From selection to a pass

`3323` forwards `3111`'s full returned AX word into `384C`. The decompiler's char declaration
is not permission to discard ABI bits or frame effects in the faithful port. The worked
receiver model concerns ordinary slot values, not a proof of arbitrary return-register states.

`0791:384C` first routes an existing pending offside (`830E`) to `82EB`. Otherwise it reads
the selected slot's point. A self-target becomes a forward dribble point and clears the
flight flag initially; a teammate outside its own goal strip can receive a small directed
lead when abs(y)<25. The receiver gets state 5 and `830C` names it. `34C1` launches event 6,
or event 11 under `80FA`. The later launch reader uses the event's skill table; ordinary
passing element 6 affects that accuracy/miscue gate, not `3111`'s receiver-distance scan.

After launching, `384C` handles its self-dribble perturbation, projected endpoint `8313`,
travel-dependent flight flag and commentary branches. A self-dribble perturbation is
conditional on longitudinal velocity and random-is-one(3), and can read dribbling skill 10.
The final receiver/flight/commentary state can differ from the initially intended pass.
The ordinary pass routine does not itself call the chase initializer; the alternate wrappers
below do. The v2 ledger corrects that attribution in its preliminary v1 description.
The [launch chapter](ball-play.md) explains those velocities, timers and accuracy branches.

`3B9E` is another wrapper: it selects a launch event from the passer's half, submits template
3, sets flight from a coin and starts a chase delay. `3BEE` chooses a selected pass or long
ball by coin, except that pending offside bypasses that coin. `3DF6` uses the cross target
or draws a fallback point, temporarily sets `830C=0xFF`, launches crossing event 5, submits
commentary, clears `830C`, sets flight using random-is-one(8), then begins chase. A cross
does not retain a normal selected-receiver slot after that tail.

`333F`, nested under launch, prepares offside state rather than immediately blowing a whistle.
If activity was stopped it enables it and returns without the candidate scan. Otherwise it
scans the first eleven, excluding the kicker and `830A`, for a teammate beyond the opposite
line with the proper sign and timer zero; the first qualifying candidate is recorded in
`830E`, with point `8317` and `8329` cleared. This scan does not use the pass selection's
availability test. Adjudication and restart effects belong to the
[resolution chapter](scoring.md), not to a distance preference alone.

`533B` also explains why a receiver need not chase the current ball: for a selected nonkeeper
with ball timer at least ten it targets projected endpoint `8313`; a keeper or shorter timer
uses the ball's current point. State-13 countdown `58E1` instead holds its own point until the
delay ends, as the [movement chapter](movement.md) details.

## Worked decisions and rewrite boundaries

For a short receiver decision, supply cutoff-table byte three, giving cutoff five, with three
first-pass-eligible candidates in descending slots: 11 at distance four, 10 at three, 9 at two.
Slot 11 is accepted without a coin. Supplied replacement coin zero keeps 11 over 10; coin one
then accepts 9 and makes the cutoff two. That selection used one table read and two main coins.
Under long mode the same list fails initial cutoff 27, and fallback returns slot 11 at distance
four with no replacement coins. A label saying long passes cannot promise a long result.

A conditional possession sequence takes a state-5 holder at feet in slot 6, role 7, point
`(0,0)`, with effective elements e1=0/e2=1/e3=0. Assume the earlier offside/shot/clearance
contexts do not intervene, the e2 coin admits action, and the two `4E28` table values avoid
crossing/forced-pass. Role 7 with e1 off chooses `3323`, and the supplied short scan above
selects slot 9. `384C` installs receiver state 5 and `830C=9`, then invokes event-6 launch
when `80FA=0`. With the launch gate passing, no pending offside and travel below eleven,
the ordinary ground tail submits commentary template 8. Selection itself changes no score.
Commentary can be deduplicated; later interception, flight and scoring remain separate steps.

This is a source-conditioned sequence with stated draws, not an executed complete legal
fixture. It does not claim exact velocities, total full-call draw counts, reachability or
passing success frequency. The script rejects always replacing a receiver, drawing a coin
for the first acceptance, an inclusive long-distance comparison, taking the first fallback,
and treating the advanced-cross threshold as inclusive.

A readable design can separate eligible candidates, receiver preference, holder action,
launch request and receive target. Preserve traversal order, fallback filters, conditional
draw/table consumption, selected-slot/identity distinctions and delayed offside state.
Changing those while keeping the same labels would change play.
