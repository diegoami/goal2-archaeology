# Substitutions: permission, selection and rebinding

A substitution is a coordinated transaction across squad identities, player status, saved
form, marking, pitch records, cached skills and replay state. The UI and normal callers supply
guards that the low-level refresh routine does not repeat. A raw record edit or isolated call
is therefore different from the normal operation.

The [sixteen-routine ledger](../../notes/engine-study/T104/T104c-v1.json) and
[source calculations](../../notes/engine-study/T104/substitutions.py) cover those layers.
They execute no engine, UI or original-key path. Interpretations remain proposed for ES-R2;
the genuine-input gaps on #400 and runtime-test gaps on #412 remain visible.

## Admission and identity layers

`8062` checks substitutions at stoppages/half starts and in the quick engine's appropriate
minute path. A managed notice depends on request `9B40`, keeper availability, time and budget.
The interaction latch `9B41` is distinct from remaining allowance `9B3A[side]`.

In in-match SELECT TEAM (`E44F`), Enter reaches `E022` only outside replay, with permission
and positive budget. Otherwise it can set/cancel a substitution request; requesting does not
itself swap a player or spend the allowance. Position/tactic editing has separate controls,
and the out-of-match squad/pool exchange is a different branch. `E949` selects the managed
screen or the unmanaged team-view route.

`DE27`/`DE51` distinguish the squad pane's one-based slot from the pool's raw index/pointer.
Neither is the persistent player identity. The in-match two-mark swap rejects:

- Both marks in the same block (both first eleven or both bench).
- An unavailable incoming bench player.
- An outgoing player with sent-off status element six.

The entry gate and those refusals together explain an admitted managed swap. `E2A0` only
chooses the hint screen; displayed instructions are not the authorisation predicate.

`C5DC` itself decrements the allowance byte unconditionally. Calling it with zero would
wrap to 255; that arithmetic alone is not a demonstrated normal-path exploit. The managed
UI checks the allowance first. The direct source callers of automatic `C88D` are `8062`,
which checks budget, and injury `7D56`; its zero-budget/energy-zero case goes to removal
rather than a bench replacement. Preserve caller protocols when exposing a readable API.

`EA09` validates managed elevens before normal play resumes. It rejects empty identities,
requires exactly one available played goalkeeper, and limits available players to three of
each played role 1..13. An unavailable first-eleven member invalidates pre-match selection;
in-match unavailable records are handled differently, allowing the remaining team to continue.
Role 13 is included. New source calculations exercise that threshold but do not close #412's
missing real port-unit edge test.

## Automatic versus managed replacement

Automatic `C88D` builds a natural-role bench map through `C7EB`, chooses through `AAE8`,
optionally uses compatibility fallback `A9B8`, copies the outgoing **played role** to the
incoming player, swaps associated records and refreshes the pitch slot. The managed `E022`
swap **retains the incoming player's played role**. It can therefore change shape unless
the user separately edits that role; natural/club role is another field again.

| Selection component | Actual criterion |
| --- | --- |
| `C7EB` map | Available bench slots 12..20 keyed by natural role; later slots overwrite earlier ones. |
| `AAE8` | Outgoing played-role preference list at `099A+8*role`; last passing mapped preference wins, with the flank/two-footed gate. |
| `A9B8` fallback | Highest compatibility-table grade by outgoing role and candidate natural role; foot mismatch can halve the grade, strict improvement keeps first tie. |

These are not a universal strongest-player search. For outgoing centre back role two, the
static preference list is `[2]`. Available natural centre backs in bench slots twelve and
eighteen leave the map pointing to eighteen, regardless of a higher ability rating in twelve.

The foot checks are not interchangeable either. A two-footed left-footed candidate can pass
the bench filter for a right-flank role, while `3179` still sets placement flag one on that
left-foot/right-flank branch. The [player derivation](player-derived.md) and
[placement audit](player-fields.md) explain the original asymmetry. Combining both tests into
one clean-looking foot-compatibility predicate would change behaviour.

The normal AI performance trigger in `8062` has its own context: budget available, relative
slot 2..11, sent-off bit clear, signed energy positive, **remaining count `831B` strictly between
one and 35**, and raw signed performance below `90-remaining`. It does not test elapsed minute
with a generic late-match label. Remaining 34/performance 55 qualifies; remaining 35 does not;
remaining two/performance 88 fails equality while 87 passes. A raw 10055 performance marker
does not pass that low threshold. Mode length and performance encoding therefore matter.

