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
  step (`8889`, `86D0` and six helpers, about 620 instructions) in about 40 minutes; it was identical in 10
  of 10 whole matches (about 93,000 calls each) and each of three deliberate errors changed the match. A
  match of the original now costs 8-17 s instead of 20-51 s (the delay count written at kick-off, 10 of 10
  matches unchanged). Showing that a re-invented engine is "close enough" takes hundreds of oracle matches
  per effect, and every gap found means changing the model and measuring again; an exact port is checked
  in minutes.
- **Cost: about 40 hours of implementer time (range 30-60) in eight tasks of 3-6 hours, plus one review
  each; about one hour of CPU per task; at most one short DOSBox-X session (P7) and no session of the
  owner.** The result is an engine exact on every path the seed families and start states reach, the
  remaining paths ported as read and labelled so, and a distribution sheet that says how close the whole
  is.
- **The remaster can have the real engine before the port is finished** (option D below): the harness that
  runs the original's code is an engine already, at 8-17 s a match; ported parts replace it piece by piece.
  Whether goal2 takes that is goal2's decision (L112).

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
| A. routine proofs (M3-M6 as in `docs/plan.md`) | substitute one routine at a time, each proved side by side at every call, with mutation harnesses | T42, T43 and T45-T48 took six tasks for about ten small routines; a proved run took 70-80 minutes per record on the loaded machine (T48). At that rate 190 routines are hundreds of hours | exact, routine by routine | too expensive: the proof per call is what costs, and the match check is as strong |
| B. a new engine, calibrated | write a pitch simulation from the findings' rules, tune free parameters to the original's distributions | 10-15 h to write; calibration is open-ended. Each effect needs hundreds of matches per arm (below); E026 could not see any tactic's effect on goals at 30 matches per arm | "close enough" at best, never shown to be; the bot learns the model's quirks, which do not transfer to the original (`docs/plan.md`: a strategy that wins in it must win in the original) | rejected as the main route; kept as the fallback for paths that are not ported |
| C. port and check whole matches (recommended) | translate the listing part by part, memory-faithful; substitute without proof; accept on identical whole matches over a seed family; prove only to locate an error | about 40 h (30-60) in eight tasks, 1 h of CPU each (below) | exact where the seed families reach; a measured distance where they do not | **recommended** |
| D. run the original's code as the engine | goal2 drives the Unicorn harness with its own state written into the guest memory | one adapter task (the image adapter of step P6, done first); 8-17 s a match | exact by construction, now; needs the original's `GOAL.EXE` bytes at run time (a private release asset, U17) and is slow for the bot | a stopgap for goal2 to choose; C replaces it piece by piece through the same hooks |

Why C over B, in numbers: watched goals have a standard deviation of 1.37 per match and bookings 1.44
(C-MATCH-27). To see a difference of 0.25 goals between two arms (alpha 0.05, power 0.8) takes about 470
matches per arm; 0.5 goals takes about 120. One effect (a skill, form, one tactic element) is two arms on
the original and two on the model: at 10 s a match, about 2.6 hours of oracle CPU for the 0.25-goal
resolution, and a model that fails has to be changed and measured again. A port of the same code is
checked in about 5 minutes (20 seeds at 15 s), and when it fails the first differing draw says where.

## The route, step by step

