# goal2-archaeology

An evidence-backed specification of *goal (version 2)* (New Era Software, 1993), a DOS text-mode
international football team-management game, using the method of
[game-archaeologist](https://github.com/diegoami/game-archaeologist) (decisions U14–U20). The spec
feeds a faithful rebuild and a bot that maximises the World Cup win rate, in the private `goal2`.
The process is `docs/process.md`; read it before running a task. Tasks are `docs/tasks/T<nn>.md`,
indexed in `docs/tasks/README.md`.

## Rules
1. The main session plans, runs `/run-task`, triages and talks to the user. It delegates
   (`/delegate`): code to OpenCode, review to another model family, repeated decisions to Jev after
   a trial, and images and audio to OpenRouter or ElevenLabs models, whose ids come from live lists,
   never memory. Before choosing, recommending or delegating to a model, check its provider's quota
   with quota-tracker and skip an exhausted one for the next of the chain with quota, saying so
   (L50, `docs/environment.md`); the light OpenAI reviewer `luna` is GPT-5.6 Luna on its own weekly
   pool (L51). Heavy models run at effort low, medium only when justified.
2. Nobody works in the main checkout but the main session: OpenCode runs in the worktree the script
   makes, Claude agents run with worktree isolation. Never `git stash`.
3. Status lives in GitHub labels. No document carries a status snapshot.
4. A question is not a request to edit files. Answer it; propose any fix and wait.
5. The Done-when is not negotiable by the implementer. It stops and reports; it never weakens an
   assertion, skips a test or edits its task file. The main session amends a Done-when on `main`
   with the reason in the commit message.
6. The reviewer is never the implementer's model family. It re-runs every Done-when line itself.
7. Merge only with an approving review and green CI. Two rework rounds, then escalate. After a heavy
   review, the next round's implementer moves one step up, never down (`/run-task`). (L38)
8. Relay review findings in full, never a subset.
9. A test proves behaviour only if it fails without that behaviour; re-take a claim that nothing failed.
10. A comment asserting behaviour at an edge arrives with the test that visits that edge.
11. Until the first playable build, schedule only bugs that break play; the rest are `post-playable`.
12. A bug whose fix stays in the files it names and changes no outcome is a `fix`; a blocking
    one-file mechanical fix may ride the PR that found it, declared under Scope.
13. Design decisions go to the user; nothing else waits for the user.
14. At session start: `gh issue list --label triage:needed --state open`, and any task in flight.

## Token economy
15. A brief carries the task file pasted in full, never a pointer to it.
16. Keep every file an agent must read under ~20k tokens. Scope searches to the source and test
    directories; keep terminal output quiet; show diffs, not files.

## Conditional
17. [evidence-driven] Every constant in driver or parser code (an offset, a timing) traces to a finding
    or a representation claim; a guessed value says so and what was searched.

## This project
18. **The artifact comes by hash** (U17: GOAL2 is treated as abandonware). The original files are
    assets of a release of this private repository, verified against `artifacts/known.json`; they are
    never committed to the tree. Derived extracts (data tables, the unpacked executable's listings)
    may be committed, under `static/`. Nothing of GOAL2 goes to a public repository.
19. **Behavioural and static methods** (U16). The original runs in DOSBox-X in WSL; `GOAL.EXE` may be
    unpacked and decompiled. `corroborated` needs both a behavioural and a static finding.
20. **Research follows game-archaeologist ADR-007/008 and `method/research-protocol.md`.** Run records
    are raw and immutable, evidence bundles are release assets, and findings start `proposed`. Only
    the main session writes `spec/`, after review. Research PRs merge with a merge commit. Every
    measured output (run records, probe logs, timings) lives under a tracked path the task owns, is
    committed and pushed after each batch of runs and at least every 30 minutes, and is never deleted
    or overwritten (game-archaeologist L207).
21. **Routing by difficulty** (U13): game-archaeologist's `docs/models.md`, after the quota check of
    rule 1 (L50). Game rules, formulas or
    constants from evidence are hard. Rule 11 has no effect: this repository builds no playable game.
