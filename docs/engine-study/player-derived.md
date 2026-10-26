# Derived player traits and their actual inputs

The card's twelve skill bars and several characteristics are computed views. They are not
independent values stored in the player record. A faithful model must preserve the relationships
among them, the player index and current playing context.

Read this beside the [stored-field dictionary](player-fields.md).
The [derived-trait ledger](../../notes/engine-study/T96/derived.json) pins original readers,
all twelve skill elements, dispositions for all 17 stored fields, and a recount of retained
original-code foot probes. It preserves proposed/unreviewed research status.

## Derived skills

The displayed elements are:

| Element | Skill | Stored inputs to its base derivation |
| ---: | --- | --- |
| 1 | keeping | ability +04, profile +05, club position +07 |
| 2 | kicking | same three bytes, a different class-table column |
| 3 | tackling | same |
| 4 | heading | same |
| 5 | marking | same |
| 6 | passing | same |
| 7 | crossing | same |
| 8 | feinting | same |
| 9 | control | same |
| 10 | dribbling | same |
| 11 | shooting | same |
| 12 | penalties | same |

For element e, club position selects a class in `DS:6D25[12*club+e]`; profile selects
the corresponding weight in `DS:6DCD[12*profile+class]`. The display routine
`1771:3947` scales that weight by ability+1 and divides by 256. Engine derivation
`1771:3A06` uses divisor 32. Rounding means an engine value is not simply eight times
the displayed bar length.

`0791:278A` then applies form/current energy or the penalty-element base, placement halving,
keeper extra and a context share. T98 traces the finite-width arithmetic and examples.
The same visible bar can therefore enter different contest values. There is no thirteenth
stored goal-kicking skill merely because help text uses that phrase.

Changing profile reshapes a vector of skills; changing ability scales several together.
Changing played position (+06) does not rewrite the natural class lookup (+07), but can change
positioning and the placement penalty. A rewrite with twelve freely editable native skill
fields would need an explicit compatibility decision.

## Characteristics and context

| Trait | Actual derivation/input | Identified use |
| --- | --- | --- |
| Height | `1771:2FAD`: club-position base at DS:0E46 plus DS:0E54[player_index mod 12] | Card; computer role conversion `0791:BEC7` uses the 72-inch threshold. The direct call census does not establish a height term in aerial duels. |
| Foot index | `1771:3088`: DS:0E60[14*DS:0E7C[player_index mod 3]+club_position] | Placement and substitution-role checks; normal table values 0 left / 1 right. |
| Two-footed display predicate | `1771:3041`: peak_age + profile equals 30 | Card and foot/role predicates; separate from foot index. |
| Hardness | `1771:2FFB`: profile minus the low bit of the creation ceiling | Foul/injury decisions and initial tactic choice; not another stored tackling skill. |
| Leadership | `1771:30D9`: signed remainder of (ceiling-profile)/8, halved for age below 21 | Captain/leader selection and card; natural inputs give the familiar 0..7 range. |
| Performance | Commentary-updated word, decoded and bucketed by `1771:3827` | Rating text, man of the match, automatic substitution decisions. |

Height and foot can differ for identical record bytes at different player indices. Keep a stable
identity/index or preserve their derivation explicitly in a readable engine.

The static call table names height callers `0791:BEC7` and `1771:42BC`; this is evidence about
identified direct calls, not a general proof that height has no indirect effect. BEC7 changes one
eligible forward's played role according to height, so a display characteristic can affect play
through a manager decision rather than a direct duel multiplier.

Leader scan `0791:1F3C` considers available starters, replaces the current best only on a
strictly larger leadership value and keeps the first on ties. It supports captain/taker selection
and `20E3`'s unmanaged-side refresh. Signed division and the later unsigned half-step matter for
arbitrary synthetic bytes: do not replace the original sequence with Python's negative modulo.

## Flags, performance and availability

For the status byte +10, Pascal element k means bit k-1:

| Element | Mask | Meaning on the identified routes |
| ---: | --- | --- |
| 1 | 0x01 | No semantic assignment established by this foundation reading; do not call it unused globally. |
| 2 | 0x02 | Same unresolved boundary. |
| 3 | 0x04 | Substituted off / participant flag; availability rejects it. |
| 4 | 0x08 | Carried booking. |
| 5 | 0x10 | Booked in the current match. |
| 6 | 0x20 | Sent off; availability rejects it. |
| 7 | 0x40 | Explicit marking override; the marking word distinguishes protected zone from a chosen opponent. |
| 8 | 0x80 | Suspended; availability rejects it. |

