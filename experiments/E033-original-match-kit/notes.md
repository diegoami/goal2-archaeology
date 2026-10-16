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
so does fixture 21 (E006-r0001's is not Denmark v 19). The kit therefore always writes its fixture record.
