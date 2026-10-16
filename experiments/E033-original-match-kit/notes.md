# E033 the original's match as a kit for goal2: notes and provenance

Made for issue 250 (the owner, 2026-10-16): make plugging the original's watched match into goal2 as
straightforward as possible, as an **interactive run** (events as they happen, the manager's decisions answered
mid-match, stop and resume, same inputs give the same match). The kit is `runtime/original_match/`; this folder
holds the evidence behind it. No DOSBox-X run was taken: every match is the original's own code in Unicorn
(Python 3.12, Unicorn 2.1.4). Neither original bytes nor savestates are committed; images come from release E006
by SHA-256. Every writer refuses an existing output; nothing in `out/` is deleted or overwritten.

## 1. The entry: run_match from a menu-state image (entry_probe.py)

Static first. `0791:F1F6 run_match(fixture far pointer)` has one caller, route_fixture `000E:6CA7`, at
`000E:6F18` (`seg_000E_09.asm:308`), which returns to `000E:6F1D`. E011-r0001's watchstart stack (BP chain)
holds F1F6's frame at `3875:3EBE`: the return `0831:6F1D` (000E relocated) and the argument `5DB4:00A6` =
fixture 21 of the calendar (`[DS:A92B] + 8*20`), so SP was `0x3EC0` at F1F6's entry. The probe builds exactly
that frame on E011-r0001's own start state (E006-r0005, the main screen) and lets the original run.

What route_fixture writes before its call (`seg_000E_05.c` route_fixture): the 6 bytes `[A923]+0x4E`, two
per-manager flags, and its loop index `[A923]+0x26`. The index matters: **the set-up reseeds the main RNG from
it** (below). The probe declares `[A923]+0x26 := 21` and the delay calibration `DS:A9FF := 20` (E032: delays
only count passes).

Result (`out/entry-probe-20261016.jsonl`): run_match ran from the menu image to its own return in 7-9 CPU s
(set-up, team screen, captain prompt, both halves, both boards, the post-match team screen, the save-summary
prompt left to time out (No), the post-match tail CB7D, BC5D, D050, BA4E), with no undeclared key read and no
stray of the 000E wait family. Against E021's emulated E011-r0001 record (whose reads E021 placed on E011's
DOSBox-X reads): score, ticks (4149), draws (182,188) and their digest, the board's statistics, scorers, man of
the match, the board screen's SHA-256 and the seed at the board are all identical. With the seed written at the
captain prompt's wait (where E011's watchstart was taken), the 10 seeds of E032's family are identical to
E032's records on score, ticks, draws, digest, statistics and template counts (10 of 10).

