# Player fields: what is actually stored

A player is **one 20-byte record**, not twelve separately stored skill values. Most of what the
card calls a skill or characteristic is derived from this record, lookup tables and sometimes
the player's index. Playing context then changes the effective value used in a contest.

This is a source-backed interpretation for review, not a promotion of the underlying findings.
The [field ledger](../../notes/engine-study/T96/fields.json) pins primary original-code readers
and writers, their exact source locations/hashes and the 17 fields covering all 20 bytes.

## Record and identity

The player-array far pointer is at `DS:A91B`; the allocation is `0xEF24` bytes:
3,061 records of `0x14` bytes, indexed 0..3060. Normal country squads refer to positive
player indices; zero is a sentinel/dummy record, not an extra normal footballer. A country holds
20 player-index words. The first eleven list positions and their assigned roles determine the
lineup; the player index is not the squad slot or the pitch slot.

The original computes record offsets with 16-bit multiplication/addition and far pointers.
Do not turn representable arbitrary indices into a claim that every index is valid. The
[image adapter](../../runtime/original_match/image.py) and
[player reader](../../runtime/driver/players.py) document the allocation and identity checks.

Names are external: an initial array at `DS:9B70` and 11-byte surname Pascal strings at
`DS:9B6C`. The card/name builder `1771:2E93` combines them; a raw 20-byte player record
does not contain the name. The index also participates in height/foot derivation, so identical
record bytes at different indices need not yield identical displayed characteristics.

## Stored fields

A byte can represent 0..255 and a little-endian word 0..65535. Those storage ranges do not
establish naturally reachable values. Signed arithmetic, flags and encoded rating words
interpret the same bits differently. In particular, the high byte of a word is not another field.

| Offset | Storage | Source/interpretive name | Meaning and bounds | Influence and lifetime |
| --- | --- | --- | --- | --- |
| `+0x00` | byte | country | Owning country index; ordinary countries are 1..128; record zero is not a normal player. | Persistent identity; resolves country defaults/management, not an independent talent score. |
| `+0x01` | byte | age | Unsigned age; new-game samples are not a universal legal range. | Persistent; ability evolution, leadership and recovery/retirement routes; no standalone age multiplier in 278A. |
| `+0x02` | byte | peak_age | Creation-time age parameter controlling the ability curve; also an input to two-footedness. | Persistent; indirect skill scale and recovery effects; the displayed card does not show a peak-age field. |
| `+0x03` | byte | rating | Creation ceiling/rating parameter, conventionally called potential; not a stored skill. | Persistent; ability curve and derived hardness/leadership. Raising it alone is not the same as raising current ability. |
| `+0x04` | byte | ability | Current ability/skill scale, an interpretive name supported by its arithmetic use. | Persistent; directly scales derived skills and quick/silent strength; recomputed during ageing. |
| `+0x05` | byte | skill_profile | Profile selector, normally 1..16 at creation; shapes a curve rather than storing twelve independent values. | Persistent; skills, hardness, leadership and two-footedness. Profile numbers are not a simple quality ranking. |
| `+0x06` | byte | position | Current played position code, normally 0..13; zero is the goalkeeper role. | Persistent squad role; formation/movement/line allocation and placement penalty; distinct from club position. |
| `+0x07` | byte | club_position | Natural/club position code, normally 0..13; feeds class, height and foot tables. | Persistent; moving played position does not rewrite the natural skill profile. |
| `+0x08` | word | caps | Little-endian 16-bit appearance count; +09 is the high byte, not another attribute. | Persistent history; participant update increments it, retirement can read it. No identified direct skill term. |
| `+0x0A` | word | goals | Little-endian 16-bit recorded goals count; distinct from the seasonal scorer byte. | Persistent history/statistic; update and attribution depend on the goal route, not a talent input. |
| `+0x0C` | byte | morale | Player confidence/form. Arithmetic reads s8; result clipping is 1..32, while live adjustment can reach other bytes. | Live and persistent; directly affects skill/strength. Match snapshots distinguish transient team swings from saved form. |
| `+0x0D` | byte | fitness | Persistent condition/recovery baseline; not the same field as current energy. | Indirect match influence through restored energy and recovery; no identified direct arithmetic term in 278A/377E. |
| `+0x0E` | byte | energy | Current energy, read signed for availability/strength. Zero means injury on the card; signed-negative bytes are unavailable too. | Live and persistent; skill/strength/chance/availability effects. Ordinary match decay stops at 1 and does not decrement fitness. |
| `+0x0F` | byte | own_tactic_set | Pascal-set byte: elements 1..4 are values, elements 5..8 enable the respective overrides. | Persistent/managed controls with setup/reset rules; a clear override-enable bit means use the country's setting. |
| `+0x10` | byte | status | Packed flags, not an ordinal status score; element k occupies bit k-1. | Mixed lifetime: carried booking/ban, live booking/send-off, substituted-off and protect-zone flags; distinguish each flag. |
| `+0x11` | byte | scorer_count | Season/year scorer-table count; separate byte from the recorded goals word. | Persistent within its season/year accounting; scorer-table maintenance and yearly clearing, not a shot-skill input. |
| `+0x12` | word | performance | Signed rating word with sentinels/encoding: 0x7FFF blank, 55 starter baseline, +10000 substitute marker. | Live match assessment; commentary deltas, man of the match and automatic substitution decisions. It is not an independent skill. |