## The rebind, cache and sort transaction

Once squad identities change, `C5DC` marks the outgoing player substituted off (status
element three), reinitialises the live slot through `A2E6`, sets incoming performance to
0x2747 (10055), re-derives AI own tactics, manages captain placeholders around `230C`, spends
the allowance and sets snapshot request `9B55`.

| Layer | Relevant effect |
| --- | --- |
| Persistent incoming player | Current energy/fitness is retained; performance marker is reset; managed played role is retained, AI role copied earlier. |
| Live pitch record | Binding/placement/manager cache refreshed; activity and timer reset, run direction five; coordinate initialisation has its own staging. |
| Associated identity state | Country squad words and saved-form entries swap; marking handling differs between managed and AI operations. |
| Whole eleven | Re-sort/rebind, marking assignment, glyph refresh, captain contribution and posts recomputed through `230C`. |
| Continuation | Budget byte decreases; snapshot request marks a new boundary rather than instantly taking a snapshot. |

`A260` binds persistent identity and initial manager cache/placement. `A2E6` adds coordinate,
colour, offset, activity/timer and run-direction initialisation; it does **not** refill energy
or zero every action field. `C5DC` preserves the outgoing drawn point (using the entry point
when already off pitch), restoring it as old position after initialisation. Current and drawn
positions can differ transiently until movement. The glyph refresh `0691` is not a coordinate
reset. A constructor that sets one position field and assumes the rest is equivalent loses
this staging.

Managed marking handling first clears the outgoing first-eleven marking word, then swaps;
AI replacement swaps its two marking words without that same clear. These differ from the
ordinary sort's identity-preserving exchanges. For outgoing mark 205/incoming zero, the
managed pair becomes zero/zero, while the AI pair becomes zero/205 before later marking
reconstruction. Keep the actual write order and distinguish table words from player IDs.

The pairwise sorting algorithm is also significant. Equal comparisons do not swap directly,
but a later smaller key can reverse earlier equal-key players. Keys `[A:14,B:14,C:1]` become
`C,B,A`; Python's stable `sorted` gives `C,A,B`. Pitch records, squad words and associated
state must move together. Equal-key stability cannot be assumed from the strict comparison.

One suspected cache issue has a normal-path explanation. `C5DC` can temporarily use a managed
captain placeholder during its internal re-sort, then clear the placeholder. The enclosing
`ED8A` menu re-sorts/rebinds on entry and normal exit. Exit therefore resets the initial extra
before `20E3` applies the selected captain's leadership. With initial 56, placeholder leadership
two can give intermediate 60, but selected leadership seven gives final 70 after rebinding,
not 74 from repeatedly adding. This is source call-order evidence, not proof of every raw
direct-entry or reentrant use.

## Worked checks and remaining boundaries

Supply an admitted managed swap of first-eleven slot three and bench eighteen, positive budget
two, available incoming player with energy twelve/played role seven, outgoing role two and no
sent-off refusal. After the swap/refresh, incoming role remains seven, energy remains twelve,
performance is 10055, activity zero, allowance one and snapshot requested. The later sort can
move the player to another pitch index; the source projection does not pretend the old slot
address stays its permanent identity. The outgoing player retains performance and a substituted-
off status, relevant to later participant/MOM processing.

For the corresponding AI role-two map, bench eighteen is chosen over twelve and receives
played role two. For player index one/natural role two/profile five/peak age 25, the static
foot tables give left/two-footed; the bench filter passes, yet rebinding at played role four
gives placement flag one. These supplied cases show separate mechanisms, not an observed
frequency of bad AI replacements.

The script rejects first-bench-wins, stable-sort substitution, role copying on the managed
path, unifying the foot predicates, an inclusive performance cutoff and captain addition
without rebind. It also checks allowance/refusal and managed validity predicates. These are
source-derived transactions, not full menu/ABI or genuine-key reproductions. F029/T75 and
#400 keep their exact evidence limits. A readable high-level operation should expose admission,
selection, identity exchange and complete rebind stages while preserving their observable order.
