# E015 protocol: one maximally informative sitting

The owner plays once; the project extracts everything (the owner's direction, 2026-10-07). A
savestate is the whole machine state, so a timestamped chain of them — plus the screens they
carry and (between snapshots) the video — is a complete behavioural record any later question is
mined from without new play. The sitting is **not scripted**: everything below is what makes one
sitting maximally informative, not a procedure to follow key by key. A partial chain is a valid
record: start, stop, and restart whenever you like; the recorder and the extraction tolerate it.

## Before

```
bash setup/goal2-runtime.sh            # once: the verified release copy in .cache/goal2
bash runtime/human/play.sh --self-test
```

## The sitting

One command starts everything (from a graphical session, so the game window opens on your
display):

```
bash runtime/human/play.sh [--video] [--quit-after SECS] [--res WIDTHxHEIGHT] [--load FILE.GL | --fresh]
```

With no subcommand `play.sh` plays. Before DOSBox-X starts, the recorder copies your newest saved
game (`.GL`) from the previous sessions into the new session's game copy (`--load FILE.GL` names
another, `--fresh` copies none); `meta.json` records the copy and its sha256 (an I3 intervention
the record declares). Load it in the game yourself (Y at the title): the recorder never presses a
key to load it.

The recorder's `--countries` argument does not exist; country selection is an extraction
parameter (rework round 2 R15: `--countries 1,4` is passed to `extract.py`, not to `play.sh`).
A Xephyr window contains DOSBox-X on a private nested display, booted from a per-session copy of the verified release. From then
on you simply play. The watcher (invisible) sends the savestate host key **directly to the game
window** (explicit XSendEvent, never a global keystroke — your terminal can keep the focus the
whole time) and stages a timestamped snapshot every 20 s and 0.05 s after each settled key
episode (the scheduling quiet `EVENT_SETTLE_S`; the 0.5 s `BURST_QUIET_S` remains the grouping
quiet the map reads), hashed into the session's index. The
session folder is `scratch/human/sessions/<date-time>/` (git-ignored: the savestates and the
video never enter the repository; only the extracted record does). The sitting is silent: the
config family is the G1 driver's, with `nosound=true`.

The logger listens only on that nested display. It writes press/release events,
UTC and monotonic timestamps, keycodes and base keysyms to `keys.jsonl`, flushed
per line; it never attaches to the outer desktop. The key log stays out of git.
The burst intervals are [designed], not measured game timings: T29's timings and
the T34 brief were searched, and neither specified a human typing interval. The
grouping quiet (0.5 s) groups keys into bursts; the scheduling quiet (0.05 s,
~4x the measured 12 ms press-release lag) is when the episode's save request
goes out — later than that and the ~0.08 s request window cannot fit between
keys spaced just over the grouping quiet (measured 0.525-0.529 s in the
20261009-142948 session).

What makes the sitting maximally informative (each row of the map below is fed by one of these):

