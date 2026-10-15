# Brief: play the game, all the way, without getting stuck

**Goal.** Explore the whole interface of GOAL2 (1993) by playing it, and leave behind a clear guide that lets
any later session play it fast and never get stuck: how to play a game, and everything that can be changed in
it. The screens are meant to be self-explanatory: if a person could work them out, so can you.

**Proof.** Play a game through the first year, then two years, then three, recording the progress as you go,
and show that you were there and did not get stuck (what the evidence is, and how someone can check it, is
yours to decide). A run that gets stuck is a result: say where and why.

**When you cannot find out how to do something, or you get stuck, do not guess:** come back to the owner with
the question (the screen, what you tried, what you need to know). Ask early; the owner would rather answer ten
questions than read a wrong guide.

**The guide** says how to play (from a new game to the end of a year and on), every screen and what it offers,
every setting and choice the game lets you change, the keys, the prompts and their defaults, and what to do
when something looks stuck. Written so a later session can execute a run as quickly as possible. Probably
runs go best slowly, at the pace of a 1990s computer; find what works and say why.

**First, draw a plan** to explore the game fully and make later runs fast and reliable, then carry it out as
far as it goes; the plan is yours, including the order and the stopping points.

**Context.** The original runs unattended under the driver in `runtime/driver/` (DOSBox-X, savestates). What is
already known is in `findings/` (F030 has the match prompts, waits and keys), `spec/`, the coverage map in
`experiments/E015-human-playthrough/protocol.md`, `docs/environment.md`. This repository explores the
original and delivers findings; the remaster is `goal2` and decides its own design (L112). Be practical (L113).
Work in a worktree on branch `docs/play-the-game`, commit and push as you go, open a PR, do not merge. Nothing
of the original is committed (CLAUDE.md rule 18).

**Bring back.** The plan, the guide, the proof of how far each run got, and your questions for the owner.
