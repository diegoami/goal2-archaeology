# Movement, occupancy and offside lines

An update chooses an action and target, tries a one-cell cardinal step, and writes sprites
back into a pitch picture that later movement reads. That picture is part of the simulation.
Removing drawing-looking operations can alter collisions and random consumption.

The [source ledger](../../notes/engine-study/T101/T101c-v1.json) covers ten scoped routines,
the internal move-test helper and the disposition of all 28 positioning/motion/pilot registry
entries. [movement.py](../../notes/engine-study/T101/movement.py) checks source-derived arithmetic
and supplied-draw examples without executing an engine routine. Interpretations remain proposed
pending ES-R2. Existing F013/E032 and port proof records are historical evidence, not new
observations made by these examples.

## Targets become steps

`0791:8AE9` dispatches the current pitch `+12` state, then calls `8889` for movement:

| State | Handler / purpose |
| ---: | --- |
| 5 | `57AC`, normal play decisions |
| 13 | `58E1`, chase countdown |
| 1, 2 | `69BD`, `6AAD`, kickoff placement / taken |
| 3 | `6AF7`, walk off |
| 6 | `6240`, restart/kickoff state |
| 7, 8, 9 | `7069`, `7287`, `715A`, throw-in / goal-kick / corner |
| 10, 11 | `73BA`, `7621`, penalty / free kick |
| Other values | No handler in this dispatch; the movement call still follows. |

Handler details belong to the ball, tactics and lifecycle chapters. The order matters: a
handler can replace a target, take an action or change state before this call's movement.
The following activity increment, possession check, sprite update and energy expenditure
also belong to the same `8AE9` call.

`0791:4D3F` starts a state-13 delay for an outfielder, or a keeper whose current point passes
its own-goal-strip test. It sets destination equal to the current point and stores
`draw_table_byte()+4`, plus ten for a keeper, in the state timer. `58E1` normally decrements
a nonzero timer; it switches to state 5 when an update **enters with zero**. Starting at four
therefore leaves state 13 after countdown values 3,2,1,0 and switches on the next update.
A keeper with the ball/play flag set but ball timer zero has an earlier state-5 branch.
This is not a universal duration measured in game minutes.

`0791:8889` first may restrict a destination against the opposing line marker. The restriction
is skipped when a moving ball is ahead of the player, for the current holder/challenger, or
when the target has the wrong longitudinal sign. Otherwise the target must reach or exceed
the opposing line's absolute y, the state must be in `{5,7,8,11}`, and this must not be a keeper
slot. It stores `opposing_line_y-attack_direction` in target y. Equality reaches the restriction:
the listing's `8972 jl` skips only a strictly smaller absolute target. Do not infer the branch
from decompiler condition flags retained across the subsequent set-membership call.

Those skips only bypass the restriction; they still reach the target test and movement.
If current and destination packed words match, direction becomes five (stand still), without
an axis coin. Otherwise one coin chooses which differing axis to prefer; if that axis is
already aligned, the other is used. Direction values are:

| Value | Attempt |
| ---: | --- |
| 1, 2 | Decrease / increase signed x by one |
| 3, 4 | Decrease / increase signed y by one |
| 5 | Stay at the drawn position |

The internal `0791:86D0` starts **each attempt** by copying old/drawn position `+2` back to
current `+0`, then applies the selected step. A rejected attempt does not become the starting
point for the next one. Every failure consumes `rand(5)` for another direction and retries;
five provides a standstill escape. The accepted direction can therefore lead away from the
destination. This is not diagonal movement or a shortest-path algorithm.

The [player dictionary](player-fields.md) contains no standalone pace byte, and the twelve
derived skills include control, not a separate speed skill. This movement helper does not
scale one-cell distance by ability or fitness. Attributes still affect upstream action,
reaction and target choices. Movement frequency depends on which updates the sweep performs;
the [frame chapter](match-flow.md) explains extra keeper/ball-phase updates. Do not convert
one helper call into a fixed physical speed or one frame of real time.

Activity `+14` increases when the final unsigned direction is below five. With live activity
`DS:8325` on and activity **greater than 180**, signed energy above one drops by one, and the
counter resets even when energy cannot drop. From activity 179, one running update gives
180 with no expenditure; from 180 it gives 181 then resets to zero and spends energy.
Direction five does not add activity, and a stopped clock postpones this expenditure check.
Other energy writers and long-term fitness/recovery remain separate mechanisms.

## The picture is occupancy

For signed coordinate bytes (x,y), the cell word is at:

```text
picture_base + 0x90E + x*160 + y*2
```

