# F015 Keeping is read through the same derivation as the screen's bars (÷32, of any challenger in the save duel), penalties only with a +0x20 bonus — and no engine reads a stored skill

- **Status**: proposed
- **Question**: Does keeping skill matter only for a goalkeeper, and penalties only in a penalty
  shoot-out? And does the match engine read F008's three-byte derivation or a stored value?
  (Q012, `docs/backlog.md`; T27)
- **Tests claims**: F008's open inference (the screen computes the twelve skills; the engine may
  read the same derivation or store a value — this finding settles: the same derivation, ÷32);
  F013's candidate for the keeper special (a class-1 reading or a +7 = 0 guard — refuted: the
  special reads no player-record byte at all); F012's line sums (the quick engine's `gk` sum is
  ability, not a keeping skill); the backlog's Q012 hypothesis (editing an outfield player's
  keeping changes no event count; editing the keeper's changes saves — corroborated, with the
  mechanism).
- **Experiment and runs**: E013 (three watched runs from E012's start state `e006-2100-r0005`
  with one I3 edit each at the half-time stall), against E012-r0001 as the unedited baseline of
  the same start state.
- **Artifact**: set `goal2-67cf27d6`, variant none (E006's published start state via E012).
- **Max intervention**: I3 (one byte of one player record — the +4, the scale of all twelve
  skills — edited in a copy of the run's own half-time savestate and restored with Host+L
  before the second half; savestates read and written throughout, I2/I1).
- **Tier reached**: V2.
- **Confidence**: unreviewed (status `proposed`). Static: every structural claim is read from
  the listing (`static/goal-exe/code/`, the named view first) with `calls.tsv` closing the
  caller sets. Behavioural: the three E013 records, each checked by
  `experiments/E013-q012-keeping/check_keeping.py` (`match: 16/16`). Claims on one route say so.

## Answer

- **The engines read the same derivation as the player screen, through `1771:3A06`, divisor 32**
  (both). `1771:3A06(player, element)` (static:static/goal-exe/code/seg_1771_05.asm:1032) computes
  `DS:6DCD[12·(+5) + DS:6D25[12·(+7) + element]] · ((+4)+1) div 32` — the same three record
  bytes and the same two tables as the screen's `1771:3947` (F008), whose divisor is 256
  (39C1). `calls.tsv`: `3A06`'s only caller is `0791:278A`, and `3947`'s only caller is the
  player screen `1771:42BC`. No stored skill byte exists anywhere (F008), and no engine reads a
  skill except through `278A`. High confidence.
- **`0791:278A(pitch, element)` is the engines' one skill reader** (static; the runs exercise
  it): form base (`+0xC`+1 below 0x20, else 0; 27AB-27C2, **SIGNED** form byte read at 27B9
  via `cwde`), the **penalties bonus** (element ≥ 0xC adds 0x20 to the base; 27C5-27CF),
  **SIGNED** energy for other elements (27D1-27D9, sign-extended at 27D8), the `3A06` skill
  (27E6), a pitch-record halving flag (+0x13; 27F1-2802), `base·skill div 256 + skill div 4`
  (2805-281E — UNSIGNED `mul` at 2814, the product's high word discarded at 2817, UNSIGNED
  `div cx` at 281C: `((base·skill) & 0xFFFF) div 256 + skill div 4`), a **table-controlled
  keeper extra** at
  2823-284C — the FIRST gate is `cmp byte ptr [di + 0x769], 0 / jne 2843` (2826-282B): a
  non-zero byte for the element fires the extra, adding pitch +0x11, WITHOUT testing
  element 1 or event-code membership; the data image has DS:0x769[2] = 1, DS:0x769[4] = 1,
  DS:0x769[11] = 1, DS:0x769[12] = 1 (static/goal-exe/data/ds_2581_01.hex:66), so elements 2, 4,
  11 and 12 carry the extra unconditionally (element 11 corrected by T42's proof: E011-r0001's
  278A call #6682, element 11, where the original added pitch +0x11; the earlier reading listed
  2, 4 and 12 only). Only when
  the table byte is zero does the 282D-284C fallback apply (element 1 and event codes 3 and 4
  (the set CS:276A = {3, 4})) — and an `80FC` share for outfield slots (284F-286A). Its callers and their
  elements are tabulated in `experiments/E013-q012-keeping/notes.md` §2. High confidence. (static:static/goal-exe/code/seg_0791_04.asm:848)
