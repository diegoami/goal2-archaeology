# F037 TEAM performance bars sum a match side's performance words by role, after the first in-match menu

- **Status**: proposed.
- **Question**: #432 / T115: what the four TEAM "performance" bars show, which players and words they aggregate, how roles are grouped, when they are drawn, and how they render.
- **Artifact**: goal2-a949da2f listings; genuine screens of goal2-67cf27d6 (same code and data, F035).
- **Method**: static first: TEAM `1771:157D`'s gate before `1289`, then `1289` itself and its tail call of `11E1` (F036), the role table `DS:0D7C`, the gate bytes `DS:0C1E`/`DS:0C1F` (F031) and the side words `DS:9B34`/`DS:9B36`. The performance word encodings are F014's. The callers `1981` and `26B9` say where the panel is reached. The reading answers the question; runs corroborate it. Corroboration follows F036: genuine DOSBox-X screens of the owner's sitting E015-r0007, each paired by its run record's digest with its snapshot, and unmodified original routines under Unicorn on genuine states. Synthetic controls are labelled.
- **Intervention**: none for the genuine screens. Original calls use synthetic frames and a scratch screen buffer, with no behaviour hooks, each bounded to 2 seconds and 500000 instructions. Synthetic controls edit a private copied machine.

## Answer

- **Gate**: 157D calls 1289 only when the bytes `DS:0C1E` (a fixture is set up) and `DS:0C1F` (the in-match menu has been left once) are both nonzero. Otherwise rows 20..23 keep the template: 25 `■` cells each, no highlight, and nothing is computed. F031 has 0C1F clear outside matches and during a match's first (pre-match) visit of the in-match menu, so the bars appear from the first return to the in-match menu onwards. The panel is reached from the main menu (`T`, the managed country), the country list (26B9) and the in-match menu (1981, either side). Only the in-match path normally has both bytes set. static:static/goal-exe/code/seg_1771_03.asm:402 static:static/goal-exe/code/seg_1771_03.asm:415 static:findings/F031-the-squad-and-the-pool-exchange-except-from-a-countrys-first-finals-group-fixture-to-the-next-qualifying-build-and-between-two-away-cross-continent-friendlies.md:1

- **Side**: 1289's argument is 1 when `DS:9B36` equals the panel's country, else 0, and 1289 reads team `DS:9B34+2*side`. A panel country outside the match therefore shows match side 0's bars, not its own and not empty. Normal play reaches the panel in a match only for the two sides. The country-list path would show it, but only if the gate were open there. static:static/goal-exe/code/seg_1771_03.asm:406 static:static/goal-exe/code/seg_1771_02.asm:883