`1771:3216` rejects signed energy below 1 or status elements 8, 6 or 3. Thus a live booking
alone does not make a player unavailable, and a substituted-out player cannot be put back merely
by restoring energy. The card's exact-zero injury caption is a different predicate from signed
availability. Marking overrides (`1771:49B8`, `3EF8`) are not discipline scores.

Performance is not a skill modifier in `278A` or `377E`. It nevertheless affects play:
`0791:8062` compares the player's signed performance word against a clock-dependent threshold
when considering a computer substitution. Describing this as a low-energy threshold would be wrong.
Its full timing/budget/participation conditions belong to T104.
The blank sentinel 0x7FFF and substitute encoding must be decoded before treating a displayed
rating as an ordinary number.

## Field roles and access boundaries

The ledger assigns a disposition to every stored field. Identity resolves country context;
age/peak/ceiling feed development and derived traits; ability/profile/natural role determine
skills; played role and tactic/status bits control actions; form/energy change current values;
fitness affects recovery; counters and performance support history, eligibility and decisions.
No field is silently dropped because its effect is indirect or display-related.

This is complete **byte ownership and primary-route mapping**, not a complete abstract
interpretation of every memory operation. Explicit unresolved access families are:

- Computed selectors, such as the geometry helper that derives a player address from pitch+0D
  and reads a caller-selected field; the selected offset must be traced at its caller.
- Generic `Rec.u8/u16`, raw memory reads/writes and nested-parent pointers whose record kind
  depends on a caller. A literal offset alone does not identify a player field.
- Whole-record swaps/copies, replay snapshots and image adaptation that move all fields without
  naming them individually. A field can be written through a copy rather than a named setter.
- Player index, country/manager/fixture context and pitch state outside the record. A 20-byte
  record by itself is not the full input to a match value.

These families point back to T95's registry/source census and T97's state dictionary; they are
not an assertion that all aliases have been resolved.

The [access frontier](../../notes/engine-study/T96/access-frontier-v1.json) makes this boundary
concrete: 2,278 memory/record-API call sites across the 22 port source files, with operation names
and source line lists. It deliberately includes non-player, table, stack and copy accesses; their
record kind remains unresolved in that ledger until pointer/caller provenance is followed.
This is an exhaustive syntactic census at the listed API names, not an exhaustive semantic census
of player accesses or evidence that each candidate actually reads a player. Raw machinery is
listed as excluded. Reproduce it with `python3 -B notes/engine-study/T96/make_accesses.py --check`.

## Known asymmetry and evidence limits

The original `1771:3179` placement test is asymmetric. With normal foot indices:

| Foot index | Two-footed? | Flank penalty, before goalkeeper-role mismatch |
| --- | --- | --- |
| left (0) | either | Played code 4, 8 or 11 |
| right (1) | no | Played code 3, 7 or 10 |
| right (1) | yes | None |

Exactly one of played/natural position being goalkeeper adds the placement flag regardless.
F028 already describes this quirk; the port preserves it. The flag halves the derived skill
on its identified reader, rather than applying a special per-cross wrong-foot penalty.

The retained original routine probe contains 2,352 cases and zero rule mismatches. It includes
102 two-footed/left-index/right-flank cases (96 without goalkeeper mismatch), all flagged.
However, its true fixtures set peak_age=15 and profile=15; peak age 15 is outside natural
generation ranges. Its false fixtures use zeros. This proves the routine's response at those
synthetic inputs, not a naturally generated player's match effect.

A range-valid static tuple is player 1, club code 2, played code 4, peak age 25, profile 5:
the tables give left index and the sum gives two-footedness, yet the branch flags placement.
It was not freshly executed or observed in play. Reachability/frequency in normal matches remains
unestablished here. The helper [reading receipt](../../notes/engine-study/T96/foot-helper-v1.json)
records one bounded Sol/xhigh source check; the main session's generator independently recounts
the retained TSV. That assistance is not the ES-R1 independent review.

Basis: [F008](../../findings/F008-the-player-screen-draws-12-skills-as-bars-derived-from-three-record-bytes.md),
[F028](../../findings/F028-formations-are-posts-by-position-code-and-out-of-position-costs-one-halving-flag.md),
the pinned original readers in the ledger, and the retained probe's source/TSV.

Reproduce the structural and retained-data checks with:

```bash
python3 -B notes/engine-study/foundations/check.py --task T96b
python3 -B notes/engine-study/T96/make_derived.py --check
```
