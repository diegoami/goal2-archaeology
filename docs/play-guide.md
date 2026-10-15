# Playing GOAL2: the guide

How to play the original *goal (version 2)* under the driver, from a new game to the end of a year
and on, fast and without getting stuck. Written from the E031 sessions
([`experiments/E031-play-the-game/`](../experiments/E031-play-the-game/README.md), brief
[`docs/briefs/play-the-game.md`](briefs/play-the-game.md)); every key below was pressed there, and the
step logs show the screen it led to. The game's own manual is `GOAL.HLP` in the release copy
(`strings -n 2 .cache/goal2/GOAL.HLP`): read it once; this guide says what it does not.

## 1. Quick start (a later session)

```
bash setup/goal2-runtime.sh                                  # once: the verified release copy
bash experiments/E031-play-the-game/start.sh S [--gl FILE.GL] # one emulator, its own display; prints "serving"
P=experiments/E031-play-the-game/play.py                      # (spell it out: the guard refuses variables)
python3 $P steps S n Return Down Down Return                  # new game, 1 player, Holland (3rd in Europe's list)
python3 $P type S "A Claude"; python3 $P steps S Return Return Return   # manager name, two bulletins: the menu
python3 $P round S -q                                         # one round as a quick result, menu to menu
python3 $P send S F7; python3 $P type S NAME; python3 $P send S Return  # save NAME.GL in the game folder
python3 experiments/E031-play-the-game/keepsave.py S NAME.GL "what it is" # keep it (the folder is wiped at launch)
python3 $P stop S                                             # ends DOSBox-X and Xvfb
```

`play.py` holds one DOSBox-X per session behind a socket; every request is logged to
`out/<S>/steps.jsonl` with the game's progress bytes (season word, stage byte, fixture index), and
every distinct screen to `out/<S>/screens.jsonl`. Its commands: `send` (keys, then wait until the
screen settles), `type` (one key per character), `show`, `wait` (until a text appears), `scan`
(read N player cards, Down between), `find` (Down/Up until a player's card shows), `select` (move a
menu highlight onto a word, then Enter), `advance` (Return through "hit any key" pages), `watch`
(follow a watched match and answer its prompts), `round` (a whole round as a quick result),
`checkpoint` (keep the savestate), `snap` (a PNG screenshot, no savestate), `note`, `stop`. `-m`
marks the highlighted cells under each row: the text alone does not show which option is selected.

## 2. Driving the original: what breaks and what works

- **Function keys need raw key events.** xdotool sends Left Alt with F1..F12 (it finds the keysym on
  a level that needs a modifier): the game received Alt+F10 (BIOS code `0x7100`) instead of F10, and
  every function key was ignored. With `keydown`/`keyup` in separate calls the Alt was never
  released, and the driver's host chord F12+S left the guest's Left Alt held from the launch on
  (BIOS flags `0040:0017` bit 3). `play.py` sends F-keys through `xtest.py` (XTestFakeKeyEvent with
  the server's own keycode, no modifier) and uses `mapper-nohost.map` (savestate on Scroll Lock,
  screenshot on Pause, load on Print Screen; no F12 chord at all). `lastkey.py <state.sav>` prints
  the last key code the game read (`DS:A976`) and the BIOS buffer and flags: use it when a key
  "does nothing". **This also affects `runtime/driver/driver.py`**: every driver run so far had
  the guest's Left Alt held (reported, not fixed here).
- **Never press F1 under a savestate driver.** The help viewer opens `GOAL.HLP`; from then on every
  savestate kills DOSBox-X ("buffer overflow detected", exit code -6), even after Esc. The help is
  the manual above. If it was pressed, the session is lost: stop it and reload the last `.GL`.
- **Lists do not wrap.** Up at the top of a list (squad, pool, fixtures) does nothing; `find`
  reverses at the end.
- **The game keeps only the last key of a burst** (`214B:08DD` reads on while another key is
  waiting), except in the match, where a burst such as Enter, R is read key by key (F004). Send one
  key, wait for the screen to change, then the next; `play.py send` does that.
- **A saved game replays identically.** Loading `G1B.GL` and making the same choices gave the
  same three results (Malta 1-0 Holland, Holland 2-1 Scotland, Luxembourg 1-2 Holland) as the first
  time: the random state is in the save.
