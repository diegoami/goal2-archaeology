# Live match state: records, aliases and lifetimes

The match creates state on top of the [persistent records](match-fields.md): pitch identity,
coordinates, action handlers, ball travel, clocks, pending events, random streams and cached
values. Several addresses have misleading names if their owner or phase is omitted.
The [source ledger](../../notes/engine-study/T97/transient.json) pins the layouts and primary
routines; it does not claim a complete typed schema for every byte in DS.

## Live records and coordinate conventions

The active players are pitch slots **1..22**, with a 22-byte stride from DS:80E8.
Slot 0 is not another footballer. For a real slot s, the persistent player index is at
pitch[s]+0D; the record's +06 is its pitch-slot identity, not player+06's played position.

The shared six-byte sprite prefix is current coordinate, previous coordinate and glyph.
In the drawing routines the cell offset is:

```text
0x90E + s8(x) * 160 + s8(y) * 2
```

Thus x (+00) is the lateral coordinate contributing to the **screen row** and y (+01) is the
longitudinal coordinate contributing to the **screen column**. World-coordinate names must not
be confused with screen-column/row labels. Position and target words pack the low/high bytes;
equality can be an exact packed-word comparison. DS:0640 supplies an off-pitch sentinel;
(0,0) is not an invented substitute for it.

### Pitch record: 22 bytes

| Offset | Bytes | Field | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 1 | x | Signed lateral coordinate; contributes to screen row in drawing. |
| `+0x01` | 1 | y | Signed longitudinal coordinate; contributes to screen column. |
| `+0x02` | 2 | old_position | Previous packed coordinate used to restore the old occupancy cell. |
| `+0x04` | 2 | glyph | Character/attribute word drawn into the pitch occupancy picture. |
| `+0x06` | 1 | pitch_slot | Pitch identity 1..22, not the played-position code. Below12 selects engine side1. |
| `+0x07` | 2 | destination | Packed target x/y bytes; used by target tests and movement. |
| `+0x09` | 2 | post | Packed home/post x/y from played role. |
| `+0x0B` | 1 | x_offset | Signed lateral target offset. |
| `+0x0C` | 1 | depth_offset | Signed longitudinal depth/target offset. |
| `+0x0D` | 2 | player_index | Persistent player-record index, re-bound from the squad slot. |
| `+0x0F` | 1 | run_direction | Direction/state-of-motion byte; activity accounting tests unsigned <5. |
| `+0x10` | 1 | state_timer | State-dependent countdown (including chase/walk-off routes); not a global game minute. |
| `+0x11` | 1 | manager_extra | A260 stores manager_bonus(player.country)+32; assigned to all bound players, later gated by skill/event. |
| `+0x12` | 1 | state | Action-handler dispatch code, distinct from player status flags. |
| `+0x13` | 1 | placement_flag | Cached 3179 result; 278A halves derived skill when nonzero. |
| `+0x14` | 2 | activity | Update counter; 8AE9 can spend energy after >180 while live play is enabled; reset separately from energy. |

### Ball core: 12 bytes

| Offset | Bytes | Field | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 1 | x | Signed lateral coordinate; contributes to screen row in drawing. |
| `+0x01` | 1 | y | Signed longitudinal coordinate; contributes to screen column. |
| `+0x02` | 2 | old_position | Previous packed coordinate used to restore the old occupancy cell. |
| `+0x04` | 2 | glyph | Character/attribute word drawn into the pitch occupancy picture. |
| `+0x06` | 2 | velocity_x | Signed word used by travel computation; step code reads its low byte. |
| `+0x08` | 2 | velocity_y | Signed word used by travel computation; step code reads its low byte. |
| `+0x0A` | 2 | timer | Remaining ball-step timer. |

The annotation's nominal 12-byte ball core is **not the whole extent of accesses**:
`A375` initialises +0C/+0D and `83A2` reads/writes +0D, which are the adjacent globals
DS:8302 and DS:8303. A modern bounded Ball object needs those flags too; declaring the legacy
core size alone is insufficient. This is a layout boundary, not evidence of an accidental
original memory overrun.