- **Aggregation**: 1289 zeroes `DS:9B45..9B54` (both sides' four words). For each squad slot 1..11 of that team it reads the slot's word with no zero-word or availability test, so a zero word reads player 0. It takes the player's `+0x12` word p and forms `v = p - 0x37`; v is reduced by 10000 when signed above 5000, then increased by 100 (all 16-bit). A starter's fresh 0x37 and a substitute's 10000+0x37 both give 100; a goal (+40) gives 140; the blank 0x7FFF gives 22812. The threshold applies after the subtraction, unlike the 3827/CAB0 readers, which differ for raw 5001..5055. The call to 3A82 in the loop has no effect: its result is stored and never read, and the routine writes nothing. static:static/goal-exe/code/seg_1771_02.asm:871 static:static/goal-exe/code/seg_1771_02.asm:921 static:static/goal-exe/code/seg_1771_02.asm:924 static:static/goal-exe/code/seg_1771_02.asm:928 static:findings/F014-performance-ratings-and-man-of-the-match.md:28

- **Role grouping**: role `DS:0D7C[+6]` equals 0D4E's line for positions 0..13 (keeper 0, defence 1, midfield 2, attack 3, 4 defence and midfield, 5 midfield and attack), but it is a separate table. Roles 0..3 take v. Roles 4 and 5 add v idiv 2 (signed, truncating) to both lines k-3 and k-2. This is the signed counterpart of 0BC4's unsigned halving. Positions 14 and 15 give 29 and 31, outside the four words. static:static/goal-exe/code/seg_1771_02.asm:944 static:static/goal-exe/code/seg_1771_02.asm:959 static:static/goal-exe/data/ds_2581_01.hex:115

- **Rendering**: 1289 ends with `11E1(20)` (F036): the keeper is undivided, the others idiv 4, all clamped 1..256, and `v*25 idiv 256` cells from column 10 of rows 20..23 get attribute 0x70. static:static/goal-exe/code/seg_1771_02.asm:993

- **Genuine screens agree exactly.** On E015-r0007's eleven country-selection screens the gate is closed (0C1E = 0C1F = 0): no highlight, decoder None. Four of those screens are stale (F036) and are compared against re-renders. On eight in-match friendly screens (sides 29 and 16) Italy is side 1 with role sums 99/497/600/204 and cells 9/12/14/4. Those sums include a substitute's 10055 word decoding to 100 and a keeper at 99. static:notes/432/performance/original-r2.json:1 E015-r0007

- **Original renders agree on every country of 17 genuine states**: E006-r0001 and two country-selection snapshots (snap-0003, snap-0009) with the gate closed, and E010-r0001..r0010, E011-r0001 (watch start and half time) and two in-match snapshots (snap-0120, snap-0128) with it open: 3 closed, 14 open. Every non-participant country shows side 0's bars, as decoded. static:notes/432/performance/original-r2.json:1 E006-r0001 E010-r0001 E011-r0001

- **Synthetic controls**: every 0C1E/0C1F pair of {0, 1, 255}, with 9B36 set to, away from and to zero against the panel country (Germany, 12). 3000 seeded squads with boundary and random words over the whole 16-bit range and positions 0..13. 608 hybrid controls put odd negative halves exactly on a 25/256 cell boundary, where truncation is visible. All equal the decoder. r1 lacked the hybrid controls, and a floor-for-truncation mutant passed it; r2 adds them and rejects it. The decoder's 8 tests fail before it exists, and 18 mutants are rejected. static:notes/432/performance/original-r1.json:1 static:notes/432/performance/mutations-r1.json:1 static:tests/test_team_performance_decoder.py:1

## Producer provenance qualification

The producer named by `notes/432/performance/original-r1.json`, SHA256
`6aaf590227c1cb8bbc2885f99291f811f63cafe1b2bf8f6364829742d59d558b`, was not committed
in the tracked history. It has not been recovered. r1 is retained unchanged as historical
output; its source cannot be reproduced/audited from this repository. The statement above
that its floor-for-truncation mutant passed is a historical report, not independently
reproducible evidence from a tracked r1 producer.

The operative superseding original comparison is **original-r2.json**. Its producer SHA256
`24270dfd33ef065b1fee4635d2a464ec744de7045cb32ce5d13426f67034a0e4` matches
`notes/432/performance/probe.py` at commit `b3e6fe7fd20fa797ded568c025229f306ca0180a`.
It includes the hybrid-half controls absent from r1. No r1 producer was reconstructed by
editing r2, and no old receipt was changed. This qualifies the evidence trail without
changing the supported decoder rule. Review follow-up #573.

## Alternatives and limits

1. **"Performance" is the panel country's own team at all times, or a mean over the eleven.** It is a sum by role, scaled by 11E1, and it belongs to the match side chosen as above.
2. **Blank or absent players are skipped.** Every slot counts, the 0x7FFF blank included; it shows a large value, clamped to the full bar.
3. **The bars are empty (zero) outside a match.** Outside the gate nothing is drawn: no highlight at all, not computed zero bars.

Not established: a genuine state with 0C1E set and 0C1F clear (the pre-match visit). It is covered statically (F031) and by synthetic gate controls only; no published snapshot holds one. Positions whose role byte exceeds 5 are refused by the decoder (the original writes outside the four words). Whether a natural state ever shows a non-participant's panel with the gate open is not claimed.

## Inferences

- goal2 draws the performance rows only when its state corresponds to both gate bytes set, for the side chosen against DS:9B36. It reads the eleven squad words of that side's country record, their players' +0x12 and +6, and the pinned role table, through `team_performance`. When the result is None it leaves the template unhighlighted. static:runtime/decoders/team_performance.py:1 static:docs/requests/432-team-panels.md:1
