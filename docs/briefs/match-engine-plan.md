# Brief: the match engine

**Goal.** Replicate the watched match engine of GOAL2 (1993), or build something close enough: players
that behave and play the way the original's do, according to their skills, form and tactics. Not the quick
result (`0791:D733`, already modelled): the engine that plays a match you watch.

**Close enough** means the remaster's matches look and feel like the original's: goals, shots, possession,
fouls and cards come out with the same distributions, and a player's skills, form and team tactics move the
result the way they do in the original. Exactness is not required where it would cost more than it is worth.

**Practical.** The owner wants a practical route: no very long sessions, no proofs that cost more than they
are worth. Where something is unknown and expensive to find out, assume and say so.

**Context.** This repository explores the original and delivers findings and models; the remaster is the
repository `goal2`, which decides how it is built (CLAUDE.md, L112). Everything known so far is in
`findings/`, `spec/`, `docs/plan.md` and `runtime/model/`; the original runs unattended under the driver in
`runtime/driver/`. Work in a worktree on branch `docs/match-engine-plan`, open a PR, do not merge.

**What to bring back.** How you would get there, and what it costs.
