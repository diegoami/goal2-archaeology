# Request #400: retained-source reassessment (T91)

**No new qualifying input and no guest execution.** The retained-source assessment
supports stopping at this checkpoint. [#400](https://github.com/diegoami/goal2-archaeology/issues/400)
remains open for CC7B role3 penalty, role4 shooting-range free kick, E022/E062 no-player
and EA09/EC60 first-eleven vacancy. T88/PR405 and T89/PR407 remain the positive
corner/goal-kick/CF3A/E19F deliveries. F029/F030 retain their proposed status.

The owner's scoped worktree exception was used: `task/T91-400-static-reassessment`
in `/tmp/goal2-archaeology-400-next`, based on fetched main
`bb971ac5fcbcfb3247a62709c56e4d8a2e68ecfa`. T91 was free in main and remote branch
names when allocated. All pre-existing checkouts and reviews were preserved. No heavy
job or guest was launched; no extra-slot waiver was used or carried forward.

## Static gates and what original controls can establish

This is a reassessment of existing readings, not a new game-rule finding or an
exhaustive reachability proof. Named routines were read first, then original listings.
The receipt pins the source files read. Existing annotations already name these gates;
no annotation or generated named file changes are claimed by this task.

- **Managed taker entry:** `0791:6D4E` calls CC7B whenever `1771:0B77` says the
  awarded side is managed (country byte +2E > 80h). It does not skip the selector
  merely because a stored taker is already valid. Role and side are low-byte arguments;
  the listing's `mov al`/`push ax` can preserve scratch high bytes. The stored pick is
  `DS:9976 + 10*side + 2*role`, updated from AX after return 6D74.
- **Stored/preferred handling and availability:** CC7B uses the current stored player
  if available and in the XI (`6B65`); otherwise `1FDD` chooses an available candidate
  by the role's skill element. `1771:3216` checks positive signed energy and status
  elements 8,6,3 clear. CC7B highlights the available stored player; without a matching
  available XI member its local pick is zero and highlight is slot1. `20E3` assigns
  takers during setup; changing the choice does not create a restart. Enter, C, Esc,
  timeout and Space/CF3A remain the existing conditional F030 contracts.
- **Role3:** the watched foul path `8206` can suppress a foul after its own-position
  `2EB8` test and coin. An accepted foul tests the ball against the fouler's own strip
  before `7EEF`; a true saved result reaches `6ECF`, then `6D4E(10,3,side)` returning
  at 6EEF. The hardness/tactic gate `4DA9` and the tackle/keeper challenge and coin
  precede this. Shootout ordering supplies none of this live managed frame chain.
- **Role4:** `6FB6` can instead use role5 for a restart in the holder's own goal area.
  `6F3E` calls `6D4E(11,4,side)` only when signed ball y times attack direction is
  at least18 and absolute signed x is at most4 (listing 6F70–6F8F, return6F92).
  Outside that range it uses the nearest player directly. The later free-kick count
  increments in either case; statistics alone cannot establish role4.
- **E062:** E022's first-selection branch obtains the actual selected word through
  DE27/DE51 and calls `214B:1765` only with the zero-word predicate, returning E062.
  An unavailable or sent-off nonzero player is a different guard. No original key
  sequence creating a zero from the inspected full sources was identified.
- **EC60:** EA09 counts actual zero XI words in `[bp-2]`. The 15-byte fill beginning
  `[bp-10h]` includes that counter. The vacancy message follows the ineligible-player,
  too-many-keepers and no-keeper checks (EB82/EBD7/EC22); the earlier checks must pass.
  A no-keeper input or a zero made by editing memory would not deliver the case.
  Existing initialization/swap/retirement reading is retained in
  [T90's vacancy note](../../notes/400-last/vacancy-path-reading.md): ordinary
  retirement installs a positive replacement before clearing the old player record.

## Retained search and actual post-setup selection

The immutable [assessment receipt](../../notes/400-reassessment/assessment-r1.json)
and [executed read-only scanner transcript](../../notes/400-reassessment/scan-r1.txt)
precede this interpretation in Git history.

- All477 decoded `runs/E*/E*-r*.json` records are byte-identical to T90's recorded
  search. No managed penalty/free-kick selector caption matched. This is a decoded-text
  search, not an exhaustive audit of all historical savestates or event timing.
- All16 T88/T89/T90 `*/steps.jsonl` groups contain1463 observations with no target
  selector caption. These overlap the earlier deliveries; they are not1463 new trials.
  T90's reviewed848-snapshot stack scan is reused, not represented as a newly expanded
  search of every raw machine frame. A caption match would still require actual CPU,
  live caller chain, manager and role/side validation.
- All17 retained E031 original .GL files were hash-checked and their actual managed
  squad words re-read: no zero slot. T89's12-core-input/100-managed-entry inventory is
  reused as prior evidence, not described as12 new examinations. Normal retirement
  therefore provides no justified shortcut to either vacancy target.
- All14 actual post-computer-setup elevens in T90's seven captain snapshots were
  re-read from native memory, including player ID, position, hardness, energy and
  status. Keeper IDs and hardness agree with the reviewed native receipt. G1A's actual
  Eire keeper is152/hardness15, rather than the saved-lineup hypothesis hardness16.
  These are real setup observations, not states immediately before a foul.

The closest already-discussed exact inputs remain G1A captain
`6731809257089157904884a54148f6f71b87a3073aaa9d433479744ba8844915`
and the same fixture's before-T core
`068a47729a3b1822ae6d3df7777eb99880bbcf74315e22098869ccaeac29ad28`.
T90 already continued the fixture. Neither identifies a new imminent foul or zero slot.
No RNG value was used to select a candidate, and no mutable goal2 code was imported.

## Importance, cost and stopping decision

The [fresh assessment on #400](https://github.com/diegoami/goal2-archaeology/issues/400#issuecomment-6388639848)
grades importance H and this read-only assessment S. One240s fixture is cheap in
isolation, but there is no distinct controlled trigger hypothesis or closer input here
that justifies another attempt. Another matchup alone is not such a hypothesis.
Repeated fixtures, a fresh campaign or a larger search need a separate owner decision.

No new executable source, legal preparation or trial is declared. Execution bound is
**zero fixtures, zero guest instructions**. The stop condition was met when the retained
search established neither a closer input nor a justified small controlled trial.
Keep the four conditional static contracts as the cheaper existing assumptions. The
risk is an unobserved original wait with incomplete live-frame and key evidence;
negative collection proves neither impossibility nor incident rates. No handler may
be removed or conditional contract promoted from this result. No remaster controls
are inferred from absence. A genuine before-event input or separately justified,
source-hashed original-key trial is needed to reopen execution.

## Reproduction and consumer boundary

T90's four original private archives were copied by full hash from their previously
verified private-download readbacks into this new worktree and extracted there. The
unchanged `python3 notes/400-last/verify.py` passed all942 observations and four
archive hashes. This is a local verified-copy reproduction, not a new Drive transfer.
T90's [clean-cache download receipt](../../notes/400-last/portable-method-r1.md)
and [private manifest](../../notes/400-last/delivery.json) remain authoritative for
actual upload/download verification. No new original payload was created; none is
committed or uploaded publicly by T91.

For an independent clean-cache reproduction, use a clean checkout of this research
head, run the first reproduction shell block in
[T90's report](400-penalty-free-kick.md), then verify every receipt hash or run the
scanner in an archive extraction that omits only the already-committed output receipt:

```sh
mkdir -p /tmp/T91-reproduce
 git archive HEAD | tar --exclude=notes/400-reassessment/assessment-r1.json -x -C /tmp/T91-reproduce
```

In that extraction, download/extract the four private packages using T90's same shell
block, then `python3 notes/400-reassessment/scan-r1.txt`. Git must be available (a clone,
remote fetch, or `GIT_DIR` pointing at this repository) for recorded collector pins.
The scanner writes once and executes no guest. Compare receipt content except `head`,
which records the checkout used for each execution; all source/scanner hashes and
observations must match. Never overwrite the committed raw assessment.

Goal2 PR378 was open at head `68d5d0786737b1e2033c466921df2ca21fb11212`
when read, already incorporating T90's limit. This task does not merge or implement
that PR. The §14 handover will cite the merged T91 head and preserve consumer Live
cells and F029/F030 proposed status in a two-file register/handover branch from latest
main. Goal2 owns its docs PR/reviewer/merge. Stop at this investigation's checkpoint;
no next task starts automatically.

The complete §14 consumer prompt and post-merge branch/checkpoint links are on
[goal2#383](https://github.com/diegoami/goal2/issues/383).