- **Keeping is read in the watched engine's save duel, of ANY challenger — the keeper's edge is
  the class column, not a gate** (both). The "saved by X" line (template 29) is written by
  `0791:5A8E` (`5A33(·, 0x1D)`), and `5A8E` is the win branch of the duel inside `0791:5B36`
  (static:static/goal-exe/code/seg_0791_10.asm:237): `rand(278A(holder, 10))` or `rand(278A(holder, 4))` against
  `rand(278A(challenger, 1))` — the challenger's **keeping**. A goalkeeper's keeping class is 1
  (class-table row 0, column 1); every outfield position's is 7, 11 or 12, so a position-2
  defender keeps at up to ~73% of a goalkeeper's value at the same +4 — a goal-line defender
  can win a save duel. "Only the keeper keeps" is true only as "the keeper keeps best". In the
  E013/E012 records every save named the side's slot-1 keeper (players 121/372). High
  confidence.
- **The keeper special `0791:9636-9666` reads no player-record byte** (static). It runs when
  the ball-event code `DS:8327` is 0x1E (the set `CS:9544`), takes the side's **slot-1** pitch
  record (`0668[side]+1`, static:static/goal-exe/code/seg_0791_15.asm:1035), compares that record's x with the ball's
  (9646-964D) and calls `8AE9`. F013's candidate (a class-1 reading or a +7 = 0 guard) is
  refuted in both forms: "goalkeeper" there is a slot property, and the keeping read happens
  later, in `5B36`. High confidence.
- **Penalties is element 12 with a +0x20 base bonus, ranked only in the shoot-out** (static).
  The unmanaged side's five shoot-out takers are the side's best penalty takers:
  `0791:9ED3` (called only from `A10A`) fills the taker array with the side's pitch slots
  1..11 in order (the keeper IS in the array — the outer index initialises to 1 at 9F1B,
  the inner to outer+1 at 9F25-9F31, and the compare/exchange at 9F39-9FE9 covers entries
  1..11) and then sorts entries 1..11 downward by `278A(pitch, 0xC)`
  (static:static/goal-exe/code/seg_0791_16.asm:886). The managed side picks by hand: `0791:9B93` shows the player
  cards (`1771:42BC` itself, 9C5C). The kick (`A006` → `6BF1(0xA, taker)`) plays through
  the watched engine with `DS:8324` set — `5B36`'s `8324` branch rates the taker by element
  12, halved (`0x800[(8327 == 4)]`) — and `690C`'s element table `0x80C[8327]` is 12 at
  event codes 3 and 4. Outside `A10A`, penalties is read only through those table columns.
  High confidence.
- **`A10A` needs a decider fixture**: it runs only when the fixture record's +3 = 2 (a draw)
  and `DS:7C36` ≠ 0 (`0791:F0F6-F10C`), and `7C36` is set at match start from "fixture byte
  +2 is a member of the set `DS:693A` = {0x10}" (`0791:A417`). A drawn friendly ends at FULL
  TIME (E011-r0001, 1-1, no shoot-out); the E006/E012 release start states are friendlies, so
  the shoot-out arm of E013 was not run — static only for the shoot-out's internal reads. High
  confidence.