- **Start a new game** (or load one — both are fine; the chain records which).
- **Watch a few matches fully**, and let the match run at a *moderate speed* (the in-match speed
  controls): at top speed a half can pass between two snapshots and the commentary ring can lap
  itself (issue #40's wrap problem). At a moderate speed consecutive snapshots share commentary
  rows, and the screen history shows the lines moving.
- **Quick-result (R) the rest** — seasons move fast and the year-end diffs are the point.
- **Cross year-ends slowly**: play until the season turnover, then pause a moment (a snapshot
  lands within 20 s) and check the news screens. Year-end player-record and squad diffs (Q013,
  Q014) come from the states either side of the turnover.
- **Do transfers / pre-season squad edits** while the recorder runs: squad diffs are read from
  the same states (Q014). Pick a player from the pool into your country, drop one out, change
  tactic bytes (R008, open finding #65) and the captain/penalty/corner presets (F015's reading
  paths), watch the squad slots move.
- **Play a knockout cup run to a penalty shoot-out** if the fixture list offers one (F015's
  shoot-out arm has never been watched: `0791:A10A`).
- **Reposition a player on the pitch** (national repositioning: F008's +6/+7 written live),
  with the watched match's states either side of the move.
- **Take a corner / a penalty / make a substitution** during a watched match (F015's reading
  paths; Q09.5 replays).
- **Visit the board / news screens** between rounds (Q016, Q017): the screens are captured.
- **Play a World Cup cycle** if you reach one: the stage and fixture bytes of the chain are the
  bot's map of the competition path.
- If you save in-game, the `.GL` save lands in the session's own game-folder copy — it stays with
  the session, never in the release cache.

### Pausing and coaching (T39b)

- **Pause: F12+P** (hold F12, press P). DOSBox-X stops and its window title ends in `PAUSED`.
  **Resume: F12+P again.** DOSBox-X's pause ends on the Pause key only, so the recorder presses
  Pause for you (an XTEST key on the nested display, the game window focused) and marks it
  `by: recorder` in `keys.jsonl`; it is never counted as your key. A Pause key, if you have one,
  resumes too.
- While paused the game does not run and DOSBox-X ignores every key: what you type then reaches
  the key log, not the game. The recorder sends no snapshot request while paused and takes the
  pause's snapshot right after you resume (DOSBox-X writes none while paused), and `pauses.jsonl`
  records each pause and resume with its time.
- **Notes**: the main session writes your chat notes into the sitting with
  `python3 runtime/human/note.py <session> "text"`; the record places each note between the two
  snapshots it falls between.
- **Live view**: `python3 runtime/human/live.py <session>` prints the newest snapshot's screen and
  the keys since its previous call, without writing anything into the session.

Stopping: close the game window (or Ctrl+C in the terminal). The watcher stops with it, stages
your last F12+S if one is pending, and writes the session's meta.

## After

```
python3 experiments/E015-human-playthrough/extract.py scratch/human/sessions/<date-time> --countries 1,4
python3 tools/validate_runs.py runs/E015
python3 tools/publish_evidence.py E015 --run E015-r<nnnn> --file <snapshot> …   # the savestates
python3 tools/verify_evidence.py E015
```

`extract.py <session-dir>` is positional; it accepts `--countries` (the countries whose records
the chain carries — pass the ones you manage, their numbers as GOAL shows them), `--runs-dir`,
and `--machine`. The record lands in `runs/E015/`, never overwriting an earlier one
(`O_CREAT|O_EXCL`, rework round 2 R2).

The key map identifies screens by SHA256 of their UTF-8 decoded text, not their
attributes, and associates each ordered key burst with the nearest preceding
snapshot and first snapshot after the quiet interval. It does not assert that
each individual key caused the eventual screen. Missing bracketing snapshots
are counted as unmapped presses. `extract.py` carries the map as a JSON
observation in the sitting's one run/1 record (T34 review R5: there is no
separate map-writing step; `keymap.py <session>` merely prints the summary and
table again from the session). A readable `<run-id>-keymap.md` table sits beside
this protocol, written from `keymap.py`'s output. Raw events
may be included with `--scripted-keys` only for scripted acceptance sittings.

## The living coverage map

The owner plays unscripted, and the map below is how the project's main session reports what one
sitting filled and what remains. Each row is a knowledge item the project will eventually need:
the byte (or set of bytes) in guest memory, the open question or finding it belongs to, the
coverage status, and the named session that fills it. The map is updated after every sitting.

Coverage statuses (the project-recognised vocabulary):

- **static-known** — the byte location and reading rules are confirmed by static analysis (one of
  `static/goal-exe/named/`, the decompiled listings, or an annotation row); no behavioural run
  needed for the location; a run may still be wanted to corroborate a value.
- **corroborated** — a behavioural run confirmed the static answer; named session cited.
- **needs-play** — no static answer; the row will be filled the first time the owner happens to
  act on the item during a sitting.
- **covered-by-a-named-session** — a sitting already captured it; the record's id is cited.

| Knowledge item | Byte / observation | Question / finding | Status | Named session |
| --- | --- | --- | --- | --- |
| Selection picks and drops (the pool into the squad, out of it) | country record `c` at `[A917]+c*0xBF`: the squad, 20 words at `+0x00..+0x27` (fields.tsv `country 0x00 squad`; F007, F008); a pool player's record `+0` (country) | F011's pool, Q014 | corroborated | E015-r0001 (initial layout); E015-r0014 (Italy's squad word in slot 13 `303→2572` at state 181, with slot 12 `313→303`, so `313` leaves the words: a pool record, numbered from 2561 per F011, enters the squad); E015-r0015 (slot 8 `309→2593` at state 19, `2565` enters at 98). That the pool player's record `+0` (country) changes with the pick is not checked |
| Repositioning on the pitch (national, between matches) | player record `+6` (position) and `+7` (club position) at `[A91B]+n*0x14` (F008); the squad words' order, sorted by `+6` in `1771:52CC` (F010) | F008, open finding | covered-by-a-named-session | E015-r0013 (Italy's player records: `+0x6` moved through the position codes while `+0x7` never changed in the whole chain; player 315 `04→05→09→0A→0B→0C→0D→00→01→02→03` over states 247–256 in the squad screen before the second match, and likewise players 2565 (390–399), 318 (411–413), 319 (443–452), 316 (457–466), 309 (649–656); E015-r0015 (player 315's `+0x6` `04→05→06→08→0D` over states 237–240, the repositioning of Stroppa in its note 8); the screen legend `R,C-reposition` at states 292, 302 of r0013; the owner's notes 21–22 name the moves: Berti central midfield, Baggio striker, Bergomi sweeper. Which player number is which name is not read here) |
| Team-tactic changes | country record byte `+0x2D`, R008, the default team tactic set (F010; fields.tsv `country 0x2D`); a player's own overrides of elements 1..4 in player record `+0xF` (F010) | #65 R008 | static-known | E015-r0001; E015-r0007 (Italy's `+0x2D` changed in a watched match at states 121, 122, 125, 128: [mined](E015-r0007-mined.md)); E015-r0013 (Italy's `+0x2D` = `0x84` at state 3, then `0x94`, `0xB4`, `0xF4`, `0xF5`, `0xF7`, `0xFF` at states 351, 353, 355, 357, 359, 362 while the owner raised the tactics (notes 20–21), then `0xFB` at 601 and `0xEB` at 602, in step with the owner's "half pitch and short passes" (note 30); Portugal's `+0x2D` `0xF7`↔`0xE2` at states 736–742 around its replay prompts, cause not read); E015-r0017 (Italy's `+0x2D` stayed `0x84` from state 4 to the end, as note 4 says: "left at the default") |
| Captain / penalty / corner presets | not established: no finding names a stored byte for them (F015 ranks the shoot-out takers by the derived penalty skill, element 12, rather than reading a stored choice); found by diffing the states either side of the owner setting one | F015 | needs-play | — |
| Transfer promise line | `000E:544D` (the screen line "the transfer promise") | Q014, open question | needs-play | — |
| Training / fitness recovery | player record `+0xC` morale, `+0xD` fitness, `+0xE` energy (F008's record layout) across consecutive states between matches | Q015 | needs-play | — (E015-r0013 and r0017 hold no state between two matches in which a record moved: Italy's `+0xC`/`+0xD`/`+0xE` first change at the next match's start, states 287–288 in r0013; what moves them after a match is the post-match row below) |
| Watched-match substitutions | player record changes between states either side of a substitution key | Q09.5 | covered-by-a-named-session | E015-r0007 (substitution screens during the watched friendly; squad reorders at seq 91, 99, 113; status `+0x10` changed 10 times; the substitutes stay in the eleven after the match, state 215: [mined](E015-r0007-mined.md)); E015-r0013 (Italy's squad words swap a slot between the eleven and the bench at states 321 (slots 10↔19: 311↔320, the injured Signori for Schillaci, note 16), 434, 640, 709, 790 (note 37: Maldini for Vierchowod), and the screen's "substitutions left" counter reads 4, 3, 2, 1, 0 ("no more substitutes") at those states; player 311's `+0xE` energy fell `19→00` at state 288 and its `+0x10` went `40→44` at 321) |
| Watched-match replays | screen-history of a watched match with replays on (commentary ring position) | Q09.5, #40 | covered-by-a-named-session | E015-r0013 (replays on throughout: the line "Hit INS to turn automatic action replay OFF" is on screen from state 29; the replay screens carry the `REPLAY` banner at states 88–89 and 334–335; the "Do you want an action replay? (Y/N)" prompt at states 339, 736, 742. The commentary ring's position is not read here: the question stays with #40) |
| Knockout shoot-out arm | the screen + takers' records during `0791:A10A` | F015 (follow-up) | needs-play | — |
| Year-end player-record diffs | states either side of a year end: the stage byte `[A923]+0x3C` entering 2, 3, 5 or 7, the season word `[A923]+0x38` (E014 notes, T28, PR #91; `+0x3A` is the new game's base year and does not move) | Q013 (T28 corroboration) | static-known | E015-r0001 (state words present) |
| Year-end squad diffs (retirements, new players) | squad words `+0x00..+0x27` either side of the same year ends, `players.check` flipping from the start layout | Q014 | static-known | E015-r0001 (initial layout) |
| Energy through a watched match | player record `+0xE` energy and `+0xD` fitness (F008's layout) across consecutive states of a watched match | Q015 | covered-by-a-named-session | E015-r0007 (a watched friendly, Italy: `+0xE` changed 115 times, `+0xD` 14 times across consecutive states); E015-r0013 (three watched matches, Italy's records: `+0xE` changed 229 times; `+0xD` changed only at state 801, the first state after the last match: 14 players; E015-r0017: `+0xE` 135 times, `+0xD` 11 times, all at state 288) |
| Exact commentary identity | consecutive `ui-text` screens of a watched match at moderate speed | #40 | needs-play | — (E015-r0013's live commentary window is 3 lines and in the states read (33–37, 20 s apart) consecutive states share no row; the scrollable commentary view holds 19 lines at once and is its own row below) |
| Board / confidence / morale | `ui-text` of the states where the board/news screens were up | Q016, Q017 | needs-play | — |
| Bot's World Cup path | stage `[A923]+0x3C`, fixture index/count `[A923]+0x26/+0x28` across a cycle's chain (E014 notes, T28, PR #91) | bot input | needs-play | — |
| Scripted opening-screen key burst | shell/mount text → title text after `a`; nearest snapshots bracket the burst, not proof that `a` caused the boot transition | T34 recorder/map acceptance | covered-by-a-named-session | E015-r0004, E015-r0005, E015-r0006; their `<run-id>-keymap.md` tables |
| Scripted title-screen key burst | title text → same title text after `b`/`c`; burst captures per key group (0.5–1.5 s human-paced gaps), all press/release events recorded, outer-app `x/y/z` absent while xev and an outer raw reader prove they were really typed | T34 recorder privacy and timing | covered-by-a-named-session | E015-r0004, E015-r0005, E015-r0006 |
| Screen-flow controls during normal play | `C`, `N`, `Insert`, and recovery keys on the relevant screens; the scripted acceptance keys do not visit those screens | T34 screen/key map; T28 EA09 stall | needs-play | — (E015-r0013 visited `C` on the captain prompt, key `c` at 05:22:02 UTC after the prompt at state 280, and `N` on the "save this goal" and "watch this match" prompts; no `Insert` and no recovery key was pressed in r0013 or r0017) |
| In-match speed byte | match delay byte `[A923]+0x3F` (0 fastest): its values against the Left/Right keys | F005, F006 (the byte; the keys are new) | covered-by-a-named-session | E015-r0013: `5` at state 3, `4` at 31 (05:05:05; `Right` at 05:05:04), `3` at 81 (`Right` at 05:12:35); it reads `4` on the replay screens (88–89, 334–335) and `3` again after. E015-r0017: `4` at state 216 and `5` at 217 (`Left` 04:54:56, `Right` 04:54:57, `Left` 04:54:59). So Right lowers the byte (faster), Left raises it; the key legend shows `»»` at byte 4 (state 88) and `»»»` at byte 3 (state 340) |
| In-match keys and the four player display modes | the legend `↓↑-display ←→-speed»»» R-result spacebar-commentary F9-♫ Esc,◄┘-bench` (state 340); the pitch markers per `Up` press | owner's notes 1–6 (E015-r0013) | covered-by-a-named-session | E015-r0013 (four markers on the pitch: faces `☺` at state 40, shirt numbers at 43 and 45, the letters `A`/`H` at 47 and 48, direction arrows `►`/`◄` at 49 and 50; the owner's notes name three of them: faces, numbers, A/H letters; the arrow mode is the fourth the screens show) |
| Scrollable commentary view | the screen opened by `Space`: 19 commentary lines at once, legend `↑↓,Pgup,Pgdn,Home,End-view commentary  Esc-play` | owner's notes 7, 31, 37–38; #40 | covered-by-a-named-session | E015-r0013 (states 56–60: state 58 is state 56 scrolled up by one line, "headed on by Jegor" entering at the top). The line the owner quotes in note 31, "Goal by Lentini, Schillaci is offside", is on no snapshot (no screen of the 554 unique ones holds "goal by"): observed in notes only |
| Prompts around a match, and which time out | the prompt screens and what follows them with no key | owner's notes 8–12, 17 | covered-by-a-named-session | E015-r0013: "Do you want an action replay? (Y/N)" (states 339, 736, 742): at 339 (05:29:29) no key was pressed from 05:29:20 to 05:29:55 and state 340 (05:29:49) shows the live match, so it left by itself within 20 s. "Do you want to save the match summary to disk? (Y/N)" (99, 799–800; E015-r0017 286): at 99 (05:16:34) no key until 05:17:03, state 100 (05:16:49) shows the group table with "hit any key", gone within 15 s. "Do you want to save this goal? (Y/N)" (87, 332, 737), answered `n` at state 87 (05:13:46) and `y` at 332. "Do you want to watch this match ?" (28, 101, 102–106, 111): the same screen held 54 s (states 102–106, 05:17:05–05:17:59) with no timeout, then `n` at 05:18:02. The captain prompt "◄┘-select CAPTAIN  C-computer select" (r0013 state 280, answered `c` at 05:22:02; r0017 state 202). File-name prompts "Please enter name of file : …HIL" (r0013 333) and "Please enter name of saved game : …GL" (r0013 2, 802, 803), r0017's "Do you want to load a saved game? (Y/N)" (2), "Are you sure you want to quit? (Y/N)" (296) and "Do you want to save this game? (Y/N)" (297). The timeout length is not measured: snapshots are 15–20 s apart, the owner estimates 2 s for the replay prompt |
| Goal-kick taker prompt (and its timeout) | the screen asking who takes the goal kick | owner's notes 12, 17 | needs-play | observed in notes only (E015-r0013 notes 12 and 17: the prompt comes after the captain prompt, `C` selects the computer, and it times out); no snapshot holds its screen |
| Highlight (`.HIL`) and saved-game (`.GL`) files | the files the game writes after "save this goal" and after F7 | owner's notes 9, 11, 16, 38; F002 (`Y.HIL`, `.HIL` string at `DS:06D6`) | covered-by-a-named-session | E015-r0013 (prompt "Please enter name of file : …-1▒▒▒▒▒▒.HIL" at state 333; the session's game folder holds `G-1.HIL`, 3,989 bytes like the `Y.HIL` F002 names, and `3.GL` and `4.GL`, 169,553 bytes each, which is outside the record: the record holds the prompts, not the files. Note 11 says the first save was "3B"; the folder has `3.GL`: unresolved, see the follow-ups) |
| Per-player marking: man to man, a named opponent, Protect zone | the player screen row `mark` (`man to man`, `mark─<name>`, `Protect zone`, suffix `P`); player record `+0x10` bit `0x40` ("Protect zone", F008) | owner's notes (E015-r0017 1–3, E015-r0013 20–21) | covered-by-a-named-session | E015-r0017 (the `mark` row steps through the opponents' names at states 89–123, `E Scifo` at 106 and 115; `+0x10` flips `00↔40` for players 305 (110, 120, 121, 128, 129), 316 (161, 169, 170) and 309 (180)); E015-r0013 (names at states 123–182 and 248–249; `+0x10` flips for players 316, 307, 309, 315, 318, 320, 319 between 171 and 528). Where the chosen opponent is stored is not found: `+0x13` changes at the match start (r0017 state 203: players 311, 314, 316, 318, 2565 `→00`; r0013 state 281) and on a substitution, a lead only |
| Player's own tactics (per-player settings) | the player screen rows `position  push forward`, `possession  quick pass`, `tackling  avoid injury` and the `+0xF` override byte | F010; owner's notes (r0017 1) | needs-play | — (E015-r0017: the screens show the rows, e.g. `position  push forward` at state 6, and `+0xF` of player 2565 changes `11→00` at state 58, once in the chain; no note says the owner set a per-player tactic, so the change is not attributed) |
| Formation and lineup switch | the formation shown on the tactics screen (`formation 5-4-1`, `4-4-2`) and the squad words | F028; owner's note 21 | covered-by-a-named-session | E015-r0013 (Italy, the right-hand team of the line-up screen: `5-4-0` at state 288, `5-4-1` at 323 and 344, `4-4-2` at 536 and 541, the tactics screen's own `formation` line agreeing at 344 and 541; between them the squad words reorder at state 434 and `+0x6` moves at 411–413, 443–452, 457–466) |
| Red card and the match statistics screen | the statistics screen (`Scorers`, `Corners`, `Free kicks`, `Penalties`, `Shots`, `On target`, `Saves`, `Fouls`, `Bookings`, `Red cards`, `Possession`, `Territory`), reached from the `match stats` menu option; the player record `+0x10` | owner's notes 23–25 | covered-by-a-named-session | E015-r0013 (statistics screen at states 52, 95 with `Red cards 0`, at 558 with `Red cards 1` on Portugal's side at half time 2:1; the screen text `sent off` at 568. Portugal's player 446, slot 10 of its eleven from state 288 and listed `T Oceano` at 617, has `+0x10` `00→20` at state 288 and `20→80` at 801, the first state after the match; the meaning of the `0x20` at 288 is not read) |
| Offside calls: the call lines and the disallowed goal | commentary lines `<name> is OFFSIDE` / `** LINESMAN FLAGS **`; the disallowed-goal line | owner's notes 26–30, 35–36 | covered-by-a-named-session | E015-r0013 (`Rotariu`, `Lacatus`, `Mihali` at states 36, 44, 46; `Jakanowski` 56–80; `Cadete` 286; `Domingos` at 776–777, a Portugal player on the list at 617). Which side was attacking at 776, and the disallowed goal ("Goal by Lentini, Schillaci is offside"), are observed in notes only: no snapshot shows them |
| Injury-triggered substitution request | the substitution screen texts and the injured player's `+0xE` | owner's notes 13–16 | covered-by-a-named-session | E015-r0013 (screens: `substitution requested` with `◄┘-cancel substitution request` at state 292, `◄┘-request substitution` at 302, `make substitutions now` at 313, `no more substitutes` at 790; player 311 `+0xE` `19→00` at state 288 (0 is injury, F018); the squad swap 311↔320 at state 321 is the first one after the stop, as note 15 says) |
| Post-match update (morale, fitness, energy, fixture index) | after a watched match: player records `+0xC`, `+0xD`, `+0xE`; `[A923]+0x26`; the country record's result bytes | Q015, Q013 (neighbouring) | covered-by-a-named-session | E015-r0013 (state 801: Italy's player records change `+0x8` (caps) for 16 players, `+0xC` for 15, `+0xD` for 14, `+0xE` for 19, `+0x10` for 5; the fixture index word `116→117`; Italy's country record `+0x3E..+0x40`, `+0x77..+0x7D`, `+0xAD..+0xB8` change); E015-r0017 (state 288: `+0x8` for 11 players, `+0xD` for 11, `+0xE` for 11, `+0xC` for 6; the fixture index `22→23`). What the new values mean is not read |

E015-r0007 (2026-10-11, 10.5 min, a watched friendly with Italy, DOSBox-X 2024.03.01 on the new
machine): 224 snapshots kept, but 313 of 537 save requests were superseded while the owner scrolled
lists with the arrow keys (#128), so its key/screen map has gaps in the menu and formation minutes;
the commentary screens it holds are not consecutive enough for the exact-commentary row.

E015-r0008 (2026-10-11, 22 s, window closed, recorded just before E015-r0007): a false start of 11
snapshots and 9 unique screens; no country record has +0x2E above 0x80 in it, and it covers no row.

E015-r0013 (2026-10-15, session 20261015-070348, 865 states, 39 notes; savestates published as evidence): Italy managed, a watched qualifying match (Poland v Romania, states 29–99), a skipped one (Sweden v Portugal), and a watched friendly against Portugal (states 288–800, one red card, five substitutions). The stage byte stayed `0x02` and the year word `2028` throughout: no year end. The fixture index word moved `23→24→27→50→110→113→116` over states 101–115 (the skipped round) and `116→117` at state 801. E015-r0017 (2026-10-15, session 20261015-064203, 297 states, 8 notes; savestates published): the pre-match squad, marking and speed work of the same morning, one watched match (states 200–287) against Belgium. E015-r0014, r0015 and r0016 (sittings of 2026-10-13, extracted 2026-10-15) are read here only for the two rows that cite them; their savestates are not published by this change.

### Report: what E015-r0013..r0017 filled and what remains (2026-10-15)

Filled by these records (rows above, each with the record data that shows it): repositioning (`+0x6`),
team-tactic bytes during a watched match, substitutions (five in a match, plus an injury-triggered
one), energy through a watched match, replays, the in-match speed byte against its keys, the four
player display modes, the scrollable commentary view, the prompts around a match and which of them
time out, `.HIL` and `.GL` file prompts, per-player marking, formation, the red card and the match
statistics screen, offside calls, the post-match update, pool picks (corroborated).

Observed in the owner's notes only (no snapshot holds it): the goal-kick taker prompt and its
timeout; the disallowed goal "Goal by Lentini, Schillaci is offside"; which side was attacking when
Domingos was flagged; the note 11 name "3B" of the first saved game (the folder has `3.GL`).

**Remains, and any normal play fills it**: captain / penalty / corner presets (the owner sets them
in the squad screen; r0013 only answered the captain prompt with `C`); per-player tactics set by
the owner (one `+0xF` change in r0017, unattributed); training / fitness recovery between matches
(no record moves between two matches in these chains: state 107–286 of r0013); the board, news and
transfer screens (none visited); the live commentary at a pace where consecutive snapshots share
rows (a watched match at moderate speed, as the sitting list above asks); the `Insert`
key and the recovery keys; Portugal's `+0x2D` flipping around a replay (read the cause).

**Remains, and needs a specific moment**: a knockout cup tie played to a penalty shoot-out (the
shoot-out arm of F015); a year end (stage byte `[A923]+0x3C` entering 3, 5 or 7, the season
word, retirements and new players in the squad words: the chains stayed in stage 2 of year 2028); a
World Cup cycle (the bot's path); the transfer promise line (`000E:544D`, needs a transfer
negotiation); a match in which the owner's team takes a penalty or a corner with a preset taker.

After a sitting, the main session appends a row per knowledge item the chain covered, with the
session's run id (e.g. `covered-by-a-named-session — E015-r0001` for the items the first sitting
already captured), and moves the relevant `needs-play` rows to `covered-by-a-named-session` once
the next sitting captures them. The map is the project's way of saying which facts still depend on
the owner's normal play, not on scripted scenarios.

The analysis of any one row is **not** this experiment's: it belongs to the question's own task,
which corroborates its finding against the chain.
