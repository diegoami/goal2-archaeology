# F039 route_fixture plays fixtures until a managed one, and runs confidence and news before the player update

- **Status**: corroborated (T119b, E040) for what the runs cover: route_fixture's writes, phases, reach and draws on
  ten calls, each a managed friendly (three defeats, six wins, a draw) after 0 to 17 silent fixtures (64 in all, one
  with first byte 0xFE); proposed for the rest (below, "What the runs do not cover").
- **Question**: #427 / T118a, narrowed to the write-set by goal2's route (b) (goal2 #527, #509). For one call of
  route_fixture `000E:6CA7`: which writes and RNG steps happen, in what order, under what conditions. That covers
  its gate `6C21`, the silent path `6970` and the news page `6685`. The post-match news `4E0E`: its game-state writes and the sack (T118b1, below); its text's draws (T118b2, below).
- **Artifact**: goal2-a949da2f listings (`static/goal-exe/code/`, unpacked sha256 6fd8c5ef…3188); five published
  states for one reading of country +0x2E; for the corroboration, twelve published states of goal2-67cf27d6
  (E006, E014, E015 releases, each verified by its manifest's sha256; E040's records name them).
- **Method**: static first (rule 22). Every memory-destination instruction and every call in the four routines'
  own bodies is one row of `notes/427/writeset/writeset.json` (134 rows), and likewise for 4E0E's own routines, `319B`, `0B77` and `01FA` in `sack.json` (185 rows, with six rules), with its target, class, phase, path
  condition and listing lines. `notes/427/writeset/check.py` derives the sites from the raw listings and fails
  on a missing, duplicate or misplaced row. The decompiled and named views were read first; where they disagree
  with the listing, the listing is followed and the difference is named below. No run was made. The only
  behavioural input is a read of country +0x2E and the `[A91F]` table in five existing states, to answer what the
  listing leaves open: which entry an unmanaged side's confidence delta reaches.
- **Intervention**: none.

## Answer

