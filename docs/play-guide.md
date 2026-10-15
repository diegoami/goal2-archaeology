# Playing GOAL2: the guide

How to play the original *goal (version 2)* under the driver, from a new game to the end of a year
and on, fast and without getting stuck. Written from the E031 sessions
([`experiments/E031-play-the-game/`](../experiments/E031-play-the-game/README.md), brief
[`docs/briefs/play-the-game.md`](briefs/play-the-game.md)): every key below was pressed there, and the
session logs show the screen it led to (`screen.py g1 <step>`). The game's own manual is `GOAL.HLP`
in the release copy (`strings -n 2 .cache/goal2/GOAL.HLP`): read it once; this guide says what it
does not, and how to drive the game from a script.

## 1. Quick start for a later session

```
bash setup/goal2-runtime.sh                                    # once: the verified release copy
bash experiments/E031-play-the-game/start.sh S                 # emulator + server; prints "serving S on display :N"
python3 experiments/E031-play-the-game/play.py steps S n Return Down Down Return   # new game, 1 player, Holland
python3 experiments/E031-play-the-game/play.py type S "A Claude"                    # the manager's name
python3 experiments/E031-play-the-game/play.py steps S Return Return Return          # accept, two bulletins: the menu
bash experiments/E031-play-the-game/rounds.sh S 12             # 12 rounds as quick results (a year is ~12 matches)
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
N player cards, Down between: name, age, position, the 12 skills, condition words, status), `find
NAME` (Down, or Up, until that player's card shows), `select WORD` (move a menu's highlight onto a
word, then Enter), `advance` (Return through "hit any key" pages), `watch` (follow a match and answer
its prompts), `round` (one round as a quick result, menu to menu), `checkpoint` (keep the savestate),
`snap` (a PNG screenshot, no savestate), `note`, `stop`. `-m` marks the highlighted cells under each
row (the text alone does not say which option is selected); `G2P_ROWS=8:19 G2P_COLS=34:62` before
the command crops the printed screen. Scripts: `rounds.sh S N`, `pick.sh S "IN" "OUT"` (pool player
in, squad player out), `swap.sh S "A" "B"` (two squad players). The bash guard refuses `$VARS` and an
apostrophe inside quotes ("J Van't Ship"): spell commands out, and find such a player by a neighbour.

Proof of a run: `progress.py S --md out/S/progress.md` lists every launch, every change of the stage
and season bytes and every full-time board of your team, each with the step that shows it.

## 2. Driving the original: what breaks, and what works

- **Function keys need raw key events.** xdotool sends Left Alt with F1..F12 (it finds the keysym on
  a level that needs a modifier): the game got Alt+F10 (BIOS code `0x7100`) for F10 and ignored every
  function key, and with `keydown`/`keyup` in two calls the Alt was never released: the driver's
  host chord F12+S left the guest's Left Alt held from the launch on (`0040:0017` bit 3, `0040:0018`
  bit 1). `play.py` sends F-keys through `xtest.py` (XTestFakeKeyEvent with the server's own keycode,
  no modifier) and uses `mapper-nohost.map` (DOSBox-X's default binds with the savestate on Scroll
  Lock, the screenshot on Pause, the load on Print Screen; no F12 chord). `lastkey.py <state.sav>`
  prints the code the game last read (`DS:A976`), the BIOS buffer and the shift flags: use it when a
  key "does nothing". **`runtime/driver/driver.py` has the same fault** (every driver run so far had
  the guest's Left Alt held); not fixed here.
- **Never press F1 under a savestate driver.** The help viewer opens `GOAL.HLP`, and from then on every
  savestate kills DOSBox-X ("*** buffer overflow detected ***", exit code -6), even after Esc. The
  help is the manual above (↑↓ move, F find a word, P print, Esc leave: seen on a screenshot). If F1
  was pressed: stop the session and reload the last `.GL`.
- **F5 (print screen) is harmless**: nothing printed, the game went on.
- **Lists do not wrap**: ↑ at the top of the squad, the pool or a fixture list does nothing. `find`
  turns round at an end.
- **Keys are read one at a time; a screen just opened can drop a key.** The game reads on while
  another key waits and keeps the last (`214B:08DD`), and a Down sent right after Enter opened team
  tactics was lost once (the next Enter then toggled the wrong row). Send a key, wait for the screen to
  change, then the next (`play.py send` does). In a match a burst is fine: Enter on the captain then
  R at once gives the quick result (F004).
- **A saved game replays identically**: loading `G1B.GL` and taking the same decisions gave the same
  three results as the first time (Malta 1-0 Holland, Holland 2-1 Scotland, Luxembourg 1-2 Holland).
  The random state is in the save.
- **Pace**: `cycles=fixed 8000` (the owner's 33 MHz 386), set at launch and never changed, so the
  prompts that time out (replay, summary 6 s; taker 10 s: F030) keep their length in emulated time. A
  screen read is a savestate: about 0.2 s of host time, the emulator paused while it is written; a
  key and its settled screen 0.5 s. A round as a quick result took 30-40 s (year 2's nine friendlies:
  5 minutes); a year with its end, 6-8 minutes. A watched match at the second-fastest speed takes about
  8 minutes when the screen is read once a second (`watch --every 1`); reading without pause slows it
  (235 s for one half).
- **The server survives a lost client** (since a killed `find` crashed it once); a crash of DOSBox-X
  ends the session: start again from the last kept `.GL`.

## 3. A new game

| screen | what it shows | keys |
| --- | --- | --- |
| title | "Do you want to load a saved game? (Y/N)" | `Y` (then "Please enter name of saved game", default the only `.GL`'s name; with several a list), `N` new game |
| players | "How many players 1 2 3 4 5 6 ?" | ←→, Enter |
| country selection | a card (status, manager, rankings now/top, formation, the team's default tactics, the skills of the eleven, average caps, age, hardness, fitness, energy, morale), 16 countries, "level of difficulty" (Germany TOO EASY, Italy EASY TASK, Holland and Denmark SIMPLE, Costa Rica QUITE EASY) | ↑↓ in the list, ←→ the next/previous 16, `Ins` world ranking instead of continental, `Space` the highlighted country's players (Esc back), Enter choose |
| manager name | "Type in characters (maximum 14). ◄┘-accept Esc-abort" | the first key replaces "Player"; Enter. Type "A Name": the papers split it into an initial and a surname |
| bulletins | THE SOCCER BULLETIN (welcome; the qualifying groups) | any key |

With 2 or more players each picks a country and a name in turn; the manager menu then belongs to one
manager at a time, and its sixth option reads **next player** for all but the last, who has **play
next game** (tried with Denmark and Scotland: the round then played every managed match).

## 4. The manager menu

| option | what it does |
| --- | --- |
| team info | every country's card. ↑↓ ←→ browse, `Ins` world/continental ranking, `Space` its players, `T` tactics, Enter its fixture list. In your own fixture list Enter on a friendly **cancels** it ("CANCELLED"), Enter on a cancelled one **arranges** another (choose the opponent in the country list) |
| fixture list | every fixture of the stage (↑↓). Enter on another country's match marks it √ **watch** or back to **auto result**: a marked match asks "Do you want to watch this match ?" when it comes up |
| tournament | groups and results: ↑↓ group, `Space` continent, ←→ Qualifying / Finals / Championship |
| history | your statistics, results by season, top scorers and caps, records; an arrow goes to the country browser (Enter another country's history), Esc back |
| select squad | section 5 (`Space` on the menu opens it too) |
| play next game | plays on to your next match (section 6); **next player** with several managers |

Keys: `T` team tactics, `Space` select squad, `F2` your own name ("Type in characters (maximum 14)"),
`F3` replay a saved goal (asks a `.HIL` name; the game ships `Y.HIL`, Neth. Antilles 2 v U.S.A 0: its
match menu, **play** shows the goal, "hit any key" back), `F4` load a match summary (asks a `.SUM`
name; shows that match's menu, **match stats** its board, **exit** back), `F5` print (nothing
happens under DOSBox-X), `F7` save ("Please enter name of saved game", default the last name; Enter
writes `NAME.GL`, 169,553 bytes; Esc cancels), `F10` quit ("Are you sure you want to quit? (Y/N)",
then "Do you want to save this game? (Y/N)"; GOAL then exits to DOS and the autoexec closes
DOSBox-X), `F1` help (never: section 2).

## 5. The squad screen

The player card on the left; on the right the squad, the eleven above the line and the nine others
below (the list re-sorts by position when you leave).

- `←→` toggles between your **squad** and the **pool** (80 more players of your country). `↑↓`
  move; the card follows.
- **Enter** = "move player": the bottom line says "◄┘-put here"; Enter on another squad player swaps
  the two (into or out of the eleven). **Pool picks**: Enter on a pool player, `←`, Enter on the squad
  player he replaces; that player goes to the pool (the squad is always 20). `pick.sh` does it.
- **Ins**: the assistant's recommended 20, applied at once, no question: it changed ten of the twenty
  (it dropped Bergkamp, Gullit and Rijkaard for pool players); two picks put the best back.
- **F2**: rename the player on the card ("maximum 12"; the first key replaces the name; Enter). For
  this game only (`ALTER.EXE` changes `GOAL.DAT` for good).
- **R**: reposition: the position steps through all 14 in the order goalkeeper, sweeper, centre back,
  left back, right back, defensive midfield, central midfield, left midfield, right midfield, forward
  midfield, left winger, right winger, centre forward, striker. **C**: back to his club position.
- **The formation** on the team card is counted from the eleven's positions: 3-6-1 (Holland's own)
  became 4-4-2 with two fullbacks in and the sweeper at defensive midfield, 3-5-2 with a sweeper in and
  the left back at left midfield, 4-3-3 with a third striker.
- **T**: the player's own tactics (position, possession, passing, tackling, mark). ↑↓←→ choose a row,
  Enter cycles: the team default → one option with "P" → the other with "P" → the default. The
  **mark** row cycles zonal (or man to man, the team's default) → "Protect zone P" → "mark ─<name> P"
  through the opponents in their order. Marks are cleared after each match (manual).
- The card: age, caps, goals, height, foot, performance stars; position and club position; cards;
  status (ready to play, selected, on the bench, injured, suspended); 12 skill bars; tactics;
  hardness, fitness, energy, morale and leadership words. `scan 20` prints the squad in one go.

## 6. A round

**play next game** first plays the round's other matches (`Space` pause, ←→ speed), shows result
pages and group tables ("hit any key"), and asks "Do you want to watch this match ?" for a match you
marked, a match of your own qualifying group, or a late knockout match (`Y`/`N`; it never times out).
A watched other match goes straight to its pitch (no captain); `R` gives its result; at half time any
key goes on.

Then your **match menu**: the two teams (home on the left), and for each side **team tactics** and
**players**, then **tournament**, **match stats**, **play** (**exit** after full time). ↑↓←→, Enter.
The other side's tactics and players can be looked at, not changed. `Ins` turns the automatic action
replay off or on (the bottom line names the next press).

- **play** → the **captain** screen ("◄┘-select CAPTAIN  C-computer select"): the computer's pick is
  highlighted; Enter accepts it, ↑↓ then Enter picks another (10 s with no key keeps the pick).
- In the match: `↑↓` the player marks (faces, numbers, H/A, arrows, position letters), `←→` speed
  (the » marks; `Right` faster), `R` the quick result ("HANG ON", then the boards; "R-result" leaves
  the bottom line), `Space` the commentary (↑↓ PgUp PgDn Home End, Esc back), `F9` music, `Esc` or
  Enter the bench (the match menu, mid-match: tactics, substitutions, then **play**).
- **Half time / full time**: the statistics board, "hit any key  Esc,◄┘-bench". Any key but Enter/Esc
  goes on (to the match menu at half time: **play** for the second half); Enter or Esc opens it too.
- **The bench** (**players** on your side): "make substitutions now", "substitutions left" (5 in
  friendlies, 2 in competition matches). Enter on one of the eleven ("take off this player"), Enter on
  a substitute ("put on this player"). R, C, T, F2 as on the squad screen. Esc back. The substitute
  stays in the eleven for the next match.
- **Prompts** (F030): "Do you want an action replay? (Y/N)" after a goal (6 s, default No; none with
  the replay off), "Do you want to save this goal? (Y/N)" after a Yes (default No; Yes asks a file
  name, default **the last `.HIL` name used**: after F3 on `Y.HIL` the new goal silently overwrote
  `Y.HIL`), the taker prompts "◄┘-select CORNER / GOAL KICK taker  C-computer select" (10 s, keeps
  the pick; `C` the computer's), the other side's "SUBSTITUTION ... press any key", and for your
  side's injury "<name> INJURED" then "SUBSTITUTION OPPORTUNITY press any key" (a key opens the match
  menu: **players**, take the injured man off; with no substitution left he stays).
- After full time: **exit** → "Do you want to save the match summary to disk? (Y/N)" (watched matches
  only; Yes asks a name, default `S-<n>`, Enter writes `S-<n>.SUM`) → the result pages and the
  bulletin → the menu.

`round` plays all of this as a quick result: Enter on **play**, Enter on the captain and `R` at once,
`Space` on the boards, **play** at half time, `N` to every question, Return on every page.

## 7. The year and its end

GOAL counts stages, not calendar years (the manual's four-year cycle). This game, started in DOS year
2026, showed 2028 for its first two years: **year 1** = stage 2 (European Championship qualifying:
6 qualifiers and 6 friendlies), **year 2** = stages 3 and 4 (the finals, group then knockout: only
friendlies if you did not qualify), **year 3** = stage 5 and the season word 1, title 2030 (World Cup
qualifying, 6 qualifiers and friendlies). When your team has no fixture left, the menu's "next
opponents" box is empty: keep pressing **play next game**; the remaining results, the final table,
the winners page ("winner / second / third", top scorers) and the new bulletins come, and the stage
byte moves on. At the change every player is a year older; players retire ("<name> RETIRES FROM THE
INTERNATIONAL SCENE") and a young player takes his place in the squad, in the eleven if he was there.
During a stage a squad player who is not capped can quit ("<name> QUITS INTERNATIONAL FOOTBALL"):
**play next game** then shows that bulletin and returns to the menu without playing; check the squad,
then play next game again. The papers' advice ("BOLTON DESERVES A CAP") names pool players. A
"SACK <name>" headline is only a headline; the sacking itself is F025's rule.

## 8. Everything you can change

| what | where | how |
| --- | --- | --- |
| country, manager name, number of players | new game | section 3 |
| own name later | manager menu | `F2` |
| team tactics: defence system (half/full pitch), protection (sag back to box / stand ground), offside (play safe / offside trap); player defaults: positioning, possession, passing, tackling, marking (man to man / zonal) | `T` on the menu, team info `T`, or **team tactics** on the match menu (also mid-match) | ↑↓ row, Enter toggles |
| formation | the eleven's positions | squad screen: who is in the eleven, `R`/`C` |
| squad: pool picks and drops | squad screen | section 5; `Ins` for the assistant's 20 |
| names of players | any player card in the squad or bench screens | `F2` |
| positions | squad screen, bench | `R` (cycle of 14), `C` (club position) |
| player tactics, marking | squad screen, bench | `T` |
| captain | each match | the captain screen |
| set-piece takers | in the match | the taker prompt |
| substitutions | bench | section 6 |
| friendlies: cancel, arrange | team info → own fixtures | Enter |
| which other matches to watch | fixture list | Enter marks √ |
| match speed, display | in the match | ←→, ↑↓ |
| action replay | match menu | `Ins` |
| save, load, quit | menu, title | `F7`, `Y`, `F10` |
| saved goals and summaries | match prompts; menu | save: Y to the prompts; view: `F3`, `F4` |

## 9. What looks stuck, and what to do

| looks stuck | what it is | do |
| --- | --- | --- |
| a function key does nothing | Alt held in the guest (section 2) | `play.py` (raw keys, no host chord); check with `lastkey.py` |
| every read fails, code -6 | F1 was pressed | stop; reload the last `.GL` |
| "Do you want to watch this match ?" for ever | it never times out | `N` or `Y` |
| a file-name line for ever | never times out | Enter writes, Esc cancels |
| "hit any key" at half or full time | the board | `Space` goes on; Enter/Esc the match menu |
| play next game comes back to the menu at once | a player quit (bulletin) | check the squad, play next game again |
| "next opponents" empty | no fixture left this stage | play next game until the stage changes |
| ↑ does nothing | the top of the list | ↓ |
| the screen changes every second | a match or the round's results playing | wait (`watch`, `advance`) |
| DOSBox-X gone after F10 | GOAL quit and the autoexec closed DOSBox-X | start again, `Y`, load |
| `send` returns `changed=False` after 8 s | the key changed nothing visible (a no-op, or a choice the screen does not redraw) | read the bottom line; `lastkey.py` |
