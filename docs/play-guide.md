# Playing GOAL2: the guide

How to play the original *goal (version 2)* under the driver, from a new game to the end of a year
and on, fast and without getting stuck. Written from the E031 sessions
([`experiments/E031-play-the-game/`](../experiments/E031-play-the-game/README.md), brief
[`docs/briefs/play-the-game.md`](briefs/play-the-game.md)). The game's own manual is `GOAL.HLP` in
the release copy (`strings -n 2 .cache/goal2/GOAL.HLP`): read it once; this guide says what it does
not, and how to drive the game from a script.

**How each statement is backed.** `[Cnn]` = observed in a logged session: the row `Cnn` of
[`out/claims.md`](../experiments/E031-play-the-game/out/claims.md) names the step whose logged screen
(or log line) shows it, and `claims.py` re-checks every row against the logs (`screen.py <session>
<step>` prints the screen). *F030* = read from the listing in finding F030 (the prompts' waits,
defaults and keys): the sessions answered every prompt with a key, so no default was seen.
*listing* = read from `static/goal-exe/`. *manual* = `GOAL.HLP`. *not seen* = not observed in these
sessions. The owner's answers on PR 242 are marked *owner*.

## 1. Quick start for a later session

```
bash setup/goal2-runtime.sh                                    # once: the verified release copy
bash experiments/E031-play-the-game/start.sh S                 # emulator + server; prints "serving S on display :N"
python3 experiments/E031-play-the-game/play.py steps S n Return Down Down Return   # new game, 1 player, Holland
python3 experiments/E031-play-the-game/play.py type S "A Claude"                    # the manager's name
python3 experiments/E031-play-the-game/play.py steps S Return Return Return          # accept, two bulletins: the menu
bash experiments/E031-play-the-game/rounds.sh S 12             # 12 rounds as quick results
python3 experiments/E031-play-the-game/play.py send S F7       # save: then type a name and Return
python3 experiments/E031-play-the-game/play.py type S G1A
python3 experiments/E031-play-the-game/play.py send S Return
python3 experiments/E031-play-the-game/keepsave.py S G1A.GL "what it is"   # keep it: the game folder is wiped at each launch
python3 experiments/E031-play-the-game/play.py stop S          # ends DOSBox-X and Xvfb
bash experiments/E031-play-the-game/start.sh S --gl .cache/kept/E031/saves/G1A.GL   # later: Y at the title, Return
```

