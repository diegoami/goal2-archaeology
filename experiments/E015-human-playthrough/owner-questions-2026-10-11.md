# Questions to the owner, 2026-10-11

The owner's request (2026-10-11): mine what the sittings hold, then ask where the uncertainty is,
as a report to fill in. The mined part is [E015-r0007-mined.md](E015-r0007-mined.md); the open
rows are the coverage map in [protocol.md](protocol.md) and the backlog
([docs/backlog.md](../../docs/backlog.md)).

**How the answers count.** An answer is the owner's testimony, tagged `owner` where it is cited.
It can set the rebuild's screens and flow, decide what the bot is for, and choose what research
looks at next. It never makes a game rule `corroborated` by itself (CLAUDE.md rule 19): a rule
still needs its static reading, and a sitting where possible. "Don't know" and "not sure" are
answers too; a guess marked as a guess is welcome.

**How to fill it in.** Write after each `Answer:` (any length): in GitHub's editor on PR #134's
branch `e015/mined-and-questions`, in a clone on either computer (commit and push to that branch),
or in chat to the main session, which writes them in. Leave out whatever you don't want to answer.

Only questions the code and the sittings cannot answer cheaply are here. What static analysis
will answer anyway (formulas, constants, the meaning of a byte) is not asked.

## A. Today's sitting: what you meant

A1. Before the match you watched Greece v Hungary, another friendly of the round. Why: to see how
the game plays, to scout, or by habit? Do you usually watch other matches?
Answer: No, I thought that it was useful for the game mining

A2. During the match you set "stand ground" and took it off again at once, then switched to half
pitch and to keep ball, all at 0:0. What were you trying to do, and did you see any effect on the
pitch or in the commentary?
Answer: It seems to fit more with Italy's playing style, defensive and on the coutner

A3. You made three substitutions (Maldini, Di Chiara, Vialli off; Vierchowod, Stroppa, Baggio on),
and after the match the three substitutes were still in the first eleven for the Belgium qualifier.
Did you expect that? Do you remember whether the game always keeps the substitutes in the eleven,
or whether you had to put the team back yourself?
Answer: Yes, the starting squad is not affected by substitutions in game

A4. You chose Italy and difficulty SIMPLE. Why Italy? Do you know what the difficulty levels
change, and which level should the rebuild and the bot aim at?
Answer: It is not a difficulty level, Italy is a strong team, that is why it is considered Simple

## B. Screens and controls you know (settles needs-play rows)

B1. Is there a way to choose a captain, a penalty taker or a corner taker? If yes, where (which
screen, which key)? (coverage row "Captain / penalty / corner presets")
Answer: There is a screen but I do not remember it

B2. Have you seen a screen or message about a "transfer promise", or any transfer of a player
between countries? What did it say, and when did it appear? (row "Transfer promise line", Q014)
Answer: No, not between countries

B3. Is there any training, rest or fitness choice between matches, or do players recover on their
own? (row "Training / fitness recovery", Q015)
Answer: No training or fitness choice in this game, you train a national squad and you choose the best or more fit players  from a national pool

B4. What do the newspapers or the board tell you over a campaign: praise, warnings, a sacking?
Have you ever been sacked, and what led to it? (row "Board / confidence / morale"; the
"Sacking and the end of the game" placeholder)
Answer: I have not been sacked but again did not pay long enough

B5. Do you use the action replays, or turn them off? Anything in a replay that the commentary does
not show? (row "Watched-match replays")
Answer: Replays are more of an annoyance

B6. Which keys and screens do you use most in normal play, and which never? Anything that
confused you or that you had to learn by trial? (row "Screen-flow controls during normal play")
Answer: mostly the arrows key to sped up and slow down the game. then some like Y to skip replay, C for computer choice and then Esc to go back to screen and some other keys to navigate in the team and tactic view to pick up choices and sometimes to rename players  

B7. Have you played with more than one human manager (up to 6)? Should the rebuild support it?
Answer: Never, but it should be supported

## C. What you have seen over whole campaigns (Q006, Q008, Q020, Q028, Q030-Q036)

C1. Describe a full cycle as you remember it: qualifying groups, the continental championship, the
World Cup finals (groups, knockouts, extra time, penalties). Anything that surprised you?
Answer: The usual cycle of national games, nothing surprising

