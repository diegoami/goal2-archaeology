# The watched match engine: how to get there, and what it costs

The owner's brief of 2026-10-15 (`docs/briefs/match-engine-plan.md`): replicate the engine that plays a
watched match (`0791:9564` and what it reaches, F013), or something close enough that goals, shots,
possession, fouls and cards come out with the original's distributions and skills, form and tactics move
results as they do there; a practical route, no long sessions, assumptions where finding out costs too
much. The numbers below come from E032 (`experiments/E032-match-engine-inventory/`, `notes.md`), measured
for this plan on the original's own code in the Unicorn harness. This page holds no status; the labels do.

## In short

- **Port the engine's code, do not re-invent it, and check whole matches instead of proving routines.**
  The engine is about 190 routines and 14,000 instructions. Each part is translated from the listing into
  Python that reads and writes the same bytes as the original, dropped into the Unicorn harness in place of
  the original routines, and accepted when whole matches stay identical draw for draw over a family of
  seeds. A wrong port changes the match at once; the side-by-side proof that made M1-M2 slow is kept only
  to find where a port is wrong.
- **It is cheaper than the alternatives, including "close enough".** E032's pilot ported the player's run
  step (`8889`, `86D0` and five helpers with the set test and the draws: 555 static instructions) in about
  40 minutes; it was identical in 10 of 10 whole matches (about 93,000 calls each) and each of three
  deliberate errors changed the match. A match of the original now costs 8.3-16.8 CPU seconds instead of
  19.5-50.8 (the delay count written at kick-off, 10 of 10 matches unchanged). Showing that a re-invented
  engine is "close enough" takes hundreds of oracle matches per effect, and every gap found means changing
  the model and measuring again; a step of the port is checked in 12.0 CPU minutes (6.0 elapsed on two
  workers).
