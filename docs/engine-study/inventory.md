# Engine inventory: code, reading order and evidence

Read the engine in this order: **inputs/setup → match control flow → player values → choices
and contests → motion/ball play → events and persistent updates**. The port consists of Python
replacements for original routines dispatched through the original-match kit.

This inventory is pinned to source commit `08beac2e9d43faf766e445e924da096b8a99d748`:
**21 modules, 423 unique registered addresses, 406 bodies and 17 declared stubs**. All 423 addresses
have original-code index entries; 422 have decompiled locations and `214B:05F0` (screen-row
unpacking) has an explicit assembly fallback because decompilation failed. Loading these
registries creates no match and reads no original image.

The [machine-readable census](../../notes/engine-study/T95/census-08beac2e-v1.json) retains every
address, implementation and original location, annotation confidence/basis, chapter assignment,
family case/reference and **179 source hashes**. The generator has a separate hash. These are
source-inventory facts, not fresh match measurements or a claim of all-path correctness.

## Three execution paths

The fixture router decides whether to play a fixture. A played fixture enters `F1F6`
(`run_match`), uses setup `A4A1` and reaches the half/tick machinery through `F098`.
The tick loop `97D0` chooses quick `D733` or watched `9564` play. A silent computer result
takes `D47E`, line strengths and trial contests rather than the watched simulation.
A quick or silent result is therefore not a substitute for watched play in an effect experiment.

The kit runs `F1F6` and post-fixture player update `B7FA` as separate guest entry paths.
Do not infer that every post-match effect is a child of the watched tick. Managed decisions,
waits, substitutions and save/resume reconstruction also cross the kit/port boundary.

| Address | Original annotated name | Original location | Python location |
| --- | --- | --- | --- |
| `0791:9564` | watched_match_engine | `static/goal-exe/named/seg_0791_09.c:30` | `runtime/original_match/port/frame.py:464` |
| `0791:97D0` | match_tick_loop | `static/goal-exe/named/seg_0791_09.c:174` | `runtime/original_match/port/frame.py:612` |
| `0791:A4A1` | match_setup | `static/goal-exe/named/seg_0791_09.c:834` | `runtime/original_match/port/setup.py:316` |
| `0791:B7FA` | update_fixture_player_state | `static/goal-exe/named/seg_0791_10.c:741` | `runtime/original_match/port/update.py:398` |
| `0791:D733` | quick_match_engine | `static/goal-exe/named/seg_0791_12.c:265` | `runtime/original_match/port/quick.py:40` |
| `0791:F1F6` | run_match | `static/goal-exe/named/seg_0791_13.c:603` | `runtime/original_match/port/postmatch.py:31` |

Start with the [kit README](../../runtime/original_match/README.md),
[registry](../../runtime/original_match/port/__init__.py),
[record adapter](../../runtime/original_match/image.py) and
[match interface](../../runtime/original_match/match.py).
The original [routine annotations](../../static/goal-exe/annotations/routines.tsv) and named
index provide navigation; T100 supplies the detailed, source-checked tick sequence.

## Registered modules and chapter coverage

Every registered routine belongs to exactly one module row below. A module may support several
chapters. Finding IDs identify research to inspect, not a blanket promotion of its claims.
The census supplies each routine's exact locations and preserves confidence separately.

| Module | Entries | Declared stubs | Variants | Study chapters | Finding leads |
| --- | ---: | ---: | ---: | --- | --- |
| attributes | 22 | 0 | 5 | T96, T98 | F007, F008, F010, F015, F018, F021, F028 |
| ball | 21 | 0 | 3 | T102 | F022, F026 |
| contests | 17 | 0 | 3 | T99, T102 | F022, F026 |
| discipline | 20 | 0 | 4 | T104 | F018, F020, F024, F027, F029 |
| display | 88 | 17 | 74 | T97, T100, T104 | F013, F014, F030 |
| duels | 14 | 0 | 3 | T99, T102 | F015, F020, F022 |
| frame | 14 | 0 | 5 | T100 | F005, F013, F014, F029, F030 |
| geometry | 32 | 0 | 7 | T98, T99, T101 | F013, F015, F021, F022, F026 |
| menus | 27 | 0 | 4 | T103, T104 | F026, F029, F030 |
| motion | 11 | 0 | 3 | T101 | F013, F018, F028 |
| pilot | 1 | 0 | 3 | T101 | F013 |
| positioning | 16 | 0 | 3 | T101, T103 | F024, F026, F028 |
| postmatch | 12 | 0 | 6 | T104 | F014, F018, F019, F020, F023, F029, F030 |
| quick | 4 | 0 | 3 | T99, T100 | F005, F012, F021, F024, F027 |
| rare | 13 | 0 | 0 | T100, T104 | F005, F024, F027, F030 |
| restarts | 26 | 0 | 4 | T102, T104 | F013, F022, F027, F030 |
| runtime | 38 | 0 | 5 | T99, T100 | F004, F012, F013 |
| selection | 9 | 0 | 3 | T103, T104 | F024, F027, F029 |
| setup | 16 | 0 | 4 | T97, T103, T104 | F010, F024, F027, F028, F029 |
| takers | 10 | 0 | 3 | T99, T104 | F015, F023, F030 |
| update | 12 | 0 | 3 | T104 | F018, F019, F020, F027 |