### Referee sprite: 8 bytes

| Offset | Bytes | Field | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 1 | x | Signed lateral coordinate; contributes to screen row in drawing. |
| `+0x01` | 1 | y | Signed longitudinal coordinate; contributes to screen column. |
| `+0x02` | 2 | old_position | Previous packed coordinate used to restore the old occupancy cell. |
| `+0x04` | 2 | glyph | Character/attribute word drawn into the pitch occupancy picture. |
| `+0x06` | 1 | target_x | Referee target lateral/screen-row coordinate. |
| `+0x07` | 1 | target_y | Referee target longitudinal/screen-column coordinate. |

Offside markers at DS:82E2 and DS:82E8 use only the six-byte common prefix; they are not
eight-byte referee records. `8E24` operates on that prefix. The referee at DS:82EE adds a
target pair; the ball at DS:82F6 instead adds velocity/timer and adjacent flags.

## State families and lifetimes

The following are identified field families and important addresses, not an assertion that all
other globals are unused. Exact original/source locations and hashes are in the ledger.

### clock

| Location | Meaning / boundary |
| --- | --- |
| `DS:8319` | byte half-length threshold; adjacent831A is kickoff side, not its high byte |
| `DS:831B` | word regular remaining count |
| `DS:831D` | word subtick countdown, reload36 |
| `DS:831F` | word displayed/elapsed count |
| `DS:8321` | word accumulated added time |
| `DS:8325` | byte live-clock/activity gate |
| `DS:8326` | byte end-time flag |

### marking

| Location | Meaning / boundary |
| --- | --- |
| `DS:9976` | captain/set-piece taker slot table |
| `DS:9A3E` | quick flag byte; overlaps dummy marking row0, not an active marking word |
| `DS:9A3E+40*t+2*s` | marking words for active squad slots; index/lifetime must be read in context |

### occupancy

| Location | Meaning / boundary |
| --- | --- |
| `DS:7C16` | far pointer to live pitch picture read by move tests |
| `DS:7C1E` | background-picture pointer used for restoration |
| `DS:80FC` | second-team-is-host byte inside nominal pitch row0 |
| `DS:82E2,82E8` | two six-byte offside-marker prefixes |
| `DS:82EE` | eight-byte referee sprite |
| `DS:82F6` | ball core plus adjacent flags |

### restart

| Location | Meaning / boundary |
| --- | --- |
| `DS:8302` | ball/play gate; nominal ball+0C |
| `DS:8303` | in-flight/ball-phase flag; nominal ball+0D |
| `DS:830B,830C,830D` | holder/challenger/nearest pitch-slot selectors |
| `DS:8324` | shootout-specific control flag |
| `DS:8327` | ball-event/action code |
| `DS:9B30` | current fixture far pointer |
| `DS:9B34` | two current country words |
| `DS:9B3A` | two substitution-budget bytes |

### rng

| Location | Meaning / boundary |
| --- | --- |
| `DS:7B62` | main16-bit LCG state |
| `DS:8336` | separate sound-seed byte |
| `DS:8337` | precomputed foul draw bytes1..255 |
| `DS:8437` | foul-table index, wraps255to1 |
| `DS:9974` | original replay snapshot of main RNG word |
| `DS:A978` | far pointer to main RNG word, normally7B62 |

### save-decisions

| Location | Meaning / boundary |
| --- | --- |
| `DS:9B07` | per-side/squad saved form snapshot; not the live player form byte |
| `DS:9B55,7C37` | original snapshot/replay request flags |
| `Match.save/load` | adapter save/replay reconstruction of live port frames; distinct from original action replay |
| `Match.st` | host-side phase/decision/event bookkeeping, separate from original DS |

### score-statistics