**The set-up reseeds the main RNG** (`0791:2648`, called by `A3DE` from match_setup `A4A1` and from the silent
result `D47E`): `seed := [A923]+0x26 * ([A923]+0x38 + 1)` (the fixture index times the year word plus one,
`seg_0791_04.asm:725-732`), then 256 draws fill the 255-entry table at `DS:8337`. Two entry seeds (0x5142, the
image's, and 0x1234) both reach the captain wait with seed 0x9115 = E011-r0001's watchstart seed (`reseed`
lines). So a watched match of the original depends on its fixture index and year, not on the RNG state
before it, and the kick-off side (the coin after the reseed) is a function of them too.

So T60's question (goal2 #130, archaeology #248) has a positive answer on this fixture: run_match can be called
directly on a fixture from a menu-state image; the one hidden input found is the fixture index the seed is
made from. What route_fixture does after run_match for a managed fixture (news pages and the sack check
`4E0E`, then `B7FA` update_fixture_player_state) is not part of run_match; the kit calls B7FA itself (section 2).

## 2. The images

E006-r0001 (goal2's own image, release E006, `e0afff67...`) and E006-r0005 (`3789d849...`) hold identical player
and country arrays; their calendars differ (another new-game seed: `DS:9D00` order table, 1464 fixture bytes) and
so does fixture 21 (E006-r0001's is not Denmark v 19). The kit therefore always writes its fixture record. From
E006-r0001 with the fixture written, E011-r0001's match is E021's (the check, section 4).

**What in an image the match depends on** (`templates.py`, `image_dependence.py`, `team_state.py`). From E011-r0001's
watchstart image (taken inside run_match, before kick-off) the same fixture is another match (1-0, 4307 ticks).
Neither the stack below the entry frame nor the text page nor the three screen buffers (`DS:7C1A/7C1E/7C22`) is
the cause: zeroed in E006-r0005 the match stays E021's, and E006-r0005's copies put into the watchstart do not
restore it. The two teams' records are: the watchstart's own set-up had sorted the computer side's squad (country
19's squad words) and set one of its players' position (378: +6 from 9 to 13; `0791:BC5D` writes the eleven's
positions from R011, F010); with country 19's record and players from E006-r0005 the watchstart gives E021's match
exactly. So, on this fixture, the match depends on the image through the teams' records (and the fixture index and
year, section 1), and those records carry the set-up's writes forward as the original carries them from fixture
to fixture. A run from E011-r0001's half-time image and from E010-r0001's (goal2's quick-friendly template) both
complete with no undeclared read.

## 3. The interactive run: the original's own decision points

Static first, from the named view and the listing (sites are return addresses of `214B:08DD` reads):

| where the original stops | routine, read site | what a manager does there | the kit |
| --- | --- | --- | --- |
| before kick-off | team menu `ED8A` from `F207` (`EE9F`) | plays (goal2's lineup and tactics are its state) | Enter on "play" |
| captain | `CC7B` role 1 (`CEED`) | picks the captain (default: the best leader `1F3C`) | Enter, or moves to `captain=` |
| in play, any slot of any tick | key poll `9372` (`93D3`) | Enter/Esc opens the team menu; R quick result; Left/Right speed | `pause()`, `quick`, `speed` |
| half time | `9A32` sets `DS:9B41 = 1`, board `0106` (`041A`), team menu (`9AE3`) | substitutes, tactics | decision `half_time` |
| a stoppage after an injury or a request | `8062` at every dead ball: `7FCF` notice (timed, `8050`), then team menu (`8103`) with `DS:9B41 = 1` | substitutes, or lets the notice time out | decision `substitution` |
| the team menu's screens | tactics `1771:1981` (`1A24`), SELECT TEAM `E44F` (`E61F`), own tactics `1771:4B61` (`4C0A`) | toggles, swaps, positions (R), marking (T, row 5) | the drivers in `screens.py` |
| set pieces | `CC7B` roles 2-5 (10 s, 1000 polls) | picks a taker | no key: the original keeps its pick |
| after a goal, at full time | `0B7C` Y/N (replay, save goal, save summary; 6 s) | answers N or waits | no key: No |
| full time | board (`041A` after `F2E3`), team menu (`F331`) | looks | Enter |

What answering changes, from the listing: in play `DS:9B41 = 0`, so SELECT TEAM's Enter only toggles the request
`DS:9B40` (`E44F`); `8062` then shows the notice at the next dead ball and opens the menu with `DS:9B41 = 1`, where
two Enters swap (`E022`: squad words, match form, marking words, `C5DC` counts the substitution and sets
`DS:9B55`). An injury to a managed player sets `DS:9B40` itself (`7D56`), so the notice repeats at every stoppage
until a substitution is made. Tactics: Enter on row r XORs element `DS:6BBF[r]` of +0x2D (`214B:0CF4`: bit e-1),
`ED8A` sets `DS:9B55` when it changed. Positions: R steps +6 by one, wrapping 0..13 (`4925`). Marking: row 5 of the
player's own tactics cycles his marked opponent through the other side's slots (`49B8`). When "play" is pressed,
`EA09` refuses an eleven with a second or no keeper, an empty slot or four of one position, with a message
(`214B:1765`), and the menu stays: the kit hands that back as the same decision with the message.

Measured (`paths.py`, `out/paths-20261016.jsonl`, 12 scenarios, all pass): a pause answered with no change leaves
the match identical to E021's; the speed byte left at 1 instead of 0 leaves it identical; a tactic change at a pause
and a substitution at half time take effect; a substitution asked for at a pause (minute 20) is offered back at the
stoppage of minute 24 and made by the default answer; a reserve keeper brought on at half time is refused with
"Denmark has too many goalkeepers" and a second answer completes the match; a position, a man-marking and a
player's own tactics are set at a pause; speed 3 and R from a pause at minute 30 end the match in 2.7 s on the quick
engine; the captain lands in `DS:9978`; a match saved at minute 30 and at the half-time decision and resumed is
identical to the straight run; goal2 managing country 19 (Denmark released) is offered country 19's decisions; seed
70 injures Larsen at 84' and the substitution offered for him is made.

## 4. The check, the tests, the trial

- `python3 -m original_match.check --family` (`out/check-20261016b.json`): engine PASS (E021's record: score,
  ticks, 182,188 draws by digest, seed and screen at the board, man of the match, the last 199 commentary lines),
  interactive PASS (example.py straight = saved and resumed at minute 60 = the recorded digest), family PASS (10 of
  10). `out/check-20261016.json` and `out/example-20261016.txt` were made before the commentary cursor was fixed
  (it skipped the lines before the first tick); superseded, kept.
- `tests/test_original_match.py`: 14 tests (screen drivers, image, machine, and four on the image). Before this PR
  the package did not exist (every test errors on import). `tests/mutations_original_match.py`: 10 of 10 mutations
  killed (`out/mutations-20261016b.txt`); its first run (`out/mutations-20261016.txt`, stopped by my time limit)
  showed the commentary-cursor mutation surviving the engine check, which compares only the last 199 lines: the test
  that every line the original writes is one event was added for it.
- goal2 (`goal2_trial.py`, run in a throwaway clone of goal2 at `6f9da19` with this folder vendored as
  `goal2/engine/original_match`, never pushed; `out/goal2-trial-20261016.txt`): goal2's GameState (Denmark, its
  14th player starting, tactics 0xAB) through goal2's `to_savestate`, a pause and a half-time substitution, the
  result read back with goal2's `from_savestate` (18 of the 20 squad records changed by the match and its post-match
  update), 5.9 s; the vendored check passes there with the same digests.

## 5. What is not possible, or costs much

- A substitution at any moment: the original takes it only at half time, at its notice after a stoppage, or (in
  extra time) before each half; a pause only asks for it. The kit keeps the original's rule.
- Undoing a substitution the original made before refusing the eleven: not possible (the swap is made before
  `EA09` checks); goal2 answers again.
- Competitive fixtures (kinds other than 1), extra time and the shoot-out (`9B93` picks the takers by hand): wired
  in the flow but unchecked; the kit refuses kind != 1. About 2 h with E031's shoot-out start state.
- The set-piece taker prompts as decisions: about 1 h (the captain driver already moves the highlight).
- The news pages and the sack check route_fixture shows after a managed fixture (`4E0E`): not run (they wait in
  the `000E` family and draw the RNG while waiting); for a friendly they change no player. About 1 h if wanted.
- Two human sides: not supported (one manager's decisions).
- Speed: a whole match 6-10 CPU s here, 2-3 s with R; stopping at every event or tick costs nothing measurable
  (`out/templates-20261016.jsonl`: 6.6-10.3 CPU s with or without `tick` events, on a shared machine). A person-speed
  display is goal2's pacing between events. A saved match is about 0.36 MB (the image's memory above 1 MiB is kept
  in it, so `memory_component()` after a resume is the image's full size); 1.5-2.3 MB with `record_draws`.

## 6. Outputs

Every file in `out/` is listed with its SHA-256 in `out/sha256-20261016.tsv` (`hashes.py`). The final runs, from
the PR's last code commit, are the files stamped `20261016c` (check, paths, example, tests, mutations, goal2 trial
and its check); the earlier stamps are the runs this notes file cites above, kept.
