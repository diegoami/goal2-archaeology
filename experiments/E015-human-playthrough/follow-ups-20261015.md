# Follow-ups from the owner's sittings of 2026-10-15

For the main session to file as issues. Each line: the owner's words (the note, by the run
record's own note number and UTC time), and a one-line proposed question or task. Only what the
notes say. Note numbers and times are written by `cite_notes.py` from the records (log:
`cite-notes-20261015.log`), not by hand.

Sources: `E015-r0013` (session 20261015-070348, notes 1–39) and `E015-r0017` (session
20261015-064203, notes 1–8).

## Questions the notes leave open

| # | Source note | Proposed question or task |
| --- | --- | --- |
| 1 | r0013 note 10, 05:14:42 UTC ("replay-prompt timeout about 2 s, an estimate, not measured") | Measure how long the action-replay prompt waits before it leaves by itself (static: the wait in the prompt routine; the record only bounds it under 20 s). |
| 2 | r0013 notes 13, 17 (goal-kick taker prompt after the captain prompt; "times out") | Read the goal-kick taker prompt and its timeout statically; no snapshot holds its screen. |
| 3 | r0013 note 11, 05:17:52 UTC ("save the match summary" also times out) | Same measure as 1 for the match-summary prompt (the record bounds it under 15 s). |
| 4 | r0013 note 12, 05:18:02 UTC ("really watch it?" asks again) | Which setting makes the game ask "Do you want to watch this match ?" again, and does it ever time out (the record shows the screen on five consecutive snapshots)? |
| 5 | r0013 note 12, 05:18:02 UTC ("saves the game as 3B") | The session folder holds `3.GL`, not `3B.GL`: what name did the game write, and does the file-name prompt cut or rename the typed name? |
| 6 | r0013 notes 9, 10 (highlights "save this goal", file name) | What does a `.HIL` file hold (3,989 bytes, like `Y.HIL` in F002)? Decode its layout. |
| 7 | r0013 notes 27, 28, 31 ("Goal by Lentini, Schillaci is offside"; the game "cares too much about offside, also for the side that is not attacking") | When is a goal disallowed for a teammate's offside, and when is offside called against the defending side? Read the offside routine (`8CF5`, F026) for both. |
| 8 | r0013 note 36, 05:51:16 UTC (offside called against Portugal's Domingos while Italy attacked) | Same as 7: does the offside call depend on which side has the ball? |
| 9 | r0013 notes 23, 24, 25 (Portugal's red card; the owner's spelling "Ocean" then "T Oceano") | What triggers a sending-off, and what is stored for it: the record shows Portugal player 446's `+0x10` `00→20` at the match start and `20→80` after the match; read the meaning of `0x20` and `0x80`. |
| 10 | r0013 notes 14, 15, 16 (an injury-triggered substitution is only requested and is carried out when the game stops) | When does the game stop for a requested substitution (which events), and can the request be lost? |
| 11 | r0013 note 22, 05:37:00 UTC (marking assignments changed; "fewer players are marked now") and r0017 note 3, 04:52:55 UTC (man to man marking) | Where is the chosen marking target stored? `+0x10` bit `0x40` only flips "Protect zone"; `+0x13` changes at the match start. Find the byte, then its reader. |
| 12 | r0013 notes 2–6 (four player display modes; the owner finds the letters mode pointless) | Nothing to build; confirm the fourth mode (direction arrows) in the code and whether it has a use. |
| 13 | r0013 note 7, 05:11:23 UTC ("Space opens a mode to scroll the whole match commentary") and r0013 note 38, 05:52:59 UTC (no line numbers in the list) | How many commentary lines does the game keep for the scroll view, and is it the ring of #40? Read its size and wrap. |
| 14 | r0013 note 31, 05:43:45 UTC (the mouse wheel also scrolls the commentary) | Is the wheel mapped by DOSBox-X to Up/Down, or does the game read the mouse? |
| 15 | r0013 note 1, 05:05:13 UTC ("cycles=fixed 8000 (scale 1) is much better, a match now feels like a 1990s computer") and r0017 notes 6, 7 (too fast with cycles=max; Ctrl+F11 about 20 times hardly changed it) | Which pace setting does the owner's sitting use from now on (`cycles=fixed 8000`)? Make it the `play.sh` default and say so in the protocol; the Ctrl+F11 finding is for the pace work. |
| 16 | r0013 notes 18, 19 and r0013 note 35, 05:49:48 UTC (the replay is offered for the opponent's goals too) | Is the replay prompt offered for every goal by either side, or only some (a setting, the `INS` toggle "automatic action replay")? |
| 17 | r0017 note 1, 04:46:22 UTC (a sweeper set as centre back; two right backs at the start) | Which rules decide a player's position code on the squad screen (`R`, `C`) and does a sweeper in a centre-back slot cost the "out of position" halving (F028)? |

## The owner's wishes (a game like this)

| # | Source note | Proposed task |
| --- | --- | --- |
| 18 | r0013 note 39, 05:56:26 UTC ("a better way to search for players in the national pool") | Record as a wish for the rebuild (a searchable pool screen): list what the original pool screen offers (F011) for comparison. |
| 19 | r0013 note 39, 05:56:26 UTC ("players' names should not be the same for each team"; the meaning was not clarified) | Ask the owner what is meant (duplicate names across teams?), then check the name tables for duplicates across countries. |
| 20 | r0013 note 7, 05:11:23 UTC (the owner misses the scrollable commentary in modern football manager games) | Record as a feature for the rebuild: the whole-match commentary list with scrolling (Space, PgUp, PgDn, Home, End, Up/Down). |
| 21 | r0013 note 27, 05:40:14 UTC (the game cares too much about offside) | Record as a rebuild decision to take with the owner after 7 and 8 are read (keep or change the original's offside behaviour). |