| Location | Meaning / boundary |
| --- | --- |
| `DS:7B7E` | 20 statistic bytes, ten per side, including injuries not one of the nine displayed rows |
| `DS:7C3A` | man-of-the-match player word |
| `DS:80F2,80F6` | two pairs of raw bar counters; legacy variable names do not establish caption/meaning |
| `DS:9B3C` | two committed score bytes, also scratch during quick trials; write-site semantics matter |

Clock widths matter: DS:8319 is a **byte**, and DS:831A is a separate kickoff-side byte.
The remaining, subtick, elapsed and added-time quantities are words. `970C` reloads the
subtick with 36; T100 explains the zero-branch ordering rather than treating a clock label as
an unconditional ticks-per-minute constant.

The two bar-counter pairs are kept at their actual addresses. In particular, `9564`'s update
of the 80F6 pair tests the ball's signed longitudinal side relative to attack direction.
Do not infer its football meaning solely from a variable named possession; caption/writer
interpretation needs both sources.

## Aliases and cached values

**Nominal pitch row zero overlaps match globals.** Its address arithmetic reaches counters at
80F2/80F6 and the venue flag at 80FC (row0+14). Iterating it as another player would confuse
match state with a player's activity field. The active sweeps use slots 1..22.

**Pitch +06 is a slot identity.** `A260` writes it from the slot argument; `2974` selects
side 1 when it is below 12. Keepers are slots 1 and 12. Therefore `278A`'s +06<12 context
share selects side 1 and includes its keeper; shorthand calling this an outfield-only test
would be misleading. T98 uses the condition itself in its formula.

**The manager extra is stored for all bound players.** `A260` writes manager_bonus+32 at
pitch+11 without a goalkeeper-role test. `278A` decides when to add it by element/event.
The historical name keeping_extra must not be turned into a restriction that only a goalkeeper
can receive it.

**Derived pitch values can be cached.** The placement flag is copied from `3179` during
binding; posts, targets and activity have their own writers. Changing a persistent role byte
mid-match is not equivalent to reinitialising the corresponding pitch state. Likewise, changing
fixture countries/kind after setup does not automatically rebuild the venue flag. Experiments
must identify the intervention boundary and which dependent state has already been computed.

**The marking base also contains mode state.** Quick flag 9A3E lives at a dummy-index address
near marking words. Active marking indices, the full nominal region and adjacent flags are
not interchangeable homogeneous arrays. Preserve index conventions and lifetimes.

## Occupancy, randomness and continuation boundaries

The live picture at far(7C16) is read by movement/collision logic. Sprite drawing restores old
cells from the background at far(7C1E) and writes new glyphs; offside/referee markers participate.
A redraw can therefore change gameplay even when a new UI never shows that old picture.
Cosmetic pixels and simulation occupancy cannot be separated by their function name alone.

Random state is more than a single seed. Setup `2648` reseeds the main word from
fixture_index*(elapsed_year+1) and consumes draws to fill foul-table entries 1..255, with the
index initialised from the second country. The kit's optional seed intervention occurs later
at the captain prompt. Restoring or varying only DS:7B62 does not reconstruct/resample the
already-filled foul table and its index. DS:9974 is an original replay snapshot of the main
word; it is not a second independently advancing match stream. DS:8336 is the identified
sound-seed byte.

The live-clock flag and original key/decision waits are state too. A stopped clock is not proof
that no other code or RNG consumer runs. The kit adds its own phase/decision/event state in
`Match.st`; its save/load reconstruction of live Python port frames differs from the original
action-replay buffers (`15B9`/`0C65`). A readable rewrite must preserve the selected save,
continuation and event contract, not just the visible score and player records.

These are static/retained-source interpretations for ES-R1 review. No new match, original binary
execution or global alias proof was performed. The [access frontier](../../notes/engine-study/T96/access-frontier-v1.json)
retains unclassified pointer-context sites. Source ambiguities, including legacy naming and
unexpanded global fields, remain explicit rather than being filled with assumed football rules.

```bash
python3 -B notes/engine-study/foundations/check.py --task T97b
python3 -B notes/engine-study/T97/make_transient.py --check
```