The primary original routines are `1771:96D3` (creation), `32EB` (ability),
`3A06`/`3947` (engine/display skill), `377E` (strength),
`3216` (availability), `0791:278A` (effective skill), `B7FA` (post-fixture participants),
`7CC5`/`B364`/`CB7D` (live/result/restored form), `6443`/`B602`/`B3B7`
(goal/scorer routes), and `1E53` (rating delta). The ledger gives each field's reader/writer
subset; these lists are intentionally primary routes rather than an exhaustive alias analysis.

## How to interpret influence

**Direct numerical inputs:** ability, profile and club position choose/scale derived skills;
form and current energy enter the effective skill calculation. Quick/silent line strength uses
a different calculation, including ability, energy and form. A larger displayed bar therefore
does not directly state a pass, tackle or goal probability.

**Role and control inputs:** played position controls formation/movement/line allocation and
placement costs; individual tactic/override bits change decisions; status flags change
availability, marking or participation. These are categorical conditions, not additive points.

**Indirect inputs:** age and peak/ceiling affect the ability/recovery trajectory and derived
traits. Fitness can matter through the energy restored before later play. Its absence from
`278A`/`377E` arithmetic is not a claim that fitness never affects a match.

**Assessment/history:** performance changes through commentary and can influence automatic
substitution and man-of-the-match selection. Caps/goals/scorer counts serve history, eligibility
or tables on the identified routes. A goal can both increase counters and alter confidence:
those simultaneous writes do not establish that the counter itself improves shooting.

The twelve skill names, characteristic derivations, status-bit meanings and computed-access
limitations are the T96b companion's scope. T98 supplies worked numerical traces rather than
inferring effect size from the field names.

## Bounds and uncertainty

- The record labels ability, potential and club position have different evidential histories.
  They are useful names supported by readers/writers, not proof of a modern football model.
- The confidence range 1..32 is a result-adjustment clamp, not a universal live-state invariant.
  Form 32 takes a different arithmetic branch from 31; signed bytes 128..255 are negative.
- Ordinary energy decay stops at 1. Injury writes zero; recovery/redraw and copying order need
  separate treatment. Availability tests signed energy, while a card's injury caption can test
  exact zero. These are different predicates.
- A field with no identified direct contest term is not globally unused. Menus, recovery,
  retirement, indirect/computed addressing and future phases remain part of the engine.
- All 20 bytes are accounted for structurally. Primary read/write routes above do not claim a
  complete resolved census of every memory alias; the next slice records that boundary explicitly.

Basis: [F007 creation](../../findings/F007-player-values-are-made-at-a-new-game-from-a-seed-per-country-not-from-the-dos-time.md),
[F008 player screen](../../findings/F008-the-player-screen-draws-12-skills-as-bars-derived-from-three-record-bytes.md),
[F018 condition](../../findings/F018-energy-is-expended-in-matches-and-restored-from-fitness.md),
[F021 match values](../../findings/F021-energy-and-form-set-a-players-strength-fitness-is-never-read-in-a-match.md),
the named originals pinned in the ledger, and their registered translations. New-game samples,
literal synthetic calls and whole-match observations retain their original scopes.
