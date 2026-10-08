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

## Probe records and limits

`probe_watched.py` uses the released E011 half-time state, SHA-256
`092f5f74bc5dc0c0f133709ca46be04122d3813a716c54fd23a686e9194ab9ff`.
It reads counter inputs at 8C35, form-delta inputs at 7CE3 and injury stores at
7D9B, and audits writes to the two squads' +0xC/+0xD/+0xE. The model starts
from every squad player word's initial record, replays the input operations,
and compares all three final bytes for each word. It does not use an observed
energy value to decide a decrement or discard bench players. This is a replay
of field-write inputs, **not** an independent movement/tactic simulator.

The immutable `watched-half-001.log` records a failed attempt (the initial
Unicorn memory-hook callback omitted its access-type argument). The second
attempt's `records/watched-half-002.json` contains 40 player comparisons,
184 activity tails and 182 actual decrement stores at 8C54; no unknown field
stores and no skipped wait-family calls. Its final clock is 91, with 2077 ticks.
On that record alone the checker returned `match: 40/40` before the recovery
records were added. The recording omits the terminal CS:IP, so the final clock
is evidence of progress but not a separately asserted terminal-address check.

`probe_recovery.py` runs original 1771:3651 on eight declared literal records
in the same hash-verified guest image. It records every final +0xC/+0xD/+0xE;
the original executable, not the model, supplies the expected bytes and caps.
No DOSBox-X game runs or E015 sitting records are used by these probes.

The immutable `records/recovery-001.json` has an input-transcript defect:
the initial recorder hooked 214B:06B1 only. **06D0 calls 0688 directly**, not
06B1 (`static/goal-exe/code/seg_214B_01.asm:913–935`, 06D0–06F7), so its healing
draw is absent even though the final expected bytes are recorded. Reading that
listing led to the corrected 0688 hook, whose independent repeat is retained
as `records/recovery-002.json`. Neither record is overwritten. The experiment's
README and `supersessions.json` declare the incomplete first capture superseded
by the complete repeat. The checker prints this declaration and rejects a
missing successor; it does not retroactively supply the omitted input or infer
the missing draw from an expected energy byte.

## Unestablished coverage

`inventory.py` enumerates candidate listing accesses whose routine loads the
player-array pointer. It does not prove that each access uses that pointer:
pitch +0xD is a player word, pitch +0xC is a movement byte, and scorer-table
words at +0xC/+0xE also appear in this candidate set. An exhaustive semantic
reader/writer inventory, the pre-half energy-set check at 9A32, year-end paths,
marking's effect on activity, and substitution's energy semantics are not
established by this map. No F018 finding or settled field annotations follow
from the partial inventory.