- **One call plays fixtures until it plays one with a managed side.** It starts at the cursor (game +0x26). When the cursor reaches the count (+0x28), it calls `1771:8757` and returns. After a fixture it played or prepared itself (`6E15`), it advances the cursor and calls `8757`. It then returns if either side was managed (frame flag bp-4), and loops otherwise. A silent fixture (`6970`) always loops. static:static/goal-exe/code/seg_000E_09.asm:118 static:static/goal-exe/code/seg_000E_09.asm:279 static:static/goal-exe/code/seg_000E_09.asm:397 static:static/goal-exe/code/seg_000E_09.asm:404 static:static/goal-exe/code/seg_000E_09.asm:441
- **Per call it clears six game bytes and builds four continent flags.** Game +0x4E..+0x53 are set to 0. A frame flag is set for the continent (+0x2C) of each manager's country (managers 1..game +0). The flags gate the kind set `DS:697A` and the news page `6685`. static:static/goal-exe/code/seg_000E_09.asm:66 static:static/goal-exe/code/seg_000E_09.asm:113 static:static/goal-exe/code/seg_000E_09.asm:174
- **Routing.** First byte 0xFE goes to the gate `6C21`, with flag 1 only when neither side is managed. If the gate returns 0, or the first byte is not 0xFE, kind (+2) in `DS:695A` asks through the gate with flag 1. So does kind in `DS:697A` when the second side's continent has a manager. Everything else goes to `6970`. The decompiled view guards the `695A` test with "first byte not 0xFE", but the listing has no such test (`6DAE`-`6DCB`): a 0xFE fixture the gate refused is tested against `695A` too. static:static/goal-exe/code/seg_000E_09.asm:131 static:static/goal-exe/code/seg_000E_09.asm:146 static:static/goal-exe/code/seg_000E_09.asm:159 static:static/goal-exe/code/seg_000E_09.asm:168
- **The gate `6C21`** shows the key page `DS:14A6` and waits for a key when route_fixture's bp-2 says a results page is open. With a nonzero flag, it then calls `ask_watch_match 0791:E80D` and returns its answer. With a zero flag, it returns 1. static:static/goal-exe/code/seg_000E_09.asm:16 static:static/goal-exe/code/seg_000E_09.asm:24 static:static/goal-exe/code/seg_000E_09.asm:37
- **Kinds 3 and 7 mark each managed side's manager.** On the played path (`6E15`), for kinds 3 and 7 (the set `CS:6C87`, byte 0 = 0x88): game +0x13+m := 1 and +0x41+m := 0 for each managed side, with m = country +0x2E − 0x80. The decompiled view's `if (!bVar12)` hides this kind test. static:static/goal-exe/code/seg_000E_09.asm:51 static:static/goal-exe/code/seg_000E_09.asm:212 static:static/goal-exe/code/seg_000E_09.asm:245 static:static/goal-exe/code/seg_000E_09.asm:261
- **The played path's order.** Kind 0 goes to `prepare_unplayed_match 0791:BB2F`, then to the cursor. Any other kind:
  `run_match 0791:F1F6`; then, when a side is managed and kind ≠ 1, for **both** sides `B71C` computes a delta and `B6CC` adds it to `[A91F] + 3e + 2` (e = that side's country +0x2E, clamped to −127..127); then `post_match_news_and_sack 000E:4E0E` for each managed side; then `update_fixture_player_state 0791:B7FA`; then the cursor +1 and `8757`. static:static/goal-exe/code/seg_000E_09.asm:296 static:static/goal-exe/code/seg_000E_09.asm:308 static:static/goal-exe/code/seg_000E_09.asm:348 static:static/goal-exe/code/seg_000E_09.asm:350 static:static/goal-exe/code/seg_000E_09.asm:383 static:static/goal-exe/code/seg_000E_09.asm:396
- **An unmanaged side's delta reaches its own country's entry.** In E006-r0001, E010-r0001, E011-r0001, E014-r0006 and one E015 sitting state, every unmanaged country c has +0x2E = c, and the managed one has 0x80 + 1. `[A91F]` holds 3-byte entries 1..128 (a country number first) and 0x81.. for the managers. In E014-r0006's year-one state, the +2 byte is nonzero for computer countries too. static:runtime/original_match/port/update.py:91 E006-r0001 E010-r0001 E011-r0001 E014-r0006
- **The silent path `6970` plays and records the fixture.** In order: `quick_result_silent D47E`, `B7FA`, `credit_silent_match_scorers B602`, `D050`, and `reset_team_tactics BC5D` for both sides, with no `is_managed` test. static:static/goal-exe/code/seg_000E_08.asm:966 static:static/goal-exe/code/seg_000E_08.asm:976 static:static/goal-exe/code/seg_000E_08.asm:986 static:static/goal-exe/code/seg_000E_08.asm:996 static:static/goal-exe/code/seg_000E_08.asm:1008
- **For first byte 0xFE, `6970` shows the score page.** It waits for a key and calls `show_updated_group_tables E929`, which rebuilds the tables. Then it advances the cursor and sets route_fixture's bp-2 := 0. static:static/goal-exe/code/seg_000E_08.asm:1040 static:static/goal-exe/code/seg_000E_08.asm:1045 static:static/goal-exe/code/seg_000E_08.asm:1047 static:static/goal-exe/code/seg_000E_08.asm:1049
- **Otherwise `6970` adds to the results list.** It lists up to 16 rows, starting from max(cursor − 15, the cursor at entry). Keys 0xAE and 0xAF move game +0x3E within 0..5, and +0x3E waits of 50 ms follow, each cut short by a key. Then it advances the cursor and sets bp-2 := 1. static:static/goal-exe/code/seg_000E_08.asm:1090 static:static/goal-exe/code/seg_000E_08.asm:1155 static:static/goal-exe/code/seg_000E_08.asm:1165 static:static/goal-exe/code/seg_000E_08.asm:1193 static:static/goal-exe/code/seg_000E_08.asm:1200 static:static/goal-exe/code/seg_000E_08.asm:1202
- **The news page `6685` always draws twice from `DS:7B62`.** It follows a silent fixture, or a fixture played here with no managed side, when its kind is 0xCB, or 0x67 with the second side's continent managed. Both draws are `214B:06B1(3)`, one LCG step each of the word at `[A978]` = `DS:7B62`, whether or not a human played. The first picks a string at `DS:006A + 16r`, the second one of three line forms. Its other helpers (`038E`, `05F6`, `062F`, `070B`, `075F`, `5978`) are shared with `4E0E`'s subtree and are T118b's. static:static/goal-exe/code/seg_000E_09.asm:438 static:static/goal-exe/code/seg_000E_08.asm:758 static:static/goal-exe/code/seg_000E_08.asm:774 static:static/goal-exe/code/seg_214B_01.asm:903
- **No other RNG call is in the four routines' own bodies.** Their RNG effects come from their callees: `F1F6`, `B7FA`, `D47E`, `E80D`, `BB2F`, `4E0E`, and `6685`'s helpers. static:notes/427/writeset/writeset.json:1
- **The post-match news (`4E0E`) writes game state only through the sack.** Its own stores are frame locals: the side s (1 when the country is the second side, +6), whether s scored, a goal tally per squad slot from the scorer list at `DS:7BD1 + 0x21 s + 3k` (1771:3A82), and the top-scoring slot (the lowest of equals). It then shows the pages `038E`, `11D9`, `4DB7` and `26F2` and waits for a key (`05F6`). The key wait's flags are: s won a kind in `CS:4DEE` = {0x67, 0xCB}, and kind in `DS:A943` with a per-manager byte below it. Finally it calls `unmanage_country` when its frame's sack flag bp-2 is set. static:static/goal-exe/code/seg_000E_06.asm:557 static:static/goal-exe/code/seg_000E_06.asm:567 static:static/goal-exe/code/seg_000E_06.asm:616 static:static/goal-exe/code/seg_000E_06.asm:636 static:static/goal-exe/code/seg_000E_06.asm:707 static:static/goal-exe/code/seg_000E_06.asm:719
- **The headline (`319B`, through `4DB7`) is chosen by the result, and sets the sack flag.** Fixture +3 = s is a win, 2 a draw, anything else a defeat. A win of kind 0xCB, 0x67, 0xC9, 0x65 or 0xC8 has a fixed headline. So does another win by margin 0 (`1771:5C60`). Otherwise the top slot's goals (1, 2, 3, other) choose the form. A defeat with equal goals (fixture +1 = +0) has a fixed headline and never reads the sack score. 319B's nine `06B1` draws (two of 2, two of 3, five of 4 values) each sit on one path. static:static/goal-exe/code/seg_000E_04.asm:156 static:static/goal-exe/code/seg_000E_04.asm:162 static:static/goal-exe/code/seg_000E_04.asm:277 static:static/goal-exe/code/seg_000E_04.asm:319 static:static/goal-exe/code/seg_000E_04.asm:739 static:notes/427/writeset/sack.json:1
- **The sack score and its thresholds.** `manager_sack_score 0B77` returns 0 when any of these holds: the year word +0x38 is below 2, the kind is 1, the stage uses the finals table (`1771:59D8`) and game +1+m is nonzero, or country +0xBE is nonzero. Otherwise it returns the signed byte `[A91F] + 3·(+0x2E) + 2`, the pending delta that `B6CC` has just added to, since route_fixture runs it before `4E0E`. On a defeat with unequal goals: −7 or −6 gives one headline, −10..−8 another, and −11 or lower (to −128, the byte's limit) stores 1 into 4E0E's bp-2: the sack. static:static/goal-exe/code/seg_000E_02.asm:159 static:static/goal-exe/code/seg_000E_02.asm:183 static:static/goal-exe/code/seg_000E_02.asm:195 static:static/goal-exe/code/seg_000E_04.asm:755 static:static/goal-exe/code/seg_000E_04.asm:771 static:static/goal-exe/code/seg_000E_04.asm:825
- **The sack (`unmanage_country 01FA`, manager m, country c) makes six writes.**
  game +0x47+m := 1; manager m's entry `[A91F] + 3(0x80+m) + 1` := 1; `reset_team_tactics BC5D(c)` while c is still managed; position +6 := +7 for squad slots 12..20; byte +0 := 0 for m's 80 pool players (`[A927] + 2k` from `DS:6D18[m]`); c +0x2E := c, after which `is_managed` says no; and 0xFE → 0xFF for c's fixtures from the first nonzero position of its fixture list to 36. static:static/goal-exe/code/seg_000E_01.asm:229 static:static/goal-exe/code/seg_000E_01.asm:231 static:static/goal-exe/code/seg_000E_01.asm:236 static:static/goal-exe/code/seg_000E_01.asm:265 static:static/goal-exe/code/seg_000E_01.asm:292 static:static/goal-exe/code/seg_000E_01.asm:306 static:static/goal-exe/code/seg_000E_01.asm:356
- **The news text draws on 7B62 at 49 sites in 30 routines, plus 319B's nine.** Each call of `214B:06B1`, `06FA` (the coin, `06B1(2) = 1`) or `06D0` is one step of the LCG `214B:0688` on the word at `[A978]` = `DS:7B62`. Apart from the crowd animation, each draw sits on one block of its routine, outside any loop, so a routine draws at most once per block it passes. `notes/427/writeset/news.json` lists each with its block. static:static/goal-exe/code/seg_214B_01.asm:903 static:notes/427/writeset/news.json:1
- **The text routines write no game state.** Their stores are frame locals, except seven, each read: an attribute byte of the video buffer `[A96A]` (the animation's colour); `DS:7968` and `DS:7966` (the tune and the speaker); `DS:0022`, written and read only inside `2071`; a caller's string length (`094A`); and a caller's frame flag (`3A5E`, `47E6`). Their string operations write frame temporaries or a string argument. static:static/goal-exe/code/seg_000E_01.asm:516 static:static/goal-exe/code/seg_000E_01.asm:538 static:static/goal-exe/code/seg_000E_01.asm:609 static:static/goal-exe/code/seg_000E_01.asm:1052 static:static/goal-exe/code/seg_000E_03.asm:130 static:static/goal-exe/code/seg_000E_03.asm:161
- **The key wait `05F6` can run the crowd animation, which draws 1,000 to 1,500 times per call.** `05F6(f1, f2, f3)` shows the back buffer. If any flag is set it calls `0572`, then reads a key. `0572` plays up to three tune parts (`04F5`, 16 notes each, each note one `045D` call, stopping at a waiting key). It then calls `045D` again until a key is waiting, at least once. `045D` runs 50 × 10 seats with `06B1(5)` and `06B1(0x50)`, plus `06B1(15)` when the seat's video byte is below 7. So the number of draws depends on the page's bytes and on when the key comes. `4E0E` sets a flag when its side won a kind in {0x67, 0xCB}, or on the `DS:A943` test; `6685`'s wait `05F6(0,0,0)` does not animate. static:static/goal-exe/code/seg_000E_01.asm:469 static:static/goal-exe/code/seg_000E_01.asm:504 static:static/goal-exe/code/seg_000E_01.asm:551 static:static/goal-exe/code/seg_000E_01.asm:626 static:static/goal-exe/code/seg_000E_01.asm:651

## Corroboration (T119b, E040)

- **Method.** Static first: the three tables are the answer, and the runs only corroborate them (rules 19, 22). The
  route harness (T119a, `runtime/original_match/route.py`) runs one call of `6CA7` per published state at the manager
  menu, with its default key policy (a key at the first poll, Enter; N at the watch prompt) and the managed match by
  `Match(tail=False)`. The runner adds code hooks at every basic-block leader, store and call site and call return of
  the 39 scoped routines, read from the raw listings, and gives each recorded write the chain of scoped calls it
  happened in. `experiments/E040-route-fixture-writes/runner.py --check` holds the committed records against the
  tables (its README states the eight rules). E040-r0001 E040-r0003 E040-r0009 E040-r0012
- **Every write lies in a row its class admits, in its phase.** 2,952,719 guest writes in ten calls, and the match's
  write-back (197,005 bytes, under `6F18`, port-owned). Frame rows write only the stack. Game, country, player,
  manager and fixture writes come only from rows of those classes or from port-owned and unread subtree calls. Screen
  rows write only the text pages and the text attribute (next item). A sack.json or news.json row is reached only
  under `6FD8`. The record replayed over the start memory gives the memory each call left. E040-r0001 E040-r0003
  E040-r0009 E040-r0012
- **The text attribute `DS:AAB2` is a display variable the screen rows' callees write.** `214B:0205` and `02C8`
  store their attribute argument in the CRT unit's TextAttr, which `01A3` and `026D` write text with. The screen
  rows' callees wrote it 2,982 times: `02C8` (news.json `069A`, `0754`, `07CA`; writeset.json `6B6A`), `0791:0712`,
  `1771:5BF6` and `1771:7812`. Their row texts name only the text pages. `E929` and `E80D` wrote it too. No other
  screen write left the text pages. static:static/goal-exe/code/seg_214B_01.asm:320
  static:static/goal-exe/code/seg_214B_01.asm:412 E040-r0001
- **The string operations write only the stack.** news.json's declared limit is checked: the callees of frame-class
  call rows (`23E4:0644`, `062A`, `06B7`, `075A`, `214B:009C`, `0018`, `1771:2E93`) made 45,919 writes, all on the
  stack (frame temporaries or a caller's frame string). E040-r0001 E040-r0009
- **The phases run in F039's order, and each row is visited as often as its basic block.** Every call's
  route_fixture-scope visits read pre-match, then per fixture the routing (and the gate), then the silent path or the
  played path (`run_match`, the news, the player update, the cursor, the tables). In every block a call entered, every
  row was visited as often as the block's leader ran. No other row was visited. That is 81 of writeset.json's 134
  rows, 69 of sack.json's 185 and 258 of news.json's 672. E040-r0001 E040-r0009 E040-r0012
- **The draws match in count and order.** Each visit of an rng row stepped `DS:7B62` once (84 visits: 75 news text,
  nine 319B), in the order of the visits. No pure, frame, screen or prompt row stepped `7B62` or `8336`. On the route
  the other `7B62` steps were made inside `B7FA` (5,824), `D47E` (21,388), `B602` (129) and `E80D` (261, the one watch
  prompt). `8336` stepped only in the match. No crowd animation ran: no managed side won a kind in {0x67, 0xCB}.
  E040-r0003 E040-r0009 E040-r0012
- **The fixtures' paths are F039's.** Each managed friendly went through `6F18`, `4E0E` once, `B7FA` once and no
  confidence term (kind 1). Each unmanaged fixture went through `6970`, with the score page (`6A84`, `E929`) exactly
  for its first byte 0xFE. 319B's win, draw and defeat rows followed the managed side's result. No sack ran: every
  state's season word +0x38 is 0, so `0B77` returns 0. E040-r0001 E040-r0003 E040-r0009
- **What the runs do not cover.** These stay proposed. A managed non-friendly: in these calendars every non-friendly
  carries its round number in fixture +1 (0 in friendlies). `Match`'s fixture builder writes +1 := 0, so the harness
  refuses the call at `6F18` (E040-r0010, E040-r0011, the E015 qualifier). So neither the confidence term (`B71C`,
  `B6CC`) nor kinds 3 and 7 are corroborated. Also uncovered: a sack (no published state has a season word of 2 or
  more), kind 0 (`BB2F`), `6685` and the crowd animation (no kind 0x67 or 0xCB), the gates `6DC6` and `6E0B`, the
  results page's keys 0xAE, 0xAF and space, and `6BFF` (the key at the first poll skips every wait). Several
  managers are not covered either. The 0xFE silent fixture's group-table reads (`1771:9022` and the like) are not in
  `route.DEFAULT_KEYS`; E040-r0009 answers them Enter, as `Match` does. E040-r0009 E040-r0010

## Alternatives and limits

- Callees are classified, not read, here. Port-owned ones (`F1F6`, `B71C`, `B6CC`, `B7FA`, `8757`, `D050`,
  `BC5D`, `E929`) are as the port translates them. Unported ones (`D47E`, `B602`, `BB2F`, `E80D`) are U2's to
  read and port. Screen callees (`5BF6`, `7812`) were read only for their own stores (frame and `DS:AAB2`).
- The readers of game +0x13+m, +0x41+m and +0x4E..+0x53 are not read here. `play_round`'s row reads a +0x47
  flag per manager, consistent with +0x41+m for m = 6, but this is not established.
- The +0x2E reading covers single-manager states only. Several managers give 0x80 + m statically (F007).
- The corroboration (T119b, E040, below) covers managed friendlies and silent fixtures only; what it leaves is listed there.

## Inferences

- **goal2's port path differs from the original after a managed match.** `Match` runs `B7FA` right after `F1F6`.
  The original runs `B6CC` and `4E0E` in between. `4E0E`'s sack branch calls `unmanage_country`, which writes
  the country's own number to +0x2E. `B7FA` tests `is_managed` for both sides (`B815`, `B825`), so after a sack it
  takes the computer branch for that side. Any draw `4E0E` makes also moves `B7FA`'s draws. The tail therefore
  cannot be reordered without proof. The news does draw: 319B nine times on its paths (T118b1), and the text routines 49 times on their blocks, plus the crowd animation's thousands when a key wait animates (T118b2). static:static/goal-exe/annotations/routines.tsv:3 static:runtime/original_match/port/update.py:404 static:static/goal-exe/annotations/routines.tsv:428
- **A native tournament continuation must also reproduce the RNG of fixtures no human plays.** Every non-managed
  fixture goes through `D47E` and `B7FA`, and a kind-0xCB or kind-0x67 fixture also through `6685`'s two
  draws. In the call graph, `E80D`, `BB2F` and `D47E` each reach the set-up reseed `0791:2648`. Whether each call
  takes it is U2's to establish. static:static/goal-exe/annotations/routines.tsv:595 static:static/goal-exe/code/seg_0791_17.asm:204
