# Q015 static reading

## Method and limits

Read the named view first (`seg_0791_07.c`, `seg_0791_10.c`,
`seg_1771_03.c`, and the fixture-update callers in `seg_0791_09.c`),
then checked the instruction listings below. No game runs have been taken.
This is an initial map, not an exhaustive reader/writer inventory or a finding.
In particular, the activity counter's upstream writers, substitution paths,
year-end paths and all +0xC readers/writers still need examination.

## Writes checked against the listing

| Path | Listing | Exact operation |
| --- | --- | --- |
| Watched player update | `static/goal-exe/code/seg_0791_14.asm:1060–1073`, 8C35–8C5D | If DS:8325 is nonzero and the pitch record's unsigned word +0x14 is **greater than** 180, decrement the player's +0xE only if its signed byte is greater than 1; reset the pitch counter to zero even when the decrement is suppressed. |
| Quick engine's slot loop | `static/goal-exe/code/seg_0791_21.asm:1165–1187`, DA8D–DAC9 | When unsigned DS:831B modulo 5 is zero, obtain the player word from pitch +0xD and decrement player +0xE only if its signed byte is greater than 1. Loop covers pitch slots 1 through 22. No role or marking test occurs at this write. |
| Post-match restoration, 0791:CB7D | `static/goal-exe/code/seg_0791_20.asm:1010–1041`, CBD2–CC27 | For nonzero squad words on both match sides, copy DS:9B07[side*20+slot] into +0xC, then copy +0xD to +0xE only if signed +0xE is greater than zero. Slots 1 through 20. This is not a fixed increment or a clamp to 32. |

The watched increment seen in the named view (`seg_0791_07.c:161–179`)
is `pitch[+0x14] += (pitch[+0xF] < 5)`; it is not yet a proof that the
help file's man-marking comparison holds, because the movement and tactic
paths that supply pitch +0xF must also be read.

## Recovery routine checked in assembly

The named view of 1771:3651 (`seg_1771_03.c:245–290`) indicates:

- injured (+0xE exactly zero): signed fitness + rand(2) - rand(8);
- otherwise flag zero: signed fitness + rand(2) - rand(3), plus one if
  the intermediate signed word is below 16;
- otherwise flag nonzero: signed fitness + rand(8) - rand(2);
- lower bound 1, upper bound DS:0E84[age > peak_age+3];
- store fitness; restore energy from fitness when signed energy is positive,
  otherwise only after the rand-is-one(3) draw succeeds.

These are draw-dependent operations, not constants. The assembly confirms the
branches and order (`static/goal-exe/code/seg_1771_05.asm:647–757`,
366B–3774). Draw order is rand(2), rand(8) in both the injured and flag-nonzero
branches, and rand(3), rand(2) in the flag-zero branch. Fitness is sign-extended
at 3672. The intermediate fits a signed word for every possible input byte
and legal draw; no word wrapping occurs. Lower clamping bypasses the upper
clamp (36E6–36EB), rather than applying both in sequence.
Fixture update 0791:B7FA and managed pool update 0791:BA4E call this routine
or 1771:3558, selected by 1771:5A8F (`seg_0791_09.c:226–260,293–303`).
1771:3558 sets energy before the final fitness lower clamp in the named view
(`seg_1771_03.c:234–239`); treating the two bytes as always equal would lose
that ordering edge.

## Baseline verification

The released `goal2-a949da2f` artifact verified by hash. Regenerating the
unmodified annotations with `decompile.sh --annotations` reproduced every
committed named-view file byte for byte (`diff -qr` returned zero).
