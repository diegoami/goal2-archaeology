# goal2-archaeology

An evidence-backed specification of *goal (version 2)* (New Era Software, 1993), a DOS text-mode
international football team-management game, using the method of
[game-archaeologist](https://github.com/diegoami/game-archaeologist) (decisions U14–U20). The spec
feeds a faithful rebuild and a bot that plays a country competently for idle play (the owner,
2026-10-11), in `goal2`. How work runs is `docs/process.md`; tasks are `docs/tasks/T<nn>.md`,
indexed in `docs/tasks/README.md`.

[designed: owner, 2026-10-20] The project runs from any checkout, a cloud session included
(`docs/cloud.md`, `tools/cloud_setup.sh`, DOSBox-X 2024.03.01 headless). The earlier review harness
(OpenCode protocol, guards, model switching, worktrees, per-PR review gates, Jev) was removed; it is
kept on the branch `local`.

## Working rules
1. [designed: owner correction, 2026-10-26] The main session plans, triages, implements, verifies
   and merges on `gpt-6.1-sol` at `high`. It may sparingly spawn a `gpt-6.1-sol` / `xhigh` agent
   for only the hardest, narrowly scoped parts; it does not delegate every task. Astra is excluded
   from implementation and review; xhigh is the Codex effort ceiling. The engine-study policy is
   `docs/engine-study-models.md`; its independent Claude/Kimi review milestones remain in force.
   Codex follows the same rules from `AGENTS.md`.
2. Work on a branch in the checkout at hand; one task at a time per checkout. No worktrees. Locally
   a task branch `task/T<nn>-<slug>`; in a cloud session the session's own `claude/…` branch, for
   every task of that session (process.md §3). Never `git stash`, never force-push, never rewrite
   `main`.
3. One task, one PR, merged by the main session once its Done-when lines pass and CI is green, always
   with a merge commit (`gh pr merge <pr> --merge --match-head-commit <sha>`): research PRs need their
   commits kept (rule 20), and a cloud session's branch then fast-forwards (`git pull --ff-only
   origin main`).
4. Reviews are optional. Per PR, when the risk warrants it (a finding, a game rule or constant, the
   engine port, the proof), run `tools/review_pr.sh <pr> <opencode|claude|codex> <model>`; any model
   may review. At each milestone, one big independent review: `tools/milestone_review.sh`
   (`docs/milestone-review.md`). Relay review findings in full.
5. The Done-when is not negotiable by the implementer: it stops and reports, never weakens an
   assertion, skips a test or edits its task file. The main session amends a Done-when on `main`
   with the reason in the commit message.
6. A question is not a request to edit files. Answer it; propose any fix and wait.
7. Design decisions go to the owner; nothing else waits for the owner.
8. A lesson or decision of the owner goes into this file or `docs/` in a commit, never only into
   a model's memory.
9. Status lives in GitHub labels and issues, not in documents.
10. A test proves behaviour only if it fails without that behaviour; a comment asserting behaviour
    at an edge arrives with the test that visits that edge.
11. Undo a scratch edit by writing back the file's saved contents, or commit first; never
    `git checkout`, `git restore` or `git reset` a file with uncommitted work.
11a. Wait on a background job by its PID (`while kill -0 <pid>; do sleep 30; done`) or by the final
    line of its log, never with `pgrep -f`: it matches the waiting shell's own command line (L48).
12. Heavy jobs (match runs, family runs, `check.py`, the unit suite) take a slot of
    `tools/heavy.sh` (#318), four at a time on a machine.

## Conditional
17. [evidence-driven] Every constant in driver or parser code (an offset, a timing) traces to a finding
    or a representation claim; a guessed value says so and what was searched.

## This project
18. **The artifact comes by hash** (U17: GOAL2 is treated as abandonware). The original files are
    assets of this repository's releases (`goal2-original` and the evidence and savestate releases),
    verified against `artifacts/known.json`; they are never committed to the tree. Derived extracts
    (data tables, the unpacked executable's listings) may be committed, under `static/`.
    [designed: owner, 2026-10-20] This repository and its releases are public, and the owner keeps
    them so: GOAL2 is abandonware. (The rule used to say "private"; the repository had become public.)
19. **Behavioural and static methods** (U16). The original runs in DOSBox-X (WSL locally, or a Linux cloud session, `docs/cloud.md`); `GOAL.EXE` may be
    unpacked and decompiled. `corroborated` needs both a behavioural and a static finding.
20. **Research follows game-archaeologist ADR-007/008 and `method/research-protocol.md`.** Run records
    are raw and immutable, evidence bundles are release assets, and findings start `proposed`. Only
    the main session writes `spec/`, after review. Research PRs merge with a merge commit (never squash: tag `research/T02`
    keeps the commits `runs/E001` cites, from #12's mistaken squash; never delete it). Every
    measured output (run records, probe logs, timings) lives under a tracked path the task owns, is
    committed and pushed after each batch of runs and at least every 30 minutes, and is never deleted
    or overwritten (game-archaeologist L207).
21. **Difficulty** (U13): game rules, formulas or constants from evidence are hard work; a hard
    task gets an independent review (`tools/review_pr.sh`, rule 4) on a strong model. This repository
    builds no playable game.
22. **Static first** (game-archaeologist U32, the owner, 2026-10-05). A research question is answered
    by reading the decompiled and disassembled `GOAL.EXE` first (the named view
    `static/goal-exe/named/`, then the raw `static/goal-exe/decompiled/` and `static/goal-exe/code/`; Ghidra as `docs/environment.md` says). Runs of the game are made only
    when static analysis cannot answer, or to corroborate a static answer (rule 19). A finding that
    rests on runs says in its Method what static analysis was tried and why it was not enough. A
    missing tool is never the reason: install it, or stop and report. A review treats runs made
    because a tool was missing as a contract defect (gate G0a): rework.
23. [designed: owner priority update, 2026-10-27; goal2#393] Standalone engine replacement
    is now immediate priority: T78 assembly, T79 fidelity, T80 sealed delivery and request427
    for safe tournament continuation. Fresh careers suffice; old-career migration is not required.
    This supersedes the earlier long-term/planning-only deferral. Preserve active engine-study
    work and strict fidelity/review/delivery gates; do not ship an unvalidated default.
    [designed: owner, 2026-10-27] The goal session handles that delivery independently in a
    cloned repository. This engine-study session continues the analysis through ES-R2 and
    prepares its independent-review prompt; it does not start standalone/backend work here.
    [designed: owner, 2026-10-22] **goal2's first version runs the original's whole game under Unicorn**
    (goal2 #308, stage 3): requests from goal2 for it (where the state lives in memory, key waits and
    timed prompts, screens; process.md §15) come before new port tasks. The independent executable
    stays the long-term goal, so the engine port continues after them, as its track; the port PRs in
    flight on 2026-10-22 (T62, T63, T64, T69) finish as decided on them. The rule below is the port's
    own order within that track.
    **The engine migration comes first** (the owner, 2026-10-18): "As a rule, work toward the engine
    migration first and document reflection or hardening issues." The route-C engine port (the port
    of the watched match engine, T57-T80 in `docs/backlog.md`) has priority over everything else.
    Hardening, defence-in-depth and edge-case work on the proof or the tooling (for
    example the reflection routes to the raw Unicorn engine, #333; refusals that wait for a slot,
    #328) is not fixed ahead of the port, unless it blocks a port task or breaks the proof for
    ordinary use. It is recorded as a follow-up issue that states the known limit and its acceptance
    (what would close it), and, where the limit concerns a mechanism, as a note in the docs too. A
    reviewer's finding that is a deliberate-reflection or adversarial-use route, when the port's own
    code does not use it, is likewise a known limit with a follow-up issue and is not reworked
    again. The owner decides when a limit is worth closing.
