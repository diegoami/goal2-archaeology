# Persistent team, manager and fixture state

A match is not determined by player records alone. The lineup and roles, manager ability,
tactics, fixture kind, venue context and competition state select different code paths and
different values. Persistent records also change after play, so a second fixture need not begin
with the first fixture's inputs.

The [source/layout ledger](../../notes/engine-study/T97/persistent.json) pins original routines
and accounts for country191, fixture8, manager3 and game270 byte spans. Unknown groups remain
explicit; byte coverage is not a claim that every historical subfield has been decoded.

## Identity, indexing and ownership

| Object | Storage / index |
| --- | --- |
| Countries | Far pointer DS:A917; 129 records of 0xBF bytes, ordinary countries 1..128 and a dummy zero row. |
| Players | DS:A91B; positive player words held in country squad slots; a player word is not a lineup slot. |
| Manager entries | DS:A91F; 135 entries of three bytes, indexed by country+2E. Computer entries begin 1..128; human entries are 129..134. |
| Fixtures | DS:A92B; fixture n is at base + 8*(n-1). The fixture index is external to its eight-byte record. |
| Game record | DS:A923; 0x10E bytes allocated, holding progression, fixture and manager context. |
| Pool index list | DS:A927; per-manager base from DS:6D18 selects 80 player-index words. Names and manager labels are separate arrays. |

Allocation is visible at `2139:0000`; country/squad initialisation at `1771:9A40`.
The [record adapter](../../runtime/original_match/image.py) preserves these identities.
A country's manager byte selects a manager entry; it is not a manager-skill value.
The managed predicate `1771:0B77` is strictly **manager_index > 128**, so index 128 remains
a computer manager. Arbitrary bytes above the allocated manager range are not automatically valid.

The engine uses side 0 for fixture country +4 and side 1 for +6. Side 0 occupies pitch
slots 12..22; side 1 slots 1..11. These are engine indices, not a home/away naming convention.
A readable API should distinguish country ID, player ID, squad slot, pitch slot and engine side.

## Persistent layouts

### Country record

| Offset | Bytes | Field/group | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 40 | squad | Twenty little-endian player-index words; slots 1..11 are starters, 12..20 bench; order changes can persist. |
| `+0x28` | 2 | unresolved_28_29 | Unexpanded country bytes +28..29; no invented skill or lifetime assignment. |
| `+0x2A` | 1 | continent_rank | Ordinary continental rank 1..32; country-rating/development/result-expectation input. |
| `+0x2B` | 1 | world_rank | Ordinary world rank 1..128; country-rating and result-expectation input. |
| `+0x2C` | 1 | continent | Ordinary continent code 1..4; rating, venue-host lookup and competition/recovery routing. |
| `+0x2D` | 1 | team_tactics | Eight Pascal-set defaults, modified/reset by setup/AI/manager paths; player overrides are separate. |
| `+0x2E` | 1 | manager_index | Index into 3-byte manager entries; >128 means human-managed. Not itself manager ability. |
| `+0x2F` | 2 | ranking_points | Persistent ranking/competition points; not the quick engine line sums. |
| `+0x31` | 70 | historical_totals_unexpanded | Persistent historical/season totals; D050 includes a season block at +3B. Exact subfield types/lifetimes are not all resolved in this foundation. |
| `+0x77` | 48 | largest_result_records | D050 largest win/loss fixture-record area +77..A6; preserve as historical data, not player attributes. |
| `+0xA7` | 24 | streaks_unexpanded | D050 home/away/all streak/current-maximum area +A7..BE; subfield enumeration remains reader-specific. |

Squad order is state. Substitution/sort swaps can persist, and formation labels/counts depend
on current played-position bytes among the starters. A single stored formation number is not
the original's full representation. Managed and computer reset/selection paths differ.

The country ranks and continent feed `1771:10E7`'s rating:
`((5-continent)*(33-continental_rank) + 129-world_rank) idiv 2` in its ordinary domain.
That rating feeds development and result expectations; it is distinct from live lineup strengths,
the TEAM panel's aggregates and manager ability. Current tactics can differ from the original
R008 defaults until the relevant reset path restores/re-derives them.

The large result/streak groups have identified ownership and writers, especially `0791:D050`,
but their subfield enumeration is intentionally unresolved here. Preserve those bytes in a
compatible adapter; do not replace them with zero or call them padding.

### Manager entry

| Offset | Bytes | Field/group | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 1 | managed_country | Country association; computer entries start with their country, human entries use 129..134. |
| `+0x01` | 1 | ability | Unsigned manager ability; 0AA7 reads this byte to compute floor(ability/8)+16. TEAM Skill labels also read it. |
| `+0x02` | 1 | result_delta | Signed manager result-delta accumulator; B6CC adds and clips to -127..127. Distinct from ability and country rank. |

The manager match bonus `1771:0AA7` reads **unsigned byte +1**, divides by eight and adds sixteen.
Thus raw ability 0..255 maps to a bonus 16..47. Its uses include quick line strengths and the
manager-derived pitch extra. TEAM Skill text (`1771:0AF8`) is a different lookup of the same
ability byte, not a country/player aggregate. The result-delta accumulator at +2 is a separate
signed quantity; `B6CC` clips its updates to -127..127.

### Fixture record

