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
sessions. *owner* = the owner's answers on PR 242. *tool* = a statement about E031's own scripts,
not the game. *assumed* = our explanation, not traced. *F025*, *F030* = those findings. In sections
2 to 9 every sentence and table row carries a tag or a label, and every row of `claims.tsv` is cited:
`claims.py` checks both.

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

- **Function keys need raw key events.** Sent the driver's way (xdotool, the F12+S host chord), F10
  reached the game as Alt+F10: code 0xD5 in `DS:A976` and 0x71 in the BIOS buffer [C01, C01b]. The
  guest's Left Alt was held from the title screen on (`0040:0017` bit 3, `0040:0018` bit 1), and still
  after F10 [C02, C02b]. Why xdotool adds the modifier (the keysym on a level that needs one) is our
  reading, not traced (*assumed*). With raw XTEST keycodes (`xtest.py`) and the mapper
  `mapper-nohost.map` (savestate on Scroll Lock, screenshot on Pause, load on Print Screen, no F12
  chord), F10 asks to quit [C03]. The driver's fault is issue 244 (*owner*). `start.sh S --mapper ""
  --fkeys xdotool` and `play.py keystate S` reproduce it (*tool*).
- **Never press F1 under a savestate driver.** After F1, and an Esc sent blind [C04b], the next
  savestate killed DOSBox-X with exit code -6 [C04]. The help viewer was seen on a screenshot only
  [C04c]. If F1 was pressed, the session is lost: stop it and reload the last `.GL` [C04].
- **F5 (print screen)** was pressed on the menu [C05], and a Down after it still moved the menu
  [C05b]. A printout was *not seen*.
- **The pool list does not wrap**: Up at its top changed nothing [C06]. `find` turns round at an end
  (*tool*).
- **A key can be lost.** The menu key reader reads on while another key waits and keeps the last
  (*listing*: `214B:08DD`, `static/goal-exe/named/seg_214B_01.c:729`). A Down sent right after Enter
  opened team tactics was lost, and the next Enter toggled the defence row instead [C07]. So send one
  key, wait for the screen to change, then the next; `play.py send` does (*tool*). In a match, Enter
  on the captain then R at once gives the quick result [C08].
- **A saved game replays identically**: loaded twice from `G1B.GL`, with the same decisions, it gave
  Malta 1-0 Holland both times [C09, C09b]. That the random state is in the save is the explanation
  we assume (*assumed*).
- **Pace.** `play.py` launches with `cycles=fixed 8000` (*tool*), the owner's setting (*owner*);
  the prompts that time out count in emulated time (*F030*). A screen read costs about 0.2 s of
  host time [C10]. Year 2's nine friendlies, as quick results, went from the first full-time board
  at 20:33:27 to the ninth at 20:38:13 [C62, C62b]. One half watched while the screen was read without
  pause took 235 s [C10b]. The first watched match went from kick-off at 19:49:32 to full time at
  19:57:10 [C63, C63b, C63c]. The last-16 match, read every 2 s, went from 21:02:03 to its
  90-minute board at 21:05:51 [C64, C64b].
- **A crash of DOSBox-X ends the session** [C04]: start again from the last kept `.GL` [C65]. The
  server survives a killed client since it crashed on one (*tool*).

## 3. A new game

| screen | what it shows | keys |
| --- | --- | --- |
| title | "Do you want to load a saved game? (Y/N)" | `Y` with one `.GL`: the name line with its name filled in [C11]; with several: a list, Esc to type a name [C11b]; `N` a new game [C12] |
| players | "How many players 1 2 3 4 5 6 ?" [C12] | ←→, Enter [C12] |
| country selection | a team card and 16 countries; "level of difficulty" TOO EASY for Germany [C13], EASY TASK for Italy [C13b], QUITE EASY for Costa Rica [C13c], SIMPLE for Holland and Denmark [C13d] | ↑↓, ←→ the next 16, `Ins` world ranking [C14], `Space` the country's players [C14b], Enter choose [C15] |
| manager name | "Type in characters (maximum 14). ◄┘-accept Esc-abort" [C15] | the first key replaces "Player"; Enter; the papers split "Claude" into "C LAUDE" [C15b] |
| bulletins | THE SOCCER BULLETIN [C66], the qualifying groups [C66b] | any key [C66] |

With 2 players each picks a country and a name in turn, and the first manager's sixth menu option
reads **next player** [C16]. It hands the menu to the second manager [C16b]. Only Scotland had a
match in the one two-player round played (*tool*: `out/mp`).

## 4. The manager menu

| option | what it does |
| --- | --- |
| team info | every country's card; `Space` its players [C17c]; the legend offers `T` tactics [C17d] (not pressed: *not seen*); in your own fixture list Enter on a friendly cancels it [C17] and Enter on the cancelled one arranges another [C17b] |
| fixture list | Enter on another country's match marks it to watch; the hint then reads "auto result" [C18]; a marked match asks "Do you want to watch this match ?" [C35] |
| tournament | groups and results; the legend's arrows and `Space` [C19] were not pressed (*not seen*) |
| history | statistics, results by season, top scorers and caps [C20]; Down brought the country browser [C20b] |
| select squad | section 5; `Space` on the menu opens it too [C21] |
| play next game | plays on to your next match [C35]; **next player** with several managers [C16] |

`F2` changes your own name [C22, C22b]. `F3` replays a saved goal: the shipped `Y.HIL` is from the
Netherlands Antilles' 2-0 against the U.S.A [C23], and **play** shows it under REPLAY [C23b]. `F4` loads a match summary as
that match's menu [C24], whose **match stats** show its board [C24b]. `F7` saves: the name line
offers SAVED the first time [C25] and the last name used later [C25b]; a `.GL` is 169,553 bytes
[C25c]; Esc cancels (*F030*). `F10` asks "Are you sure you want to quit? (Y/N)" and then whether to
save [C26]; after the answer GOAL exits and DOSBox-X closes [C26b]. `F1` opens the help: never under
the driver [C04].

## 5. The squad screen

- `←→` toggles between your squad and the pool [C27]. Enter on a player shows "◄┘-put here" [C28].
  **Pool picks**: Enter on a pool player, `←`, Enter on the squad player he replaces: Ford took
  Wouters' place [C28b]. `pick.sh` does it (*tool*).
- **Ins** applies the assistant's 20 at once, with no question: pool players came in [C29], and
  Bergkamp [C29b, C29c], Gullit [C29d, C29e] and Rijkaard [C29f, C29g] went out. Two picks brought
  Bergkamp [C29h] and Rijkaard [C29i] back.
- **F2** renames the player on the card, "maximum 12" [C30], the first key replacing the name
  [C30b]. `ALTER.EXE` makes names permanent (*manual*).
- **R** steps the position through the 14: right winger, centre forward, striker [C31], then
  goalkeeper [C31c], and on to defensive midfield after right back [C31d]. **C** puts him back in his
  club position [C31b].
- **The formation** on the team card follows the eleven's positions: 4-4-2 [C32], 3-5-2 [C32b] and
  4-3-3 [C32c] came from picks, swaps and `R`.
- **T** opens the player's own tactics: Enter on a row goes to one option with "P" [C33] and then to
  the other [C33b]. The mark row offers "Protect zone P" [C33c] and then the opponents by name
  [C33d]. Marks are cleared after each match (*manual*).
- The card shows the status: suspended [C34], injured [C34b]. `scan 20` prints the squad (*tool*).

## 6. A round

**play next game** asks "Do you want to watch this match ?" for a match you marked [C35], a match of
your own group [C35b] and the World Cup's knockout matches [C35c]. That question never times out
(*F030*). A watched match of others goes straight to the pitch [C68], with no captain screen
[C68b], and `R` gives its result [C68c].

Your **match menu** shows the two teams and, for each, **team tactics** and **players**, then
**tournament**, **match stats** and **play** [C37]. The other side's tactics can be read, "hit any
key" back [C36]. `Ins` turns the action replay off or on, and the bottom line names the next press
[C37].

- **play** leads to the captain screen [C38]: Enter accepts the highlighted player [C38], and ↑↓
  then Enter picks another [C38b]. The highlighted one is the computer's pick, and with no key it stands after
  10 s (*F030*).
- In the match: `↑↓` changes the player marks, here to arrows [C39b]; `Left` slows the match by one »
  [C39]; `R` gives the quick result [C08]; `Space` opens the commentary view [C39c]. `F9` was not
  tried (*not seen*).
- **Half time**: the board says "hit any key  Esc,◄┘-bench" [C40]. Enter [C40b] and `Space` [C40c]
  both led to the match menu, where **play** starts the second half [C40b].
- **The bench** (**players**): a friendly allows 5 substitutions [C41]; after one change in a
  qualifier [C41b] and in the World Cup [C41c] one was left (2 per competition match: *manual*). The
  bottom line says "◄┘-take off this player" on one of the eleven [C41d] and "◄┘-put on this player"
  on a substitute [C41e]. A substitution takes two Enters, one on each man, in either order: Enter on
  one of the eleven first changed nothing visible [C41k] and Enter on the substitute then made the
  change [C41c]; Enter on the substitute first changed nothing visible [C41f] and Enter on one of the
  eleven then made it [C41i]. After that, one Esc left the screen unchanged [C41g] and a second Esc
  went to the match menu [C41j]. The substitute was still in the eleven at the next menu [C41h].
- **Prompts**: "Do you want an action replay? (Y/N)" came after a goal [C42], and after a Yes "Do you
  want to save this goal? (Y/N)" [C42b]. Both wait 6 s and then mean No, only `Y` is Yes, and with the
  replay off neither comes (*F030*). After `F3` on `Y.HIL` the file-name line showed a one-letter
  name [C42c], and the saved goal replaced `Y.HIL` in the session's copy [C42d].
- **Taker prompts**: "◄┘-select CORNER taker" [C43] and "GOAL KICK taker" [C43b] wait 10 s and keep
  the current pick; `C` takes the computer's (*F030*).
- **Substitution notices**: the other side's "SUBSTITUTION ... press any key" [C44]; your player's
  injury "<name> INJURED" [C45], then "SUBSTITUTION OPPORTUNITY press any key" [C45b]. With no
  substitution left the case was *not seen*.
- **An injury in a quick result**: if **play** is chosen with the injured man still on, the notice
  comes back again and again [C46, C46b], which is the original's behaviour (*owner*). Taking him off
  [C71] let the match go on [C71b].
- **Extra time**: level after 90 minutes in a knockout match, the match menu shows "---- EXTRA TIME
  ----" and offers **play** [C47]. Extra time has its own half time [C47b], and its length was *not
  seen*.
- **The penalty shoot-out**: "penalty shoot out  PRESS ANY KEY" [C48], then your order ("use ↑↓
  then ◄┘ to select the order  Hit Esc to undo") [C48b]. Each pick is numbered on the right [C48c].
  The kicks play out in the commentary: "<name> to shoot" [C48d], a save [C48e], the post [C48f].
  Level after five each, it went on kick for kick: Gregory's fifth saved at 5-5 [C49], a sixth for
  England [C49b] and for Holland [C49c], and Holland's sixth in [C49d]. The shoot-out came in a quick
  result too [C50]. The other side's order was *not seen*.
- **After a watched match**: the match-summary question offers `S-1` [C51], then `S-2` [C51b]. It
  waits 6 s and comes only after a watched match (*F030*).

`round` plays a round as a quick result and stops at an injury notice, a shoot-out or any unknown
screen (*tool*).

## 7. The years

A "year" is a year of the manual's four-year cycle (*owner*). The title still said 2028 after the
first year [C52], when the stage byte moved to 3 [C52b], and the history names the seasons 2027/28
and 2029/30 [C52c].

| year | stages | what came for Holland |
| --- | --- | --- |
| 1 | 2 [C75] | qualifiers and friendlies [C53] |
| 2 | 3 [C52b], 4 [C75b] | friendlies only after not qualifying [C53b] |
| 3 | 5 [C75c], 6 [C75d]; title 2030 [C52d] | World Cup qualifiers and friendlies [C53c] |
| 4 | 7 [C74], 8 [C75e] | five friendlies [C72c], the World Cup group [C72], then last 16 to third place [C72b] |
| 5 | 2 again; title 2032 [C52e] | the next cycle [C65b] |

With no fixture left the "next opponents" box is empty [C54], and **play next game** brings the
remaining results, the winners page [C55] and the next stage [C52b]. A player was a year older after
the change: Bergkamp 23 [C61], then 24 [C61b]. A retiring player's bulletin [C56] goes with a young
player taking his place in the eleven [C56b]. A squad player can quit during a stage [C57], and in
year 4 players retired between matches [C73, C57b]. The squad screen and the pool were open during
the World Cup finals [C58]; a pick there was *not seen*. The papers' advice names pool players
[C59]. A "SACK" headline [C60] is only a headline; sacking is F025's rule (*F025*). Session g1 took
the whole cycle from 19:44:37 [C65] to 21:17:58 [C65b].

## 8. Everything you can change

| what | where and how |
| --- | --- |
| country, manager name, number of players | the new game [C12, C13, C15] |
| own name | `F2` on the menu [C22] |
| team tactics | `T` on the menu, or **team tactics** on the match menu, Enter toggles a row [C07] |
| formation | the eleven's positions [C32] |
| squad | pool picks [C28b], the assistant's 20 [C29] |
| player names | `F2` on a card [C30] |
| positions | `R` and `C` [C31] |
| player tactics, marking | `T` [C33, C33d] |
| captain | the captain screen [C38b] |
| set-piece takers | the taker prompts [C43]; the shoot-out order [C48b] |
| substitutions | the bench [C41] |
| friendlies | cancel and arrange [C17, C17b] |
| other matches to watch | the fixture list [C18] |
| match speed and display | ←→ [C39], ↑↓ [C39b] |
| action replay | `Ins` on the match menu [C37] |
| save, load, quit | `F7` [C25], `Y` at the title [C11], `F10` [C26] |
| saved goals and summaries | `F3` [C23], `F4` [C24] |

## 9. What looks stuck, and what to do

| looks stuck | what it is | do |
| --- | --- | --- |
| a function key does nothing | Alt held in the guest [C01, C02] | raw keys [C03]; `keystate` (*tool*) |
| reads fail with exit code -6 | F1 was pressed [C04] | stop; reload the last `.GL` [C65] |
| "Do you want to watch this match ?" for ever | it never times out (*F030*) | `N` or `Y` |
| a file-name line for ever | it never times out (*F030*) | Enter writes, Esc cancels |
| "hit any key" at half time | the board [C40] | `Space` or Enter: the match menu [C40b, C40c] |
| play next game comes back at once | a quit or retirement bulletin [C57, C73] | check the squad, play next game again |
| "SUBSTITUTION OPPORTUNITY" again and again | the injured player is still on [C46] | take him off, then **play** [C71, C71b] |
| "penalty shoot out PRESS ANY KEY" | the shoot-out [C48] | pick the order [C48b] |
| the full-time menu offers **play** | extra time [C47] | **play** |
| one Enter on the bench changes nothing | half of a substitution [C41f, C41k] | Enter on the other man [C41i] |
| "next opponents" empty | no fixture left [C54] | play next game until the stage moves [C52b] |
| ↑ does nothing | the top of the list [C06] | ↓ |
| DOSBox-X gone after F10 | GOAL quit [C26b] | start again, `Y`, load [C11] |