Each step is one task (`docs/process.md`), merged on its own, implemented by a Claude subagent and
reviewed by OpenCode (CLAUDE.md "Choosing models"). Every step's exit check is the same mechanism: whole
watched matches of the original with the step's routines replaced by their ports, compared with the
unhooked matches of the same seeds, field by field (score, ticks, every main-seed draw by its digest, the
full-time board's raw statistics, the commentary's template counts), plus two or three falsifiers that
must each change a match. The seed family is 20 seeds from E011-r0001's watchstart state, half of them with
declared edits that widen the paths (one side's tactic byte, skills, energy and form, as E026 edited them);
start states with other countries come with P7. (E011-r0002's records differ from r0001's only in
bytes F013 calls timing artefacts, so its watchstart adds little once the seed is written.)

| step | what | instructions | exit check | cost |
| --- | --- | --- | --- | --- |
| P0 | **Tooling.** Fold E032's pieces into the harness: the delay count at kick-off as a run option; a `port` mode that hooks a set of Python routines without proof; the field-by-field comparison and a seed-family runner (two processes at most, as the machine is shared); a divergence locator (the first tick whose draws differ, then `prove=True` on the routines of that tick) | — | the E032 pilot re-run through the new mode: 20 of 20 identical, its 3 falsifiers caught | 3 h |
| P1 | **Leaves**: geometry and queries, player attributes, the runtime primitives the engine calls (sets, long arithmetic, the draws). Ports are plain functions on a `Match` memory view | ~2,500 | every leaf hooked at once: 40 of 40 identical | 4 h |
| P2 | **Movement**: motion and the offside line (`8537`, `8E24`, `8AE9`, `8CF5`, `90C5`, the referee `9119`, the ball's travel `835F`, `83A2`), positioning and marking (`419C`-`4D3F`, `1F3C`-`20E3`, `1771:3E2F`, `3EF8`) | ~2,900 | the same, with P1's ports in | 5 h |
| P3 | **The ball and the holder's choices**: passing, shooting, launches, the decisions and contests (`2FB1`-`4151`, `4DA9`-`5A8E`) | ~3,300 | the same | 6 h |
| P4 | **Duels, goals and restarts**: `5B36`-`6240`, `6337`-`7621` (kick-offs, throw-ins, corners, goal kicks, free kicks, the goal and after-goal swing) | ~2,900 | the same; plus the frontier routines reached by an edited state where one is cheap (S) | 6 h |
| P5 | **The rest of the match**: fouls, cards, injuries, the cap and bans (`7CC5`-`82EB`, `798D`, `7B77`, `7D56`, `7A43`), substitutions and the computer manager (`8062`, `A260`-`CC2D`), commentary and ratings (`1D4A`-`1EB5`), the frame (`9564`, `970C`, `97D0`, `983F`, `9A32`), the per-match set-up `A4A1` | ~3,500 | from kick-off to full time every engine routine is a port (only the boards, the menus and the removed display code are still guest code); 40 of 40 identical | 6 h |
| P6 | **The engine on its own**: the port runs a match from a match image (the bytes of DS, the pitch records, the picture, the player and country records) without Unicorn; an adapter writes the image from a squad, a formation and tactics, and reads back the result (score, scorers, minutes, ratings, energy, form, cards, injuries, the commentary's events). This is option D's adapter too | — | the port alone, from the images the harness dumps at kick-off, equals the harness on 40 of 40 matches; its speed per match is stated | 4 h |
| P7 | **Rare paths and competitive matches**: penalties (`6ECF`, `690C`), sendings off, extra time, the shoot-out `A10A`, the two-substitution budget, the frontier of E032's `union-5seeds` table; start states from competitive fixtures (from the play-the-game run's savestates, or one DOSBox-X session to the first cup match), and edited states | ~800 | identical on each start state that reaches the path; what no state reaches is listed with its assumption | 4 h |
| — | **The distribution sheet**, run once at P6 and once at P7: 500 oracle matches and 500 port matches over the start states, the nine board statistics and the possession bar, the means and their intervals; then the effect table for the bot: skill +4, energy, form, each tactic element, one flipped at a time, 470 matches per arm on the port (fast) with 100 per arm on the oracle as the check | — | port and oracle within their intervals everywhere; any gap names a path that is not exact | 2 h of work, about 3 h of CPU |

Total: about 40 hours of implementer time, for about 15,900 instructions. The pilot's rate (620
instructions in 40 minutes, exact at the first run, about 900 an hour) is the optimistic end: it ran on
clean, well-annotated code. The step estimates assume about 40% of that rate on average (about 370 an hour),
for nested procedures, Pascal sets, the long arithmetic, state machines and debugging; at half the pilot's
rate the whole is about 30 hours, at a quarter of it about 60. Reviews: one per step, re-running the
step's check (5-10 minutes of CPU) and its falsifiers; no mutation harnesses (T47, T48) unless a reviewer
asks for one.

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

- After P0 and the adapter of P6 (option D, if goal2 wants it): the real engine, exact, at 8-17 s a match,
  as long as the original's bytes are available at run time.
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
| the machine is shared | two processes at most; a step's checks are minutes, not hours |
