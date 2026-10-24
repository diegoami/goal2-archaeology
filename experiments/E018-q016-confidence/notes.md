# Q016 static notebook

## Method

Read the named view first: `seg_0791_09.c` B71C/B7FA/BA4E/BB2F,
`seg_0791_11.c` F098/F1F6, `seg_000E_05.c` 6970/6CA7,
`seg_1771_04.c` 5A03/5C60. The assembly, rather than the decompiler's
broken reconstruction of Pascal set membership, determines branches.
No DOSBox game run has been taken. After this reading, two isolated
original-routine probe batches were made, each with six fixture inputs.
The first is retained as defective (its declared slots disagree with its injected squads); the replacement checks all 240
player words. These probe B7FA, not the entire watched fixture route.

## Result-relative confidence

* `0791:B71C` calls `1771:10E7` for each country, subtracts own rating
  from opponent rating, and uses signed IDIV 32 (truncation toward zero).
  `code/seg_0791_18.asm:1012–1046`.
* Unless fixture +3 is 2 (a draw), add the absolute difference between the
  two signed score bytes for the winning side and subtract it for the loser.
  `seg_0791_18.asm:1047–1070`; helper `1771:5C60`,
  `seg_1771_08.asm:1047` onward. A draw retains the rating-difference term:
  this is not necessarily zero.
* Unless drawn, double the term if `(winner == side)` equals
  `(side == 0 or 1771:5A03(fixture))`. `seg_0791_18.asm:1071–1109`.
  The classification helper must be read in assembly: its named C output
  does not faithfully express the flags returned by set membership.
* `0791:B364` adds that signed word to the signed morale byte and clips to
  1..32. `code/seg_0791_18.asm:621` onward; named
  `seg_0791_08.c:1110–1127`.
* B7FA applies the result term to slots 1..11 and status-bit-3 bench
  participants; participating bench additionally receives draw(2)-draw(2),
  in that call order (first draw is subtracted). An unused bench player
  instead receives draw(2)-draw(4), not the result term. Empty words are
  ignored. `named/seg_0791_09.c:245–279`,
  `code/seg_0791_19.asm:9` onward.
* BA4E applies draw(4)-draw(4) independently to every word in the managed
  pool. It precedes the result term on the watched/managed route, not after
  it: F1F6 calls BA4E, then its caller 000E:6CA7 calls B7FA.
  `named/seg_0791_11.c:704–704`, `named/seg_000E_05.c:605–640`.
  Pool overlap with squad words therefore matters; clipping each call is
  not equivalent to clipping the sum once.

## Routes and temporary match morale

* F1F6 copies the squads' morale to DS:9B07[20*side+slot]. Its CB7D call
  restores those bytes after play, before pool and fixture updates.
  `named/seg_0791_11.c:662–653,678`; assembly
  `seg_0791_23.asm:1035` onward and `seg_0791_20.asm:973` onward.
  Not all in-match changes disappear: 7CC5's nonzero flag updates this
  saved array (see inventory below). Ordinary team-wide goal reactions
  use flag zero, whereas the scorer's goal call uses flag one.
* Silent quick results: 000E:6970 calls D47E, B7FA, B602, D050 in order.
  B602 then grants each selected goal scorer +1 via B364. This is after
  result clipping and is not restored on this route.
  `named/seg_000E_05.c:392–406`, `named/seg_0791_09.c:122–116`.
* Unplayed fixtures: BB2F calls fitness rolling and B364 with
  draw(2)-draw(4), without B71C. `named/seg_0791_09.c:350` onward;
  `code/seg_0791_19.asm:337` onward. The router selects this branch for
  fixture +2 = 0 on the 6E15 path (`named/seg_000E_05.c:605–612`).

## The DS:6ED4..6FF4 lead

The accesses are to a string table rooted at DS:6EB4, in 16-byte
strides, not to an expected-margin word array. The morale screen selects
a string via DS:78A3[min(morale,32)]. `named/seg_1771_03.c:881–892`.
The team panel uses the same table for its aggregates, including morale:
`named/seg_1771_02.c:73–88`. Direct references to DS:6ED4 and DS:6FF4
were not found in the named C or assembly. `strings.tsv:1195–1212`
identifies the queried range as Pascal strings, from `demoralised` through
`acceptable`. These words are descriptions, not numerical expected-margin
storage. No instruction storing to this range or table was found in the
direct/indirect table-reference sweep.

### Table readers (all references to the 6EB4 root in the code listing)

* `1771:0AF8`, manager description: `code/seg_1771_02.asm:82`
  (0B59), `named/seg_1771_01.c:551–562`.
* `1771:157D`, team panel, four descriptions: `code/seg_1771_03.asm:201,218,235,252`
  (16D1,16F7,171D,1743), `named/seg_1771_02.c:73–84`.
* The preceding player-quality text routine: `code/seg_1771_03.asm:31`
  (155D), `named/seg_1771_01.c:1054–1061`.