| Offset | Bytes | Field/group | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 1 | first_score_or_pending_mark | Side-0 score after play; pending marker such as FE/FF before play. Phase-dependent, not always a score. |
| `+0x01` | 1 | second_score | Side-1 score after play; pending representation must be read with its phase. |
| `+0x02` | 1 | kind | Competition/friendly kind; 1 is friendly; gates budgets, fouls, results/deciders and venue. |
| `+0x03` | 1 | result_code | Played result: 0 side-0 winner, 1 side-1 winner, 2 draw; a silent decider coin may choose 0/1 despite equal score bytes. |
| `+0x04` | 2 | first_country | Country for engine side 0; API first does not mean home. |
| `+0x06` | 2 | second_country | Country for engine side 1; used by the venue-host equality flag. |

Result code describes the completed result, not a universal formula of the score bytes:
`D47E` can resolve a still-level silent decider with a coin and record winner 0/1.
Pending markers must be distinguished from completed score zero. Fixture kind controls whether
play happens, discipline/budgets, post-match routing and whether a winner is required.

### Game record

| Offset | Bytes | Field/group | Meaning |
| --- | ---: | --- | --- |
| `+0x00` | 1 | human_count | Number of human managers at creation (ordinary 1..6). |
| `+0x01` | 37 | manager_context_unexpanded | Manager/selection flags and context not fully typed here; preserve them. |
| `+0x26` | 2 | fixture_index | Current fixture index used to locate the 8-byte fixture, not stored inside it. |
| `+0x28` | 2 | fixture_count | Fixture-list count/context. |
| `+0x2A` | 4 | host_prefix_unexpanded | Includes the dummy/base host-table region; no further semantics assigned. |
| `+0x2E` | 10 | host_countries | Five host-country words: continent slots 1..4 and slot 5 selected by the calendar-class flag. |
| `+0x38` | 2 | elapsed_year | Year/cycle offset: initialised to 0; incremented by the yearly progression. |
| `+0x3A` | 2 | initial_year | Initial calendar-base year from DOS year+1 made even, not the elapsed counter. |
| `+0x3C` | 1 | cycle_stage | Stage byte in the competition cycle. |
| `+0x3D` | 1 | option_3d_unexpanded | Initial option byte 1; exact UI meaning not established here. |
| `+0x3E` | 1 | option_3e_unexpanded | Initial option byte 2; exact UI meaning not established here. |
| `+0x3F` | 1 | speed_delay | Match speed/delay option; simulation determinism still requires the stated key discipline. |
| `+0x40` | 1 | calendar_class | Initial year modulo 4==2 flag; chooses host slot 5 and stage calendar variant. |
| `+0x41` | 205 | remaining_context_unexpanded | Other options, manager flags, pool viewports and strings within the 0x10E-byte allocation; not fully typed here. |

The two year words are distinct: `1771:9B85` initialises +38 to zero and +3A from the DOS year,
made even after adding one. A field simply called year in an adapter may mean the elapsed
counter; do not substitute the initial calendar word for it. The host words at +2E..37 precede
these year words. Additional manager flags/viewports/options and strings remain preserved in
the unresolved spans, rather than guessed from an offset or caption.

## Fixture routing and venue

The router `000E:6CA7` distinguishes pending/watch decisions and kind-zero preparation
from played `0791:F1F6` and silent `D47E` routes. Kind zero on the preparation path is not
a completed ordinary watched match. The outer silent route `000E:6970` also performs its
post-result updates.

Venue selection is explicit:

1. `0791:A6E4` returns fixture country +6 unless the kind belongs to the result-kind set.
2. Otherwise it reads the game host word selected by the second country's continent, or host
   slot 5 when game+40 is set.
3. `D44C` returns whether this host equals the second country; setup stores that result
   in `DS:80FC`.

This identifies **second-team-is-host**, not a generic symmetric home flag.
A friendly/qualifier normally takes the second-country venue route; a finals-like result kind
can select a neutral host. Actual fixture kind membership, not a display label, chooses it.
T98 describes the conditional line/skill arithmetic; T105 can later test outcome effects without
confusing a country swap with an unchanged venue context.

Important source addresses: `A4A1`, `A6E4`, `D44C`, `D47E`, `B7FA`, `B6CC`,
`BC5D`, `D050`, `1771:5A03`, `0AA7` and `9B85`; exact original locations/hashes
are in the ledger.

## Cross-match lifetime and unresolved groups

Persistent does not mean immutable. Lineup/role/tactic edits, participant caps, recovery,
confidence, bans, ranking/history and pool updates have different writers and timing.
Match form also has a live/saved snapshot distinction. The kit runs the post-fixture player
update separately from run_match; callers must preserve that continuation contract.

The [T96 dictionary](player-fields.md) and [derived traits](player-derived.md) explain player
inputs. T97b accounts for pitch/ball/global state created from these persistent records.
T104 will explain the detailed update lifecycle; this foundation records owners and boundaries.

Evidence limitations: these are static source readings and reused findings, not new matched
games, full save-format proof or proof of every indirect alias. Country history subfields,
several game options and manager-specific flags remain explicitly unexpanded. Host identity and
side numbering are established by their writers/readers; a net home-advantage effect is not
measured here. The F035 [country decoder](../../runtime/decoders/country.py) documents the
separation of rank-derived TEAM Status and manager-derived Skill.

Reproduce layout/source checks with:

```bash
python3 -B notes/engine-study/foundations/check.py --task T97a
python3 -B notes/engine-study/T97/make_persistent.py --check
```
