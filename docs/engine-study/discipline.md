# Discipline: foul decisions, sanctions and live consequences

The foul predicate, a recorded foul, a card attempt, a completed sending-off and an injury
are separate steps. Availability, loss limits, management context and later handlers can
suppress or change a consequence after a draw has selected it.

The [eleven-routine ledger](../../notes/engine-study/T104/T104b-v1.json) pins those mechanisms.
[discipline.py](../../notes/engine-study/T104/discipline.py) checks supplied status/form/cap
cases without engine execution. This proposed source explanation reuses F018/F020/F027
and port evidence; it adds no natural foul rates or original-key observations.

## Foul admission, consequences and guards

The contact/keeper readers in [scoring](scoring.md) can reach `4DA9` and its hardness/tactic
predicate. `8206` still has a further own-strip/coin bail. An admitted watched foul installs
the offending pitch slot in `830C/830D`, submits the brought-down/foul lines, stops activity
through `7E60(1)`, increments the fouls byte and invokes `7EEF`. Penalty geometry is evaluated
before card/injury dispatch, whose removal/substitution effects can change bindings. That
cached context then chooses a penalty or free-kick route.

`7EEF` explicitly reads the precomputed draw table before card handling and again afterward:

| Read / condition | Attempt |
| --- | --- |
| First value 0..3, not booked | Booking through `798D`. |
| First value 0..3, already booked | Sending-off through `7B77`. |
| First value 4..15 | A fresh main random-is-one(32) can attempt a sending-off. |
| Second table value equals one | Attempt injury of the lower-hardness player; equal hardness chooses the victim/holder. |

The callee checks still apply. A red-card attempt is not automatically a red-card event.
The second stage can attempt injury as well as a card; it may select a player who has become
unavailable, in which case the injury handler refuses it. Hardness determines this target;
there is no direct fitness or height input in this dispatch's injury-target calculation.
Those attributes can affect other choices and later recovery through separate routes.

`7A43` admits a new red/injury loss only when the side's **reds plus injuries is below three**.
An unmanaged side also needs more than eleven available players across its twenty squad words.
These conditions are an AND, not an alternative way around the three-loss cap. A booking
does not use this loss guard. The count is not simply the number of players currently drawn
on the pitch, and does not by itself prove every initial-team/lifecycle invariant.

The table reader `261A` advances `8437`, wrapping 255 to one. Setup fills 255 values 0..15
and starts the cursor from the second country's number; normal country IDs are 1..128, with
zero the dummy country record. Reading the table does not step the main seed. Other action
readers consume the same table, and the sequence repeats on wrap. The 4-of-16 and 1-of-16
value classes therefore do not establish a fixed per-foul card/injury percentage in every
match. Selection, cursor position, guards and callee effects matter.

## Status, form and injury lifetimes

| Completed action | Immediate principal writes | Additional consequence |
| --- | --- | --- |
| Yellow `798D` | Set player status element 5 (mask 0x10), increment booking statistic | Increment added time only while below five; unmanaged player gets personal go-in-hard override forced off. |
| Red `7B24` / `7B77` | Set status element 6 (0x20), clear booked element 5, increment reds | Walk off, own saved-form loss, opposite-side live-form change, management/removal follow-up. |
| Injury `7D56` | Energy becomes zero, injury statistic increments | Walk off, saved-form loss, replacement or managed notice according to context. |

Yellow has no direct form write. It can still affect commentary-linked performance and
future decisions. `1771:33CD` sets personal override-enable element eight and clears tactic
element four: the AI's booked player can avoid go in hard even if the team setting remains
on. Managed players do not receive this automatic adjustment from the booking routine.

The sending-off routine changes the offender's live form by -2 **with persistence enabled**.
It then changes each available player on the opposite pitch side by +2 **without** writing
saved form. The side selection is `2974` followed by its opposite; the historical annotation's
possession-side wording should not replace that actual side test. Positive numeric form
changes still have the [form-32 qualification](audit-arithmetic.md).

`7CC5` is the common form writer:

