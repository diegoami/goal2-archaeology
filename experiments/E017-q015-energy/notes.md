# Q015 static reading

## Method and limits

Read the named view first (`seg_0791_07.c`, `seg_0791_10.c`,
`seg_1771_03.c`, and the fixture-update callers in `seg_0791_09.c`),
then checked the instruction listings below. No game runs have been taken.
The inventory below separates player records from pitch and other records.
The byte-write model replays instruction inputs; it is not a movement simulator
or a model of Q016/Q017's morale outcomes.

## Writes checked against the listing

| Path | Listing | Exact operation |
| --- | --- | --- |
| Watched player update | `static/goal-exe/code/seg_0791_14.asm:1060–1073`, 8C35–8C5D | If DS:8325 is nonzero and the pitch record's unsigned word +0x14 is **greater than** 180, decrement the player's +0xE only if its signed byte is greater than 1; reset the pitch counter to zero even when the decrement is suppressed. |
| Quick engine's slot loop | `static/goal-exe/code/seg_0791_21.asm:1165–1187`, DA8D–DAC9 | When unsigned DS:831B modulo 5 is zero, obtain the player word from pitch +0xD and decrement player +0xE only if its signed byte is greater than 1. Loop covers pitch slots 1 through 22. No role or marking test occurs at this write. |
| Post-match restoration, 0791:CB7D | `static/goal-exe/code/seg_0791_20.asm:1010–1041`, CBD2–CC27 | For nonzero squad words on both match sides, copy DS:9B07[side*20+slot] into +0xC, then copy +0xD to +0xE only if signed +0xE is greater than zero. Slots 1 through 20. This is not a fixed increment or a clamp to 32. |

The watched increment seen in the named view (`seg_0791_07.c:161–179`)
is `pitch[+0x14] += (pitch[+0xF] < 5)`. The movement and tactic analysis below
explains why this does not prove an unconditional man-marking penalty.

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

## Reader/writer inventory

`python3 experiments/E017-q015-energy/inventory.py` enumerates **all** direct
`es:[di + 0xc|0xd|0xe]` and `add di, 0xc|0xd|0xe` occurrences in `code/`,
including routines without a player-array load. The following tables classify
that entire output. Line numbers are physical lines of the named **assembly**
file under `static/goal-exe/code/`, not C line numbers. R/W includes comparisons
as reads. Bulk saves, loads and swaps of whole records are not field arithmetic.

A player pointer is `[DS:A91B] + 20 * player_word`. A pitch pointer is the
far argument used by the watched handlers, or `DS:80E8 + 22 * pitch_slot`.
Pitch +0xD is a **word index**, not player fitness. The particularly important
rebase is shown at 2790–27A5 (`seg_0791_04.asm:851–858`), 8AEF–8B04
(`seg_0791_14.asm:897–904`) and DA9F–DAB4
(`seg_0791_21.asm:1173–1180`). Reloading the pitch argument after such a
rebase makes later +0xC accesses movement accesses again, not morale writes.

### Actual player accesses (complete direct-field inventory)

