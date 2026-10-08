# Q016 static notebook

## Method

Read the named view first: `seg_0791_09.c` B71C/B7FA/BA4E/BB2F,
`seg_0791_11.c` F098/F1F6, `seg_000E_05.c` 6970/6CA7,
`seg_1771_04.c` 5A03/5C60. The assembly, rather than the decompiler's
broken reconstruction of Pascal set membership, determines branches.
No game run has been taken.

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
  ignored. `named/seg_0791_09.c:218–278`,
  `code/seg_0791_19.asm:9` onward.
* BA4E applies draw(4)-draw(4) independently to every word in the managed
  pool. It precedes the result term on the watched/managed route, not after
  it: F1F6 calls BA4E, then its caller 000E:6CA7 calls B7FA.
  `named/seg_0791_11.c:674–700`, `named/seg_000E_05.c:605–640`.
  Pool overlap with squad words therefore matters; clipping each call is
  not equivalent to clipping the sum once.

## Routes and temporary match morale

* F1F6 copies the squads' morale to DS:9B07[20*side+slot]. Its CB7D call
  restores those bytes after play, before pool and fixture updates.
  `named/seg_0791_11.c:632–649,674`; assembly
  `seg_0791_23.asm:1035` onward and `seg_0791_20.asm:973` onward.
  In-match confidence changes must not be counted as permanent changes.
* Silent quick results: 000E:6970 calls D47E, B7FA, B602, D050 in order.
  B602 then grants each selected goal scorer +1 via B364. This is after
  result clipping and is not restored on this route.
  `named/seg_000E_05.c:392–406`, `named/seg_0791_09.c:96–116`.
* Unplayed fixtures: BB2F calls fitness rolling and B364 with
  draw(2)-draw(4), without B71C. `named/seg_0791_09.c:323` onward;
  `code/seg_0791_19.asm:337` onward. The router selects this branch for
  fixture +2 = 0 on the 6E15 path (`named/seg_000E_05.c:605–612`).

## The DS:6ED4..6FF4 lead

The accesses found are to a string table rooted at DS:6EB4, in 16-byte
strides, not to an expected-margin word array. The morale screen selects
a string via DS:78A3[min(morale,32)]. `named/seg_1771_03.c:881–892`.
The team panel uses the same table for its aggregates, including morale:
`named/seg_1771_02.c:73–88`. Direct references to DS:6ED4 and DS:6FF4
were not found in the named C or assembly. The table's indirect readers
and the complete player-field inventory still require enumeration before
this notebook can support the Done-when inventory claim.

## Available human records

`experiments/E015-human-playthrough/README.md:55–65` identifies all three
records as extractions of the same four-state scripted sitting. The first
two are superseded by r0003. These are not yet established before/after
played-match pairs; none has been used as a confidence comparison.