```text
live = clamp(signed_byte(old_live) + word_delta, 1, 255)  # word arithmetic
if persist_flag:
    saved_9B07[side,relative_slot] = byte(min(32, signed_byte(new_live)))
```

Live 16 with delta -2/persist gives live/saved `(14,14)`. An opponent's delta +2 without
persistence gives `(18,16)`. Live 31 with +2/persist gives `(33,32)`. In an edited signed-edge
case, new live 128 produces saved byte 128, not an unsigned cap of 32. The last case is not
claimed naturally reached. Do not replace signed/word semantics with a generic bounded score.

The immediate injury handler sets energy zero, which makes `3216` treat the player as
unavailable. It does not fill in a fresh injury-duration word here. Later duration, fitness,
energy and ban processing belongs to the post-match/recovery slice. AI injuries can invoke
replacement immediately; a managed injury requests notice for a played goalkeeper or when
substitutions remain. An outfielder injured after that budget is exhausted can leave without
another prompt while retaining its squad identity.

These booking/red/injury writers add one to `8321` only if its current value is below five.
That does not clamp a value already above five and is not a universal extra-time limit for
all clock writers. The [frame chapter](match-flow.md) keeps that distinction.

## Animation, offside and random sources

`7881` walks the affected record off even if ordinary availability checks would skip it.
It saves/clears activity and interaction flags, uses state 12 and exit point `0642`, directly
updates that record, redraws all 22 pictures and polls keys/audio until arrival. It then
installs off-pitch sentinel `0640`, state zero and restores the saved flags. Quick mode skips
the walking loop. No `970C` clock tick occurs inside this wrapper, so transient state 12
need not appear at a completed-tick observation.

The visual operations are not all cosmetic. `7E60` runs ten passes of holder/challenger sprite
updates and referee movement. The foul path passes referee mode one; the offside path passes
zero. Each mode-zero referee call consumes a main rand(2), so that component contributes ten
main draws for the offside whistle and zero for the mode-one foul whistle. This is a component
count, not a claimed total for all nested foul/offside processing. Sprite writes also affect
the live occupancy picture.

`82EB` turns a pending offside candidate into a restart. It sets offender `830C` from `830E`,
clears `830D`, submits offside text/marker, invokes whistle mode zero and restores the saved
ball point `8317`. The initial awarded holder becomes the other side's same-relative slot:
slots 1..11 add eleven, slots 12..22 subtract eleven. It recomputes nearest players and enters
`6FB6`; the later restart route can repick the actual taker. This path does not call the
card/injury dispatcher. Offside can contribute a free-kick count without being a contact-foul
count, and it advances a different random-call sequence.

## Worked paths and limits

Supply a booked offender, first table byte two, second byte one and equal offender/victim
hardness six. The first stage attempts a red under the shared loss guard. The second injury
choice selects the victim on the tie; its own availability and side-loss guard still decide
whether an injury completes. This can produce consequences on both teams, but the supplied
values do not establish a natural joint probability or a full re-sorting/substitution trace.

For a completed red with offender live/saved form 16 and an available opponent at 16,
`7CC5` gives the offender `(14,14)` and opponent `(18,16)`. The latter live change is distinct
from the saved value later restored. The substitution and persistence slices connect those
writes to later fixtures; this example does not count their full RNG or UI effects.

For two accumulated losses, a managed side passes the loss guard with eleven squad players
available; an unmanaged side fails at eleven and passes at twelve. At three combined losses
the guard fails even if there have been no red cards. These are literal source predicates,
not observations of team sizes after every possible lifecycle path.

For offside slot sixteen, the initial opposite-side selector is five, not twenty-seven.
The component above consumes ten referee main draws, then the saved point/nearest/restart
steps follow. This illustrates why preserving only a final free-kick label is insufficient.
The five altered-rule controls cover loss counting, AI depth, saved-form persistence/signedness
and opposite-slot mapping. Existing original-key and T77 coverage limits remain visible;
no new engine, key-collection or match run was performed.