| Routine | Assembly file and lines (field R/W) | Pointer provenance / operation |
| --- | --- | --- |
| 0791:278A | seg_0791_04.asm:860,863 (+C R),878 (+E R) | pitch +D word, multiply 20, A91B, saved far pointer; signed morale/energy skill blend (F015) |
| 0791:2B7B | seg_0791_05.asm:220 (+E R) | argument pitch +D -> A91B+20*w, lines 214–219; random-is-one(33-s8(E)) |
| 0791:4A28 | seg_0791_08.asm:561 (+E R) | saved player pointer from pitch word (462 onward); signed E compared with rand(6) at 4B04–4B12 before following a marking target |
| 0791:5049 | seg_0791_09.asm:353 (+E R) | pitch argument reloaded at 346–348; A91B+20*w at 349–352; signed E/2 supplies random-is-one bound (353–361) |
| 0791:7CC5 | seg_0791_13.asm:496,514 (+C R),510 (+C W) | pitch word -> saved A91B+20*w, 487–494; s8(C)+argument in a word, clamp 1..255, store; optional read for line sums (F012) |
| 0791:7D56 | seg_0791_13.asm:587 (+E W) | pitch +D -> A91B+20*w, 582–586; injury store E=0; injury cause not in Q015 |
| 0791:8062 | seg_0791_13.asm:1019 (+E R) | pitch +D -> A91B+20*w, 1002 onward; zero test in substitution/injury checks |
| 0791:8AE9 | seg_0791_14.asm:1066 (+E R),1069 (+E W) | saved player pointer 897–904; decrement when s8(E)>1; counter reset is on the pitch argument |
| 0791:9A32 | seg_0791_16.asm:370 (+E R),378 (+E W) | 22 pitch slots, +D -> A91B+20*w, 354–368; set membership then add 2 |
| 0791:B364 | seg_0791_18.asm:634 (+C R),650 (+C W) | argument player word -> A91B+20*w, 626–632; signed C+delta, clamp 1..32; callers' delta outcomes belong to Q016/Q017 |
| 0791:C88D | seg_0791_20.asm:687 (+E R) | outgoing country squad word -> A91B+20*w; signed E<1 in forced removal guard |
| 0791:CB7D | seg_0791_20.asm:1026 (+C W),1028 (+E R),1031 (+D R),1033 (+E W) | squad word -> A91B+20*w; restore shadow C; copy D to E only for positive signed E |
| 0791:D733 | seg_0791_21.asm:1181 (+E R),1184 (+E W) | pitch +D -> A91B+20*w; signed E>1 decrement on minute modulo 5=0 |
| 0791:F1F6 | seg_0791_23.asm:1101 (+C R) | nonzero squad word -> A91B+20*w, 1092–1100; pre-match shadow copy to 9B07 (1110) |
| 1771:13D0 | seg_1771_02.asm:1046 (+C R),1058,1075 (+E R),1061 (+D R) | eligible squad word -> saved A91B+20*w, 1034–1044; team bars, signed sums |
| 1771:2E20 | seg_1771_04.asm:903 (+E R) | argument word -> A91B+20*w; zero test for injured display colour |
| 1771:3216 | seg_1771_05.asm:201 (+E R) | argument word -> A91B+20*w, 193–199; signed E<1 means unavailable before status-bit tests |
| 1771:3558 | seg_1771_05.asm:594,613,619,629 (+D W),616,622,626 (+D R),624 (+E W) | argument word -> saved A91B+20*w; random redraw described below |
| 1771:3651 | seg_1771_05.asm:648,755 (+D R),744 (+D W),652,746 (+E R),757 (+E W) | argument word -> saved A91B+20*w, 640–646; draw-dependent recovery described above |
| 1771:377E | seg_1771_05.asm:785 (+E R),795,805 (+C R) | argument word -> A91B+20*w; signed energy and morale in displayed effective ability |
| 1771:42BC | seg_1771_06.asm:1060,1063,1106,1192,1214,1354 (+E R),1085,1199 (+D R),1126,1174,1181 (+C R) | saved A91B+20*argument word; words/bars and tactics panel; the row at y=20 uses D unless E=0, y=21 uses E, y=22 uses C |
| 1771:96D3 | seg_1771_13.asm:1190 (+C W) | saved A91B+20*argument player word; rand(32) morale; calls 3558 for D/E at 1196 |

### Pitch accesses in that same exhaustive scan (not player fields)

Each row gives every +C/D/E occurrence in its routine. `D word R` means the
pitch record's player index, including a push of that index. C is a movement
offset. The base is the pitch far argument unless explicitly shown otherwise.

