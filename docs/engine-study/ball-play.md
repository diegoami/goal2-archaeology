# Ball actions: aim, skill, duration and flight

The engine approximates a launch with a small integer velocity and a remaining timer. A target
point helps choose those values; it is not a promise that the ball will arrive there. Skill can
change an accuracy gate, remaining duration or a reach bound. Boundary handling, interceptions
and keeper contests then decide what actually happens.

This proposed source explanation covers sixteen routines in the
[source/calculation ledger](../../notes/engine-study/T102/T102b-v1.json).
[flight.py](../../notes/engine-study/T102/flight.py) reproduces supplied arithmetic cases without
executing an engine. A bounded [Sol/xhigh assistance record](../../notes/engine-study/T102/launch-helper-v1.md)
checks the difficult `34C1` arithmetic; it is implementation assistance, not independent review.
The main session re-read the original long-division instructions before integrating it. ES-R2
reviews the whole interpretation separately.

## Aiming, event and skill are separate

The launch event selects a context-specific skill through `DS:0779+event`:

| Event | Table skill | Use in the launch path |
| ---: | --- | --- |
| 1 | shooting 11 | Shot-duration branch, with an extra cached-byte term. |
| 2 | heading 4 | Header-duration branch, with the same explicit extra term. |
| 3, 4 | penalties 12 | Different duration branch, without that second extra term. |
| 5 | crossing 7 | Conditional launch accuracy/miscue gate. |
| 6, 7 | passing 6 | Conditional launch accuracy/miscue gate. |
| 8 | keeping 1 | The normal event-8 launch bypasses that accuracy gate; a table entry alone is not a skill read. |
| 9, 10 | kicking 2 | Conditional accuracy/miscue gate. |
| 11 | heading 4 | Conditional accuracy/miscue gate. |

These are original event identifiers, not an exhaustive set of English football actions.
In particular an input mode to a wrapper need not be its emitted event:

| Routine / input | Reach before launch | Emitted event |
| --- | --- | ---: |
| `3B15` | max(30,rand(kicking/4)) added along attack direction | 10 |
| `3EF8`, input mode 9 | max(30,rand(kicking/4)) | 10 |
| `3EF8`, other mode (such as 11) | max(20,rand(heading/6)) | 11 |

The draw still occurs when the floor makes reach constant. For kicking 100, its bound is 25,
so every possible draw gives reach 30. That does not make kicking irrelevant: another gate
can read it later, and a higher value can eventually exceed the floor.

`3FAD` chooses a sign-based random clearance point. Its wide branch (coin or keeper) uses
x=±12 and y=±rand(40); its narrow branch uses x=±(rand(8)+2), y=±50. Signs come from the
player's current coordinates, with zero selecting the negative table entry. Those points can
lie beyond the pitch. `408E` chooses this random-target route or `3EF8`, passing mode 11.
`4151` tests the holder's own-goal strip and can call `3FAD` with mode 9; despite its historical
keeper name, that body contains no keeper-slot test of its own.

Geometry also opens shot choices. `40BC` requires the holder outside its own half, beyond the
opposing marker, with abs(y)<35 and abs(x)<4. This gate is separate from the skill formula.
The [possession chapter](possession.md) explains how the holder reaches these action routines.

## Launch vector and duration

`0791:34C1` sets the kicker's run direction to five, enables moving-ball state `8302` and
records the kicker in `830B`. It subtracts ball coordinates from target coordinates **as bytes**,
then interprets each difference as signed. Define A=abs(dx), B=abs(dy), and `step(z)=+1` when
z>0, otherwise -1. Zero therefore selects -1.

| Geometry | Velocity / base timer |
| --- | --- |
| A>B | vx=step(dx), T=A. If B>=A//2, also vy=step(dy), T+=B. |
| A<=B | vy=step(dy), T=B. If A>0 and A>=B//2, also vx=step(dx), T+=A and vy doubles. |

