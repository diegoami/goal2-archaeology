# F014 The performance ratings: every commentary line adds a signed byte of the table at DS:0x720 to its named player, a completed "challenge by" nets 0, a sending-off or injury re-sorts the XI, and the man of the match is CAB0's max-scan

- **Status**: proposed
- **Question**: How are performance ratings (the player-record word at `+0x12`, F008) and the man
  of the match computed — every writer, the delta table, the encodings, the selection — such that
  a rebuild predicts them from a match's commentary lines? (Q011, `docs/backlog.md`; T26,
  milestone 2)
- **Tests claims**: the backlog's Q011; feeds the rebuild's post-match screens and the bot's team
  selection; bears on F005/F009 (the watched engine and its annotation), F008 (the field and its
  display), F012 (the substitution write and the engines' shared commentary), F013 (the pitch
  record's own +0x12 byte, distinct from this word).
- **Experiment and runs**: E012 (T26's records r0001..r0003 under `runs/E012/`, watched matches
  from E010's published start states; `experiments/E012-q011-ratings/`), the E011 half-time
  savestates' instrumented second halves (E012 notes.md §6, check 1), and E012's own instrumented
  first-half emulation `emu_firsthalf.py` (check 2).
- **Artifact**: set `goal2-a949da2f` (the E011 watchstart/half-time savestates, release assets).
- **Max intervention**: I2 (savestates read at every read; the Unicorn harness runs the original
  binary's own halves from the published savestates with the key thunk neutralised).
- **Tier reached**: V2 (`check_ratings.py` ends `match: 3/3` over the E012 records — every
  squad slot's +0x12 at half time and full time and the MoM word predicted from the line log;
  the instrumented emulated first half matches 40/40 with no invisible writer).
- **Confidence**: unreviewed (status `proposed`). Static: every claim read from
  `static/goal-exe/code/` (the named view first, then the raw listings). Behavioural: the three
  E012 records (DOSBox-X, E004's key discipline) and the Unicorn emulations of the original
  binary's own halves. Claims marked "both" have both routes; a claim on one route says so.

## Answer

- **The word and its encodings (recap, F007/F008) (both).** The performance is the word at
  `+0x12` of the 20-byte player record at `[DS:A91B] + 0x14*word`: `0x7FFF` blank, a raw rating
  (a starter begins at `0x37` = 55, `0791:F2C7` in `run_match` F1F6), or `10000 + raw` for an
  incoming substitute (written whole as `0x2747`, `0791:C6FA`); readers decode `> 5000` (signed,
  `0x1388`) → subtract `0x2710` (`1771:3855-385C`, `0791:CB2E-CB43`), and `1771:3827` maps the
  decoded value to the displayed 1..9 bucket by nine signed compares (`3865-38CF`). (static:static/goal-exe/code/seg_0791_23.asm:1122)
- **Every commentary line rates its named player (both).** `0791:1EB5` (static:static/goal-exe/code/seg_0791_03.asm:991)
  is the tail of every emitter: `call 1E53` first — `0791:1E53` computes the pitch record
  `0x80E8 + 0x16*(0668[team] + slot)`, takes its `+0xD` player word, and executes
  `add word es:[di+0x12], ax` at `1EAB` with `ax = s8(DS:0x720[template])` — then `call 1D4A`
  writes the ring line. A dedup refusal (`1C78`, the new line identical to the newest) stops the
  ring write and the counter but NOT the delta; the instrumented halves measured it: 580
  entries / 523 accepted writes / 57 refusals in the emulated first half, 550 / 507 / 43 in
  the second-half scratch — every refusal a template-6 repeat (delta 0), so no refused write
  changes a rating. A line with no player (slot ≤ 0)
  lands its delta on the dummy pitch record 0's player word — beyond the array, harmless.
- **The delta table is the 67 signed bytes at DS:0x720..0x762, indexed by template id (both).**
  Goal (38) +40, own goal (39) −50, booked (50) −20, sent off (51) −100, "wins the ball" (14)
  +20, "dodged by" (12) +20, tackle (11) −10, challenge (65) −10, substitution (0) +0, full/half
  time (63/64) 0 (E012 notes.md §3; byte-exact from `ds_2581_01.hex`, identical in every
  savestate — nothing writes it). (static:static/goal-exe/data/ds_2581_01.hex)
- **A sending-off or injury re-sorts the XI with `0791:230C`'s pairwise compare-and-swap (both).**
  A template-51 (sent off, `0791:7B77`) or template-52 (injury, `0791:7D56`) line takes its player
  off the pitch and re-sorts his side's squad slots 1..11 through `230C`: each slot's key is
  `0x0E` when `1771:3216` says so, else the record's position byte `+6` (which is not in the line
  log; the model keys a player by his starting slot, and the E012 records corroborate the keying
  since every analysed XI was already in ascending key order); for `j = 1..10`, `i = j+1..11`,
  `key[i] < key[j]` swaps the two slots fully — squad words (`2218`), the `9B07` form bytes, the
  `0x80E8` pitch records, and the keys themselves. Equal keys never swap, so the still-available
  keep their order, but every strictly smaller key does, so two removed players can REVERSE their
  original relative order (review R2's case: XI 101–111, removing 103 then 108, ends with the tail
  `108, 103`). The bench (slots 12..20) is untouched; a booking (50) re-orders nothing. The
  callers are `7B77 → C48D → C503 → 230C` and `7D56 → C88D → C503 → 230C`; the same routine also
  sorts the bench and re-points `DS:830B/830C/830D` after the sort (the established annotation
  row at `0791:230C resort_pitch_and_bench`). E012-r0002/r0003: side 1's XI ends
  ...,131,126,130 — the injured 126 then the sent-off 130, in original relative order here because
  the removals were far enough apart that no swap reversed them; side 0's sent-off 173 moves
  slot 5 → 11; the predictor matches all three records (`check_ratings.py` `match: 3/3`).
- **The man of the match is CAB0's max-scan (both).** `0791:CAB0`
  (static:static/goal-exe/code/seg_0791_20.asm:918): for side 0 then side 1, squad slots 1..20 — slots 1..11 always,
  12..20 only for players substituted off (status bit 3, `214B:0C57`) — skip `0x7FFF`, decode
  (>5000 → −10000), strict compare against a best that starts at 1, ties keeping the first in
  scan order; the winner's squad word goes to `DS:7C3A` (cleared per match by `A4A1`), and
  `0791:0106` draws it on the summary only when `DS:9A3F` is clear (a quick result shows no
  MoM). The only caller is `F1F6` at `F2F8`, after the match. Because the unavailable stay
  inside slots 1..11, a sent-off player is still scanned (a sent-off player who scored enough
  can still be the MoM).
- **The starting XI's words (both).** `F1F6`'s pre-match loop (`F234`-`F2CD`): for both sides,
  every squad slot 1..20 with a player — copy the record's `+0xC` form to
  `DS:9B07 + 0x14*side + slot` (restored by `CB7D` after the match) and set slots 1..11 to
  `0x37` (`F2C7`). `D5A9` (the silent quick result) blanks both sides to `0x7FFF`, and
  `1771:97C0` (new game) writes `0x7FFF`: a CPU-vs-CPU result carries no ratings. (static:static/goal-exe/code/seg_0791_23.asm:1065)
- **The readers (static).** `1771:3827` (the display, F008); `1771:1289`→`1301-1320` (the
  player-value calculation: `−0x37`, then `>0x1388: −0x2710`, `+0x64`); `214B:19F4` (tests bit 0
  of the word — every encoding the writers produce is odd and all but three deltas are even, a
  persistent "rated" marker); `0791:81A2` (F012's sub-readiness compare `+0x12 < 0x5A − 831B`). (static:static/goal-exe/code/seg_1771_05.asm:840)

## Inferences

- **A completed "challenge by" nets 0, not −10 (both).** `0791:5565` with `DS:8303` set emits
  `2B28(0x41)` ("challenge by", `5653`), then runs the chain `5474` (5676) → `5513` (567E) →
  `4151` (5685) → `045D(DS:830B)` (5692) → `4D3F` (56A3) → the `DS:8303` test (56A6, `jne
  56B5`) → `56CB`, which writes `add word es:[di+0x12], 0xA` at `0791:56CB` — a +10 with no
  ring line, the only ring-invisible mid-match writer. The bail paths are visible as the line
  immediately after the 0x41: `539F`'s 0x0E/0x21 pair (`5465`/`5468`), `408E`'s 0x16-0x18,
  `8206`'s 0x35-0x37, `3FAD(9)`'s 0x15. The ONE silent bail is `045D(DS:830B)` at
  `5692-5697`: `045D` (seg_0791_01.asm:511) returns 1 when its argument — the HOLDER's pitch
  slot, `DS:830B` — is 1 or 12, i.e. when the ball holder stands on a side's slot 1 (pitch
  slots 1 and 12 are the two keepers' slots; `0668 = [0x0B, 0x00]`: team 0 plays pitch 12..22,
  team 1 plays 1..11), and the `jne 56D0` skips 56CB without emitting anything. `4D3F` at
  `56A3` is NOT a bail: its return is never tested — `56A6`'s `cmp byte [0x8303],0` is the
  next branch — so a goalkeeper CHALLENGER still gets the +10 (T26 rework R1 removed the
  earlier claim that it does not). E012-r0001's positions 294-297 show both outcomes: a
  completed challenge (123: followed by another player's 0x41; +10 on the read — slot 3 read
  0x8C where the plain table gives 0x82) and a bailed one (124: followed by the 0x0E/0x21 pair
  naming 124; the plain −10). `5B36` can also emit 0x41 with 8303 set (`5B88`) without the +10;
  no 5B36-emitted 0x41 appeared in any analysed half — the rule's one recorded ambiguity.

## Evidence

- `experiments/E012-q011-ratings/notes.md` — the static map, claim by claim with listing lines;
  the writers (§4), the readers and CAB0 (§5), the rule (§6), the runs (§7).
- `runs/E012/E012-r000{1,2,3}.json` — watched matches from E010's published start states
  (e006-2100-r0005, e006-1001-r0002; r0003 the deterministic replay of r0002): full line logs,
  half-time and full-time reads of every slot's `+0x12` both sides, the MoM word, the start
  squads.
- `experiments/E012-q011-ratings/emu-firsthalf-r0002.{txt,json}` — the regenerated
  instrumented Unicorn emulation of the original binary's own first half from E011's published
  watchstart savestate, logging at the accepted-write path (`1D66`): 580 entries, 523 accepted
  ring lines, 57 dedup refusals (all template-6 repeats, delta 0), no 56CB, the plain-table
  predictor matching the accepted lines' final words 40/40. The second-half scratch harness
  (E012 notes.md §6) measured 550 entries / 507 accepted / 43 refusals the same way.
  `emu-firsthalf-r0001.{txt,json}` is superseded history: its entry logging counted `1D4A`
  entries, not accepted writes, and its "no dedup refusal" was inferred from that defect.
- `runtime/model/ratings.py` (the predictor), `tests/test_model_ratings.py` (21 tests, a
  14-mutation matrix), `experiments/E012-q011-ratings/check_ratings.py` (`match: 3/3`).

## Method

Static first (rule 22): every rule above was read from the listing — the writers of the word
(grep of the `45 12` stores over `static/goal-exe/code/`, then each site read in context), the
delta table (the data segment bytes), CAB0 (its decompiled body), the encodings (the readers'
compares). The runs corroborate: the three E012 records provide the behavioural ground truth
(their +0x12 reads at half time and full time and the MoM word, which the predictor matches
exactly — including the cases the static reading alone left ambiguous: the completed challenge's
+10, whose ring signature the record pins, the silent goalkeeper-holder bail at `5692-5697`
(which the records corroborate as a followable branch, §4.3), and the XI re-sort, whose order
the records pin — side 1's `...,131,126,130` is the exchange-sort result, not a stable partition);
the Unicorn emulations of the original binary's own halves (from E011's published savestates)
instrument the writers directly and show no invisible writer other than 56CB in ~1660 line events
(first half `emu_firsthalf.py` 580 entries, 523 accepted, 57 dedup refusals measured; second-half
scratch 550 entries, 507 accepted, 43 refusals — all template-6 repeats with delta 0). What static
analysis could not answer and the runs did: whether 56CB's bail conditions are observable in the
ring log (the record's adjacent 0x41 pair shows they are), the exact re-sort order (the record's
squad reads), and the dedup rate (non-zero — measured). What the runs cannot yet show: a
5B36-emitted 0x41 line's net (never observed) and a second-half sending-off's re-sort (r0002/r0003's
second halves had none) — each recorded as the rule's stated limits in the notes.