C2. How many substitutions does a competition match allow (a friendly showed 5)? Can a substitute
come back on? (Q034)
Answer: No a substitute is out and the rule is general 5 players substitutions

C3. How long do injuries and suspensions last, as you remember them? Do players miss matches after
a red card or a number of bookings? (Q033)
Answer: Yes they should

C4. When do the world and continental rankings move: after every match, after tournaments only?
(Q020)
Answer: No idea

C5. Do computer-managed teams seem to change tactics or players during a match, or between
matches? (Q035, Q036)
Answer: No idea, it is possible, probably not

C6. Does playing at home seem to matter? Is a continental title easier outside Europe? (Q028, Q006)
Answer: It might but could not measer

C7. When can you not change your squad (finals, tours)? What does the assistant's pick do for you?
(Q008)
Answer: I do not know if there is an assistant, you can choose players from a national pool but not when when they are on a tournament

## D. What the rebuild and the bot are for

D1. Which parts of the game must the rebuild get exactly right for you (match engine, screens,
competitions, player development), and which can be simpler or modern?
Answer: Guess most of it, but the UI can and should be improved. 

D2. The bot's goal is the World Cup win rate. With which country, at which difficulty, from which
starting point (a new game, or a saved game like `1.GL`)? Should it play whole campaigns, or only
the matches?
Answer: Well it does not have to win the world cup but it must be competent enough to allow idle gaming

## E. Material you may have

E1. Do you have older GOAL2 saved games (`.GL`), match summaries (`.SUM`) or highlights (`.HIL`)
from earlier play, a printed manual, or notes? Each is evidence the project cannot make itself.
Answer: No, I can produce them

E2. May the main session publish today's `1.GL` (your saved game, 169,553 bytes) to release E015 as
evidence? It holds no personal data beyond the manager name "E Go".
Answer: Sure

## What the answers change (the main session, 2026-10-11)

Testimony (`owner`), read against the records; nothing here makes a rule `corroborated`.

- **A3 against the record.** The owner: substitutions do not change the starting squad. E015-r0007
  holds the substitutes in the first eleven from state 113 through state 224 (after the save), and
  the sitting ended before the next match. Both can hold: the stored order survives the match, and
  the game may restore the eleven when the next match starts. Open: the next sitting shows whether
  the Belgium qualifier starts with Maldini, Di Chiara and Vialli.
- **A4.** "level of difficulty : SIMPLE" on the country screen is not a game setting: it rates the
  country (Italy is strong). [E015-r0007-mined.md](E015-r0007-mined.md) is corrected; where the
  label comes from is a static question.
- **B1.** A captain / penalty / corner screen exists; the owner does not remember where. The
  coverage row stays needs-play; the screen catalogue (T39a) and a coaching session find it.
- **B2.** No transfers between countries: the "transfer promise" line (`000E:544D`) is something
  else, still open.
- **B3.** No training or fitness choice: fitness recovers on its own; the manager picks fit players
  from the pool. The coverage row "Training / fitness recovery" is about that recovery only.
- **B5, B6.** Replays are an annoyance. Keys used: the arrows for the match speed, `Y` to skip a
  replay, `C` for the computer's choice, `Esc` back, others in the team and tactics views, and
  renaming players. They go into the screen catalogue as `owner` rows.
- **B7.** Several human managers: never played, but the rebuild should support them.
- **C2.** Five substitutions in every match, and a substituted player stays off. `GOAL.HLP` 254–259
  says 2 in competition, 5 in friendlies: Q034 settles it from the code.
- **C3.** Injured and suspended players miss matches (Q033's premise).
- **C7.** No assistant the owner knows of; the squad changes from the national pool, not during a
  tournament (Q008).
- **D1.** The rebuild keeps most of the game; its UI can and should be improved.
- **D2.** The bot need not win the World Cup: it must be competent enough to allow idle gaming.
  This changes the plan's G-M5 goal (U15, "the best World Cup win rate"): a design decision for the
  owner to confirm in [plan.md](../../docs/plan.md).
- **E1.** No older saved games, summaries or highlights; the owner can produce them on request.
- **E2.** Yes: `1.GL` may be published. A published manifest is never rewritten, so it needs its own
  record: a follow-up.
