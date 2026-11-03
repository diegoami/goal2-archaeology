# F039 route_fixture plays fixtures until a managed one, and runs confidence and news before the player update

- **Status**: proposed.
- **Question**: #427 / T118a, narrowed to the write-set by goal2's route (b) (goal2 #527, #509). For one call of
  route_fixture `000E:6CA7`: which writes and RNG steps happen, in what order, under what conditions. That covers
  its gate `6C21`, the silent path `6970` and the news page `6685`. The post-match news `4E0E` is T118b's.
- **Artifact**: goal2-a949da2f listings (`static/goal-exe/code/`, unpacked sha256 6fd8c5ef…3188); five published
  states for one reading of country +0x2E.
- **Method**: static first (rule 22). Every memory-destination instruction and every call in the four routines'
  own bodies is one row of `notes/427/writeset/writeset.json` (134 rows), with its target, class, phase, path
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

## Alternatives and limits

- Callees are classified, not read, here. Port-owned ones (`F1F6`, `B71C`, `B6CC`, `B7FA`, `8757`, `D050`,
  `BC5D`, `E929`) are as the port translates them. Unported ones (`D47E`, `B602`, `BB2F`, `E80D`) are U2's to
  read and port. Screen callees (`5BF6`, `7812`) were read only for their own stores (frame and `DS:AAB2`).
- The readers of game +0x13+m, +0x41+m and +0x4E..+0x53 are not read here. `play_round`'s row reads a +0x47
  flag per manager, consistent with +0x41+m for m = 6, but this is not established.
- The +0x2E reading covers single-manager states only. Several managers give 0x80 + m statically (F007).
- T118c corroborates the whole account with a write watch.

## Inferences

- **goal2's port path differs from the original after a managed match.** `Match` runs `B7FA` right after `F1F6`.
  The original runs `B6CC` and `4E0E` in between. `4E0E`'s sack branch calls `unmanage_country`, which writes
  the country's own number to +0x2E. `B7FA` tests `is_managed` for both sides (`B815`, `B825`), so after a sack it
  takes the computer branch for that side. Any draw `4E0E` makes also moves `B7FA`'s draws. The tail therefore
  cannot be reordered without proof: T118b settles the draws. static:static/goal-exe/annotations/routines.tsv:3 static:runtime/original_match/port/update.py:404 static:static/goal-exe/annotations/routines.tsv:428
- **A native tournament continuation must also reproduce the RNG of fixtures no human plays.** Every non-managed
  fixture goes through `D47E` and `B7FA`, and a kind-0xCB or kind-0x67 fixture also through `6685`'s two
  draws. In the call graph, `E80D`, `BB2F` and `D47E` each reach the set-up reseed `0791:2648`. Whether each call
  takes it is U2's to establish. static:static/goal-exe/annotations/routines.tsv:595 static:static/goal-exe/code/seg_0791_17.asm:204