These comparisons use the quotient after integer division. Consequently dx=1,dy=0 satisfies
the x-dominant secondary threshold because `1//2=0`; it gets velocity `(1,-1)`. Zero displacement
takes the y-dominant branch and gets `(0,-1)` with base timer zero. Neither should be replaced
with an invented idle return in a faithful rewrite. Their natural reachability/frequency is
not established by these isolated calculations.

For input event 6, base timer above 20 rewrites it to event 7. Otherwise a keeper in its own
goal strip can get event 8. That area test uses the **ball's current point**, not the target.
The event is stored, then skill or accuracy modifies the timer/vector:

```text
events 1/2: T = max(U16(T+5), U16(effective_skill + cached_extra_byte)//3)
events 3/4: T = max(U16(T+5), effective_skill//3)
other events: possible accuracy/miscue branch

final_timer = max(2, T // (abs(vx)+abs(vy)))
projected_point = byte(ball_point + velocity * final_timer)
```

The final division is signed-long division with zero-extended timer and the sign-extended
velocity sum; with the shipped ±1 sign table and generated velocities, the divisor is positive.
It can be **one, two or three**. The decompiler's apparent division-by-two argument list hides
the actual register operands. `37CE–37E7` builds the sum, `37E9–37EE` supplies timer to
`23E4:0294`, and `37F5` applies the minimum. This is not universal timer halving.

The explicit cached extra in events 1/2 is additional to whatever `278A` already included in
effective skill. Thus manager/captain context can enter both terms. Events 3/4 do not add that
second copy. The [contest chapter](contest-formulas.md) describes these local formulas;
the final velocity-sum division and subsequent play still matter.

The accuracy branch runs only outside events 1..4, for full-word event other than 8, timer>1,
and different kicker/receiver selectors. `287C` uses the event's effective skill and quantised
bound `V//32+1`. On failure it clears `830C` first. A keeper stops there; a nonkeeper consumes
a coin even if control byte `8323` already selects shortening. It then either subtracts a
draw from the timer or perturbs velocity, with further conditional draws. Finally `8323`
is cleared, endpoint `8313` is projected, offside preparation runs and `830D` copies `830C`.

A failed accuracy gate can therefore remove the receiver and change the path, rather than
simply label a pass unsuccessful. Branches consume different random draws. A rewrite that
substitutes one success percentage loses state and future randomness.

## Shot and flight bookkeeping

`3EC5` wraps common `3C3F` with event 1 and its supplied commentary template; `3EDF` uses
event 2 and template 0x14. The shared routine has several distinct effects:

- Nonheader events consume two coins and alter ball x by their difference (-1,0,+1).
- Outside `8324` mode, a shooting/header gate, then a one-in-four fallback, then `29B3` can
  set byte `80FB`. Later readers interpret this flag; it is not an immediate score increment.
  Its decompiled alias as pitch-record-zero placement is misleading: this address is a global.
  This first gate uses shooting 11 for nonheader events and heading 4 for event 2; events 3/4
  use penalties 12 later in launch duration, rather than at this first gate.
- It mirrors goal target `DS:0646=(0,38)`, launches, submits commentary and increments the
  side's statistic byte at `7B7E+10*side+3` when `8326` is clear.
- Heading event 2 sets flight `8303` with no final tail draw. Every other event first draws a
  coin; only event 4 can use a true result to skip `rand(3)`. Events 1/3 discard that coin's
  result but still consume it before the one-in-three flight test.

Submitting commentary and incrementing a direct counter are separate operations. A deduplicated
line need not cancel that later counter write. `3C20` separately increments statistic +4 under
the same `8326` guard when its caller reaches it. Counting shot-looking text as all attempts,
on-target outcomes or goals would confuse these mechanisms. The resolution slice traces
their later callers and scoreboard consequences.