* `1771:42BC`, player panel, hardness/fitness/energy/morale/leadership:
  `code/seg_1771_06.asm:1048,1071,1093,1114,1142,1162`
  (447A,44B0,44DE,450A,4545,4570), `named/seg_1771_03.c:862–889`.
* Writers: none in these routines. Generic string-rendering helpers read
  the selected Pascal string; the above list enumerates their callers
  that select this table. Other nearby bases 6E92/6EBA select continent
  and home/away strings, not this confidence-description table.

## Complete direct player +0C reader/writer inventory

The named-field sweep (`morale`) was cross-checked against raw C `+ 0xc`
references and the table-root assembly sweep. Pitch record +C and stack
parameter +C are not player +C. This inventory is of semantic field
accesses; serialization and whole-record memory copies also carry the byte
unchanged, not a second confidence rule.

| Routine | Reads / writes | Listing lines |
| --- | --- | --- |
| 0791:278A | reads signed +C for the skill blend | named/seg_0791_02.c:540–549; code/seg_0791_04.asm, 27A2–27BC (F015) |
| 0791:7CC5 | reads live +C; writes clamp(s8(live)+delta,1,255); nonzero flag writes min(32,s8(new live)) to DS:9B07[side*20+slot] | named/seg_0791_06.c:610–625 |
| 0791:B364 | reads/writes signed +C, clamp1..32 | code/seg_0791_18.asm:621 onward; named/seg_0791_08.c:1118–1126 |
| 0791:CB7D | writes +C from saved DS:9B07 | code/seg_0791_20.asm:973 onward; named/seg_0791_10.c:112–83 |
| 0791:F1F6 | reads +C into saved DS:9B07 | code/seg_0791_23.asm:1035 onward; named/seg_0791_11.c:662–653 |
| 1771:13D0 | reads capped +C into team aggregate DS:9B5A | named/seg_1771_01.c:1021–1038 |
| 1771:377E | reads signed +C into player strength, special branch >=32 | named/seg_1771_03.c:308–325 |
| 1771:42BC | reads +C for description and bar | code/seg_1771_06.asm:1114–1142; named/seg_1771_03.c:881–892 |
| 1771:96D3 | writes draw(32) at player creation | named/seg_1771_06.c:1001–1006 |

### Callers that cause field or saved-field writes

* B364: B602 goal scorer (+1; `named/seg_0791_09.c:130–112`),
  B7FA result/bench (`code/seg_0791_19.asm:137–187`), BA4E managed
  pool (`named/seg_0791_09.c:323–312`), BB2F unplayed fixture
  (`named/seg_0791_09.c:366` onward).
* 7CC5: 6443 scorer with flag one (`named/seg_0791_05.c:543–545`);
  65FE team-wide goal reaction with flag zero (`:628–643`);
  card/removal paths 7A9D and 7D56 (`named/seg_0791_06.c:565–572,656`).
  Cards/injuries are not inferred here, but their field writer is named.
* 96D3 is reached by creation and retirement/replacement (F007/F016);
  it is not a post-match result-relative update.
* CB7D is called by F1F6 after the summary (`named/seg_0791_11.c:704`).

### B71C's term outside player +0C (for T33)

B71C's term is also consumed by 0791:B6CC, which adds it as a signed word
to the byte [DS:A91F]+3*manager+2 and clamps the sum to -127..127
(`code/seg_0791_18.asm:979` onward, B6E9-B712). Two callers pass it:
B7FA, for each side, when neither country is managed (1771:0B77 false for
both, B81C-B82F) and fixture +2 is not 1 (B86B-B889,
`code/seg_0791_19.asm:20–66`; `named/seg_0791_09.c:240–230`); and the
000E:6E15 route after `run_match`, when its local flag is set and fixture
+2 is not 1 (`named/seg_000E_05.c:614–624`). 1771:63A4 later folds that
byte into the manager byte +1 and clears it (annotation row, F017). This
is a manager/country quantity, not player confidence; its meaning for
team morale is T33's question and is not established here.

### What can be predicted from before state and score alone

The B71C term is exact from the country rank bytes and fixture result.
B7FA's bench effect is exactly given its two bounded draws, otherwise the
sets returned by `participant_values`. The complete watched before/after
byte is **not determined by score alone**: 6443 persists the scorer's
current live form through 7CC5, including earlier temporary goal reactions.
`match_form` represents these operations exactly when the event order is
given; pool/unused/participating bench draws remain named draws. Reading
the saved array after play is enough for the subsequent result update,
but is not equivalent to the kickoff byte. No event stream was invented
for the E015 sitting.

## Available human records

`experiments/E015-human-playthrough/README.md:55–65` identifies all three
records as extractions of the same four-state scripted sitting. The first
two are superseded by r0003. These are not yet established before/after
played-match pairs; none has been used as a confidence comparison.