The loader excludes `mem`, `guest` and `prove` from selectable modules because they are
machinery; the engine still depends on them. `_display_finals.py` registers into display,
rather than adding another selectable module. A registered variant is a deliberate alteration,
not evidence that its mutation was caught in a particular family.

The historical [allocation](../../experiments/E036-match-port/out/backlog/sizes-20261017d.md)
used a 540-routine static closure, assigned 442 entries to port tasks and placed 98 OUT.
Those planning-universe counts are not today's registry or a branch-coverage denominator.
Likewise, the 17 `Registry.stub` declarations are an API classification, not a count of all
semantically empty or display-only bodies.

## Existing family evidence

[Family discovery](../../experiments/E036-match-port/families.py) selects every top-level
family JSON for ALL. The pinned definitions now contain **75 cases**:

| Family | Cases | Variation and limitation |
| --- | ---: | --- |
| F40 | 40 | Reference friendly; 20 seeds and their edited weak/tired-opponent counterparts. |
| O8 | 8 | Four other country pairs; friendly and qualifier cases. |
| S | 16 | Decisions, no managed side, injury/hard play, mixed quick/watched paths, knockouts, set-piece taker. |
| R | 10 | Frontier cases including competitive quick play and disciplinary/removal routes. |
| FS | 1 | Genuine-source finals snapshot restarted through the API; not an untouched original-key continuation. |

The census hashes each definition/reference and checks that every declared ID exists in its
declared reference. It does **not** rerun the comparator or certify each record's outcome.
The active [display profile](../../experiments/E036-match-port/families/display/profile.json)
binds a reference/proof with an empty DS mask. Historical unprofiled `--no-screen` has different
projection semantics; consult [E036 notes](../../experiments/E036-match-port/notes.md) and
[the comparator](../../experiments/E036-match-port/compare.py) before reusing results.

These are scenario cases, not 75 independent countries, seeds or effect observations. Edits,
shared start states and answer policies matter. Earlier 62-case records describe their actual
runs; the label ALL does not retrospectively cover later additions.

## Evidence boundaries and unresolved work

All 35 finding-file headers still declare proposed (two include a terminal period).
Finding-header status, claim status in `spec/` and annotation confidence are different
registers. This census preserves them; it promotes none.

Read named original sources first, then the listing/raw decompilation and the port. The main
leads are [the tick map](../../findings/F013-the-watched-engine-tick-map.md),
[skills/keeping](../../findings/F015-keeping-and-penalties-read-through-the-derived-skills.md),
[condition](../../findings/F021-energy-and-form-set-a-players-strength-fitness-is-never-read-in-a-match.md),
[contests](../../findings/F022-contest-sites-287c-5474-5d69-and-the-branches-e011-takes.md),
[tactics](../../findings/F026-what-each-team-tactic-changes-in-a-watched-match.md),
[discipline](../../findings/F027-discipline-cap-bans-added-time-substitution-budget-and-foul-chain.md)
and [positions/foot](../../findings/F028-formations-are-posts-by-position-code-and-out-of-position-costs-one-halving-flag.md).

- No fresh match was run: source membership is not parity, reachability, exhaustive branch
  coverage or a measured football effect.
- The current kit still uses Unicorn and an original image. This inventory delivers neither
  T78's standalone engine, T79's distribution sheet nor T80's packaging.
- Annotations do not name every byte or indirect access. T96/T97 must retain unlabelled bytes,
  computed accesses and context-dependent interpretations.
- Names can retain stale interpretations: the pitch `keeping_extra` annotation still says
  event `0x18`; corrected F015/T40/T42 material distinguishes a set's encoding from its event
  members and the unconditional element-table gate. T98 must follow the reader.
- Original-key gaps (#400), offside interpretation (#227), the uncaught A2E6 falsifier (#375),
  listing-edge tests (#412), displaced return-frame proof (#394) and stateful display boundaries
  (#416) remain leads. Registration does not close them.
- Pitch drawing participates in occupancy/collision state. Display-looking work, state aliases
  and replay/save continuations need a read/write trace before simplifying the engine.

## Reproduction

```bash
PYTHONPATH=runtime python3 -B notes/engine-study/T95/census.py --check
PYTHONPATH=runtime python3 -B notes/engine-study/T95/census.py --controls
python3 tools/check_links.py
```

The generator refuses source drift from the baseline and refuses to overwrite an existing census
or requested receipt. The check regenerates the complete manifest, validates uniqueness,
classification and source locations, and requires every module's chapter row.
The controls accept the valid manifest and reject a missing routine, a duplicate address and
a declared stub relabelled as a body. They protect inventory integrity, not a football hypothesis.