`835F` computes the low word of `(abs(word_vx)+abs(word_vy))*remaining_timer`. It measures
remaining travel used by other branches, not a standalone physical speed or height attribute.
`83A2` computes a candidate using the **low velocity bytes**, decrements a nonzero timer,
then keeps an existing air flag only while the new remaining travel is at least three.
It accepts a candidate inside the wider rectangle abs(x)<=9,abs(y)<=39, draws the ball, and
tests the actual point against playing bounds abs(x)<=8,abs(y)<=37.

Crossing the playing bounds invokes offside/restart/finish logic. Without an earlier offside
return it clears selectors/activity, then uses mouth width, longitudinal boundary and holder
direction to choose `698E`, `690C`, throw-in, corner or goal-kick/free-kick routing. In particular
the centre/forward route to `690C` is not an automatic goal or a penalty award inferred from
that routine's historical name. It still needs the later resolution. The timer/event cleanup
and nested calls are part of that state transition.

`83A2` itself does not have an entry “timer zero means do nothing” guard; normal calling
conditions belong to the [sweep](match-flow.md). `869F` installs possession by writing `830B`
and clearing timer, `830C/830D`, `8302/8303` and event `8327`. Some callers restore a previous
flag afterward, as `8AE9` does for `8303`, so the wrapper's resulting state must be traced too.

Woodwork uses another route. `59B3` considers an active-mode, nonkeeper moving ball at
abs(y)=37,abs(x)<2. `593B` consumes its chance before the event/template guards; on a bounce
it negates both velocity words and sets timer to `max(1,T//4)`, submits commentary and clears
`8324`. It quarters remaining duration, not the velocity magnitudes. When neither active flag
is set, `59B3` returns an unwritten local byte; a clean-looking unconditional false return
would need a compatibility argument, not a guess.

## Worked boundaries and limitations

For target `(7,14)` from `(0,0)`, the base vector is `(1,2)` and timer 21. Event 6 becomes 7.
With the accuracy branch bypassed by equal selectors, divisor three gives timer seven and
projected `(7,14)`. Universal halving gives timer ten and `(10,20)`, which the control rejects.
For event 3 at target `(4,8)` with supplied effective value 90, the base timer 12 becomes
`max(17,90//3)=30`, then divides by three to ten; adding the cache again would give a different
result. These supplied values/selectors are arithmetic cases, not observed full fixtures.

A shot from `(0,20)` toward `(0,38)` has vector `(0,1)` and base timer 18. With supplied
effective shooting 98 and cached extra 56, adjusted timer is `max(23,154//3)=51`. Divisor one
leaves 51 and projects `(0,71)`. The projection does not mean the ball will reach y=71:
boundaries and contests intervene. One unobstructed step gives `(0,21)`, timer 50 and remaining
travel 50. These are potential inputs to later reactions/keeper difficulty, not a goal prediction.

At point `(0,37)`, velocity `(0,1)`, timer one and existing air=true, the next candidate
`(0,38)` is inside wide bounds. Timer becomes zero, air clears, and playing bounds trigger
resolution. With no pending offside and forward holder direction this reaches `690C`; the
example stops at that dispatch. A zero-displacement launch instead projects `(0,-2)` under
its minimum timer, demonstrating why a semantic idle shortcut is not equivalent.

For an ordinary shot's final tail entered at main seed zero, the source consumes coin then
rand(3). Removing the apparently unused coin can leave the same air flag, but the next common
rand(100) becomes **24 instead of 97**. This is a tail-only source calculation, not a seeded
match experiment. The script also rejects the universal-halving, extra-on-penalty, zero-vector
idle and pre-countdown-air interpretations.

The calculations do not model a complete original call frame, every miscue outcome, natural
reachability or match frequencies. Word velocities versus byte stepping, byte projections,
event rewrites, multiple cache uses, pending flags and exact draw order are explicit rewrite
boundaries. Independent review and later selected probes must preserve those distinctions.