- **Pace.** The owner plays at `cycles=fixed 8000` (a 33 MHz 386); `play.py` uses it. One screen
  read (a savestate) costs about 0.2 s of host time and pauses the emulator while it is written;
  a key and its settled screen about 0.5 s. A watched half at the second-fastest speed took 235 s
  when the screen was read continuously; read it once a second (`watch --every 1`). A round played
  as a quick result takes about a minute and a half. The prompts that time out (replay, summary:
  6 s; taker: 10 s) are counted in the emulated machine's time (F030), so they are safe at any pace
  as long as the speed is not changed after the launch.

## 3. From a new game to the manager menu

| screen | what it shows | keys |
| --- | --- | --- |
| title | "Do you want to load a saved game? (Y/N)" | `Y` load (next: the file-name line, default the only `.GL`'s name, or a list when there are several), `N` new game |
| players | "How many players 1 2 3 4 5 6 ?" | ←→ choose, Enter |
| country selection | a country card (manager, ranking, formation, the team's default tactics, skills, average condition) and a list of 16 countries; "level of difficulty" above (Germany TOO EASY, Holland SIMPLE, Italy EASY TASK, Costa Rica QUITE EASY) | ↑↓ in the list, ←→ the next or previous 16, `Ins` world ranking instead of continental, `Space` the highlighted country's players (Esc back), Enter choose |
| manager name | "Type in characters (maximum 14). ◄┘-accept Esc-abort" | the first key replaces the default "Player"; Enter. Write it "A Name": the papers split it into initial and surname |
| bulletins | THE SOCCER BULLETIN pages (welcome, the groups) | any key |

## 4. The manager menu

Six options (↑↓, Enter), the squad list on the right, the next opponents and the fixture kind on the
left, and the F-keys on the bottom line.

| option | what it does |
| --- | --- |
| team info | every country's card. ↑↓ ←→ browse, `Ins` world/continental ranking, `Space` its players, Enter its fixture list: for your own country, Enter on a friendly **cancels** it ("CANCELLED"), Enter on a cancelled one **arranges** a new friendly (choose the opponent from the country list). `T` on your own card: team tactics |
| fixture list | every fixture of the round (↑↓ scroll). Enter on a match that is not yours marks it **watch** (√) or back to **auto result**; a marked match asks "Do you want to watch this match ?" when it comes up |
| tournament | the groups and results of the competitions: ↑↓ group, `Space` continent, ←→ Qualifying / Finals / Championship |
| history | your country's statistics, results by year, top scorers and caps, records; any arrow goes to the country browser (Enter another country's history), Esc back |
| select squad | the squad screen (section 5); `Space` on the menu opens it directly |
| play next game | plays on to your next match (section 6) |

Keys on the menu: `T` team tactics, `Space` select squad, `F2` your own name, `F3` replay a saved
goal (`.HIL`), `F4` load a match summary (`.SUM`), `F5` print the screen (not tried: no printer),
`F7` save ("Please enter name of saved game", default the last name, Enter writes `NAME.GL`, Esc
cancels), `F10` quit ("Are you sure you want to quit? (Y/N)", then "Do you want to save this game?
(Y/N)"; after the answer GOAL exits to DOS and the session's DOSBox-X closes), `F1` help (do not:
section 2).

## 5. The squad screen (select squad)

The player card on the left, the squad on the right: the eleven, a line, then the nine others.

- **←→** toggles between your squad and the **pool** (80 other players of your country). **↑↓** move,
  the card follows.
- **Enter** = "move player": the bottom line changes to "◄┘-put here"; Enter on another squad player
  swaps the two (into or out of the eleven). Enter on a **pool** player, then ← to the squad and Enter
  on a squad player, puts the pool player in that place and sends the other to the pool: that is how
  you pick and drop (the squad is always 20).
- **Ins**: the assistant's recommended 20 (not tried).
- **F2**: rename the player on the card ("Type in characters (maximum 12)"; the first key replaces
  the name; Enter). The name lasts for this game only (ALTER.EXE changes GOAL.DAT for good).
- **R**: reposition: the player's position steps through all 14, in the order goalkeeper, sweeper,
  centre back, left back, right back, defensive midfield, central midfield, left midfield, right
  midfield, forward midfield, left winger, right winger, centre forward, striker. **C**: back to his
  club position. The formation on the team card follows the eleven's positions (3-6-1 became 4-4-2
  after two fullbacks came in, the sweeper went to defensive midfield and a winger to centre forward).
- **T**: the player's own tactics (position, possession, passing, tackling, mark): ↑↓←→ choose a row,
  Enter cycles team default → one option "P" → the other "P" → default (e.g. "stay back P",
  "push forward P"). Esc back.