| Routine | Assembly file:lines | Classification |
| --- | --- | --- |
| 0791:1E53 | seg_0791_03.asm:972 | D word R |
| 0791:1FDD | seg_0791_04.asm:58,105 | D word R |
| 0791:26D7 | seg_0791_04.asm:793,806 | D word R; only the subsequent +F accesses are on players |
| 0791:278A | seg_0791_04.asm:852,883 | D word R; distinct from its actual player accesses above |
| 0791:2956 | seg_0791_04.asm:1058 | D word R |
| 0791:2B7B | seg_0791_05.asm:215 | D word R |
| 0791:2F28 | seg_0791_05.asm:757 | D word R |
| 0791:3D38 | seg_0791_07.asm:46,59 | D word R |
| 0791:419C | seg_0791_07.asm:612 | D word R |
| 0791:42CB | seg_0791_07.asm:701 | D word R |
| 0791:4354 | seg_0791_07.asm:767,809,821 | D word R, C byte R; pitch pointer reloaded at 808,820 |
| 0791:4438 | seg_0791_07.asm:865 | D word R |
| 0791:4532 | seg_0791_07.asm:1010 | C byte R |
| 0791:4649 | seg_0791_08.asm:52,112 | C byte R, D word R |
| 0791:474D | seg_0791_08.asm:144,164,170 | D word R, C byte R/W; reload argument after player-position test, 163,169 |
| 0791:4A28 | seg_0791_08.asm:462 | D word R |
| 0791:4B64 | seg_0791_08.asm:650,673,686,700,741,759,797,799 | D word R, C byte W / pointer to C passed to clamp; argument is reloaded, e.g. 4C94,4CD9; not saved player pointer |
| 0791:4DA9 | seg_0791_08.asm:884,916 | D word R |
| 0791:4E28 | seg_0791_08.asm:943 | D word R |
| 0791:5049 | seg_0791_09.asm:218,257,348 | D word R |
| 0791:5565 | seg_0791_09.asm:783 | D word R |
| 0791:57AC | seg_0791_09.asm:960 | D word R |
| 0791:6443 | seg_0791_11.asm:145,158 | D word R |
| 0791:69BD | seg_0791_11.asm:784,794,796 | D word R, C byte W/R; reloaded argument at 793,795 after reading player position |
| 0791:74C2 | seg_0791_12.asm:977,987,1007,1028 | D word R |
| 0791:798D | seg_0791_13.asm:119,171,183 | D word R |
| 0791:7B77 | seg_0791_13.asm:334,370,443 | D word R |
| 0791:7CC5 | seg_0791_13.asm:488 | D word R |
| 0791:7D56 | seg_0791_13.asm:582,617 | D word R |
| 0791:7EEF | seg_0791_13.asm:756 | D word R |
| 0791:8062 | seg_0791_13.asm:1002 | D word R |
| 0791:86D0 | seg_0791_14.asm:543 | D word R |
| 0791:8AE9 | seg_0791_14.asm:898 | D word R |
| 0791:9A32 | seg_0791_16.asm:362 | D word R; DS:80E8+22*slot |
| 0791:9B93 | seg_0791_16.asm:672 | D word R |
| 0791:A260 | seg_0791_17.asm:38,40,53 | D word W/R; assignment from country squad, 29–38 |
| 0791:C5DC | seg_0791_20.asm:400,459,497,506,513 | D word R on DS:80E8+22*slot, 390–396 |
| 0791:D5C1 | seg_0791_21.asm:762 | D word R |
| 0791:D733 | seg_0791_21.asm:1173 | D word R; DS:80E8+22*slot |

### Other records in the scan

| Routine | Assembly file:lines | Base / classification |
| --- | --- | --- |
| 000E:6685 | seg_000E_08.asm:651,654,691 | A93F scorer record, built at 642–649; +E player word and +C goal-count word R |
| 0791:83A2 | seg_0791_14.asm:117,133 | passed ball record; +D control byte R/W, not fitness (movement timer is +A, lines 111–114) |
| 0791:8F10 | seg_0791_15.asm:317 | passed ball record +D R |
| 0791:A375 | seg_0791_17.asm:132,134 | C,D byte W on passed ball object (match setup caller named/seg_0791_08.c:436); not player fitness |
| 0791:B3B7 | seg_0791_18.asm:699,817,859,884 | saved scorer pointer A93F+96*category+16*entry-112 (692–697); +E word R/W, +C word R/W; player pointer saved separately at 665–666 |
| 1771:1B2E | seg_1771_03.asm:829 | caps/goals historical table A937/A93B, 14-byte entry; +C word W (named/seg_1771_02.c:232–256) |
| 1771:1D5C | seg_1771_03.asm:1606,1637,1774,1805 | historical goals/caps table pointers A93B/A937; +C word R, not morale |
| 1771:2D15 | seg_1771_04.asm:859 | manager record at A923+manager; +D byte W (rating), construction 854–858 |
| 1771:63A4 | seg_1771_09.asm:851,870 | manager record at saved A923 plus manager-128, 845–850 / 864–869; +D byte R/W |
| 1771:883F | seg_1771_12.asm:843,878 | A93F scorer-table entry; +E,+C word R (named/seg_1771_06.c:297–315) |
| 2382:0391 | seg_2382_01.asm:291 | runtime object far pointer at +C (LES), not byte arithmetic |
| 23E4:15F1 | seg_23E4_03.asm:79 | runtime object far pointer at +C (LES) |
| 23E4:1631 | seg_23E4_03.asm:113 | runtime object far pointer at +C (LES) |
| 23E4:1664 | seg_23E4_03.asm:152 | runtime object far pointer at +C (LES) |

### Field identities, activity and the help claims

Fitness is +D; energy is +E. The screen proves this independently of identical
new-game bytes: 42BC reads +D for the fitness row unless +E=0 (injured), then
reads +E for the energy row; assembly `seg_1771_06.asm:1060–1118,1192–1229`.
3558/3651 establish D as the persistent recovery baseline and E as the
in-match expendable byte; the decrement routines never write D.

