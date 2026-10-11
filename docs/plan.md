# Plan

From the owner's decisions U14–U20 (game-archaeologist `docs/phase0/README.md`, 2026-10-03): a
behavioural spec of *goal (version 2)*, then a faithful rebuild that can simulate it, then a bot that
manages a country competently enough for idle play (the owner, 2026-10-11, replacing U15's "the best
World Cup win rate"), and modern databases from open data. This page
holds no status; the labels do.

## What shapes the plan

- **The match is a moving simulation, not a formula.** The help file describes zonal and man
  marking, energy spent "in direct proportion to the activity of the player", an offside trap and a
  pitch view where "you watch every move" (`GOAL.HLP` 61–63, 334–336, 469–555). The rebuild has to
  reproduce that simulation closely enough that a strategy that wins in it also wins in the
  original. That makes static analysis of the engine central (U16), with behaviour as the check.
- **The executable is small**: `GOAL.EXE` is 92,391 bytes, LZEXE-compressed, so a complete reading is
  realistic. `GOAL.DAT` is 44,040 bytes.
- **The original is fast to sample**: there is a "quick result option" (`GOAL.HLP` 127). If it uses
  the same engine as a watched match, which G6 checks, it makes statistical confirmation on the
  original affordable.
- **The bot needs speed**: millions of simulated matches. The rebuild is Python (U18), and is ported
  only if speed limits the bot.

## Milestones

| Milestone | It proves | Exit check |
| --- | --- | --- |
| **G-M1 Runtime** | an agent can launch → act → observe → reset the original | G1's driver repeats a launch, keystroke, screen read and reset cycle 10 times with the same before-state hash; a savestate restores; a memory read (from a savestate: apt's DOSBox-X has no debugger) is recorded as an I1 observation |
| **G-M2 Static base** | the executable and the data file can be read | `GOAL.EXE` unpacked and its unpacked hash recorded; the routines indexed by area; `GOAL.DAT`'s layout proposed as representation claims, one confirmed by a run |
| **G-M3 Simulatable spec** | the spec covers what a simulator needs | every knowledge-map area the rebuild needs (the match engine, attributes and their changes, competitions, the other managers) is `supported` or better, each by static and behavioural findings where it touches the match |
| **G-M4 Faithful rebuild** (`goal2`) | the simulator behaves like the original | on matched start states, the rebuild's result distributions (goals, possession, shots, bookings, injuries) agree with the original's within stated tolerances over a stated n; a 4-year cycle's competition structure is reproduced exactly |
| **G-M5 The bot** | competent idle play (the owner, 2026-10-11, replacing U15's World Cup win rate): the bot manages a country through whole campaigns with no human | a policy for squad, formation and tactics; for selected countries, whole 4-year cycles in the rebuild with no human input, every match fielding a legal, fit eleven by stated checks, and results no worse than the game's own computer choice (`C`) over a stated n; one cycle confirmed on the original |
| **G-M6 Modern databases** (U20) | current teams and players in GOAL2's own format | a writer for `GOAL.DAT`, proven by the original loading it; facts from Wikidata and openfootball, with source and licence recorded; our own ratings formula, documented; private only |

## The first tasks

All start after G0 (this repository, T01). G1–G4 can run in parallel.

| Task | Plan label | What | Difficulty |
| --- | --- | --- | --- |
| T01 | G0 | the repository, the artifact by hash, this plan | hard (Jev) |
| — | G1 | **DOSBox-X runtime spike, then the driver**: headless DOSBox-X in WSL; keystrokes in; the text screen read from video memory (`B800:0000`); savestates; memory reads (from savestates: apt's DOSBox-X has no debugger); what the game writes (completes `runtime_writes`); timing and determinism (does a fixed start state replay identically?) | hard: a new external dependency |
| — | G2 | **The record tools**, adapted from toy-archaeology's (`fetch_artifact`, `validate_runs`, `verify_evidence`, `check_citations`, `register_artifact`), with `verify_evidence` downloading in bulk (toy-archaeology#11) and citations checked across wrapped bullets (toy-archaeology#12). This is their second consumer, so game-archaeologist#10 (a shared validator) is due. | by Jev |
| — | G3 | **Static inventory**: unpack LZEXE (an open-source unpacker, named with its version); a disassembly of the 16-bit code (tool named and pinned); the routines indexed by area; `GOAL.DAT`'s structure proposed | hard: the evidence format of every static finding |
| — | G4 | **The documentation map**: `GOAL.HLP` passages recorded as sources, moving knowledge-map cells to `documented` | by Jev |
| T06 | G5 | **The research backlog** ([backlog.md](backlog.md)): falsifiable questions per area, ordered by what G-M3 needs, each naming its behavioural and static routes | — (an architecture task, main session) |

## The watched match: read it and run it (the owner, 2026-10-11)

The watched engine (`0791:9564`, F013) is learnt by two routes on one tool, together. **Read**
(white box): a routine of the decompiled `GOAL.EXE` is read and modelled in Python. **Run** (black
box): the Unicorn harness (`runtime/emul/watched.py`, F013) runs the original's own code on inputs
we choose. They meet by **substitution**: the harness can replace a guest routine with its model,
and a model is right when the match stays tick-exact against the original (the main seed's
trajectory, F013's check). A model that is wrong shows where: the first tick that diverges. The
same harness measures effects for the bot (G-M5) on the original code before the reading is done.

Each milestone is a task that merges on its own and moves one number: the share of the watched
engine's routines replaced by models while matches stay exact (L102).

| M | Read | Run | Exit check |
| --- | --- | --- | --- |
| M0 | — | whole matches from kick-off; inputs (tactics, skills, positions, seed); a substitution hook | a recorded watched match reproduced tick-exactly; a hooked routine keeps it exact, a wrong hook breaks it |
| M1 | the skill reader `278A` and strength `377E` (F015, F021) | substituted | matches stay exact |
| M2 | contests: tackle, pass, shot, header (Q010) | substituted; contest odds by skill | exact; a table of odds |
| M3 | a player's turn: what he chooses, from what | substituted | exact |
| M4 | movement, formations, positions, the sweeper (Q021–Q023) | substituted; out-of-position and wrong-foot costs | exact; effect tables |
| M5 | fouls, cards, injuries, keeper, set pieces (Q024–Q026, Q033) | substituted; offside trap, going in hard, marking | exact; effect tables |
| M6 | what remains | the whole engine is the model | a batch of seeded matches all exact: the rebuild's engine (G-M4) |

Effect measurements for the bot start right after M0, on the original's code. The owner's sittings
corroborate (their commentary and the pitch records each savestate holds), and the owner's answers
(`owner` testimony) give intent and the look of the game; neither replaces the code.

## Runtime prerequisites

The owner installs DOSBox-X, Xvfb and xdotool (installing software is the owner's step).
`bash setup/goal2-runtime.sh` checks the tools and versions, unpacks the release into `.cache/`, and
prints `ready` or what is missing (F001).

## Risks

| Risk | Mitigation |
| --- | --- |
| The match engine is too intricate to reproduce exactly | reproduce it by reading it (G3), then measure agreement statistically (G-M4); exactness is the goal, tolerances are the gate |
| Matches are random and the RNG cannot be controlled | G1 measures determinism from a savestate; G3 finds the RNG and its seeding, so a seed can be set (an I3 intervention, declared) |
| DOSBox-X timing differs from 1993 hardware | rule claims count from DOSBox-X; timing-dependent behaviour (if the engine reads the clock) is a G3 question |
| The modern databases raise licence questions | U20: open data only, our own ratings, private only |