- The card: age, caps, goals, height, foot, performance stars; position and club position; cards;
  status ("ready to play", "selected", "on the bench", injured, suspended); 12 skill bars; tactics;
  hardness, fitness, energy, morale, leadership words. `scan` prints them all, one line a player.

## 6. A round

"play next game" first shows the round's other results being played (`Space` pause, ←→ speed),
pages of results and group tables ("hit any key"), and "Do you want to watch this match ?" for any
match marked to watch or of a late world stage (`Y`/`N`; it never times out). Then your match's
**match menu**: your team (left or right: the home side is on the left), the opponents, and the
options **team tactics** and **players** for each side, **tournament**, **match stats**, **play**
(**exit** after full time). ↑↓←→ move, Enter.

- **play** → the **captain** screen ("◄┘-select CAPTAIN  C-computer select": the computer's pick is
  highlighted; Enter accepts, ↑↓ then Enter picks another; with no key the pick stands after 10 s).
- The match: `↑↓` display (faces, numbers, H/A letters, arrows, position letters), `←→` speed,
  `R` result (quick result: "HANG ON", then the half-time and full-time boards), `Space` the
  commentary (↑↓ PgUp PgDn Home End, Esc back), `F9` music, `Esc`/Enter the bench, `Ins` (on the
  match menu) the automatic action replay on/off.
- Half time and full time: the statistics **board**, "hit any key  Esc,◄┘-bench". Any key but Enter
  or Esc goes on (to the match menu: choose **play** for the second half); Enter or Esc opens the
  bench first.
- **The bench** ("players" on the match menu, or Enter/Esc in play): "make substitutions now",
  "substitutions left 5" (friendlies; 2 in competitions). Enter on a player of the eleven ("take off
  this player"), then Enter on a substitute ("put on this player"). `R`/`C`/`T`/`F2` as on the squad
  screen. A substitution stays after the match: the substitute is in the eleven for the next match
  (F029). Esc back to the match menu.
- Prompts during the match (F030): "Do you want an action replay? (Y/N)" after a goal (6 s, default
  No), "Do you want to save this goal? (Y/N)" after a replay (default No; Yes asks a `.HIL` name),
  the set-piece taker (10 s, keeps the current pick; `C` the computer's), the other side's
  "SUBSTITUTION ... press any key".
- After full time: **exit** → "Do you want to save the match summary to disk? (Y/N)" (only for a
  watched match; Yes asks a name, default `S-1`, Enter writes `S-1.SUM`) → the bulletin → the menu.

## 7. Everything you can change

| what | where | how |
| --- | --- | --- |
| country, manager name, number of players | new game | section 3 |
| own name later | manager menu | `F2` |
| team tactics (defence system half/full pitch, protection sag back/stand ground, offside play safe/offside trap; player defaults: positioning, possession, passing, tackling, marking) | `T` on the menu, team info `T`, or "team tactics" on the match menu | ↑↓ row, Enter toggles |
| formation | the eleven's positions | squad screen `R`/`C` and who is in the eleven |
| squad picks and drops | squad screen | pool ↔ squad, section 5 |
| player names | squad screen, bench, any player card | `F2` |
| player positions | squad screen, bench | `R` (cycle), `C` (club position) |
| player tactics, marking | squad screen, bench | `T` |
| captain | before kick-off | captain screen |
| set-piece takers | in the match | the taker prompt |
| substitutions | bench | section 6 |
| friendlies | team info → own fixtures | Enter cancels / arranges |
| which other matches to watch | fixture list | Enter marks |
| match speed, display | in the match | ←→, ↑↓ |
| action replay on/off | match menu | `Ins` |
| save, load, quit | menu | `F7`, title `Y`, `F10` |

## 8. What looks stuck, and what to do

| looks stuck | what it is | do |
| --- | --- | --- |
| a function key does nothing | Alt held in the guest (section 2) | use `play.py`; check with `lastkey.py` |
| every read fails with code -6 | F1 was pressed | stop, reload the last `.GL` |
| "Do you want to watch this match ?" for ever | it never times out | `N` (or `Y`) |
| a file-name line for ever | never times out | Enter writes, Esc cancels |
| "hit any key" at half time | the board waits | `Space` goes on; Enter/Esc opens the bench |
| ↑ does nothing in a list | the top of the list | ↓ |
| the screen changes on its own every second | a match or the round's results being played | wait (`watch`, `advance`) |
| DOSBox-X gone after `F10` | GOAL quit to DOS and the autoexec closed DOSBox-X | start again, `Y`, load |
