# Country TEAM Status and Skill delivery (#428, T94)

The original TEAM layout resolves a misleading routine annotation:

| Visible field | Original source | Germany in both recorded states |
| --- | --- | --- |
| Status, row 8 / column 25 | Country rank formula `1771:10E7`, label `1527`, table DS:7884 | giant (country rating 126) |
| Skill, row 10 / column 24 | Selected manager's ability byte, `1771:0AF8`, table DS:7894 | eclectic (manager 12, ability 126) |

F035 remains proposed. Independent review and merged source/file hashes are linked
on the delivery issue. The finding and `notes/428/original-r3.json` contain the exact
contract and original observations. The earlier r1 receipt's semantic keys were
reversed; its raw screen rows are preserved. Use r2/r3 for interpreted visible `status`/`skill` values. Their legacy `status_byte` key means manager ability (+1), not the visible country Status; it is retained unchanged for provenance.

## Consumer adapter

Deliberately vendor reviewed `runtime/decoders/country.py` and its dependency
`runtime/decoders/manager.py`, recording both file hashes and the reviewed commit.
The modules have no emulator or original-data dependency. In a separately scoped
goal2 consumer task:

1. Read exactly 191 current bytes at `far(DS:A917)+191*country` (country 1..128).
2. Read m from country+0x2E. Read exactly three bytes at `far(DS:A91F)+3*m`
   when m is nonzero, including human manager slots 129..134; do not use the country
   number as a shortcut. Manager+1 is ability; +2 is confidence and is not read.
3. Supply `read_ds(off,n)` and `read_code(image_segment,off,n)` returning exact
   bytes from the current original memory. Code segments are original image
   paragraphs: the code label is 1771:0AF0. Call `team_labels` and forward only
   `status` and `skill`; its `country_rating` is a provenance/debug value.
4. Manager 0 yields Skill = None because the original draws no label. Ability 0
   yields `unknown`. The full unsigned ability byte is preserved: 129..255 look
   into neighboring table entries in the original; do not invent a clamp or
   attach semantic meaning to those values. Rank inputs outside the normal
   domain are explicit host errors, not claims about original validation.
5. Add independent Germany, Albania, Sweden, Yemen, every band boundary,
   zero/missing-manager and current-human-manager context regressions. Existing
   player-card skills and team line-strength bars do not supply these labels.

No goal2 runtime, vendor, UI, engine or backend change is part of this delivery.
No original executable/data/savestate/screenshot bytes cross repositories.

## Evidence audit of other placeholders

| Placeholder | Existing accepted or proposed evidence | Remaining gap |
| --- | --- | --- |
| Ranking top | F007/C-TEAM-01/02 establish current ranks; C-CTY-05 leaves+0x28/+0x29 unknown. TEAM displays them beside current continental/world ranks. | Establish best-rank semantics from writers and independent original bounds. |
| Strips | F002 R007 establishes three country-indexed bytes at DS:9D80; C-ALT-04's color interpretation is hypothesis. | Full TEAM palette/layout/context mapping is not an accepted decoder contract. |
| Team skills | F010/F012 and supported C-TEAM-06 establish quick-engine line sums. C-TEAM-07 explicitly leaves the panel connection unestablished. | Prove 0BC4→11E1 display division/clamp/scaling, not merely use raw sums. |
| Performance | F014 establishes individual performance words/deltas. T73's reviewed 1289/11E1 port is source evidence. | No complete accepted TEAM role-distribution/bar/context decoder finding. |
| Characteristics | F020/F021 establish the team morale aggregate, signed/wrapping behavior and display-only role.13D0 writes six aggregates. | Complete other aggregates and every descriptor/bar contract; do not extrapolate morale to all fields. |

See [follow-up #432](https://github.com/diegoami/goal2-archaeology/issues/432) for
concrete acceptance, including the existing C-CTY-05/F024 disagreement about
computer-manager selection. Existing proposed findings remain proposed; a
supported spec row or a reviewed port is recorded as that evidence type. This
audit neither claims research is absent nor silently implements other fields.

## Reproduction

```sh
/home/diego/.local/bin/python3.12 -B -m unittest tests.test_country_decoder tests.test_manager_decoder
/home/diego/.local/bin/python3.12 -B notes/428/mutations.py /tmp/T94-review-mutations-unique.json
tools/heavy.sh T94-original -- /home/diego/.local/bin/python3.12 -B notes/428/probe.py --output /tmp/T94-review-original-unique.json
```

12 tests pass (7 country / 5 manager), 11 country mutants are rejected. The original
probe checks two existing input hashes against their immutable run records and
the original build guard, runs 256 genuine country/state label pairs, six complete
original TEAM panels and four explicitly synthetic context panels, all 128 normal
country rating values and all 256 manager byte values. Every call must return
with its expected stack cleanup under its time/instruction bound. These are
isolated original-code executions, not new behavioral campaign evidence.

The private cached inputs are E010-r0001 half-time and E006-r0001 new-game
savestates at the producer's declared paths. Missing inputs are prerequisites,
not permission to skip the original comparison. Re-runs always use new output
paths. Receipts pin input, producer, helper, source and Unicorn versions.