`play.py` keeps one DOSBox-X per session behind a socket, so each command is one short process. Its
commands: `send` (keys, then wait until the screen settles; `--blind N` sends without reading),
`type` (one key per character), `show`, `wait TEXT [--gone]`, `steps` (several sends), `scan N` (read
N player cards, Down between), `find NAME` (Down, or Up, until that player's card shows), `select
WORD` (move a menu's highlight onto a word, then Enter), `advance` (Return through "hit any key"
pages), `watch` (follow a match and answer its prompts), `round` (one round as a quick result, menu
to menu), `keystate` (log what reached the game: the last key code and the BIOS keyboard buffer and
flags), `checkpoint` (keep the savestate), `snap` (a PNG screenshot, no savestate), `note`, `stop`.
`-m` marks the highlighted cells under each row (the text alone does not say which option is
selected); `G2P_ROWS=8:19 G2P_COLS=34:62` before the command crops the printed screen. Scripts:
`rounds.sh S N`, `pick.sh S "IN" "OUT"` (pool player in, squad player out), `swap.sh S "A" "B"`
(two squad players), `order.sh S "A" ...` (the shoot-out order). The bash guard refuses `$VARS` and
an apostrophe inside quotes ("J Van't Ship"): spell commands out, and find such a player by a
neighbour.

Proof of a run: `progress.py S --md out/S/progress.md` lists every launch, every change of the stage
and season bytes and every full-time board of your team, each with its step; `checks.sh` re-runs
the checks the PR quotes; the saved games are on release `play-the-game-saves` (`verify_saves.py`
downloads and checks them); loading one shows the game's own **history** [C52c].

## 2. Driving the original: what breaks, and what works

- **Function keys need raw key events.** Sent the driver's way (xdotool), a function key reaches the
  game with Left Alt: F10 arrived as Alt+F10 (0x71 in the BIOS buffer, `DS:A976` = 0xD5) and the
  game ignored it [C01]; and with the F12+S host chord the guest's Left Alt is held from the title
  screen on (`0040:0017` bit 3, `0040:0018` bit 1) [C02]. That xdotool adds the modifier because the
  keysym sits on a level that needs one is our reading of its behaviour, not traced. `play.py` sends
  F-keys as raw XTEST keycodes (`xtest.py`) and uses `mapper-nohost.map` (the savestate on Scroll
  Lock, the screenshot on Pause, the load on Print Screen; no F12 chord): F10 then asks to quit [C03].
  `runtime/driver/driver.py` has the fault: issue 244 (*owner*). Reproduce it with
  `start.sh S --mapper "" --fkeys xdotool` and `play.py keystate S`.
- **Never press F1 under a savestate driver.** After F1 every savestate killed DOSBox-X ("*** buffer
  overflow detected ***", exit code -6), also after Esc [C04]. The help viewer itself was seen on a
  screenshot [C04c] (its legend: arrows move, F finds a word, P prints, Esc leaves). If F1 was pressed:
  stop the session and reload the last `.GL`.
- **F5 (print screen)**: the game went on [C05]; no printout appeared (*not seen*: nothing was
  written to the session folder).
- **The squad and pool lists do not wrap**: Up at the top of the pool changed nothing [C06]. `find`
  turns round at an end.
- **Keys are read one at a time; a screen just opened can drop a key.** The menu key reader reads on
  while another key is waiting and keeps the last (*listing*: `214B:08DD`,
  `static/goal-exe/named/seg_214B_01.c:729`), and a Down sent right after Enter opened team tactics
  was lost: the next Enter toggled the defence row instead [C07]. Send a key, wait for the screen to
  change, then the next (`play.py send` does). In a match Enter on the captain then R at once gives
  the quick result [C08] (F004).
- **A saved game replays identically**: loading `G1B.GL` and taking the same decisions gave the same
  results, e.g. Malta 1-0 Holland both times [C09]. That the random state is in the save is the
  explanation we assume, not traced.
- **Pace**: `cycles=fixed 8000` (the owner's 33 MHz 386), set at launch and never changed, so the
  prompts that time out keep their length in emulated time (*F030*). A screen read (a savestate)
  costs about 0.2 s of host time [C10]; a key and its settled screen about 0.5 s. Rounds played as
  quick results came 28 to 55 s apart (year 2's nine friendlies: steps 2007 to 2309 of
  `out/g1/progress.md`, 5 minutes). One half watched while the screen was read without pause took
  235 s [C10b]; the first watched match, kick-off to full time with a half-time substitution, took
  7.6 minutes (steps 251 to 372); the last-16 match, read every 2 s, 3.8 minutes to the 90-minute
  board (steps 3702 to 3827).
- **The server survives a lost client** since a killed `find` crashed it (the fix catches the broken
  pipe; not exercised since). A crash of DOSBox-X ends the session: start again from the last kept
  `.GL`.

## 3. A new game

| screen | what it shows | keys |
| --- | --- | --- |
| title | "Do you want to load a saved game? (Y/N)" | `Y`: with one `.GL` in the folder the name line comes with its name filled in [C11]; with several, a list ("hit ◄┘ to select saved game, hit Esc to type in a name") [C11b]. `N` new game |
| players | "How many players 1 2 3 4 5 6 ?" [C12] | ←→, Enter |
| country selection | a card (status, manager, rankings now/top, formation, the team's default tactics, the skills of the eleven, average caps, age, hardness, fitness, energy, morale), 16 countries, "level of difficulty": Germany TOO EASY, Italy EASY TASK, Costa Rica QUITE EASY, Holland and Denmark SIMPLE [C13] | ↑↓ in the list, ←→ the next/previous 16, `Ins` world ranking instead of continental [C14], `Space` the highlighted country's players [C14b] (Esc back), Enter choose |
| manager name | "Type in characters (maximum 14). ◄┘-accept Esc-abort" [C15] | the first key replaces "Player"; Enter. Type "A Name": the papers split the name into an initial and a surname ("C LAUDE" for "Claude") [C15b] |
| bulletins | THE SOCCER BULLETIN (welcome; the qualifying groups) | any key |

With 2 players each picks a country and a name in turn; the first manager's sixth menu option reads
**next player** [C16], which hands the menu to the second [C16b], whose sixth option is **play next
game** (tried with Denmark and Scotland for one round; only Scotland had a match in it).

## 4. The manager menu

| option | what it does |
| --- | --- |
| team info | every country's card: ↑↓ ←→ browse, `Ins` ranking, `Space` its players [C17c], Enter its fixture list. In your own fixture list Enter on a friendly **cancels** it [C17], Enter on the cancelled one **arranges** another: choose the opponent in the country list [C17b]. The legend offers `T` tactics [C17d] (not pressed there) |
| fixture list | every fixture of the stage. Enter on another country's match marks it √ to watch; the hint then reads "auto result" for the way back [C18]; a marked match asks "Do you want to watch this match ?" when it comes up [C35] |
| tournament | groups and results; the legend says `Space` continent, ←→ Qualifying / Finals / Championship [C19] (those keys were not pressed) |
| history | your statistics, results by season, top scorers and caps, records [C20]; Down brought the country browser [C20b] (another country's history was not opened) |
| select squad | section 5 (`Space` on the menu opens it too [C21]) |
| play next game | plays on to your next match (section 6); **next player** with several managers |

Keys: `T` team tactics, `Space` select squad, `F2` your own name [C22], `F3` replay a saved goal
(asks a `.HIL` name; the shipped `Y.HIL` is Neth. Antilles 2 v U.S.A 0 [C23]: its match menu,
**play** shows the goal under REPLAY [C23b], "hit any key" back), `F4` load a match summary (asks a
`.SUM` name; that match's menu [C24], **match stats** its board, **exit** back), `F5` print (above),
`F7` save ("Please enter name of saved game": SAVED the first time [C25], then the last name used
[C25b]; Enter writes `NAME.GL`, 169,553 bytes [C25c]; Esc cancels, *F030*), `F10` quit ("Are you sure
you want to quit? (Y/N)", then "Do you want to save this game? (Y/N)" [C26]; after the answer GOAL
exits and DOSBox-X closes [C26b]), `F1` help (never: section 2).

## 5. The squad screen

The player card on the left; on the right the squad, the eleven above the line and the nine others
below (the list re-sorts by position when you come back).

- `←→` toggles between your **squad** and the **pool** [C27] (80 more players of your country).
  `↑↓` move; the card follows.
- **Enter** = "move player": the bottom line says "◄┘-put here" [C28]; Enter on another squad player
  swaps the two (into or out of the eleven). **Pool picks**: Enter on a pool player, `←`, Enter on
  the squad player he replaces [C28b]; the squad stays at 20. `pick.sh` does it.
- **Ins**: the assistant's recommended 20, applied at once with no question [C29]; it changed ten of
  the twenty, dropping Bergkamp, Gullit and Rijkaard; two picks put the best back.
- **F2**: rename the player on the card ("maximum 12" [C30]; the first key replaces the name; Enter
  [C30b]). For this game only; `ALTER.EXE` changes `GOAL.DAT` for good (*manual*).
- **R**: reposition: the position steps through all 14 in the order goalkeeper, sweeper, centre back,
  left back, right back, defensive midfield, central midfield, left midfield, right midfield, forward
  midfield, left winger, right winger, centre forward, striker [C31, C31c, C31d]. **C**: back to his
  club position [C31b].
- **The formation** on the team card follows the eleven's positions: 4-4-2 after two fullbacks came
  in and the sweeper went to defensive midfield [C32], 3-5-2 with a sweeper in and the left back at
  left midfield [C32b], 4-3-3 with a third striker [C32c].
- **T**: the player's own tactics (position, possession, passing, tackling, mark). ↑↓←→ choose a row;
  Enter cycles the team default → one option with "P" [C33] → the other with "P" [C33b] → the
  default. The **mark** row cycles the team's marking → "Protect zone P" [C33c] → "mark─<name> P"
  through the opponents [C33d]. Marks are cleared after each match (*manual*; not checked).
- The card: age, caps, goals, height, foot, performance stars; position and club position; cards;
  status such as ready to play, selected, on the bench, injured [C34b], suspended [C34]; 12 skill
  bars; tactics; hardness, fitness, energy, morale and leadership words. `scan 20` prints the squad.

## 6. A round

**play next game** first plays the round's other matches (`Space` pause, ←→ speed: the legend),
shows result pages and group tables ("hit any key"), and asks "Do you want to watch this match ?"
for a match you marked [C35], a match of your own qualifying group [C35b] and the World Cup knockout
matches [C35c]. The question never times out (*F030*). A watched match of others has no captain
screen; `R` gives its result.

Then your **match menu**: the two teams (home on the left), and for each side **team tactics** and
**players**, then **tournament**, **match stats**, **play** (**exit** after full time). ↑↓←→, Enter.
The other side's tactics can be looked at ("hit any key" back) [C36]. `Ins` turns the automatic
action replay off or on; the bottom line names the next press [C37].

- **play** → the **captain** screen ("◄┘-select CAPTAIN  C-computer select") [C38]: Enter accepts
  the highlighted player (the computer's pick: *F030*), ↑↓ then Enter picks another [C38b]; with no
  key the pick stands after 10 s (*F030*).
- In the match: `↑↓` the player marks (arrows mode seen [C39b]; faces, numbers, H/A, position letters:
  *manual* and E015-r0013), `←→` speed (`Left` took one » away [C39]), `R` the quick result ("HANG ON"
  in the legend [C08]), `Space` the commentary view [C39c] (Esc back), `F9` music (not tried), `Esc` or
  Enter the bench (the match menu mid-match).
- **Half time / full time**: the statistics board, "hit any key  Esc,◄┘-bench" [C40]. At half time
  both Enter [C40b] and `Space` [C40c] led to the match menu: **play** for the second half.
- **The bench** (**players** on your side): "make substitutions now", "substitutions left": 5 in a
  friendly [C41]; one left after one change in a qualifier [C41b] and in the World Cup [C41c] (2 per
  competition match: *manual*). The bottom line follows the cursor: "◄┘-take off this player" on one
  of the eleven [C41d], "◄┘-put on this player" on a substitute [C41e]. Enter on the man to take off
  (the screen does not change), then Enter on the substitute (the counter drops). Enter on a
  substitute alone did nothing [C41f]. R, C, T, F2 as on the squad screen. Esc back; an Esc sent right
  after a substitution was lost once [C41g]: send it again. The substitute stays in the eleven for the
  next match [C41h] (F029).
- **Prompts**: "Do you want an action replay? (Y/N)" after a goal [C42], "Do you want to save this
  goal? (Y/N)" after a Yes [C42b]; both wait 6 s and then mean No, and only `Y` is Yes (*F030*); with
  the replay off neither comes (*F030*). Yes to the second asks a file name, whose default is the last
  `.HIL` name used: after `F3` on `Y.HIL` the line showed a one-letter name [C42c] and the goal was
  written over `Y.HIL` without a question [C42d] (in the session's copy). The taker prompts
  "◄┘-select CORNER / GOAL KICK taker  C-computer select" [C43] wait 10 s and keep the current pick
  (*F030*); `C` takes the computer's. The other side's substitutions show "SUBSTITUTION ... press any
  key" [C44]. Your player's injury shows "<name> INJURED", then "SUBSTITUTION OPPORTUNITY press any
  key" [C45]; a key opens the match menu: **players**, take the injured man off. What happens with no
  substitution left: *not seen*.
- **An injury in a quick result**: the notice comes in the quick result too. If you choose **play**
  without taking the injured man off, the result runs on a little and the notice comes back, again
  and again [C46] (a script that just answered it looped about 90 times in the 2030 third-place
  match). This is the original's behaviour (*owner*). Take him off (**players**), then **play**.
- **Extra time** (a knockout match level after 90 minutes): the board and the match menu show "----
  EXTRA TIME ----" and the option is **play** again, not **exit** [C47]; extra time has a half time
  that ends at the match menu [C47b]. Its length was not measured (*not seen*).
- **The penalty shoot-out**: "penalty shoot out  PRESS ANY KEY" [C48], then your order: "use ↑↓ then
  ◄┘ to select the order  Hit Esc to undo" [C48b]: choose the takers one by one; each pick leaves the
  list and is numbered on the right [C48c] (`order.sh`; `scan 11` reads each man's penalties bar).
  The kicks then play out in the commentary: "<name> to shoot" [C48d], goals, saves [C48e], the post
  [C48f]. After five each level it went on kick for kick (sudden death): Gregory's fifth saved, 5-5 on
  the board [C49], a sixth for England [C49b] and for Holland [C49c], and Holland's sixth in [C49d].
  The shoot-out came in a quick result too [C50]. The other side's order: no screen for it was seen.
- After full time of a watched match: **exit** → "Do you want to save the match summary to disk?
  (Y/N)" (6 s, then No: *F030*; asked only after a watched match: *F030*); Yes asks a name, default
  `S-1` [C51], then `S-2` [C51b]; Enter writes it → the result pages and the bulletin → the menu.

`round` plays all of this as a quick result: Enter on **play**, Enter on the captain and `R` at once,
`Space` on the boards, **play** at half time and in extra time, `N` to every question, Return on
every page; it stops (printing the screen) at an injury's substitution opportunity, at a shoot-out,
and at any screen it does not know, for you to decide.

## 7. The years

A "year" here is a year of the manual's four-year cycle (*owner*: this reading is right); GOAL counts
stages. This game, started in DOS year 2026, still showed 2028 after its first year [C52, C52b] and
its history calls the first two years season 2027/28 and the next two 2029/30 [C52c]:

| year | stages (`[A923]+0x3C`) | what came for Holland |
| --- | --- | --- |
| 1 | 2 | European Championship qualifying: 6 qualifiers and 6 friendlies [C53] |
| 2 | 3, 4 | the finals (group, then knockout); not qualified: 9 friendlies [C53b] |
| 3 | 5, 6 (season word 1, title 2030 [C52d]) | World Cup qualifying: 6 qualifiers and 4 friendlies [C53c]; stage 6 brought no Holland match (other continents' play-offs: *manual*) |
| 4 | 7, 8 | friendlies, the World Cup group of four, then last 16, quarter-final, semi-final, third place (`out/g1/progress.md`) |
| 5 | 2 again (season word 2, title 2032 [C52e]) | the next cycle |

When your team has no fixture left the menu's "next opponents" box is empty [C54]: keep pressing
**play next game**; the remaining results, the final tables, the winners page [C55] and the new
bulletins come, and the stage byte moves on. At the year's change the players grow a year older
(Bergkamp 23 [C61], then 24 [C61b]; F016 for all of them). Players retire ("<name> RETIRES FROM THE INTERNATIONAL SCENE")
[C56] and a young player takes the place, in the eleven if the retired man was there [C56b]. During a
stage a squad player can quit ("QUITS INTERNATIONAL FOOTBALL") [C57] or give up and retire [C57b]:
**play next game** then shows that bulletin and returns to the menu without playing; check the
squad, then play next game again. It came again and again in year 4. The squad screen and the pool
stayed open during the World Cup finals [C58]; a pick there was not tried (the manual says none is
allowed). The papers' advice ("BOLTON DESERVES A CAP") names a pool player [C59]. A "SACK <name>"
headline [C60] is only a headline; the sacking rule is F025's.

Session g1 took 94 minutes of host time for the whole cycle (19:44 to 21:18 UTC in
`out/g1/progress.md`), with the exploration, the watched matches and one crash replayed.

## 8. Everything you can change

| what | where | how |
| --- | --- | --- |
| country, manager name, number of players | new game | section 3 |
| own name later | manager menu | `F2` [C22] |
| team tactics: defence system (half/full pitch), protection (sag back to box / stand ground), offside (play safe / offside trap); player defaults: positioning, possession, passing, tackling, marking (man to man / zonal) | `T` on the menu, or **team tactics** on the match menu, also mid-match | ↑↓ row, Enter toggles [C07] |
| formation | the eleven's positions | squad screen: who is in the eleven, `R`/`C` [C32] |
| squad: pool picks and drops | squad screen | section 5; `Ins` for the assistant's 20 [C29] |
| names of players | a player card in the squad or bench screens | `F2` [C30] |
| positions | squad screen, bench | `R` (cycle of 14), `C` (club position) [C31] |
| player tactics, marking | squad screen, bench | `T` [C33] |
| captain | each match | the captain screen [C38b] |
| set-piece takers | in the match | the taker prompt [C43]; the shoot-out order [C48b] |
| substitutions | bench | section 6 [C41] |
| friendlies: cancel, arrange | team info → own fixtures | Enter [C17] |
| which other matches to watch | fixture list | Enter marks √ [C18] |
| match speed, display | in the match | ←→, ↑↓ [C39] |
| action replay | match menu | `Ins` [C37] |
| save, load, quit | menu, title | `F7`, `Y`, `F10` [C25, C11, C26] |
| saved goals and summaries | match prompts; menu | save: Y to the prompts; view: `F3` [C23], `F4` [C24] |

## 9. What looks stuck, and what to do

| looks stuck | what it is | do |
| --- | --- | --- |
| a function key does nothing | Alt held in the guest [C01, C02] | `play.py` (raw keys, no host chord); check with `keystate` |
| every read fails, code -6 | F1 was pressed [C04] | stop; reload the last `.GL` |
| "Do you want to watch this match ?" for ever | it never times out (*F030*) | `N` or `Y` |
| a file-name line for ever | it never times out (*F030*) | Enter writes, Esc cancels |
| "hit any key" at half or full time | the board [C40] | `Space` goes on; Enter/Esc the match menu |
| play next game comes back to the menu at once | a player quit or retired [C57] | check the squad, play next game again |
| "SUBSTITUTION OPPORTUNITY" again and again in a quick result | your injured player is still on [C46] | take him off on the bench, then **play** |
| "penalty shoot out PRESS ANY KEY", then a list | the shoot-out order [C48b] | pick the takers (`order.sh`) |
| the full-time match menu offers **play**, not **exit** | extra time [C47] | **play** |
| Enter on the bench changes nothing | the cursor is on a substitute [C41f] | Enter on one of the eleven, then on the substitute |
| "next opponents" empty | no fixture left this stage [C54] | play next game until the stage changes |
| ↑ does nothing | the top of the list [C06] | ↓ |
| the screen changes every second | a match or the round's results playing | wait (`watch`, `advance`) |
| DOSBox-X gone after F10 | GOAL quit and DOSBox-X closed [C26b] | start again, `Y`, load |
| `send` returns `changed=False` after 8 s | the key changed nothing visible (a no-op, a dropped key [C41g], or a choice the screen does not redraw) | read the bottom line; `keystate` |