`DS:7624` is **not a per-match energy array**: `strings.tsv:1307` identifies
2581:7624 as the Pascal string "very tired", in the 16-byte word-string table
based at 6EB4. The screen indexes that table through 78D5/78F6, not by changing
7624. Actual activity lives in each pitch word +14. Its complete explicit
writers are A2E6 reset (seg_0791_17.asm:113–117), 8AE9 increment (seg_0791_14.asm:
1005–1017) and 8AE9 threshold reset (1071–1073). Whole-pitch copies/sorts carry
the word along with its player; it is not a player +D word or a role-weight table.

The increment is **one per update with unsigned pitch +F < 5**, not distance,
speed or a man-marking weight. 8889 supplies +F: when already at target it writes
5; otherwise chooses an axis using a coin flip, writes 1/2 or 3/4 by the delta's
sign, and retries rejected movements with rand(5) (seg_0791_14.asm:775–886).
The handler/state and engine slot scheduler decide which updates occur. Thus
positions and tactics can affect movement and hence activity, but there is no
direct role, minutes, marking or substitution test in the decrement tail.

**Man-marker loses more? No as an unconditional arithmetic rule; an indirect
movement effect exists.** F010's 3EF8 uses country +2D element 8 for marking
words, with player +10 element 7 (Protect zone) exempt; +F overrides only tactic
elements 1..4, never marking (26D7, seg_0791_04.asm:787–835). 47C5 reads the
assigned opponent word at 4832 and, when zero, selects an eligible target by
the zone tests (seg_0791_08.asm:190–254 and named/seg_0791_04.c:23–79).
4A28 may copy that target's coordinates to pitch +7 after its energy draw and
half-pitch guard (seg_0791_08.asm:553–581; named/seg_0791_04.c:105–122).
8889 moves toward those coordinates, and 8AE9 counts active updates. This
supports an indirect activity explanation, **not** a proof that every marked
player loses strictly more than every zonal counterpart. The quick write is
identical for all 22 pitch slots; element 8 is absent from that write.

**Substitute starts full? No automatic refill at substitution.** C88D swaps
squad words, marking words and saved morale; C5DC calls A2E6 to bind the new
squad word to the pitch slot and resets pitch +14 to zero and +F to 5
(seg_0791_20.asm:490–518; seg_0791_17.asm:6–120). Neither routine writes player
D/E. The manual menu E022 also swaps squad/shadow words and calls C5DC
(named/seg_0791_10.c:969–980). The substitute therefore brings his **own current
energy**, commonly unchanged from pre-match fitness while on the bench, not a
literal 32 or newly copied D. Injury checks, removal and subsequent reordering
can alter the slot assignment, not refill the player's byte.

The shared pre-half 9A32 adds 2 to energy **1..30 only**: CS:99F2's FE FF FF 7F
has precisely bits 1..30 set (seg_0791_16.asm:339,370–378). It leaves 0,31,32
and signed-negative encodings untouched. This occurs **before** E011's team
screen half-start state, so the watched probe does not apply the increment again.

### Between-match and year-end call paths

B7FA selects 3651 when 5A8F returns nonzero, otherwise 3558. It passes flag 1
for starting XI or status bit 3 (participated), flag 0 for unused bench players
(seg_0791_19.asm:103–135,171–205); BA4E passes flag 0 for the manager's 80
pool words, with the same selector (245–301). BB2F's unplayed-match path always
calls 3558 for its squad words (named/seg_0791_09.c:320–358). The flag is an
actual caller input, not inferred by the recovery model from the final energy.

3558 redraws from B=DS:0E82[age>peak_age+4] (357B,
seg_1771_05.asm:543–550): managed player fitness is
byte(B+rand(3*B)-rand(B+1)), with the latter draw first; unmanaged is
byte(B+rand(2*B)). It clamps **signed byte** D above 32, copies D to E, then
clamps signed D below 1; hence pathological byte inputs can leave D/E unequal
(seg_1771_05.asm:550–629). 3651's arithmetic and ordered draws are above.
These routines read no marking, position +6 or elapsed-match minutes.

The year-end age pass 7FDF/7FB1/7E4A does not directly change C/D/E; computer
retirees are recreated by 7E80 -> 96D3 -> 3558, redrawing all three bytes, not
applying an annual energy-rest increment (named/seg_1771_05.c:1035–1170;
seg_1771_11.asm:870–938,1000–1120). No direct C/D/E writer is hidden in that
age pass; the above direct-field scan includes the recreation's stores.
