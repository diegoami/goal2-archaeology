# Extra time, shootouts and taker decisions

Extra time reuses the match-half machinery. A shootout reuses watched placement, shot and
keeper mechanics while repurposing some clock bytes and suppressing selected normal statistics.
Its order, working tally and fixture result are separate representations.

The [ten-routine ledger](../../notes/engine-study/T104/T104d-v2.json) and
[bookkeeping calculations](../../notes/engine-study/T104/shootouts.py) contain source-derived
examples only. No kicks, UI keys, original/port routines or full matches were executed here.
These interpretations remain proposed pending ES-R2; F015/F023/F030 and T76/T77 coverage
retain their actual evidence levels.

## Extra time and overloaded clock state

`F098` first writes the played goal bytes/result into the fixture. With decider flag `7C36`
and a draw, it invokes `9B0C` and `9B5B`, stores the extra-time result again, and calls `A10A`
if still level. The full 32-byte set at `DS:693A` is **{4,8..203}**, not the literal value
0x10 or element sixteen. F023 already corrected the older first-byte interpretation.
The calendar builders' naturally emitted deciders are kinds 8,101..103,200..203; membership
of an unused kind does not establish that the normal calendar produces it. A friendly kind
one is outside the set.

The first extra-time wrapper installs remaining count 31, elapsed 89, half threshold 15,
subtick zero and end flag zero. It grants the selection interaction latch and can open the
managed menu, chooses the kickoff selector, then runs `983F`. The second wrapper grants
interaction, chooses the other kickoff selector and reuses that half machinery. These
wrappers do not replenish the substitution allowance. The [clock ordering](match-flow.md)
explains why 31/89 are entry values rather than a literal 31-minute extra period: the first
eligible advance gives 30/90. Replacing 31 by 30 changes the actual boundary.

During a shootout kick, `A006` writes byte `8319=-side`. At remaining zero, the existing
signed `2BE5` rule makes both current kicking sides face negative y, with the other keeper
facing the opposite way. The normal half-threshold field is being used as a direction control;
0xFF does not mean a 255-minute half. Word `831D` is likewise the shootout round display
counter, not the ordinary subtick countdown. No normal clock tick is run by the kick's
`9564` sweep loops.

## Ordering, eligibility and one kick

The managed order reader `9B93` requires an order of **all available first-eleven players**,
not only five. It rejects duplicate/unavailable choices, appends on Enter and removes the
last choice on Esc. It finishes when the selected count reaches the available count. Keeper
slots are allowed. An incomplete order cannot be treated as a cancelled shootout.

The automatic order `9ED3` starts with all eleven pitch slots, including the keeper, and
pairwise sorts them by effective penalties element 12. It does not filter availability in
that sorting function. Equal comparisons do not imply a stable sort, as with the
[substitution sort](substitutions.md). A keeper can lead the supplied ranking; an outfield-only
rewrite changes it. Penalties skill has its [special energy term](attribute-formulas.md),
so unavailable status/energy is not equivalent to a zero ranking value.

That does **not** mean an unavailable entry necessarily takes a kick. `A006` first passes
the current ordered entry to `6BF1`, whose `2A15` advances past an unavailable outfielder.
It then advances the order cursor, wrapping 1..11 and probing availability for the **next**
ordered entry. Current fallback and next-order skipping happen at different times.

A source example makes the distinction: automatic order starts `[11,5,2,...]`, slot eleven
is unavailable and slot two available. The current setup wraps the initial eleven to two;
the next cursor names five. Filtering the order before starting would choose five first,
which is a different original behaviour. Natural incidence and complete-match consequences
of this case remain unestablished here.

There is a further boundary to audit: managed orders can have fewer than eleven entries,
but the next cursor still wraps at eleven. The first probe after an eight-entry list is a
zero-filled entry. Whether the dummy pitch-record availability/context safely rejects it,
and which normal paths reach that state, is not established by this projection. Do not
silently assume either an invalid kicker or correct wrap-at-length behaviour.