The character is the low byte and colour/attribute the high byte. For directions 1..4,
`86D0` first requires `abs(x)<=8` and `abs(y)<=37` (`2DCA`). During live play, an ordinary
outfielder who is neither holder nor challenger then reads the live picture `DS:7C16`:
attribute 0x0D permits the step; otherwise a character in the 256-bit set at `DS:0648` blocks
it. These occupancy checks are bypassed while activity is stopped, for the holder/challenger,
or for played role zero. Those exemptions do not bypass the preceding coordinate bounds.
Direction five returns successfully without either check.

The complete blocking character list is in the ledger. It includes player-looking characters
1/2, marker-looking 16/17, dollar/digit/letter codes and two extended codes. Character 1 at
attribute 7 blocks an ordinary step, while the same character at attribute 13 permits it.
Thus a grid storing only “occupied or free” loses a real branch.

`0791:8537` restores a moved player's old cell from the background pointer `DS:7C1E`, except
for unchanged or sentinel positions, updates old=current, and draws the player at the new cell.
A held player glyph can differ from its ordinary glyph. When that player holds a stationary
ball, the routine also installs the ball coordinate, offsets ball y using the run direction
outside the keeper exception, applies its two endpoint adjustments, and draws the ball.
The ball and drawing calls can overwrite cells that later players inspect.

`0791:8E24`, used for lines/markers/referee, has a different restoration rule: it restores
the old cell only if the **full glyph word** still equals that sprite's glyph. If another
sprite has overwritten it, restoration would erase that later occupant. It then stores
old=current and writes the new glyph. A modern renderer may be separated eventually, but a
faithful rewrite must first preserve the simulation-visible buffer and update order.

## Offside, referee and worked boundaries

`8C67` resets each line sprite to x=`8*direction`, y=0 with old=current. `8CCA` calls it for
side 1 then side 0 and initialises referee current/old/target to `(1,0)`.

`0791:8CF5` computes each side's longitudinal line from its ten outfield slots, with no
availability filter in this loop:

```text
minimum = min(0, y[slot2]*direction, ..., y[slot11]*direction)
line_y = byte(minimum * direction)
```

The zero initializer matters: if all directed values are positive, the line stays zero.
Values `[-8,-2,10]` in direction +1 produce -8. This is a deepest-outfield-coordinate rule,
not a player-slot number or the modern second-last-defender definition. Drawing the line
uses `8E24`. Matching signs between nonzero line y and ball y, plus pending-message flag
`8328`, can also place a marker through `90C5` using `8304/8308`. The geometry/restriction
is distinct from offside adjudication and the later restart consequence.

`90C5` stores marker glyph/x and offsets y by the direction-table entry selected by whether
the glyph equals 0x0EAE. It skips drawing for a quick result, but still writes marker state.
These operations have no RNG in this line/marker path; the player movement using the line can
consume a different number of draws after its target changes.

The ordinary `0791:9119` referee update consumes exactly one `rand(2)` before checking whether
it needs to move. For positive ball y it targets `min(ball_y+1,30+draw)`; otherwise
`max(ball_y-1,-30-draw)`. Target x is `clamp(trunc(target_y/4)+1,-5,5)`. It can step each
axis by one, then rolls back to the old coordinate if the **background** character is in
the blocker set, and redraws through `8E24`. A nonzero mode uses a separate ball-relative
target and stepping branch; it must not be replaced by the ordinary mode's algorithm.
Even an unmoved referee changes the future main random stream on the normal watched call.

A blocked-step example supplies a current/drawn point `(0,0)`, target `(1,0)`, axis coin one
and an ordinary live outfielder. Direction two tries `(1,0)`, but character 1/attribute 7
rejects it. Supplied retry draw four resets from `(0,0)` and tries `(0,1)`, whose space/attribute
7 is accepted. The final direction is four and the path consumed two main draws (coin and
retry). Ignoring the picture accepts `(1,0)` and consumes only the coin. These are declared
draws/cell contents, not an executed seeded fixture or a claim about ordinary collision rates.

Other checks distinguish the y=37 boundary from y=38, attribute/exemption branches, energy
thresholds, zero-initialised lines and referee signed division. Ball y=-1 with draw one gives
referee target `(1,-2)`; Python floor division would give target x=0. A glyph-restoration
control demonstrates why unconditional erasure is wrong.

The T95 registry frontier is fully assigned: T101a/b/c explain 25 entries across positioning,
motion and pilot; `835F` ball travel, `83A2` ball step and `869F` possession belong to T102.
Internal `86D0` and geometry helpers are cited explicitly rather than treated as extra registry
entries. This is source coverage, not dynamic coverage or a claim that every state combination
has been observed. Separate structures for target choice, attempted step, accepted position
and simulation-visible cells would improve readability while retaining those boundaries.