- **Cost: about 50 hours of implementer time (49.5; 29.8 at the pilot's rate, 89.1 at a quarter of it) in
  eight tasks of 3-8.3 hours, plus one review each; 1.35 CPU hours per task (0.68 hours elapsed on two
  workers), 10.8 CPU hours for all eight; 8.2 CPU hours (4.1 elapsed) for the required distribution sheet;
  at most one short DOSBox-X session (P7) and no session of the owner.** Every number is recounted by a
  script from the committed logs (`experiments/E032-match-engine-inventory/costs.py`, output
  `out/costs-review2-v3.md` and `.json`), with each assumption named, and `plancheck.py` checks that the
  figures on this page equal the report's. The result is an
  engine exact on every path the seed families and start states reach, the remaining paths ported as read
  and labelled so, and a distribution sheet that says how close the whole is.
- **The remaster can have the real engine first, for about 7 hours** (option D below): P0's tooling and
  P6's image adapter turn the harness that runs the original's code into an engine, at 8.3-16.8 CPU seconds
  a match; the port then replaces it piece by piece through the same hooks. Whether goal2 takes that is
  goal2's decision (L112; goal2 issue 97).

## What is known, and what is left

From F013 and the findings after it, and E032's coverage of five whole matches (kick-off to full time):

| part of the engine | routines | instructions (static) | reached by 5 seeds | known (findings) |
| --- | --- | --- | --- | --- |
| geometry and queries (`261A`-`2F28`, `045D`) | 36 | 1,027 | 97% | names (F013, F022); `278A`, `287C` substituted exactly (T42, T46) |
| player attributes (`1771`) | 21 | 1,174 | 95% | `377E` exact (T43), `3A06` inside `278A`'s model (T42); `3179`, `3216` read (F027, F028) |
| ball, passing, shooting (`2FB1`-`4151`) | 21 | 1,893 | 98% | launch and miscue read (F022); pass target read (F026) |
| positioning and marking movement (`419C`-`4D3F`) | 12 | 1,284 | 94% | depth tables and tactic readers read (F026); posts exact (F028) |
| decisions and contests (`4DA9`-`5A8E`) | 17 | 1,400 | 91% | tackle, challenge read (F022); holder's choice read (F026) |
| duels and play at the ball (`5B36`-`6240`) | 8 | 869 | 88% | keeper duel read (F015, F022) |
| goals, restarts, set pieces (`6337`-`7621`) | 29 | 2,009 | 82% | goal and after-goal swing exact in the quick engine (F012, F020) |
| form, fouls, cards, substitutions (`7CC5`-`82EB`) | 6 | 515 | 84% | foul chain, cap, bans read (F027); substitutions (F012, F029) |
| ball and player motion, offside line (`835F`-`90C5`) | 10 | 970 | 98% | tick map (F013); `8889`, `86D0` ported exactly (E032 pilot) |
| marking and leaders (`1F3C`-`20E3`) | 3 | 284 | 97% | man marking read (F026) |
| match frame (`9564`-`9A32`, `230C`) | 8 | 790 | 77% | tick order, clock, halves exact (F013) |
| commentary and ratings (`1829`-`1EB5`) | 5 | 447 | 99% | ratings exact (F014) |
| set-up and computer manager (`A260`-`CC2D`) | 14 | 1,240 | 86% | computer tactics and subs read (F010, F024) |
| **engine, all parts** | **190** | **13,902** | | 3 routines substituted exactly (`278A`, `287C`, `377E`), 2 more by the pilot |

Not in those numbers: the per-match set-up `A4A1` (192 instructions and its callees: it runs before the
watchstart state) and the shoot-out `A10A` (136), which no friendly reaches. Left out of the port: the
display and sound code that E032 removed without changing a match (`8F10`, `9079`, `0481`, `1829`, the
delay `0425`, the whistle `0441`, the speaker `94E8`, and the key poll `9372` when no key is pressed), the
boards, menus and the captain screen, about 4,400 instructions in all (E032's UI and sound parts, less the
three drawing routines that stay: `8537`, `8E24`, `9119`), and the runtime's screen primitives.

**One fact shapes every route:** the pitch picture is the players' occupancy grid. The move test `86D0`
blocks a step onto a cell of the picture `[DS:7C16]` whose character is in the set `DS:0648`, and the
referee and the offside-line markers are drawn into that picture by `8E24`; skipping `8E24` or the player
sprite routine `8537` changes the match or stops it ending (E032 notes, "Why 8537 and 8E24 stay"). A
rebuild that moves players on a grid of its own design, without the referee and the markers in it, will
not move them the way the original does.

## Four routes

| route | what | cost | what it delivers | verdict |
| --- | --- | --- | --- | --- |
| A. routine proofs (M3-M6 as in `docs/plan.md`) | substitute one routine at a time, each proved side by side at every call, with mutation harnesses | T42, T43 and T45-T48 took six tasks for about ten small routines; T48's logs hold 14 proved whole matches of 32-80 minutes each, and 8 more stopped at a time limit. At six tasks per ten routines, 190 routines are over a hundred tasks | exact, routine by routine | too expensive: the proof per call is what costs, and the match check is as strong |
| B. a new engine, calibrated | write a pitch simulation from the findings' rules, tune free parameters to the original's distributions | 10-15 h to write (an estimate, not measured); calibration is open-ended. Each effect needs hundreds of matches per arm (below); E026 could not see any tactic's effect on goals at 30 matches per arm | "close enough" at best, never shown to be; the bot learns the model's quirks, which do not transfer to the original (`docs/plan.md`: a strategy that wins in it must win in the original) | rejected as the main route; kept as the fallback for paths that are not ported |
| C. port and check whole matches (recommended) | translate the listing part by part, memory-faithful; substitute without proof; accept on identical whole matches over a seed family; prove only to locate an error | about 50 h (29.8-89.1) in eight tasks, 1.35 CPU h each, plus 8.2 CPU h for the required sheet (below) | exact where the seed families reach; a measured distance where they do not | **recommended** |
| D. run the original's code as the engine | goal2 drives the Unicorn harness with its own state written into the guest memory | about 7 h: P0's tooling (3 h) and P6's image adapter (4 h), done first; then 8.3-16.8 CPU s a match | exact by construction, now; needs the original's `GOAL.EXE` bytes at run time (a private release asset, U17) and is slow for the bot | a stopgap for goal2 to choose; C replaces it piece by piece through the same hooks |

Why C over B, in numbers: watched goals have a standard deviation of 1.37 per match and bookings 1.44
(C-MATCH-27). To see a difference of 0.25 goals between two arms (alpha 0.05, power 0.8) takes 472
matches per arm; 0.5 goals takes 118. One effect (a skill, form, one tactic element) is two arms on the
original and two on the model: at the measured 11.1 CPU seconds an oracle match, the original's two arms
alone are 944 matches, 2.9 CPU hours (1.5 elapsed on two workers) for the 0.25-goal resolution, and a model
that fails has to be changed and measured again. A step of the port is checked on 40 matches at 18.0 s
(the pilot's hooked speed): 12.0 CPU minutes, and when it fails the first differing draw says where.

## The route, step by step

Each step is one task (`docs/process.md`), merged on its own, implemented by a Claude subagent and
reviewed by OpenCode (CLAUDE.md "Choosing models"). Every step's exit check is the same mechanism: whole
watched matches of the original with the step's routines replaced by their ports, compared with the
unhooked matches of the same seeds, field by field (score, ticks, every main-seed draw by its digest, the
full-time board's raw statistics, the commentary's template counts), plus two or three falsifiers that
must each change a match or stop it completing. The comparison fails closed (`compare.py`, after PR 243's
review): the candidate must hold exactly the expected seeds, each once, every match must have reached
the full-time board with no error and no stray key wait, and every record must carry all the evidence the
comparison uses (missing evidence is neither a match nor a caught falsifier); a run whose generator failed
is never compared. The family is 40 matches: 20 seeds from E011-r0001's
watchstart state as they are, and the same 20 with declared edits that widen the paths (one side's tactic
byte, skills, energy and form, as E026 edited them); start states with other countries come with P7. (E011-r0002's records differ from r0001's only in
bytes F013 calls timing artefacts, so its watchstart adds little once the seed is written.)

| step | what | instructions | exit check | cost |
| --- | --- | --- | --- | --- |
| P0 | **Tooling.** Fold E032's pieces into the harness: the delay count at kick-off as a run option; a `port` mode that hooks a set of Python routines without proof; the field-by-field comparison and a seed-family runner (two processes at most, as the machine is shared); a divergence locator (the first tick whose draws differ, then `prove=True` on the routines of that tick) | — | the E032 pilot re-run through the new mode: 40 of 40 identical, its 3 falsifiers caught | 3 h |
| P1 | **Leaves**: geometry and queries, player attributes, the runtime primitives the engine calls (sets, long arithmetic, the draws). Ports are plain functions on a `Match` memory view | 2,449 | every leaf hooked at once: 40 of 40 identical | 5.9 h |
| P2 | **Movement**: motion and the offside line (`8537`, `8E24`, `8AE9`, `8CF5`, `90C5`, the referee `9119`, the ball's travel `835F`, `83A2`), positioning and marking (`419C`-`4D3F`, `1F3C`-`20E3`, `1771:3E2F`, `3EF8`) | 2,941 | the same, with P1's ports in | 7.1 h |
| P3 | **The ball and the holder's choices**: passing, shooting, launches, the decisions and contests (`2FB1`-`4151`, `4DA9`-`5A8E`) | 3,293 | the same | 7.9 h |
| P4 | **Duels, goals and restarts**: `5B36`-`6240`, `6337`-`7621` (kick-offs, throw-ins, corners, goal kicks, free kicks, the goal and after-goal swing) | 2,878 | the same; plus the frontier routines reached by an edited state where one is cheap (S) | 6.9 h |
| P5 | **The rest of the match**: fouls, cards, injuries, the cap and bans (`7CC5`-`82EB`, `798D`, `7B77`, `7D56`, `7A43`), substitutions and the computer manager (`8062`, `A260`-`CC2D`), commentary and ratings (`1D4A`-`1EB5`), the frame (`9564`, `970C`, `97D0`, `983F`, `9A32`), the per-match set-up `A4A1` and its callees | 3,457 | from kick-off to full time every engine routine is a port (only the boards, the menus and the removed display code are still guest code); 40 of 40 identical | 8.3 h |
| P6 | **The engine on its own**: the port runs a match from a match image (the bytes of DS, the pitch records, the picture, the player and country records) without Unicorn; an adapter writes the image from a squad, a formation and tactics, and reads back the result (score, scorers, minutes, ratings, energy, form, cards, injuries, the commentary's events). This is option D's adapter too | — | the port alone, from the images the harness dumps at kick-off, equals the harness on 40 of 40 matches; its speed per match is stated | 4 h |
| P7 | **Rare paths and competitive matches**: penalties (`6ECF`), sendings off (`7B77`), extra time, the shoot-out `A10A` and its callees, the two-substitution budget, the rest of the frontier of E032's `union-5seeds` table; start states from competitive fixtures (from the play-the-game run's savestates, or one DOSBox-X session to the first cup match), and edited states | 1,437 | identical on each start state that reaches the path; what no state reaches is listed with its assumption | 4.5 h (1 h of it preparing the start states) |
| — | **Sheet A, fidelity (required)**: the nine board statistics and the possession bar, means and intervals, oracle against port. The oracle's 500 matches on E011-r0001's state run once, at P6, and are reused at P7, which adds 100 on each of two new start states (700 oracle matches in all); the port runs 500 at P6 and all 700 again at P7, because the port changes between them (1,200 port matches) | — | port and oracle within their intervals everywhere; any gap names a path that is not exact | 2 h of work; 8.2 CPU h, 4.1 h elapsed on two workers |
| — | **Sheet B, effects for the bot (optional, goal2's call)**: eleven effects (skill +4, energy, form, tactic elements 1-8, one flipped at a time) against ONE baseline arm shared by all eleven, 12 arms; run once, after P7, on whichever engine is faster (an exact port gives the original's numbers) | — | the table, with intervals | at 0.25 goals, 472 a arm: 5,664 matches, 17.5 CPU h, 8.7 h elapsed; at 0.5 goals, 118 a arm: 1,416 matches, 4.4 CPU h, 2.2 h elapsed |

The CPU figures use the measured 11.1 CPU seconds an oracle match (the mean of 10 with the delay count),
18.0 s a hooked port match (the mean of the pilot's 18 exact hooked matches; ASSUMED for the port on its
own, whose speed P6 measures), and 349.0 s for a step's three falsifiers (the measured mean of the pilot's
two falsifier sets, each with one falsifier that ran to the 300 s limit without completing; budgeting them
at the hooked mean would have given 54.1 s). Elapsed time is CPU time divided by two workers, the most the
shared machine allows.

Total: 49.5 hours of implementer time, for 16,455 static instructions (`costs.py`: the reached routines by
step, A4A1's unreached callees, the frontier without the modelled quick engine, the shoot-out). The pilot's
rate (555 instructions in 40 minutes, about 832 an hour, exact at the first run; the 40 minutes are my own
account, not logged) is the optimistic end: it ran on clean, well-annotated code; there the porting is 19.8
hours and the whole 29.8. The step costs above assume half that rate on average, for nested procedures,
Pascal sets, the long arithmetic, state machines and debugging: 39.5 hours of porting and 10 fixed (P0 3, P6
4, P7's start states 1, the sheet's work 2; estimates); at a quarter of the pilot's rate the whole is 89.1.
Per step, 1.35 CPU hours (0.68 elapsed): six family checks of 40 matches (12.0 CPU minutes each), the three
falsifiers and five coverage runs; 10.8 CPU hours for the eight steps. Reviews: one per step, re-running one
family check and the falsifiers (17.8 CPU minutes, 8.9 elapsed); no mutation harnesses (T47, T48) unless a
reviewer asks for one.

What would change the estimate: a part whose port stays non-exact after one hour of locating is accepted
non-exact, with its divergence recorded (the tick, the routine, the field), and moved to the distribution
sheet; it does not stop the step. Two such parts in one step are raised to the main session.

## What is assumed

Graded as `docs/wide-pass.md` does (importance, cost, decision):

| unknown | importance | cost | assumption, and its risk |
| --- | --- | --- | --- |
| the manager's actions during play (a substitution, a tactic change, a taker) | H for the remaster, M for the engine | M (keys queued at declared ticks in the harness) | the port applies them between ticks through the same routines (`C88D`, `BBFF`, `CC7B`); the original applies them inside `9372` at some slot of a sweep, so a change can land up to one sweep (22 slot updates) earlier or later. Checked once in P5 with one queued key, if the harness takes it in under an hour |
| matches between other countries than E011's pair | M | S per start state | the code has no country-specific paths; the data (squads, formations, tactics) is read through the same routines. P7 adds two start states with other countries |
| the display code E032 removed (`8F10`, `9079`, `0481`, `1829`, `0425`, `0441`, `94E8`, `9372` without a key) | M | S | removable on every seed family: E032 tried 2 seeds; P0 re-runs the removal on 20 |
| the speaker's stream `DS:8336` | L | — | dropped: it feeds sound only (C-MATCH-05) |
| action replay, highlights (`.HIL`), the commentary's scroll | L | — | dropped (wide-pass: post-playable) |
| paths no start state reaches (the frontier after P7) | M | L | each is ported from the listing as read (status `read`, not `exact`), and listed; if one matters to the bot it gets a start state later |
| the quick result (`D733`) | — | — | already modelled (F012); not part of this route |

## What the remaster gets

- After P0 and the adapter of P6, about 7 hours (option D, if goal2 wants it): the real engine, exact, at
  8.3-16.8 CPU seconds a match, as long as the original's bytes are available at run time.
- After P6: an exact engine in Python with no emulation, speed stated; goal2 can lift it into its own types
  and check the lift against it in pure Python (no oracle needed), and can make it fast (a compiled port,
  or a cut-down model for the bot's search) as it decides.
- After P7 and the sheet: the rare paths, and the measured table of effects (skills, form, energy,
  tactics) that the bot's policy needs, from the port rather than from 30-match arms on the original.

## Risks

| risk | mitigation |
| --- | --- |
| a part resists exactness (for example a routine whose result depends on stack garbage or an uninitialised local) | the one-hour rule above; the divergence locator says which call; the part goes to the sheet |
| the seed family does not reach a branch the bot relies on | E032's union table per step; edited start states (P7); the coverage tool is re-run on each step's family |
| the port is too slow for the bot | measured at P6; the quick engine (F012) stays available for search; a compiled port is goal2's call |
| the machine is shared | two processes at most; a family check is 12.0 CPU minutes (6.0 elapsed), a step 1.35 CPU hours; the sheets (8.2 CPU hours for A, 4.4-17.5 for B) are the only long runs and can wait for a quiet machine |