For each kick, `A006` establishes penalty state ten, prepares mode `8324`, stops activity,
then repeatedly sweeps `9564` until that mode clears. It sets player states zero and sweeps
until the ball timer settles. The state-ten handler includes spot/wait/run-up/return-to-spot
steps before event-three shooting; the [restart chapter](restarts.md) describes them.
It is a ball simulation, not a single independent penalty-success coin.

## Round stopping and score representations

`A10A` temporarily raises the match delay byte to at least2 (slowing play), forces watched play even after a quick route, fills orders,
initialises five remaining kicks per side and starts with side `831A`. It stops when one
working score exceeds the other's score plus remaining kicks. When the starting side has
used its five, the other side's counter is set to one for its equalising opportunity; this
mechanism also supports successive sudden-death pairs. After the second side's kick the
round counter increments before the next stop test. It restores the saved delay byte and
the quick flag from `9A3F` on return.

With supplied outcomes make/miss repeated, three-nil can terminate after six kicks rather
than forcing ten. With ten supplied misses and tied initial working score `(2,2)`, the first
sudden-death make gives `(3,2)` but does **not** terminate: the other side still gets its kick.
A subsequent miss ends after twelve kicks. The last displayed round was six; the incremented
next-round counter is seven. These are bookkeeping projections, not twelve executed kicks.

The working tally starts from the tied score already in `9B3C`; the equal base does not change
the stopping comparisons. At the `F098` boundary after the shootout, the caller updates the
fixture **result byte** from that working comparison, without copying the penalty-increased
working tally into the already stored goal bytes. In the example, stored fixture goals can
remain `(2,2)` with result zero, while the working tally is `(3,2)`. Later consumers must choose
the correct representation, not infer a draw solely from tied goal bytes.

Mode `8326` skips normal `6443` scorer/player-goal recording and selected shot/save counters,
as described in [scoring](scoring.md). Commentary still reaches `1EB5`/`1E53`, whose rating
delta precedes ring deduplication and has no shootout exclusion there. A named goal line
therefore can add the table's +40 performance delta while the ordinary player-goals word
does not increment. The subsequent man-of-match scan occurs after play; player statistics,
performance and outcome are different consumers.

## Prompts, timing and evidence limits

`CC7B` manages a single captain/set-piece identity. It validates stored availability and a
resolved squad slot <=11, can fall back automatically, highlights an available current pick,
and returns the selected **player identity**. Enter chooses an available highlight; C invokes
the captain or taker helper; Esc/timeout retain the current usable pick. Slot eleven is valid.
That is a different interface from the full-order `9B93` screen.

The role-2..5 Space view opens the board and performs a separate blocking read at `CF3A`.
The next Enter can dismiss that view without committing a taker. A later prompt Enter makes
the choice. Captain role one does not use that Space branch. A client that merges those reads
can wait for the wrong decision; source reading does not supply the missing genuine input
states on [#400](https://github.com/diegoami/goal2-archaeology/issues/400).

`CC2E` polls for a key, delaying ten calibrated units after an empty poll, up to its supplied
count. `0B7C`'s Y/N question uses 600 polls and answers yes only for a waiting Y. The single
taker prompt uses 1000 polls. Their nominal 6000/10000 calibrated units are not observations
of invariant host duration and do not advance the match clock. The wait-count/runtime-unit
gap on [#412](https://github.com/diegoami/goal2-archaeology/issues/412) is still open.

`0C0B` increments the unsigned delay byte below five and raises a result below two to two;
it preserves an already larger raw byte. For inputs 0,1,2,4,5,9,255 the results are
2,2,3,5,5,9,255. The last two are edited-width cases, not claims that the normal UI chooses
those settings. A generic clamp-to-five changes the primitive.

Eight altered-rule controls cover extra-time entry, keeper inclusion, initial availability
fallback, sudden-death equalisation, board dismissal, raw delay, normal player-goal counting
and fixture/working-score separation. None is a new original or port kick comparison. The
partial-order/dummy context and actual availability histories remain explicit audit questions;
new probes or match batches require the T105 design and accepted ES-R2 gate.