- **The I3 corroboration** (behavioural): the keeper (player 372, +4 195, +5 3, +7 0) keeps at
  `3A06` = 159; +4 edited to 0x00 at half time floors his keeping at 0 and the second half has
  **0 saves against the baseline's 3** (E013-r0001); +4 edited to 0xFF raises the value to 208
  and the second half is not the baseline replay (E013-r0002). An outfield player's (122, +4
  241→255, keeping 45→48) edit changed **no** event count — the second half is the baseline's
  own 507 lines, 0 goals, 3 saves (E013-r0003): the RNG chain advances once per `rand(n)` call
  whatever n is (F012), so a value edit changes an outcome only where it flips a comparison,
  and none flipped. The backlog's hypothesis is corroborated with its mechanism: there is no
  stored keeping byte to edit; the +4 edit shifts every derived value, and only the keeper's
  marginal goal-mouth duels flip.

## Inferences

- **The quick engine reads NO keeping** (static): its `gk` line sum is the eleven `377E`
  strengths (ability +4, form, energy; F012) routed by `DS:0D4E[+6]`; nothing under `D733`
  calls `278A`/`3A06` (calls.tsv). High confidence. (static:static/goal-exe/calls.tsv)

## Method

- Static first (U32): the named view, then the raw listing, then `calls.tsv` for the caller
  closures. What static analysis answered: everything structural above — the derivation and its
  divisor, `278A`'s blend and its callers' elements, the save duel, the keeper special's bytes,
  the quick engine's non-read, the shoot-out's reads and its fixture gate. Nothing in the runs
  was needed to place a read.
- Why runs were made (rule 19, corroboration): the derivation's ÷32 scale and the claim that a
  +4 edit moves saves only through the keeper's duels are behavioural claims about the live
  engine — a mis-read divisor or a second, stored value would have shown as a mismatch. The
  three runs edit one byte each in the run's own half-time savestate (`with_memory`, an I3
  edit) and restore it before the second half; each record keeps the edited player's 20 record
  bytes, the derivation tables `DS:6D25/6DCD` read from the same savestate (F008's hazard),
  the edit proven in guest memory after the restore, and the full commentary line log.
  `check_keeping.py` checks the predictions against the same start state's E012 baseline
  (`match: 16/16`): the exact keeping values, the first half's identity with the baseline's
  (determinism), the low edit's 0 saves, the high edit's changed half, the outfield edit's
  unchanged counts.
- Machine and tools: as E012 (Ubuntu 24.04 in WSL2, DOSBox-X 2024.03.01, `cycles=30000`,
  E004's key discipline, driver `runtime/driver/driver.py`, runner
  `experiments/E013-q012-keeping/run.py`).

## Scope and limits

- The shoot-out's own kicks were not watched (the decider-fixture gate; above): `9ED3`'s
  ranking, the `824` branch's element-12 read and `690C`'s codes-3/4 columns are static only.
- One outfield player, one match: "no comparison flipped" is this instance, not a law — the
  drawn operands do change, so another edit (or a marginal duel) can flip one.
- The energy/confidence path (Q015-Q017) and the foul path's keeper role are out of scope.
- What pitch +0x11 (the keeping extra of events 3 and 4) holds, and what writes it, was not traced.

## Where the evidence is

- `runs/E013/E013-r0001.json` … `E013-r0003.json`; the baseline is `runs/E012/E012-r0001.json`
  (start state `e006-2100-r0005`, release E006 via E012). Each run's edited half-time savestate
  (the I3 artifact itself) is published on release `E013`
  (`evidence/E013/*.manifest.json`, `tools/verify_evidence.py E013`).
- The static map: `experiments/E013-q012-keeping/notes.md`.

## Reproduction

```
bash setup/goal2-runtime.sh
python3 experiments/E013-q012-keeping/run.py edit --from-run E006-r0005 --who keeper --side 1 --to 0x00 --batch b1
python3 experiments/E013-q012-keeping/run.py edit --from-run E006-r0005 --who keeper --side 1 --to 0xFF --batch b2
python3 experiments/E013-q012-keeping/run.py edit --from-run E006-r0005 --who outfield --side 0 --to 0xFF --batch b3
python3 experiments/E013-q012-keeping/check_keeping.py
python3 tools/validate_runs.py runs/E013
```
